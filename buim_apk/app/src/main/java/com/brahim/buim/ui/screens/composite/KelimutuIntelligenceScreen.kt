/**
 * Kelimutu Intelligence Screen
 * ============================
 *
 * Composite App: ML + Security + Business
 * Three-lake decision engine using Kelimutu routing.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens.composite

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants

/**
 * Lake classification result.
 */
data class LakeResult(
    val lake: String,
    val score: Float,
    val activation: String,
    val color: Color,
    val description: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KelimutuIntelligenceScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var query by remember { mutableStateOf("") }
    var isProcessing by remember { mutableStateOf(false) }
    var results by remember { mutableStateOf<List<LakeResult>?>(null) }
    var selectedLake by remember { mutableStateOf<String?>(null) }
    var safetyVerdict by remember { mutableStateOf("NOMINAL") }
    var riskScore by remember { mutableFloatStateOf(0f) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Kelimutu Intelligence", fontWeight = FontWeight.Bold) },
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
                                    listOf(Color(0xFF14B8A6), Color(0xFF1A4A6E), Color(0xFF8B4513))
                                )
                            )
                            .padding(20.dp)
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.Hub, null, tint = Color.White)
                                Spacer(Modifier.width(8.dp))
                                Text("Three Lakes, One Magma",
                                    style = MaterialTheme.typography.titleLarge,
                                    color = Color.White, fontWeight = FontWeight.Bold)
                            }
                            Spacer(Modifier.height(8.dp))
                            Text("Kelimutu Volcano (8.77°S, 121.82°E)",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                            Text("Note: 121.82 ≈ B(6) = 121 in Brahim sequence",
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.White.copy(alpha = 0.7f))
                        }
                    }
                }
            }

            // Query Input
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Decision Query", style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold)
                        Spacer(Modifier.height(12.dp))

                        OutlinedTextField(
                            value = query,
                            onValueChange = { query = it },
                            label = { Text("Enter your query or decision") },
                            modifier = Modifier.fillMaxWidth(),
                            minLines = 3,
                            maxLines = 5
                        )

                        Spacer(Modifier.height(12.dp))

                        Button(
                            onClick = {
                                isProcessing = true
                                // Simulate processing
                                results = simulateKelimutuRouting(query)
                                selectedLake = results?.maxByOrNull { it.score }?.lake
                                safetyVerdict = simulateSafetyCheck(query)
                                riskScore = simulateRiskAssessment(query)
                                isProcessing = false
                            },
                            modifier = Modifier.fillMaxWidth(),
                            enabled = query.isNotBlank() && !isProcessing,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFF14B8A6)
                            )
                        ) {
                            if (isProcessing) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(20.dp),
                                    color = Color.White,
                                    strokeWidth = 2.dp
                                )
                            } else {
                                Icon(Icons.Filled.Psychology, null)
                            }
                            Spacer(Modifier.width(8.dp))
                            Text("Route Through Lakes")
                        }
                    }
                }
            }

            // Three Lakes Display
            item {
                ThreeLakesCard(results = results, selectedLake = selectedLake)
            }

            // Results
            if (results != null) {
                // ASIOS Safety Check
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = when (safetyVerdict) {
                                "SAFE" -> Color(0xFF22C55E).copy(alpha = 0.15f)
                                "NOMINAL" -> Color(0xFF3B82F6).copy(alpha = 0.15f)
                                "CAUTION" -> Color(0xFFF59E0B).copy(alpha = 0.15f)
                                else -> Color(0xFFEF4444).copy(alpha = 0.15f)
                            }
                        )
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.Shield, null,
                                    tint = when (safetyVerdict) {
                                        "SAFE" -> Color(0xFF22C55E)
                                        "NOMINAL" -> Color(0xFF3B82F6)
                                        "CAUTION" -> Color(0xFFF59E0B)
                                        else -> Color(0xFFEF4444)
                                    })
                                Spacer(Modifier.width(8.dp))
                                Text("ASIOS Safety Verdict", style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.SemiBold)
                                Spacer(Modifier.weight(1f))
                                Surface(
                                    shape = RoundedCornerShape(4.dp),
                                    color = when (safetyVerdict) {
                                        "SAFE" -> Color(0xFF22C55E)
                                        "NOMINAL" -> Color(0xFF3B82F6)
                                        "CAUTION" -> Color(0xFFF59E0B)
                                        else -> Color(0xFFEF4444)
                                    }
                                ) {
                                    Text(safetyVerdict, style = MaterialTheme.typography.labelSmall,
                                        color = Color.White,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp))
                                }
                            }
                            Spacer(Modifier.height(8.dp))
                            Text("Berry-Keating Energy: ${String.format("%.6f", BrahimConstants.GENESIS_CONSTANT)}",
                                style = MaterialTheme.typography.bodySmall,
                                fontFamily = FontFamily.Monospace)
                        }
                    }
                }

                // Risk Assessment
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.Analytics, null, tint = Color(0xFFD4AF37))
                                Spacer(Modifier.width(8.dp))
                                Text("Risk Assessment", style = MaterialTheme.typography.titleSmall,
                                    fontWeight = FontWeight.SemiBold)
                            }
                            Spacer(Modifier.height(12.dp))

                            LinearProgressIndicator(
                                progress = { riskScore },
                                modifier = Modifier.fillMaxWidth(),
                                color = when {
                                    riskScore < 0.3f -> Color(0xFF22C55E)
                                    riskScore < 0.6f -> Color(0xFFF59E0B)
                                    else -> Color(0xFFEF4444)
                                },
                                trackColor = MaterialTheme.colorScheme.surfaceVariant
                            )

                            Spacer(Modifier.height(8.dp))
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text("Risk Level", style = MaterialTheme.typography.bodySmall)
                                Text("${String.format("%.1f", riskScore * 100)}%",
                                    style = MaterialTheme.typography.bodySmall,
                                    fontFamily = FontFamily.Monospace,
                                    color = when {
                                        riskScore < 0.3f -> Color(0xFF22C55E)
                                        riskScore < 0.6f -> Color(0xFFF59E0B)
                                        else -> Color(0xFFEF4444)
                                    })
                            }
                        }
                    }
                }

                // Decision Output
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.primaryContainer
                        )
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("Fused Decision", style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.SemiBold)
                            Spacer(Modifier.height(12.dp))

                            val winningLake = results?.maxByOrNull { it.score }
                            if (winningLake != null) {
                                Text("Primary Route: ${winningLake.lake}",
                                    style = MaterialTheme.typography.bodyMedium,
                                    fontWeight = FontWeight.SemiBold)
                                Text(winningLake.description,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                                Spacer(Modifier.height(8.dp))
                                Text("Activation: ${winningLake.activation}",
                                    style = MaterialTheme.typography.labelSmall,
                                    fontFamily = FontFamily.Monospace)
                                Text("Confidence: ${String.format("%.1f", winningLake.score * 100)}%",
                                    style = MaterialTheme.typography.labelSmall,
                                    fontFamily = FontFamily.Monospace)
                            }
                        }
                    }
                }
            }

            // Skills Used
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Skills Composed (Fusion Mode)",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold)
                        Spacer(Modifier.height(12.dp))

                        SkillRow("ML - Kelimutu Router", "Three-lake intent classification")
                        SkillRow("Security - ASIOS Guard", "Berry-Keating safety validation")
                        SkillRow("Business - Risk Assessment", "Portfolio risk analysis")
                    }
                }
            }
        }
    }
}

@Composable
private fun ThreeLakesCard(results: List<LakeResult>?, selectedLake: String?) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Three Lakes Classification", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(16.dp))

            val lakes = results ?: listOf(
                LakeResult("Tiwu Ata Mbupu", 0f, "sigmoid", Color(0xFF2E5A4D), "Old People - Literal interpretation"),
                LakeResult("Tiwu Nuwa Muri", 0f, "tanh", Color(0xFF1A4A6E), "Young Maidens - Semantic meaning"),
                LakeResult("Tiwu Ata Polo", 0f, "softplus", Color(0xFF8B4513), "Enchanted - Structural patterns")
            )

            lakes.forEach { lake ->
                LakeRow(
                    lake = lake,
                    isSelected = lake.lake == selectedLake
                )
                if (lake != lakes.last()) {
                    Spacer(Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun LakeRow(lake: LakeResult, isSelected: Boolean) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                if (isSelected) lake.color.copy(alpha = 0.15f) else Color.Transparent,
                RoundedCornerShape(8.dp)
            )
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(40.dp)
                .background(lake.color, CircleShape),
            contentAlignment = Alignment.Center
        ) {
            if (isSelected) {
                Icon(Icons.Filled.Check, null, tint = Color.White,
                    modifier = Modifier.size(20.dp))
            }
        }
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(lake.lake, style = MaterialTheme.typography.bodyMedium,
                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal)
            Text(lake.description, style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        Column(horizontalAlignment = Alignment.End) {
            Text(lake.activation, style = MaterialTheme.typography.labelSmall,
                color = lake.color, fontFamily = FontFamily.Monospace)
            if (lake.score > 0) {
                Text("${String.format("%.1f", lake.score * 100)}%",
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun SkillRow(skill: String, description: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(Icons.Filled.Check, null, tint = Color(0xFF14B8A6),
            modifier = Modifier.size(16.dp))
        Spacer(Modifier.width(8.dp))
        Column {
            Text(skill, style = MaterialTheme.typography.bodySmall,
                fontWeight = FontWeight.SemiBold)
            Text(description, style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

// Simulation functions
private fun simulateKelimutuRouting(query: String): List<LakeResult> {
    val words = query.lowercase().split(" ")
    val hasKeywords = words.any { it in listOf("how", "what", "calculate", "find") }
    val hasSemantic = words.any { it in listOf("meaning", "understand", "why", "explain") }
    val hasStructural = words.any { it in listOf("pattern", "structure", "organize", "plan") }

    val literalScore = if (hasKeywords) 0.6f + (Math.random() * 0.3f).toFloat() else (Math.random() * 0.4f).toFloat()
    val semanticScore = if (hasSemantic) 0.6f + (Math.random() * 0.3f).toFloat() else (Math.random() * 0.4f).toFloat()
    val structuralScore = if (hasStructural) 0.6f + (Math.random() * 0.3f).toFloat() else (Math.random() * 0.4f).toFloat()

    val total = literalScore + semanticScore + structuralScore

    return listOf(
        LakeResult("Tiwu Ata Mbupu", literalScore / total, "sigmoid", Color(0xFF2E5A4D), "Old People - Literal interpretation"),
        LakeResult("Tiwu Nuwa Muri", semanticScore / total, "tanh", Color(0xFF1A4A6E), "Young Maidens - Semantic meaning"),
        LakeResult("Tiwu Ata Polo", structuralScore / total, "softplus", Color(0xFF8B4513), "Enchanted - Structural patterns")
    )
}

private fun simulateSafetyCheck(query: String): String {
    val dangerWords = listOf("hack", "attack", "exploit", "bypass", "illegal")
    val hasDanger = query.lowercase().split(" ").any { it in dangerWords }
    return if (hasDanger) "CAUTION" else if (query.length > 50) "NOMINAL" else "SAFE"
}

private fun simulateRiskAssessment(query: String): Float {
    val riskWords = listOf("invest", "trade", "risk", "gamble", "uncertain")
    val riskCount = query.lowercase().split(" ").count { it in riskWords }
    return (riskCount * 0.2f + Math.random() * 0.2f).toFloat().coerceIn(0f, 1f)
}
