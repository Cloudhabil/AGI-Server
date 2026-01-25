/**
 * Composite Apps Hub Screen
 * =========================
 *
 * Hub for 21 skill-powered composite applications.
 * Organized by category: Science, Navigation, Enterprise, Exploration, Intelligence.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens.composite

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.skills.CompositeCategory
import com.brahim.buim.skills.ExecutionMode
import com.brahim.buim.ui.theme.GoldenPrimary

/**
 * UI representation of a composite app.
 */
data class CompositeAppUI(
    val id: String,
    val name: String,
    val description: String,
    val skillCount: Int,
    val skills: List<String>,
    val category: CompositeCategory,
    val executionMode: ExecutionMode,
    val icon: ImageVector,
    val primaryColor: Color,
    val secondaryColor: Color
)

// Category colors and icons
private val categoryConfig = mapOf(
    CompositeCategory.SCIENCE to Triple(Color(0xFF6366F1), Color(0xFF8B5CF6), Icons.Filled.Science),
    CompositeCategory.NAVIGATION to Triple(Color(0xFF3B82F6), Color(0xFF14B8A6), Icons.Filled.Navigation),
    CompositeCategory.ENTERPRISE to Triple(Color(0xFFD4AF37), Color(0xFF22C55E), Icons.Filled.Business),
    CompositeCategory.EXPLORATION to Triple(Color(0xFFF59E0B), Color(0xFFEC4899), Icons.Filled.Explore),
    CompositeCategory.INTELLIGENCE to Triple(Color(0xFFEC4899), Color(0xFF8B5CF6), Icons.Filled.Psychology)
)

// All 21 composite applications
private val compositeApps = listOf(
    // SCIENCE (5 apps)
    CompositeAppUI("universe_simulator", "Universe Simulator",
        "Interactive cosmic exploration with real physics", 3,
        listOf("Physics", "Cosmology", "Visualization"),
        CompositeCategory.SCIENCE, ExecutionMode.FUSION,
        Icons.Filled.Public, Color(0xFF6366F1), Color(0xFF8B5CF6)),

    CompositeAppUI("pinn_lab", "PINN Physics Lab",
        "Physics-informed neural networks", 3,
        listOf("Physics", "ML", "Solvers"),
        CompositeCategory.SCIENCE, ExecutionMode.FUSION,
        Icons.Filled.Science, Color(0xFF8B5CF6), Color(0xFFEC4899)),

    CompositeAppUI("cosmic_calculator", "Cosmic Calculator",
        "Universe-scale computations", 3,
        listOf("Physics", "Cosmology", "Math"),
        CompositeCategory.SCIENCE, ExecutionMode.PARALLEL,
        Icons.Filled.Calculate, Color(0xFF6366F1), Color(0xFF14B8A6)),

    CompositeAppUI("golden_optimizer", "Golden Optimizer",
        "Phi-weighted optimization", 3,
        listOf("Math", "Solvers", "Visualization"),
        CompositeCategory.SCIENCE, ExecutionMode.FUSION,
        Icons.Filled.TrendingUp, Color(0xFFD4AF37), Color(0xFF6366F1)),

    CompositeAppUI("resonance_lab", "Resonance Lab",
        "V-NAND resonance experimentation", 3,
        listOf("Visualization", "Physics", "ML"),
        CompositeCategory.SCIENCE, ExecutionMode.FUSION,
        Icons.Filled.GraphicEq, Color(0xFF8B5CF6), Color(0xFFEC4899)),

    CompositeAppUI("brahim_workspace", "Brahim Workspace",
        "Complete calculation environment", 3,
        listOf("Utilities", "Math", "Visualization"),
        CompositeCategory.SCIENCE, ExecutionMode.SEQUENTIAL,
        Icons.Filled.Workspaces, Color(0xFFD4AF37), Color(0xFF8B5CF6)),

    // NAVIGATION (4 apps)
    CompositeAppUI("smart_navigator", "Smart Navigator",
        "Multi-modal route optimization", 3,
        listOf("Aviation", "Traffic", "Solvers"),
        CompositeCategory.NAVIGATION, ExecutionMode.SEQUENTIAL,
        Icons.Filled.Navigation, Color(0xFF3B82F6), Color(0xFF14B8A6)),

    CompositeAppUI("aerospace_optimizer", "Aerospace Optimizer",
        "CFD + trajectory optimization", 3,
        listOf("Aviation", "Solvers", "Physics"),
        CompositeCategory.NAVIGATION, ExecutionMode.SEQUENTIAL,
        Icons.Filled.Flight, Color(0xFF3B82F6), Color(0xFF6366F1)),

    CompositeAppUI("emergency_response", "Emergency Response",
        "Crisis routing and coordination", 3,
        listOf("Traffic", "Aviation", "Security"),
        CompositeCategory.NAVIGATION, ExecutionMode.PARALLEL,
        Icons.Filled.LocalHospital, Color(0xFFEF4444), Color(0xFF3B82F6)),

    CompositeAppUI("fleet_manager", "Fleet Manager",
        "Multi-vehicle coordination", 3,
        listOf("Aviation", "Business", "Traffic"),
        CompositeCategory.NAVIGATION, ExecutionMode.PARALLEL,
        Icons.Filled.LocalShipping, Color(0xFF14B8A6), Color(0xFF3B82F6)),

    // ENTERPRISE (4 apps)
    CompositeAppUI("secure_business", "Secure Business Suite",
        "Protected financial operations with AI", 3,
        listOf("Security", "Business", "ML"),
        CompositeCategory.ENTERPRISE, ExecutionMode.PARALLEL,
        Icons.Filled.Security, Color(0xFF22C55E), Color(0xFFD4AF37)),

    CompositeAppUI("quantum_finance", "Quantum Finance",
        "Brahim-based trading algorithms", 3,
        listOf("Physics", "Business", "Security"),
        CompositeCategory.ENTERPRISE, ExecutionMode.PARALLEL,
        Icons.Filled.ShowChart, Color(0xFFD4AF37), Color(0xFF6366F1)),

    CompositeAppUI("crypto_observatory", "Crypto Observatory",
        "Cipher strength visualization", 3,
        listOf("Security", "Math", "Visualization"),
        CompositeCategory.ENTERPRISE, ExecutionMode.PARALLEL,
        Icons.Filled.Lock, Color(0xFF22C55E), Color(0xFF8B5CF6)),

    CompositeAppUI("compliance_intel", "Compliance Intelligence",
        "AI-driven regulatory validation", 3,
        listOf("Business", "Security", "ML"),
        CompositeCategory.ENTERPRISE, ExecutionMode.SEQUENTIAL,
        Icons.Filled.FactCheck, Color(0xFFD4AF37), Color(0xFF22C55E)),

    // EXPLORATION (3 apps)
    CompositeAppUI("titan_colony", "Titan Colony Planner",
        "Space colony resource management", 3,
        listOf("Planetary", "Business", "Visualization"),
        CompositeCategory.EXPLORATION, ExecutionMode.SEQUENTIAL,
        Icons.Filled.Satellite, Color(0xFFF59E0B), Color(0xFF8B5CF6)),

    CompositeAppUI("mars_mission", "Mars Mission Control",
        "Interplanetary trajectory planning", 3,
        listOf("Planetary", "Planetary", "Solvers"),
        CompositeCategory.EXPLORATION, ExecutionMode.SEQUENTIAL,
        Icons.Filled.RocketLaunch, Color(0xFFEF4444), Color(0xFFF59E0B)),

    CompositeAppUI("dark_sector", "Dark Sector Explorer",
        "Dark matter/energy investigation", 3,
        listOf("Cosmology", "Cosmology", "Visualization"),
        CompositeCategory.EXPLORATION, ExecutionMode.PARALLEL,
        Icons.Filled.DarkMode, Color(0xFF1F2937), Color(0xFF6366F1)),

    // INTELLIGENCE (4 apps)
    CompositeAppUI("traffic_brain", "Traffic Brain",
        "AI-powered signal optimization", 3,
        listOf("Traffic", "ML", "Visualization"),
        CompositeCategory.INTELLIGENCE, ExecutionMode.FUSION,
        Icons.Filled.Psychology, Color(0xFF22C55E), Color(0xFFEC4899)),

    CompositeAppUI("fair_division_ai", "Fair Division AI",
        "AI-powered resource allocation", 3,
        listOf("Business", "ML", "Math"),
        CompositeCategory.INTELLIGENCE, ExecutionMode.FUSION,
        Icons.Filled.Balance, Color(0xFFD4AF37), Color(0xFFEC4899)),

    CompositeAppUI("sat_ml_hybrid", "SAT-ML Hybrid",
        "Neural-guided satisfiability", 3,
        listOf("Solvers", "ML", "Math"),
        CompositeCategory.INTELLIGENCE, ExecutionMode.FUSION,
        Icons.Filled.Memory, Color(0xFF6366F1), Color(0xFFEC4899)),

    CompositeAppUI("kelimutu_intel", "Kelimutu Intelligence",
        "Three-lake decision engine", 3,
        listOf("ML", "Security", "Business"),
        CompositeCategory.INTELLIGENCE, ExecutionMode.FUSION,
        Icons.Filled.Hub, Color(0xFF14B8A6), Color(0xFFEC4899))
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CompositeAppsHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedCategory by remember { mutableStateOf<CompositeCategory?>(null) }

    val filteredApps = selectedCategory?.let { cat ->
        compositeApps.filter { it.category == cat }
    } ?: compositeApps

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Composite Apps", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Filled.ArrowBack, "Back")
                    }
                },
                actions = {
                    Text("21 Apps", style = MaterialTheme.typography.labelMedium,
                        modifier = Modifier.padding(end = 16.dp))
                }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Header Card
            item {
                CompositeHeaderCard()
            }

            // Category Filter
            item {
                CategoryFilterRow(
                    selectedCategory = selectedCategory,
                    onCategorySelect = { selectedCategory = it }
                )
            }

            // Stats Card
            item {
                CompositeStatsCard()
            }

            // Apps by category
            if (selectedCategory == null) {
                // Show all categories
                CompositeCategory.values().forEach { category ->
                    val categoryApps = compositeApps.filter { it.category == category }
                    if (categoryApps.isNotEmpty()) {
                        item {
                            CategoryHeader(category)
                        }
                        items(categoryApps) { app ->
                            CompositeAppCard(app = app, onClick = { onAppSelect(app.id) })
                        }
                    }
                }
            } else {
                // Show filtered apps
                items(filteredApps) { app ->
                    CompositeAppCard(app = app, onClick = { onAppSelect(app.id) })
                }
            }

            item { Spacer(Modifier.height(16.dp)) }
        }
    }
}

@Composable
private fun CompositeHeaderCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.horizontalGradient(
                        listOf(Color(0xFF6366F1), Color(0xFFEC4899), Color(0xFFD4AF37))
                    )
                )
                .padding(20.dp)
        ) {
            Column {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.AutoAwesome, null, tint = Color.White)
                    Spacer(Modifier.width(8.dp))
                    Text("Skill-Powered Composites",
                        style = MaterialTheme.typography.titleLarge,
                        color = Color.White, fontWeight = FontWeight.Bold)
                }
                Spacer(Modifier.height(8.dp))
                Text("21 applications combining 60+ skills across 12 domains",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.White.copy(alpha = 0.9f))
                Spacer(Modifier.height(4.dp))
                Text("Execution modes: Sequential | Parallel | Branching | Fusion",
                    style = MaterialTheme.typography.labelSmall,
                    color = Color.White.copy(alpha = 0.7f))
            }
        }
    }
}

@Composable
private fun CategoryFilterRow(
    selectedCategory: CompositeCategory?,
    onCategorySelect: (CompositeCategory?) -> Unit
) {
    LazyRow(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        contentPadding = PaddingValues(vertical = 8.dp)
    ) {
        item {
            FilterChip(
                selected = selectedCategory == null,
                onClick = { onCategorySelect(null) },
                label = { Text("All") },
                leadingIcon = if (selectedCategory == null) {
                    { Icon(Icons.Filled.Check, null, Modifier.size(18.dp)) }
                } else null
            )
        }
        items(CompositeCategory.values().toList()) { category ->
            val (color, _, icon) = categoryConfig[category]!!
            FilterChip(
                selected = selectedCategory == category,
                onClick = { onCategorySelect(category) },
                label = { Text(category.name.lowercase().replaceFirstChar { it.uppercase() }) },
                leadingIcon = {
                    Icon(icon, null, Modifier.size(18.dp),
                        tint = if (selectedCategory == category) Color.White else color)
                },
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = color
                )
            )
        }
    }
}

@Composable
private fun CategoryHeader(category: CompositeCategory) {
    val (color, _, icon) = categoryConfig[category]!!
    val count = compositeApps.count { it.category == category }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, null, tint = color, modifier = Modifier.size(24.dp))
        Spacer(Modifier.width(8.dp))
        Text(
            category.name.lowercase().replaceFirstChar { it.uppercase() },
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        Spacer(Modifier.width(8.dp))
        Surface(
            shape = RoundedCornerShape(4.dp),
            color = color.copy(alpha = 0.15f)
        ) {
            Text("$count apps", style = MaterialTheme.typography.labelSmall,
                color = color, modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp))
        }
    }
}

@Composable
private fun CompositeAppCard(
    app: CompositeAppUI,
    onClick: () -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded },
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // Gradient icon background
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.size(56.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(
                                Brush.linearGradient(
                                    listOf(app.primaryColor, app.secondaryColor)
                                )
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(app.icon, null, tint = Color.White,
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
                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        ExecutionModeChip(app.executionMode, app.primaryColor)
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = app.secondaryColor.copy(alpha = 0.15f)
                        ) {
                            Text("${app.skillCount} skills",
                                style = MaterialTheme.typography.labelSmall,
                                color = app.secondaryColor,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp))
                        }
                    }
                }
                Icon(
                    if (expanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                    "Expand", tint = app.primaryColor
                )
            }

            if (expanded) {
                Spacer(Modifier.height(12.dp))
                Divider()
                Spacer(Modifier.height(12.dp))

                Text("Skills Combined:", style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(8.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    app.skills.forEachIndexed { index, skill ->
                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = if (index == 0) app.primaryColor.copy(alpha = 0.15f)
                            else app.secondaryColor.copy(alpha = 0.15f)
                        ) {
                            Text(skill, style = MaterialTheme.typography.labelMedium,
                                color = if (index == 0) app.primaryColor else app.secondaryColor,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                        }
                        if (index < app.skills.size - 1) {
                            Icon(Icons.Filled.Add, null, tint = MaterialTheme.colorScheme.outline,
                                modifier = Modifier.size(16.dp).align(Alignment.CenterVertically))
                        }
                    }
                }

                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = onClick,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = app.primaryColor
                    )
                ) {
                    Icon(Icons.Filled.PlayArrow, null)
                    Spacer(Modifier.width(8.dp))
                    Text("Launch ${app.name}")
                }
            }
        }
    }
}

@Composable
private fun ExecutionModeChip(mode: ExecutionMode, color: Color) {
    val (icon, label) = when (mode) {
        ExecutionMode.SEQUENTIAL -> Icons.Filled.LinearScale to "Sequential"
        ExecutionMode.PARALLEL -> Icons.Filled.CallSplit to "Parallel"
        ExecutionMode.BRANCHING -> Icons.Filled.AccountTree to "Branching"
        ExecutionMode.FUSION -> Icons.Filled.Merge to "Fusion"
    }

    Surface(
        shape = RoundedCornerShape(4.dp),
        color = color.copy(alpha = 0.15f)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(icon, null, tint = color, modifier = Modifier.size(12.dp))
            Spacer(Modifier.width(4.dp))
            Text(label, style = MaterialTheme.typography.labelSmall, color = color)
        }
    }
}

@Composable
private fun CompositeStatsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Composition Statistics", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatColumn("Apps", "21")
                StatColumn("Skills", "60+")
                StatColumn("Domains", "12")
                StatColumn("Modes", "4")
            }

            Spacer(Modifier.height(12.dp))
            Divider()
            Spacer(Modifier.height(12.dp))

            Text("Brahim Integration", style = MaterialTheme.typography.labelMedium)
            Spacer(Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("φ-weighted execution", style = MaterialTheme.typography.bodySmall)
                Text(String.format("%.10f", BrahimConstants.PHI),
                    style = MaterialTheme.typography.bodySmall,
                    fontFamily = FontFamily.Monospace)
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("β-security threshold", style = MaterialTheme.typography.bodySmall)
                Text(String.format("%.10f", BrahimConstants.BETA_SECURITY),
                    style = MaterialTheme.typography.bodySmall,
                    fontFamily = FontFamily.Monospace)
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Resonance target", style = MaterialTheme.typography.bodySmall)
                Text(String.format("%.4f", BrahimConstants.GENESIS_CONSTANT),
                    style = MaterialTheme.typography.bodySmall,
                    fontFamily = FontFamily.Monospace)
            }
        }
    }
}

@Composable
private fun StatColumn(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold, color = GoldenPrimary)
        Text(label, style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
