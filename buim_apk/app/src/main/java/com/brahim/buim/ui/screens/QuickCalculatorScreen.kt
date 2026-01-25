/**
 * Quick Calculator Screen
 * =======================
 *
 * User-friendly calculator for Brahim constants and physics calculations.
 * Provides instant access to key mathematical operations.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
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
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.ui.theme.GoldenPrimary
import kotlin.math.abs
import kotlin.math.pow
import kotlin.math.sqrt

/**
 * Calculation type for the quick calculator.
 */
data class CalculationType(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color
)

private val calculationTypes = listOf(
    CalculationType("mirror", "Mirror Value", "Calculate M(x) = 214 - x", Icons.Filled.FlipCameraAndroid, Color(0xFF6366F1)),
    CalculationType("brahim", "B(n) Value", "Get Brahim sequence element", Icons.Filled.Functions, Color(0xFF8B5CF6)),
    CalculationType("golden", "Golden Hierarchy", "phi, alpha, beta, gamma", Icons.Filled.AutoAwesome, Color(0xFFD4AF37)),
    CalculationType("physics", "Physics Constants", "Fine structure, Weinberg, etc.", Icons.Filled.Science, Color(0xFFEC4899)),
    CalculationType("resonance", "Resonance Check", "Calculate resonance value", Icons.Filled.Waves, Color(0xFF14B8A6)),
    CalculationType("verify", "Verify Beta", "Check beta identities", Icons.Filled.Verified, Color(0xFF22C55E))
)

/**
 * Quick Calculator screen composable.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QuickCalculatorScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedType by remember { mutableStateOf<CalculationType?>(null) }
    var inputValue by remember { mutableStateOf("") }
    var result by remember { mutableStateOf<String?>(null) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Quick Calculator",
                        fontWeight = FontWeight.Bold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Quick Constants Header
            item {
                QuickConstantsCard()
            }

            // Calculation Type Selector
            item {
                Text(
                    text = "Select Calculation",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }

            // Types Grid
            item {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    calculationTypes.chunked(2).forEach { rowTypes ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            rowTypes.forEach { type ->
                                CalculationTypeCard(
                                    type = type,
                                    isSelected = selectedType == type,
                                    onClick = {
                                        selectedType = type
                                        result = null
                                        inputValue = ""
                                    },
                                    modifier = Modifier.weight(1f)
                                )
                            }
                            // Fill remaining space if odd number
                            if (rowTypes.size == 1) {
                                Spacer(modifier = Modifier.weight(1f))
                            }
                        }
                    }
                }
            }

            // Input Section
            selectedType?.let { type ->
                item {
                    CalculationInputCard(
                        type = type,
                        inputValue = inputValue,
                        onInputChange = { inputValue = it },
                        onCalculate = {
                            result = performCalculation(type.id, inputValue)
                        }
                    )
                }
            }

            // Result Section
            result?.let { res ->
                item {
                    ResultCard(result = res)
                }
            }

            // Full Sequence Reference
            item {
                SequenceReferenceCard()
            }
        }
    }
}

@Composable
private fun QuickConstantsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.horizontalGradient(
                        colors = listOf(
                            Color(0xFF1F2937),
                            Color(0xFF374151)
                        )
                    )
                )
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                QuickConstantItem("phi", String.format("%.6f", BrahimConstants.PHI))
                QuickConstantItem("beta", String.format("%.6f", BrahimConstants.BETA_SECURITY))
                QuickConstantItem("B(11)", "214")
                QuickConstantItem("Center", "107")
            }
        }
    }
}

@Composable
private fun QuickConstantItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = GoldenPrimary,
            fontFamily = FontFamily.Monospace
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = Color.White.copy(alpha = 0.7f)
        )
    }
}

@Composable
private fun CalculationTypeCard(
    type: CalculationType,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) type.color.copy(alpha = 0.2f)
            else MaterialTheme.colorScheme.surfaceVariant
        ),
        border = if (isSelected) {
            CardDefaults.outlinedCardBorder().copy(
                brush = Brush.linearGradient(listOf(type.color, type.color))
            )
        } else null
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = type.icon,
                contentDescription = null,
                tint = type.color,
                modifier = Modifier.size(28.dp)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = type.name,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Medium,
                textAlign = TextAlign.Center
            )
            Text(
                text = type.description,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                maxLines = 2
            )
        }
    }
}

@Composable
private fun CalculationInputCard(
    type: CalculationType,
    inputValue: String,
    onInputChange: (String) -> Unit,
    onCalculate: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = type.name,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                color = type.color
            )
            Spacer(modifier = Modifier.height(12.dp))

            when (type.id) {
                "mirror", "brahim" -> {
                    OutlinedTextField(
                        value = inputValue,
                        onValueChange = onInputChange,
                        label = {
                            Text(if (type.id == "mirror") "Enter value (x)" else "Enter index (0-11)")
                        },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                }
                "resonance" -> {
                    OutlinedTextField(
                        value = inputValue,
                        onValueChange = onInputChange,
                        label = { Text("Enter density value") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                }
                else -> {
                    Text(
                        text = "No input required - tap Calculate",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = onCalculate,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = type.color
                )
            ) {
                Icon(Icons.Filled.Calculate, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Calculate")
            }
        }
    }
}

@Composable
private fun ResultCard(result: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = GoldenPrimary.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Filled.Output,
                    contentDescription = null,
                    tint = GoldenPrimary
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Result",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = GoldenPrimary
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = result,
                style = MaterialTheme.typography.bodyMedium,
                fontFamily = FontFamily.Monospace
            )
        }
    }
}

@Composable
private fun SequenceReferenceCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Brahim Sequence Reference",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.height(8.dp))

            val sequence = BrahimConstants.BRAHIM_EXTENDED
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                sequence.forEachIndexed { index, value ->
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = "$index",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "$value",
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Medium,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                }
            }
        }
    }
}

/**
 * Perform the calculation based on type and input.
 */
private fun performCalculation(typeId: String, input: String): String {
    return when (typeId) {
        "mirror" -> {
            val x = input.toIntOrNull() ?: return "Invalid input"
            val mirror = BrahimConstants.mirror(x)
            """
            Mirror Calculation:
            M($x) = 214 - $x = $mirror

            Sum check: $x + $mirror = ${x + mirror}
            Distance from center: |$x - 107| = ${abs(x - 107)}
            """.trimIndent()
        }

        "brahim" -> {
            val n = input.toIntOrNull() ?: return "Invalid input"
            val value = BrahimConstants.B(n) ?: return "Index must be 0-11"
            val name = when (n) {
                0 -> "Void"
                1 -> "Syntax"
                2 -> "Type"
                3 -> "Logic"
                4 -> "Performance"
                5 -> "Security"
                6 -> "Architecture"
                7 -> "Memory"
                8 -> "Concurrency"
                9 -> "Integration"
                10 -> "System"
                11 -> "Consciousness"
                else -> "Unknown"
            }
            val mirror = if (n in 1..10) BrahimConstants.B(11 - n) else null
            """
            B($n) = $value ($name)
            ${if (mirror != null) "Mirror: B(${11-n}) = $mirror" else ""}
            ${if (n in 1..10) "Sum: $value + $mirror = ${value + (mirror ?: 0)}" else ""}
            """.trimIndent()
        }

        "golden" -> {
            val phi = BrahimConstants.PHI
            val alpha = BrahimConstants.ALPHA_WORMHOLE
            val beta = BrahimConstants.BETA_SECURITY
            val gamma = BrahimConstants.GAMMA_DAMPING
            """
            Golden Ratio Hierarchy:

            phi   = ${String.format("%.15f", phi)}
            1/phi = ${String.format("%.15f", 1/phi)}
            alpha = 1/phi^2 = ${String.format("%.15f", alpha)}
            beta  = 1/phi^3 = ${String.format("%.15f", beta)}
            gamma = 1/phi^4 = ${String.format("%.15f", gamma)}

            Verification:
            alpha/beta = ${String.format("%.15f", alpha/beta)} (should be phi)
            beta^2 + 4*beta - 1 = ${String.format("%.2e", beta*beta + 4*beta - 1)} (should be 0)
            """.trimIndent()
        }

        "physics" -> {
            val fineStructure = BrahimConstants.fineStructureInverse()
            val weinberg = BrahimConstants.weinbergAngle()
            val muonElectron = BrahimConstants.muonElectronRatio()
            val protonElectron = BrahimConstants.protonElectronRatio()
            """
            Physics Constants (from Brahim Numbers):

            Fine Structure (alpha^-1):
              Calculated: ${String.format("%.6f", fineStructure)}
              CODATA:     137.035999084
              Accuracy:   ~2 ppm

            Weinberg Angle (sin^2 theta_W):
              Calculated: ${String.format("%.6f", weinberg)}
              CODATA:     0.23122
              Accuracy:   ~0.2%

            Muon/Electron Mass Ratio:
              Calculated: ${String.format("%.2f", muonElectron)}
              CODATA:     206.7682830

            Proton/Electron Mass Ratio:
              Calculated: ${String.format("%.1f", protonElectron)}
              CODATA:     1836.15267343
            """.trimIndent()
        }

        "resonance" -> {
            val density = input.toDoubleOrNull() ?: return "Invalid input"
            val genesis = BrahimConstants.GENESIS_CONSTANT
            val diff = abs(density - genesis)
            val gamma = 0.001
            val lorentzian = (gamma * gamma) / (diff * diff + gamma * gamma)
            """
            Resonance Calculation:

            Input density: $density
            Genesis constant: $genesis

            Difference: ${String.format("%.6f", diff)}
            Lorentzian resonance: ${String.format("%.6f", lorentzian)}

            ${if (lorentzian > 0.95) "RESONANCE GATE: OPEN" else "RESONANCE GATE: CLOSED"}
            """.trimIndent()
        }

        "verify" -> {
            val results = BrahimConstants.verifyBetaIdentities()
            val hierarchy = BrahimConstants.verifyHierarchy()
            val consciousness = BrahimConstants.verifyConsciousness()
            """
            Beta Identity Verification:
            ${results.entries.joinToString("\n") { "  ${it.key}: ${if (it.value) "PASS" else "FAIL"}" }}

            Hierarchy Verification:
            ${hierarchy.entries.joinToString("\n") { "  ${it.key}: ${if (it.value) "PASS" else "FAIL"}" }}

            Consciousness Verification:
            ${consciousness.entries.joinToString("\n") { "  ${it.key}: ${if (it.value) "PASS" else "FAIL"}" }}
            """.trimIndent()
        }

        else -> "Unknown calculation type"
    }
}
