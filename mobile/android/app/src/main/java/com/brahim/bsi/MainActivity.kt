/**
 * Brahim Secure Intelligence - Main Activity
 * ===========================================
 *
 * Entry point for the BSI Android application.
 * Unified interface for all Brahim framework modules.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-24
 */

package com.brahim.bsi

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.brahim.bsi.core.BrahimConstants
import com.brahim.bsi.cipher.WormholeCipher
import com.brahim.bsi.safety.ASIOSGuard
import com.brahim.bsi.router.IntentRouter
import com.brahim.bsi.agent.BOAAgent

/**
 * Main Activity - BSI Application Entry Point
 */
class MainActivity : AppCompatActivity() {

    // Core modules
    private lateinit var agent: BOAAgent
    private lateinit var cipher: WormholeCipher
    private lateinit var safetyGuard: ASIOSGuard
    private lateinit var router: IntentRouter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(R.layout.activity_main)

        // Initialize modules
        initializeModules()

        // Run verification
        runStartupVerification()
    }

    /**
     * Initialize all BSI modules.
     */
    private fun initializeModules() {
        // Generate or load encryption key
        val key = WormholeCipher.generateKey()

        // Initialize modules
        agent = BOAAgent()
        cipher = WormholeCipher(key)
        safetyGuard = ASIOSGuard()
        router = IntentRouter()
    }

    /**
     * Run startup verification of mathematical constants.
     */
    private fun runStartupVerification() {
        val verification = BrahimConstants.verifyBetaIdentities()

        if (verification["all_verified"] == true) {
            showMessage("BSI initialized: beta = ${BrahimConstants.BETA_SECURITY}")
        } else {
            showMessage("Warning: Constant verification failed!")
        }
    }

    /**
     * Process user input through the agent.
     */
    fun processInput(input: String): String {
        val response = agent.process(input)
        return """
            Territory: ${response.territory.name}
            Confidence: ${(response.confidence * 100).toInt()}%
            Safety: ${(response.safetyScore * 100).toInt()}%

            ${response.content}
        """.trimIndent()
    }

    /**
     * Encrypt a message using Wormhole Cipher.
     */
    fun encryptMessage(message: String): ByteArray {
        return cipher.encrypt(message.toByteArray(Charsets.UTF_8))
    }

    /**
     * Decrypt a message using Wormhole Cipher.
     */
    fun decryptMessage(ciphertext: ByteArray): String {
        return cipher.decrypt(ciphertext).toString(Charsets.UTF_8)
    }

    /**
     * Check safety of an embedding.
     */
    fun checkSafety(embedding: DoubleArray): Map<String, Any> {
        val assessment = safetyGuard.assessSafety(embedding)
        return mapOf(
            "verdict" to assessment.verdict.name,
            "safety_score" to assessment.safetyScore,
            "on_critical_line" to assessment.isOnCriticalLine
        )
    }

    /**
     * Route a query to territory.
     */
    fun routeQuery(query: String): Map<String, Any> {
        return router.routeWithAnalysis(query)
    }

    /**
     * Get system status.
     */
    fun getSystemStatus(): Map<String, Any> {
        return mapOf(
            "app" to "Brahim Secure Intelligence",
            "version" to "1.0.0",
            "beta_security" to BrahimConstants.BETA_SECURITY,
            "phi" to BrahimConstants.PHI,
            "constants_verified" to BrahimConstants.verifyBetaIdentities()["all_verified"],
            "agent" to agent.getAgentInfo(),
            "cipher" to cipher.getCipherInfo(),
            "safety" to safetyGuard.getGuardInfo(),
            "router" to router.getRouterInfo()
        )
    }

    /**
     * Show a toast message.
     */
    private fun showMessage(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
}
