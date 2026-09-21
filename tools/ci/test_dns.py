#!/usr/bin/env python3
"""Host-level DNS tests for CI.

This script discovers the DNS servers configured in the repository Kotlin source
(app/src/main/java/repository/DnsDataSource.kt) and checks them the same way the
app uses them:

  - plaintext entries (no port/name): a DNS query over UDP/53
  - DoH entries (port 443 + name/path): a DNS-over-HTTPS query against
    https://<ip>/<path> with the entry's hostname (Host header + SNI), which is
    how Blokada reaches DoH servers by IP

IPv6 addresses are skipped automatically when the host has no IPv6 connectivity
(for example on GitHub-hosted runners), and reported as skipped, not failed.

Usage:
  - Install dependency: pip install "dnspython" "httpx[http2]"
  - Run: ./tools/ci/test_dns.py
  - You can override the kotlin source path with --kotlin-path

Google (dns.google) is special-cased: the app's engine uses Google's JSON
DoH API at /resolve rather than RFC 8484 wire format, so the check does too.

Exit codes:
  0 = all checks passed (skipped entries are not failures)
  2 = one or more checks failed, or no servers/domains could be determined
"""

from __future__ import annotations

import argparse
import base64
import ipaddress
import json
import os
import re
import socket
import sys
import time
from typing import List, Optional

import dns.exception
import dns.message
import dns.query
import dns.rcode
import dns.rdatatype
import dns.resolver
import httpx

DEFAULT_DOMAINS = ["example.com", "blokada.org"]
DEFAULT_KOTLIN_PATH = "app/src/main/java/repository/DnsDataSource.kt"

DNS_ENTRY_RE = re.compile(r"Dns(?:\.plaintextDns)?\s*\(\s*(.*?)\n\s*\)", re.DOTALL)
IP_LITERAL_RE = re.compile(r'"([0-9a-fA-F:.]+)"')


def parse_env_list(name: str, default: List[str]) -> List[str]:
    v = os.getenv(name)
    if not v:
        return default
    return [s.strip() for s in v.split(",") if s.strip()]


def has_ipv6_connectivity(timeout: float = 3.0) -> bool:
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(("2606:4700:4700::1111", 443))
        s.close()
        return True
    except OSError:
        return False


class DnsServerEntry:
    def __init__(self, entry_id: str, ips: List[str], port: Optional[int],
                 name: Optional[str], path: Optional[str]):
        self.entry_id = entry_id
        self.ips = ips
        self.port = port
        self.name = name
        self.path = path

    @property
    def is_doh(self) -> bool:
        return self.port is not None and self.name is not None and self.path is not None

    def __repr__(self) -> str:
        kind = "DoH" if self.is_doh else "plain"
        return f"{self.entry_id} ({kind})"


def extract_field(body: str, field: str) -> Optional[str]:
    m = re.search(rf"{field}\s*=\s*\"([^\"]*)\"", body)
    return m.group(1) if m else None


def extract_ips(body: str) -> List[str]:
    m = re.search(r"ips\s*=\s*listOf\((.*?)\)", body, re.DOTALL)
    if not m:
        return []
    raw = [lit.strip() for lit in IP_LITERAL_RE.findall(m.group(1))]
    ips: List[str] = []
    invalid: List[str] = []
    for lit in raw:
        try:
            ipaddress.ip_address(lit)
        except ValueError:
            invalid.append(lit)
            continue
        if lit not in ips:
            ips.append(lit)
    if invalid:
        for bad in invalid:
            print(f"[FAIL] {bad}: not a valid IP address literal in DnsDataSource.kt")
        sys.exit(2)
    return ips


def extract_entries_from_kotlin(path: str) -> List[DnsServerEntry]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"Kotlin file not found at {path}, skipping Kotlin-based discovery.")
        return []

    # Drop comment lines so commented-out Dns entries are not picked up
    src = "\n".join(line for line in src.splitlines()
                     if not line.strip().startswith("//"))

    entries: List[DnsServerEntry] = []
    for m in DNS_ENTRY_RE.finditer(src):
        body = m.group(1)
        entry_id = extract_field(body, "id")
        ips = extract_ips(body)
        if not entry_id or not ips:
            continue
        port_str = re.search(r"port\s*=\s*(\d+)", body)
        entries.append(DnsServerEntry(
            entry_id=entry_id,
            ips=ips,
            port=int(port_str.group(1)) if port_str else None,
            name=extract_field(body, "name"),
            path=extract_field(body, "path"),
        ))
    return entries


def check_plaintext(server: str, domain: str, timeout: float) -> Optional[str]:
    """Query a plaintext DNS server over UDP/53. Returns error text or None on success."""
    query = dns.message.make_query(domain, "A")
    try:
        response = dns.query.udp(query, server, timeout=timeout)
    except (dns.exception.DNSException, OSError) as e:
        return str(e)
    if response.rcode() != dns.rcode.NOERROR:
        return f"rcode={dns.rcode.to_text(response.rcode())}"
    if not response.answer:
        return "no answer section"
    return None


class DoHChecker:
    """Performs DoH queries against a literal server IP, using the entry's
    hostname for SNI and certificate validation (the same way the app's engine
    reaches DoH servers by IP). Speaks HTTP/2 when the server offers it."""

    def __init__(self, timeout: float):
        self.timeout = timeout
        self.client = httpx.Client(http2=True, timeout=timeout)

    def close(self):
        self.client.close()

    def check(self, ip: str, host: str, path: str, domain: str) -> Optional[str]:
        """Returns error text, or None on success."""
        if not path.startswith("/"):
            path = "/" + path
        try:
            if host == "dns.google":
                return self._check_google_json(ip, host, path, domain)
            return self._check_rfc8484(ip, host, path, domain)
        except httpx.HTTPError as e:
            return str(e)
        except (OSError, socket.timeout) as e:
            return str(e)

    def _request(self, ip: str, host: str, url_path: str,
                 accept: Optional[str] = None) -> httpx.Response:
        headers = {"Host": host}
        if accept:
            headers["Accept"] = accept
        if ":" in ip:
            ip = f"[{ip}]"
        return self.client.get(
            f"https://{ip}{url_path}",
            headers=headers,
            extensions={"sni_hostname": host},
        )

    def _check_rfc8484(self, ip: str, host: str, path: str, domain: str) -> Optional[str]:
        query = dns.message.make_query(domain, "A")
        b64 = base64.urlsafe_b64encode(query.to_wire()).rstrip(b"=").decode()
        resp = self._request(ip, host, f"{path}?dns={b64}",
                             accept="application/dns-message")
        if resp.status_code != 200:
            return f"HTTP {resp.status_code}"
        try:
            message = dns.message.from_wire(resp.content)
        except Exception as e:
            return f"malformed DNS response: {e}"
        if message.rcode() != dns.rcode.NOERROR:
            return f"rcode={dns.rcode.to_text(message.rcode())}"
        if not message.answer:
            return "no answer section"
        return None

    def _check_google_json(self, ip: str, host: str, path: str, domain: str) -> Optional[str]:
        resp = self._request(ip, host, f"{path}?name={domain}&type=A",
                             accept="application/dns-json")
        if resp.status_code != 200:
            return f"HTTP {resp.status_code}"
        try:
            data = json.loads(resp.content)
        except Exception as e:
            return f"malformed JSON response: {e}"
        if data.get("Status") != 0:
            return f"Status={data.get('Status')}"
        if not data.get("Answer"):
            return "no Answer in JSON response"
        return None


def run_checks(servers: List[DnsServerEntry], domains: List[str], timeout: float,
               retries: int, retry_delay: float) -> int:
    ipv6_available = has_ipv6_connectivity()
    if not ipv6_available:
        print("No IPv6 connectivity detected; IPv6 addresses will be skipped.")

    doh_checker = DoHChecker(timeout)
    failed = False
    skipped = 0

    try:
        for entry in servers:
            print(f"\n--- {entry} ---")
            for ip in entry.ips:
                if ":" in ip and not ipv6_available:
                    print(f"[SKIP] {ip}: IPv6 not available on this host")
                    skipped += 1
                    continue
                for domain in domains:
                    error = None
                    for attempt in range(1, retries + 1):
                        if entry.is_doh:
                            error = doh_checker.check(ip, entry.name, entry.path, domain)
                        else:
                            error = check_plaintext(ip, domain, timeout)
                        if error is None:
                            break
                        print(f"[WARN] attempt {attempt} failed for "
                              f"{entry.entry_id} ({ip}) -> {domain}: {error}")
                        if attempt < retries:
                            time.sleep(retry_delay)
                    if error is None:
                        kind = "DoH" if entry.is_doh else "plain"
                        print(f"[OK] {entry.entry_id} ({ip}, {kind}) -> {domain}")
                    else:
                        print(f"[FAIL] {entry.entry_id} ({ip}) -> {domain}: {error}")
                        failed = True
    finally:
        doh_checker.close()

    if skipped:
        print(f"\nSkipped {skipped} IPv6 address(es) due to no IPv6 connectivity.")

    return 2 if failed else 0


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description="Entry-aware DNS checks for CI")
    p.add_argument("--domains", "-d", type=str,
                   help="Comma-separated list of domains to query")
    p.add_argument("--timeout", type=float, default=5.0, help="Per-attempt timeout (seconds)")
    p.add_argument("--retries", type=int, default=2, help="Number of attempts per query")
    p.add_argument("--retry-delay", type=float, default=1.0,
                   help="Delay between retries (seconds)")
    p.add_argument("--kotlin-path", type=str, default=DEFAULT_KOTLIN_PATH,
                   help="Path to DnsDataSource.kt to discover servers")
    args = p.parse_args(argv)

    entries = extract_entries_from_kotlin(args.kotlin_path)
    if not entries:
        print("No DNS server entries found in Kotlin source.", file=sys.stderr)
        return 2

    domains = [d.strip() for d in (args.domains.split(",") if args.domains
                else parse_env_list("DNS_DOMAINS", DEFAULT_DOMAINS)) if d.strip()]
    if not domains:
        print("No domains specified. Use --domains or set DNS_DOMAINS.",
              file=sys.stderr)
        return 2

    print(f"Discovered {len(entries)} DNS entries from {args.kotlin_path}")
    print(f"Testing domains: {domains}")
    return run_checks(entries, domains, timeout=args.timeout, retries=args.retries,
                      retry_delay=args.retry_delay)


if __name__ == "__main__":
    try:
        rc = main(sys.argv[1:])
    except KeyboardInterrupt:
        rc = 2
    sys.exit(rc)
