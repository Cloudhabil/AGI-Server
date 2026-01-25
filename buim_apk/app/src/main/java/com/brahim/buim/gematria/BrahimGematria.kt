/**
 * Brahim Gematria Calculator
 * ==========================
 *
 * Extends the Brahim Calculator to support coordinate-to-symbol mappings,
 * gematria analysis, and sacred geometry connections.
 *
 * Inspired by the Sagrada Familia analysis:
 * Coordinates (41.4037°N, 2.1735°E) → Brahim Number → Symbolic Meaning
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.gematria

import com.brahim.buim.core.BrahimConstants
import kotlin.math.abs
import kotlin.math.pow
import kotlin.math.roundToLong
import kotlin.math.sqrt

/**
 * Hebrew letter with gematria value and meaning.
 */
data class HebrewLetter(
    val letter: Char,
    val name: String,
    val value: Int,
    val meaning: String
)

/**
 * Coordinate analysis result.
 */
data class CoordinateAnalysis(
    val latitude: Double,
    val longitude: Double,
    val brahimNumber: Long,
    val digitSum: Int,
    val digitalRoot: Int,
    val mod26Letter: Char,
    val hebrewLetters: List<HebrewLetter>,
    val singleDigitMeanings: List<String>,
    val brahimConnections: Map<String, Any>,
    val mirrorAnalysis: Map<String, Any>
)

/**
 * Brahim Gematria Calculator.
 */
object BrahimGematria {

    // Hebrew letters with single-digit values (1-9)
    private val HEBREW_SINGLE = mapOf(
        1 to HebrewLetter('א', "Aleph", 1, "Unity, origin, source, singularity"),
        2 to HebrewLetter('ב', "Bet", 2, "House, container, interior, domain"),
        3 to HebrewLetter('ג', "Gimel", 3, "Movement, bridge, transfer, motion"),
        4 to HebrewLetter('ד', "Dalet", 4, "Door, threshold, passage, transition"),
        5 to HebrewLetter('ה', "He", 5, "Presence, revelation, openness"),
        6 to HebrewLetter('ו', "Vav", 6, "Connector, link, binding element"),
        7 to HebrewLetter('ז', "Zayin", 7, "Division, sword, discernment"),
        8 to HebrewLetter('ח', "Het", 8, "Boundary, enclosure, limit, constraint"),
        9 to HebrewLetter('ט', "Tet", 9, "Potential, latent force, gestation")
    )

    // Hebrew letters for tens (10-90)
    private val HEBREW_TENS = mapOf(
        10 to HebrewLetter('י', "Yod", 10, "Point, seed, hand, creation"),
        20 to HebrewLetter('כ', "Kaf", 20, "Form, containment, palm"),
        30 to HebrewLetter('ל', "Lamed", 30, "Learning, teaching, staff"),
        40 to HebrewLetter('מ', "Mem", 40, "Water, flow, transformation"),
        50 to HebrewLetter('נ', "Nun", 50, "Fish, continuity, faithfulness"),
        60 to HebrewLetter('ס', "Samekh", 60, "Support, structure, scaffold"),
        70 to HebrewLetter('ע', "Ayin", 70, "Eye, perception, insight"),
        80 to HebrewLetter('פ', "Pe", 80, "Mouth, speech, expression"),
        90 to HebrewLetter('צ', "Tsade", 90, "Righteousness, fishing hook")
    )

    // Hebrew letters for hundreds (100-400)
    private val HEBREW_HUNDREDS = mapOf(
        100 to HebrewLetter('ק', "Qof", 100, "Back of head, cycle, holiness"),
        200 to HebrewLetter('ר', "Resh", 200, "Head, beginning, poverty"),
        300 to HebrewLetter('ש', "Shin", 300, "Tooth, fire, transformation"),
        400 to HebrewLetter('ת', "Tav", 400, "Mark, sign, covenant, completion")
    )

    // Latin A1-Z26 mapping
    private val LATIN_A1Z26 = ('A'..'Z').mapIndexed { i, c -> (i + 1) to c }.toMap()

    /**
     * Cantor pairing function - maps two integers to one unique integer.
     */
    fun cantorPair(a: Long, b: Long): Long {
        return ((a + b) * (a + b + 1)) / 2 + b
    }

    /**
     * Inverse Cantor pairing - recovers original pair from paired value.
     */
    fun cantorUnpair(z: Long): Pair<Long, Long> {
        val w = ((sqrt(8.0 * z + 1) - 1) / 2).toLong()
        val t = (w * w + w) / 2
        val b = z - t
        val a = w - b
        return a to b
    }

    /**
     * Convert coordinates to Brahim Number using Cantor pairing.
     * Uses microdegrees (6 decimal precision).
     */
    fun coordinatesToBrahimNumber(lat: Double, lon: Double, globalShift: Boolean = false): Long {
        val scale = 1_000_000L

        val a = if (globalShift) {
            ((lat + 90) * scale).roundToLong()
        } else {
            (lat * scale).roundToLong()
        }

        val b = if (globalShift) {
            ((lon + 180) * scale).roundToLong()
        } else {
            (lon * scale).roundToLong()
        }

        return cantorPair(abs(a), abs(b))
    }

    /**
     * Calculate digit sum of a number.
     */
    fun digitSum(n: Long): Int {
        var sum = 0
        var num = abs(n)
        while (num > 0) {
            sum += (num % 10).toInt()
            num /= 10
        }
        return sum
    }

    /**
     * Calculate digital root (repeated digit sum until single digit).
     */
    fun digitalRoot(n: Long): Int {
        var result = digitSum(n)
        while (result >= 10) {
            result = digitSum(result.toLong())
        }
        return result
    }

    /**
     * Get single digits of a number.
     */
    fun getSingleDigits(n: Long): List<Int> {
        return abs(n).toString().map { it.digitToInt() }
    }

    /**
     * Convert number to Latin letter via mod 26.
     */
    fun mod26ToLetter(n: Long): Char {
        val mod = ((n % 26) + 26) % 26  // Handle negatives
        return if (mod == 0L) 'Z' else LATIN_A1Z26[mod.toInt()] ?: '?'
    }

    /**
     * Convert digit sum to Hebrew letters (≤400 decomposition).
     */
    fun digitSumToHebrew(sum: Int): List<HebrewLetter> {
        val letters = mutableListOf<HebrewLetter>()
        var remaining = sum.coerceAtMost(400)

        // Hundreds
        while (remaining >= 100) {
            val hundred = (remaining / 100) * 100
            HEBREW_HUNDREDS[hundred.coerceAtMost(400)]?.let { letters.add(it) }
            remaining -= hundred.coerceAtMost(400)
        }

        // Tens
        if (remaining >= 10) {
            val ten = (remaining / 10) * 10
            HEBREW_TENS[ten]?.let { letters.add(it) }
            remaining -= ten
        }

        // Units
        if (remaining > 0) {
            HEBREW_SINGLE[remaining]?.let { letters.add(it) }
        }

        return letters
    }

    /**
     * Get Hebrew meaning for a single digit.
     */
    fun singleDigitMeaning(digit: Int): String {
        return if (digit == 0) {
            "∅ (Null, silence, void)"
        } else {
            HEBREW_SINGLE[digit]?.let { "${it.letter} (${it.name}): ${it.meaning}" } ?: "Unknown"
        }
    }

    /**
     * Analyze connections to Brahim sequence.
     */
    fun analyzeBrahimConnections(n: Long): Map<String, Any> {
        val connections = mutableMapOf<String, Any>()
        val sequence = BrahimConstants.BRAHIM_SEQUENCE

        // Check if number mod 214 is close to any Brahim number
        val mod214 = (n % BrahimConstants.BRAHIM_SUM).toInt()
        connections["mod_214"] = mod214

        val closestBrahim = sequence.minByOrNull { abs(it - mod214) }
        connections["closest_brahim_to_mod"] = closestBrahim ?: 0
        connections["distance_to_closest"] = closestBrahim?.let { abs(it - mod214) } ?: 0

        // Check mirror of mod214
        val mirror = BrahimConstants.BRAHIM_SUM - mod214
        connections["mirror_of_mod"] = mirror
        connections["mirror_in_sequence"] = mirror in sequence

        // Check digit sum connections
        val dSum = digitSum(n)
        connections["digit_sum"] = dSum
        connections["digit_sum_mod_10"] = dSum % 10
        connections["digit_sum_equals_sequence_length"] = (dSum % 100 == 10 || digitalRoot(n.toLong()) == 1)

        // Check for V-NAND grid connection (64 = 8²)
        if (dSum == 64) {
            connections["vnand_connection"] = "Digit sum 64 = 8² matches V-NAND row dimension"
        }

        // Golden ratio check
        val phi = BrahimConstants.PHI
        val beta = BrahimConstants.BETA_SECURITY
        connections["n_div_phi"] = n / phi
        connections["n_times_beta"] = n * beta

        return connections
    }

    /**
     * Perform mirror analysis on the number's digits.
     */
    fun analyzeMirrorSymmetry(digits: List<Int>): Map<String, Any> {
        val analysis = mutableMapOf<String, Any>()

        // Check for palindromic patterns
        val reversed = digits.reversed()
        analysis["is_palindrome"] = digits == reversed

        // Check for mirror pairs in sequence (like 9,4,9,4)
        val mirrorPairs = mutableListOf<String>()
        for (i in 0 until digits.size - 3) {
            if (digits[i] == digits[i + 2] && digits[i + 1] == digits[i + 3]) {
                mirrorPairs.add("${digits[i]}${digits[i+1]}${digits[i+2]}${digits[i+3]} at position $i")
            }
        }
        analysis["mirror_pairs"] = mirrorPairs

        // Check for Brahim-style symmetry (pairs summing to constant)
        val pairSums = mutableListOf<Int>()
        for (i in 0 until digits.size / 2) {
            pairSums.add(digits[i] + digits[digits.size - 1 - i])
        }
        analysis["symmetric_pair_sums"] = pairSums
        analysis["all_pairs_equal"] = pairSums.distinct().size == 1

        // Count occurrences
        val counts = digits.groupingBy { it }.eachCount()
        analysis["digit_frequency"] = counts
        analysis["most_frequent"] = counts.maxByOrNull { it.value }?.key

        return analysis
    }

    /**
     * Full coordinate analysis.
     */
    fun analyzeCoordinates(lat: Double, lon: Double, name: String = "Location"): CoordinateAnalysis {
        val brahimNumber = coordinatesToBrahimNumber(lat, lon)
        val digits = getSingleDigits(brahimNumber)
        val dSum = digitSum(brahimNumber)
        val dRoot = digitalRoot(brahimNumber)

        return CoordinateAnalysis(
            latitude = lat,
            longitude = lon,
            brahimNumber = brahimNumber,
            digitSum = dSum,
            digitalRoot = dRoot,
            mod26Letter = mod26ToLetter(brahimNumber),
            hebrewLetters = digitSumToHebrew(dSum),
            singleDigitMeanings = digits.map { singleDigitMeaning(it) },
            brahimConnections = analyzeBrahimConnections(brahimNumber),
            mirrorAnalysis = analyzeMirrorSymmetry(digits)
        )
    }

    /**
     * Generate semantic narrative from digit meanings.
     */
    fun generateSemanticNarrative(digits: List<Int>): String {
        val meanings = digits.filter { it != 0 }.map { HEBREW_SINGLE[it]?.meaning ?: "void" }

        return buildString {
            appendLine("Semantic Sequence:")
            meanings.forEachIndexed { i, meaning ->
                append("  ${i + 1}. $meaning")
                if (i < meanings.size - 1) appendLine(" →")
                else appendLine()
            }

            appendLine()
            appendLine("Narrative Interpretation:")
            append("  ")
            append(meanings.joinToString(" → "))
        }
    }

    /**
     * Sagrada Familia specific analysis.
     */
    fun analyzeSagradaFamilia(): Map<String, Any> {
        val lat = 41.4037
        val lon = 2.1735
        val analysis = analyzeCoordinates(lat, lon, "Sagrada Familia")

        val result = mutableMapOf<String, Any>()
        result["location"] = "La Sagrada Família, Barcelona"
        result["coordinates"] = "$lat°N, $lon°E"
        result["brahim_number"] = analysis.brahimNumber
        result["digit_sum"] = analysis.digitSum
        result["digital_root"] = analysis.digitalRoot
        result["mod_26_letter"] = analysis.mod26Letter

        // Hebrew interpretation
        result["hebrew_letters"] = analysis.hebrewLetters.map { "${it.letter} (${it.name})" }
        result["hebrew_meaning"] = analysis.hebrewLetters.joinToString(" + ") { it.meaning }

        // Single digit sequence
        val digits = getSingleDigits(analysis.brahimNumber)
        result["digit_sequence"] = digits.joinToString(",")
        result["semantic_narrative"] = generateSemanticNarrative(digits)

        // Brahim connections
        result["brahim_analysis"] = analysis.brahimConnections
        result["mirror_analysis"] = analysis.mirrorAnalysis

        // Special observations
        val observations = mutableListOf<String>()

        // Digit sum = 64 = 8² (V-NAND connection)
        if (analysis.digitSum == 64) {
            observations.add("Digit sum 64 = 8² connects to V-NAND 8×8×8×8 grid")
        }

        // Digital root = 1 (Aleph, unity)
        if (analysis.digitalRoot == 1) {
            observations.add("Digital root 1 = Aleph (א) = Unity, Origin - fitting for a sacred structure")
        }

        // Hebrew interpretation fits architecture
        val hebrewMeaning = analysis.hebrewLetters.joinToString("") { it.name }
        if (hebrewMeaning.contains("Samekh") && hebrewMeaning.contains("Dalet")) {
            observations.add("סד (Samekh-Dalet) = 'Support + Threshold' - architectural symbolism")
        }

        // Mirror pattern in digits
        if (digits.take(4) == listOf(9, 4, 9, 4)) {
            observations.add("Opening sequence 9-4-9-4 shows mirror symmetry (Tet-Dalet-Tet-Dalet)")
            observations.add("  → Potential-Threshold-Potential-Threshold: entering sacred space")
        }

        // Latitude close to 42 (B₂ in Brahim sequence)
        if (abs(lat - 42) < 1) {
            observations.add("Latitude ≈ 42 = B₂ in Brahim sequence")
        }

        result["special_observations"] = observations

        // Completion year connection (2026)
        result["completion_note"] = "Sagrada Familia expected completion: 2026 (140+ years of construction)"
        result["year_2026_analysis"] = mapOf(
            "2026_digit_sum" to digitSum(2026),
            "2026_digital_root" to digitalRoot(2026),
            "2026_mod_214" to 2026 % 214,
            "2026_hebrew" to digitSumToHebrew(digitSum(2026)).map { "${it.letter}: ${it.meaning}" }
        )

        return result
    }
}
