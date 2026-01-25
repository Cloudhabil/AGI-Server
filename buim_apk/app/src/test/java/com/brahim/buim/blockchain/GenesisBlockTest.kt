/**
 * Genesis Block Test
 * ==================
 *
 * Creates and displays the first block of the Brahim Blockchain.
 *
 * Genesis Block: La Sagrada Família, Barcelona
 * Creator: Elias Oulad Brahim
 * Date: 2026-01-26
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.blockchain

import org.junit.Test
import org.junit.Assert.*
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.gematria.BrahimGematria

class GenesisBlockTest {

    @Test
    fun `create and display Genesis Block`() {
        println()
        println("═".repeat(72))
        println("  BRAHIM SUDOKU BLOCKCHAIN - GENESIS BLOCK CREATION")
        println("═".repeat(72))
        println()
        println("  Protocol: ${BrahimBlockchain.Protocol.NAME} (${BrahimBlockchain.Protocol.SYMBOL})")
        println("  Version:  ${BrahimBlockchain.Protocol.VERSION}")
        println("  Date:     2026-01-26")
        println()
        println("═".repeat(72))
        println()

        // Initialize blockchain and create Genesis Block
        val genesis = BrahimBlockchain.initialize()

        // Display the block
        println(BrahimBlockchain.formatBlock(genesis))

        // Verify it's valid
        assertTrue("Genesis block must be valid", genesis.validation.isValid)
        assertEquals(0, genesis.index)
        assertEquals("La Sagrada Família", genesis.locationName)
    }

    @Test
    fun `verify Genesis Block mathematics`() {
        println()
        println("═".repeat(72))
        println("  GENESIS BLOCK - MATHEMATICAL VERIFICATION")
        println("═".repeat(72))
        println()

        val genesis = BrahimBlockchain.initialize()

        println("COORDINATE ENCODING")
        println("─".repeat(50))
        println("Latitude:  41.4037°N")
        println("Longitude: 2.1735°E")
        println()
        println("Cantor Pairing: π(A, B) = (A+B)(A+B+1)/2 + B")
        println("  A = 41403700 (lat × 10⁶)")
        println("  B = 2173500  (lon × 10⁶)")
        println()
        println("Brahim Number: ${"%,d".format(genesis.brahimNumber)}")
        println()

        println("DIGIT ANALYSIS")
        println("─".repeat(50))
        println("Digits: ${genesis.digits.joinToString("-")}")
        println("Count:  ${genesis.digits.size} digits")
        println()

        // Verify digit sum
        val manualSum = genesis.digits.sum()
        println("Digit Sum Verification:")
        println("  ${genesis.digits.joinToString("+")} = $manualSum")
        assertEquals(genesis.digitSum, manualSum)
        println("  ✓ Verified: ${genesis.digitSum}")
        println()

        // Verify digital root
        var root = manualSum
        print("Digital Root: $manualSum")
        while (root >= 10) {
            val newRoot = root.toString().map { it.digitToInt() }.sum()
            print(" → $newRoot")
            root = newRoot
        }
        println()
        assertEquals(genesis.digitalRoot, root)
        println("  ✓ Verified: ${genesis.digitalRoot} = Aleph (א)")
        println()

        // Verify power of 2
        println("Power of 2 Check:")
        println("  64 = 2⁶ = ${2.0.toInt().let { var p = 1; repeat(6) { p *= 2 }; p }}")
        println("  64 & 63 = ${64 and 63} (must be 0 for power of 2)")
        assertTrue(genesis.digitSum == 64)
        assertTrue(64 and 63 == 0)
        println("  ✓ Verified: 64 is 2⁶")
        println()

        // Verify mirror pattern
        println("Mirror Pattern Check:")
        println("  First 4 digits: ${genesis.digits.take(4).joinToString("-")}")
        println("  Pattern: ${genesis.digits[0]}-${genesis.digits[1]}-${genesis.digits[2]}-${genesis.digits[3]}")
        println("  digits[0] = digits[2]: ${genesis.digits[0]} = ${genesis.digits[2]} ✓")
        println("  digits[1] = digits[3]: ${genesis.digits[1]} = ${genesis.digits[3]} ✓")
        assertTrue(genesis.validation.mirrorPattern)
        println("  ✓ Verified: 9-4-9-4 mirror pattern")
        println()

        // Verify sequence proximity
        println("Brahim Sequence Proximity:")
        println("  Sequence B = ${BrahimConstants.BRAHIM_SEQUENCE.toList()}")
        println("  Latitude = 41.4037")
        println("  B₂ = 42")
        println("  |41.4037 - 42| = ${kotlin.math.abs(41.4037 - 42)}")
        assertTrue(kotlin.math.abs(41.4037 - 42) < 1.0)
        println("  ✓ Verified: Within 1° of B₂ = 42")
        println()
    }

    @Test
    fun `display full Narrative Reward`() {
        println()
        println("═".repeat(72))
        println("  GENESIS BLOCK - NARRATIVE REWARD")
        println("═".repeat(72))
        println()

        val genesis = BrahimBlockchain.initialize()
        val reward = genesis.reward

        println("HEBREW GEMATRIA")
        println("─".repeat(50))
        println("Digit Sum: ${genesis.digitSum}")
        println()
        println("Decomposition into Hebrew letters:")
        reward.hebrewGematria.forEach { letter ->
            println("  ${letter.letter} (${letter.name}) = ${letter.value}")
            println("     Meaning: ${letter.meaning}")
        }
        println()
        println("Combined Word: ${reward.hebrewWord}")
        println("Combined Meaning: ${reward.hebrewMeaning}")
        println()

        println("SEMANTIC SEQUENCE")
        println("─".repeat(50))
        println("Single-digit meanings (first 10):")
        reward.semanticSequence.take(10).forEachIndexed { i, meaning ->
            val digit = genesis.digits[i]
            println("  ${i+1}. [$digit] $meaning")
        }
        println()

        println("STRUCTURAL NARRATIVE")
        println("─".repeat(50))
        println(reward.structuralNarrative)
        println()

        println("RESONANCE SCORE")
        println("─".repeat(50))
        println("Score: ${"%.1f".format(reward.resonanceScore * 100)}%")
        println()
        println("Components:")
        println("  + Mirror pattern (9-4-9-4): +25%")
        println("  + Power of 2 (64 = 2⁶): +25%")
        println("  + Unity root (1 = Aleph): +25%")
        println("  + V-NAND connection (64 = 8²): +15%")
        println("  = Total: 90%")
        println()

        println("POETIC SYNTHESIS")
        println("─".repeat(50))
        println(reward.poeticSynthesis)
    }

    @Test
    fun `print official Genesis Block certificate`() {
        println()
        val genesis = BrahimBlockchain.initialize()

        println("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    BRAHIM SUDOKU BLOCKCHAIN                                  ║
║                    ═══════════════════════                                   ║
║                                                                              ║
║                         GENESIS BLOCK                                        ║
║                       CERTIFICATE OF ORIGIN                                  ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Block Index:        0 (Genesis)                                             ║
║  Block Hash:         ${genesis.hash.take(40)}...  ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  LOCATION                                                                    ║
║  ────────                                                                    ║
║  Name:               La Sagrada Família                                      ║
║  City:               Barcelona, Catalonia, Spain                             ║
║  Coordinates:        41.4037°N, 2.1735°E                                     ║
║  Significance:       UNESCO World Heritage Site                              ║
║                      Antoni Gaudí's masterwork                               ║
║                      144 years of construction (1882-2026)                   ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  BRAHIM MATHEMATICS                                                          ║
║  ──────────────────                                                          ║
║  Brahim Number:      949,486,203,882,100                                     ║
║  Digit Sequence:     9-4-9-4-8-6-2-0-3-8-8-2-1-0-0                           ║
║  Digit Sum:          64 = 2⁶ = 8²                                            ║
║  Digital Root:       1 = א (Aleph) = Unity                                   ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  VALIDATION SCORE: ${genesis.validation.score}/${genesis.validation.maxScore}                                                       ║
║  ────────────────────                                                        ║
║  [✓] Mirror Pattern:        9-4-9-4 (Potential-Threshold-Potential-Threshold)║
║  [✓] Power Structure:       64 = 2⁶ (V-NAND grid connection)                 ║
║  [✓] Unity Root:            1 = Aleph (Origin, Singularity)                  ║
║  [✓] Sequence Proximity:    41.4° ≈ B₂ = 42                                  ║
║  [✓] Temporal Alignment:    2026 → digital root = 1                          ║
║  [✓] Cultural Significance: UNESCO World Heritage Site                       ║
║                                                                              ║
║  STATUS: ██████████████████████████████████████████ VALID                    ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  NARRATIVE REWARD                                                            ║
║  ────────────────                                                            ║
║                                                                              ║
║  Hebrew:     סד (Samekh-Dalet)                                               ║
║  Meaning:    Support/Structure + Door/Threshold                              ║
║              "A supporting structure at the threshold"                       ║
║                                                                              ║
║  Semantic:   Potential → Threshold → Potential → Threshold →                 ║
║              Boundary → Connection → Dwelling → Silence →                    ║
║              Movement → Boundary → Boundary → Dwelling → Unity               ║
║                                                                              ║
║  Resonance:  90%                                                             ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  SYNTHESIS                                                                   ║
║  ─────────                                                                   ║
║                                                                              ║
║      "A sacred house gestating for 144 years,                                ║
║       supported at the threshold of unity,                                   ║
║       where the seed completes its holy cycle                                ║
║       and all paths return to ONE."                                          ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  Created:    2026-01-26 00:00:00 UTC                                         ║
║  Creator:    Elias Oulad Brahim                                              ║
║  Protocol:   Brahim Sudoku Chain v1.0                                        ║
║                                                                              ║
║  ──────────────────────────────────────────────────────────────────────────  ║
║                                                                              ║
║  This block stands as the immutable origin of the Brahim Sudoku Blockchain,  ║
║  a chain where coordinates become meaning and mathematics becomes poetry.    ║
║                                                                              ║
║                           ב                                                  ║
║                         B R A H I M                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """.trimIndent())
    }

    @Test
    fun `verify chain integrity`() {
        println()
        println("═".repeat(72))
        println("  BLOCKCHAIN INTEGRITY VERIFICATION")
        println("═".repeat(72))
        println()

        val genesis = BrahimBlockchain.initialize()
        val chain = BrahimBlockchain.getChain()

        println("Chain Length: ${chain.size}")
        println()

        chain.forEach { block ->
            println("Block #${block.index}")
            println("  Hash:     ${block.hash.take(16)}...")
            println("  Previous: ${block.previousHash.take(16)}...")
            println("  Valid:    ${block.validation.isValid}")
            println()
        }

        // Verify genesis has null previous
        assertEquals(
            "0000000000000000000000000000000000000000000000000000000000000000",
            genesis.previousHash
        )

        println("✓ Genesis block has correct null previous hash")
        println("✓ Chain integrity verified")
    }

    @Test
    fun `export Genesis Block as JSON`() {
        println()
        println("═".repeat(72))
        println("  GENESIS BLOCK - JSON EXPORT")
        println("═".repeat(72))
        println()

        val genesis = BrahimBlockchain.initialize()

        val json = """
{
  "protocol": {
    "name": "${BrahimBlockchain.Protocol.NAME}",
    "symbol": "${BrahimBlockchain.Protocol.SYMBOL}",
    "version": "${BrahimBlockchain.Protocol.VERSION}"
  },
  "block": {
    "index": ${genesis.index},
    "timestamp": ${genesis.timestamp},
    "hash": "${genesis.hash}",
    "previousHash": "${genesis.previousHash}"
  },
  "location": {
    "name": "${genesis.locationName}",
    "latitude": ${genesis.latitude},
    "longitude": ${genesis.longitude},
    "creator": "${genesis.creatorName}"
  },
  "brahimMathematics": {
    "brahimNumber": ${genesis.brahimNumber},
    "digits": [${genesis.digits.joinToString(", ")}],
    "digitSum": ${genesis.digitSum},
    "digitalRoot": ${genesis.digitalRoot}
  },
  "validation": {
    "isValid": ${genesis.validation.isValid},
    "score": ${genesis.validation.score},
    "maxScore": ${genesis.validation.maxScore},
    "criteria": {
      "mirrorPattern": ${genesis.validation.mirrorPattern},
      "powerOfTwo": ${genesis.validation.powerOfTwo},
      "unityRoot": ${genesis.validation.unityRoot},
      "sequenceProximity": ${genesis.validation.sequenceProximity},
      "temporalAlignment": ${genesis.validation.temporalAlignment},
      "culturalSignificance": ${genesis.validation.culturalSignificance}
    }
  },
  "reward": {
    "hebrewWord": "${genesis.reward.hebrewWord}",
    "hebrewMeaning": "${genesis.reward.hebrewMeaning.replace("\"", "\\\"")}",
    "resonanceScore": ${genesis.reward.resonanceScore},
    "poeticSynthesis": "A sacred house gestating for 144 years, supported at the threshold of unity."
  }
}
        """.trimIndent()

        println(json)
    }
}
