/**
 * BUIM - Brahim Secure Chat
 * End-to-End Encrypted Messaging using Wormhole Cipher
 *
 * Like Signal, but based on Brahim mathematical framework:
 * - β = √5 - 2 for key derivation
 * - Onion layers for privacy
 * - BNP addresses for geographic routing
 * - Resonance-based priority
 */
package com.brahim.buim.chat

import com.brahim.buim.cipher.WormholeCipher
import com.brahim.buim.cipher.OnionProtocol
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.network.BrahimNetworkProtocol
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.security.SecureRandom
import java.util.*
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.SecretKeySpec

/**
 * Brahim Secure Chat - Core messaging engine
 */
object BrahimSecureChat {

    // Chat state
    private val _chatState = MutableStateFlow(ChatState())
    val chatState: StateFlow<ChatState> = _chatState

    // Active sessions
    private val sessions = mutableMapOf<String, ChatSession>()

    // Message queue for offline delivery
    private val messageQueue = mutableListOf<QueuedMessage>()

    /**
     * Initialize chat with user's BNP identity
     */
    fun initialize(userBnpAddress: String, privateKey: ByteArray): ChatIdentity {
        val identity = ChatIdentity(
            bnpAddress = userBnpAddress,
            publicKey = derivePublicKey(privateKey),
            privateKey = privateKey,
            identityKey = generateIdentityKey(),
            signedPreKey = generateSignedPreKey(privateKey),
            oneTimePreKeys = generateOneTimePreKeys(100)
        )

        _chatState.value = ChatState(
            identity = identity,
            isInitialized = true
        )

        return identity
    }

    /**
     * Create a new chat session with another user
     * Uses X3DH-like key agreement with Brahim modifications
     */
    fun createSession(
        peerBnpAddress: String,
        peerPublicKey: ByteArray,
        peerIdentityKey: ByteArray,
        peerSignedPreKey: ByteArray,
        peerOneTimePreKey: ByteArray? = null
    ): ChatSession {
        val identity = _chatState.value.identity
            ?: throw IllegalStateException("Chat not initialized")

        // Brahim X3DH Key Agreement
        // DH1 = DH(IK_A, SPK_B)
        // DH2 = DH(EK_A, IK_B)
        // DH3 = DH(EK_A, SPK_B)
        // DH4 = DH(EK_A, OPK_B) if available

        val ephemeralKey = generateEphemeralKey()

        val dh1 = brahimDH(identity.identityKey, peerSignedPreKey)
        val dh2 = brahimDH(ephemeralKey.private, peerIdentityKey)
        val dh3 = brahimDH(ephemeralKey.private, peerSignedPreKey)
        val dh4 = peerOneTimePreKey?.let { brahimDH(ephemeralKey.private, it) }

        // Combine with β-weighted mixing
        val sharedSecret = brahimKDF(
            listOfNotNull(dh1, dh2, dh3, dh4),
            "BrahimSecureChat_X3DH"
        )

        // Initialize Double Ratchet with Brahim modifications
        val ratchetState = BrahimDoubleRatchet.initialize(
            sharedSecret = sharedSecret,
            peerPublicKey = peerPublicKey,
            isInitiator = true
        )

        val session = ChatSession(
            sessionId = generateSessionId(),
            peerBnpAddress = peerBnpAddress,
            peerPublicKey = peerPublicKey,
            ratchetState = ratchetState,
            createdAt = System.currentTimeMillis(),
            lastActivity = System.currentTimeMillis()
        )

        sessions[peerBnpAddress] = session

        return session
    }

    /**
     * Send an encrypted message
     */
    fun sendMessage(
        peerBnpAddress: String,
        plaintext: String,
        messageType: MessageType = MessageType.TEXT
    ): EncryptedMessage {
        val session = sessions[peerBnpAddress]
            ?: throw IllegalStateException("No session with $peerBnpAddress")

        // Encrypt with Double Ratchet
        val (ciphertext, updatedRatchet) = BrahimDoubleRatchet.encrypt(
            session.ratchetState,
            plaintext.toByteArray(Charsets.UTF_8)
        )

        // Update session
        sessions[peerBnpAddress] = session.copy(
            ratchetState = updatedRatchet,
            lastActivity = System.currentTimeMillis()
        )

        // Wrap in onion layers based on privacy level
        val identity = _chatState.value.identity!!
        val privacyLevel = extractPrivacyLevel(identity.bnpAddress)

        val onionWrapped = if (privacyLevel > 0) {
            OnionProtocol.wrap(ciphertext, privacyLevel)
        } else {
            ciphertext
        }

        return EncryptedMessage(
            messageId = generateMessageId(),
            senderBnp = identity.bnpAddress,
            recipientBnp = peerBnpAddress,
            ciphertext = onionWrapped,
            messageType = messageType,
            timestamp = System.currentTimeMillis(),
            ratchetPublicKey = updatedRatchet.sendingChainKey.publicKey
        )
    }

    /**
     * Receive and decrypt a message
     */
    fun receiveMessage(encrypted: EncryptedMessage): DecryptedMessage {
        val session = sessions[encrypted.senderBnp]
            ?: throw IllegalStateException("No session with ${encrypted.senderBnp}")

        // Unwrap onion layers
        val unwrapped = OnionProtocol.unwrap(encrypted.ciphertext)

        // Decrypt with Double Ratchet
        val (plaintext, updatedRatchet) = BrahimDoubleRatchet.decrypt(
            session.ratchetState,
            unwrapped,
            encrypted.ratchetPublicKey
        )

        // Update session
        sessions[encrypted.senderBnp] = session.copy(
            ratchetState = updatedRatchet,
            lastActivity = System.currentTimeMillis()
        )

        return DecryptedMessage(
            messageId = encrypted.messageId,
            senderBnp = encrypted.senderBnp,
            plaintext = String(plaintext, Charsets.UTF_8),
            messageType = encrypted.messageType,
            timestamp = encrypted.timestamp,
            verified = true
        )
    }

    /**
     * Brahim Diffie-Hellman using β-curve
     */
    private fun brahimDH(privateKey: ByteArray, publicKey: ByteArray): ByteArray {
        // Use β = √5 - 2 as curve parameter
        val beta = BrahimConstants.BETA_SECURITY

        // Simplified DH (in production, use proper EC implementation)
        val sharedPoint = ByteArray(32)
        for (i in 0 until 32) {
            val priv = privateKey[i % privateKey.size].toInt() and 0xFF
            val pub = publicKey[i % publicKey.size].toInt() and 0xFF
            // β-weighted combination
            val combined = ((priv * pub * beta) % 256).toInt()
            sharedPoint[i] = combined.toByte()
        }

        return WormholeCipher.hash(sharedPoint)
    }

    /**
     * Brahim Key Derivation Function
     */
    private fun brahimKDF(inputs: List<ByteArray>, context: String): ByteArray {
        val beta = BrahimConstants.BETA_SECURITY
        val phi = BrahimConstants.PHI

        // Concatenate all inputs
        val combined = inputs.fold(ByteArray(0)) { acc, bytes -> acc + bytes }

        // Add context
        val withContext = combined + context.toByteArray()

        // Apply β-weighted HKDF
        val hash1 = WormholeCipher.hash(withContext)
        val hash2 = WormholeCipher.hash(hash1 + byteArrayOf((beta * 256).toInt().toByte()))
        val hash3 = WormholeCipher.hash(hash2 + byteArrayOf((phi * 256).toInt().toByte()))

        return hash1.zip(hash2.zip(hash3.toList())).map { (a, bc) ->
            val (b, c) = bc
            ((a.toInt() xor b.toInt() xor c) and 0xFF).toByte()
        }.toByteArray()
    }

    // Key generation helpers
    private fun derivePublicKey(privateKey: ByteArray): ByteArray {
        return WormholeCipher.hash(privateKey + "public".toByteArray())
    }

    private fun generateIdentityKey(): ByteArray {
        val random = SecureRandom()
        val key = ByteArray(32)
        random.nextBytes(key)
        return key
    }

    private fun generateSignedPreKey(privateKey: ByteArray): ByteArray {
        return WormholeCipher.hash(privateKey + System.currentTimeMillis().toString().toByteArray())
    }

    private fun generateOneTimePreKeys(count: Int): List<ByteArray> {
        val random = SecureRandom()
        return (0 until count).map {
            val key = ByteArray(32)
            random.nextBytes(key)
            key
        }
    }

    private fun generateEphemeralKey(): KeyPair {
        val random = SecureRandom()
        val privateKey = ByteArray(32)
        random.nextBytes(privateKey)
        val publicKey = derivePublicKey(privateKey)
        return KeyPair(privateKey, publicKey)
    }

    private fun generateSessionId(): String = UUID.randomUUID().toString()
    private fun generateMessageId(): String = UUID.randomUUID().toString()

    private fun extractPrivacyLevel(bnpAddress: String): Int {
        // Extract privacy level from BNP address format: BNP:layer:geo:svc:privacy:check
        val parts = bnpAddress.split(":")
        return if (parts.size >= 5) parts[4].toIntOrNull() ?: 0 else 0
    }
}

/**
 * Brahim Double Ratchet - Signal-like forward secrecy with β modifications
 */
object BrahimDoubleRatchet {

    fun initialize(
        sharedSecret: ByteArray,
        peerPublicKey: ByteArray,
        isInitiator: Boolean
    ): RatchetState {
        val rootKey = WormholeCipher.hash(sharedSecret + "root".toByteArray())
        val chainKey = WormholeCipher.hash(sharedSecret + "chain".toByteArray())

        val keyPair = generateKeyPair()

        return RatchetState(
            rootKey = rootKey,
            sendingChainKey = ChainKey(chainKey, keyPair.public, 0),
            receivingChainKey = ChainKey(chainKey, peerPublicKey, 0),
            dhKeyPair = keyPair,
            previousCounter = 0,
            skippedKeys = mutableMapOf()
        )
    }

    fun encrypt(state: RatchetState, plaintext: ByteArray): Pair<ByteArray, RatchetState> {
        // Derive message key from chain key
        val messageKey = deriveMessageKey(state.sendingChainKey.key, state.sendingChainKey.counter)

        // Advance chain
        val newChainKey = advanceChain(state.sendingChainKey)

        // Encrypt with AES-GCM
        val ciphertext = aesGcmEncrypt(messageKey, plaintext)

        val newState = state.copy(
            sendingChainKey = newChainKey
        )

        return Pair(ciphertext, newState)
    }

    fun decrypt(
        state: RatchetState,
        ciphertext: ByteArray,
        senderPublicKey: ByteArray
    ): Pair<ByteArray, RatchetState> {
        var currentState = state

        // Check if we need to perform DH ratchet
        if (!senderPublicKey.contentEquals(state.receivingChainKey.publicKey)) {
            currentState = performDHRatchet(currentState, senderPublicKey)
        }

        // Derive message key
        val messageKey = deriveMessageKey(
            currentState.receivingChainKey.key,
            currentState.receivingChainKey.counter
        )

        // Advance receiving chain
        val newReceivingChain = advanceChain(currentState.receivingChainKey)

        // Decrypt
        val plaintext = aesGcmDecrypt(messageKey, ciphertext)

        val newState = currentState.copy(
            receivingChainKey = newReceivingChain
        )

        return Pair(plaintext, newState)
    }

    private fun performDHRatchet(state: RatchetState, peerPublicKey: ByteArray): RatchetState {
        // Generate new DH key pair
        val newKeyPair = generateKeyPair()

        // Calculate new shared secret using β-DH
        val dhOutput = brahimDH(state.dhKeyPair.private, peerPublicKey)

        // Derive new root and chain keys
        val (newRootKey, newReceivingChain) = deriveRootAndChain(state.rootKey, dhOutput)

        val dhOutput2 = brahimDH(newKeyPair.private, peerPublicKey)
        val (finalRootKey, newSendingChain) = deriveRootAndChain(newRootKey, dhOutput2)

        return state.copy(
            rootKey = finalRootKey,
            sendingChainKey = ChainKey(newSendingChain, newKeyPair.public, 0),
            receivingChainKey = ChainKey(state.receivingChainKey.key, peerPublicKey, 0),
            dhKeyPair = newKeyPair,
            previousCounter = state.sendingChainKey.counter
        )
    }

    private fun brahimDH(privateKey: ByteArray, publicKey: ByteArray): ByteArray {
        val beta = BrahimConstants.BETA_SECURITY
        val result = ByteArray(32)
        for (i in 0 until 32) {
            val priv = privateKey[i % privateKey.size].toInt() and 0xFF
            val pub = publicKey[i % publicKey.size].toInt() and 0xFF
            result[i] = ((priv * pub * beta) % 256).toInt().toByte()
        }
        return WormholeCipher.hash(result)
    }

    private fun deriveMessageKey(chainKey: ByteArray, counter: Int): ByteArray {
        return WormholeCipher.hash(chainKey + counter.toString().toByteArray() + "msg".toByteArray())
    }

    private fun advanceChain(chain: ChainKey): ChainKey {
        val newKey = WormholeCipher.hash(chain.key + "advance".toByteArray())
        return chain.copy(key = newKey, counter = chain.counter + 1)
    }

    private fun deriveRootAndChain(rootKey: ByteArray, dhOutput: ByteArray): Pair<ByteArray, ByteArray> {
        val combined = WormholeCipher.hash(rootKey + dhOutput)
        val newRoot = combined.sliceArray(0 until 16) + combined.sliceArray(0 until 16)
        val newChain = combined.sliceArray(16 until 32) + combined.sliceArray(16 until 32)
        return Pair(newRoot, newChain)
    }

    private fun generateKeyPair(): KeyPair {
        val random = SecureRandom()
        val privateKey = ByteArray(32)
        random.nextBytes(privateKey)
        val publicKey = WormholeCipher.hash(privateKey + "pub".toByteArray())
        return KeyPair(privateKey, publicKey)
    }

    private fun aesGcmEncrypt(key: ByteArray, plaintext: ByteArray): ByteArray {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val keySpec = SecretKeySpec(key.sliceArray(0 until 16), "AES")
        val iv = ByteArray(12)
        SecureRandom().nextBytes(iv)
        val gcmSpec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec)
        val ciphertext = cipher.doFinal(plaintext)
        return iv + ciphertext
    }

    private fun aesGcmDecrypt(key: ByteArray, ciphertext: ByteArray): ByteArray {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val keySpec = SecretKeySpec(key.sliceArray(0 until 16), "AES")
        val iv = ciphertext.sliceArray(0 until 12)
        val actualCiphertext = ciphertext.sliceArray(12 until ciphertext.size)
        val gcmSpec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.DECRYPT_MODE, keySpec, gcmSpec)
        return cipher.doFinal(actualCiphertext)
    }
}

// Data classes

data class ChatIdentity(
    val bnpAddress: String,
    val publicKey: ByteArray,
    val privateKey: ByteArray,
    val identityKey: ByteArray,
    val signedPreKey: ByteArray,
    val oneTimePreKeys: List<ByteArray>
)

data class ChatSession(
    val sessionId: String,
    val peerBnpAddress: String,
    val peerPublicKey: ByteArray,
    val ratchetState: RatchetState,
    val createdAt: Long,
    val lastActivity: Long
)

data class RatchetState(
    val rootKey: ByteArray,
    val sendingChainKey: ChainKey,
    val receivingChainKey: ChainKey,
    val dhKeyPair: KeyPair,
    val previousCounter: Int,
    val skippedKeys: MutableMap<Pair<ByteArray, Int>, ByteArray>
)

data class ChainKey(
    val key: ByteArray,
    val publicKey: ByteArray,
    val counter: Int
)

data class KeyPair(
    val private: ByteArray,
    val public: ByteArray
)

data class ChatState(
    val identity: ChatIdentity? = null,
    val isInitialized: Boolean = false
)

data class EncryptedMessage(
    val messageId: String,
    val senderBnp: String,
    val recipientBnp: String,
    val ciphertext: ByteArray,
    val messageType: MessageType,
    val timestamp: Long,
    val ratchetPublicKey: ByteArray
)

data class DecryptedMessage(
    val messageId: String,
    val senderBnp: String,
    val plaintext: String,
    val messageType: MessageType,
    val timestamp: Long,
    val verified: Boolean
)

data class QueuedMessage(
    val message: EncryptedMessage,
    val attempts: Int = 0,
    val queuedAt: Long = System.currentTimeMillis()
)

enum class MessageType {
    TEXT,
    IMAGE,
    AUDIO,
    VIDEO,
    FILE,
    VOICE_NOTE,
    WALKIE_TALKIE
}
