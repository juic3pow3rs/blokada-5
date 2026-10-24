/*
 * This file is part of Blokada.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

package repository

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class DnsDataSourceTest {
    @Test fun blokadaDnsRemainsSelectable() {
        assertTrue(DnsDataSource.getDns().any { it.id == DnsDataSource.blocka.id })
    }

    @Test fun plusDnsRemainsAvailableInternally() {
        assertEquals("blocka2", DnsDataSource.blocka.id)
        assertTrue(DnsDataSource.blocka.plusIps?.isNotEmpty() == true)
    }

    @Test fun unknownLegacyDnsFallsBackToCloudflare() {
        assertEquals(DnsDataSource.cloudflare, DnsDataSource.byId("some-removed-legacy-dns"))
    }

    @Test fun selectableListHasUniqueIds() {
        val ids = DnsDataSource.getDns().map { it.id }
        assertEquals(ids.size, ids.toSet().size)
    }
}
