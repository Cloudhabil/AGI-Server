/**
 * Visualization Hub Screen
 * ========================
 *
 * Hub for visualization and analysis tools.
 * Resonance monitor, phase portraits, sequence plots, symmetry.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens.hubs

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

data class VisualizationApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color,
    val features: List<String>
)

private val visualizationApps = listOf(
    VisualizationApp(
        "resonance", "Resonance Monitor", "V-NAND 0.0219 resonance tracking",
        Icons.Filled.GraphicEq, Color(0xFF8B5CF6),
        listOf("Real-time resonance", "Gate threshold", "4096 voxel grid")
    ),
    VisualizationApp(
        "phase", "Phase Portrait", "FitzHugh-Nagumo dynamics visualization",
        Icons.Filled.BubbleChart, Color(0xFFEC4899),
        listOf("κ-D phase space", "Limit cycles", "Bifurcation diagrams")
    ),
    VisualizationApp(
        "sequence", "Sequence Plot", "Brahim sequence visualization",
        Icons.Filled.ShowChart, Color(0xFF14B8A6),
        listOf("B(0) to B(11)", "Mirror pairs", "214 consciousness")
    ),
    VisualizationApp(
        "symmetry", "Symmetry Viewer", "SO(10) symmetry representation",
        Icons.Filled.FlipCameraAndroid, Color(0xFFF59E0B),
        listOf("Group structure", "Breaking patterns", "45 representation")
    )
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VisualizationHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Visualization", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Filled.ArrowBack, "Back")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(
                                Brush.horizontalGradient(
                                    listOf(Color(0xFF8B5CF6), Color(0xFFEC4899))
                                )
                            )
                            .padding(20.dp)
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.Insights, null, tint = Color.White)
                                Spacer(Modifier.width(8.dp))
                                Text("Visualization Suite", style = MaterialTheme.typography.titleLarge,
                                    color = Color.White, fontWeight = FontWeight.Bold)
                            }
                            Spacer(Modifier.height(8.dp))
                            Text("Interactive plots and phase space exploration",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                        }
                    }
                }
            }

            items(visualizationApps) { app ->
                var expanded by remember { mutableStateOf(false) }

                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { expanded = !expanded },
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = app.color.copy(alpha = 0.15f),
                                modifier = Modifier.size(56.dp)
                            ) {
                                Box(contentAlignment = Alignment.Center) {
                                    Icon(app.icon, null, tint = app.color,
                                        modifier = Modifier.size(28.dp))
                                }
                            }
                            Spacer(Modifier.width(16.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(app.name, style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.SemiBold)
                                Text(app.description, style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                            Icon(
                                if (expanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                                "Expand", tint = app.color
                            )
                        }

                        if (expanded) {
                            Spacer(Modifier.height(12.dp))
                            Divider()
                            Spacer(Modifier.height(12.dp))

                            app.features.forEach { feature ->
                                Row(
                                    modifier = Modifier.padding(vertical = 2.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Filled.Check, null, tint = app.color,
                                        modifier = Modifier.size(16.dp))
                                    Spacer(Modifier.width(8.dp))
                                    Text(feature, style = MaterialTheme.typography.bodySmall)
                                }
                            }

                            Spacer(Modifier.height(12.dp))
                            Button(
                                onClick = { onAppSelect(app.id) },
                                colors = ButtonDefaults.buttonColors(containerColor = app.color),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("Open ${app.name}")
                            }
                        }
                    }
                }
            }

            item { ResonanceExplainerCard() }
        }
    }
}

@Composable
private fun ResonanceExplainerCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("V-NAND Resonance System", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))

            Text("The 4D voxel grid (8x8x8x8 = 4096 voxels) achieves resonance when variance aligns with the genesis constant:",
                style = MaterialTheme.typography.bodySmall)
            Spacer(Modifier.height(8.dp))

            Surface(
                shape = RoundedCornerShape(8.dp),
                color = Color(0xFF8B5CF6).copy(alpha = 0.15f),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Target: 0.0219 (Genesis Constant)",
                        style = MaterialTheme.typography.labelMedium,
                        color = Color(0xFF8B5CF6))
                    Text("Gate Threshold: 95%",
                        style = MaterialTheme.typography.labelMedium,
                        color = Color(0xFF8B5CF6))
                    Text("Lorentzian Peak: γ = 0.001",
                        style = MaterialTheme.typography.labelMedium,
                        color = Color(0xFF8B5CF6))
                }
            }
        }
    }
}
