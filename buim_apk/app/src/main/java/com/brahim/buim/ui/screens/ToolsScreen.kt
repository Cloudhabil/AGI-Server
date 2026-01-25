/**
 * Tools Screen - SDK Agents Dashboard
 * ====================================
 *
 * Dashboard for accessing BOA SDK agents.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.brahim.buim.ui.theme.GoldenPrimary

/**
 * Tool/Agent definition.
 */
data class ToolInfo(
    val id: String,
    val name: String,
    val domain: String,
    val description: String,
    val capabilities: List<String>,
    val icon: ImageVector
)

/**
 * Hub category definition.
 */
data class HubCategory(
    val id: String,
    val name: String,
    val appCount: Int,
    val icon: ImageVector,
    val color: Color,
    val description: String
)

// Composite Apps Entry
private val compositeAppsEntry = HubCategory(
    "composite_apps", "Composite Apps", 21, Icons.Filled.AutoAwesome, Color(0xFFEC4899),
    "21 skill-powered fusion apps"
)

// Application Hubs (12 categories, 83 total apps)
private val applicationHubs = listOf(
    HubCategory("physics_hub", "Physics", 8, Icons.Filled.Science, Color(0xFF6366F1),
        "Fine structure, Weinberg, mass ratios"),
    HubCategory("math_hub", "Mathematics", 7, Icons.Filled.Calculate, Color(0xFF8B5CF6),
        "Sequences, fractions, operators"),
    HubCategory("cosmology_hub", "Cosmology", 5, Icons.Filled.DarkMode, Color(0xFF1F2937),
        "Dark energy, matter, CMB"),
    HubCategory("aviation_hub", "Aviation", 7, Icons.Filled.Flight, Color(0xFF3B82F6),
        "Flight planning, pathfinding"),
    HubCategory("traffic_hub", "Traffic", 7, Icons.Filled.Traffic, Color(0xFF22C55E),
        "Signal optimization, routing"),
    HubCategory("business_hub", "Business", 7, Icons.Filled.Business, Color(0xFFD4AF37),
        "Fair division, scheduling"),
    HubCategory("solvers_hub", "Solvers", 6, Icons.Filled.Memory, Color(0xFF6366F1),
        "SAT, CFD, PDE, optimization"),
    HubCategory("planetary_hub", "Planetary", 3, Icons.Filled.RocketLaunch, Color(0xFFF59E0B),
        "Titan, Mars, orbital mechanics"),
    HubCategory("security_hub", "Security", 3, Icons.Filled.Security, Color(0xFF22C55E),
        "Wormhole cipher, ASIOS"),
    HubCategory("ml_hub", "ML/AI", 3, Icons.Filled.Psychology, Color(0xFFEC4899),
        "Kelimutu router, phase classifier"),
    HubCategory("visualization_hub", "Visualization", 4, Icons.Filled.Insights, Color(0xFF8B5CF6),
        "Resonance, phase portraits"),
    HubCategory("utilities_hub", "Utilities", 5, Icons.Filled.Build, Color(0xFF3B82F6),
        "Converter, export, formulas")
)

// Available tools
private val availableTools = listOf(
    ToolInfo(
        id = "killer_use_cases",
        name = "Brahim Tools (BNv1)",
        domain = "Utility",
        description = "Killer use cases: Geo IDs, Routes, Fingerprints, Provenance",
        capabilities = listOf(
            "Geospatial Product IDs",
            "Route Tracking & Checksums",
            "Dataset Fingerprinting",
            "OpenAI SDK Integration"
        ),
        icon = Icons.Filled.Build
    ),
    ToolInfo(
        id = "brahim_sudoku",
        name = "Brahim Sudoku",
        domain = "Games",
        description = "10×10 Sudoku with Brahim numbers and mirror constraint",
        capabilities = listOf(
            "Mirror property: α + ω = 214",
            "Uses {27,42,60,75,97,121,136,154,172,187}",
            "4 difficulty levels"
        ),
        icon = Icons.Filled.GridOn
    ),
    ToolInfo(
        id = "egyptian_fractions",
        name = "Egyptian Fractions",
        domain = "Mathematics",
        description = "Solves 4/n = 1/a + 1/b + 1/c problems",
        capabilities = listOf(
            "Erdős-Straus conjecture",
            "Fair division",
            "Unit fraction decomposition"
        ),
        icon = Icons.Filled.Calculate
    ),
    ToolInfo(
        id = "sat_solver",
        name = "SAT Solver",
        domain = "Logic",
        description = "Boolean satisfiability solver using DPLL",
        capabilities = listOf(
            "CNF formula solving",
            "DIMACS format",
            "Phase transition detection"
        ),
        icon = Icons.Filled.Memory
    ),
    ToolInfo(
        id = "physics_calculator",
        name = "Physics Calculator",
        domain = "Physics",
        description = "Derives constants from Brahim sequence",
        capabilities = listOf(
            "Fine structure constant",
            "Weinberg angle",
            "Mass ratios",
            "Cosmological parameters"
        ),
        icon = Icons.Filled.Science
    ),
    ToolInfo(
        id = "manifold_query",
        name = "Manifold Query",
        domain = "AI",
        description = "Direct access to unified manifold",
        capabilities = listOf(
            "Ball Tree search",
            "V-NAND learning",
            "Kelimutu routing"
        ),
        icon = Icons.Filled.Hub
    ),
    ToolInfo(
        id = "solar_map",
        name = "Solar System Map",
        domain = "Astronomy",
        description = "Brahim Number geomap of the Solar System",
        capabilities = listOf(
            "Planetary Brahim IDs",
            "Heliocentric coordinates",
            "Sequence resonances",
            "Exoplanet encoding"
        ),
        icon = Icons.Filled.Public
    ),
    ToolInfo(
        id = "secure_chat",
        name = "Secure Chat",
        domain = "Communication",
        description = "Signal-like encrypted messaging with walkie-talkie",
        capabilities = listOf(
            "End-to-end encryption",
            "Wormhole Cipher (β = 0.236)",
            "Push-to-Talk voice",
            "BNP address routing"
        ),
        icon = Icons.Filled.Lock
    ),
    ToolInfo(
        id = "network_diagnostics",
        name = "Network Diagnostics",
        domain = "Network",
        description = "Ping, traceroute, and connectivity testing",
        capabilities = listOf(
            "ICMP/TCP ping",
            "BNP address testing",
            "Packet statistics",
            "Relay connectivity"
        ),
        icon = Icons.Filled.NetworkCheck
    )
)

/**
 * Tools screen composable.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ToolsScreen(
    onToolSelected: (String) -> Unit,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("SDK Tools") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Header Card
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
                            Text("BUIM Application Suite",
                                style = MaterialTheme.typography.titleLarge,
                                color = Color.White, fontWeight = FontWeight.Bold)
                            Spacer(Modifier.height(4.dp))
                            Text("83 applications across 12 categories",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                            Text("B(11) = 214 Consciousness Integrated",
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.White.copy(alpha = 0.7f))
                        }
                    }
                }
            }

            // Featured: Symmetry Dashboard & Composite Apps
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Symmetry Dashboard
                    Card(
                        modifier = Modifier
                            .weight(1f)
                            .clickable { onToolSelected("symmetry_dashboard") },
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(
                                    Brush.verticalGradient(
                                        listOf(Color(0xFF6366F1), Color(0xFFD4AF37))
                                    )
                                )
                                .padding(16.dp)
                        ) {
                            Column {
                                Icon(Icons.Filled.Balance, null, tint = Color.White,
                                    modifier = Modifier.size(32.dp))
                                Spacer(Modifier.height(8.dp))
                                Text("Symmetry",
                                    style = MaterialTheme.typography.titleSmall,
                                    color = Color.White, fontWeight = FontWeight.Bold)
                                Text("Mirror pairs",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = Color.White.copy(alpha = 0.8f))
                            }
                        }
                    }

                    // Composite Apps
                    Card(
                        modifier = Modifier
                            .weight(1f)
                            .clickable { onToolSelected("composite_apps") },
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(
                                    Brush.verticalGradient(
                                        listOf(Color(0xFFEC4899), Color(0xFF8B5CF6))
                                    )
                                )
                                .padding(16.dp)
                        ) {
                            Column {
                                Icon(Icons.Filled.AutoAwesome, null, tint = Color.White,
                                    modifier = Modifier.size(32.dp))
                                Spacer(Modifier.height(8.dp))
                                Text("Composites",
                                    style = MaterialTheme.typography.titleSmall,
                                    color = Color.White, fontWeight = FontWeight.Bold)
                                Text("21 fusion apps",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = Color.White.copy(alpha = 0.8f))
                            }
                        }
                    }
                }
            }

            // Application Hubs Section
            item {
                Text(
                    text = "Application Hubs",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)
                )
            }

            item {
                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    contentPadding = PaddingValues(vertical = 4.dp)
                ) {
                    items(applicationHubs) { hub ->
                        HubCard(
                            hub = hub,
                            onClick = { onToolSelected(hub.id) }
                        )
                    }
                }
            }

            // Quick Tools Section
            item {
                Text(
                    text = "Quick Access Tools",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(top = 16.dp, bottom = 4.dp)
                )
            }

            items(availableTools) { tool ->
                ToolCard(
                    tool = tool,
                    onClick = { onToolSelected(tool.id) }
                )
            }

            item {
                Spacer(modifier = Modifier.height(16.dp))

                // Manifold stats card
                ManifoldStatsCard()
            }
        }
    }
}

/**
 * Tool card composable.
 */
@Composable
private fun ToolCard(
    tool: ToolInfo,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        onClick = onClick,
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Icon
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = GoldenPrimary.copy(alpha = 0.15f)
            ) {
                Icon(
                    imageVector = tool.icon,
                    contentDescription = null,
                    modifier = Modifier
                        .padding(12.dp)
                        .size(32.dp),
                    tint = GoldenPrimary
                )
            }

            // Content
            Column(modifier = Modifier.weight(1f)) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = tool.name,
                        style = MaterialTheme.typography.titleSmall
                    )
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = MaterialTheme.colorScheme.secondaryContainer
                    ) {
                        Text(
                            text = tool.domain,
                            style = MaterialTheme.typography.labelSmall,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }

                Text(
                    text = tool.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = 4.dp)
                )

                // Capabilities
                FlowRow(
                    modifier = Modifier.padding(top = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    tool.capabilities.take(3).forEach { capability ->
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = MaterialTheme.colorScheme.surfaceVariant
                        ) {
                            Text(
                                text = capability,
                                style = MaterialTheme.typography.labelSmall,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }
                }
            }

            // Arrow
            Icon(
                Icons.Filled.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Hub category card composable.
 */
@Composable
private fun HubCard(
    hub: HubCategory,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.width(160.dp),
        onClick = onClick,
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = hub.color.copy(alpha = 0.15f),
                modifier = Modifier.size(56.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = hub.icon,
                        contentDescription = null,
                        tint = hub.color,
                        modifier = Modifier.size(28.dp)
                    )
                }
            }
            Spacer(Modifier.height(12.dp))
            Text(
                text = hub.name,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold
            )
            Text(
                text = "${hub.appCount} apps",
                style = MaterialTheme.typography.labelSmall,
                color = hub.color
            )
            Spacer(Modifier.height(4.dp))
            Text(
                text = hub.description,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2
            )
        }
    }
}

/**
 * Manifold statistics card.
 */
@Composable
private fun ManifoldStatsCard(
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Manifold Status",
                style = MaterialTheme.typography.titleSmall
            )

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(label = "Ball Tree", value = "384-D")
                StatItem(label = "V-NAND", value = "4096 voxels")
                StatItem(label = "Skills", value = "60+")
            }

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(label = "β", value = "0.2361")
                StatItem(label = "φ", value = "1.6180")
                StatItem(label = "S", value = "214")
            }
        }
    }
}

@Composable
private fun StatItem(
    label: String,
    value: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
