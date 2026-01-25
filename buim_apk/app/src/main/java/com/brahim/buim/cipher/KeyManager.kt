/**
 * Key Manager - Secure Key Storage
 * =================================
 *
 * Manages cryptographic keys using Android Keystore.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.cipher

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * Key Manager using Android Keystore for secure key storage.
 */
class KeyManager(private val context: Context) {

    companion object {
        private const val KEYSTORE_PROVIDER = "AndroidKeyStore"
        private const val MASTER_KEY_ALIAS = "buim_master_key"
        private const val AES_MODE = "AES/GCM/NoPadding"
        private const val GCM_TAG_LENGTH = 128
        private const val GCM_IV_LENGTH = 12
    }

    private val keyStore: KeyStore = KeyStore.getInstance(KEYSTORE_PROVIDER).apply {
        load(null)
    }

    /**
     * Initialize or retrieve the master key.
     */
    fun initializeMasterKey(): Boolean {
        return try {
            if (!keyStore.containsAlias(MASTER_KEY_ALIAS)) {
                generateMasterKey()
            }
            true
        } catch (e: IOException)  // TODO: catch specific type {
            false
        }
    }

    /**
     * Generate a new master key in the Android Keystore.
     */
    private fun generateMasterKey() {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            KEYSTORE_PROVIDER
        )

        val keySpec = KeyGenParameterSpec.Builder(
            MASTER_KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setUserAuthenticationRequired(false) // Set true for biometric requirement
            .build()

        keyGenerator.init(keySpec)
        keyGenerator.generateKey()
    }

    /**
     * Get the master key from Keystore.
     */
    private fun getMasterKey(): SecretKey {
        return keyStore.getKey(MASTER_KEY_ALIAS, null) as SecretKey
    }

    /**
     * Encrypt data using the master key.
     */
    fun encrypt(plaintext: ByteArray): ByteArray {
        val cipher = Cipher.getInstance(AES_MODE)
        cipher.init(Cipher.ENCRYPT_MODE, getMasterKey())

        val iv = cipher.iv
        val ciphertext = cipher.doFinal(plaintext)

        // Prepend IV to ciphertext
        return iv + ciphertext
    }

    /**
     * Decrypt data using the master key.
     */
    fun decrypt(ciphertext: ByteArray): ByteArray {
        require(ciphertext.size > GCM_IV_LENGTH) { "Ciphertext too short" }

        val iv = ciphertext.copyOfRange(0, GCM_IV_LENGTH)
        val encrypted = ciphertext.copyOfRange(GCM_IV_LENGTH, ciphertext.size)

        val cipher = Cipher.getInstance(AES_MODE)
        val spec = GCMParameterSpec(GCM_TAG_LENGTH, iv)
        cipher.init(Cipher.DECRYPT_MODE, getMasterKey(), spec)

        return cipher.doFinal(encrypted)
    }

    /**
     * Generate a new key for WormholeCipher and store it encrypted.
     */
    fun generateAndStoreWormholeKey(alias: String): ByteArray {
        val wormholeKey = WormholeCipher.generateKey()
        storeKey(alias, wormholeKey)
        return wormholeKey
    }

    /**
     * Store a key encrypted with the master key.
     */
    fun storeKey(alias: String, key: ByteArray) {
        val encryptedKey = encrypt(key)
        val prefs = context.getSharedPreferences("buim_keys", Context.MODE_PRIVATE)
        prefs.edit()
            .putString(alias, android.util.Base64.encodeToString(encryptedKey, android.util.Base64.NO_WRAP))
            .apply()
    }

    /**
     * Retrieve a stored key.
     */
    fun retrieveKey(alias: String): ByteArray? {
        val prefs = context.getSharedPreferences("buim_keys", Context.MODE_PRIVATE)
        val encoded = prefs.getString(alias, null) ?: return null
        val encrypted = android.util.Base64.decode(encoded, android.util.Base64.NO_WRAP)
        return decrypt(encrypted)
    }

    /**
     * Delete a stored key.
     */
    fun deleteKey(alias: String) {
        val prefs = context.getSharedPreferences("buim_keys", Context.MODE_PRIVATE)
        prefs.edit().remove(alias).apply()
    }

    /**
     * Check if master key exists.
     */
    fun hasMasterKey(): Boolean {
        return keyStore.containsAlias(MASTER_KEY_ALIAS)
    }

    /**
     * Delete all keys (use with caution).
     */
    fun deleteAllKeys() {
        keyStore.deleteEntry(MASTER_KEY_ALIAS)
        context.getSharedPreferences("buim_keys", Context.MODE_PRIVATE)
            .edit()
            .clear()
            .apply()
    }

    /**
     * Get key manager info.
     */
    fun getInfo(): Map<String, Any> {
        return mapOf(
            "provider" to KEYSTORE_PROVIDER,
            "algorithm" to "AES-256-GCM",
            "hasMasterKey" to hasMasterKey(),
            "tagLength" to GCM_TAG_LENGTH,
            "ivLength" to GCM_IV_LENGTH
        )
    }
}
