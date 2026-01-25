/**
 * Business Hub Screen
 * ===================
 *
 * Hub for business optimization tools using Brahim fair division.
 * 7 applications for resource allocation and management.
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
import com.brahim.buim.ui.theme.GoldenPrimary

data class BusinessApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color
)

private val businessApps = listOf(
    BusinessApp("allocator", "Resource Allocator", "Fair division using Egyptian fractions",
        Icons.Filled.PieChart, Color(0xFFD4AF37)),
    BusinessApp("salary", "Salary Structure", "Compensation optimization",
        Icons.Filled.AttachMoney, Color(0xFF22C55E)),
    BusinessApp("scheduler", "Task Scheduler", "Project timeline optimization",
        Icons.Filled.CalendarMonth, Color(0xFF3B82F6)),
    BusinessApp("risk", "Risk Assessment", "Portfolio risk analysis",
        Icons.Filled.Shield, Color(0xFFEF4444)),
    BusinessApp("synergy", "Team Synergy", "Collaboration metrics",
        Icons.Filled.Groups, Color(0xFF8B5CF6)),
    BusinessApp("compliance", "Compliance Checker", "Regulatory validation",
        Icons.Filled.FactCheck, Color(0xFF14B8A6)),
    BusinessApp("kpi", "KPI Dashboard", "Key performance indicators",
        Icons.Filled.Analytics, Color(0xFFF59E0B))
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BusinessHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Business", fontWeight = FontWeight.Bold) },
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
                                    listOf(GoldenPrimary, Color(0xFFB8860B))
                                )
                            )
                            .padding(20.dp)
                    ) {
                        Column {
                            Text("Business Suite", style = MaterialTheme.typography.titleLarge,
                                color = Color.White, fontWeight = FontWeight.Bold)
                            Text("7 optimization tools using Egyptian fraction fair division",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                        }
                    }
                }
            }

            items(businessApps) { app ->
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
