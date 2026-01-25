/**
 * Physics Screen - Brahim Calculator Interface
 * =============================================
 *
 * Interface for physics constant calculations.
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.physics.BrahimCalculator
import com.brahim.buim.physics.PhysicsResult
import com.brahim.buim.ui.theme.GoldenPrimary
import kotlin.math.abs

/**
 * Physics screen composable.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PhysicsScreen(
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val physicsResults = remember { BrahimCalculator.getAllConstants() }
    val sequenceInfo = remember { BrahimCalculator.getSequence() }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Physics Calculator") },
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
            // Brahim Sequence header
            item {
                BrahimSequenceCard()
            }

            // Section header
            item {
                Text(
                    text = "Derived Constants",
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)
                )
            }

            // Physics constants
            items(physicsResults) { result ->
                PhysicsResultCard(result = result)
            }

            // Yang-Mills section
            item {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Yang-Mills Mass Gap",
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(bottom = 4.dp)
                )
                YangMillsCard()
            }

            // Cosmology section
            item {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Cosmology",
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(bottom = 4.dp)
                )
                CosmologyCard()
            }
        }
    }
}

/**
 * Brahim sequence display card.
 */
@Composable
private fun BrahimSequenceCard(
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
                text = "Brahim Sequence",
                style = MaterialTheme.typography.titleSmall
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Sequence display
            Text(
                text = "B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}",
                style = MaterialTheme.typography.bodyMedium,
                fontFamily = FontFamily.Monospace
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Key values
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "214",
                        style = MaterialTheme.typography.titleMedium,
                        color = GoldenPrimary
                    )
                    Text(
                        text = "Sum (S)",
                        style = MaterialTheme.typography.labelSmall
                    )
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "107",
                        style = MaterialTheme.typography.titleMedium,
                        color = GoldenPrimary
                    )
                    Text(
                        text = "Center (C)",
                        style = MaterialTheme.typography.labelSmall
                    )
                }
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = "1.618",
                        style = MaterialTheme.typography.titleMedium,
                        color = GoldenPrimary
                    )
                    Text(
                        text = "φ (phi)",
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Mirror property
            Text(
                text = "Mirror Property: α + ω = 214",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Physics result card.
 */
@Composable
private fun PhysicsResultCard(
    result: PhysicsResult,
    modifier: Modifier = Modifier
) {
    val errorPercent = abs(result.value - result.codataValue) / result.codataValue * 100

    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = result.name,
                        style = MaterialTheme.typography.titleSmall
                    )
                    Text(
                        text = result.symbol,
                        style = MaterialTheme.typography.bodyMedium,
                        fontFamily = FontFamily.Monospace,
                        color = GoldenPrimary
                    )
                }

                // Accuracy badge
                Surface(
                    shape = RoundedCornerShape(4.dp),
                    color = when {
                        errorPercent < 0.1 -> MaterialTheme.colorScheme.primaryContainer
                        errorPercent < 1.0 -> MaterialTheme.colorScheme.secondaryContainer
                        else -> MaterialTheme.colorScheme.tertiaryContainer
                    }
                ) {
                    Text(
                        text = result.accuracy,
                        style = MaterialTheme.typography.labelSmall,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Values comparison
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = "Calculated",
                        style = MaterialTheme.typography.labelSmall
                    )
                    Text(
                        text = "%.6f".format(result.value),
                        style = MaterialTheme.typography.bodyMedium,
                        fontFamily = FontFamily.Monospace
                    )
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "CODATA",
                        style = MaterialTheme.typography.labelSmall
                    )
                    Text(
                        text = "%.6f".format(result.codataValue),
                        style = MaterialTheme.typography.bodyMedium,
                        fontFamily = FontFamily.Monospace
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Formula
            Text(
                text = "Formula: ${result.formula}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            // Derivation
            Text(
                text = result.derivation,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
            )
        }
    }
}

/**
 * Yang-Mills mass gap card.
 */
@Composable
private fun YangMillsCard(
    modifier: Modifier = Modifier
) {
    val yangMills = remember { BrahimCalculator.yangMillsMassGap() }

    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(text = "Mass Gap (Δ)", style = MaterialTheme.typography.labelSmall)
                    Text(
                        text = "${yangMills.massGap.toInt()} MeV",
                        style = MaterialTheme.typography.titleMedium,
                        color = GoldenPrimary
                    )
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text(text = "λ_QCD", style = MaterialTheme.typography.labelSmall)
                    Text(
                        text = "%.1f MeV".format(yangMills.lambdaQCD),
                        style = MaterialTheme.typography.titleMedium
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Derivation steps
            yangMills.derivationChain.take(3).forEach { step ->
                Text(
                    text = step,
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

/**
 * Cosmology fractions card.
 */
@Composable
private fun CosmologyCard(
    modifier: Modifier = Modifier
) {
    val cosmology = remember { BrahimCalculator.cosmicFractions() }

    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                FractionItem(
                    label = "Dark Energy",
                    value = cosmology.darkEnergyFraction,
                    color = MaterialTheme.colorScheme.primary
                )
                FractionItem(
                    label = "Dark Matter",
                    value = cosmology.darkMatterFraction,
                    color = MaterialTheme.colorScheme.secondary
                )
                FractionItem(
                    label = "Normal Matter",
                    value = cosmology.normalMatterFraction,
                    color = MaterialTheme.colorScheme.tertiary
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Hubble constant
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center
            ) {
                Text(text = "H₀ = ", style = MaterialTheme.typography.bodyMedium)
                Text(
                    text = "%.1f km/s/Mpc".format(cosmology.hubbleConstant),
                    style = MaterialTheme.typography.bodyMedium,
                    color = GoldenPrimary
                )
            }
        }
    }
}

@Composable
private fun FractionItem(
    label: String,
    value: Double,
    color: androidx.compose.ui.graphics.Color
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = "%.1f%%".format(value * 100),
            style = MaterialTheme.typography.titleMedium,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall
        )
    }
}
