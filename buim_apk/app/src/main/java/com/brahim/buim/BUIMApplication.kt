/**
 * BUIM Application - Main Application Class
 * ==========================================
 *
 * Entry point for the BUIM Android application.
 * Initializes all core services and manifold components.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim

import android.app.Application
import android.util.Log
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.manifold.UnifiedManifold
import com.brahim.buim.sdk.AgentRegistry
import com.brahim.buim.sdk.EgyptianFractionsAgent
import com.brahim.buim.sdk.SATSolverAgent
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

/**
 * BUIM Application class.
 */
class BUIMApplication : Application() {

    companion object {
        private const val TAG = "BUIMApplication"

        // Application-wide singleton
        lateinit var instance: BUIMApplication
            private set
    }

    // Application scope for coroutines
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    // Unified manifold - lazy initialized
    lateinit var unifiedManifold: UnifiedManifold
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this

        Log.i(TAG, "BUIM Application starting...")
        Log.i(TAG, "β = ${BrahimConstants.BETA_SECURITY}")
        Log.i(TAG, "φ = ${BrahimConstants.PHI}")
        Log.i(TAG, "S = ${BrahimConstants.BRAHIM_SUM}")

        // Verify mathematical foundation
        val verified = BrahimConstants.verifyBetaIdentities()
        Log.i(TAG, "Beta identities verified: $verified")

        // Initialize components in background
        applicationScope.launch {
            initializeManifold()
            registerAgents()
        }

        Log.i(TAG, "BUIM Application initialized")
    }

    /**
     * Initialize the unified manifold.
     */
    private suspend fun initializeManifold() {
        try {
            Log.i(TAG, "Initializing Unified Manifold...")
            unifiedManifold = UnifiedManifold(this)
            Log.i(TAG, "Unified Manifold ready")
        } catch (e: IOException)  // TODO: catch specific type {
            Log.e(TAG, "Failed to initialize manifold: ${e.message}")
        }
    }

    /**
     * Register SDK agents.
     */
    private fun registerAgents() {
        Log.i(TAG, "Registering SDK agents...")

        // Register Egyptian Fractions Agent
        AgentRegistry.register(EgyptianFractionsAgent())

        // Register SAT Solver Agent
        AgentRegistry.register(SATSolverAgent())

        Log.i(TAG, "Registered ${AgentRegistry.getAll().size} agents")
    }

    /**
     * Check if manifold is initialized.
     */
    fun isManifoldReady(): Boolean {
        return ::unifiedManifold.isInitialized
    }
}
