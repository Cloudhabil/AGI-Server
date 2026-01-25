/**
 * Preferences Store - DataStore Wrapper
 * ======================================
 *
 * Type-safe preferences storage using DataStore.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import java.io.IOException

// Extension property for DataStore
private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "buim_settings")

/**
 * Preferences keys.
 */
object PreferenceKeys {
    val DARK_MODE = booleanPreferencesKey("dark_mode")
    val DYNAMIC_COLOR = booleanPreferencesKey("dynamic_color")
    val SAFETY_ENABLED = booleanPreferencesKey("safety_enabled")
    val RESONANCE_THRESHOLD = floatPreferencesKey("resonance_threshold")
    val CLOUD_SYNC_ENABLED = booleanPreferencesKey("cloud_sync_enabled")
    val BIOMETRIC_ENABLED = booleanPreferencesKey("biometric_enabled")
    val API_KEY = stringPreferencesKey("api_key")
    val CURRENT_SESSION_ID = stringPreferencesKey("current_session_id")
    val FIRST_LAUNCH = booleanPreferencesKey("first_launch")
    val MANIFOLD_INITIALIZED = booleanPreferencesKey("manifold_initialized")
}

/**
 * User preferences data class.
 */
data class UserPreferences(
    val darkMode: Boolean = true,
    val dynamicColor: Boolean = false,
    val safetyEnabled: Boolean = true,
    val resonanceThreshold: Float = 0.95f,
    val cloudSyncEnabled: Boolean = false,
    val biometricEnabled: Boolean = false,
    val apiKey: String = "",
    val currentSessionId: String? = null,
    val firstLaunch: Boolean = true,
    val manifoldInitialized: Boolean = false
)

/**
 * Preferences Store for managing app settings.
 */
class PreferencesStore(private val context: Context) {

    private val dataStore = context.dataStore

    /**
     * Get all preferences as a flow.
     */
    val preferencesFlow: Flow<UserPreferences> = dataStore.data
        .catch { exception ->
            if (exception is IOException) {
                emit(emptyPreferences())
            } else {
                throw exception
            }
        }
        .map { preferences ->
            UserPreferences(
                darkMode = preferences[PreferenceKeys.DARK_MODE] ?: true,
                dynamicColor = preferences[PreferenceKeys.DYNAMIC_COLOR] ?: false,
                safetyEnabled = preferences[PreferenceKeys.SAFETY_ENABLED] ?: true,
                resonanceThreshold = preferences[PreferenceKeys.RESONANCE_THRESHOLD] ?: 0.95f,
                cloudSyncEnabled = preferences[PreferenceKeys.CLOUD_SYNC_ENABLED] ?: false,
                biometricEnabled = preferences[PreferenceKeys.BIOMETRIC_ENABLED] ?: false,
                apiKey = preferences[PreferenceKeys.API_KEY] ?: "",
                currentSessionId = preferences[PreferenceKeys.CURRENT_SESSION_ID],
                firstLaunch = preferences[PreferenceKeys.FIRST_LAUNCH] ?: true,
                manifoldInitialized = preferences[PreferenceKeys.MANIFOLD_INITIALIZED] ?: false
            )
        }

    /**
     * Update dark mode setting.
     */
    suspend fun setDarkMode(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferenceKeys.DARK_MODE] = enabled
        }
    }

    /**
     * Update dynamic color setting.
     */
    suspend fun setDynamicColor(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferenceKeys.DYNAMIC_COLOR] = enabled
        }
    }

    /**
     * Update safety enabled setting.
     */
    suspend fun setSafetyEnabled(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferenceKeys.SAFETY_ENABLED] = enabled
        }
    }

    /**
     * Update resonance threshold.
     */
    suspend fun setResonanceThreshold(threshold: Float) {
        dataStore.edit { preferences ->
            preferences[PreferenceKeys.RESONANCE_THRESHOLD] = threshold
        }
    }

    /**
     * Update cloud sync setting.
     */
    suspend fun setCloudSyncEnabled(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferenceKeys.CLOUD_SYNC_ENABLED] = enabled
        }
    }

    /**
     * Update biometric authentication setting.
     */
    suspend fun setBiometricEnabled(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferenceKeys.BIOMETRIC_ENABLED] = enabled
        }
    }

    /**
     * Update API key.
     */
    suspend fun setApiKey(key: String) {
        dataStore.edit { preferences ->
            preferences[PreferenceKeys.API_KEY] = key
        }
    }

    /**
     * Update current session ID.
     */
    suspend fun setCurrentSessionId(sessionId: String?) {
        dataStore.edit { preferences ->
            if (sessionId != null) {
                preferences[PreferenceKeys.CURRENT_SESSION_ID] = sessionId
            } else {
                preferences.remove(PreferenceKeys.CURRENT_SESSION_ID)
            }
        }
    }

    /**
     * Mark first launch completed.
     */
    suspend fun setFirstLaunchComplete() {
        dataStore.edit { preferences ->
            preferences[PreferenceKeys.FIRST_LAUNCH] = false
        }
    }

    /**
     * Mark manifold as initialized.
     */
    suspend fun setManifoldInitialized(initialized: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferenceKeys.MANIFOLD_INITIALIZED] = initialized
        }
    }

    /**
     * Clear all preferences.
     */
    suspend fun clearAll() {
        dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
