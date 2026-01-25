/**
 * Kelimutu Subnet - Three Lakes, One Magma
 * =========================================
 *
 * Inspired by Kelimutu volcano's three crater lakes:
 * - Surface: Three different colored lakes (visible outputs)
 * - Underground: Connected through volcanic channels (hidden structure)
 * - Magma: Single heat source producing all three (unified substrate)
 *
 * Architecture:
 *     Query -> Magma Substrate (Brahim) -> Underground Channels -> 3 Lake Outputs
 *
 * The lakes aren't separate experts - they're THREE EXPRESSIONS of ONE truth,
 * differentiated by oxidation state (activation function) in the channels.
 *
 * Coordinates: 8.77°S, 121.82°E (121 ∈ Brahim Sequence - B₆)
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ml

import com.brahim.buim.core.BrahimConstants
import kotlin.math.*
import kotlin.random.Random

/**
 * Kelimutu's three crater lakes + Dark Energy field.
 *
 * Each lake has different mineral oxidation -> different color
 * Same underlying magma -> different surface expression
 */
enum class Lake(val displayName: String, val perspective: String) {
    TIWU_ATA_MBUPU("old_people", "LITERAL"),      // Blue-green, stable
    TIWU_NUWA_MURI("young_maidens", "SEMANTIC"),  // Turquoise, active
    TIWU_ATA_POLO("enchanted", "STRUCTURAL"),     // Red-brown, mystic
    DARK_ENERGY("dark_energy", "CONTRASTIVE")     // Invisible, repulsive
}

/**
 * All possible intents for classification.
 */
val ALL_INTENTS = listOf("physics", "cosmology", "yang_mills", "mirror", "sequence", "verify", "help", "unknown")

/**
 * Output from Kelimutu subnet routing.
 */
data class KelimutuOutput(
    val intent: String,
    val confidence: Double,
    val lake: Lake,
    val lakeActivations: Map<String, Double>,
    val undergroundFlow: Double,
    val magmaEnergy: Double,
    val mineralSignature: DoubleArray
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is KelimutuOutput) return false
        return intent == other.intent && lake == other.lake
    }

    override fun hashCode(): Int = intent.hashCode() * 31 + lake.hashCode()
}

/**
 * Magma Substrate - Single Source of Truth.
 *
 * Contains the Brahim sequence as "mineral composition"
 * Provides energy (gradients) to all channels equally
 */
class MagmaSubstrate {

    // Magma composition = Brahim sequence normalized
    private val composition = BrahimConstants.BRAHIM_SEQUENCE.map {
        it.toDouble() / BrahimConstants.BRAHIM_SUM
    }.toDoubleArray()

    // Heat capacity
    var temperature = 1.0

    // Crystal structure matrix
    private val crystal: Array<DoubleArray> = buildCrystalMatrix()

    // Energy state
    var energy = 0.0
        private set

    /**
     * Build crystal structure from Brahim sequence.
     * Encodes mirror symmetry: M(x) = 214 - x
     */
    private fun buildCrystalMatrix(): Array<DoubleArray> {
        val dim = BrahimConstants.BRAHIM_DIMENSION
        val crystal = Array(dim) { DoubleArray(dim) }

        for (i in 0 until dim) {
            for (j in 0 until dim) {
                val bi = BrahimConstants.BRAHIM_SEQUENCE[i]
                val bj = BrahimConstants.BRAHIM_SEQUENCE[j]
                val mirrorI = BrahimConstants.BRAHIM_SUM - bi

                crystal[i][j] = when {
                    bj == mirrorI -> 1.0  // Strong bond (mirror pair)
                    abs(bi - bj) == abs(BrahimConstants.BRAHIM_SEQUENCE[1] - BrahimConstants.BRAHIM_SEQUENCE[0]) ->
                        BrahimConstants.PHI / 10  // Sequential bond
                    else -> 1.0 / (1 + abs(bi - bj).toDouble() / BrahimConstants.BRAHIM_CENTER)
                }
            }
        }

        // Normalize rows
        for (i in 0 until dim) {
            val rowSum = crystal[i].sum() + 1e-8
            for (j in 0 until dim) {
                crystal[i][j] /= rowSum
            }
        }

        return crystal
    }

    /**
     * Apply magma heat to query embedding.
     */
    fun heat(queryEmbedding: DoubleArray): DoubleArray {
        val dim = BrahimConstants.BRAHIM_DIMENSION
        val heated = DoubleArray(dim)

        // Matrix multiplication
        for (i in 0 until dim) {
            for (j in 0 until dim) {
                heated[i] += queryEmbedding[j] * crystal[j][i]
            }
        }

        // Apply temperature scaling
        for (i in heated.indices) {
            heated[i] *= temperature
        }

        // Compute energy
        energy = heated.sumOf { it * it }

        return heated
    }

    /**
     * Extract mineral signature from text.
     */
    fun getMineralSignature(text: String): DoubleArray {
        val signature = DoubleArray(BrahimConstants.BRAHIM_DIMENSION)
        val textLower = text.lowercase()

        // Keyword to Brahim dimension mapping
        val mineralKeywords = mapOf(
            0 to listOf("first", "initial", "start", "begin", "27"),
            1 to listOf("second", "ratio", "proportion", "42"),
            2 to listOf("third", "angle", "geometry", "60"),
            3 to listOf("fourth", "mass", "matter", "75"),
            4 to listOf("fifth", "prime", "fundamental", "97"),
            5 to listOf("sixth", "energy", "force", "121"),  // 121 = Kelimutu longitude
            6 to listOf("seventh", "transform", "change", "136"),
            7 to listOf("eighth", "symmetry", "mirror", "154"),
            8 to listOf("ninth", "cosmos", "universe", "172"),
            9 to listOf("tenth", "complete", "total", "187")
        )

        for ((idx, keywords) in mineralKeywords) {
            for (kw in keywords) {
                if (kw in textLower) {
                    signature[idx] += composition[idx]
                }
            }
        }

        // Add character-level features
        for ((i, char) in textLower.take(BrahimConstants.BRAHIM_DIMENSION).withIndex()) {
            signature[i % BrahimConstants.BRAHIM_DIMENSION] += char.code / 1000.0
        }

        // Normalize
        val norm = sqrt(signature.sumOf { it * it })
        if (norm > 0) {
            for (i in signature.indices) {
                signature[i] /= norm
            }
        }

        return signature
    }
}

/**
 * Underground Channel connecting magma to a specific lake.
 */
class UndergroundChannel(
    val lake: Lake,
    private var oxidationBias: Double = 0.0
) {
    // Channel-specific filter
    private val mineralFilter = DoubleArray(BrahimConstants.BRAHIM_DIMENSION) {
        Random.nextDouble() * 0.1 + getLakeAffinity(it)
    }

    // Lateral connections
    private val lateralWeights = mutableMapOf<Lake, Double>()

    // Statistics
    var totalFlow = 0.0
        private set
    var activationCount = 0
        private set

    private fun getLakeAffinity(index: Int): Double {
        return when (lake) {
            Lake.TIWU_ATA_MBUPU -> if (index >= 7) 0.3 else 0.0  // Wisdom
            Lake.TIWU_NUWA_MURI -> if (index in 3..6) 0.3 else 0.0  // Energy
            Lake.TIWU_ATA_POLO -> if (index == 0 || index == 9 || index == 4) 0.3 else 0.0  // Transformation
            Lake.DARK_ENERGY -> 0.0
        }
    }

    /**
     * Apply oxidation transformation.
     */
    fun oxidize(heatedEmbedding: DoubleArray): Double {
        // Apply mineral filter
        val filtered = heatedEmbedding.zip(mineralFilter.toList()) { h, m -> h * m }
        val sum = filtered.sum()

        // Oxidation transformation
        val activation = when (lake) {
            Lake.TIWU_ATA_MBUPU -> 1.0 / (1.0 + exp(-sum + oxidationBias))  // Sigmoid
            Lake.TIWU_NUWA_MURI -> (tanh(sum + oxidationBias) + 1) / 2  // Tanh
            Lake.TIWU_ATA_POLO -> ln(1 + exp(sum + oxidationBias)) / 3  // Softplus
            Lake.DARK_ENERGY -> sum
        }

        val clampedActivation = activation.coerceIn(0.0, 1.0)
        totalFlow += clampedActivation
        activationCount++

        return clampedActivation
    }

    fun connectLateral(otherChannel: UndergroundChannel, weight: Double) {
        lateralWeights[otherChannel.lake] = weight
    }

    fun updateFilter(gradient: DoubleArray, lr: Double = 0.01) {
        for (i in mineralFilter.indices) {
            mineralFilter[i] += lr * gradient[i]
        }
    }
}

/**
 * Wormhole Transform - Bypass Singularity at C=107.
 *
 * W(x) = C + (x - C) / phi
 */
class WormholeTransform {
    private val C = BrahimConstants.BRAHIM_CENTER  // 107
    private val S = BrahimConstants.BRAHIM_SUM      // 214
    private val phi = BrahimConstants.PHI

    // Wormhole throat position: C * phi = 173.13
    val throat = C * phi

    // Pre-computed wormhole sequence
    val wormholeSequence = BrahimConstants.BRAHIM_SEQUENCE.map { forward(it.toDouble()) }

    fun forward(x: Double): Double = C + (x - C) / phi

    fun inverse(y: Double): Double = C + (y - C) * phi

    /**
     * Apply wormhole bridging to intent scores.
     */
    fun bridgeIntentScores(
        scores: Map<String, Double>,
        mineralSig: DoubleArray,
        text: String
    ): Map<String, Double> {
        val bridged = scores.toMutableMap()
        val textLower = text.lowercase()

        // Compute query position in Brahim space
        val dominantDim = mineralSig.indices.maxByOrNull { mineralSig[it] } ?: 0
        val queryPosition = if (mineralSig.max() > 0.1) {
            BrahimConstants.BRAHIM_SEQUENCE[dominantDim].toDouble()
        } else {
            C.toDouble()
        }

        val warpedPosition = forward(queryPosition)

        // Brahim structure terms
        val brahimStructureTerms = listOf("sum constant", "center value", "delta 4", "delta 5",
            "dimension", "brahim sequence", "functional equation", "phi-adic", "regulator")
        val aboutStructure = brahimStructureTerms.any { it in textLower }

        val physicsTerms = listOf("fine structure", "weinberg", "muon", "proton", "electron",
            "mass ratio", "coupling", "hubble", "dark matter", "dark energy")
        val isPhysics = physicsTerms.any { it in textLower }

        val mirrorOperation = "transform" in textLower || "mirror of" in textLower ||
                              "apply mirror" in textLower || "mirror operator" in textLower

        val mirrorScore = scores["mirror"] ?: 0.0
        val physicsScore = scores["physics"] ?: 0.0
        val sequenceScore = scores["sequence"] ?: 0.0

        when {
            // Case A: ABOUT Brahim structure -> bypass to sequence
            aboutStructure && !mirrorOperation && !isPhysics -> {
                bridged["sequence"] = (bridged["sequence"] ?: 0.0) + 0.5
                bridged["mirror"] = (bridged["mirror"] ?: 0.0) * 0.3
                bridged["physics"] = (bridged["physics"] ?: 0.0) * 0.6
            }

            // Case B: Explicit mirror operation
            mirrorOperation -> {
                bridged["mirror"] = (bridged["mirror"] ?: 0.0) + 0.4
                bridged["physics"] = (bridged["physics"] ?: 0.0) * 0.5
            }

            // Case C: Yang-Mills territory
            "wightman" in textLower -> {
                bridged["yang_mills"] = (bridged["yang_mills"] ?: 0.0) + 0.5
                bridged["verify"] = (bridged["verify"] ?: 0.0) * 0.4
            }

            // Case D: Mirror winning but in broken pair territory
            mirrorScore > physicsScore && mirrorScore > sequenceScore &&
            warpedPosition in 85.0..130.0 -> {
                if (sequenceScore > 0.05 || physicsScore < 0.3) {
                    bridged["sequence"] = (bridged["sequence"] ?: 0.0) + 0.3
                    bridged["mirror"] = (bridged["mirror"] ?: 0.0) * 0.6
                }
            }

            // Case E: Random input going to physics
            physicsScore > 0.5 && mineralSig.max() < 0.15 -> {
                bridged["physics"] = (bridged["physics"] ?: 0.0) * 0.5
                bridged["unknown"] = (bridged["unknown"] ?: 0.0) + 0.3
            }
        }

        return bridged
    }

    fun getStats(): Map<String, Any> {
        return mapOf(
            "singularity" to C,
            "throat" to throat,
            "wormhole_sequence" to wormholeSequence.map { "%.1f".format(it) }
        )
    }
}

/**
 * Dark Energy Field - Repulsive Force.
 */
class DarkEnergyField {
    // Track attractor mass
    private val attractorMass = ALL_INTENTS.associateWith { 0.0 }.toMutableMap()

    // Confusable pairs
    private val confusionPairs = listOf(
        "sequence" to "mirror",
        "physics" to "mirror",
        "verify" to "mirror",
        "cosmology" to "physics",
        "yang_mills" to "verify",
        "help" to "sequence"
    )

    // Repulsion matrix
    private val repulsionMatrix = confusionPairs.flatMap { (a, b) ->
        listOf((a to b) to 0.5, (b to a) to 0.5)
    }.toMap().toMutableMap()

    // Discriminative keywords
    private val discriminativeKeywords = mapOf(
        "sequence" to listOf("brahim", "b1", "b10", "regulator", "dimension", "delta",
            "sum constant", "center value", "manifold", "phi-adic"),
        "mirror" to listOf("214 -", "m(", "reflect", "minus", "transform using mirror",
            "mirror operator on", "mirror of", "apply mirror"),
        "physics" to listOf("alpha", "weinberg", "muon", "proton", "electron", "coupling",
            "fine structure", "mass ratio", "bekenstein"),
        "cosmology" to listOf("dark matter", "dark energy", "hubble", "universe", "omega",
            "cosmic", "percentage of", "baryon"),
        "yang_mills" to listOf("qcd", "glueball", "confinement", "mills", "lattice",
            "wightman", "mass gap", "deviation"),
        "verify" to listOf("verify", "validate", "check", "prove", "satisfied"),
        "help" to listOf("can you", "how do", "what can", "capabilities", "list your",
            "show me what", "calculate everything", "functions")
    )

    // Dark energy constant
    val lambdaDark = 0.68  // Cosmological dark energy fraction

    fun applyRepulsion(intentScores: Map<String, Double>): Map<String, Double> {
        val adjusted = intentScores.toMutableMap()

        for ((pair, repulsion) in repulsionMatrix) {
            val (intent1, intent2) = pair
            val score1 = intentScores[intent1] ?: 0.0
            val score2 = intentScores[intent2] ?: 0.0

            if (score1 > 0.1 && score2 > 0.1) {
                val mass1 = attractorMass[intent1] ?: 0.0
                val mass2 = attractorMass[intent2] ?: 0.0
                val reduction = repulsion * lambdaDark * (score1 * score2)

                when {
                    mass1 > mass2 -> adjusted[intent1] = (adjusted[intent1] ?: 0.0) - reduction
                    mass2 > mass1 -> adjusted[intent2] = (adjusted[intent2] ?: 0.0) - reduction
                    else -> {
                        adjusted[intent1] = (adjusted[intent1] ?: 0.0) - reduction / 2
                        adjusted[intent2] = (adjusted[intent2] ?: 0.0) - reduction / 2
                    }
                }
            }
        }

        return adjusted.mapValues { maxOf(0.0, it.value) }
    }

    fun discriminativeBoost(text: String, intentScores: Map<String, Double>): Map<String, Double> {
        val boosted = intentScores.toMutableMap()
        val textLower = text.lowercase()

        for ((intent, keywords) in discriminativeKeywords) {
            for (kw in keywords) {
                if (kw in textLower) {
                    boosted[intent] = (boosted[intent] ?: 0.0) + 0.3
                }
            }
        }

        return boosted
    }

    fun updateAttractorMass(predicted: String, target: String) {
        if (predicted != target) {
            attractorMass[predicted] = (attractorMass[predicted] ?: 0.0) + 0.1
            attractorMass[target] = maxOf(0.0, (attractorMass[target] ?: 0.0) - 0.05)
        }
    }

    fun getStats(): Map<String, Any> {
        return mapOf(
            "lambda" to lambdaDark,
            "attractor_mass" to attractorMass.filter { it.value > 0 }
        )
    }
}

/**
 * Kelimutu Subnet - Complete Three Lakes System.
 */
class KelimutuSubnet(private val useDarkEnergy: Boolean = true) {

    // Single source of truth
    val magma = MagmaSubstrate()

    // Three perspective channels
    private val channels = mapOf(
        Lake.TIWU_ATA_MBUPU to UndergroundChannel(Lake.TIWU_ATA_MBUPU, oxidationBias = -0.5),
        Lake.TIWU_NUWA_MURI to UndergroundChannel(Lake.TIWU_NUWA_MURI, oxidationBias = 0.0),
        Lake.TIWU_ATA_POLO to UndergroundChannel(Lake.TIWU_ATA_POLO, oxidationBias = 0.3)
    )

    // Fusion weights
    private val fusionWeights = mutableMapOf(
        Lake.TIWU_ATA_MBUPU to 0.40,  // Literal: high trust
        Lake.TIWU_NUWA_MURI to 0.35,  // Semantic: medium trust
        Lake.TIWU_ATA_POLO to 0.25    // Structural: catches edge cases
    )

    // Dark energy field
    private val darkEnergy = if (useDarkEnergy) DarkEnergyField() else null

    // Wormhole transform
    private val wormhole = WormholeTransform()

    // Keyword database
    private val keywords = mapOf(
        "physics" to listOf("fine", "structure", "alpha", "constant", "weinberg", "angle",
            "muon", "electron", "proton", "mass", "ratio", "coupling"),
        "cosmology" to listOf("dark", "matter", "energy", "universe", "cosmic", "hubble",
            "percentage", "fraction", "baryon", "lambda", "omega"),
        "yang_mills" to listOf("yang", "mills", "mass", "gap", "qcd", "confinement",
            "glueball", "wightman", "qft", "gauge", "lattice"),
        "mirror" to listOf("mirror", "reflect", "symmetry", "transform", "operator",
            "214", "minus", "m(", "apply", "center"),
        "sequence" to listOf("sequence", "brahim", "numbers", "list", "b1", "b10",
            "sum", "phi", "dimension", "manifold", "regulator"),
        "verify" to listOf("verify", "check", "validate", "prove", "axiom", "satisfied"),
        "help" to listOf("help", "what can", "how", "capabilities", "functions"),
        "unknown" to emptyList()
    )

    init {
        // Connect channels laterally
        for ((lake1, channel1) in channels) {
            for ((lake2, _) in channels) {
                if (lake1 != lake2) {
                    channel1.connectLateral(channels[lake2]!!, 0.15)
                }
            }
        }
    }

    /**
     * Lake 1: Literal keyword matching.
     */
    private fun literalClassify(text: String): Map<String, Double> {
        val scores = ALL_INTENTS.associateWith { 0.0 }.toMutableMap()
        val textLower = text.lowercase()

        for ((intent, kws) in keywords) {
            for (kw in kws) {
                if (kw in textLower) {
                    scores[intent] = (scores[intent] ?: 0.0) + 1.0
                    if (" " in kw && kw in textLower) {
                        scores[intent] = (scores[intent] ?: 0.0) + 0.5
                    }
                }
            }
        }

        val total = scores.values.sum() + 1e-8
        return scores.mapValues { it.value / total }
    }

    /**
     * Lake 2: Semantic meaning-based classification.
     */
    private fun semanticClassify(mineralSig: DoubleArray): Map<String, Double> {
        val scores = mutableMapOf<String, Double>()

        // Simple semantic scoring based on mineral signature
        for (intent in ALL_INTENTS) {
            val alignment = when (intent) {
                "physics" -> mineralSig.slice(3..5).sum()
                "cosmology" -> mineralSig[8]
                "yang_mills" -> mineralSig[5] + mineralSig[6]
                "mirror" -> mineralSig[7]
                "sequence" -> mineralSig.slice(0..2).sum()
                "verify" -> mineralSig[6] + mineralSig[7]
                "help" -> mineralSig.average()
                else -> 0.1
            }
            scores[intent] = maxOf(0.0, alignment + 0.5)
        }

        val total = scores.values.sum() + 1e-8
        return scores.mapValues { it.value / total }
    }

    /**
     * Lake 3: Structural pattern-based classification.
     */
    private fun structuralClassify(mineralSig: DoubleArray, heated: DoubleArray): Map<String, Double> {
        val scores = ALL_INTENTS.associateWith { 0.0 }.toMutableMap()
        val dim = BrahimConstants.BRAHIM_DIMENSION

        // Check for mirror symmetry patterns
        var symmetryScore = 0.0
        for (i in 0 until dim / 2) {
            symmetryScore += abs(mineralSig[i] - mineralSig[dim - 1 - i])
        }
        symmetryScore = 1.0 - (symmetryScore / (dim / 2))

        scores["mirror"] = (scores["mirror"] ?: 0.0) + symmetryScore * 0.5
        scores["verify"] = (scores["verify"] ?: 0.0) + symmetryScore * 0.3

        // Energy concentration
        val energyConcentration = heated.max() / (heated.average() + 1e-8)
        if (energyConcentration > 2) {
            scores["physics"] = (scores["physics"] ?: 0.0) + 0.3
            scores["yang_mills"] = (scores["yang_mills"] ?: 0.0) + 0.2
        }

        // Uniformity
        val stdDev = sqrt(mineralSig.map { (it - mineralSig.average()).pow(2) }.average())
        val uniformity = 1.0 - stdDev
        scores["sequence"] = (scores["sequence"] ?: 0.0) + uniformity * 0.3
        scores["help"] = (scores["help"] ?: 0.0) + uniformity * 0.2

        val total = scores.values.sum() + 1e-8
        return scores.mapValues { it.value / total }
    }

    /**
     * Route through three lakes and fuse results.
     */
    fun route(text: String): KelimutuOutput {
        // Extract mineral signature
        val mineralSig = magma.getMineralSignature(text)
        val heated = magma.heat(mineralSig)

        // Get channel activations
        val channelActivations = mutableMapOf<Lake, Double>()
        for ((lake, channel) in channels) {
            channelActivations[lake] = channel.oxidize(heated)
        }

        // Each lake classifies from its perspective
        val lakeScores = mapOf(
            Lake.TIWU_ATA_MBUPU to literalClassify(text),
            Lake.TIWU_NUWA_MURI to semanticClassify(mineralSig),
            Lake.TIWU_ATA_POLO to structuralClassify(mineralSig, heated)
        )

        // Fuse: weighted combination
        val fusedScores = ALL_INTENTS.associateWith { 0.0 }.toMutableMap()

        for ((lake, scores) in lakeScores) {
            val lakeWeight = fusionWeights[lake] ?: 0.0
            val channelActivation = channelActivations[lake] ?: 0.0

            for ((intent, score) in scores) {
                fusedScores[intent] = (fusedScores[intent] ?: 0.0) + lakeWeight * channelActivation * score
            }
        }

        // Apply dark energy
        var finalScores = fusedScores.toMap()
        darkEnergy?.let { de ->
            finalScores = de.discriminativeBoost(text, finalScores)
            finalScores = de.applyRepulsion(finalScores)
        }

        // Apply wormhole
        finalScores = wormhole.bridgeIntentScores(finalScores, mineralSig, text)

        // Select best intent
        val bestIntent = finalScores.maxByOrNull { it.value }?.key ?: "unknown"
        val totalScore = finalScores.values.sum() + 1e-8
        val confidence = (finalScores[bestIntent] ?: 0.0) / totalScore

        // Determine dominant lake
        val lakeContributions = lakeScores.mapValues { (lake, scores) ->
            (scores[bestIntent] ?: 0.0) * (fusionWeights[lake] ?: 0.0)
        }
        val dominantLake = lakeContributions.maxByOrNull { it.value }?.key ?: Lake.TIWU_ATA_MBUPU

        return KelimutuOutput(
            intent = bestIntent,
            confidence = confidence,
            lake = dominantLake,
            lakeActivations = channelActivations.mapKeys { it.key.displayName },
            undergroundFlow = channelActivations.values.sum(),
            magmaEnergy = magma.energy,
            mineralSignature = mineralSig
        )
    }

    /**
     * Get system statistics.
     */
    fun getStats(): Map<String, Any> {
        return mapOf(
            "magma_temperature" to magma.temperature,
            "magma_energy" to magma.energy,
            "fusion_weights" to fusionWeights.mapKeys { it.key.displayName },
            "channel_flows" to channels.mapKeys { it.key.displayName }.mapValues { entry ->
                mapOf(
                    "total_flow" to entry.value.totalFlow,
                    "activations" to entry.value.activationCount
                )
            },
            "dark_energy" to (darkEnergy?.getStats() ?: emptyMap()),
            "wormhole" to wormhole.getStats()
        )
    }
}
