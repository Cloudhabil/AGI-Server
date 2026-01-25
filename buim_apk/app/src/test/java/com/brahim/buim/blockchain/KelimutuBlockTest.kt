/**
 * Kelimutu Block Validation Test
 * ===============================
 *
 * Validates Kelimutu volcano coordinates as Block #1 of the Brahim Blockchain.
 *
 * Kelimutu: Three-colored lakes volcano in Flores, Indonesia
 * Coordinates: 8.77°S, 121.82°E
 * Note: Longitude 121.82 ≈ B₆ = 121 in Brahim sequence
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.blockchain

import org.junit.Test
import org.junit.Assert.*
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.gematria.BrahimGematria
import kotlin.math.abs

class KelimutuBlockTest {

    companion object {
        // Kelimutu coordinates (from BrahimConstants)
        const val KELIMUTU_LAT = -8.77   // 8.77°S
        const val KELIMUTU_LON = 121.82  // 121.82°E

        // For Cantor pairing, we use absolute values
        const val KELIMUTU_LAT_ABS = 8.77
    }

    @Test
    fun `analyze Kelimutu coordinates`() {
        println()
        println("═".repeat(72))
        println("  KELIMUTU VOLCANO - COORDINATE ANALYSIS")
        println("═".repeat(72))
        println()

        println("LOCATION")
        println("─".repeat(50))
        println("Name:        Kelimutu (Three-Colored Lakes)")
        println("Location:    Flores Island, East Nusa Tenggara, Indonesia")
        println("Coordinates: ${KELIMUTU_LAT}°S, ${KELIMUTU_LON}°E")
        println()

        println("SIGNIFICANCE IN BRAHIM SYSTEM")
        println("─".repeat(50))
        println("The Kelimutu Subnet is named after this volcano.")
        println("Three lakes with different colors share one magma source.")
        println("This models the three-territory intent routing system:")
        println("  • Tiwu Ata Mbupu (Old People) → Literal classification")
        println("  • Tiwu Nuwa Muri (Young Maidens) → Semantic classification")
        println("  • Tiwu Ata Polo (Enchanted) → Structural classification")
        println()

        // Check longitude proximity to B₆ = 121
        val b6 = BrahimConstants.BRAHIM_SEQUENCE[5]  // 121
        val lonDistance = abs(KELIMUTU_LON - b6)
        println("BRAHIM SEQUENCE CONNECTION")
        println("─".repeat(50))
        println("Longitude: $KELIMUTU_LON°E")
        println("B₆ = $b6")
        println("Distance: |$KELIMUTU_LON - $b6| = $lonDistance")
        println("Within 1°: ${lonDistance < 1.0}")
        println()

        assertTrue(lonDistance < 1.0)
    }

    @Test
    fun `calculate Kelimutu Brahim Number`() {
        println()
        println("═".repeat(72))
        println("  KELIMUTU - BRAHIM NUMBER CALCULATION")
        println("═".repeat(72))
        println()

        // Using absolute latitude for Cantor pairing
        val brahimNumber = BrahimGematria.coordinatesToBrahimNumber(KELIMUTU_LAT_ABS, KELIMUTU_LON)
        val digits = BrahimGematria.getSingleDigits(brahimNumber)
        val digitSum = BrahimGematria.digitSum(brahimNumber)
        val digitalRoot = BrahimGematria.digitalRoot(brahimNumber)

        println("CANTOR PAIRING")
        println("─".repeat(50))
        println("Latitude (abs):  $KELIMUTU_LAT_ABS° → ${(KELIMUTU_LAT_ABS * 1_000_000).toLong()}")
        println("Longitude:       $KELIMUTU_LON° → ${(KELIMUTU_LON * 1_000_000).toLong()}")
        println()
        println("Brahim Number:   ${"%,d".format(brahimNumber)}")
        println()

        println("DIGIT ANALYSIS")
        println("─".repeat(50))
        println("Digits:          ${digits.joinToString("-")}")
        println("Count:           ${digits.size}")
        println("Digit Sum:       $digitSum")
        println("Digital Root:    $digitalRoot")
        println()

        // Check criteria
        println("GENESIS BLOCK CRITERIA CHECK")
        println("─".repeat(50))

        // 1. Mirror pattern
        val hasMirror = digits.size >= 4 && digits[0] == digits[2] && digits[1] == digits[3]
        println("1. Mirror pattern (X-Y-X-Y): ${if (hasMirror) "✓ YES" else "✗ NO"}")
        if (digits.size >= 4) {
            println("   First 4 digits: ${digits.take(4).joinToString("-")}")
        }

        // 2. Power of 2
        val isPowerOf2 = digitSum > 0 && (digitSum and (digitSum - 1)) == 0
        println("2. Digit sum power of 2: ${if (isPowerOf2) "✓ YES ($digitSum)" else "✗ NO ($digitSum)"}")

        // 3. Digital root = 1
        val isUnity = digitalRoot == 1
        println("3. Digital root = 1: ${if (isUnity) "✓ YES" else "✗ NO ($digitalRoot)"}")

        // 4. Near Brahim sequence
        val nearLat = BrahimConstants.BRAHIM_SEQUENCE.any { abs(KELIMUTU_LAT_ABS - it) < 1.0 }
        val nearLon = BrahimConstants.BRAHIM_SEQUENCE.any { abs(KELIMUTU_LON - it) < 1.0 }
        println("4. Near Brahim number: ${if (nearLat || nearLon) "✓ YES" else "✗ NO"}")
        if (nearLon) println("   Longitude $KELIMUTU_LON ≈ B₆ = 121")

        // 5. Temporal (2026)
        val year = 2026
        val yearRoot = BrahimGematria.digitalRoot(year.toLong())
        println("5. Temporal alignment (2026): ${if (yearRoot == 1) "✓ YES" else "✗ NO"}")

        // 6. Cultural significance
        println("6. Cultural significance: ✓ YES (Sacred volcano, UNESCO consideration)")

        println()

        // Count score
        var score = 0
        if (hasMirror) score++
        if (isPowerOf2) score++
        if (isUnity) score++
        if (nearLat || nearLon) score++
        if (yearRoot == 1) score++
        score++ // Cultural significance

        println("TOTAL SCORE: $score/6")
        println("MINIMUM REQUIRED: 4/6")
        println("STATUS: ${if (score >= 4) "✓ VALID BLOCK CANDIDATE" else "✗ DOES NOT QUALIFY"}")
        println()
    }

    @Test
    fun `generate Kelimutu Hebrew gematria`() {
        println()
        println("═".repeat(72))
        println("  KELIMUTU - HEBREW GEMATRIA ANALYSIS")
        println("═".repeat(72))
        println()

        val brahimNumber = BrahimGematria.coordinatesToBrahimNumber(KELIMUTU_LAT_ABS, KELIMUTU_LON)
        val digits = BrahimGematria.getSingleDigits(brahimNumber)
        val digitSum = BrahimGematria.digitSum(brahimNumber)
        val digitalRoot = BrahimGematria.digitalRoot(brahimNumber)

        println("Brahim Number: ${"%,d".format(brahimNumber)}")
        println("Digit Sum: $digitSum")
        println()

        // Hebrew decomposition
        val hebrewLetters = BrahimGematria.digitSumToHebrew(digitSum)
        println("HEBREW DECOMPOSITION OF $digitSum")
        println("─".repeat(50))
        hebrewLetters.forEach { letter ->
            println("  ${letter.letter} (${letter.name}) = ${letter.value}")
            println("     ${letter.meaning}")
        }
        println()

        val hebrewWord = hebrewLetters.map { it.letter }.joinToString("")
        println("Hebrew Word: $hebrewWord")
        println()

        // Single digit meanings
        println("SEMANTIC SEQUENCE")
        println("─".repeat(50))
        digits.take(10).forEachIndexed { i, d ->
            println("  ${i+1}. [$d] ${BrahimGematria.singleDigitMeaning(d)}")
        }
        println()

        // Digital root interpretation
        println("DIGITAL ROOT: $digitalRoot")
        println("─".repeat(50))
        val rootMeaning = BrahimGematria.singleDigitMeaning(digitalRoot)
        println("  $rootMeaning")
        println()
    }

    @Test
    fun `create Kelimutu as Block 1`() {
        println()
        println("═".repeat(72))
        println("  CREATING BLOCK #1: KELIMUTU")
        println("═".repeat(72))
        println()

        // First initialize with Genesis
        val genesis = BrahimBlockchain.initialize()
        println("Genesis Block initialized: ${genesis.locationName}")
        println("Genesis Hash: ${genesis.hash.take(32)}...")
        println()

        // Create Kelimutu block
        val kelimutuDescription = """
            Kelimutu is a volcano on Flores Island, Indonesia, containing three
            crater lakes of varying colors. The lakes are the site of sacred
            beliefs among local villagers. The Kelimutu Subnet in the Brahim
            system is named after this volcano, modeling how three different
            classification methods (literal, semantic, structural) share one
            underlying "magma" of truth. Longitude 121.82°E ≈ B₆ = 121.
        """.trimIndent()

        // Try to add Kelimutu block
        val kelimutuBlock = BrahimBlockchain.createBlock(
            index = 1,
            timestamp = System.currentTimeMillis(),
            locationName = "Kelimutu Volcano",
            latitude = KELIMUTU_LAT_ABS,
            longitude = KELIMUTU_LON,
            culturalDescription = kelimutuDescription,
            creatorName = "Elias Oulad Brahim",
            previousHash = genesis.hash
        )

        // Display the block
        println(BrahimBlockchain.formatBlock(kelimutuBlock))

        // Show validation details
        println()
        println("VALIDATION DETAILS")
        println("─".repeat(50))
        println("Score: ${kelimutuBlock.validation.score}/${kelimutuBlock.validation.maxScore}")
        println("Valid: ${kelimutuBlock.validation.isValid}")
        if (kelimutuBlock.validation.errors.isNotEmpty()) {
            println()
            println("Criteria not met:")
            kelimutuBlock.validation.errors.forEach { error ->
                println("  • $error")
            }
        }
        println()
    }

    @Test
    fun `compare Sagrada Familia and Kelimutu`() {
        println()
        println("═".repeat(72))
        println("  BLOCK COMPARISON: GENESIS vs BLOCK #1")
        println("═".repeat(72))
        println()

        val genesis = BrahimBlockchain.initialize()

        val kelimutuBlock = BrahimBlockchain.createBlock(
            index = 1,
            timestamp = System.currentTimeMillis(),
            locationName = "Kelimutu Volcano",
            latitude = KELIMUTU_LAT_ABS,
            longitude = KELIMUTU_LON,
            culturalDescription = "Three-colored lakes volcano, sacred site in Indonesia.",
            creatorName = "Elias Oulad Brahim",
            previousHash = genesis.hash
        )

        println("                          SAGRADA FAMILIA    KELIMUTU")
        println("─".repeat(72))
        println("Location:                 Barcelona          Flores, Indonesia")
        println("Coordinates:              41.40°N, 2.17°E    8.77°S, 121.82°E")
        println("Brahim Number:            ${"%,d".format(genesis.brahimNumber).padEnd(18)} ${"%,d".format(kelimutuBlock.brahimNumber)}")
        println("Digit Sum:                ${genesis.digitSum.toString().padEnd(18)} ${kelimutuBlock.digitSum}")
        println("Digital Root:             ${genesis.digitalRoot.toString().padEnd(18)} ${kelimutuBlock.digitalRoot}")
        println()
        println("CRITERIA:")
        println("  Mirror Pattern:         ${(if (genesis.validation.mirrorPattern) "✓" else "✗").padEnd(18)} ${if (kelimutuBlock.validation.mirrorPattern) "✓" else "✗"}")
        println("  Power of 2:             ${(if (genesis.validation.powerOfTwo) "✓" else "✗").padEnd(18)} ${if (kelimutuBlock.validation.powerOfTwo) "✓" else "✗"}")
        println("  Unity Root:             ${(if (genesis.validation.unityRoot) "✓" else "✗").padEnd(18)} ${if (kelimutuBlock.validation.unityRoot) "✓" else "✗"}")
        println("  Near Brahim Seq:        ${(if (genesis.validation.sequenceProximity) "✓" else "✗").padEnd(18)} ${if (kelimutuBlock.validation.sequenceProximity) "✓" else "✗"}")
        println("  Temporal (2026):        ${(if (genesis.validation.temporalAlignment) "✓" else "✗").padEnd(18)} ${if (kelimutuBlock.validation.temporalAlignment) "✓" else "✗"}")
        println("  Cultural:               ${(if (genesis.validation.culturalSignificance) "✓" else "✗").padEnd(18)} ${if (kelimutuBlock.validation.culturalSignificance) "✓" else "✗"}")
        println()
        println("SCORE:                    ${genesis.validation.score}/6".padEnd(28) + "${kelimutuBlock.validation.score}/6")
        println("STATUS:                   ${(if (genesis.validation.isValid) "VALID" else "INVALID").padEnd(18)} ${if (kelimutuBlock.validation.isValid) "VALID" else "INVALID"}")
        println()
        println("HEBREW WORD:              ${genesis.reward.hebrewWord.padEnd(18)} ${kelimutuBlock.reward.hebrewWord}")
        println("RESONANCE:                ${"%.0f%%".format(genesis.reward.resonanceScore * 100).padEnd(18)} ${"%.0f%%".format(kelimutuBlock.reward.resonanceScore * 100)}")
        println()
    }

    @Test
    fun `print Kelimutu block certificate`() {
        println()

        val genesis = BrahimBlockchain.initialize()
        val kelimutu = BrahimBlockchain.createBlock(
            index = 1,
            timestamp = 1737936000000L,  // 2026-01-27 00:00:00 UTC
            locationName = "Kelimutu Volcano",
            latitude = KELIMUTU_LAT_ABS,
            longitude = KELIMUTU_LON,
            culturalDescription = """
                Kelimutu is a volcano containing three crater lakes of varying colors,
                located on Flores Island, Indonesia. The lakes change color periodically
                due to volcanic activity. Sacred to local Lio people who believe the lakes
                are resting places for souls. The Kelimutu Subnet routing system is named
                after this natural phenomenon. Longitude 121.82°E ≈ B₆ = 121.
            """.trimIndent(),
            creatorName = "Elias Oulad Brahim",
            previousHash = genesis.hash
        )

        val digitSeq = kelimutu.digits.joinToString("-")
        val statusBar = if (kelimutu.validation.isValid) {
            "██████████████████████████████████████████ VALID"
        } else {
            "████████████████████░░░░░░░░░░░░░░░░░░░░░░ PARTIAL (${kelimutu.validation.score}/6)"
        }

        println("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    BRAHIM SUDOKU BLOCKCHAIN                                  ║
║                    ═══════════════════════                                   ║
║                                                                              ║
║                          BLOCK #1                                            ║
║                     CERTIFICATE OF ENTRY                                     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Block Index:        1                                                       ║
║  Block Hash:         ${kelimutu.hash.take(40)}...  ║
║  Previous Hash:      ${kelimutu.previousHash.take(40)}...  ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  LOCATION                                                                    ║
║  ────────                                                                    ║
║  Name:               Kelimutu Volcano (Three-Colored Lakes)                  ║
║  Region:             Flores Island, East Nusa Tenggara, Indonesia            ║
║  Coordinates:        8.77°S, 121.82°E                                        ║
║  Significance:       Sacred volcanic lakes                                   ║
║                      Inspiration for Kelimutu Subnet routing                 ║
║                      Longitude 121.82° ≈ B₆ = 121                            ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  BRAHIM MATHEMATICS                                                          ║
║  ──────────────────                                                          ║
║  Brahim Number:      ${"%,d".format(kelimutu.brahimNumber).padEnd(45)}║
║  Digit Sequence:     ${digitSeq.take(45).padEnd(45)}║
║  Digit Sum:          ${kelimutu.digitSum.toString().padEnd(45)}║
║  Digital Root:       ${kelimutu.digitalRoot.toString().padEnd(45)}║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  VALIDATION SCORE: ${kelimutu.validation.score}/${kelimutu.validation.maxScore}                                                       ║
║  ────────────────────                                                        ║
║  [${if (kelimutu.validation.mirrorPattern) "✓" else "✗"}] Mirror Pattern                                                          ║
║  [${if (kelimutu.validation.powerOfTwo) "✓" else "✗"}] Power Structure (digit sum = 2^k)                                         ║
║  [${if (kelimutu.validation.unityRoot) "✓" else "✗"}] Unity Root (digital root = 1)                                              ║
║  [${if (kelimutu.validation.sequenceProximity) "✓" else "✗"}] Sequence Proximity (lon 121.82 ≈ B₆ = 121)                              ║
║  [${if (kelimutu.validation.temporalAlignment) "✓" else "✗"}] Temporal Alignment (2026)                                               ║
║  [${if (kelimutu.validation.culturalSignificance) "✓" else "✗"}] Cultural Significance                                                    ║
║                                                                              ║
║  STATUS: $statusBar                    ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║                         NARRATIVE REWARD                                     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  HEBREW GEMATRIA                                                             ║
║  ───────────────                                                             ║
║  Word:       ${kelimutu.reward.hebrewWord.padEnd(62)}║
║  Meaning:    ${kelimutu.reward.hebrewMeaning.take(60).padEnd(62)}║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  KELIMUTU SYMBOLISM                                                          ║
║  ──────────────────                                                          ║
║                                                                              ║
║     Three lakes, three colors, one magma source.                             ║
║     Three territories of intent, one truth beneath.                          ║
║                                                                              ║
║     • Tiwu Ata Mbupu (Old People)    → Literal truth                         ║
║     • Tiwu Nuwa Muri (Young Maidens) → Semantic truth                        ║
║     • Tiwu Ata Polo (Enchanted)      → Structural truth                      ║
║                                                                              ║
║     The colors change, but the mountain remains.                             ║
║     The words differ, but the meaning persists.                              ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  Resonance:  ${"%.0f%%".format(kelimutu.reward.resonanceScore * 100).padEnd(62)}║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  Created:    2026-01-27 00:00:00 UTC                                         ║
║  Creator:    Elias Oulad Brahim                                              ║
║  Protocol:   Brahim Sudoku Chain v1.0                                        ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  CHAIN LINK                                                                  ║
║  ──────────                                                                  ║
║  Block #0 (Sagrada Familia) ──────────────────────────► Block #1 (Kelimutu)  ║
║  Barcelona, Spain                                       Flores, Indonesia    ║
║  41.40°N, 2.17°E                                        8.77°S, 121.82°E     ║
║                                                                              ║
║  From the threshold of Unity in the West,                                    ║
║  to the three-colored lakes of the East.                                     ║
║                                                                              ║
║                           ב                                                  ║
║                         B R A H I M                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """.trimIndent())
    }
}
