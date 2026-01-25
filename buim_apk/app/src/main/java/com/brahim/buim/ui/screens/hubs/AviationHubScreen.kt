/**
 * Aviation Hub Screen
 * ===================
 *
 * Hub for aviation optimization tools using Brahim resonance.
 * 7 applications for flight planning and operations.
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

data class AviationApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color,
    val features: List<String>
)

private val aviationApps = listOf(
    AviationApp("pathfinder", "Flight Pathfinder", "Optimal route calculation",
        Icons.Filled.Flight, Color(0xFF3B82F6),
        listOf("Great circle routing", "Wind optimization", "Fuel efficiency")),
    AviationApp("fuel", "Fuel Optimizer", "Minimize fuel consumption",
        Icons.Filled.LocalGasStation, Color(0xFF10B981),
        listOf("Weight & balance", "Altitude optimization", "Step climbs")),
    AviationApp("weather", "Weather Router", "Weather-aware planning",
        Icons.Filled.Cloud, Color(0xFF6366F1),
        listOf("Turbulence avoidance", "Icing zones", "Wind shear alerts")),
    AviationApp("conflict", "Conflict Detection", "Airspace deconfliction",
        Icons.Filled.Warning, Color(0xFFEF4444),
        listOf("TCAS logic", "Separation minima", "4D trajectory")),
    AviationApp("altitude", "Altitude Optimizer", "Cruise level selection",
        Icons.Filled.Height, Color(0xFF8B5CF6),
        listOf("Cost index", "RVSM compliance", "Weather avoidance")),
    AviationApp("maintenance", "Maintenance Scheduler", "Predictive maintenance",
        Icons.Filled.Build, Color(0xFFF59E0B),
        listOf("Component tracking", "MEL management", "Reliability analysis")),
    AviationApp("runway", "Runway Allocation", "Airport slot optimization",
        Icons.Filled.FlightLand, Color(0xFFEC4899),
        listOf("Gate assignment", "Taxi routing", "Noise abatement"))
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AviationHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Aviation", fontWeight = FontWeight.Bold) },
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
            item { AviationHeaderCard() }

            item {
                Text("Aviation Tools", style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold)
            }

            items(aviationApps) { app ->
                AviationAppCard(app) { onAppSelect(app.id) }
            }
        }
    }
}

@Composable
private fun AviationHeaderCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.horizontalGradient(
                        listOf(Color(0xFF3B82F6), Color(0xFF1E40AF))
                    )
                )
                .padding(20.dp)
        ) {
            Column {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.Flight, null, tint = Color.White,
                        modifier = Modifier.size(32.dp))
                    Spacer(Modifier.width(12.dp))
                    Text("Brahim Aviation Suite", style = MaterialTheme.typography.titleLarge,
                        color = Color.White, fontWeight = FontWeight.Bold)
                }
                Spacer(Modifier.height(8.dp))
                Text("7 optimization tools using golden ratio resonance for flight operations",
                    style = MaterialTheme.typography.bodyMedium, color = Color.White.copy(alpha = 0.9f))
                Spacer(Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(24.dp)) {
                    AviationStat("7", "Tools")
                    AviationStat("phi", "Weighted")
                    AviationStat("4D", "Trajectory")
                }
            }
        }
    }
}

@Composable
private fun AviationStat(value: String, label: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, style = MaterialTheme.typography.titleMedium,
            color = Color.White, fontWeight = FontWeight.Bold)
        Text(label, style = MaterialTheme.typography.labelSmall,
            color = Color.White.copy(alpha = 0.7f))
    }
}

@Composable
private fun AviationAppCard(app: AviationApp, onClick: () -> Unit) {
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
                    modifier = Modifier.size(48.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(app.icon, null, tint = app.color, modifier = Modifier.size(24.dp))
                    }
                }
                Spacer(Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(app.name, style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold)
                    Text(app.description, style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                IconButton(onClick = onClick) {
                    Icon(Icons.Filled.PlayArrow, "Launch", tint = app.color)
                }
            }

            if (expanded) {
                Spacer(Modifier.height(12.dp))
                HorizontalDivider()
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
            }
        }
    }
}
