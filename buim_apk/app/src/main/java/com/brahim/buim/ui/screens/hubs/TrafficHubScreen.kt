/**
 * Traffic Hub Screen
 * ==================
 *
 * Hub for traffic optimization tools using Brahim wave equations.
 * 7 applications for urban mobility.
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

data class TrafficApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color
)

private val trafficApps = listOf(
    TrafficApp("signal", "Signal Timing", "Optimize traffic light cycles",
        Icons.Filled.TrafficOutlined, Color(0xFF22C55E)),
    TrafficApp("congestion", "Congestion Predictor", "Forecast traffic density",
        Icons.Filled.Timeline, Color(0xFFEF4444)),
    TrafficApp("route", "Route Optimizer", "Find optimal paths",
        Icons.Filled.Route, Color(0xFF3B82F6)),
    TrafficApp("parking", "Parking Finder", "Locate available spots",
        Icons.Filled.LocalParking, Color(0xFF8B5CF6)),
    TrafficApp("emergency", "Emergency Routing", "Priority vehicle paths",
        Icons.Filled.LocalHospital, Color(0xFFF43F5E)),
    TrafficApp("waves", "Traffic Wave PDE", "Solve traffic flow equations",
        Icons.Filled.Waves, Color(0xFF14B8A6)),
    TrafficApp("intersection", "Intersection Control", "Multi-way optimization",
        Icons.Filled.CallSplit, Color(0xFFF59E0B))
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrafficHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Traffic", fontWeight = FontWeight.Bold) },
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
                                    listOf(Color(0xFF22C55E), Color(0xFF14B8A6))
                                )
                            )
                            .padding(20.dp)
                    ) {
                        Column {
                            Text("Traffic Optimization", style = MaterialTheme.typography.titleLarge,
                                color = Color.White, fontWeight = FontWeight.Bold)
                            Text("7 tools using Brahim wave equations for urban mobility",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                        }
                    }
                }
            }

            items(trafficApps) { app ->
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
                            modifier = Modifier.size(48.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(app.icon, null, tint = app.color,
                                    modifier = Modifier.size(24.dp))
                            }
                        }
                        Spacer(Modifier.width(16.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(app.name, style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.SemiBold)
                            Text(app.description, style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Icon(Icons.Filled.ChevronRight, null, tint = app.color)
                    }
                }
            }
        }
    }
}
