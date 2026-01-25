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
import com.brahim.buim.ui.screens.hubs.*
import com.brahim.buim.ui.screens.composite.*
import com.brahim.buim.ui.theme.BuimTheme
import kotlinx.coroutines.launch
import java.util.UUID

/**
 * Navigation destinations.
 */
sealed class Screen {
    // Main Screens
    data object Home : Screen()
    data object IntelligentHome : Screen()  // New adaptive home
    data object Chat : Screen()
    data object Tools : Screen()
    data object Settings : Screen()
    data object Roadmap : Screen()          // Growth roadmap to 214

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

    // Hub Screens (83 applications in 12 categories)
    data object PhysicsHub : Screen()
    data object MathHub : Screen()
    data object CosmologyHub : Screen()
    data object AviationHub : Screen()
    data object TrafficHub : Screen()
    data object BusinessHub : Screen()
    data object SolversHub : Screen()
    data object PlanetaryHub : Screen()
    data object SecurityHub : Screen()
    data object MLHub : Screen()
    data object VisualizationHub : Screen()
    data object UtilitiesHub : Screen()

    // Symmetry Dashboard
    data object SymmetryDashboard : Screen()

    // Composite Apps (21 skill-powered applications)
    data object CompositeAppsHub : Screen()
    data object UniverseSimulator : Screen()
    data object SmartNavigator : Screen()
    data object SecureBusiness : Screen()
    data object PINNLab : Screen()
    data object TitanColony : Screen()
    data object QuantumFinance : Screen()
    data object TrafficBrain : Screen()
    data object AerospaceOptimizer : Screen()
    data object CryptoObservatory : Screen()
    data object FairDivisionAI : Screen()
    data object CosmicCalculator : Screen()
    data object MarsMission : Screen()
    data object GoldenOptimizer : Screen()
    data object EmergencyResponse : Screen()
    data object ComplianceIntel : Screen()
    data object ResonanceLab : Screen()
    data object FleetManager : Screen()
    data object SATMLHybrid : Screen()
    data object DarkSector : Screen()
    data object BrahimWorkspace : Screen()
    data object KelimutuIntel : Screen()
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
                                        "intelligent_home" -> currentScreen = Screen.IntelligentHome
                                        "roadmap" -> currentScreen = Screen.Roadmap
                                    }
                                }
                            )
                        }

                        // ===== INTELLIGENT HOME (Adaptive Discovery) =====
                        is Screen.IntelligentHome -> {
                            IntelligentHomeScreen(
                                onNavigateToApp = { appId ->
                                    currentScreen = navigateToApp(appId)
                                },
                                onNavigateToRoadmap = { currentScreen = Screen.Roadmap },
                                onNavigateToChat = { currentScreen = Screen.Chat },
                                onNavigateToTools = { currentScreen = Screen.Tools }
                            )
                        }

                        // ===== GROWTH ROADMAP =====
                        is Screen.Roadmap -> {
                            RoadmapScreen(
                                onBack = { currentScreen = Screen.IntelligentHome },
                                onNavigateToApp = { appId ->
                                    currentScreen = navigateToApp(appId)
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
                                onNavigateToSettings = { currentScreen = Screen.Settings },
                                onNavigateToApp = { appId ->
                                    currentScreen = navigateToApp(appId)
                                },
                                onNavigateToHome = { currentScreen = Screen.IntelligentHome }
                            )
                        }

                        is Screen.Tools -> {
                            ToolsScreen(
                                onToolSelected = { toolId ->
                                    when (toolId) {
                                        // Symmetry & Composite Apps
                                        "symmetry_dashboard" -> currentScreen = Screen.SymmetryDashboard
                                        "composite_apps" -> currentScreen = Screen.CompositeAppsHub
                                        // Hub Routes
                                        "physics_hub" -> currentScreen = Screen.PhysicsHub
                                        "math_hub" -> currentScreen = Screen.MathHub
                                        "cosmology_hub" -> currentScreen = Screen.CosmologyHub
                                        "aviation_hub" -> currentScreen = Screen.AviationHub
                                        "traffic_hub" -> currentScreen = Screen.TrafficHub
                                        "business_hub" -> currentScreen = Screen.BusinessHub
                                        "solvers_hub" -> currentScreen = Screen.SolversHub
                                        "planetary_hub" -> currentScreen = Screen.PlanetaryHub
                                        "security_hub" -> currentScreen = Screen.SecurityHub
                                        "ml_hub" -> currentScreen = Screen.MLHub
                                        "visualization_hub" -> currentScreen = Screen.VisualizationHub
                                        "utilities_hub" -> currentScreen = Screen.UtilitiesHub
                                        // Individual Tools
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

                        // ===== HUB SCREENS (83 apps in 12 categories) =====
                        is Screen.PhysicsHub -> {
                            PhysicsHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.MathHub -> {
                            MathHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.CosmologyHub -> {
                            CosmologyHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.AviationHub -> {
                            AviationHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.TrafficHub -> {
                            TrafficHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.BusinessHub -> {
                            BusinessHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.SolversHub -> {
                            SolversHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.PlanetaryHub -> {
                            PlanetaryHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.SecurityHub -> {
                            SecurityHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.MLHub -> {
                            MLHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.VisualizationHub -> {
                            VisualizationHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.UtilitiesHub -> {
                            UtilitiesHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        // ===== SYMMETRY DASHBOARD =====
                        is Screen.SymmetryDashboard -> {
                            SymmetryDashboardScreen(
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        // ===== COMPOSITE APPS (21 skill-powered applications) =====
                        is Screen.CompositeAppsHub -> {
                            CompositeAppsHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = when (appId) {
                                        "universe_simulator" -> Screen.UniverseSimulator
                                        "smart_navigator" -> Screen.SmartNavigator
                                        "secure_business" -> Screen.SecureBusiness
                                        "pinn_lab" -> Screen.PINNLab
                                        "titan_colony" -> Screen.TitanColony
                                        "quantum_finance" -> Screen.QuantumFinance
                                        "traffic_brain" -> Screen.TrafficBrain
                                        "aerospace_optimizer" -> Screen.AerospaceOptimizer
                                        "crypto_observatory" -> Screen.CryptoObservatory
                                        "fair_division_ai" -> Screen.FairDivisionAI
                                        "cosmic_calculator" -> Screen.CosmicCalculator
                                        "mars_mission" -> Screen.MarsMission
                                        "golden_optimizer" -> Screen.GoldenOptimizer
                                        "emergency_response" -> Screen.EmergencyResponse
                                        "compliance_intel" -> Screen.ComplianceIntel
                                        "resonance_lab" -> Screen.ResonanceLab
                                        "fleet_manager" -> Screen.FleetManager
                                        "sat_ml_hybrid" -> Screen.SATMLHybrid
                                        "dark_sector" -> Screen.DarkSector
                                        "brahim_workspace" -> Screen.BrahimWorkspace
                                        "kelimutu_intel" -> Screen.KelimutuIntel
                                        else -> Screen.ToolDetail(appId)
                                    }
                                },
                                onBack = { currentScreen = Screen.Tools }
                            )
                        }

                        is Screen.UniverseSimulator -> {
                            UniverseSimulatorScreen(
                                onBack = { currentScreen = Screen.CompositeAppsHub }
                            )
                        }

                        is Screen.KelimutuIntel -> {
                            KelimutuIntelligenceScreen(
                                onBack = { currentScreen = Screen.CompositeAppsHub }
                            )
                        }

                        // Placeholder screens for remaining composite apps
                        is Screen.SmartNavigator,
                        is Screen.SecureBusiness,
                        is Screen.PINNLab,
                        is Screen.TitanColony,
                        is Screen.QuantumFinance,
                        is Screen.TrafficBrain,
                        is Screen.AerospaceOptimizer,
                        is Screen.CryptoObservatory,
                        is Screen.FairDivisionAI,
                        is Screen.CosmicCalculator,
                        is Screen.MarsMission,
                        is Screen.GoldenOptimizer,
                        is Screen.EmergencyResponse,
                        is Screen.ComplianceIntel,
                        is Screen.ResonanceLab,
                        is Screen.FleetManager,
                        is Screen.SATMLHybrid,
                        is Screen.DarkSector,
                        is Screen.BrahimWorkspace -> {
                            // Placeholder - show composite hub for now
                            CompositeAppsHubScreen(
                                onAppSelect = { appId ->
                                    currentScreen = Screen.ToolDetail(appId)
                                },
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

    /**
     * Navigate to app by ID - helper for discovery engine recommendations.
     */
    private fun navigateToApp(appId: String): Screen {
        return when {
            // Hub categories
            appId.startsWith("hub_") -> when (appId) {
                "hub_physics" -> Screen.PhysicsHub
                "hub_math" -> Screen.MathHub
                "hub_cosmology" -> Screen.CosmologyHub
                "hub_aviation" -> Screen.AviationHub
                "hub_traffic" -> Screen.TrafficHub
                "hub_business" -> Screen.BusinessHub
                "hub_solvers" -> Screen.SolversHub
                "hub_planetary" -> Screen.PlanetaryHub
                "hub_security" -> Screen.SecurityHub
                "hub_ml" -> Screen.MLHub
                "hub_visualization" -> Screen.VisualizationHub
                "hub_utilities" -> Screen.UtilitiesHub
                else -> Screen.Tools
            }

            // Composite apps
            appId == "universe_simulator" -> Screen.UniverseSimulator
            appId == "kelimutu_intel" -> Screen.KelimutuIntel
            appId == "smart_navigator" -> Screen.SmartNavigator
            appId == "secure_business" -> Screen.SecureBusiness
            appId == "pinn_lab" -> Screen.PINNLab
            appId == "titan_colony" -> Screen.TitanColony
            appId == "quantum_finance" -> Screen.QuantumFinance
            appId == "traffic_brain" -> Screen.TrafficBrain
            appId == "aerospace_optimizer" -> Screen.AerospaceOptimizer
            appId == "crypto_observatory" -> Screen.CryptoObservatory
            appId == "fair_division_ai" -> Screen.FairDivisionAI
            appId == "cosmic_calculator" -> Screen.CosmicCalculator
            appId == "mars_mission" -> Screen.MarsMission
            appId == "golden_optimizer" -> Screen.GoldenOptimizer
            appId == "emergency_response" -> Screen.EmergencyResponse
            appId == "compliance_intel" -> Screen.ComplianceIntel
            appId == "resonance_lab" -> Screen.ResonanceLab
            appId == "fleet_manager" -> Screen.FleetManager
            appId == "sat_ml_hybrid" -> Screen.SATMLHybrid
            appId == "dark_sector" -> Screen.DarkSector
            appId == "brahim_workspace" -> Screen.BrahimWorkspace

            // Direct tools
            appId == "physics_calculator" -> Screen.Physics
            appId == "brahim_sudoku" -> Screen.Sudoku
            appId == "solar_map" -> Screen.SolarMap
            appId == "consciousness_explorer" -> Screen.ConsciousnessExplorer
            appId == "quick_calculator" -> Screen.QuickCalculator

            // Default to tool detail
            else -> Screen.ToolDetail(appId)
        }
    }
}
