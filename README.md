# Blokada 5

Blokada 5 is the well known open source mobile ad blocker and privacy app.

>Status: AI-supported, not actively maintained. This fork was initiated after blokada discontinued the development of 5 in favor of 6. It is maintained on a best-effort basis with AI assistance.
>Dependabot keeps dependencies and security advisories up to date automatically (patch and minor bumps auto-merge; majors require manual review).
>Feature work, bug fixes, and other changes happen on a best-effort basis. Pull requests and issues are welcome — they may take time to be reviewed.

## Difference to Blokada 6

There is also Blokada 6 with cloud adblocking (as opposed to on-device adblocking of Blokada 5). It works better for most users, but requires a subscription. [Click here to open Google Play Store](https://go.blokada.org/play_cloud).

Both editions are being developed independently. See our main Github page for the source code.

# DNS servers

The app ships with a built-in list of DNS servers (see
[`DnsDataSource.kt`](app/src/main/java/repository/DnsDataSource.kt)). The list is checked
regularly; dead or changed upstreams are fixed, migrated, or removed. Each entry was verified
live against its configured endpoints (DoH entries via RFC 8484/JSON over HTTPS, plaintext
entries via UDP/53) with
[`tools/ci/test_dns.py`](tools/ci/test_dns.py).

Status: **OK** = endpoint answered DNS queries at last check.
**Last checked: 2026-09-21** (all IPv4 and IPv6 endpoints, both test domains).

| ID | Provider | Protocol | Endpoint | Status |
| --- | --- | --- | --- | --- |
| `network` | Network DNS | n/a | DNS of the current network | n/a (special entry) |
| `blocka2` | Blokada DNS | DoH | `dns.blokada.org` | OK |
| `cloudflare` | Cloudflare | DoH | `cloudflare-dns.com` | OK |
| `cloudflare.malware` | Cloudflare: malware blocking | DoH | `security.cloudflare-dns.com` | OK |
| `cloudflare.adult` | Cloudflare: malware & adult blocking | DoH | `family.cloudflare-dns.com` | OK |
| `adguard` | AdGuard | Plain (UDP/53) | `94.140.14.14`, `94.140.15.15` | OK |
| `adguard_family` | AdGuard: family | Plain (UDP/53) | `94.140.14.15`, `94.140.15.16` | OK |
| `alternate` | Alternate DNS | Plain (UDP/53) | `44.222.89.164` | OK |
| `artikel10` | Artikel10 | DoH | `dns.artikel10.org` | OK |
| `digitalcourage` | Digitalcourage | Plain (UDP/53) | `46.182.19.48` (dns2) | OK |
| `digitalegesellschaft` | Digitale Gesellschaft (Switzerland) | DoH | `dns.digitale-gesellschaft.ch` | OK |
| `dismail.plain` | Dismail plain | Plain (UDP/53) | `dismail.de` nodes | OK |
| `dismail.doh1` | Dismail DoH 1 | DoH | `fdns1.dismail.de` | OK |
| `dismail.doh2` | Dismail DoH 2 | DoH | `fdns2.dismail.de` | OK |
| `dnsforge.normal` | dnsforge | DoH | `dnsforge.de` | OK |
| `dns.sb` | dns.sb | DoH | `doh.dns.sb` | OK |
| `dnswatch` | DNS.Watch | Plain (UDP/53) | `84.200.69.80`, `84.200.70.40` | OK (resolver1 intermittently slow) |
| `fdn` | French Data Network | DoH | `ns0.fdn.fr` | OK |
| `fdn.secondary` | French Data Network: secondary | DoH | `ns1.fdn.fr` | OK |
| `google` | Google | DoH (JSON) | `dns.google` | OK |
| `mullvad` | Mullvad | DoH | `dns.mullvad.net` | OK |
| `njalla` | Njalla | DoH | `dns.njal.la` | OK |
| `opendns` | Open DNS | Plain (UDP/53) | `208.67.222.222`, `208.67.220.220` | OK |
| `opendns_family` | Open DNS: family | Plain (UDP/53) | `208.67.220.123`, `208.67.222.123` | OK |
| `quad9` | Quad9 | Plain (UDP/53) | `9.9.9.9`, `149.112.112.112` | OK |
| `quad101` | Quad 101 (TWNIC) | Plain (UDP/53) | `101.101.101.101`, `101.102.103.104` | Service alive; UDP filtered from some networks |
| `uncensored` | Uncensored DNS (CensurfriDNS) | DoH | `anycast.censurfridns.dk` | OK |
| `uncensored.dk` | Uncensored DNS (Denmark) | DoH | `unicast.censurfridns.dk` | OK |
| `verisign` | Verisign Public DNS | Plain (UDP/53) | `64.6.64.6`, `64.6.65.6` | OK |

Notes on recent changes (checked 2026-09-21):

- **AhaDNS** (au/chi/nl/no): removed — all four legacy endpoints are dead (connections refused or
  timing out). AhaDNS's replacement service "Blitz" was evaluated and is **not viable** for this
  app: `blitz.ahadns.com` currently has no A/AAAA records (authoritative NODATA) and requests to
  the Cloudflare edge return HTTP 530 (error 1016, origin DNS error). Even when reachable, Blitz
  publishes no fixed IPs, which conflicts with the app's connect-by-IP DoH model. See PR #9.
- **Alternate DNS**: re-pointed to its new primary `44.222.89.164` (old `76.76.19.19` is dead; old
  secondary and IPv6 literals removed as dead).
- **Digitalcourage**: switched to dns2 `46.182.19.48`, its only plaintext endpoint (dns3 is
  DoT-only now).
- **FDN**: migrated to DoH on the same IPs, split into `fdn` and `fdn.secondary` (per-hostname
  certificates); FDN disabled plaintext DNS in March 2025.
- **Uncensored DNS (CensurfriDNS)**: migrated to DoH, split into `uncensored` and `uncensored.dk`;
  plaintext port 53 was disabled upstream in September 2022.
- **quad101 (TWNIC)**: kept as-is — the service answers on TCP/53 and IPs are unchanged; UDP/53 is
  filtered from some networks (including the CI runner), which the non-blocking CI check reports
  as a failure.



# Building (outdated)

For information on how to build Blokada, see [BUILDING.md](BUILDING.md). To get help on development issues, [post your question on our developers-only forum](https://go.blokada.org/development) (we prioritise those).

# Contributing (outdated)

If you are interested to join us and do stuff used by hundreds of thousands of users every day, check [CONTRIBUTING.md](CONTRIBUTING.md).
