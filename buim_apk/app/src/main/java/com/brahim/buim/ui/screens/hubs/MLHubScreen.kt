/**
 * ML Hub Screen
 * =============
 *
 * Hub for ML/AI tools using Brahim resonance.
 * Kelimutu router, wavelength analyzer, phase classifier.
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

data class MLApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color,
    val technique: String
)

private val mlApps = listOf(
    MLApp("intent", "Kelimutu Router", "3-lake intent classification",
        Icons.Filled.Hub, Color(0xFF14B8A6), "sigmoid/tanh/softplus"),
    MLApp("wavelength", "Wavelength Analyzer", "12-wavelength signal analysis",
        Icons.Filled.Waves, Color(0xFF8B5CF6), "FFT + resonance"),
    MLApp("phase", "Phase Classifier", "Time-series phase detection",
        Icons.Filled.Timeline, Color(0xFFEC4899), "FitzHugh-Nagumo")
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MLHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("ML/AI", fontWeight = FontWeight.Bold) },
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
                                Icon(Icons.Filled.Psychology, null, tint = Color.White)
                                Spacer(Modifier.width(8.dp))
                                Text("ML/AI Suite", style = MaterialTheme.typography.titleLarge,
                                    color = Color.White, fontWeight = FontWeight.Bold)
                            }
                            Spacer(Modifier.height(8.dp))
                            Text("Neural classification using Brahim resonance principles",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                        }
                    }
                }
            }

            item { KelimutuExplainerCard() }

            items(mlApps) { app ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onAppSelect(app.id) },
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
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
                            Spacer(Modifier.height(4.dp))
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = app.color.copy(alpha = 0.15f)
                            ) {
                                Text(app.technique, style = MaterialTheme.typography.labelSmall,
                                    color = app.color, modifier = Modifier.padding(4.dp, 2.dp))
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun KelimutuExplainerCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Kelimutu 3-Lake System", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))

            LakeRow("Tiwu Ata Mbupu", "Literal", "sigmoid", Color(0xFF2E5A4D))
            LakeRow("Tiwu Nuwa Muri", "Semantic", "tanh", Color(0xFF1A4A6E))
            LakeRow("Tiwu Ata Polo", "Structural", "softplus", Color(0xFF8B4513))

            Spacer(Modifier.height(8.dp))
            Text("Based on Kelimutu volcano (8.77°S, 121.82°E)",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text("Note: 121.82 ≈ B(6) = 121 in Brahim sequence",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun LakeRow(name: String, type: String, activation: String, color: Color) {
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
                    .background(color, RoundedCornerShape(2.dp))
            )
            Spacer(Modifier.width(8.dp))
            Text(name, style = MaterialTheme.typography.bodySmall)
        }
        Text(type, style = MaterialTheme.typography.bodySmall)
        Text(activation, style = MaterialTheme.typography.labelSmall, color = color)
    }
}
