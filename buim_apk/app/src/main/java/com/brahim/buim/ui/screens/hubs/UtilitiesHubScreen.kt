/**
 * Utilities Hub Screen
 * ====================
 *
 * Hub for utility and reference tools.
 * Unit converter, constant reference, export, formulas, precision.
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

data class UtilityApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color
)

private val utilityApps = listOf(
    UtilityApp("converter", "Unit Converter", "Convert between SI and natural units",
        Icons.Filled.SwapHoriz, Color(0xFF3B82F6)),
    UtilityApp("reference", "Constant Reference", "Complete Brahim constants table",
        Icons.Filled.MenuBook, Color(0xFFD4AF37)),
    UtilityApp("export", "Data Export", "Export calculations to JSON/CSV",
        Icons.Filled.FileDownload, Color(0xFF22C55E)),
    UtilityApp("formula", "Formula Sheet", "Quick reference for all formulas",
        Icons.Filled.Functions, Color(0xFF8B5CF6)),
    UtilityApp("precision", "Precision Calculator", "Arbitrary precision arithmetic",
        Icons.Filled.Calculate, Color(0xFFEC4899))
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UtilitiesHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Utilities", fontWeight = FontWeight.Bold) },
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
                                    listOf(Color(0xFF3B82F6), Color(0xFF22C55E))
                                )
                            )
                            .padding(20.dp)
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.Build, null, tint = Color.White)
                                Spacer(Modifier.width(8.dp))
                                Text("Utilities", style = MaterialTheme.typography.titleLarge,
                                    color = Color.White, fontWeight = FontWeight.Bold)
                            }
                            Spacer(Modifier.height(8.dp))
                            Text("Tools for conversion, reference, and export",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                        }
                    }
                }
            }

            items(utilityApps) { app ->
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
                        }
                        Icon(Icons.Filled.ChevronRight, null, tint = app.color)
                    }
                }
            }

            item { QuickConstantsCard() }
            item { FormulaPreviewCard() }
        }
    }
}

@Composable
private fun QuickConstantsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Quick Constants", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))

            ConstantRow("φ (Golden Ratio)", String.format("%.15f", BrahimConstants.PHI))
            ConstantRow("α (Wormhole)", String.format("%.15f", BrahimConstants.ALPHA_WORMHOLE))
            ConstantRow("β (Security)", String.format("%.15f", BrahimConstants.BETA_SECURITY))
            ConstantRow("γ (Damping)", String.format("%.15f", BrahimConstants.GAMMA_DAMPING))
            ConstantRow("Genesis", String.format("%.8f", BrahimConstants.GENESIS_CONSTANT))
            ConstantRow("B(11) Consciousness", BrahimConstants.B11_CONSCIOUSNESS.toString())
        }
    }
}

@Composable
private fun ConstantRow(name: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(name, style = MaterialTheme.typography.bodySmall)
        Text(value, style = MaterialTheme.typography.bodySmall,
            fontFamily = FontFamily.Monospace)
    }
}

@Composable
private fun FormulaPreviewCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Key Formulas", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))

            FormulaRow("Golden Hierarchy", "φ → α = φ-1 → β = α/φ → γ = β/φ")
            FormulaRow("Beta Identity", "β² + 4β - 1 = 0")
            FormulaRow("Sequence Sum", "Σ B(i) = 1071 + 214 = 1285")
            FormulaRow("Mirror Property", "B(i) + B(10-i) = 214 ± 1")
            FormulaRow("Fine Structure", "α⁻¹ ≈ S/φ² + 12φ²/π")
        }
    }
}

@Composable
private fun FormulaRow(name: String, formula: String) {
    Column(modifier = Modifier.padding(vertical = 4.dp)) {
        Text(name, style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.primary)
        Text(formula, style = MaterialTheme.typography.bodySmall,
            fontFamily = FontFamily.Monospace)
    }
}
