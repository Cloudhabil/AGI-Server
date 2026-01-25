/**
 * BUIM - Brahim Walkie Talkie
 * Encrypted Push-to-Talk Voice Communication
 *
 * Features:
 * - Real-time voice encryption using Wormhole Cipher
 * - Push-to-talk (PTT) mode
 * - Group channels with resonance-based priority
 * - Geographic proximity channels
 */
package com.brahim.buim.chat

import android.Manifest
import android.content.Context
import android.media.*
import android.media.audiofx.AcousticEchoCanceler
import android.media.audiofx.NoiseSuppressor
import androidx.annotation.RequiresPermission
import com.brahim.buim.cipher.WormholeCipher
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.network.BrahimNetworkProtocol
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.nio.ByteBuffer
import java.util.concurrent.ConcurrentLinkedQueue

/**
 * Brahim Walkie Talkie - Encrypted voice communication
 */
class BrahimWalkieTalkie(private val context: Context) {

    companion object {
        // Audio configuration optimized for voice
        const val SAMPLE_RATE = 16000
        const val CHANNEL_CONFIG_IN = AudioFormat.CHANNEL_IN_MONO
        const val CHANNEL_CONFIG_OUT = AudioFormat.CHANNEL_OUT_MONO
        const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT

        // Frame size for encryption (must match Opus frame size)
        const val FRAME_SIZE_MS = 20
        const val SAMPLES_PER_FRAME = SAMPLE_RATE * FRAME_SIZE_MS / 1000

        // Brahim sequence for audio channels
        val CHANNEL_FREQUENCIES = BrahimConstants.SEQUENCE.map { it * 10 } // 270, 420, 600...Hz markers
    }

    // State
    private val _state = MutableStateFlow(WalkieTalkieState())
    val state: StateFlow<WalkieTalkieState> = _state

    // Audio components
    private var audioRecord: AudioRecord? = null
    private var audioTrack: AudioTrack? = null
    private var echoCanceler: AcousticEchoCanceler? = null
    private var noiseSuppressor: NoiseSuppressor? = null

    // Encryption
    private var sessionKey: ByteArray? = null
    private var frameCounter: Long = 0

    // Buffers
    private val transmitQueue = ConcurrentLinkedQueue<EncryptedAudioFrame>()
    private val receiveQueue = ConcurrentLinkedQueue<EncryptedAudioFrame>()

    // Coroutine scope
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    // Active channel
    private var currentChannel: WalkieTalkieChannel? = null

    /**
     * Initialize walkie talkie with a session key
     */
    fun initialize(sessionKey: ByteArray) {
        this.sessionKey = sessionKey
        _state.value = _state.value.copy(isInitialized = true)
    }

    /**
     * Join a walkie talkie channel
     */
    fun joinChannel(channel: WalkieTalkieChannel) {
        currentChannel = channel
        _state.value = _state.value.copy(
            currentChannel = channel,
            isInChannel = true
        )
    }

    /**
     * Leave current channel
     */
    fun leaveChannel() {
        stopTransmitting()
        stopReceiving()
        currentChannel = null
        _state.value = _state.value.copy(
            currentChannel = null,
            isInChannel = false
        )
    }

    /**
     * Start Push-to-Talk transmission
     */
    @RequiresPermission(Manifest.permission.RECORD_AUDIO)
    fun startTransmitting() {
        if (_state.value.isTransmitting) return
        if (sessionKey == null) throw IllegalStateException("Not initialized")

        _state.value = _state.value.copy(isTransmitting = true)

        // Initialize audio recorder
        val bufferSize = AudioRecord.getMinBufferSize(
            SAMPLE_RATE,
            CHANNEL_CONFIG_IN,
            AUDIO_FORMAT
        )

        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.VOICE_COMMUNICATION,
            SAMPLE_RATE,
            CHANNEL_CONFIG_IN,
            AUDIO_FORMAT,
            bufferSize * 2
        )

        // Enable audio processing
        audioRecord?.audioSessionId?.let { sessionId ->
            if (AcousticEchoCanceler.isAvailable()) {
                echoCanceler = AcousticEchoCanceler.create(sessionId)
                echoCanceler?.enabled = true
            }
            if (NoiseSuppressor.isAvailable()) {
                noiseSuppressor = NoiseSuppressor.create(sessionId)
                noiseSuppressor?.enabled = true
            }
        }

        audioRecord?.startRecording()

        // Start capture coroutine
        scope.launch {
            captureAndEncryptAudio()
        }
    }

    /**
     * Stop Push-to-Talk transmission
     */
    fun stopTransmitting() {
        _state.value = _state.value.copy(isTransmitting = false)

        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null

        echoCanceler?.release()
        echoCanceler = null
        noiseSuppressor?.release()
        noiseSuppressor = null
    }

    /**
     * Start receiving and playing audio
     */
    fun startReceiving() {
        if (_state.value.isReceiving) return

        _state.value = _state.value.copy(isReceiving = true)

        val bufferSize = AudioTrack.getMinBufferSize(
            SAMPLE_RATE,
            CHANNEL_CONFIG_OUT,
            AUDIO_FORMAT
        )

        audioTrack = AudioTrack.Builder()
            .setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_VOICE_COMMUNICATION)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            .setAudioFormat(
                AudioFormat.Builder()
                    .setEncoding(AUDIO_FORMAT)
                    .setSampleRate(SAMPLE_RATE)
                    .setChannelMask(CHANNEL_CONFIG_OUT)
                    .build()
            )
            .setBufferSizeInBytes(bufferSize * 2)
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build()

        audioTrack?.play()

        // Start playback coroutine
        scope.launch {
            decryptAndPlayAudio()
        }
    }

    /**
     * Stop receiving audio
     */
    fun stopReceiving() {
        _state.value = _state.value.copy(isReceiving = false)

        audioTrack?.stop()
        audioTrack?.release()
        audioTrack = null
    }

    /**
     * Receive an encrypted audio frame from network
     */
    fun receiveFrame(frame: EncryptedAudioFrame) {
        receiveQueue.offer(frame)
    }

    /**
     * Get next encrypted frame to transmit
     */
    fun getNextTransmitFrame(): EncryptedAudioFrame? {
        return transmitQueue.poll()
    }

    /**
     * Capture and encrypt audio frames
     */
    private suspend fun captureAndEncryptAudio() = withContext(Dispatchers.IO) {
        val buffer = ShortArray(SAMPLES_PER_FRAME)

        while (_state.value.isTransmitting) {
            val readResult = audioRecord?.read(buffer, 0, SAMPLES_PER_FRAME) ?: -1

            if (readResult > 0) {
                // Convert to bytes
                val audioBytes = shortsToBytes(buffer)

                // Apply Brahim audio processing
                val processed = applyBrahimAudioProcessing(audioBytes)

                // Encrypt frame
                val encrypted = encryptFrame(processed)

                // Add to transmit queue
                transmitQueue.offer(encrypted)

                // Update state
                _state.value = _state.value.copy(
                    transmittedFrames = _state.value.transmittedFrames + 1
                )
            }

            // Yield to other coroutines
            yield()
        }
    }

    /**
     * Decrypt and play audio frames
     */
    private suspend fun decryptAndPlayAudio() = withContext(Dispatchers.IO) {
        while (_state.value.isReceiving) {
            val frame = receiveQueue.poll()

            if (frame != null) {
                // Decrypt frame
                val decrypted = decryptFrame(frame)

                // Reverse Brahim processing
                val processed = reverseBrahimAudioProcessing(decrypted)

                // Convert to shorts and play
                val shorts = bytesToShorts(processed)
                audioTrack?.write(shorts, 0, shorts.size)

                // Update state
                _state.value = _state.value.copy(
                    receivedFrames = _state.value.receivedFrames + 1
                )
            } else {
                // No data, small delay
                delay(5)
            }

            yield()
        }
    }

    /**
     * Encrypt an audio frame using Wormhole Cipher
     */
    private fun encryptFrame(audio: ByteArray): EncryptedAudioFrame {
        val key = sessionKey ?: throw IllegalStateException("No session key")

        // Generate frame-specific IV using β
        val beta = BrahimConstants.BETA_SECURITY
        val frameIv = ByteArray(12)
        val counterBytes = ByteBuffer.allocate(8).putLong(frameCounter).array()
        for (i in 0 until 12) {
            frameIv[i] = ((counterBytes[i % 8].toInt() and 0xFF) xor
                    ((beta * 256 * (i + 1)).toInt() and 0xFF)).toByte()
        }

        // Encrypt
        val ciphertext = WormholeCipher.encrypt(audio, key, frameIv)

        frameCounter++

        return EncryptedAudioFrame(
            frameId = frameCounter - 1,
            channelId = currentChannel?.channelId ?: "",
            senderBnp = _state.value.currentChannel?.members?.firstOrNull() ?: "",
            ciphertext = ciphertext,
            iv = frameIv,
            timestamp = System.currentTimeMillis()
        )
    }

    /**
     * Decrypt an audio frame
     */
    private fun decryptFrame(frame: EncryptedAudioFrame): ByteArray {
        val key = sessionKey ?: throw IllegalStateException("No session key")
        return WormholeCipher.decrypt(frame.ciphertext, key, frame.iv)
    }

    /**
     * Apply Brahim-specific audio processing
     * Uses sequence frequencies for spectral shaping
     */
    private fun applyBrahimAudioProcessing(audio: ByteArray): ByteArray {
        // Simple implementation: add resonance markers
        // In production, use proper DSP with sequence-based filtering
        val processed = audio.copyOf()

        // Add β-weighted noise floor for anti-analysis
        val beta = BrahimConstants.BETA_SECURITY
        for (i in processed.indices) {
            val noise = ((Math.random() * 2 - 1) * beta * 3).toInt()
            processed[i] = (processed[i].toInt() + noise).coerceIn(-128, 127).toByte()
        }

        return processed
    }

    /**
     * Reverse Brahim audio processing
     */
    private fun reverseBrahimAudioProcessing(audio: ByteArray): ByteArray {
        // The β-noise is below audible threshold, so no reversal needed
        return audio
    }

    // Utility functions
    private fun shortsToBytes(shorts: ShortArray): ByteArray {
        val bytes = ByteArray(shorts.size * 2)
        for (i in shorts.indices) {
            bytes[i * 2] = (shorts[i].toInt() and 0xFF).toByte()
            bytes[i * 2 + 1] = (shorts[i].toInt() shr 8 and 0xFF).toByte()
        }
        return bytes
    }

    private fun bytesToShorts(bytes: ByteArray): ShortArray {
        val shorts = ShortArray(bytes.size / 2)
        for (i in shorts.indices) {
            shorts[i] = ((bytes[i * 2].toInt() and 0xFF) or
                    (bytes[i * 2 + 1].toInt() shl 8)).toShort()
        }
        return shorts
    }

    /**
     * Clean up resources
     */
    fun release() {
        stopTransmitting()
        stopReceiving()
        scope.cancel()
    }
}

/**
 * Create channel based on geographic proximity
 */
fun createProximityChannel(
    centerBnp: String,
    radiusKm: Double,
    name: String
): WalkieTalkieChannel {
    // Use Brahim sequence for radius tiers
    val tierIndex = BrahimConstants.SEQUENCE.indexOfFirst { it >= radiusKm * 10 }
    val actualRadius = if (tierIndex >= 0) {
        BrahimConstants.SEQUENCE[tierIndex] / 10.0
    } else {
        radiusKm
    }

    return WalkieTalkieChannel(
        channelId = "proximity_${centerBnp}_${actualRadius}",
        name = name,
        channelType = ChannelType.PROXIMITY,
        centerBnp = centerBnp,
        radiusKm = actualRadius,
        members = mutableListOf()
    )
}

/**
 * Create private channel between two users
 */
fun createPrivateChannel(
    user1Bnp: String,
    user2Bnp: String
): WalkieTalkieChannel {
    val channelId = if (user1Bnp < user2Bnp) {
        "${user1Bnp}_$user2Bnp"
    } else {
        "${user2Bnp}_$user1Bnp"
    }

    return WalkieTalkieChannel(
        channelId = "private_$channelId",
        name = "Private",
        channelType = ChannelType.PRIVATE,
        members = mutableListOf(user1Bnp, user2Bnp)
    )
}

/**
 * Create group channel
 */
fun createGroupChannel(
    name: String,
    members: List<String>
): WalkieTalkieChannel {
    return WalkieTalkieChannel(
        channelId = "group_${System.currentTimeMillis()}",
        name = name,
        channelType = ChannelType.GROUP,
        members = members.toMutableList()
    )
}

// Data classes

data class WalkieTalkieState(
    val isInitialized: Boolean = false,
    val isInChannel: Boolean = false,
    val isTransmitting: Boolean = false,
    val isReceiving: Boolean = false,
    val currentChannel: WalkieTalkieChannel? = null,
    val transmittedFrames: Long = 0,
    val receivedFrames: Long = 0
)

data class WalkieTalkieChannel(
    val channelId: String,
    val name: String,
    val channelType: ChannelType,
    val centerBnp: String? = null,
    val radiusKm: Double? = null,
    val members: MutableList<String> = mutableListOf()
)

enum class ChannelType {
    PRIVATE,    // 1-to-1
    GROUP,      // Multiple users, invite only
    PROXIMITY,  // Geographic, auto-join within radius
    PUBLIC      // Open to all
}

data class EncryptedAudioFrame(
    val frameId: Long,
    val channelId: String,
    val senderBnp: String,
    val ciphertext: ByteArray,
    val iv: ByteArray,
    val timestamp: Long
)
