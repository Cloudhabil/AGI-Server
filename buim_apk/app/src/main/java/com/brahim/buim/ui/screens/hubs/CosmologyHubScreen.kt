/**
 * Cosmology Hub Screen
 * ====================
 *
 * Hub for cosmological calculations from Brahim framework.
 * Dark energy, dark matter, Hubble constant, CMB, timeline.
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.ui.theme.GoldenPrimary

data class CosmologyApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color,
    val value: String,
    val codata: String
)

private val cosmologyApps = listOf(
    CosmologyApp("dark_energy", "Dark Energy", "Omega Lambda = 68.9%",
        Icons.Filled.DarkMode, Color(0xFF6366F1), "0.689", "0.685 +/- 0.007"),
    CosmologyApp("dark_matter", "Dark Matter", "Omega M = 31.1%",
        Icons.Filled.Visibility, Color(0xFF8B5CF6), "0.311", "0.315 +/- 0.007"),
    CosmologyApp("hubble", "Hubble Constant", "H0 from Brahim numbers",
        Icons.Filled.Speed, Color(0xFFEC4899), "67.4", "67.4 +/- 0.5 km/s/Mpc"),
    CosmologyApp("cmb", "CMB Temperature", "T = 2.725 K",
        Icons.Filled.Thermostat, Color(0xFF14B8A6), "2.725", "2.72548 +/- 0.00057 K"),
    CosmologyApp("timeline", "Cosmic Timeline", "Age of universe",
        Icons.Filled.Timeline, Color(0xFFF59E0B), "13.8 Gyr", "13.787 +/- 0.020 Gyr")
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CosmologyHubScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedApp by remember { mutableStateOf<CosmologyApp?>(null) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Cosmology", fontWeight = FontWeight.Bold) },
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
            item { CosmologyHeaderCard() }

            item {
                Text("Cosmological Parameters", style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold)
            }

            items(cosmologyApps) { app ->
                CosmologyAppCard(app, selectedApp == app) {
                    selectedApp = if (selectedApp == app) null else app
                }
            }

            item { UniverseCompositionCard() }
            item { BrahimCosmologyCard() }
        }
    }
}

@Composable
private fun CosmologyHeaderCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.horizontalGradient(
                        listOf(Color(0xFF1F2937), Color(0xFF374151))
                    )
                )
                .padding(20.dp)
        ) {
            Column {
                Text("Brahim Cosmology", style = MaterialTheme.typography.titleLarge,
                    color = Color.White, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text("Dark energy and matter fractions derived from golden ratio hierarchy",
                    style = MaterialTheme.typography.bodyMedium, color = Color.White.copy(alpha = 0.9f))
                Spacer(Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(24.dp)) {
                    CosmologyStatBadge("68.9%", "Dark Energy", Color(0xFF6366F1))
                    CosmologyStatBadge("26.6%", "Dark Matter", Color(0xFF8B5CF6))
                    CosmologyStatBadge("4.5%", "Baryonic", Color(0xFFD4AF37))
                }
            }
        }
    }
}

@Composable
private fun CosmologyStatBadge(value: String, label: String, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, style = MaterialTheme.typography.titleMedium,
            color = color, fontWeight = FontWeight.Bold)
        Text(label, style = MaterialTheme.typography.labelSmall,
            color = Color.White.copy(alpha = 0.7f))
    }
}

@Composable
private fun CosmologyAppCard(app: CosmologyApp, isSelected: Boolean, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) app.color.copy(alpha = 0.15f)
            else MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = app.color.copy(alpha = 0.2f),
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
                Text(app.value, style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold, color = app.color)
            }

            if (isSelected) {
                Spacer(Modifier.height(12.dp))
                HorizontalDivider()
                Spacer(Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("CODATA/Planck:", style = MaterialTheme.typography.bodySmall)
                    Text(app.codata, style = MaterialTheme.typography.bodySmall,
                        fontFamily = FontFamily.Monospace)
                }
            }
        }
    }
}

@Composable
private fun UniverseCompositionCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Universe Composition", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(16.dp))

            // Visual bar
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(24.dp)
            ) {
                Box(
                    modifier = Modifier
                        .weight(0.689f)
                        .fillMaxHeight()
                        .background(Color(0xFF6366F1), RoundedCornerShape(topStart = 8.dp, bottomStart = 8.dp))
                )
                Box(
                    modifier = Modifier
                        .weight(0.266f)
                        .fillMaxHeight()
                        .background(Color(0xFF8B5CF6))
                )
                Box(
                    modifier = Modifier
                        .weight(0.045f)
                        .fillMaxHeight()
                        .background(Color(0xFFD4AF37), RoundedCornerShape(topEnd = 8.dp, bottomEnd = 8.dp))
                )
            }

            Spacer(Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                CompositionLabel("Dark Energy", "68.9%", Color(0xFF6366F1))
                CompositionLabel("Dark Matter", "26.6%", Color(0xFF8B5CF6))
                CompositionLabel("Baryonic", "4.5%", Color(0xFFD4AF37))
            }
        }
    }
}

@Composable
private fun CompositionLabel(name: String, value: String, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(
            modifier = Modifier
                .size(12.dp)
                .background(color, RoundedCornerShape(2.dp))
        )
        Spacer(Modifier.width(4.dp))
        Column {
            Text(name, style = MaterialTheme.typography.labelSmall)
            Text(value, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun BrahimCosmologyCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = GoldenPrimary.copy(alpha = 0.1f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Brahim Derivation", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold, color = GoldenPrimary)
            Spacer(Modifier.height(12.dp))

            Text("Dark Energy: Omega_Lambda = 31/45 = 0.689",
                style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace)
            Text("Matter Ratio: phi^5 / 200 = 0.045 (baryonic)",
                style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace)
            Text("Genesis Constant: beta / 107 = 0.00221",
                style = MaterialTheme.typography.bodySmall, fontFamily = FontFamily.Monospace)

            Spacer(Modifier.height(8.dp))
            Text("All derived from phi = 1.618... and beta = sqrt(5) - 2",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
