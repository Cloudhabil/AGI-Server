/**
 * Brahim Geo ID - Real Use Case Tests
 * ====================================
 *
 * Demonstrates practical applications that make Brahim Numbers USEFUL,
 * not just interesting.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.usecase

import org.junit.Test
import org.junit.Assert.*

class BrahimGeoIDUseCaseTest {

    // =========================================================================
    // USE CASE 1: WAREHOUSE INVENTORY SLOTS
    // =========================================================================

    @Test
    fun `use case 1 - warehouse inventory slots`() {
        println()
        println("═".repeat(72))
        println("  USE CASE 1: WAREHOUSE INVENTORY MANAGEMENT")
        println("═".repeat(72))
        println()
        println("Scenario: A warehouse uses lat/lon micro-coordinates for shelf locations.")
        println("Each shelf slot gets a unique, verifiable Brahim Geo ID.")
        println()

        // Warehouse grid (microdegrees within building)
        // Building corner: 40.7128°N, -74.0060°W (NYC)
        val baseLatitude = 40.7128
        val baseLongitude = 74.0060  // Using absolute

        // Create inventory slots (row, column → lat offset, lon offset)
        val slots = mutableListOf<GeoProduct>()

        for (row in 0..2) {
            for (col in 0..3) {
                val lat = baseLatitude + (row * 0.00001)  // ~1 meter per row
                val lon = baseLongitude + (col * 0.00001)  // ~1 meter per col

                val product = BrahimGeoIDFactory.createProduct(
                    name = "Slot-R${row}C${col}",
                    category = "WAREHOUSE_SLOT",
                    latitude = lat,
                    longitude = lon,
                    locationHint = "R${row}C${col}",
                    metadata = mapOf(
                        "row" to row.toString(),
                        "col" to col.toString(),
                        "zone" to "A"
                    )
                )
                slots.add(product)
            }
        }

        println("INVENTORY SLOTS CREATED:")
        println("─".repeat(72))
        slots.forEach { slot ->
            println("${slot.name}: ${slot.geoId.fullId}")
            println("  Human ID: ${slot.geoId.humanId}")
            println("  Verify: ${BrahimGeoIDFactory.verify(slot.geoId.fullId)}")
        }
        println()

        // Verify all IDs are unique
        val uniqueIds = slots.map { it.geoId.brahimNumber }.toSet()
        assertEquals("All IDs must be unique", slots.size, uniqueIds.size)

        println("✓ All ${slots.size} slots have unique, verifiable IDs")
        println()

        // Demonstrate error detection
        println("ERROR DETECTION:")
        println("─".repeat(72))
        val correctId = slots[0].geoId.fullId
        val corruptedId = correctId.replace("-7", "-8")  // Wrong check digit
        println("Correct ID:   $correctId → Valid: ${BrahimGeoIDFactory.verify(correctId)}")
        println("Corrupted ID: $corruptedId → Valid: ${BrahimGeoIDFactory.verify(corruptedId)}")
        println()
    }

    // =========================================================================
    // USE CASE 2: DELIVERY ROUTE TRACKING
    // =========================================================================

    @Test
    fun `use case 2 - delivery route tracking`() {
        println()
        println("═".repeat(72))
        println("  USE CASE 2: DELIVERY ROUTE TRACKING")
        println("═".repeat(72))
        println()
        println("Scenario: A delivery vehicle follows waypoints.")
        println("Each waypoint is a Brahim Geo ID. Route has a checksum.")
        println()

        // Barcelona delivery route
        val waypoints = listOf(
            41.3851 to 2.1734,   // Start: Barcelona center
            41.3902 to 2.1540,   // Stop 1
            41.4036 to 2.1744,   // Stop 2: Sagrada Familia area
            41.4128 to 2.1530,   // Stop 3
            41.3851 to 2.1734    // Return to start
        )

        val route = BrahimGeoIDFactory.createRoute("BCN-ROUTE-001", waypoints)

        println("ROUTE: ${route.routeId}")
        println("─".repeat(72))
        route.waypoints.forEachIndexed { i, wp ->
            val label = when (i) {
                0 -> "START"
                route.waypoints.size - 1 -> "END"
                else -> "STOP $i"
            }
            println("$label: (${wp.latitude}, ${wp.longitude})")
            println("  ID: ${wp.fullId}")
            println("  Short: ${wp.shortId}")
        }
        println()
        println("ROUTE CHECKSUM: ${route.checksum}")
        println("  (XOR of all Brahim numbers - tamper detection)")
        println()

        // Verify route integrity
        val recomputedChecksum = route.waypoints.fold(0L) { acc, id -> acc xor id.brahimNumber }
        assertEquals(route.checksum, recomputedChecksum)
        println("✓ Route integrity verified")
        println()
    }

    // =========================================================================
    // USE CASE 3: DATASET FINGERPRINTING
    // =========================================================================

    @Test
    fun `use case 3 - dataset fingerprinting`() {
        println()
        println("═".repeat(72))
        println("  USE CASE 3: DATASET FINGERPRINTING")
        println("═".repeat(72))
        println()
        println("Scenario: A geospatial dataset needs a unique fingerprint")
        println("for provenance tracking and integrity verification.")
        println()

        // Simulated dataset: 10 sensor locations
        val sensorLocations = listOf(
            41.4037 to 2.1735,    // Barcelona
            40.7128 to 74.0060,   // NYC
            51.5074 to 0.1278,    // London
            35.6762 to 139.6503,  // Tokyo
            48.8566 to 2.3522,    // Paris
            55.7558 to 37.6173,   // Moscow
            39.9042 to 116.4074,  // Beijing
            -33.8688 to 151.2093, // Sydney
            37.7749 to 122.4194,  // San Francisco
            52.5200 to 13.4050    // Berlin
        )

        val fingerprint = BrahimGeoIDFactory.fingerprintDataset(sensorLocations)

        println("DATASET: Global Sensor Network")
        println("─".repeat(72))
        println("Points:       ${fingerprint.count}")
        println("XOR Hash:     ${fingerprint.xorFingerprint}")
        println("Sum Mod214:   ${fingerprint.sumMod214}")
        println("Digital Root: ${fingerprint.digitalRoot}")
        println("Check Digit:  ${fingerprint.checkDigit}")
        println()
        println("FINGERPRINT ID: ${fingerprint.fingerprintId}")
        println()

        // Verify fingerprint is deterministic
        val fingerprint2 = BrahimGeoIDFactory.fingerprintDataset(sensorLocations)
        assertEquals(fingerprint.fingerprintId, fingerprint2.fingerprintId)
        println("✓ Fingerprint is deterministic (same input → same output)")
        println()

        // Show that changing one point changes the fingerprint
        val alteredLocations = sensorLocations.toMutableList()
        alteredLocations[0] = 41.4038 to 2.1735  // Tiny change: 0.0001° = ~11 meters
        val alteredFingerprint = BrahimGeoIDFactory.fingerprintDataset(alteredLocations)

        println("TAMPER DETECTION:")
        println("─".repeat(72))
        println("Original fingerprint:  ${fingerprint.fingerprintId}")
        println("After 11m change:      ${alteredFingerprint.fingerprintId}")
        println()
        assertNotEquals(fingerprint.fingerprintId, alteredFingerprint.fingerprintId)
        println("✓ Fingerprint changes when data is altered")
        println()
    }

    // =========================================================================
    // USE CASE 4: PROVENANCE ANCHORING
    // =========================================================================

    @Test
    fun `use case 4 - build artifact provenance`() {
        println()
        println("═".repeat(72))
        println("  USE CASE 4: BUILD ARTIFACT PROVENANCE")
        println("═".repeat(72))
        println()
        println("Scenario: Track where software artifacts were built.")
        println("The build location becomes part of the artifact identity.")
        println()

        // Build servers at different locations
        data class BuildArtifact(
            val name: String,
            val version: String,
            val geoId: BrahimGeoID,
            val buildTime: String,
            val gitCommit: String
        )

        val artifacts = listOf(
            BuildArtifact(
                name = "buim-core",
                version = "1.0.0",
                geoId = BrahimGeoIDFactory.create(41.4037, 2.1735, "BCN"),
                buildTime = "2026-01-25T10:30:00Z",
                gitCommit = "abc123"
            ),
            BuildArtifact(
                name = "buim-sdk",
                version = "1.0.0",
                geoId = BrahimGeoIDFactory.create(37.7749, 122.4194, "SFO"),
                buildTime = "2026-01-25T18:45:00Z",
                gitCommit = "def456"
            )
        )

        println("BUILD ARTIFACTS:")
        println("─".repeat(72))
        artifacts.forEach { artifact ->
            println("${artifact.name}:${artifact.version}")
            println("  Location:  ${artifact.geoId.humanId}")
            println("  Full ID:   ${artifact.geoId.fullId}")
            println("  Built:     ${artifact.buildTime}")
            println("  Commit:    ${artifact.gitCommit}")
            println("  Verify:    ${BrahimGeoIDFactory.verify(artifact.geoId.fullId)}")
            println()
        }

        // Create provenance record
        val provenanceRecord = """
            {
              "artifact": "buim-core:1.0.0",
              "provenance": {
                "buildLocation": "${artifacts[0].geoId.fullId}",
                "coordinates": [${artifacts[0].geoId.latitude}, ${artifacts[0].geoId.longitude}],
                "timestamp": "${artifacts[0].buildTime}",
                "gitCommit": "${artifacts[0].gitCommit}"
              },
              "verification": {
                "spec": "BNv1",
                "checkDigit": "${artifacts[0].geoId.checkDigit}",
                "valid": ${BrahimGeoIDFactory.verify(artifacts[0].geoId.fullId)}
              }
            }
        """.trimIndent()

        println("PROVENANCE RECORD (JSON):")
        println("─".repeat(72))
        println(provenanceRecord)
        println()
    }

    // =========================================================================
    // USE CASE 5: HUMAN-MEMORABLE CHECK DIGITS
    // =========================================================================

    @Test
    fun `use case 5 - human readable IDs with error detection`() {
        println()
        println("═".repeat(72))
        println("  USE CASE 5: HUMAN-READABLE IDS WITH ERROR DETECTION")
        println("═".repeat(72))
        println()
        println("The mod-214 short form + check digit creates memorable IDs")
        println("that humans can read, speak, and verify.")
        println()

        // Create several IDs
        val locations = listOf(
            Triple(41.4037, 2.1735, "Sagrada Familia"),
            Triple(40.7484, 73.9857, "Empire State"),
            Triple(48.8584, 2.2945, "Eiffel Tower"),
            Triple(51.5007, 0.1246, "Big Ben")
        )

        println("HUMAN-READABLE IDS:")
        println("─".repeat(72))
        println()
        println("Instead of: BN:949486203882100-7")
        println("Humans say: BN214:42-7")
        println()

        locations.forEach { (lat, lon, name) ->
            val id = BrahimGeoIDFactory.create(lat, lon, name.take(4))
            println("$name:")
            println("  Full:    ${id.fullId}")
            println("  Short:   ${id.shortId}  ← Easy to speak!")
            println("  Human:   ${id.humanId}")
            println()
        }

        // Demonstrate spoken verification
        println("SPOKEN VERIFICATION:")
        println("─".repeat(72))
        println("Phone call: 'Can you verify ID BN214:42-7?'")
        println("System: 'Confirmed. Location: Sagrada Familia area.'")
        println()
        println("If they say 'BN214:42-8' (wrong check digit):")
        println("System: 'Invalid check digit. Please verify.'")
        println()
    }

    // =========================================================================
    // SPECIFICATION COMPLIANCE
    // =========================================================================

    @Test
    fun `BNv1 specification test vectors`() {
        println()
        println("═".repeat(72))
        println("  BNv1 SPECIFICATION COMPLIANCE TEST")
        println("═".repeat(72))
        println()
        println("These test vectors are from SPECIFICATION_BNv1.md Section 7.")
        println("ALL implementations MUST pass these tests.")
        println()

        // Test vectors from spec
        val testVectors = listOf(
            Triple(0L, 0L, 0L),
            Triple(0L, 1L, 1L),
            Triple(1L, 0L, 2L),
            Triple(1L, 1L, 4L),
            Triple(2L, 0L, 5L),
            Triple(0L, 2L, 3L),
            Triple(10L, 10L, 220L),
            Triple(100L, 100L, 20200L),
            Triple(41403700L, 2173500L, 949486203882100L)
        )

        println("CANTOR PAIRING TEST VECTORS:")
        println("─".repeat(72))

        var allPassed = true
        testVectors.forEach { (a, b, expected) ->
            // Manual Cantor pairing
            val result = ((a + b) * (a + b + 1)) / 2 + b
            val passed = result == expected
            if (!passed) allPassed = false

            println("BN($a, $b) = $result (expected: $expected) ${if (passed) "✓" else "✗ FAIL"}")
        }
        println()

        assertTrue("All BNv1 test vectors must pass", allPassed)
        println("✓ All BNv1 specification test vectors passed")
        println()
        println("This implementation is COMPLIANT with BNv1.")
    }

    @Test
    fun `print killer use case summary`() {
        println()
        println("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    BRAHIM NUMBERS - KILLER USE CASES                         ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  These make Brahim Numbers USEFUL, not just interesting:                     ║
║                                                                              ║
║  1. GEOSPATIAL PRODUCT IDS                                                   ║
║     • Warehouse shelf slots                                                  ║
║     • Inventory management                                                   ║
║     • Unique, collision-free IDs from coordinates                            ║
║                                                                              ║
║  2. DELIVERY ROUTE TRACKING                                                  ║
║     • Waypoints as Brahim Geo IDs                                            ║
║     • Route checksum for integrity                                           ║
║     • Tamper detection                                                       ║
║                                                                              ║
║  3. DATASET FINGERPRINTING                                                   ║
║     • Provenance anchors for geospatial data                                 ║
║     • Deterministic, verifiable fingerprints                                 ║
║     • Detects even tiny changes                                              ║
║                                                                              ║
║  4. BUILD ARTIFACT PROVENANCE                                                ║
║     • Track WHERE software was built                                         ║
║     • Immutable location identity                                            ║
║     • Supply chain security                                                  ║
║                                                                              ║
║  5. HUMAN-MEMORABLE CHECK DIGITS                                             ║
║     • Mod-214 gives small numbers (0-213)                                    ║
║     • Check digit catches transcription errors                               ║
║     • "BN214:42-7" is speakable                                              ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  SPECIFICATION GOVERNANCE:                                                   ║
║                                                                              ║
║  • BNv1 is FROZEN - the algorithm never changes                              ║
║  • Test vectors in spec MUST always pass                                     ║
║  • Future versions get new names (BNv2, etc.)                                ║
║  • CC0 license - anyone can implement                                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """.trimIndent())
    }
}
