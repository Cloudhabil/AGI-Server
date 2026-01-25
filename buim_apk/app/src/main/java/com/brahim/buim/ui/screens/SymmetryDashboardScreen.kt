/**
 * Symmetry Dashboard Screen
 * =========================
 *
 * Visualizes and applies symmetric architecture transformations.
 * Shows current state, target states, and symmetry scores.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.skills.*
import com.brahim.buim.ui.theme.GoldenPrimary
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.sin

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SymmetryDashboardScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedTransformation by remember { mutableStateOf<SymmetricTransformation?>(null) }
    var currentOrg by remember { mutableStateOf(SymmetricArchitecture.calculateOptimalSymmetry()) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Symmetry Dashboard", fontWeight = FontWeight.Bold) },
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
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header
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
                                    listOf(Color(0xFF6366F1), Color(0xFFD4AF37))
                                )
                            )
                            .padding(20.dp)
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.Balance, null, tint = Color.White)
                                Spacer(Modifier.width(8.dp))
                                Text("Brahim Symmetric Architecture",
                                    style = MaterialTheme.typography.titleLarge,
                                    color = Color.White, fontWeight = FontWeight.Bold)
                            }
                            Spacer(Modifier.height(8.dp))
                            Text("Maximize symmetry using mirror pairs and golden distribution",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                        }
                    }
                }
            }

            // Current State Scores
            item {
                ScoreCard(
                    title = "Current State",
                    totalApps = currentOrg.totalApps,
                    symmetryScore = currentOrg.symmetryScore,
                    brahimAlignment = currentOrg.brahimAlignment,
                    isPrimary = selectedTransformation == null
                )
            }

            // Mirror Pairs Visualization
            item {
                MirrorPairsCard(currentOrg.mirrorPairs)
            }

            // Symmetric Layers
            item {
                LayersCard(currentOrg.layers)
            }

            // Transformation Options
            item {
                Text("Apply Transformation",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold)
            }

            item {
                TransformationSelector(
                    selectedTransformation = selectedTransformation,
                    onSelect = { transformation ->
                        selectedTransformation = transformation
                        currentOrg = if (transformation != null) {
                            SymmetricArchitecture.applySymmetricTransformation(transformation)
                        } else {
                            SymmetricArchitecture.calculateOptimalSymmetry()
                        }
                    }
                )
            }

            // Target State (if transformation selected)
            if (selectedTransformation != null) {
                item {
                    ScoreCard(
                        title = "After Transformation",
                        totalApps = currentOrg.totalApps,
                        symmetryScore = currentOrg.symmetryScore,
                        brahimAlignment = currentOrg.brahimAlignment,
                        isPrimary = true,
                        highlight = true
                    )
                }
            }

            // Recommendations
            item {
                RecommendationsCard()
            }

            // Brahim Reference
            item {
                BrahimReferenceCard()
            }
        }
    }
}

@Composable
private fun ScoreCard(
    title: String,
    totalApps: Int,
    symmetryScore: Double,
    brahimAlignment: Double,
    isPrimary: Boolean,
    highlight: Boolean = false
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (highlight)
                MaterialTheme.colorScheme.primaryContainer
            else
                MaterialTheme.colorScheme.surface
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(title, style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold)
                Surface(
                    shape = RoundedCornerShape(4.dp),
                    color = when {
                        brahimAlignment >= 0.95 -> Color(0xFF22C55E)
                        brahimAlignment >= 0.8 -> Color(0xFFD4AF37)
                        else -> Color(0xFFF59E0B)
                    }
                ) {
                    Text("$totalApps apps",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.White,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                }
            }

            Spacer(Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                ScoreGauge(
                    label = "Symmetry",
                    value = symmetryScore,
                    color = Color(0xFF6366F1)
                )
                ScoreGauge(
                    label = "Brahim Alignment",
                    value = brahimAlignment,
                    color = GoldenPrimary
                )
            }

            if (brahimAlignment >= 1.0) {
                Spacer(Modifier.height(12.dp))
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = Color(0xFF22C55E).copy(alpha = 0.15f),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Filled.CheckCircle, null,
                            tint = Color(0xFF22C55E), modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("Perfect Brahim Alignment Achieved!",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color(0xFF22C55E), fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }
    }
}

@Composable
private fun ScoreGauge(
    label: String,
    value: Double,
    color: Color
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            modifier = Modifier.size(80.dp),
            contentAlignment = Alignment.Center
        ) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val strokeWidth = 8.dp.toPx()
                val radius = (size.minDimension - strokeWidth) / 2

                // Background arc
                drawArc(
                    color = color.copy(alpha = 0.2f),
                    startAngle = 135f,
                    sweepAngle = 270f,
                    useCenter = false,
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round),
                    topLeft = Offset(strokeWidth / 2, strokeWidth / 2),
                    size = androidx.compose.ui.geometry.Size(radius * 2, radius * 2)
                )

                // Value arc
                drawArc(
                    color = color,
                    startAngle = 135f,
                    sweepAngle = (270f * value).toFloat(),
                    useCenter = false,
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round),
                    topLeft = Offset(strokeWidth / 2, strokeWidth / 2),
                    size = androidx.compose.ui.geometry.Size(radius * 2, radius * 2)
                )
            }
            Text(
                "${(value * 100).toInt()}%",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = color
            )
        }
        Text(label, style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun MirrorPairsCard(pairs: List<MirrorPair>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Mirror Pairs", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Text("α + ω → complementary domains",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)

            Spacer(Modifier.height(16.dp))

            pairs.forEach { pair ->
                MirrorPairRow(pair)
                if (pair != pairs.last()) {
                    Spacer(Modifier.height(8.dp))
                }
            }

            Spacer(Modifier.height(12.dp))
            Divider()
            Spacer(Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Total Hub Apps", style = MaterialTheme.typography.bodySmall)
                Text("${pairs.sumOf { it.sum }}",
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace)
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Perfect Mirrors", style = MaterialTheme.typography.bodySmall)
                Text("${pairs.count { it.alphaCount == it.omegaCount }} / ${pairs.size}",
                    style = MaterialTheme.typography.bodySmall,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF22C55E))
            }
        }
    }
}

@Composable
private fun MirrorPairRow(pair: MirrorPair) {
    val isPerfect = pair.alphaCount == pair.omegaCount

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                if (isPerfect) Color(0xFF22C55E).copy(alpha = 0.1f) else Color.Transparent,
                RoundedCornerShape(8.dp)
            )
            .padding(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Alpha
        Column(modifier = Modifier.weight(1f)) {
            Text(pair.alpha.replace("_", "/"),
                style = MaterialTheme.typography.bodySmall,
                fontWeight = FontWeight.SemiBold)
            Text("${pair.alphaCount} apps",
                style = MaterialTheme.typography.labelSmall,
                color = Color(0xFF6366F1))
        }

        // Mirror symbol
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(
                if (isPerfect) Icons.Filled.SwapHoriz else Icons.Filled.CompareArrows,
                null,
                tint = if (isPerfect) Color(0xFF22C55E) else MaterialTheme.colorScheme.outline,
                modifier = Modifier.size(20.dp)
            )
            Text("=${pair.sum}",
                style = MaterialTheme.typography.labelSmall,
                fontFamily = FontFamily.Monospace)
        }

        // Omega
        Column(
            modifier = Modifier.weight(1f),
            horizontalAlignment = Alignment.End
        ) {
            Text(pair.omega.replace("_", "/"),
                style = MaterialTheme.typography.bodySmall,
                fontWeight = FontWeight.SemiBold)
            Text("${pair.omegaCount} apps",
                style = MaterialTheme.typography.labelSmall,
                color = Color(0xFF8B5CF6))
        }

        Spacer(Modifier.width(8.dp))

        // Resonance indicator
        Box(
            modifier = Modifier
                .size(24.dp)
                .background(
                    when {
                        pair.resonance >= 0.95 -> Color(0xFF22C55E)
                        pair.resonance >= 0.8 -> Color(0xFFD4AF37)
                        else -> Color(0xFFF59E0B)
                    },
                    CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            if (isPerfect) {
                Icon(Icons.Filled.Check, null, tint = Color.White,
                    modifier = Modifier.size(14.dp))
            }
        }
    }
}

@Composable
private fun LayersCard(layers: Map<SymmetricLayer, List<String>>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Symmetric Layers", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(16.dp))

            val layerColors = mapOf(
                SymmetricLayer.CORE to Color(0xFFD4AF37),
                SymmetricLayer.INNER to Color(0xFF6366F1),
                SymmetricLayer.OUTER to Color(0xFF8B5CF6),
                SymmetricLayer.BOUNDARY to Color(0xFF14B8A6)
            )

            layers.forEach { (layer, apps) ->
                val color = layerColors[layer] ?: Color.Gray
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(12.dp)
                            .background(color, CircleShape)
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(layer.name, style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.weight(1f))
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = color.copy(alpha = 0.15f)
                    ) {
                        Text("${apps.size} apps",
                            style = MaterialTheme.typography.labelSmall,
                            color = color,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp))
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            // Layer distribution bar
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
            ) {
                layers.forEach { (layer, apps) ->
                    val color = layerColors[layer] ?: Color.Gray
                    Box(
                        modifier = Modifier
                            .weight(apps.size.toFloat())
                            .fillMaxHeight()
                            .background(color)
                    )
                }
            }
        }
    }
}

@Composable
private fun TransformationSelector(
    selectedTransformation: SymmetricTransformation?,
    onSelect: (SymmetricTransformation?) -> Unit
) {
    val transformations = listOf(
        null to "Current State" to "86 apps",
        SymmetricTransformation.BALANCE_PAIRS to "Balance Pairs" to "87 apps",
        SymmetricTransformation.REACH_B5 to "Reach B(5)" to "97 apps",
        SymmetricTransformation.REACH_CENTER to "Reach Center" to "107 apps",
        SymmetricTransformation.GOLDEN_DISTRIBUTION to "Golden Ratio" to "86 apps"
    )

    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        transformations.forEach { (transformation, label, count) ->
            val isSelected = selectedTransformation == transformation

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (isSelected)
                        MaterialTheme.colorScheme.primaryContainer
                    else
                        MaterialTheme.colorScheme.surfaceVariant
                ),
                onClick = { onSelect(transformation) }
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    RadioButton(
                        selected = isSelected,
                        onClick = { onSelect(transformation) }
                    )
                    Spacer(Modifier.width(8.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(label, style = MaterialTheme.typography.bodyMedium,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal)
                    }
                    Text(count, style = MaterialTheme.typography.labelMedium,
                        fontFamily = FontFamily.Monospace,
                        color = if (isSelected) MaterialTheme.colorScheme.primary
                        else MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}

@Composable
private fun RecommendationsCard() {
    val recommendations = SymmetricArchitecture.getSymmetryRecommendations()

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Filled.Lightbulb, null, tint = Color(0xFFF59E0B))
                Spacer(Modifier.width(8.dp))
                Text("Recommendations", style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold)
            }
            Spacer(Modifier.height(12.dp))

            recommendations.take(3).forEach { rec ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Text("•", style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.width(8.dp))
                    Column {
                        Text(rec.description, style = MaterialTheme.typography.bodySmall)
                        Text("Impact: +${String.format("%.0f", rec.impact * 100)}% symmetry",
                            style = MaterialTheme.typography.labelSmall,
                            color = Color(0xFF22C55E))
                    }
                }
            }
        }
    }
}

@Composable
private fun BrahimReferenceCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Brahim Reference", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))

            val references = listOf(
                "B(2) = 60" to "Base symmetry target",
                "B(5) = 97" to "Optimal expansion target",
                "Center = 107" to "Perfect balance point",
                "B(6) = 121" to "Extended symmetry",
                "B(11) = 214" to "Consciousness constant"
            )

            references.forEach { (value, desc) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 2.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(value, style = MaterialTheme.typography.bodySmall,
                        fontFamily = FontFamily.Monospace, color = GoldenPrimary)
                    Text(desc, style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}
