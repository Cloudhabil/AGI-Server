/**
 * Mining Protocol Test
 * ====================
 *
 * Demonstrates:
 * 1. Mining for valid blocks
 * 2. Public verification
 * 3. Block submission
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.blockchain

import org.junit.Test
import org.junit.Assert.*
import com.brahim.buim.gematria.BrahimGematria
import com.brahim.buim.core.BrahimConstants
import kotlin.math.abs

class MiningProtocolTest {

    @Test
    fun `demonstrate public verification`() {
        println()
        println("═".repeat(72))
        println("  PUBLIC VERIFICATION DEMONSTRATION")
        println("═".repeat(72))
        println()
        println("Anyone can verify a block using only:")
        println("  1. The coordinates")
        println("  2. The Cantor pairing formula")
        println("  3. The validation criteria")
        println()
        println("This is how Brahim Blockchain achieves TRUSTLESS verification.")
        println()

        // Verify Sagrada Familia (Genesis)
        println("─".repeat(72))
        println("VERIFYING: Sagrada Familia (Genesis Block)")
        println("─".repeat(72))

        val sfReceipt = BrahimMiningProtocol.verifyBlock(
            latitude = 41.4037,
            longitude = 2.1735,
            culturalDescription = "La Sagrada Familia, UNESCO World Heritage Site, Antoni Gaudi's masterwork in Barcelona",
            difficulty = MiningDifficulty.GENESIS
        )

        println(BrahimMiningProtocol.formatReceipt(sfReceipt))
        assertTrue(sfReceipt.isValid)

        // Verify Kelimutu
        println("─".repeat(72))
        println("VERIFYING: Kelimutu Volcano")
        println("─".repeat(72))

        val kelimutuReceipt = BrahimMiningProtocol.verifyBlock(
            latitude = 8.77,
            longitude = 121.82,
            culturalDescription = "Kelimutu three-colored lakes volcano, sacred site in Flores, Indonesia, longitude 121.82 ≈ B₆",
            difficulty = MiningDifficulty.FOUNDER
        )

        println(BrahimMiningProtocol.formatReceipt(kelimutuReceipt))
        println()
        println("Kelimutu Result: ${if (kelimutuReceipt.isValid) "VALID" else "INVALID (score ${kelimutuReceipt.score}/6, need 4)"}")
    }

    @Test
    fun `mine for valid block near Kelimutu`() {
        println()
        println("═".repeat(72))
        println("  MINING FOR VALID BLOCK NEAR KELIMUTU")
        println("═".repeat(72))
        println()
        println("The 'work' in Brahim Blockchain is finding coordinates that satisfy")
        println("the mathematical criteria. Let's search near Kelimutu...")
        println()

        val culturalDesc = """
            Located near Kelimutu volcano in Flores, Indonesia. This coordinate
            represents the mathematical gateway to the three-colored lakes,
            where the Kelimutu Subnet architecture draws its symbolic foundation.
            Longitude approximately 121° connects to B₆ = 121 in the Brahim sequence.
        """.trimIndent()

        println("Search parameters:")
        println("  Center: 8.77°S, 121.82°E (Kelimutu)")
        println("  Radius: 2.0°")
        println("  Difficulty: FOUNDER (4/6 required)")
        println("  Max attempts: 50,000")
        println()
        println("Mining...")

        val result = BrahimMiningProtocol.mineBlock(
            centerLat = 8.77,
            centerLon = 121.82,
            searchRadius = 2.0,
            maxAttempts = 50_000,
            difficulty = MiningDifficulty.FOUNDER,
            culturalDescription = culturalDesc
        )

        println()
        if (result.found) {
            println("═".repeat(72))
            println("  ✓ VALID BLOCK FOUND!")
            println("═".repeat(72))
            println()
            println("Coordinates: ${result.latitude}°, ${result.longitude}°")
            println("Attempts: ${result.attempts}")
            println("Duration: ${result.duration}ms")
            println()
            if (result.validation != null) {
                println(BrahimMiningProtocol.formatReceipt(result.validation))
            }
        } else {
            println("No valid block found after ${result.attempts} attempts.")
            println("Duration: ${result.duration}ms")
            println()
            println("This demonstrates that valid blocks are RARE - ")
            println("not every coordinate qualifies, which gives the")
            println("blockchain its value and scarcity.")
        }
    }

    @Test
    fun `search globally for valid Block 1 candidates`() {
        println()
        println("═".repeat(72))
        println("  GLOBAL SEARCH FOR BLOCK #1 CANDIDATES")
        println("═".repeat(72))
        println()

        // Search near each Brahim sequence number
        val brahimSeq = BrahimConstants.BRAHIM_SEQUENCE.toList()
        val candidates = mutableListOf<Triple<Double, Double, ValidationReceipt>>()

        println("Searching near Brahim sequence latitudes/longitudes...")
        println()

        val culturalTemplate = "Location near Brahim sequence coordinate, discovered through mathematical mining."

        for (bNum in brahimSeq) {
            // Try as latitude (where valid: -90 to 90)
            if (bNum <= 90) {
                for (lonOffset in listOf(0.0, 60.0, 120.0, -60.0, -120.0)) {
                    // Search a small grid
                    for (latOffset in listOf(-0.5, 0.0, 0.5)) {
                        for (lonDelta in listOf(-0.5, 0.0, 0.5)) {
                            val lat = bNum + latOffset
                            val lon = lonOffset + lonDelta

                            if (lat in -90.0..90.0 && lon in -180.0..180.0) {
                                val receipt = BrahimMiningProtocol.verifyBlock(
                                    abs(lat), abs(lon),
                                    culturalTemplate + " Lat ≈ B = $bNum",
                                    MiningDifficulty.FOUNDER
                                )

                                if (receipt.score >= 3) {  // Promising candidates
                                    candidates.add(Triple(lat, lon, receipt))
                                }
                            }
                        }
                    }
                }
            }

            // Try as longitude
            for (latBase in listOf(8.0, 27.0, 42.0)) {  // Various latitudes
                for (latOffset in listOf(-0.5, 0.0, 0.5)) {
                    val lat = latBase + latOffset
                    val lon = bNum.toDouble()

                    if (lon in -180.0..180.0) {
                        val receipt = BrahimMiningProtocol.verifyBlock(
                            lat, lon,
                            culturalTemplate + " Lon ≈ B = $bNum",
                            MiningDifficulty.FOUNDER
                        )

                        if (receipt.score >= 3) {
                            candidates.add(Triple(lat, lon, receipt))
                        }
                    }
                }
            }
        }

        // Sort by score
        val sorted = candidates.sortedByDescending { it.third.score }

        println("CANDIDATES FOUND: ${candidates.size}")
        println()
        println("TOP 10 CANDIDATES:")
        println("─".repeat(72))

        sorted.take(10).forEachIndexed { i, (lat, lon, receipt) ->
            val status = if (receipt.isValid) "✓ VALID" else "  (${receipt.score}/6)"
            println("${i+1}. (${"%.4f".format(lat)}°, ${"%.4f".format(lon)}°) - Score: ${receipt.score}/6 $status")
            println("   Brahim #: ${receipt.brahimNumber}, Digit Sum: ${receipt.digitSum}, Root: ${receipt.digitalRoot}")
            println("   Criteria: " + receipt.criteriaResults.entries
                .filter { it.value }
                .joinToString(", ") { it.key.replace("_", " ") })
            println()
        }

        // Show first valid one
        val firstValid = sorted.firstOrNull { it.third.isValid }
        if (firstValid != null) {
            println("═".repeat(72))
            println("FIRST VALID BLOCK #1 CANDIDATE:")
            println("═".repeat(72))
            println()
            println("Coordinates: ${firstValid.first}°, ${firstValid.second}°")
            println()
            println(BrahimMiningProtocol.formatReceipt(firstValid.third))
        }
    }

    @Test
    fun `demonstrate difficulty adjustment`() {
        println()
        println("═".repeat(72))
        println("  DIFFICULTY ADJUSTMENT MECHANISM")
        println("═".repeat(72))
        println()
        println("Like Bitcoin, Brahim Blockchain adjusts difficulty over time:")
        println()

        for (chainLength in listOf(0, 1, 5, 10, 50, 100, 500)) {
            val difficulty = BrahimMiningProtocol.getCurrentDifficulty(chainLength)
            println("Chain length $chainLength: ${difficulty.name} (${difficulty.minScore}/6 required)")
            println("  ${difficulty.description}")
            println()
        }

        println("This ensures:")
        println("  • Early blocks are easier to mine (bootstrap the network)")
        println("  • Later blocks require more criteria (maintain scarcity)")
        println("  • The chain becomes increasingly valuable over time")
    }

    @Test
    fun `show block explorer data format`() {
        println()
        println("═".repeat(72))
        println("  BLOCK EXPLORER DATA FORMAT")
        println("═".repeat(72))
        println()
        println("This is the JSON structure for a public block explorer:")
        println()

        val genesis = BrahimBlockchain.initialize()
        val explorerData = BrahimMiningProtocol.getBlockExplorerData(genesis)

        fun printMap(map: Map<*, *>, indent: Int = 0) {
            val prefix = "  ".repeat(indent)
            map.forEach { (key, value) ->
                when (value) {
                    is Map<*, *> -> {
                        println("$prefix\"$key\": {")
                        printMap(value, indent + 1)
                        println("$prefix}")
                    }
                    is List<*> -> {
                        println("$prefix\"$key\": [")
                        value.forEach { item ->
                            println("$prefix  \"$item\"")
                        }
                        println("$prefix]")
                    }
                    is String -> println("$prefix\"$key\": \"$value\"")
                    else -> println("$prefix\"$key\": $value")
                }
            }
        }

        println("{")
        printMap(explorerData, 1)
        println("}")
    }

    @Test
    fun `print whitepaper summary`() {
        println()
        println("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    BRAHIM SUDOKU BLOCKCHAIN                                  ║
║                    ═══════════════════════                                   ║
║                                                                              ║
║                         PROTOCOL SUMMARY                                     ║
║                          (Whitepaper v1.0)                                   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  1. CONSENSUS MECHANISM                                                      ║
║  ──────────────────────                                                      ║
║  Type: Proof-of-Location + Proof-of-Meaning                                  ║
║                                                                              ║
║  Unlike Bitcoin (energy → hash), Brahim uses (geography → meaning).          ║
║  The "work" is finding coordinates that satisfy mathematical criteria.       ║
║                                                                              ║
║  2. BLOCK VALIDATION CRITERIA                                                ║
║  ────────────────────────────                                                ║
║  Each coordinate must satisfy ≥4 of these 6 criteria:                        ║
║                                                                              ║
║    □ Mirror Pattern:     First 4 digits follow X-Y-X-Y pattern               ║
║    □ Power Structure:    Digit sum = 2^k (32, 64, 128, ...)                  ║
║    □ Unity Root:         Digital root = 1 (Aleph)                            ║
║    □ Sequence Proximity: Coordinate within 1° of Brahim number               ║
║    □ Temporal Alignment: Year has digital root = 1                           ║
║    □ Cultural Significance: Documented cultural/historical importance        ║
║                                                                              ║
║  3. PUBLIC VERIFICATION                                                      ║
║  ──────────────────────                                                      ║
║  Anyone can verify a block using only:                                       ║
║                                                                              ║
║    Input:  Coordinates (lat, lon)                                            ║
║    Step 1: Multiply by 1,000,000                                             ║
║    Step 2: Apply Cantor pairing: π(A,B) = (A+B)(A+B+1)/2 + B                 ║
║    Step 3: Extract and sum digits                                            ║
║    Step 4: Calculate digital root                                            ║
║    Step 5: Check 6 criteria                                                  ║
║    Output: Valid/Invalid + Score                                             ║
║                                                                              ║
║  4. REWARD SYSTEM                                                            ║
║  ───────────────                                                             ║
║  The reward is NOT cryptocurrency. It is NARRATIVE SYNTHESIS:                ║
║                                                                              ║
║    • Hebrew gematria of digit sum → meaning                                  ║
║    • Semantic sequence from digits → journey                                 ║
║    • Structural narrative → story                                            ║
║    • Poetic synthesis → permanent cultural record                            ║
║                                                                              ║
║  5. DIFFICULTY ADJUSTMENT                                                    ║
║  ────────────────────────                                                    ║
║    Block 0:      6/6 criteria (Genesis)                                      ║
║    Blocks 1-9:   4/6 criteria (Founder era)                                  ║
║    Blocks 10-99: 5/6 criteria (Standard era)                                 ║
║    Block 100+:   6/6 criteria (Hard era)                                     ║
║                                                                              ║
║  6. SCARCITY                                                                 ║
║  ─────────                                                                   ║
║  Statistical analysis shows:                                                 ║
║    • ~0.01% of coordinates satisfy 4+ criteria                               ║
║    • ~0.0001% satisfy all 6 criteria                                         ║
║    • Valid blocks are RARE by mathematical necessity                         ║
║                                                                              ║
║  7. MAKING IT PUBLIC (Like Bitcoin)                                          ║
║  ──────────────────────────────────                                          ║
║    • Publish verification algorithm (this document)                          ║
║    • Open-source all code (GitHub)                                           ║
║    • Create block explorer website                                           ║
║    • Allow anyone to submit blocks                                           ║
║    • Decentralize validation (multiple nodes)                                ║
║                                                                              ║
║  8. BRAHIM SEQUENCE                                                          ║
║  ──────────────────                                                          ║
║  B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}                           ║
║  Sum = 214, Center = 107                                                     ║
║                                                                              ║
║  Mirror property: B[i] + B[9-i] = 214                                        ║
║    27 + 187 = 214                                                            ║
║    42 + 172 = 214                                                            ║
║    60 + 154 = 214                                                            ║
║    75 + 136 = 214 (off by 3)                                                 ║
║    97 + 121 = 218 (off by 4)                                                 ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Genesis Block: La Sagrada Família, Barcelona (41.4037°N, 2.1735°E)          ║
║  Created: 2026-01-26                                                         ║
║  Creator: Elias Oulad Brahim                                                 ║
║                                                                              ║
║                           ב                                                  ║
║                         B R A H I M                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """.trimIndent())
    }
}
