/**
 * TensorFlow Lite Engine for On-Device ML
 * =========================================
 *
 * Real ML inference using TensorFlow Lite for:
 * - Text classification (sector/datatype detection)
 * - Engineering value prediction
 * - Similarity matching for standards lookup
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.ml

import android.content.Context
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.common.FileUtil
import java.io.Closeable
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Model types supported by the engine
 */
enum class ModelType(val filename: String, val description: String) {
    SECTOR_CLASSIFIER("sector_classifier.tflite", "Classifies query into industry sector"),
    DATATYPE_CLASSIFIER("datatype_classifier.tflite", "Classifies expected data type"),
    VALUE_PREDICTOR("value_predictor.tflite", "Predicts engineering values"),
    EMBEDDING_MODEL("text_embedding.tflite", "Generates text embeddings for similarity"),
    FORMULA_SELECTOR("formula_selector.tflite", "Selects appropriate formula for query")
}

/**
 * Prediction result from TFLite model
 */
data class TFLitePrediction(
    val label: String,
    val confidence: Float,
    val rawOutput: FloatArray,
    val modelType: ModelType,
    val inferenceTimeMs: Long
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is TFLitePrediction) return false
        return label == other.label && confidence == other.confidence
    }

    override fun hashCode(): Int = label.hashCode() * 31 + confidence.hashCode()
}

/**
 * Text embedding for similarity search
 */
data class TextEmbedding(
    val text: String,
    val vector: FloatArray,
    val dimension: Int
) {
    fun cosineSimilarity(other: TextEmbedding): Float {
        require(dimension == other.dimension) { "Embedding dimensions must match" }
        var dotProduct = 0f
        var normA = 0f
        var normB = 0f
        for (i in 0 until dimension) {
            dotProduct += vector[i] * other.vector[i]
            normA += vector[i] * vector[i]
            normB += other.vector[i] * other.vector[i]
        }
        return if (normA > 0 && normB > 0) {
            dotProduct / (kotlin.math.sqrt(normA) * kotlin.math.sqrt(normB))
        } else 0f
    }
}

/**
 * TensorFlow Lite Engine - Core ML inference
 */
class TensorFlowLiteEngine(private val context: Context) : Closeable {

    private val interpreters = mutableMapOf<ModelType, Interpreter>()
    private val tokenizer = SimpleTokenizer()

    // Sector labels matching Sector enum order
    private val sectorLabels = listOf(
        "ELECTRICAL", "MECHANICAL", "CHEMICAL", "DIGITAL", "AEROSPACE",
        "BIOMEDICAL", "ENERGY", "MATERIALS", "CONSTRUCTION", "TRANSPORT"
    )

    // DataType labels
    private val dataTypeLabels = listOf(
        "SPECIFICATION", "DATASHEET", "FORMULA", "TABLE", "DIAGRAM",
        "PROCEDURE", "MEASUREMENT", "SIMULATION", "LEARNED"
    )

    /**
     * Initialize engine and load models
     */
    fun initialize(modelsToLoad: List<ModelType> = ModelType.values().toList()): Boolean {
        return try {
            modelsToLoad.forEach { modelType ->
                loadModel(modelType)
            }
            true
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    /**
     * Load a specific model
     */
    private fun loadModel(modelType: ModelType) {
        try {
            val modelBuffer = FileUtil.loadMappedFile(context, "models/${modelType.filename}")
            val options = Interpreter.Options().apply {
                setNumThreads(4)
                // Enable NNAPI for hardware acceleration if available
                // setUseNNAPI(true)
            }
            interpreters[modelType] = Interpreter(modelBuffer, options)
        } catch (e: Exception) {
            // Model not found - will use fallback
            println("Model ${modelType.filename} not found, using fallback")
        }
    }

    /**
     * Classify text into industry sector
     */
    fun classifySector(text: String): TFLitePrediction {
        val startTime = System.currentTimeMillis()

        val interpreter = interpreters[ModelType.SECTOR_CLASSIFIER]
        if (interpreter == null) {
            // Fallback to rule-based classification
            return fallbackSectorClassification(text, startTime)
        }

        val inputBuffer = tokenizer.tokenize(text, maxLength = 128)
        val outputBuffer = Array(1) { FloatArray(sectorLabels.size) }

        interpreter.run(inputBuffer, outputBuffer)

        val inferenceTime = System.currentTimeMillis() - startTime
        val maxIndex = outputBuffer[0].indices.maxByOrNull { outputBuffer[0][it] } ?: 0
        val confidence = outputBuffer[0][maxIndex]

        return TFLitePrediction(
            label = sectorLabels[maxIndex],
            confidence = confidence,
            rawOutput = outputBuffer[0],
            modelType = ModelType.SECTOR_CLASSIFIER,
            inferenceTimeMs = inferenceTime
        )
    }

    /**
     * Classify expected data type
     */
    fun classifyDataType(text: String): TFLitePrediction {
        val startTime = System.currentTimeMillis()

        val interpreter = interpreters[ModelType.DATATYPE_CLASSIFIER]
        if (interpreter == null) {
            return fallbackDataTypeClassification(text, startTime)
        }

        val inputBuffer = tokenizer.tokenize(text, maxLength = 128)
        val outputBuffer = Array(1) { FloatArray(dataTypeLabels.size) }

        interpreter.run(inputBuffer, outputBuffer)

        val inferenceTime = System.currentTimeMillis() - startTime
        val maxIndex = outputBuffer[0].indices.maxByOrNull { outputBuffer[0][it] } ?: 0

        return TFLitePrediction(
            label = dataTypeLabels[maxIndex],
            confidence = outputBuffer[0][maxIndex],
            rawOutput = outputBuffer[0],
            modelType = ModelType.DATATYPE_CLASSIFIER,
            inferenceTimeMs = inferenceTime
        )
    }

    /**
     * Generate text embedding for similarity search
     */
    fun generateEmbedding(text: String): TextEmbedding {
        val interpreter = interpreters[ModelType.EMBEDDING_MODEL]
        val dimension = 384  // Standard sentence transformer dimension

        if (interpreter == null) {
            // Fallback: simple bag-of-words embedding
            return fallbackEmbedding(text, dimension)
        }

        val inputBuffer = tokenizer.tokenize(text, maxLength = 128)
        val outputBuffer = Array(1) { FloatArray(dimension) }

        interpreter.run(inputBuffer, outputBuffer)

        return TextEmbedding(
            text = text,
            vector = outputBuffer[0],
            dimension = dimension
        )
    }

    /**
     * Find most similar text from candidates
     */
    fun findMostSimilar(query: String, candidates: List<String>): Pair<String, Float>? {
        if (candidates.isEmpty()) return null

        val queryEmbedding = generateEmbedding(query)
        var bestMatch: String? = null
        var bestScore = -1f

        candidates.forEach { candidate ->
            val candidateEmbedding = generateEmbedding(candidate)
            val similarity = queryEmbedding.cosineSimilarity(candidateEmbedding)
            if (similarity > bestScore) {
                bestScore = similarity
                bestMatch = candidate
            }
        }

        return bestMatch?.let { it to bestScore }
    }

    /**
     * Predict engineering value (regression)
     */
    fun predictValue(features: FloatArray): Float {
        val interpreter = interpreters[ModelType.VALUE_PREDICTOR]
        if (interpreter == null) {
            return 0f  // Fallback
        }

        val inputBuffer = ByteBuffer.allocateDirect(features.size * 4).apply {
            order(ByteOrder.nativeOrder())
            features.forEach { putFloat(it) }
            rewind()
        }
        val outputBuffer = Array(1) { FloatArray(1) }

        interpreter.run(inputBuffer, outputBuffer)

        return outputBuffer[0][0]
    }

    // =========================================================================
    // Fallback Methods (when models not available)
    // =========================================================================

    private fun fallbackSectorClassification(text: String, startTime: Long): TFLitePrediction {
        val lowerText = text.lowercase()
        val scores = FloatArray(sectorLabels.size)

        // Keyword matching for each sector
        val sectorKeywords = mapOf(
            0 to listOf("voltage", "current", "wire", "circuit", "electrical", "power", "iec"),
            1 to listOf("torque", "bearing", "mechanical", "shaft", "gear", "force"),
            2 to listOf("chemical", "reaction", "process", "catalyst", "pressure"),
            3 to listOf("software", "digital", "ieee", "protocol", "data", "network"),
            4 to listOf("aircraft", "flight", "aerospace", "aviation", "space"),
            5 to listOf("medical", "biomedical", "patient", "clinical", "health"),
            6 to listOf("solar", "wind", "battery", "renewable", "energy", "grid"),
            7 to listOf("material", "steel", "alloy", "composite", "metal"),
            8 to listOf("building", "construction", "concrete", "structural"),
            9 to listOf("vehicle", "transport", "automotive", "rail", "car")
        )

        sectorKeywords.forEach { (index, keywords) ->
            keywords.forEach { keyword ->
                if (lowerText.contains(keyword)) scores[index] += 0.2f
            }
        }

        // Normalize
        val sum = scores.sum()
        if (sum > 0) scores.indices.forEach { scores[it] /= sum }

        val maxIndex = scores.indices.maxByOrNull { scores[it] } ?: 0
        val confidence = if (sum > 0) scores[maxIndex] else 0.5f

        return TFLitePrediction(
            label = sectorLabels[maxIndex],
            confidence = confidence.coerceIn(0.3f, 0.9f),
            rawOutput = scores,
            modelType = ModelType.SECTOR_CLASSIFIER,
            inferenceTimeMs = System.currentTimeMillis() - startTime
        )
    }

    private fun fallbackDataTypeClassification(text: String, startTime: Long): TFLitePrediction {
        val lowerText = text.lowercase()
        val scores = FloatArray(dataTypeLabels.size)

        val typeKeywords = mapOf(
            0 to listOf("standard", "iec", "iso", "specification", "requirement"),
            1 to listOf("datasheet", "spec sheet", "component", "part"),
            2 to listOf("formula", "equation", "calculate", "compute"),
            3 to listOf("table", "lookup", "reference", "values"),
            4 to listOf("diagram", "schematic", "drawing", "circuit"),
            5 to listOf("procedure", "instruction", "how to", "step"),
            6 to listOf("measurement", "reading", "sensor", "test"),
            7 to listOf("simulation", "fea", "cfd", "analysis"),
            8 to listOf("predict", "estimate", "approximate")
        )

        typeKeywords.forEach { (index, keywords) ->
            keywords.forEach { keyword ->
                if (lowerText.contains(keyword)) scores[index] += 0.25f
            }
        }

        val sum = scores.sum()
        if (sum > 0) scores.indices.forEach { scores[it] /= sum }

        val maxIndex = scores.indices.maxByOrNull { scores[it] } ?: 0

        return TFLitePrediction(
            label = dataTypeLabels[maxIndex],
            confidence = if (sum > 0) scores[maxIndex].coerceIn(0.3f, 0.9f) else 0.5f,
            rawOutput = scores,
            modelType = ModelType.DATATYPE_CLASSIFIER,
            inferenceTimeMs = System.currentTimeMillis() - startTime
        )
    }

    private fun fallbackEmbedding(text: String, dimension: Int): TextEmbedding {
        // Simple hash-based embedding as fallback
        val vector = FloatArray(dimension)
        val words = text.lowercase().split(Regex("\\s+"))

        words.forEachIndexed { wordIndex, word ->
            word.forEachIndexed { charIndex, char ->
                val idx = (word.hashCode() + charIndex) % dimension
                val absIdx = if (idx < 0) idx + dimension else idx
                vector[absIdx] += (1f / (wordIndex + 1))
            }
        }

        // Normalize
        val norm = kotlin.math.sqrt(vector.sumOf { (it * it).toDouble() }).toFloat()
        if (norm > 0) vector.indices.forEach { vector[it] /= norm }

        return TextEmbedding(text, vector, dimension)
    }

    override fun close() {
        interpreters.values.forEach { it.close() }
        interpreters.clear()
    }

    /**
     * Get loaded model info
     */
    fun getLoadedModels(): List<ModelType> = interpreters.keys.toList()

    /**
     * Check if engine is ready
     */
    fun isReady(): Boolean = interpreters.isNotEmpty()
}

/**
 * Simple tokenizer for text preprocessing
 */
class SimpleTokenizer {
    private val vocabSize = 30000
    private val padToken = 0
    private val unkToken = 1

    /**
     * Tokenize text to ByteBuffer for TFLite input
     */
    fun tokenize(text: String, maxLength: Int): ByteBuffer {
        val tokens = text.lowercase()
            .replace(Regex("[^a-z0-9\\s]"), " ")
            .split(Regex("\\s+"))
            .filter { it.isNotEmpty() }
            .take(maxLength)

        val buffer = ByteBuffer.allocateDirect(maxLength * 4).apply {
            order(ByteOrder.nativeOrder())
        }

        // Convert words to token IDs (simple hash-based)
        tokens.forEach { word ->
            val tokenId = (word.hashCode() % (vocabSize - 2) + 2).let {
                if (it < 0) it + vocabSize else it
            }
            buffer.putInt(tokenId)
        }

        // Pad remaining
        repeat(maxLength - tokens.size) {
            buffer.putInt(padToken)
        }

        buffer.rewind()
        return buffer
    }

    /**
     * Tokenize to IntArray
     */
    fun tokenizeToArray(text: String, maxLength: Int): IntArray {
        val tokens = text.lowercase()
            .replace(Regex("[^a-z0-9\\s]"), " ")
            .split(Regex("\\s+"))
            .filter { it.isNotEmpty() }
            .take(maxLength)

        val result = IntArray(maxLength) { padToken }
        tokens.forEachIndexed { index, word ->
            val tokenId = (word.hashCode() % (vocabSize - 2) + 2).let {
                if (it < 0) it + vocabSize else it
            }
            result[index] = tokenId
        }

        return result
    }
}
