/**
 * Onion Protocol - Multi-Layer Privacy Protection
 * ================================================
 *
 * Implements onion-style encryption with multiple layers for
 * enhanced privacy protection.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.cipher

import com.brahim.buim.core.BrahimConstants
import java.security.SecureRandom
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import kotlin.math.pow

/**
 * Onion layer with its key material.
 */
data class OnionLayer(
    val layerId: Int,
    val keyMaterial: ByteArray,
    val ciphertext: ByteArray
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is OnionLayer) return false
        return layerId == other.layerId &&
               keyMaterial.contentEquals(other.keyMaterial) &&
               ciphertext.contentEquals(other.ciphertext)
    }

    override fun hashCode(): Int {
        var result = layerId
        result = 31 * result + keyMaterial.contentHashCode()
        result = 31 * result + ciphertext.contentHashCode()
        return result
    }
}

/**
 * Complete onion packet with all layers.
 */
data class OnionPacket(
    val layers: List<OnionLayer>,
    val metadata: Map<String, Any>
)

/**
 * Onion Protocol implementation using Brahim security constants.
 *
 * Each layer uses a different key derived from the master key and
 * layer index using the golden ratio hierarchy.
 */
class OnionProtocol(private val masterKey: ByteArray, private val numLayers: Int = 3) {

    companion object {
        private const val LAYER_KEY_SIZE = 32

        /** Maximum recommended layers */
        const val MAX_LAYERS = 7

        /** Generate a new random master key */
        fun generateMasterKey(): ByteArray {
            val key = ByteArray(32)
            SecureRandom().nextBytes(key)
            return key
        }
    }

    // Layer ciphers (one per layer)
    private val layerCiphers: List<WormholeCipher>

    init {
        require(numLayers in 1..MAX_LAYERS) {
            "Number of layers must be between 1 and $MAX_LAYERS"
        }

        // Derive layer keys using golden ratio powers
        layerCiphers = (0 until numLayers).map { i ->
            val layerKey = deriveLayerKey(i)
            WormholeCipher(layerKey)
        }
    }

    /**
     * Derive layer key using HKDF with golden ratio salt.
     */
    private fun deriveLayerKey(layerIndex: Int): ByteArray {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(masterKey, "HmacSHA256"))

        // Salt includes layer index and golden ratio component
        val phiComponent = BrahimConstants.PHI.pow(layerIndex.toDouble())
        val salt = "layer-$layerIndex-${phiComponent}".toByteArray()

        mac.update(salt)
        return mac.doFinal().copyOf(LAYER_KEY_SIZE)
    }

    /**
     * Wrap plaintext in multiple onion layers.
     *
     * @param plaintext Data to protect
     * @return Onion packet with all layers
     */
    fun wrap(plaintext: ByteArray): OnionPacket {
        var currentData = plaintext
        val layers = mutableListOf<OnionLayer>()

        // Apply layers from innermost to outermost
        for (i in 0 until numLayers) {
            val cipher = layerCiphers[i]
            val encrypted = cipher.encrypt(currentData)

            layers.add(OnionLayer(
                layerId = i,
                keyMaterial = encrypted.nonce,
                ciphertext = encrypted.ciphertext
            ))

            // Combine nonce and ciphertext for next layer
            currentData = encrypted.nonce + encrypted.ciphertext
        }

        return OnionPacket(
            layers = layers,
            metadata = mapOf(
                "numLayers" to numLayers,
                "protocol" to "OnionProtocol-v1",
                "beta" to BrahimConstants.BETA_SECURITY
            )
        )
    }

    /**
     * Unwrap an onion packet to retrieve the plaintext.
     *
     * @param packet Onion packet to unwrap
     * @return Original plaintext
     */
    fun unwrap(packet: OnionPacket): ByteArray {
        require(packet.layers.size == numLayers) {
            "Packet has ${packet.layers.size} layers, expected $numLayers"
        }

        // Get the outermost ciphertext
        val outerLayer = packet.layers.last()
        var currentData = outerLayer.keyMaterial + outerLayer.ciphertext

        // Peel layers from outermost to innermost
        for (i in (numLayers - 1) downTo 0) {
            val cipher = layerCiphers[i]
            currentData = cipher.decryptLegacy(currentData)
        }

        return currentData
    }

    /**
     * Wrap with simplified output (just the final ciphertext).
     */
    fun wrapSimple(plaintext: ByteArray): ByteArray {
        var currentData = plaintext

        for (i in 0 until numLayers) {
            val cipher = layerCiphers[i]
            currentData = cipher.encryptLegacy(currentData)
        }

        return currentData
    }

    /**
     * Unwrap from simplified format.
     */
    fun unwrapSimple(ciphertext: ByteArray): ByteArray {
        var currentData = ciphertext

        for (i in (numLayers - 1) downTo 0) {
            val cipher = layerCiphers[i]
            currentData = cipher.decryptLegacy(currentData)
        }

        return currentData
    }

    /**
     * Get protocol info.
     */
    fun getProtocolInfo(): Map<String, Any> {
        return mapOf(
            "protocol" to "OnionProtocol",
            "version" to "1.0",
            "numLayers" to numLayers,
            "maxLayers" to MAX_LAYERS,
            "layerKeySize" to LAYER_KEY_SIZE,
            "beta" to BrahimConstants.BETA_SECURITY,
            "derivation" to "HKDF with golden ratio salts"
        )
    }
}
