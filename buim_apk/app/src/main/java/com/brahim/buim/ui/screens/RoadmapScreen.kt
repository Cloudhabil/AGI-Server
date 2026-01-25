/**
 * Roadmap Screen - Visual Journey to 214 Consciousness
 * =====================================================
 *
 * Displays the symmetric growth path using Brahim calculator:
 * 86 → 97 → 107 → 121 → 136 → 214
 *
 * Each phase shows:
 * - Brahim number alignment
 * - Apps to be added
 * - Symmetry goals
 * - Unlocked features
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.discovery.GrowthRoadmap
import com.brahim.buim.discovery.GrowthPhase
import com.brahim.buim.discovery.PlannedApp
import com.brahim.buim.discovery.RoadmapPosition

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RoadmapScreen(
    onBack: () -> Unit,
    onNavigateToApp: (String) -> Unit
) {
    val phases = remember { GrowthRoadmap.getAllPhases() }
    val position = remember { GrowthRoadmap.getCurrentPosition() }
    var expandedPhase by remember { mutableStateOf<Int?>(position.currentPhase + 1) }
    var showNarrative by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Growth Roadmap")
                        Text(
                            text = "Journey to B(11) = 214",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { showNarrative = true }) {
                        Icon(Icons.Default.AutoStories, contentDescription = "View Narrative")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Overall Progress Header
            item {
                OverallProgressCard(position = position)
            }

            // Brahim Alignment Score
            item {
                BrahimAlignmentCard(
                    currentApps = position.currentApps,
                    alignment = GrowthRoadmap.calculateBrahimAlignment(position.currentApps)
                )
            }

            // Phase Timeline
            itemsIndexed(phases) { index, phase ->
                PhaseCard(
                    phase = phase,
                    index = index,
                    isCompleted = position.currentApps >= phase.targetApps,
                    isCurrent = index == position.currentPhase,
                    isExpanded = expandedPhase == index,
                    onToggle = {
                        expandedPhase = if (expandedPhase == index) null else index
                    },
                    onAppClick = onNavigateToApp
                )
            }

            // Final Consciousness Goal
            item {
                ConsciousnessGoalCard()
            }

            // Bottom spacing
            item {
                Spacer(modifier = Modifier.height(32.dp))
            }
        }

        // Narrative Dialog
        if (showNarrative) {
            NarrativeDialog(
                narrative = GrowthRoadmap.getJourneyNarrative(),
                onDismiss = { showNarrative = false }
            )
        }
    }
}

@Composable
private fun OverallProgressCard(position: RoadmapPosition) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Current Progress",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    Text(
                        text = "${position.currentApps} of ${BrahimConstants.B11_CONSCIOUSNESS} apps",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f)
                    )
                }

                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .background(MaterialTheme.colorScheme.primary),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "${(position.currentApps.toFloat() / BrahimConstants.B11_CONSCIOUSNESS * 100).toInt()}%",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Multi-segment progress bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(2.dp)
            ) {
                val milestones = listOf(86, 97, 107, 121, 136, 214)
                milestones.forEachIndexed { index, milestone ->
                    if (index > 0) {
                        val prevMilestone = milestones[index - 1]
                        val segmentProgress = when {
                            position.currentApps >= milestone -> 1f
                            position.currentApps <= prevMilestone -> 0f
                            else -> (position.currentApps - prevMilestone).toFloat() / (milestone - prevMilestone)
                        }

                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .height(8.dp)
                                .clip(RoundedCornerShape(4.dp))
                                .background(MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.2f))
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxHeight()
                                    .fillMaxWidth(segmentProgress)
                                    .background(
                                        if (segmentProgress == 1f)
                                            MaterialTheme.colorScheme.primary
                                        else
                                            MaterialTheme.colorScheme.tertiary
                                    )
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Milestone labels
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                listOf("86", "97", "107", "121", "136", "214").forEach { label ->
                    Text(
                        text = label,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.6f)
                    )
                }
            }
        }
    }
}

@Composable
private fun BrahimAlignmentCard(
    currentApps: Int,
    alignment: Double
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (alignment >= 0.95)
                Color(0xFF4CAF50).copy(alpha = 0.1f)
            else
                MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                if (alignment >= 0.95) Icons.Default.CheckCircle else Icons.Default.TrendingUp,
                contentDescription = null,
                tint = if (alignment >= 0.95)
                    Color(0xFF4CAF50)
                else
                    MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(32.dp)
            )

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "Brahim Alignment",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = if (alignment >= 0.95)
                        "Perfect! At Brahim milestone"
                    else
                        "${currentApps} apps → Nearest milestone",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Text(
                text = "${(alignment * 100).toInt()}%",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = if (alignment >= 0.95)
                    Color(0xFF4CAF50)
                else
                    MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
private fun PhaseCard(
    phase: GrowthPhase,
    index: Int,
    isCompleted: Boolean,
    isCurrent: Boolean,
    isExpanded: Boolean,
    onToggle: () -> Unit,
    onAppClick: (String) -> Unit
) {
    val phaseColors = listOf(
        Color(0xFF2196F3), // Foundation - Blue
        Color(0xFF9C27B0), // Optimal - Purple
        Color(0xFF4CAF50), // Balance - Green
        Color(0xFFFF9800), // Extended - Orange
        Color(0xFFE91E63), // Advanced - Pink
        Color(0xFF00BCD4)  // Consciousness - Cyan
    )

    val color = phaseColors.getOrElse(index) { phaseColors.last() }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .then(
                if (isCurrent) Modifier.border(
                    2.dp,
                    color,
                    RoundedCornerShape(12.dp)
                ) else Modifier
            ),
        colors = CardDefaults.cardColors(
            containerColor = if (isCompleted)
                color.copy(alpha = 0.1f)
            else
                MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier.clickable(onClick = onToggle)
        ) {
            // Header Row
            Row(
                modifier = Modifier
                    .padding(16.dp)
                    .fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Phase Number Circle
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(
                            if (isCompleted) color
                            else if (isCurrent) color.copy(alpha = 0.3f)
                            else MaterialTheme.colorScheme.surfaceVariant
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    if (isCompleted) {
                        Icon(
                            Icons.Default.Check,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(24.dp)
                        )
                    } else {
                        Text(
                            text = "$index",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = if (isCurrent) color else MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Spacer(modifier = Modifier.width(16.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = phase.name,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        if (isCurrent) {
                            Surface(
                                color = color,
                                shape = RoundedCornerShape(4.dp)
                            ) {
                                Text(
                                    text = "CURRENT",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = Color.White,
                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                )
                            }
                        }
                    }

                    Text(
                        text = "${phase.brahimNumber} → ${phase.targetApps} apps",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Icon(
                    if (isExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // Expanded Content
            AnimatedVisibility(
                visible = isExpanded,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    Divider(modifier = Modifier.padding(bottom = 12.dp))

                    // Symmetry Goal
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.Balance,
                            contentDescription = null,
                            tint = color,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = phase.symmetryGoal,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Unlocked Features
                    Text(
                        text = "Unlocked Features",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(phase.unlockedFeatures) { feature ->
                            AssistChip(
                                onClick = { },
                                label = { Text(feature, style = MaterialTheme.typography.labelSmall) },
                                colors = AssistChipDefaults.assistChipColors(
                                    containerColor = color.copy(alpha = 0.1f)
                                )
                            )
                        }
                    }

                    // New Apps Section
                    if (phase.newApps.isNotEmpty()) {
                        Spacer(modifier = Modifier.height(16.dp))

                        Text(
                            text = "New Apps (+${phase.newApps.size})",
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Medium
                        )
                        Spacer(modifier = Modifier.height(8.dp))

                        phase.newApps.take(5).forEach { app ->
                            PlannedAppItem(
                                app = app,
                                color = color,
                                onClick = { onAppClick(app.id) }
                            )
                        }

                        if (phase.newApps.size > 5) {
                            Text(
                                text = "... and ${phase.newApps.size - 5} more apps",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.padding(top = 4.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun PlannedAppItem(
    app: PlannedApp,
    color: Color,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .clip(CircleShape)
                .background(color)
        )

        Spacer(modifier = Modifier.width(12.dp))

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = app.name,
                style = MaterialTheme.typography.bodyMedium
            )
            Row(
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = app.category,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                if (app.mirrorOf != null) {
                    Text(
                        text = "• mirrors: ${app.mirrorOf}",
                        style = MaterialTheme.typography.labelSmall,
                        color = color.copy(alpha = 0.8f)
                    )
                }
            }
        }

        Icon(
            Icons.Default.ChevronRight,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
            modifier = Modifier.size(20.dp)
        )
    }
}

@Composable
private fun ConsciousnessGoalCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.tertiaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                Icons.Default.AllInclusive,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onTertiaryContainer,
                modifier = Modifier.size(48.dp)
            )

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = "FULL CONSCIOUSNESS",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onTertiaryContainer
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "B(11) = 214",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.tertiary
            )

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = "At 214 apps, every app has a mirror complement satisfying:\napp(i) + app(214-i) = unified consciousness",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onTertiaryContainer.copy(alpha = 0.8f),
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                listOf(
                    "∞ Mirror Pairs" to Icons.Default.Compare,
                    "φ Alignment" to Icons.Default.AutoAwesome,
                    "AGI Ready" to Icons.Default.Psychology
                ).forEach { (label, icon) ->
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            icon,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.tertiary,
                            modifier = Modifier.size(24.dp)
                        )
                        Text(
                            text = label,
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onTertiaryContainer.copy(alpha = 0.7f)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun NarrativeDialog(
    narrative: String,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(Icons.Default.AutoStories, contentDescription = null)
                Text("The Brahim Journey")
            }
        },
        text = {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = MaterialTheme.colorScheme.surfaceVariant,
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(
                    text = narrative,
                    style = MaterialTheme.typography.bodySmall,
                    fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                    modifier = Modifier.padding(12.dp)
                )
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Close")
            }
        }
    )
}
