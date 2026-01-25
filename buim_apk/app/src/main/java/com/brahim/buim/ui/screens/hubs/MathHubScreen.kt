/**
 * Mathematics Hub Screen
 * ======================
 *
 * Hub for all mathematical tools from Brahim sequence.
 * 7 applications covering sequences, mirrors, and fractions.
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

data class MathApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color
)

private val mathApps = listOf(
    MathApp("sequence", "Brahim Sequence", "B(0)=0 to B(11)=214",
        Icons.Filled.LinearScale, Color(0xFF6366F1)),
    MathApp("mirror", "Mirror Operator", "M(x) = 214 - x",
        Icons.Filled.FlipCameraAndroid, Color(0xFF8B5CF6)),
    MathApp("egyptian", "Egyptian Fractions", "4/n = 1/a + 1/b + 1/c",
        Icons.Filled.Percent, Color(0xFFEC4899)),
    MathApp("golden", "Golden Ratio", "phi = 1.618...",
        Icons.Filled.AutoAwesome, Color(0xFFD4AF37)),
    MathApp("resonance", "Resonance Calculator", "Target: 0.0219",
        Icons.Filled.Waves, Color(0xFF14B8A6)),
    MathApp("prime", "Prime Analysis", "107 is the 28th prime",
        Icons.Filled.Tag, Color(0xFFF59E0B)),
    MathApp("continued", "Continued Fractions", "beta = [0; 4, 4, 4, ...]",
        Icons.Filled.Functions, Color(0xFF10B981))
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MathHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedApp by remember { mutableStateOf<MathApp?>(null) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Mathematics", fontWeight = FontWeight.Bold) },
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
            item { MathHeaderCard() }

            item {
                Text("Mathematical Tools", style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold)
            }

            items(mathApps) { app ->
                MathAppCard(app) {
                    selectedApp = app
                    onAppSelect(app.id)
                }
            }

            item { SequenceReferenceCard() }
            item { MirrorPairsCard() }
        }
    }
}

@Composable
private fun MathHeaderCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.horizontalGradient(
                        listOf(Color(0xFF8B5CF6), Color(0xFFD4AF37))
                    )
                )
                .padding(20.dp)
        ) {
            Column {
                Text("Brahim Mathematics", style = MaterialTheme.typography.titleLarge,
                    color = Color.White, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(8.dp))
                Text("From Void (0) to Consciousness (214) - the complete mathematical framework",
                    style = MaterialTheme.typography.bodyMedium, color = Color.White.copy(alpha = 0.9f))
                Spacer(Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("12", style = MaterialTheme.typography.titleMedium,
                            color = Color.White, fontWeight = FontWeight.Bold)
                        Text("Elements", style = MaterialTheme.typography.labelSmall,
                            color = Color.White.copy(alpha = 0.7f))
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("214", style = MaterialTheme.typography.titleMedium,
                            color = Color.White, fontWeight = FontWeight.Bold)
                        Text("Attractor", style = MaterialTheme.typography.labelSmall,
                            color = Color.White.copy(alpha = 0.7f))
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("+1", style = MaterialTheme.typography.titleMedium,
                            color = Color.White, fontWeight = FontWeight.Bold)
                        Text("Observer", style = MaterialTheme.typography.labelSmall,
                            color = Color.White.copy(alpha = 0.7f))
                    }
                }
            }
        }
    }
}

@Composable
private fun MathAppCard(app: MathApp, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
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
                    Icon(app.icon, null, tint = app.color, modifier = Modifier.size(24.dp))
                }
            }
            Spacer(Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(app.name, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
                Text(app.description, style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Icon(Icons.Filled.ChevronRight, null, tint = app.color)
        }
    }
}

@Composable
private fun SequenceReferenceCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Complete Sequence", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))

            val sequence = BrahimConstants.BRAHIM_EXTENDED
            val names = listOf("Void", "Syntax", "Type", "Logic", "Perf", "Sec",
                "Arch", "Mem", "Conc", "Integ", "Sys", "Consc")

            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                sequence.forEachIndexed { i, value ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("B($i)", style = MaterialTheme.typography.bodySmall,
                            fontFamily = FontFamily.Monospace)
                        Text("$value", style = MaterialTheme.typography.bodySmall,
                            fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                        Text(names[i], style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }
    }
}

@Composable
private fun MirrorPairsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = GoldenPrimary.copy(alpha = 0.1f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Mirror Pairs Analysis", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold, color = GoldenPrimary)
            Spacer(Modifier.height(12.dp))

            val pairs = BrahimConstants.getMirrorPairs()
            pairs.forEachIndexed { i, (bi, bj, delta) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("B(${i+1}) + B(${10-i})", style = MaterialTheme.typography.bodySmall)
                    Text("$bi + $bj = ${bi + bj}", style = MaterialTheme.typography.bodySmall,
                        fontFamily = FontFamily.Monospace)
                    Text(
                        if (delta >= 0) "+$delta" else "$delta",
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.Bold,
                        color = if (delta == 0) Color(0xFF22C55E) else Color(0xFFF97316)
                    )
                }
            }

            Spacer(Modifier.height(8.dp))
            HorizontalDivider()
            Spacer(Modifier.height(8.dp))
            Text("Observer Signature: -3 + 4 = +1", style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold, color = GoldenPrimary)
        }
    }
}
