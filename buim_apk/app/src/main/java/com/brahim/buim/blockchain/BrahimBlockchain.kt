/**
 * Brahim Sudoku Blockchain
 * ========================
 *
 * A novel blockchain where:
 * - Proof-of-Location: Blocks are geographic coordinates
 * - Proof-of-Meaning: Must satisfy mathematical criteria
 * - Reward: Narrative Synthesis (computational semiotics)
 *
 * Protocol Version: 1.0
 * Genesis Block: Sagrada Familia, Barcelona
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.blockchain

import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.gematria.BrahimGematria
import com.brahim.buim.gematria.HebrewLetter
import java.security.MessageDigest
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import kotlin.math.abs
import kotlin.math.pow

/**
 * Narrative Reward - The "currency" of the Brahim Blockchain.
 * Not financial value, but MEANING.
 */
data class NarrativeReward(
    val hebrewGematria: List<HebrewLetter>,
    val hebrewWord: String,
    val hebrewMeaning: String,
    val semanticSequence: List<String>,
    val structuralNarrative: String,
    val resonanceScore: Double,
    val poeticSynthesis: String
)

/**
 * Block validation result.
 */
data class BlockValidation(
    val isValid: Boolean,
    val mirrorPattern: Boolean,
    val powerOfTwo: Boolean,
    val unityRoot: Boolean,
    val sequenceProximity: Boolean,
    val temporalAlignment: Boolean,
    val culturalSignificance: Boolean,
    val score: Int,
    val maxScore: Int,
    val errors: List<String>
)

/**
 * A single block in the Brahim Blockchain.
 */
data class BrahimBlock(
    val index: Int,
    val timestamp: Long,
    val locationName: String,
    val latitude: Double,
    val longitude: Double,
    val culturalDescription: String,
    val creatorName: String,
    val previousHash: String,
    val brahimNumber: Long,
    val digitSum: Int,
    val digitalRoot: Int,
    val digits: List<Int>,
    val validation: BlockValidation,
    val reward: NarrativeReward,
    val hash: String,
    val nonce: Int = 0
)

/**
 * Brahim Blockchain - Proof of Location + Proof of Meaning.
 */
object BrahimBlockchain {

    private val chain = mutableListOf<BrahimBlock>()
    private const val GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    /**
     * Protocol constants.
     */
    object Protocol {
        const val VERSION = "1.0"
        const val NAME = "Brahim Sudoku Chain"
        const val SYMBOL = "BSC"
        const val MIN_SCORE = 4  // Minimum criteria to pass
        const val MAX_SCORE = 6
    }

    /**
     * Initialize blockchain with Genesis Block.
     */
    fun initialize(): BrahimBlock {
        if (chain.isNotEmpty()) {
            return chain[0]
        }

        val genesis = createGenesisBlock()
        chain.add(genesis)
        return genesis
    }

    /**
     * Create the Genesis Block - Sagrada Familia.
     */
    private fun createGenesisBlock(): BrahimBlock {
        val lat = 41.4037
        val lon = 2.1735
        val locationName = "La Sagrada Família"
        val culturalDescription = """
            The Basílica de la Sagrada Família, designed by Antoni Gaudí.
            Construction began in 1882, expected completion in 2026.
            A UNESCO World Heritage Site and Barcelona's most iconic landmark.
            144 years of construction = 12² = F₁₂ (Fibonacci).
        """.trimIndent()
        val creator = "Elias Oulad Brahim"
        val timestamp = 1737849600000L  // 2026-01-26 00:00:00 UTC

        return createBlock(
            index = 0,
            timestamp = timestamp,
            locationName = locationName,
            latitude = lat,
            longitude = lon,
            culturalDescription = culturalDescription,
            creatorName = creator,
            previousHash = GENESIS_HASH
        )
    }

    /**
     * Create a new block.
     */
    fun createBlock(
        index: Int,
        timestamp: Long,
        locationName: String,
        latitude: Double,
        longitude: Double,
        culturalDescription: String,
        creatorName: String,
        previousHash: String
    ): BrahimBlock {
        // Calculate Brahim Number
        val brahimNumber = BrahimGematria.coordinatesToBrahimNumber(latitude, longitude)
        val digits = BrahimGematria.getSingleDigits(brahimNumber)
        val digitSum = BrahimGematria.digitSum(brahimNumber)
        val digitalRoot = BrahimGematria.digitalRoot(brahimNumber)

        // Validate block
        val validation = validateBlock(latitude, longitude, brahimNumber, digits, digitSum, digitalRoot, timestamp, culturalDescription)

        // Generate reward (even if invalid, for demonstration)
        val reward = generateReward(brahimNumber, digits, digitSum, digitalRoot, locationName)

        // Calculate block hash
        val blockData = "$index$timestamp$locationName$latitude$longitude$previousHash$brahimNumber"
        val hash = sha256(blockData)

        return BrahimBlock(
            index = index,
            timestamp = timestamp,
            locationName = locationName,
            latitude = latitude,
            longitude = longitude,
            culturalDescription = culturalDescription,
            creatorName = creatorName,
            previousHash = previousHash,
            brahimNumber = brahimNumber,
            digitSum = digitSum,
            digitalRoot = digitalRoot,
            digits = digits,
            validation = validation,
            reward = reward,
            hash = hash
        )
    }

    /**
     * Validate a block against protocol criteria.
     */
    private fun validateBlock(
        latitude: Double,
        longitude: Double,
        brahimNumber: Long,
        digits: List<Int>,
        digitSum: Int,
        digitalRoot: Int,
        timestamp: Long,
        culturalDescription: String
    ): BlockValidation {
        val errors = mutableListOf<String>()

        // Criterion 1: Mirror pattern in first 4 digits
        val mirrorPattern = digits.size >= 4 &&
            digits[0] == digits[2] && digits[1] == digits[3]
        if (!mirrorPattern) errors.add("No mirror pattern in digits[0:3]")

        // Criterion 2: Digit sum is power of 2 (≥32)
        val powerOfTwo = digitSum >= 32 && digitSum > 0 && (digitSum and (digitSum - 1)) == 0
        if (!powerOfTwo) errors.add("Digit sum $digitSum is not a power of 2 (≥32)")

        // Criterion 3: Digital root is 1 (Aleph/Unity)
        val unityRoot = digitalRoot == 1
        if (!unityRoot) errors.add("Digital root $digitalRoot ≠ 1 (Aleph)")

        // Criterion 4: Latitude OR Longitude near Brahim sequence number
        val latNearSequence = BrahimConstants.BRAHIM_SEQUENCE.any { abs(latitude - it) < 1.0 }
        val lonNearSequence = BrahimConstants.BRAHIM_SEQUENCE.any { abs(longitude - it) < 1.0 }
        val sequenceProximity = latNearSequence || lonNearSequence
        if (!sequenceProximity) errors.add("Neither coordinate within 1° of any Brahim number")

        // Criterion 5: Temporal alignment (year digital root = 1)
        val year = Instant.ofEpochMilli(timestamp)
            .atZone(ZoneId.of("UTC"))
            .year
        val yearDigitalRoot = BrahimGematria.digitalRoot(year.toLong())
        val temporalAlignment = yearDigitalRoot == 1
        if (!temporalAlignment) errors.add("Year $year has digital root $yearDigitalRoot ≠ 1")

        // Criterion 6: Cultural significance (non-empty description)
        val culturalSignificance = culturalDescription.length >= 50
        if (!culturalSignificance) errors.add("Cultural description too short (<50 chars)")

        // Calculate score
        var score = 0
        if (mirrorPattern) score++
        if (powerOfTwo) score++
        if (unityRoot) score++
        if (sequenceProximity) score++
        if (temporalAlignment) score++
        if (culturalSignificance) score++

        val isValid = score >= Protocol.MIN_SCORE

        return BlockValidation(
            isValid = isValid,
            mirrorPattern = mirrorPattern,
            powerOfTwo = powerOfTwo,
            unityRoot = unityRoot,
            sequenceProximity = sequenceProximity,
            temporalAlignment = temporalAlignment,
            culturalSignificance = culturalSignificance,
            score = score,
            maxScore = Protocol.MAX_SCORE,
            errors = errors
        )
    }

    /**
     * Generate the Narrative Reward.
     */
    private fun generateReward(
        brahimNumber: Long,
        digits: List<Int>,
        digitSum: Int,
        digitalRoot: Int,
        locationName: String
    ): NarrativeReward {
        // Hebrew gematria of digit sum
        val hebrewLetters = BrahimGematria.digitSumToHebrew(digitSum)
        val hebrewWord = hebrewLetters.map { it.letter }.joinToString("")
        val hebrewMeaning = hebrewLetters.joinToString(" + ") { "${it.name} (${it.meaning})" }

        // Semantic sequence from single digits
        val semanticSequence = digits.map { BrahimGematria.singleDigitMeaning(it) }

        // Structural narrative
        val structuralNarrative = generateStructuralNarrative(digits, locationName)

        // Resonance score (0-1)
        val resonanceScore = calculateResonanceScore(digits, digitSum, digitalRoot)

        // Poetic synthesis
        val poeticSynthesis = generatePoeticSynthesis(
            hebrewLetters, digits, locationName, digitSum, digitalRoot
        )

        return NarrativeReward(
            hebrewGematria = hebrewLetters,
            hebrewWord = hebrewWord,
            hebrewMeaning = hebrewMeaning,
            semanticSequence = semanticSequence,
            structuralNarrative = structuralNarrative,
            resonanceScore = resonanceScore,
            poeticSynthesis = poeticSynthesis
        )
    }

    /**
     * Generate structural narrative from digit sequence.
     */
    private fun generateStructuralNarrative(digits: List<Int>, locationName: String): String {
        val meanings = mapOf(
            0 to "silence",
            1 to "unity",
            2 to "dwelling",
            3 to "movement",
            4 to "threshold",
            5 to "revelation",
            6 to "connection",
            7 to "division",
            8 to "boundary",
            9 to "potential"
        )

        val journey = digits.take(10).mapNotNull { meanings[it] }

        return buildString {
            appendLine("THE JOURNEY OF $locationName")
            appendLine()
            journey.forEachIndexed { i, meaning ->
                append("Step ${i + 1}: ")
                append(meaning.replaceFirstChar { it.uppercase() })
                if (i < journey.size - 1) appendLine(" →")
                else appendLine(".")
            }
        }
    }

    /**
     * Calculate resonance score based on mathematical properties.
     */
    private fun calculateResonanceScore(digits: List<Int>, digitSum: Int, digitalRoot: Int): Double {
        var score = 0.0

        // Mirror pattern bonus
        if (digits.size >= 4 && digits[0] == digits[2] && digits[1] == digits[3]) {
            score += 0.25
        }

        // Power of 2 bonus
        if (digitSum > 0 && (digitSum and (digitSum - 1)) == 0) {
            score += 0.25
        }

        // Unity root bonus
        if (digitalRoot == 1) {
            score += 0.25
        }

        // 64 = 8² specific bonus (V-NAND connection)
        if (digitSum == 64) {
            score += 0.15
        }

        // Fibonacci digit sum bonus
        val fibs = listOf(1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144)
        if (digitSum in fibs) {
            score += 0.10
        }

        return score.coerceIn(0.0, 1.0)
    }

    /**
     * Generate poetic synthesis - the crown of the reward.
     */
    private fun generatePoeticSynthesis(
        hebrewLetters: List<HebrewLetter>,
        digits: List<Int>,
        locationName: String,
        digitSum: Int,
        digitalRoot: Int
    ): String {
        val hebrewNames = hebrewLetters.map { it.name }
        val hebrewMeanings = hebrewLetters.map { it.meaning.split(",")[0].trim() }

        // Extract key themes from first 4 digits
        val themes = digits.take(4).map { d ->
            when (d) {
                0 -> "void"
                1 -> "origin"
                2 -> "house"
                3 -> "bridge"
                4 -> "door"
                5 -> "breath"
                6 -> "link"
                7 -> "sword"
                8 -> "wall"
                9 -> "seed"
                else -> "mystery"
            }
        }

        return buildString {
            appendLine("╔════════════════════════════════════════════════════════════════╗")
            appendLine("║              NARRATIVE SYNTHESIS: $locationName")
            appendLine("╠════════════════════════════════════════════════════════════════╣")
            appendLine("║")
            appendLine("║  In the language of ${hebrewNames.joinToString("-")}:")
            appendLine("║")
            appendLine("║      \"${hebrewMeanings.joinToString(" and ")}\"")
            appendLine("║")
            appendLine("║  The digits speak of ${themes.joinToString(", then ")}.")
            appendLine("║")
            if (digitSum == 64) {
                appendLine("║  Sixty-four: the grid of eight by eight,")
                appendLine("║  Where V-NAND voxels hold memory's weight.")
            }
            appendLine("║")
            if (digitalRoot == 1) {
                appendLine("║  All paths return to ONE—")
                appendLine("║  Aleph, the silent breath before creation,")
                appendLine("║  The unity from which all numbers run.")
            }
            appendLine("║")
            appendLine("║  This place stands as witness:")
            appendLine("║  A ${themes[0]} becomes a ${themes[1]},")
            appendLine("║  A ${themes[2]} opens to a ${themes[3]}.")
            appendLine("║")
            appendLine("║  So it was written in coordinates,")
            appendLine("║  So it is sealed in the chain.")
            appendLine("║")
            appendLine("╚════════════════════════════════════════════════════════════════╝")
        }
    }

    /**
     * Get the current chain.
     */
    fun getChain(): List<BrahimBlock> = chain.toList()

    /**
     * Get the latest block.
     */
    fun getLatestBlock(): BrahimBlock? = chain.lastOrNull()

    /**
     * Add a new block to the chain.
     */
    fun addBlock(
        locationName: String,
        latitude: Double,
        longitude: Double,
        culturalDescription: String,
        creatorName: String
    ): BrahimBlock? {
        val previousBlock = getLatestBlock() ?: return null

        val newBlock = createBlock(
            index = previousBlock.index + 1,
            timestamp = System.currentTimeMillis(),
            locationName = locationName,
            latitude = latitude,
            longitude = longitude,
            culturalDescription = culturalDescription,
            creatorName = creatorName,
            previousHash = previousBlock.hash
        )

        if (newBlock.validation.isValid) {
            chain.add(newBlock)
            return newBlock
        }

        return null // Block rejected
    }

    /**
     * SHA-256 hash function.
     */
    private fun sha256(input: String): String {
        val bytes = MessageDigest.getInstance("SHA-256").digest(input.toByteArray())
        return bytes.joinToString("") { "%02x".format(it) }
    }

    /**
     * Format block for display.
     */
    fun formatBlock(block: BrahimBlock): String {
        val dateFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss z")
        val timestamp = Instant.ofEpochMilli(block.timestamp)
            .atZone(ZoneId.of("UTC"))
            .format(dateFormatter)

        return buildString {
            appendLine("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
            appendLine("┃  BRAHIM BLOCKCHAIN - BLOCK #${block.index}".padEnd(69) + "┃")
            appendLine("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
            appendLine("┃")
            appendLine("┃  BLOCK HEADER")
            appendLine("┃  ────────────────────────────────────────────────────────────────")
            appendLine("┃  Index:          ${block.index}")
            appendLine("┃  Timestamp:      $timestamp")
            appendLine("┃  Hash:           ${block.hash.take(32)}...")
            appendLine("┃  Previous Hash:  ${block.previousHash.take(32)}...")
            appendLine("┃")
            appendLine("┃  LOCATION DATA")
            appendLine("┃  ────────────────────────────────────────────────────────────────")
            appendLine("┃  Name:           ${block.locationName}")
            appendLine("┃  Coordinates:    ${block.latitude}°N, ${block.longitude}°E")
            appendLine("┃  Creator:        ${block.creatorName}")
            appendLine("┃")
            appendLine("┃  BRAHIM MATHEMATICS")
            appendLine("┃  ────────────────────────────────────────────────────────────────")
            appendLine("┃  Brahim Number:  ${"%,d".format(block.brahimNumber)}")
            appendLine("┃  Digit Sequence: ${block.digits.joinToString("-")}")
            appendLine("┃  Digit Sum:      ${block.digitSum}")
            appendLine("┃  Digital Root:   ${block.digitalRoot}")
            appendLine("┃")
            appendLine("┃  VALIDATION (${block.validation.score}/${block.validation.maxScore})")
            appendLine("┃  ────────────────────────────────────────────────────────────────")
            appendLine("┃  ${if (block.validation.mirrorPattern) "✓" else "✗"} Mirror Pattern (X-Y-X-Y)")
            appendLine("┃  ${if (block.validation.powerOfTwo) "✓" else "✗"} Digit Sum = 2^k")
            appendLine("┃  ${if (block.validation.unityRoot) "✓" else "✗"} Digital Root = 1 (Aleph)")
            appendLine("┃  ${if (block.validation.sequenceProximity) "✓" else "✗"} Near Brahim Sequence")
            appendLine("┃  ${if (block.validation.temporalAlignment) "✓" else "✗"} Temporal Alignment")
            appendLine("┃  ${if (block.validation.culturalSignificance) "✓" else "✗"} Cultural Significance")
            appendLine("┃")
            appendLine("┃  STATUS: ${if (block.validation.isValid) "✓ VALID BLOCK" else "✗ INVALID"}")
            appendLine("┃")
            appendLine("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
            appendLine("┃  NARRATIVE REWARD")
            appendLine("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
            appendLine("┃")
            appendLine("┃  Hebrew Word:    ${block.reward.hebrewWord}")
            appendLine("┃  Meaning:        ${block.reward.hebrewMeaning}")
            appendLine("┃")
            appendLine("┃  Resonance:      ${"%.1f".format(block.reward.resonanceScore * 100)}%")
            appendLine("┃")
            appendLine("┃  SEMANTIC SEQUENCE:")
            block.reward.semanticSequence.take(5).forEach { meaning ->
                appendLine("┃    → $meaning")
            }
            appendLine("┃")
            appendLine("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
            appendLine()
            appendLine(block.reward.poeticSynthesis)
        }
    }
}
