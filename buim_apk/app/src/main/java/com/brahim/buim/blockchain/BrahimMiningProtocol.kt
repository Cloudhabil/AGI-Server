/**
 * Brahim Mining Protocol
 * =======================
 *
 * Proof-of-Location + Proof-of-Meaning consensus mechanism.
 *
 * Unlike Bitcoin's Proof-of-Work (energy → hash):
 *   Brahim uses Proof-of-Location (geography → meaning)
 *
 * The "work" is finding coordinates that satisfy mathematical criteria.
 * The "reward" is the narrative synthesis permanently recorded on-chain.
 *
 * PUBLIC VERIFICATION: Anyone can verify a block using only:
 *   1. The coordinates
 *   2. The Cantor pairing formula
 *   3. The validation criteria
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.blockchain

import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.gematria.BrahimGematria
import java.security.MessageDigest
import java.time.Instant
import kotlin.math.abs
import kotlin.random.Random

/**
 * Mining difficulty levels.
 */
enum class MiningDifficulty(
    val minScore: Int,
    val description: String
) {
    GENESIS(6, "All 6 criteria required"),
    FOUNDER(4, "4+ criteria (founding era)"),
    STANDARD(5, "5+ criteria (standard era)"),
    HARD(6, "All 6 criteria (hard era)")
}

/**
 * Block submission for validation.
 */
data class BlockSubmission(
    val locationName: String,
    val latitude: Double,
    val longitude: Double,
    val culturalDescription: String,
    val creatorName: String,
    val creatorPublicKey: String,  // For attribution
    val timestamp: Long = System.currentTimeMillis(),
    val nonce: Long = 0  // Optional: for additional proof-of-work
)

/**
 * Validation receipt (publicly verifiable).
 */
data class ValidationReceipt(
    val submissionHash: String,
    val isValid: Boolean,
    val score: Int,
    val maxScore: Int,
    val difficulty: MiningDifficulty,
    val brahimNumber: Long,
    val digitSum: Int,
    val digitalRoot: Int,
    val criteriaResults: Map<String, Boolean>,
    val verificationSteps: List<String>,  // Public verification trail
    val timestamp: Long
)

/**
 * Mining result.
 */
data class MiningResult(
    val found: Boolean,
    val latitude: Double,
    val longitude: Double,
    val attempts: Long,
    val duration: Long,
    val validation: ValidationReceipt?
)

/**
 * Brahim Mining Protocol - Public Verification System.
 */
object BrahimMiningProtocol {

    /**
     * Current network difficulty (adjusts based on chain length).
     */
    fun getCurrentDifficulty(chainLength: Int): MiningDifficulty {
        return when {
            chainLength == 0 -> MiningDifficulty.GENESIS
            chainLength < 10 -> MiningDifficulty.FOUNDER
            chainLength < 100 -> MiningDifficulty.STANDARD
            else -> MiningDifficulty.HARD
        }
    }

    /**
     * PUBLIC VERIFICATION FUNCTION
     *
     * Anyone can verify a block using only the coordinates.
     * This is the core of the trustless system.
     */
    fun verifyBlock(
        latitude: Double,
        longitude: Double,
        culturalDescription: String,
        difficulty: MiningDifficulty
    ): ValidationReceipt {
        val steps = mutableListOf<String>()

        // Step 1: Validate coordinate ranges
        steps.add("STEP 1: Coordinate Validation")
        steps.add("  Latitude: $latitude (valid: ${latitude in -90.0..90.0})")
        steps.add("  Longitude: $longitude (valid: ${longitude in -180.0..180.0})")

        if (latitude !in -90.0..90.0 || longitude !in -180.0..180.0) {
            return createInvalidReceipt(latitude, longitude, steps, "Invalid coordinates")
        }

        // Step 2: Calculate Brahim Number (Cantor Pairing)
        steps.add("")
        steps.add("STEP 2: Brahim Number Calculation")
        steps.add("  Formula: π(A, B) = (A + B)(A + B + 1)/2 + B")

        val scale = 1_000_000L
        val A = (abs(latitude) * scale).toLong()
        val B = (abs(longitude) * scale).toLong()

        steps.add("  A = |$latitude| × $scale = $A")
        steps.add("  B = |$longitude| × $scale = $B")

        val brahimNumber = BrahimGematria.coordinatesToBrahimNumber(abs(latitude), abs(longitude))
        steps.add("  Brahim Number = $brahimNumber")

        // Step 3: Extract digits
        steps.add("")
        steps.add("STEP 3: Digit Extraction")
        val digits = BrahimGematria.getSingleDigits(brahimNumber)
        steps.add("  Digits: ${digits.joinToString("-")}")

        // Step 4: Calculate digit sum
        steps.add("")
        steps.add("STEP 4: Digit Sum")
        val digitSum = digits.sum()
        steps.add("  Sum: ${digits.joinToString("+")} = $digitSum")

        // Step 5: Calculate digital root
        steps.add("")
        steps.add("STEP 5: Digital Root")
        var root = digitSum
        val rootSteps = mutableListOf(digitSum.toString())
        while (root >= 10) {
            root = root.toString().map { it.digitToInt() }.sum()
            rootSteps.add(root.toString())
        }
        steps.add("  Path: ${rootSteps.joinToString(" → ")}")
        steps.add("  Digital Root = $root")

        // Step 6: Evaluate criteria
        steps.add("")
        steps.add("STEP 6: Criteria Evaluation")

        val criteria = mutableMapOf<String, Boolean>()

        // Criterion 1: Mirror pattern
        val hasMirror = digits.size >= 4 && digits[0] == digits[2] && digits[1] == digits[3]
        criteria["mirror_pattern"] = hasMirror
        steps.add("  [${if (hasMirror) "✓" else "✗"}] Mirror Pattern: ${digits.take(4).joinToString("-")}")

        // Criterion 2: Power of 2
        val isPowerOf2 = digitSum >= 32 && digitSum > 0 && (digitSum and (digitSum - 1)) == 0
        criteria["power_of_two"] = isPowerOf2
        steps.add("  [${if (isPowerOf2) "✓" else "✗"}] Power of 2: $digitSum ${if (isPowerOf2) "= 2^${log2(digitSum)}" else ""}")

        // Criterion 3: Unity root
        val isUnity = root == 1
        criteria["unity_root"] = isUnity
        steps.add("  [${if (isUnity) "✓" else "✗"}] Unity Root: $root ${if (isUnity) "= Aleph" else ""}")

        // Criterion 4: Sequence proximity
        val nearLat = BrahimConstants.BRAHIM_SEQUENCE.any { abs(abs(latitude) - it) < 1.0 }
        val nearLon = BrahimConstants.BRAHIM_SEQUENCE.any { abs(abs(longitude) - it) < 1.0 }
        val nearSequence = nearLat || nearLon
        criteria["sequence_proximity"] = nearSequence
        val seqNote = when {
            nearLat -> "lat ≈ ${BrahimConstants.BRAHIM_SEQUENCE.minByOrNull { abs(abs(latitude) - it) }}"
            nearLon -> "lon ≈ ${BrahimConstants.BRAHIM_SEQUENCE.minByOrNull { abs(abs(longitude) - it) }}"
            else -> ""
        }
        steps.add("  [${if (nearSequence) "✓" else "✗"}] Sequence Proximity: $seqNote")

        // Criterion 5: Temporal alignment (2026)
        val year = Instant.now().atZone(java.time.ZoneId.of("UTC")).year
        val yearRoot = BrahimGematria.digitalRoot(year.toLong())
        val temporalOk = yearRoot == 1
        criteria["temporal_alignment"] = temporalOk
        steps.add("  [${if (temporalOk) "✓" else "✗"}] Temporal: $year → root $yearRoot")

        // Criterion 6: Cultural significance
        val culturalOk = culturalDescription.length >= 50
        criteria["cultural_significance"] = culturalOk
        steps.add("  [${if (culturalOk) "✓" else "✗"}] Cultural: ${culturalDescription.length} chars")

        // Calculate score
        val score = criteria.values.count { it }
        steps.add("")
        steps.add("STEP 7: Final Score")
        steps.add("  Score: $score/${criteria.size}")
        steps.add("  Required: ${difficulty.minScore} (${difficulty.name})")
        steps.add("  Result: ${if (score >= difficulty.minScore) "VALID ✓" else "INVALID ✗"}")

        val submissionHash = sha256("$latitude$longitude${System.currentTimeMillis()}")

        return ValidationReceipt(
            submissionHash = submissionHash,
            isValid = score >= difficulty.minScore,
            score = score,
            maxScore = criteria.size,
            difficulty = difficulty,
            brahimNumber = brahimNumber,
            digitSum = digitSum,
            digitalRoot = root,
            criteriaResults = criteria,
            verificationSteps = steps,
            timestamp = System.currentTimeMillis()
        )
    }

    /**
     * MINING FUNCTION
     *
     * Search for valid coordinates near a target location.
     * This is the "work" in Proof-of-Location.
     */
    fun mineBlock(
        centerLat: Double,
        centerLon: Double,
        searchRadius: Double = 1.0,
        maxAttempts: Long = 100_000,
        difficulty: MiningDifficulty = MiningDifficulty.FOUNDER,
        culturalDescription: String
    ): MiningResult {
        val startTime = System.currentTimeMillis()
        var attempts = 0L

        val random = Random(System.currentTimeMillis())

        while (attempts < maxAttempts) {
            attempts++

            // Generate random coordinate within search radius
            val lat = centerLat + (random.nextDouble() - 0.5) * 2 * searchRadius
            val lon = centerLon + (random.nextDouble() - 0.5) * 2 * searchRadius

            // Validate
            val receipt = verifyBlock(abs(lat), abs(lon), culturalDescription, difficulty)

            if (receipt.isValid) {
                return MiningResult(
                    found = true,
                    latitude = lat,
                    longitude = lon,
                    attempts = attempts,
                    duration = System.currentTimeMillis() - startTime,
                    validation = receipt
                )
            }
        }

        return MiningResult(
            found = false,
            latitude = centerLat,
            longitude = centerLon,
            attempts = attempts,
            duration = System.currentTimeMillis() - startTime,
            validation = null
        )
    }

    /**
     * SUBMIT BLOCK TO NETWORK
     *
     * Validates and adds block to chain if valid.
     */
    fun submitBlock(submission: BlockSubmission): Pair<Boolean, String> {
        val chain = BrahimBlockchain.getChain()
        val difficulty = getCurrentDifficulty(chain.size)

        val receipt = verifyBlock(
            submission.latitude,
            submission.longitude,
            submission.culturalDescription,
            difficulty
        )

        if (!receipt.isValid) {
            return false to "Block validation failed: score ${receipt.score}/${receipt.maxScore}, required ${difficulty.minScore}"
        }

        val newBlock = BrahimBlockchain.addBlock(
            locationName = submission.locationName,
            latitude = submission.latitude,
            longitude = submission.longitude,
            culturalDescription = submission.culturalDescription,
            creatorName = submission.creatorName
        )

        return if (newBlock != null) {
            true to "Block #${newBlock.index} added successfully"
        } else {
            false to "Failed to add block to chain"
        }
    }

    /**
     * FORMAT VERIFICATION RECEIPT
     *
     * Human-readable public verification output.
     */
    fun formatReceipt(receipt: ValidationReceipt): String {
        return buildString {
            appendLine("╔══════════════════════════════════════════════════════════════════╗")
            appendLine("║           BRAHIM BLOCKCHAIN - PUBLIC VERIFICATION                ║")
            appendLine("╠══════════════════════════════════════════════════════════════════╣")
            appendLine("║")
            appendLine("║  Submission Hash: ${receipt.submissionHash.take(32)}...")
            appendLine("║  Timestamp: ${Instant.ofEpochMilli(receipt.timestamp)}")
            appendLine("║")
            appendLine("║  ────────────────────────────────────────────────────────────────")
            appendLine("║")
            receipt.verificationSteps.forEach { step ->
                appendLine("║  $step")
            }
            appendLine("║")
            appendLine("║  ────────────────────────────────────────────────────────────────")
            appendLine("║")
            appendLine("║  VERIFICATION RESULT: ${if (receipt.isValid) "✓ VALID" else "✗ INVALID"}")
            appendLine("║")
            appendLine("╚══════════════════════════════════════════════════════════════════╝")
        }
    }

    /**
     * GENERATE BLOCK EXPLORER DATA
     *
     * Data structure for public block explorer.
     */
    fun getBlockExplorerData(block: BrahimBlock): Map<String, Any> {
        return mapOf(
            "block" to mapOf(
                "index" to block.index,
                "hash" to block.hash,
                "previousHash" to block.previousHash,
                "timestamp" to block.timestamp,
                "timestampHuman" to Instant.ofEpochMilli(block.timestamp).toString()
            ),
            "location" to mapOf(
                "name" to block.locationName,
                "latitude" to block.latitude,
                "longitude" to block.longitude,
                "creator" to block.creatorName
            ),
            "mathematics" to mapOf(
                "brahimNumber" to block.brahimNumber,
                "digits" to block.digits,
                "digitSum" to block.digitSum,
                "digitalRoot" to block.digitalRoot
            ),
            "validation" to mapOf(
                "isValid" to block.validation.isValid,
                "score" to block.validation.score,
                "maxScore" to block.validation.maxScore,
                "criteria" to mapOf(
                    "mirrorPattern" to block.validation.mirrorPattern,
                    "powerOfTwo" to block.validation.powerOfTwo,
                    "unityRoot" to block.validation.unityRoot,
                    "sequenceProximity" to block.validation.sequenceProximity,
                    "temporalAlignment" to block.validation.temporalAlignment,
                    "culturalSignificance" to block.validation.culturalSignificance
                )
            ),
            "reward" to mapOf(
                "hebrewWord" to block.reward.hebrewWord,
                "hebrewMeaning" to block.reward.hebrewMeaning,
                "resonanceScore" to block.reward.resonanceScore
            ),
            "verification" to mapOf(
                "formula" to "π(A, B) = (A + B)(A + B + 1)/2 + B",
                "instructions" to listOf(
                    "1. Take coordinates (lat, lon)",
                    "2. Multiply each by 1,000,000",
                    "3. Apply Cantor pairing formula",
                    "4. Extract digits and sum them",
                    "5. Calculate digital root (repeated sum until single digit)",
                    "6. Check all 6 criteria",
                    "7. Score ≥ 4 = valid block"
                )
            )
        )
    }

    // Helper functions

    private fun createInvalidReceipt(
        lat: Double,
        lon: Double,
        steps: List<String>,
        error: String
    ): ValidationReceipt {
        return ValidationReceipt(
            submissionHash = sha256("$lat$lon$error"),
            isValid = false,
            score = 0,
            maxScore = 6,
            difficulty = MiningDifficulty.FOUNDER,
            brahimNumber = 0,
            digitSum = 0,
            digitalRoot = 0,
            criteriaResults = emptyMap(),
            verificationSteps = steps + listOf("ERROR: $error"),
            timestamp = System.currentTimeMillis()
        )
    }

    private fun sha256(input: String): String {
        val bytes = MessageDigest.getInstance("SHA-256").digest(input.toByteArray())
        return bytes.joinToString("") { "%02x".format(it) }
    }

    private fun log2(n: Int): Int {
        var count = 0
        var num = n
        while (num > 1) {
            num /= 2
            count++
        }
        return count
    }
}
