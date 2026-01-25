/**
 * Universe Simulator Screen
 * =========================
 *
 * Composite App: Physics + Cosmology + Visualization
 * Interactive cosmic exploration with real physics.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens.composite

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import kotlin.math.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UniverseSimulatorScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var cosmicAge by remember { mutableFloatStateOf(13.8f) }
    var darkEnergyRatio by remember { mutableFloatStateOf(0.689f) }
    var darkMatterRatio by remember { mutableFloatStateOf(0.266f) }
    var hubbleConstant by remember { mutableFloatStateOf(67.4f) }
    var showTimeline by remember { mutableStateOf(false) }

    val baryonicMatter = 1f - darkEnergyRatio - darkMatterRatio

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Universe Simulator", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Filled.ArrowBack, "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color(0xFF0D1117)
                )
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFF0D1117))
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Universe Visualization
            item {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(250.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF161B22))
                ) {
                    Box(modifier = Modifier.fillMaxSize()) {
                        UniverseCanvas(
                            darkEnergy = darkEnergyRatio,
                            darkMatter = darkMatterRatio,
                            baryonic = baryonicMatter
                        )
                        // Overlay info
                        Column(
                            modifier = Modifier
                                .align(Alignment.TopStart)
                                .padding(16.dp)
                        ) {
                            Text("Cosmic Age: ${String.format("%.1f", cosmicAge)} Gyr",
                                style = MaterialTheme.typography.labelMedium,
                                color = Color.White)
                            Text("H₀: ${String.format("%.1f", hubbleConstant)} km/s/Mpc",
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.White.copy(alpha = 0.7f))
                        }
                    }
                }
            }

            // Composition Breakdown
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF161B22))
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Universe Composition", style = MaterialTheme.typography.titleMedium,
                            color = Color.White, fontWeight = FontWeight.SemiBold)
                        Spacer(Modifier.height(16.dp))

                        CompositionBar(
                            darkEnergy = darkEnergyRatio,
                            darkMatter = darkMatterRatio,
                            baryonic = baryonicMatter
                        )

                        Spacer(Modifier.height(16.dp))

                        CompositionRow("Dark Energy", darkEnergyRatio, Color(0xFF6366F1),
                            "Λ = 31/45 (Brahim)")
                        CompositionRow("Dark Matter", darkMatterRatio, Color(0xFF8B5CF6),
                            "φ⁵/200 aligned")
                        CompositionRow("Baryonic Matter", baryonicMatter, Color(0xFFD4AF37),
                            "Observable universe")
                    }
                }
            }

            // Controls
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF161B22))
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Simulation Controls", style = MaterialTheme.typography.titleMedium,
                            color = Color.White, fontWeight = FontWeight.SemiBold)
                        Spacer(Modifier.height(16.dp))

                        Text("Dark Energy Ratio", style = MaterialTheme.typography.labelSmall,
                            color = Color.White.copy(alpha = 0.7f))
                        Slider(
                            value = darkEnergyRatio,
                            onValueChange = { darkEnergyRatio = it.coerceIn(0.5f, 0.8f) },
                            valueRange = 0.5f..0.8f,
                            colors = SliderDefaults.colors(
                                thumbColor = Color(0xFF6366F1),
                                activeTrackColor = Color(0xFF6366F1)
                            )
                        )

                        Text("Dark Matter Ratio", style = MaterialTheme.typography.labelSmall,
                            color = Color.White.copy(alpha = 0.7f))
                        Slider(
                            value = darkMatterRatio,
                            onValueChange = { darkMatterRatio = it.coerceIn(0.15f, 0.35f) },
                            valueRange = 0.15f..0.35f,
                            colors = SliderDefaults.colors(
                                thumbColor = Color(0xFF8B5CF6),
                                activeTrackColor = Color(0xFF8B5CF6)
                            )
                        )

                        Text("Hubble Constant (km/s/Mpc)", style = MaterialTheme.typography.labelSmall,
                            color = Color.White.copy(alpha = 0.7f))
                        Slider(
                            value = hubbleConstant,
                            onValueChange = { hubbleConstant = it },
                            valueRange = 60f..80f,
                            colors = SliderDefaults.colors(
                                thumbColor = Color(0xFFD4AF37),
                                activeTrackColor = Color(0xFFD4AF37)
                            )
                        )

                        Spacer(Modifier.height(8.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            OutlinedButton(
                                onClick = {
                                    darkEnergyRatio = 0.689f
                                    darkMatterRatio = 0.266f
                                    hubbleConstant = 67.4f
                                },
                                modifier = Modifier.weight(1f)
                            ) {
                                Text("Reset to ΛCDM", color = Color.White)
                            }
                            Button(
                                onClick = {
                                    // Set to Brahim predictions
                                    darkEnergyRatio = 31f / 45f
                                    darkMatterRatio = (BrahimConstants.PHI.pow(5) / 200).toFloat()
                                    hubbleConstant = 67.4f
                                },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = Color(0xFFD4AF37)
                                ),
                                modifier = Modifier.weight(1f)
                            ) {
                                Text("Brahim Model")
                            }
                        }
                    }
                }
            }

            // Physics Constants
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF161B22))
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Filled.Science, null, tint = Color(0xFF6366F1))
                            Spacer(Modifier.width(8.dp))
                            Text("Physics Integration", style = MaterialTheme.typography.titleMedium,
                                color = Color.White, fontWeight = FontWeight.SemiBold)
                        }
                        Spacer(Modifier.height(12.dp))

                        PhysicsConstantRow("Fine Structure (α⁻¹)", "137.036", "2 ppm")
                        PhysicsConstantRow("Weinberg Angle", "0.2312", "0.2%")
                        PhysicsConstantRow("CMB Temperature", "2.725 K", "COBE")
                        PhysicsConstantRow("Cosmic Age", "${String.format("%.2f", cosmicAge)} Gyr", "Planck")
                    }
                }
            }

            // Cosmic Timeline Toggle
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF161B22))
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Cosmic Timeline", style = MaterialTheme.typography.titleMedium,
                                color = Color.White, fontWeight = FontWeight.SemiBold)
                            Switch(
                                checked = showTimeline,
                                onCheckedChange = { showTimeline = it },
                                colors = SwitchDefaults.colors(
                                    checkedThumbColor = Color(0xFFD4AF37),
                                    checkedTrackColor = Color(0xFFD4AF37).copy(alpha = 0.5f)
                                )
                            )
                        }

                        if (showTimeline) {
                            Spacer(Modifier.height(12.dp))
                            TimelineEvent("Big Bang", "0", "Singularity")
                            TimelineEvent("Inflation", "10⁻³⁶ s", "Exponential expansion")
                            TimelineEvent("Recombination", "380,000 yr", "CMB release")
                            TimelineEvent("First Stars", "200 Myr", "Cosmic dawn")
                            TimelineEvent("Galaxy Formation", "1 Gyr", "Structure emerges")
                            TimelineEvent("Solar System", "9.2 Gyr", "Our home forms")
                            TimelineEvent("Today", "13.8 Gyr", "B(11) = 214")
                        }
                    }
                }
            }

            // Skills Used
            item {
                SkillsUsedCard(
                    skills = listOf(
                        "Physics" to "Dark energy/matter ratios",
                        "Cosmology" to "Timeline and expansion",
                        "Visualization" to "Interactive canvas"
                    )
                )
            }
        }
    }
}

@Composable
private fun UniverseCanvas(
    darkEnergy: Float,
    darkMatter: Float,
    baryonic: Float
) {
    Canvas(modifier = Modifier.fillMaxSize()) {
        val center = Offset(size.width / 2, size.height / 2)
        val maxRadius = minOf(size.width, size.height) / 2.5f

        // Draw dark energy (outer glow)
        for (i in 20 downTo 0) {
            val alpha = (1f - i / 20f) * 0.3f * darkEnergy
            drawCircle(
                color = Color(0xFF6366F1).copy(alpha = alpha),
                radius = maxRadius + i * 5,
                center = center
            )
        }

        // Draw dark matter halo
        drawCircle(
            color = Color(0xFF8B5CF6).copy(alpha = 0.4f),
            radius = maxRadius * 0.8f,
            center = center
        )

        // Draw baryonic matter (visible universe)
        drawCircle(
            color = Color(0xFFD4AF37).copy(alpha = 0.6f),
            radius = maxRadius * baryonic * 5,
            center = center
        )

        // Draw stars
        val starCount = 50
        for (i in 0 until starCount) {
            val angle = (i * 137.508f) * (PI / 180f)  // Golden angle
            val distance = sqrt(i.toFloat() / starCount) * maxRadius * 0.7f
            val x = center.x + cos(angle).toFloat() * distance
            val y = center.y + sin(angle).toFloat() * distance
            val starSize = (1f + (i % 3)) * 1.5f

            drawCircle(
                color = Color.White.copy(alpha = 0.8f),
                radius = starSize,
                center = Offset(x, y)
            )
        }

        // Draw center (observer)
        drawCircle(
            color = Color.White,
            radius = 4f,
            center = center
        )
    }
}

@Composable
private fun CompositionBar(
    darkEnergy: Float,
    darkMatter: Float,
    baryonic: Float
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(24.dp)
    ) {
        Box(
            modifier = Modifier
                .weight(darkEnergy)
                .fillMaxHeight()
                .background(
                    Color(0xFF6366F1),
                    RoundedCornerShape(topStart = 8.dp, bottomStart = 8.dp)
                )
        )
        Box(
            modifier = Modifier
                .weight(darkMatter)
                .fillMaxHeight()
                .background(Color(0xFF8B5CF6))
        )
        Box(
            modifier = Modifier
                .weight(baryonic)
                .fillMaxHeight()
                .background(
                    Color(0xFFD4AF37),
                    RoundedCornerShape(topEnd = 8.dp, bottomEnd = 8.dp)
                )
        )
    }
}

@Composable
private fun CompositionRow(name: String, value: Float, color: Color, note: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .background(color, CircleShape)
            )
            Spacer(Modifier.width(8.dp))
            Text(name, style = MaterialTheme.typography.bodySmall, color = Color.White)
        }
        Column(horizontalAlignment = Alignment.End) {
            Text("${String.format("%.1f", value * 100)}%",
                style = MaterialTheme.typography.bodySmall,
                color = color, fontFamily = FontFamily.Monospace)
            Text(note, style = MaterialTheme.typography.labelSmall,
                color = Color.White.copy(alpha = 0.5f))
        }
    }
}

@Composable
private fun PhysicsConstantRow(name: String, value: String, source: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(name, style = MaterialTheme.typography.bodySmall, color = Color.White)
        Row {
            Text(value, style = MaterialTheme.typography.bodySmall,
                color = Color(0xFFD4AF37), fontFamily = FontFamily.Monospace)
            Spacer(Modifier.width(8.dp))
            Text("($source)", style = MaterialTheme.typography.labelSmall,
                color = Color.White.copy(alpha = 0.5f))
        }
    }
}

@Composable
private fun TimelineEvent(event: String, time: String, description: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .background(Color(0xFFD4AF37), CircleShape)
        )
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(event, style = MaterialTheme.typography.bodySmall,
                color = Color.White, fontWeight = FontWeight.SemiBold)
            Text(description, style = MaterialTheme.typography.labelSmall,
                color = Color.White.copy(alpha = 0.7f))
        }
        Text(time, style = MaterialTheme.typography.labelSmall,
            color = Color(0xFF6366F1), fontFamily = FontFamily.Monospace)
    }
}

@Composable
private fun SkillsUsedCard(skills: List<Pair<String, String>>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF161B22))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Filled.Hub, null, tint = Color(0xFF6366F1))
                Spacer(Modifier.width(8.dp))
                Text("Skills Composed", style = MaterialTheme.typography.titleSmall,
                    color = Color.White, fontWeight = FontWeight.SemiBold)
            }
            Spacer(Modifier.height(12.dp))

            skills.forEach { (skill, usage) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = Color(0xFF6366F1).copy(alpha = 0.15f)
                    ) {
                        Text(skill, style = MaterialTheme.typography.labelSmall,
                            color = Color(0xFF6366F1),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                    }
                    Text(usage, style = MaterialTheme.typography.labelSmall,
                        color = Color.White.copy(alpha = 0.7f))
                }
            }
        }
    }
}
