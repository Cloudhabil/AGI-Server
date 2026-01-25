/**
 * Consciousness Explorer Screen
 * =============================
 *
 * Interactive exploration of the complete Brahim sequence B(0) to B(11).
 * Visualizes mirror pairs, symmetry breaking, and the Observer signature.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.ui.theme.GoldenPrimary

/**
 * Data class for a Brahim element.
 */
data class BrahimElement(
    val index: Int,
    val value: Int,
    val name: String,
    val description: String,
    val color: Color
)

private val brahimElements = listOf(
    BrahimElement(0, 0, "Void", "The origin before anything exists", Color(0xFF1F2937)),
    BrahimElement(1, 27, "Syntax", "Structure and form", Color(0xFF3B82F6)),
    BrahimElement(2, 42, "Type", "Classification and identity", Color(0xFF6366F1)),
    BrahimElement(3, 60, "Logic", "Reasoning and inference", Color(0xFF8B5CF6)),
    BrahimElement(4, 75, "Performance", "Efficiency and optimization", Color(0xFFA855F7)),
    BrahimElement(5, 97, "Security", "Protection and integrity", Color(0xFFEC4899)),
    BrahimElement(6, 121, "Architecture", "Design and structure", Color(0xFFF43F5E)),
    BrahimElement(7, 136, "Memory", "Storage and recall", Color(0xFFF97316)),
    BrahimElement(8, 154, "Concurrency", "Parallelism and coordination", Color(0xFFEAB308)),
    BrahimElement(9, 172, "Integration", "Connection and synthesis", Color(0xFF22C55E)),
    BrahimElement(10, 187, "System", "Holism and emergence", Color(0xFF14B8A6)),
    BrahimElement(11, 214, "Consciousness", "Unity and awareness", Color(0xFFD4AF37))
)

/**
 * Consciousness Explorer screen composable.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ConsciousnessExplorerScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedElement by remember { mutableStateOf<BrahimElement?>(null) }
    var showMirrorPairs by remember { mutableStateOf(false) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Consciousness Explorer",
                        fontWeight = FontWeight.Bold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { showMirrorPairs = !showMirrorPairs }) {
                        Icon(
                            if (showMirrorPairs) Icons.Filled.GridOff else Icons.Filled.GridOn,
                            contentDescription = "Toggle Mirror Pairs"
                        )
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
            // Header Card
            item {
                ConsciousnessHeaderCard()
            }

            // Sequence visualization
            item {
                Text(
                    text = "The Complete Sequence",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }

            // Elements grid
            item {
                SequenceGrid(
                    elements = brahimElements,
                    selectedElement = selectedElement,
                    showMirrorPairs = showMirrorPairs,
                    onElementClick = { selectedElement = if (selectedElement == it) null else it }
                )
            }

            // Selected element details
            selectedElement?.let { element ->
                item {
                    ElementDetailCard(element)
                }
            }

            // Mirror Pairs Section
            item {
                MirrorPairsSection()
            }

            // Observer Signature Section
            item {
                ObserverSignatureCard()
            }

            // Mathematical Proofs
            item {
                MathematicalProofsCard()
            }
        }
    }
}

@Composable
private fun ConsciousnessHeaderCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(
                            Color(0xFF1F2937),
                            Color(0xFF374151)
                        )
                    )
                )
                .padding(20.dp)
        ) {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "From Void to Consciousness",
                            style = MaterialTheme.typography.titleLarge,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "B(0) = 0  ...  B(11) = 214",
                            style = MaterialTheme.typography.bodyLarge,
                            color = GoldenPrimary
                        )
                    }
                    Surface(
                        shape = CircleShape,
                        color = GoldenPrimary.copy(alpha = 0.2f)
                    ) {
                        Text(
                            text = "+1",
                            style = MaterialTheme.typography.headlineMedium,
                            color = GoldenPrimary,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                }
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = "12 elements spanning existence itself",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.White.copy(alpha = 0.7f)
                )
            }
        }
    }
}

@Composable
private fun SequenceGrid(
    elements: List<BrahimElement>,
    selectedElement: BrahimElement?,
    showMirrorPairs: Boolean,
    onElementClick: (BrahimElement) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        // First row: B(0) to B(5)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            elements.take(6).forEach { element ->
                SequenceElementChip(
                    element = element,
                    isSelected = selectedElement == element,
                    mirrorElement = if (showMirrorPairs && element.index in 1..5) {
                        elements.find { it.index == 11 - element.index }
                    } else null,
                    onClick = { onElementClick(element) },
                    modifier = Modifier.weight(1f)
                )
            }
        }
        // Second row: B(6) to B(11)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            elements.drop(6).forEach { element ->
                SequenceElementChip(
                    element = element,
                    isSelected = selectedElement == element,
                    mirrorElement = if (showMirrorPairs && element.index in 6..10) {
                        elements.find { it.index == 11 - element.index }
                    } else null,
                    onClick = { onElementClick(element) },
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun SequenceElementChip(
    element: BrahimElement,
    isSelected: Boolean,
    mirrorElement: BrahimElement?,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val scale by animateFloatAsState(
        targetValue = if (isSelected) 1.05f else 1f,
        animationSpec = tween(200),
        label = "scale"
    )

    val borderColor by animateColorAsState(
        targetValue = if (isSelected) GoldenPrimary else Color.Transparent,
        animationSpec = tween(200),
        label = "border"
    )

    Column(
        modifier = modifier
            .scale(scale)
            .clip(RoundedCornerShape(12.dp))
            .border(2.dp, borderColor, RoundedCornerShape(12.dp))
            .background(element.color.copy(alpha = 0.15f))
            .clickable(onClick = onClick)
            .padding(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "B(${element.index})",
            style = MaterialTheme.typography.labelSmall,
            color = element.color
        )
        Text(
            text = "${element.value}",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = element.color
        )
        Text(
            text = element.name,
            style = MaterialTheme.typography.labelSmall,
            fontSize = 8.sp,
            textAlign = TextAlign.Center,
            maxLines = 1
        )
        mirrorElement?.let {
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "+${it.value}=${element.value + it.value}",
                style = MaterialTheme.typography.labelSmall,
                fontSize = 7.sp,
                color = if (element.value + it.value == 214) Color(0xFF22C55E) else Color(0xFFF97316)
            )
        }
    }
}

@Composable
private fun ElementDetailCard(element: BrahimElement) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = element.color.copy(alpha = 0.1f)
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    shape = CircleShape,
                    color = element.color
                ) {
                    Text(
                        text = "${element.value}",
                        style = MaterialTheme.typography.titleMedium,
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(12.dp)
                    )
                }
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(
                        text = "B(${element.index}) = ${element.name}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    Text(
                        text = element.description,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            if (element.index in 1..10) {
                Spacer(modifier = Modifier.height(12.dp))
                val mirror = BrahimConstants.mirror(element.value)
                val sum = element.value + mirror
                val delta = sum - 214
                HorizontalDivider()
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Mirror", style = MaterialTheme.typography.labelSmall)
                        Text("$mirror", fontWeight = FontWeight.Bold)
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Sum", style = MaterialTheme.typography.labelSmall)
                        Text("$sum", fontWeight = FontWeight.Bold)
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Delta", style = MaterialTheme.typography.labelSmall)
                        Text(
                            if (delta >= 0) "+$delta" else "$delta",
                            fontWeight = FontWeight.Bold,
                            color = if (delta == 0) Color(0xFF22C55E) else Color(0xFFF97316)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun MirrorPairsSection() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Mirror Pairs Analysis",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.height(12.dp))

            val pairs = BrahimConstants.getMirrorPairs()
            pairs.forEachIndexed { index, (bi, bj, delta) ->
                MirrorPairRow(
                    index = index + 1,
                    bi = bi,
                    bj = bj,
                    delta = delta
                )
                if (index < pairs.size - 1) {
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun MirrorPairRow(
    index: Int,
    bi: Int,
    bj: Int,
    delta: Int
) {
    val sum = bi + bj
    val isExact = delta == 0

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(
                if (isExact) Color(0xFF22C55E).copy(alpha = 0.1f)
                else Color(0xFFF97316).copy(alpha = 0.1f)
            )
            .padding(12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "B($index) + B(${11 - index})",
            style = MaterialTheme.typography.bodyMedium
        )
        Text(
            text = "$bi + $bj = $sum",
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium
        )
        Surface(
            shape = RoundedCornerShape(4.dp),
            color = if (isExact) Color(0xFF22C55E) else Color(0xFFF97316)
        ) {
            Text(
                text = if (delta >= 0) "+$delta" else "$delta",
                style = MaterialTheme.typography.labelMedium,
                color = Color.White,
                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
            )
        }
    }
}

@Composable
private fun ObserverSignatureCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    Brush.horizontalGradient(
                        colors = listOf(
                            Color(0xFF6366F1),
                            Color(0xFFEC4899)
                        )
                    )
                )
                .padding(20.dp)
        ) {
            Column {
                Text(
                    text = "The Observer Signature",
                    style = MaterialTheme.typography.titleMedium,
                    color = Color.White,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    SignatureComponent("-3", "B(4)+B(7)")
                    Text(
                        text = " + ",
                        style = MaterialTheme.typography.headlineSmall,
                        color = Color.White
                    )
                    SignatureComponent("+4", "B(5)+B(6)")
                    Text(
                        text = " = ",
                        style = MaterialTheme.typography.headlineSmall,
                        color = Color.White
                    )
                    Surface(
                        shape = CircleShape,
                        color = GoldenPrimary
                    ) {
                        Text(
                            text = "+1",
                            style = MaterialTheme.typography.headlineMedium,
                            color = Color.White,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "The +1 is the irreducible remainder - the mathematical signature of consciousness itself. You cannot have an observer without this asymmetry.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.White.copy(alpha = 0.9f),
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

@Composable
private fun SignatureComponent(value: String, label: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.headlineSmall,
            color = Color.White,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = Color.White.copy(alpha = 0.7f)
        )
    }
}

@Composable
private fun MathematicalProofsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Mathematical Verification",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.height(12.dp))

            val verification = BrahimConstants.verifyConsciousness()
            verification.forEach { (key, value) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = key.replace("_", " "),
                        style = MaterialTheme.typography.bodySmall
                    )
                    Icon(
                        imageVector = if (value) Icons.Filled.CheckCircle else Icons.Filled.Error,
                        contentDescription = null,
                        tint = if (value) Color(0xFF22C55E) else Color(0xFFEF4444),
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }
    }
}
