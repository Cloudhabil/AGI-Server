/**
 * Main Activity - BUIM Entry Point
 * =================================
 *
 * Primary activity for the BUIM Android application.
 * Implements navigation between screens.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.lifecycleScope
import com.brahim.buim.manifold.ManifoldResponse
import com.brahim.buim.safety.SafetyVerdict
import com.brahim.buim.ui.components.ChatMessage
import com.brahim.buim.ui.components.MessageSender
import com.brahim.buim.ui.screens.*
import com.brahim.buim.ui.theme.BuimTheme
import kotlinx.coroutines.launch
import java.util.UUID

/**
 * Navigation destinations.
 */
sealed class Screen {
    // Main Screens
    data object Home : Screen()
    data object Chat : Screen()
    data object Tools : Screen()
    data object Settings : Screen()

    // User-Friendly Screens
    data object Onboarding : Screen()
    data object ConsciousnessExplorer : Screen()
    data object QuickCalculator : Screen()
    data object About : Screen()
    data object Help : Screen()

    // Feature Screens
    data object Physics : Screen()
    data object Sudoku : Screen()
    data object KillerUseCases : Screen()
    data object Blockchain : Screen()
    data object SolarMap : Screen()
    data object Contacts : Screen()
    data class SecureChat(val peerName: String, val peerBnpAddress: String) : Screen()
    data object NetworkDiagnostics : Screen()
    data class ToolDetail(val toolId: String) : Screen()
}

/**
 * Main Activity for BUIM.
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            var currentScreen by remember { mutableStateOf<Screen>(Screen.Home) }
            var hasSeenOnboarding by remember { mutableStateOf(true) } // TODO: Load from DataStore
            var chatState by remember { mutableStateOf(ChatScreenState()) }
            var settingsState by remember { mutableStateOf(SettingsState()) }

            // Show onboarding for first-time users
            LaunchedEffect(Unit) {
                // TODO: Check DataStore for onboarding status
                // For now, skip onboarding by default
            }

            BuimTheme(
                darkTheme = settingsState.darkMode,
                dynamicColor = settingsState.dynamicColor
            ) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    when (val screen = currentScreen) {
                        // ===== MAIN SCREENS =====
                        is Screen.Home -> {
                            HomeScreen(
                                onNavigate = { destination ->
                                    when (destination) {
                                        "chat" -> currentScreen = Screen.Chat
                                        "tools" -> currentScreen = Screen.Tools
                                        "physics" -> currentScreen = Screen.Physics
                                        "consciousness" -> currentScreen = Screen.ConsciousnessExplorer
                                        "calculator" -> currentScreen = Screen.QuickCalculator
                                        "sudoku" -> currentScreen = Screen.Sudoku
                                        "secure_chat" -> currentScreen = Screen.Contacts
                                        "settings" -> currentScreen = Screen.Settings
                                        "help" -> currentScreen = Screen.Help
                                        "about" -> currentScreen = Screen.About
                                    }
                                }
                            )
                        }

                        is Screen.Chat -> {
                            ChatScreen(
                                state = chatState,
                                onSendMessage = { message ->
                                    handleSendMessage(
                                        message = message,
                                        currentState = chatState,
                                        onStateChange = { chatState = it }
                                    )
                                },
                                onNavigateToTools = { currentScreen = Screen.Tools },
                                onNavigateToSettings = { currentScreen = Screen.Settings }
                            )
                        }

                        is Screen.Tools -> {
                            ToolsScreen(
                                onToolSelected = { toolId ->
                                    when (toolId) {
                                        "physics_calculator" -> currentScreen = Screen.Physics
                                        "brahim_sudoku" -> currentScreen = Screen.Sudoku
                                        "killer_use_cases" -> currentScreen = Screen.KillerUseCases
                                        "solar_map" -> currentScreen = Screen.SolarMap
                                        "secure_chat" -> currentScreen = Screen.Contacts
                                        "network_diagnostics" -> currentScreen = Screen.NetworkDiagnostics
                                        "consciousness_explorer" -> currentScreen = Screen.ConsciousnessExplorer
                                        "quick_calculator" -> currentScreen = Screen.QuickCalculator
                                        else -> currentScreen = Screen.ToolDetail(toolId)
                                    }
                                },
                                onNavigateBack = { currentScreen = Screen.Home }
                            )
                        }

                        is Screen.Settings -> {
                            SettingsScreen(
                                state = settingsState,
                                onStateChange = { settingsState = it },
                                onNavigateBack = { currentScreen = Screen.Home }
                            )
                        }

                        // ===== USER-FRIENDLY SCREENS =====
                        is Screen.Onboarding -> {
                            OnboardingScreen(
                                onComplete = {
                                    hasSeenOnboarding = true
                                    currentScreen = Screen.Home
                                }
                            )
                        }

                        is Screen.ConsciousnessExplorer -> {
                            ConsciousnessExplorerScreen(
                                onBack = { currentScreen = Screen.Home }
                            )
                        }

                        is Screen.QuickCalculator -> {
                            QuickCalculatorScreen(
                                onBack = { currentScreen = Screen.Home }
                            )
                        }

                        is Screen.About -> {
                            AboutScreen(
                                onBack = { currentScreen = Screen.Home }
                            )
                        }

                        is Screen.Help -> {
                            HelpScreen(
                                onBack = { currentScreen = Screen.Home }
                            )
                        }

                        // ===== FEATURE SCREENS =====
                        is Screen.Physics -> {
                            PhysicsScreen(
                                onNavigateBack = { currentScreen = Screen.Home }
                            )
                        }

                        is Screen.Sudoku -> {
                            SudokuScreen(
                                onNavigateBack = { currentScreen = Screen.Home }
                            )
                        }

                        is Screen.KillerUseCases -> {
                            KillerUseCasesScreen(
                                onNavigateBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.Blockchain -> {
                            // Blockchain explorer - can be expanded
                            KillerUseCasesScreen(
                                onNavigateBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.SolarMap -> {
                            SolarMapScreen(
                                onNavigateBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.ToolDetail -> {
                            // Tool detail screen - can be expanded later
                            ToolsScreen(
                                onToolSelected = { },
                                onNavigateBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.Contacts -> {
                            ContactsScreen(
                                onContactClick = { contact ->
                                    currentScreen = Screen.SecureChat(
                                        peerName = contact.name,
                                        peerBnpAddress = contact.bnpAddress
                                    )
                                },
                                onNewChat = { /* Open new chat dialog */ },
                                onBack = { currentScreen = Screen.Home }
                            )
                        }

                        is Screen.SecureChat -> {
                            SecureChatScreen(
                                peerName = screen.peerName,
                                peerBnpAddress = screen.peerBnpAddress,
                                onBack = { currentScreen = Screen.Contacts }
                            )
                        }

                        is Screen.NetworkDiagnostics -> {
                            NetworkDiagnosticsScreen(
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }
                    }
                }
            }
        }
    }

    /**
     * Handle sending a message.
     */
    private fun handleSendMessage(
        message: String,
        currentState: ChatScreenState,
        onStateChange: (ChatScreenState) -> Unit
    ) {
        // Add user message
        val userMessage = ChatMessage(
            id = UUID.randomUUID().toString(),
            content = message,
            sender = MessageSender.USER
        )

        onStateChange(
            currentState.copy(
                messages = currentState.messages + userMessage,
                isLoading = true,
                error = null
            )
        )

        // Process through manifold
        lifecycleScope.launch {
            try {
                val app = application as BUIMApplication

                if (app.isManifoldReady()) {
                    val response = app.unifiedManifold.query(message)
                    handleManifoldResponse(response, currentState, userMessage, onStateChange)
                } else {
                    // Manifold not ready - simple response
                    val assistantMessage = ChatMessage(
                        id = UUID.randomUUID().toString(),
                        content = "Manifold initializing... Please try again in a moment.",
                        sender = MessageSender.ASSISTANT,
                        metadata = mapOf("safety" to SafetyVerdict.NOMINAL.name)
                    )

                    onStateChange(
                        currentState.copy(
                            messages = currentState.messages + userMessage + assistantMessage,
                            isLoading = false
                        )
                    )
                }
            } catch (e: Exception) {
                // Catch any exception
                val errorMessage = ChatMessage(
                    id = UUID.randomUUID().toString(),
                    content = "Error: ${e.message}",
                    sender = MessageSender.SYSTEM
                )

                onStateChange(
                    currentState.copy(
                        messages = currentState.messages + userMessage + errorMessage,
                        isLoading = false,
                        error = e.message
                    )
                )
            }
        }
    }

    /**
     * Handle manifold response.
     */
    private fun handleManifoldResponse(
        response: ManifoldResponse,
        currentState: ChatScreenState,
        userMessage: ChatMessage,
        onStateChange: (ChatScreenState) -> Unit
    ) {
        val assistantMessage = ChatMessage(
            id = UUID.randomUUID().toString(),
            content = response.result?.toString() ?: "I couldn't process that request.",
            sender = MessageSender.ASSISTANT,
            metadata = mapOf(
                "skill" to (response.skillId ?: "unknown"),
                "safety" to response.safetyVerdict.name,
                "territory" to response.territory.name
            )
        )

        onStateChange(
            currentState.copy(
                messages = currentState.messages + userMessage + assistantMessage,
                isLoading = false,
                currentSafetyVerdict = response.safetyVerdict,
                currentResonance = response.resonance
            )
        )
    }
}
