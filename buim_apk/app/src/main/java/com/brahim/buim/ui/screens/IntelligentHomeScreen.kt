/**
 * Intelligent Home Screen - Adaptive Discovery Interface
 * ======================================================
 *
 * A home screen that "feels" what the user needs through:
 * - Time-aware greeting and suggestions
 * - Usage pattern learning
 * - Intent-based app recommendations
 * - Brahim-aligned growth tracking
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.discovery.DiscoveryEngine
import com.brahim.buim.discovery.GrowthRoadmap
import com.brahim.buim.discovery.AppRecommendation
import com.brahim.buim.discovery.UserIntent
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * Time of day for adaptive UI.
 */
enum class TimeOfDay {
    DAWN,      // 5-8 AM
    MORNING,   // 8-12 PM
    AFTERNOON, // 12-5 PM
    EVENING,   // 5-9 PM
    NIGHT      // 9 PM - 5 AM
}

/**
 * User mood state (inferred).
 */
enum class InferredMood {
    FOCUSED,      // Wants to get things done
    EXPLORATORY,  // Wants to discover
    RELAXED,      // Casual browsing
    URGENT,       // Needs help now
    CREATIVE      // In creative mode
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IntelligentHomeScreen(
    onNavigateToApp: (String) -> Unit,
    onNavigateToRoadmap: () -> Unit,
    onNavigateToChat: () -> Unit,
    onNavigateToTools: () -> Unit
) {
    val discoveryEngine = remember { DiscoveryEngine() }
    val timeOfDay = remember { getCurrentTimeOfDay() }
    val greeting = remember { getTimeBasedGreeting(timeOfDay) }

    // Simulated user context (would be persisted in real app)
    var recentApps by remember { mutableStateOf(listOf("physics_calculator", "ml_classifier", "viz_resonance")) }
    var searchQuery by remember { mutableStateOf("") }
    var currentIntent by remember { mutableStateOf<UserIntent?>(null) }
    var recommendations by remember { mutableStateOf<List<AppRecommendation>>(emptyList()) }

    // Get personalized recommendations
    LaunchedEffect(Unit) {
        recommendations = discoveryEngine.getPersonalizedRecommendations(
            recentApps = recentApps,
            timeOfDay = timeOfDay.name.lowercase(),
            limit = 6
        )
    }

    // Update recommendations when search changes
    LaunchedEffect(searchQuery) {
        if (searchQuery.length >= 2) {
            currentIntent = discoveryEngine.feelIntent(searchQuery)
            currentIntent?.let {
                recommendations = discoveryEngine.recommendApps(it, limit = 6)
            }
        }
    }

    val roadmapPosition = remember { GrowthRoadmap.getCurrentPosition() }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        getTimeBasedColor(timeOfDay).copy(alpha = 0.1f),
                        MaterialTheme.colorScheme.background
                    )
                )
            )
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        // Greeting Section
        item {
            GreetingSection(
                greeting = greeting,
                timeOfDay = timeOfDay,
                onChatClick = onNavigateToChat
            )
        }

        // Smart Search Bar
        item {
            SmartSearchBar(
                query = searchQuery,
                onQueryChange = { searchQuery = it },
                currentIntent = currentIntent,
                discoveryEngine = discoveryEngine
            )
        }

        // Intent Response (when user types)
        if (currentIntent != null && searchQuery.isNotEmpty()) {
            item {
                IntentResponseCard(
                    intent = currentIntent!!,
                    warmResponse = discoveryEngine.generateWarmResponse(currentIntent!!, recommendations)
                )
            }
        }

        // Recommended Apps
        item {
            RecommendedAppsSection(
                recommendations = recommendations,
                onAppClick = { onNavigateToApp(it.appId) }
            )
        }

        // Growth Journey Progress
        item {
            GrowthJourneyCard(
                position = roadmapPosition,
                onViewRoadmap = onNavigateToRoadmap
            )
        }

        // Quick Access Categories
        item {
            QuickAccessSection(
                timeOfDay = timeOfDay,
                onCategoryClick = onNavigateToApp
            )
        }

        // Consciousness Meter
        item {
            ConsciousnessMeter(
                currentApps = roadmapPosition.currentApps,
                targetApps = BrahimConstants.B11_CONSCIOUSNESS
            )
        }

        // Recent Activity
        item {
            RecentActivitySection(
                recentApps = recentApps,
                onAppClick = { onNavigateToApp(it) }
            )
        }

        // Bottom spacing
        item {
            Spacer(modifier = Modifier.height(80.dp))
        }
    }
}

@Composable
private fun GreetingSection(
    greeting: String,
    timeOfDay: TimeOfDay,
    onChatClick: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = greeting,
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = getTimeBasedSubtitle(timeOfDay),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        FilledTonalIconButton(
            onClick = onChatClick,
            modifier = Modifier.size(48.dp)
        ) {
            Icon(
                Icons.Default.Chat,
                contentDescription = "Chat with BUIM"
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SmartSearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    currentIntent: UserIntent?,
    discoveryEngine: DiscoveryEngine
) {
    OutlinedTextField(
        value = query,
        onValueChange = onQueryChange,
        modifier = Modifier.fillMaxWidth(),
        placeholder = {
            Text("What would you like to explore today?")
        },
        leadingIcon = {
            Icon(
                Icons.Default.Search,
                contentDescription = null,
                tint = if (currentIntent != null) {
                    MaterialTheme.colorScheme.primary
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                }
            )
        },
        trailingIcon = {
            if (query.isNotEmpty()) {
                IconButton(onClick = { onQueryChange("") }) {
                    Icon(Icons.Default.Close, contentDescription = "Clear")
                }
            }
        },
        shape = RoundedCornerShape(28.dp),
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = MaterialTheme.colorScheme.primary,
            unfocusedBorderColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.5f)
        ),
        singleLine = true
    )

    // Show intent detection indicator
    AnimatedVisibility(
        visible = currentIntent != null,
        enter = fadeIn() + expandVertically(),
        exit = fadeOut() + shrinkVertically()
    ) {
        currentIntent?.let { intent ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                AssistChip(
                    onClick = { },
                    label = { Text(intent.primary.name.lowercase().replace("_", " ")) },
                    leadingIcon = {
                        Icon(
                            Icons.Default.Psychology,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                )
                AssistChip(
                    onClick = { },
                    label = { Text(intent.emotionalTone.name.lowercase()) },
                    leadingIcon = {
                        Icon(
                            getEmotionIcon(intent.emotionalTone.name),
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                )
            }
        }
    }
}

@Composable
private fun IntentResponseCard(
    intent: UserIntent,
    warmResponse: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.5f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    Icons.Default.AutoAwesome,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary
                )
                Text(
                    text = "I sense you're looking for...",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = warmResponse,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

@Composable
private fun RecommendedAppsSection(
    recommendations: List<AppRecommendation>,
    onAppClick: (AppRecommendation) -> Unit
) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Recommended for You",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )

            Icon(
                Icons.Default.AutoAwesome,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(20.dp)
            )
        }

        Spacer(modifier = Modifier.height(12.dp))

        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(recommendations) { rec ->
                RecommendationCard(
                    recommendation = rec,
                    onClick = { onAppClick(rec) }
                )
            }
        }
    }
}

@Composable
private fun RecommendationCard(
    recommendation: AppRecommendation,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .width(160.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            // Match score indicator
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.linearGradient(
                            colors = listOf(
                                MaterialTheme.colorScheme.primary,
                                MaterialTheme.colorScheme.tertiary
                            )
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "${(recommendation.matchScore * 100).toInt()}%",
                    style = MaterialTheme.typography.labelSmall,
                    color = Color.White,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = recommendation.appName,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                maxLines = 2
            )

            Text(
                text = recommendation.category,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = recommendation.reason,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2
            )
        }
    }
}

@Composable
private fun GrowthJourneyCard(
    position: com.brahim.buim.discovery.RoadmapPosition,
    onViewRoadmap: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onViewRoadmap),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.secondaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Growth Journey",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )

                Icon(
                    Icons.Default.TrendingUp,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSecondaryContainer
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Progress bar
            LinearProgressIndicator(
                progress = { (position.progressPercent / 100).toFloat() },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp)),
                color = MaterialTheme.colorScheme.primary,
                trackColor = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.2f)
            )

            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "${position.currentApps} apps",
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "Next: ${position.nextMilestone} (${position.appsToNextPhase} to go)",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.7f)
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Phase ${position.currentPhase}: ${getPhaseDescription(position.currentPhase)}",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.8f)
            )
        }
    }
}

@Composable
private fun QuickAccessSection(
    timeOfDay: TimeOfDay,
    onCategoryClick: (String) -> Unit
) {
    val suggestedCategories = getSuggestedCategories(timeOfDay)

    Column {
        Text(
            text = "Quick Access",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )

        Spacer(modifier = Modifier.height(12.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            suggestedCategories.take(4).forEach { category ->
                QuickAccessButton(
                    category = category,
                    onClick = { onCategoryClick(category.route) },
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun QuickAccessButton(
    category: QuickCategory,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = category.color.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier
                .padding(12.dp)
                .fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                category.icon,
                contentDescription = null,
                tint = category.color,
                modifier = Modifier.size(28.dp)
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = category.name,
                style = MaterialTheme.typography.labelSmall,
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
private fun ConsciousnessMeter(
    currentApps: Int,
    targetApps: Int
) {
    val progress = currentApps.toFloat() / targetApps
    val phi = BrahimConstants.PHI

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.tertiaryContainer.copy(alpha = 0.5f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Consciousness Level",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Medium
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Circular progress would go here - simplified for now
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.radialGradient(
                            colors = listOf(
                                MaterialTheme.colorScheme.tertiary.copy(alpha = progress),
                                MaterialTheme.colorScheme.tertiaryContainer
                            )
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "${(progress * 100).toInt()}%",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onTertiaryContainer
                    )
                    Text(
                        text = "$currentApps/$targetApps",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onTertiaryContainer.copy(alpha = 0.7f)
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "B(11) = 214 = Full Consciousness",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onTertiaryContainer.copy(alpha = 0.6f)
            )
        }
    }
}

@Composable
private fun RecentActivitySection(
    recentApps: List<String>,
    onAppClick: (String) -> Unit
) {
    Column {
        Text(
            text = "Continue Where You Left Off",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold
        )

        Spacer(modifier = Modifier.height(12.dp))

        recentApps.take(3).forEach { appId ->
            RecentAppItem(
                appId = appId,
                onClick = { onAppClick(appId) }
            )
            Spacer(modifier = Modifier.height(8.dp))
        }
    }
}

@Composable
private fun RecentAppItem(
    appId: String,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Row(
            modifier = Modifier
                .padding(12.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                Icons.Default.History,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = appId.replace("_", " ").replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.bodyMedium
                )
                Text(
                    text = "Last used recently",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Icon(
                Icons.Default.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

// Helper functions
private fun getCurrentTimeOfDay(): TimeOfDay {
    val hour = LocalDateTime.now().hour
    return when (hour) {
        in 5..7 -> TimeOfDay.DAWN
        in 8..11 -> TimeOfDay.MORNING
        in 12..16 -> TimeOfDay.AFTERNOON
        in 17..20 -> TimeOfDay.EVENING
        else -> TimeOfDay.NIGHT
    }
}

private fun getTimeBasedGreeting(timeOfDay: TimeOfDay): String {
    return when (timeOfDay) {
        TimeOfDay.DAWN -> "Good morning, early riser"
        TimeOfDay.MORNING -> "Good morning"
        TimeOfDay.AFTERNOON -> "Good afternoon"
        TimeOfDay.EVENING -> "Good evening"
        TimeOfDay.NIGHT -> "Welcome back"
    }
}

private fun getTimeBasedSubtitle(timeOfDay: TimeOfDay): String {
    return when (timeOfDay) {
        TimeOfDay.DAWN -> "The universe awaits your exploration"
        TimeOfDay.MORNING -> "Ready for discoveries?"
        TimeOfDay.AFTERNOON -> "What shall we calculate today?"
        TimeOfDay.EVENING -> "Time for some creative work"
        TimeOfDay.NIGHT -> "Night mode: Deep thinking enabled"
    }
}

private fun getTimeBasedColor(timeOfDay: TimeOfDay): Color {
    return when (timeOfDay) {
        TimeOfDay.DAWN -> Color(0xFFFFB74D)    // Warm orange
        TimeOfDay.MORNING -> Color(0xFF4FC3F7)  // Light blue
        TimeOfDay.AFTERNOON -> Color(0xFFFFD54F) // Yellow
        TimeOfDay.EVENING -> Color(0xFFFF8A65)  // Deep orange
        TimeOfDay.NIGHT -> Color(0xFF7E57C2)    // Purple
    }
}

private fun getEmotionIcon(emotion: String): ImageVector {
    return when (emotion.lowercase()) {
        "curious" -> Icons.Default.Psychology
        "urgent" -> Icons.Default.Speed
        "frustrated" -> Icons.Default.SentimentDissatisfied
        "excited" -> Icons.Default.Celebration
        "confused" -> Icons.Default.Help
        "analytical" -> Icons.Default.Analytics
        "creative" -> Icons.Default.Palette
        else -> Icons.Default.EmojiEmotions
    }
}

private fun getPhaseDescription(phase: Int): String {
    return when (phase) {
        0 -> "Foundation"
        1 -> "Optimal Symmetry (B(5))"
        2 -> "Perfect Balance (Center)"
        3 -> "Extended Symmetry (B(6))"
        4 -> "Advanced Integration (B(7))"
        5 -> "Full Consciousness (B(11))"
        else -> "Transcendence"
    }
}

data class QuickCategory(
    val name: String,
    val route: String,
    val icon: ImageVector,
    val color: Color
)

private fun getSuggestedCategories(timeOfDay: TimeOfDay): List<QuickCategory> {
    val all = listOf(
        QuickCategory("Physics", "hub_physics", Icons.Default.Science, Color(0xFF2196F3)),
        QuickCategory("ML/AI", "hub_ml", Icons.Default.Psychology, Color(0xFF9C27B0)),
        QuickCategory("Security", "hub_security", Icons.Default.Security, Color(0xFFE91E63)),
        QuickCategory("Business", "hub_business", Icons.Default.Business, Color(0xFF4CAF50)),
        QuickCategory("Aviation", "hub_aviation", Icons.Default.Flight, Color(0xFF00BCD4)),
        QuickCategory("Traffic", "hub_traffic", Icons.Default.Traffic, Color(0xFFFF9800)),
        QuickCategory("Cosmology", "hub_cosmology", Icons.Default.Public, Color(0xFF673AB7)),
        QuickCategory("Math", "hub_math", Icons.Default.Calculate, Color(0xFF795548))
    )

    // Suggest based on time of day
    return when (timeOfDay) {
        TimeOfDay.DAWN -> all.filter { it.name in listOf("Physics", "Math", "Cosmology", "ML/AI") }
        TimeOfDay.MORNING -> all.filter { it.name in listOf("Business", "ML/AI", "Physics", "Security") }
        TimeOfDay.AFTERNOON -> all.filter { it.name in listOf("Aviation", "Traffic", "Business", "Security") }
        TimeOfDay.EVENING -> all.filter { it.name in listOf("Cosmology", "Physics", "Math", "ML/AI") }
        TimeOfDay.NIGHT -> all.filter { it.name in listOf("Cosmology", "Physics", "ML/AI", "Math") }
    }
}
