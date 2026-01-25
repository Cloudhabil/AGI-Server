/**
 * Solvers Hub Screen
 * ==================
 *
 * Hub for computational solvers using Brahim algorithms.
 * 6 applications for SAT, CFD, PDE, and optimization.
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

data class SolverApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color,
    val complexity: String
)

private val solverApps = listOf(
    SolverApp("sat", "SAT Solver", "Boolean satisfiability (DPLL)",
        Icons.Filled.Memory, Color(0xFF6366F1), "NP-Complete"),
    SolverApp("cfd", "CFD Solver", "Computational fluid dynamics",
        Icons.Filled.Air, Color(0xFF3B82F6), "Navier-Stokes"),
    SolverApp("pde", "PDE Solver", "Method of characteristics",
        Icons.Filled.Functions, Color(0xFF8B5CF6), "Hyperbolic"),
    SolverApp("optimization", "Optimizer", "Gradient descent with golden ratio",
        Icons.Filled.TrendingUp, Color(0xFF22C55E), "Convex"),
    SolverApp("constraint", "Constraint Solver", "Constraint satisfaction problems",
        Icons.Filled.Rule, Color(0xFFF59E0B), "CSP"),
    SolverApp("linear", "Linear Algebra", "Matrix operations and decomposition",
        Icons.Filled.GridOn, Color(0xFFEC4899), "O(n^3)")
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SolversHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Solvers", fontWeight = FontWeight.Bold) },
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
                                    listOf(Color(0xFF6366F1), Color(0xFF8B5CF6))
                                )
                            )
                            .padding(20.dp)
                    ) {
                        Column {
                            Text("Computational Solvers", style = MaterialTheme.typography.titleLarge,
                                color = Color.White, fontWeight = FontWeight.Bold)
                            Text("6 solvers using Brahim-weighted algorithms",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                        }
                    }
                }
            }

            items(solverApps) { app ->
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
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = app.color.copy(alpha = 0.15f)
                        ) {
                            Text(app.complexity, style = MaterialTheme.typography.labelSmall,
                                color = app.color, modifier = Modifier.padding(4.dp, 2.dp))
                        }
                    }
                }
            }
        }
    }
}
