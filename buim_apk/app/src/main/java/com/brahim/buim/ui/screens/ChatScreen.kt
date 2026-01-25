/**
 * Chat Screen - Intelligent Conversation Interface
 * =================================================
 *
 * Primary chat interface for BUIM interactions with:
 * - Intent detection via DiscoveryEngine
 * - Emotional tone awareness
 * - Contextual app recommendations
 * - Warm, empathetic responses
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.brahim.buim.discovery.DiscoveryEngine
import com.brahim.buim.discovery.AppRecommendation
import com.brahim.buim.discovery.UserIntent
import com.brahim.buim.discovery.IntentCategory
import com.brahim.buim.discovery.EmotionalTone
import com.brahim.buim.safety.SafetyVerdict
import com.brahim.buim.ui.components.*
import com.brahim.buim.ui.theme.GoldenPrimary
import kotlinx.coroutines.launch

/**
 * Chat screen state with intent awareness.
 */
data class ChatScreenState(
    val messages: List<ChatMessage> = emptyList(),
    val isLoading: Boolean = false,
    val currentSafetyVerdict: SafetyVerdict = SafetyVerdict.SAFE,
    val currentResonance: Double = 0.0,
    val error: String? = null,
    // Intent awareness
    val currentIntent: UserIntent? = null,
    val recommendations: List<AppRecommendation> = emptyList(),
    val showRecommendations: Boolean = false
)

/**
 * Main chat screen composable with intent awareness.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    state: ChatScreenState,
    onSendMessage: (String) -> Unit,
    onNavigateToTools: () -> Unit,
    onNavigateToSettings: () -> Unit,
    onNavigateToApp: (String) -> Unit = {},
    onNavigateToHome: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    var inputText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()

    // Discovery engine for intent detection
    val discoveryEngine = remember { DiscoveryEngine() }
    var detectedIntent by remember { mutableStateOf<UserIntent?>(null) }
    var recommendations by remember { mutableStateOf<List<AppRecommendation>>(emptyList()) }
    var showIntentPanel by remember { mutableStateOf(false) }

    // Detect intent as user types
    LaunchedEffect(inputText) {
        if (inputText.length >= 3) {
            detectedIntent = discoveryEngine.feelIntent(inputText)
            detectedIntent?.let { intent ->
                recommendations = discoveryEngine.recommendApps(intent, limit = 3)
                showIntentPanel = recommendations.isNotEmpty()
            }
        } else {
            showIntentPanel = false
        }
    }

    // Auto-scroll to bottom when new messages arrive
    LaunchedEffect(state.messages.size) {
        if (state.messages.isNotEmpty()) {
            listState.animateScrollToItem(state.messages.size - 1)
        }
    }

    Scaffold(
        modifier = modifier,
        topBar = {
            Column {
                TopAppBar(
                    title = {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text("BUIM")
                            SafetyIndicator(
                                verdict = state.currentSafetyVerdict,
                                compact = true
                            )
                            // Intent awareness indicator
                            if (detectedIntent != null && showIntentPanel) {
                                IntentIndicator(intent = detectedIntent!!)
                            }
                        }
                    },
                    navigationIcon = {
                        IconButton(onClick = onNavigateToHome) {
                            Icon(Icons.Filled.Home, contentDescription = "Home")
                        }
                    },
                    actions = {
                        IconButton(onClick = onNavigateToTools) {
                            Icon(Icons.Filled.Build, contentDescription = "Tools")
                        }
                        IconButton(onClick = onNavigateToSettings) {
                            Icon(Icons.Filled.Settings, contentDescription = "Settings")
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.surface
                    )
                )

                // Intent-based recommendations panel
                AnimatedVisibility(
                    visible = showIntentPanel && recommendations.isNotEmpty(),
                    enter = fadeIn() + expandVertically(),
                    exit = fadeOut() + shrinkVertically()
                ) {
                    IntentRecommendationsPanel(
                        intent = detectedIntent!!,
                        recommendations = recommendations,
                        onAppClick = { rec ->
                            onNavigateToApp(rec.appId)
                        },
                        onDismiss = { showIntentPanel = false }
                    )
                }
            }
        },
        bottomBar = {
            ChatInputBar(
                text = inputText,
                onTextChange = { inputText = it },
                onSend = {
                    if (inputText.isNotBlank()) {
                        onSendMessage(inputText)
                        inputText = ""
                    }
                },
                isLoading = state.isLoading,
                resonance = state.currentResonance
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Error banner if present
            state.error?.let { error ->
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = MaterialTheme.colorScheme.errorContainer
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            Icons.Filled.Error,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onErrorContainer
                        )
                        Text(
                            text = error,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onErrorContainer
                        )
                    }
                }
            }

            // Messages list
            if (state.messages.isEmpty()) {
                // Empty state
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .weight(1f),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Icon(
                            Icons.Filled.AutoAwesome,
                            contentDescription = null,
                            modifier = Modifier.size(64.dp),
                            tint = GoldenPrimary.copy(alpha = 0.6f)
                        )
                        Text(
                            text = "Brahim Unified IAAS Manifold",
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "Ask anything to get started",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                        )
                    }
                }
            } else {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .weight(1f),
                    state = listState,
                    contentPadding = PaddingValues(vertical = 8.dp)
                ) {
                    items(state.messages, key = { it.id }) { message ->
                        MessageBubble(message = message)
                    }

                    if (state.isLoading) {
                        item {
                            TypingIndicator()
                        }
                    }
                }
            }
        }
    }
}

/**
 * Chat input bar with resonance indicator.
 */
@Composable
private fun ChatInputBar(
    text: String,
    onTextChange: (String) -> Unit,
    onSend: () -> Unit,
    isLoading: Boolean,
    resonance: Double,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier,
        tonalElevation = 3.dp
    ) {
        Column(
            modifier = Modifier.padding(8.dp)
        ) {
            // Resonance bar
            ResonanceBar(
                resonance = resonance,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp, vertical = 4.dp)
            )

            // Input row
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedTextField(
                    value = text,
                    onValueChange = onTextChange,
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Type a message...") },
                    shape = RoundedCornerShape(24.dp),
                    maxLines = 4,
                    enabled = !isLoading
                )

                FilledIconButton(
                    onClick = onSend,
                    enabled = text.isNotBlank() && !isLoading,
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = GoldenPrimary
                    )
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            strokeWidth = 2.dp
                        )
                    } else {
                        Icon(Icons.Filled.Send, contentDescription = "Send")
                    }
                }
            }
        }
    }
}

/**
 * Intent indicator chip showing detected user intent.
 */
@Composable
private fun IntentIndicator(intent: UserIntent) {
    val color = getIntentColor(intent.primary)
    val icon = getEmotionalIcon(intent.emotionalTone)

    Surface(
        color = color.copy(alpha = 0.15f),
        shape = CircleShape
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Icon(
                icon,
                contentDescription = null,
                modifier = Modifier.size(14.dp),
                tint = color
            )
            Text(
                text = intent.emotionalTone.name.lowercase(),
                style = MaterialTheme.typography.labelSmall,
                color = color
            )
        }
    }
}

/**
 * Panel showing contextual app recommendations based on detected intent.
 */
@Composable
private fun IntentRecommendationsPanel(
    intent: UserIntent,
    recommendations: List<AppRecommendation>,
    onAppClick: (AppRecommendation) -> Unit,
    onDismiss: () -> Unit
) {
    val color = getIntentColor(intent.primary)
    val discoveryEngine = remember { DiscoveryEngine() }
    val warmResponse = remember(intent, recommendations) {
        discoveryEngine.generateWarmResponse(intent, recommendations)
    }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = color.copy(alpha = 0.08f),
        tonalElevation = 1.dp
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            // Header with dismiss button
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Icon(
                        Icons.Filled.Psychology,
                        contentDescription = null,
                        tint = color,
                        modifier = Modifier.size(20.dp)
                    )
                    Text(
                        text = "I sense you need...",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Medium,
                        color = color
                    )
                }

                IconButton(
                    onClick = onDismiss,
                    modifier = Modifier.size(24.dp)
                ) {
                    Icon(
                        Icons.Filled.Close,
                        contentDescription = "Dismiss",
                        modifier = Modifier.size(16.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(modifier = Modifier.height(4.dp))

            // Warm response text
            Text(
                text = warmResponse.take(100) + if (warmResponse.length > 100) "..." else "",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f)
            )

            Spacer(modifier = Modifier.height(8.dp))

            // App recommendation chips
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(recommendations) { rec ->
                    RecommendationChip(
                        recommendation = rec,
                        color = color,
                        onClick = { onAppClick(rec) }
                    )
                }
            }
        }
    }
}

/**
 * Compact chip for a single app recommendation.
 */
@Composable
private fun RecommendationChip(
    recommendation: AppRecommendation,
    color: Color,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier.clickable(onClick = onClick),
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(16.dp),
        shadowElevation = 1.dp
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            // Match score indicator
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .clip(CircleShape)
                    .background(color.copy(alpha = 0.2f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "${(recommendation.matchScore * 100).toInt()}",
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold,
                    color = color
                )
            }

            Column {
                Text(
                    text = recommendation.appName,
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = recommendation.category,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Icon(
                Icons.Filled.ChevronRight,
                contentDescription = null,
                modifier = Modifier.size(16.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Get color based on intent category.
 */
private fun getIntentColor(category: IntentCategory): Color {
    return when (category) {
        IntentCategory.PHYSICS -> Color(0xFF2196F3)
        IntentCategory.MATHEMATICS -> Color(0xFF795548)
        IntentCategory.ML_AI -> Color(0xFF9C27B0)
        IntentCategory.SECURITY -> Color(0xFFE91E63)
        IntentCategory.BUSINESS -> Color(0xFF4CAF50)
        IntentCategory.AVIATION -> Color(0xFF00BCD4)
        IntentCategory.TRAFFIC -> Color(0xFFFF9800)
        IntentCategory.COSMOLOGY -> Color(0xFF673AB7)
        IntentCategory.VISUALIZATION -> Color(0xFF3F51B5)
        IntentCategory.UTILITIES -> Color(0xFF607D8B)
        IntentCategory.PLANETARY -> Color(0xFFFF5722)
        IntentCategory.GENERAL -> Color(0xFF9E9E9E)
    }
}

/**
 * Get icon based on emotional tone.
 */
@Composable
private fun getEmotionalIcon(tone: EmotionalTone) = when (tone) {
    EmotionalTone.CURIOUS -> Icons.Filled.Psychology
    EmotionalTone.URGENT -> Icons.Filled.Speed
    EmotionalTone.FRUSTRATED -> Icons.Filled.SentimentDissatisfied
    EmotionalTone.EXCITED -> Icons.Filled.Celebration
    EmotionalTone.CONFUSED -> Icons.Filled.Help
    EmotionalTone.ANALYTICAL -> Icons.Filled.Analytics
    EmotionalTone.CREATIVE -> Icons.Filled.Palette
    EmotionalTone.NEUTRAL -> Icons.Filled.EmojiEmotions
}
