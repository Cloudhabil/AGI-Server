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
import androidx.compose.ui.graphics.vector.ImageVector
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
            item {
                Text(
                    text = "Available Agents",
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(bottom = 8.dp)
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
