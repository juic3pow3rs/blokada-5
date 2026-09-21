/*
 * This file is part of Blokada.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 *
 * Copyright © 2021 Blocka AB. All rights reserved.
 *
 * @author Karol Gusak (karol@blocka.net)
 */

package repository

import model.Dns
import model.DnsId

object DnsDataSource {

    val network = Dns.plaintextDns(
        id = "network",
        ips = listOf(),
        label = "Network DNS"
    )

    val blocka = Dns(
        id = "blocka2",
        ips = listOf("193.180.80.1", "193.180.80.2"),
        plusIps = listOf("193.180.80.100", "193.180.80.101"),
        label = "Blokada DNS",
        port = 443,
        name = "dns.blokada.org",
        path = "dns-query",
        canUseInCleartext = false
    )

    val cloudflare = Dns(
        id = "cloudflare",
        ips = listOf("1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001"),
        port = 443,
        name = "cloudflare-dns.com",
        path = "dns-query",
        label = "Cloudflare"
    )

    fun getDns() = listOf(
        blocka,
        Dns.plaintextDns(
            id = "adguard",
            ips = listOf("94.140.14.14", "94.140.15.15", "2a10:50c0::ad1:ff", "2a10:50c0::ad2:ff"),
            label = "AdGuard"
        ),
        Dns.plaintextDns(
            id = "adguard_family",
            ips = listOf("94.140.14.15", "94.140.15.16", "2a10:50c0::bad1:ff", "2a10:50c0::bad2:ff"),
            label = "AdGuard: family"
        ),
        Dns.plaintextDns(
            id = "alternate",
            ips = listOf("44.222.89.164"),
            label = "Alternate DNS"
        ),
        Dns(
            id = "artikel10",
            ips = listOf("217.197.91.153", "2001:67c:1401:2120::1"),
            port = 443,
            name = "dns.artikel10.org",
            path = "dns-query",
            label = "Artikel10",
            region = "europe"
        ),
        cloudflare,
        Dns(
            id = "cloudflare.malware",
            ips = listOf("1.1.1.2", "1.0.0.2", "2606:4700:4700::1112", "2606:4700:4700::1002"),
            port = 443,
            name = "security.cloudflare-dns.com",
            path = "dns-query",
            label = "Cloudflare: malware blocking"
        ),
        Dns(
            id = "cloudflare.adult",
            ips = listOf("1.1.1.3", "1.0.0.3", "2606:4700:4700::1113", "2606:4700:4700::1003"),
            port = 443,
            name = "family.cloudflare-dns.com",
            path = "dns-query",       
            label = "Cloudflare: malware & adult blocking"
        ),
        Dns.plaintextDns(
            id = "digitalcourage",
            ips = listOf("46.182.19.48", "2a02:2970:1002::18"),
            label = "Digitalcourage",
            region = "europe"
        ),
        Dns(
            id = "digitalegesellschaft",
            ips = listOf("185.95.218.42", "185.95.218.43", "2a05:fc84::42", "2a05:fc84::43"),
            port = 443,
            name = "dns.digitale-gesellschaft.ch",
            path = "dns-query",
            label = "Digitale Gesellschaft (Switzerland)",
            canUseInCleartext = false,
            region = "europe"
        ),
        Dns.plaintextDns(
            id = "dismail.plain",
            ips = listOf("116.203.32.217", "159.69.114.157", "2a01:4f8:1c1b:44aa::32:217", "2a01:4f8:1c1b:44aa::1", "2a01:4f8:c17:739a::2"),
            label = "Dismail plain",
            region = "europe"
        ),
        Dns(
            id = "dismail.doh1",
            ips = listOf("116.203.32.217", "2a01:4f8:1c1b:44aa::32:217", "2a01:4f8:1c1b:44aa::1"),
            label = "Dismail DoH 1",
            port = 443,
            name = "fdns1.dismail.de",
            path = "dns-query",       
            region = "europe"
        ),
        Dns(
            id = "dismail.doh2",
            ips = listOf("159.69.114.157", "2a01:4f8:c17:739a::2"),
            label = "Dismail DoH 2",
            port = 443,
            name = "fdns2.dismail.de",
            path = "dns-query",       
            region = "europe"
        ),
        Dns(
            id = "dnsforge.normal",
            ips = listOf("49.12.67.122", "91.99.154.175", "176.9.93.198", "176.9.1.117", "2a01:4f8:c013:29d::122", "2a01:4f8:c010:8c35::175", "2a01:4f8:151:34aa::198", "2a01:4f8:141:316d::117"),
            label = "dnsforge",
            port = 443,
            name = "dnsforge.de",
            path = "dns-query",       
            region = "europe"
        ),
        Dns(
            id = "dns.sb",
            ips = listOf("185.222.222.222", "45.11.45.11", "2a09::", "2a11::"),
            label = "dns.sb",
            port = 443,
            name = "doh.dns.sb",
            path = "dns-query",       
            region = "europe"
        ),
        Dns.plaintextDns(
            id = "dnswatch",
            ips = listOf("84.200.69.80", "84.200.70.40"),
            label = "DNS.Watch",
            region = "europe"
        ),
//        Dns.plaintextDns(
//            id = "freenom",
//            ips = listOf("80.80.80.80", "80.80.81.81"),
//            label = "Freenom"
//        ),
        Dns(
            id = "fdn",
            ips = listOf("80.67.169.12", "2001:910:800::12"),
            port = 443,
            name = "ns0.fdn.fr",
            path = "dns-query",
            label = "French Data Network",
            region = "europe"
        ),
        Dns(
            id = "fdn.secondary",
            ips = listOf("80.67.169.40", "2001:910:800::40"),
            port = 443,
            name = "ns1.fdn.fr",
            path = "dns-query",
            label = "French Data Network: secondary",
            region = "europe"
        ),
        Dns(
            id = "google",
            ips = listOf("8.8.8.8", "8.8.4.4", "2001:4860:4860::8888", "2001:4860:4860::8844"),
            port = 443,
            name = "dns.google",
            path = "resolve",
            label = "Google"
        ),
        Dns(
            id = "mullvad",
            ips = listOf("194.242.2.2", "2a07:e340::2"),
            port = 443,
            name = "dns.mullvad.net",
            path = "dns-query",
            label = "Mullvad",
            region = "europe"
        ),
        Dns(
            id = "njalla",
            ips = listOf("95.215.19.53", "2001:67c:2354:2::53"),
            port = 443,
            name = "dns.njal.la",
            path = "dns-query",
            label = "Njalla",
            region = "europe"
        ),
        Dns.plaintextDns(
            id = "opendns",
            ips = listOf("208.67.222.222", "208.67.220.220"),
            label = "Open DNS"
        ),
        Dns.plaintextDns(
            id = "opendns_family",
            ips = listOf("208.67.220.123", "208.67.222.123"),
            label = "Open DNS: family"
        ),
        Dns.plaintextDns(
            id = "quad9",
            ips = listOf("9.9.9.9", "149.112.112.112", "2620:fe::fe", "2620:fe::9"),
            label = "Quad9"
        ),
        Dns.plaintextDns(
            id = "quad101",
            ips = listOf("101.101.101.101", "101.102.103.104", "2001:de4::101", "2001:de4::102"),
            label = "Quad 101"
        ),
        Dns(
            id = "uncensored",
            ips = listOf("91.239.100.100", "2001:67c:28a4::"),
            port = 443,
            name = "anycast.censurfridns.dk",
            path = "dns-query",
            label = "Uncensored DNS",
            region = "europe"
        ),
        Dns(
            id = "uncensored.dk",
            ips = listOf("89.233.43.71", "2a01:3a0:53:53::"),
            port = 443,
            name = "unicast.censurfridns.dk",
            path = "dns-query",
            label = "Uncensored DNS (Denmark)",
            region = "europe"
        ),
        Dns.plaintextDns(
            id = "verisign",
            ips = listOf("64.6.64.6", "64.6.65.6"),
            label = "Verisign Public DNS"
        )
    )

    // All special cases and removed legacy needs to be handled here to not cause crashes when migrating
    fun byId(dnsId: DnsId) = when(dnsId) {
        network.id -> network
        else -> getDns().firstOrNull { it.id == dnsId } ?: cloudflare // Fallback for previously selected removed DNS
    }
}
