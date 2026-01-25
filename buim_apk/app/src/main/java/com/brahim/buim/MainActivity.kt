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
    data object Chat : Screen()
    data object Tools : Screen()
    data object Settings : Screen()
    data object Physics : Screen()
    data object Sudoku : Screen()
    data class ToolDetail(val toolId: String) : Screen()
}

/**
 * Main Activity for BUIM.
 */
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            var currentScreen by remember { mutableStateOf<Screen>(Screen.Chat) }
            var chatState by remember { mutableStateOf(ChatScreenState()) }
            var settingsState by remember { mutableStateOf(SettingsState()) }

            BuimTheme(
                darkTheme = settingsState.darkMode,
                dynamicColor = settingsState.dynamicColor
            ) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    when (val screen = currentScreen) {
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
                                        else -> currentScreen = Screen.ToolDetail(toolId)
                                    }
                                },
                                onNavigateBack = { currentScreen = Screen.Chat }
                            )
                        }

                        is Screen.Settings -> {
                            SettingsScreen(
                                state = settingsState,
                                onStateChange = { settingsState = it },
                                onNavigateBack = { currentScreen = Screen.Chat }
                            )
                        }

                        is Screen.Physics -> {
                            PhysicsScreen(
                                onNavigateBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.Sudoku -> {
                            SudokuScreen(
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
