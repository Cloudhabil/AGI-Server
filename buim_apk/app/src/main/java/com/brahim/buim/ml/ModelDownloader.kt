/**
 * TensorFlow Lite Model Downloader
 * ==================================
 *
 * Downloads and manages ML models for on-device inference.
 * Supports background downloading with progress tracking.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.ml

import android.content.Context
import kotlinx.coroutines.*
import java.io.File
import java.io.FileOutputStream
import java.net.URL

/**
 * Model metadata
 */
data class ModelInfo(
    val type: ModelType,
    val url: String,
    val sizeBytes: Long,
    val version: String,
    val description: String
)

/**
 * Download progress
 */
data class DownloadProgress(
    val modelType: ModelType,
    val bytesDownloaded: Long,
    val totalBytes: Long,
    val percent: Int,
    val status: DownloadStatus
)

enum class DownloadStatus {
    PENDING,
    DOWNLOADING,
    COMPLETED,
    FAILED,
    CANCELLED
}

/**
 * Model repository URLs
 */
object ModelRepository {

    // Base URL for model downloads (placeholder - replace with actual server)
    private const val BASE_URL = "https://models.brahim.ai/tflite/v1"

    val AVAILABLE_MODELS = listOf(
        ModelInfo(
            type = ModelType.SECTOR_CLASSIFIER,
            url = "$BASE_URL/sector_classifier.tflite",
            sizeBytes = 5_000_000,  // ~5MB
            version = "1.0.0",
            description = "Classifies engineering queries into 10 industry sectors"
        ),
        ModelInfo(
            type = ModelType.DATATYPE_CLASSIFIER,
            url = "$BASE_URL/datatype_classifier.tflite",
            sizeBytes = 3_000_000,  // ~3MB
            version = "1.0.0",
            description = "Classifies expected data type (formula, datasheet, etc.)"
        ),
        ModelInfo(
            type = ModelType.EMBEDDING_MODEL,
            url = "$BASE_URL/text_embedding.tflite",
            sizeBytes = 25_000_000,  // ~25MB (sentence transformer)
            version = "1.0.0",
            description = "Generates 384-dim text embeddings for similarity search"
        ),
        ModelInfo(
            type = ModelType.VALUE_PREDICTOR,
            url = "$BASE_URL/value_predictor.tflite",
            sizeBytes = 2_000_000,  // ~2MB
            version = "1.0.0",
            description = "Predicts engineering values from features"
        ),
        ModelInfo(
            type = ModelType.FORMULA_SELECTOR,
            url = "$BASE_URL/formula_selector.tflite",
            sizeBytes = 4_000_000,  // ~4MB
            version = "1.0.0",
            description = "Selects appropriate formula for engineering query"
        )
    )

    fun getModelInfo(type: ModelType): ModelInfo? {
        return AVAILABLE_MODELS.find { it.type == type }
    }

    fun getTotalSize(): Long = AVAILABLE_MODELS.sumOf { it.sizeBytes }
}

/**
 * Model Downloader - Handles downloading and caching of TFLite models
 */
class ModelDownloader(private val context: Context) {

    private val modelsDir: File
        get() = File(context.filesDir, "models").apply { mkdirs() }

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val downloadJobs = mutableMapOf<ModelType, Job>()

    /**
     * Check if model exists locally
     */
    fun isModelDownloaded(type: ModelType): Boolean {
        return getModelFile(type).exists()
    }

    /**
     * Get local model file path
     */
    fun getModelFile(type: ModelType): File {
        return File(modelsDir, type.filename)
    }

    /**
     * Get all downloaded models
     */
    fun getDownloadedModels(): List<ModelType> {
        return ModelType.values().filter { isModelDownloaded(it) }
    }

    /**
     * Get all missing models
     */
    fun getMissingModels(): List<ModelType> {
        return ModelType.values().filter { !isModelDownloaded(it) }
    }

    /**
     * Download a model with progress callback
     */
    suspend fun downloadModel(
        type: ModelType,
        onProgress: (DownloadProgress) -> Unit = {}
    ): Result<File> = withContext(Dispatchers.IO) {
        val info = ModelRepository.getModelInfo(type)
            ?: return@withContext Result.failure(Exception("Unknown model type: $type"))

        val outputFile = getModelFile(type)
        val tempFile = File(modelsDir, "${type.filename}.tmp")

        try {
            onProgress(DownloadProgress(type, 0, info.sizeBytes, 0, DownloadStatus.DOWNLOADING))

            val url = URL(info.url)
            val connection = url.openConnection().apply {
                connectTimeout = 30000
                readTimeout = 60000
            }

            connection.getInputStream().use { input ->
                FileOutputStream(tempFile).use { output ->
                    val buffer = ByteArray(8192)
                    var bytesDownloaded = 0L

                    while (true) {
                        val bytesRead = input.read(buffer)
                        if (bytesRead == -1) break

                        output.write(buffer, 0, bytesRead)
                        bytesDownloaded += bytesRead

                        val percent = ((bytesDownloaded * 100) / info.sizeBytes).toInt()
                        onProgress(DownloadProgress(type, bytesDownloaded, info.sizeBytes, percent, DownloadStatus.DOWNLOADING))
                    }
                }
            }

            // Rename temp file to final
            tempFile.renameTo(outputFile)

            onProgress(DownloadProgress(type, info.sizeBytes, info.sizeBytes, 100, DownloadStatus.COMPLETED))
            Result.success(outputFile)

        } catch (e: Exception) {
            tempFile.delete()
            onProgress(DownloadProgress(type, 0, info.sizeBytes, 0, DownloadStatus.FAILED))
            Result.failure(e)
        }
    }

    /**
     * Download all missing models
     */
    suspend fun downloadAllMissing(
        onProgress: (ModelType, DownloadProgress) -> Unit = { _, _ -> }
    ): Map<ModelType, Result<File>> {
        val results = mutableMapOf<ModelType, Result<File>>()
        val missing = getMissingModels()

        for (type in missing) {
            results[type] = downloadModel(type) { progress ->
                onProgress(type, progress)
            }
        }

        return results
    }

    /**
     * Download model in background
     */
    fun downloadInBackground(
        type: ModelType,
        onComplete: (Result<File>) -> Unit = {}
    ) {
        downloadJobs[type]?.cancel()
        downloadJobs[type] = scope.launch {
            val result = downloadModel(type)
            withContext(Dispatchers.Main) {
                onComplete(result)
            }
        }
    }

    /**
     * Cancel download
     */
    fun cancelDownload(type: ModelType) {
        downloadJobs[type]?.cancel()
        downloadJobs.remove(type)

        // Delete partial file
        File(modelsDir, "${type.filename}.tmp").delete()
    }

    /**
     * Delete a downloaded model
     */
    fun deleteModel(type: ModelType): Boolean {
        return getModelFile(type).delete()
    }

    /**
     * Delete all models
     */
    fun deleteAllModels() {
        ModelType.values().forEach { deleteModel(it) }
    }

    /**
     * Get total downloaded size
     */
    fun getDownloadedSize(): Long {
        return getDownloadedModels().sumOf { getModelFile(it).length() }
    }

    /**
     * Get storage info
     */
    fun getStorageInfo(): Map<String, Any> {
        val downloaded = getDownloadedModels()
        val missing = getMissingModels()

        return mapOf(
            "downloaded_count" to downloaded.size,
            "missing_count" to missing.size,
            "downloaded_models" to downloaded.map { it.name },
            "missing_models" to missing.map { it.name },
            "downloaded_size_bytes" to getDownloadedSize(),
            "total_available_size_bytes" to ModelRepository.getTotalSize(),
            "models_directory" to modelsDir.absolutePath
        )
    }

    /**
     * Cleanup
     */
    fun cleanup() {
        scope.cancel()
        downloadJobs.clear()
    }
}

/**
 * Model Manager - High-level interface for model lifecycle
 */
class ModelManager(private val context: Context) {

    private val downloader = ModelDownloader(context)
    private var engine: TensorFlowLiteEngine? = null

    /**
     * Initialize with available models
     */
    fun initialize(): Boolean {
        val downloaded = downloader.getDownloadedModels()
        if (downloaded.isEmpty()) {
            // Use fallback (rule-based) engine
            engine = TensorFlowLiteEngine(context)
            return engine?.initialize(emptyList()) ?: false
        }

        engine = TensorFlowLiteEngine(context)
        return engine?.initialize(downloaded) ?: false
    }

    /**
     * Get the TFLite engine
     */
    fun getEngine(): TensorFlowLiteEngine? = engine

    /**
     * Ensure minimum required models are available
     */
    suspend fun ensureMinimumModels(
        required: List<ModelType> = listOf(ModelType.SECTOR_CLASSIFIER, ModelType.DATATYPE_CLASSIFIER),
        onProgress: (ModelType, DownloadProgress) -> Unit = { _, _ -> }
    ): Boolean {
        val missing = required.filter { !downloader.isModelDownloaded(it) }

        for (type in missing) {
            val result = downloader.downloadModel(type) { progress ->
                onProgress(type, progress)
            }
            if (result.isFailure) return false
        }

        return true
    }

    /**
     * Get status
     */
    fun getStatus(): Map<String, Any> {
        return mapOf(
            "engine_ready" to (engine?.isReady() ?: false),
            "loaded_models" to (engine?.getLoadedModels()?.map { it.name } ?: emptyList()),
            "storage" to downloader.getStorageInfo()
        )
    }

    /**
     * Cleanup
     */
    fun cleanup() {
        engine?.close()
        downloader.cleanup()
    }
}
