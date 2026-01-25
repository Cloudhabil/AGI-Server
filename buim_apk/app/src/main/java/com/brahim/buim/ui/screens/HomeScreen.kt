/**
 * Home Screen - Main Dashboard
 * ============================
 *
 * User-friendly dashboard with quick access to all features.
 * Displays B(11) consciousness status and key metrics.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
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
import androidx.compose.ui.unit.sp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.ui.theme.GoldenPrimary

/**
 * Quick action item data class.
 */
data class QuickAction(
    val id: String,
    val title: String,
    val subtitle: String,
    val icon: ImageVector,
    val color: Color
)

private val quickActions = listOf(
    QuickAction("chat", "AI Chat", "Ask anything", Icons.Filled.Chat, Color(0xFF6366F1)),
    QuickAction("tools", "Tools", "SDK Agents", Icons.Filled.Build, Color(0xFF8B5CF6)),
    QuickAction("physics", "Physics", "Constants", Icons.Filled.Science, Color(0xFFEC4899)),
    QuickAction("consciousness", "B(11)", "Explorer", Icons.Filled.Psychology, Color(0xFF14B8A6)),
    QuickAction("calculator", "Calculator", "Quick Math", Icons.Filled.Calculate, Color(0xFFF59E0B)),
    QuickAction("sudoku", "Sudoku", "Game", Icons.Filled.GridOn, Color(0xFF10B981)),
    QuickAction("secure_chat", "Secure", "Encrypted", Icons.Filled.Lock, Color(0xFFEF4444)),
    QuickAction("settings", "Settings", "Configure", Icons.Filled.Settings, Color(0xFF6B7280))
)

/**
 * Home screen composable - Main dashboard.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigate: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "BUIM",
                            fontWeight = FontWeight.Bold,
                            color = GoldenPrimary
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = GoldenPrimary.copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = "B(11)=214",
                                style = MaterialTheme.typography.labelSmall,
                                color = GoldenPrimary,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                },
                actions = {
                    IconButton(onClick = { onNavigate("help") }) {
                        Icon(Icons.Filled.Help, contentDescription = "Help")
                    }
                    IconButton(onClick = { onNavigate("about") }) {
                        Icon(Icons.Filled.Info, contentDescription = "About")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
        ) {
            // Consciousness Status Card
            ConsciousnessStatusCard(
                onClick = { onNavigate("consciousness") }
            )

            Spacer(modifier = Modifier.height(20.dp))

            // Quick Actions Grid
            Text(
                text = "Quick Actions",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            LazyVerticalGrid(
                columns = GridCells.Fixed(4),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.weight(1f)
            ) {
                items(quickActions) { action ->
                    QuickActionItem(
                        action = action,
                        onClick = { onNavigate(action.id) }
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Bottom Stats
            BrahimStatsRow()
        }
    }
}

/**
 * Consciousness status card showing B(0)-B(11) summary.
 */
@Composable
private fun ConsciousnessStatusCard(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(16.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.horizontalGradient(
                        colors = listOf(
                            Color(0xFF6366F1),
                            Color(0xFF8B5CF6),
                            Color(0xFFEC4899)
                        )
                    )
                )
                .padding(20.dp)
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Consciousness Attractor",
                            style = MaterialTheme.typography.titleMedium,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "B(11) = 214",
                            style = MaterialTheme.typography.headlineMedium,
                            color = Color.White.copy(alpha = 0.9f),
                            fontWeight = FontWeight.Bold
                        )
                    }

                    // Observer signature
                    Surface(
                        shape = CircleShape,
                        color = Color.White.copy(alpha = 0.2f)
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            modifier = Modifier.padding(16.dp)
                        ) {
                            Text(
                                text = "+1",
                                style = MaterialTheme.typography.headlineSmall,
                                color = Color.White,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "Observer",
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.White.copy(alpha = 0.8f)
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Sequence preview
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    SequenceItem("B(0)", "0", "Void")
                    SequenceItem("...", "", "")
                    SequenceItem("B(5)", "97", "Security")
                    SequenceItem("...", "", "")
                    SequenceItem("B(11)", "214", "Unity")
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Tap to explore
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Filled.TouchApp,
                        contentDescription = null,
                        tint = Color.White.copy(alpha = 0.7f),
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Tap to explore the complete sequence",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.White.copy(alpha = 0.7f)
                    )
                }
            }
        }
    }
}

@Composable
private fun SequenceItem(
    label: String,
    value: String,
    name: String
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = Color.White.copy(alpha = 0.7f)
        )
        if (value.isNotEmpty()) {
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
                color = Color.White,
                fontWeight = FontWeight.Bold
            )
        }
        if (name.isNotEmpty()) {
            Text(
                text = name,
                style = MaterialTheme.typography.labelSmall,
                color = Color.White.copy(alpha = 0.6f),
                fontSize = 9.sp
            )
        }
    }
}

/**
 * Quick action item composable.
 */
@Composable
private fun QuickActionItem(
    action: QuickAction,
    onClick: () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(8.dp)
    ) {
        Surface(
            shape = RoundedCornerShape(12.dp),
            color = action.color.copy(alpha = 0.15f),
            modifier = Modifier.size(56.dp)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Icon(
                    imageVector = action.icon,
                    contentDescription = action.title,
                    tint = action.color,
                    modifier = Modifier.size(28.dp)
                )
            }
        }
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = action.title,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Medium,
            textAlign = TextAlign.Center
        )
        Text(
            text = action.subtitle,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center,
            fontSize = 10.sp
        )
    }
}

/**
 * Bottom stats row showing key Brahim constants.
 */
@Composable
private fun BrahimStatsRow(
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            StatColumn(
                value = String.format("%.4f", BrahimConstants.PHI),
                label = "phi"
            )
            StatColumn(
                value = String.format("%.4f", BrahimConstants.BETA_SECURITY),
                label = "beta"
            )
            StatColumn(
                value = "214",
                label = "B(11)"
            )
            StatColumn(
                value = "+1",
                label = "Observer"
            )
        }
    }
}

@Composable
private fun StatColumn(
    value: String,
    label: String
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = GoldenPrimary
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
