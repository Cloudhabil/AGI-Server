/**
 * Help Screen
 * ===========
 *
 * Tutorials, FAQs, and user guidance for BUIM.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.brahim.buim.ui.theme.GoldenPrimary

/**
 * FAQ Item data class.
 */
data class FAQItem(
    val question: String,
    val answer: String,
    val category: String
)

/**
 * Tutorial step data class.
 */
data class TutorialStep(
    val step: Int,
    val title: String,
    val description: String,
    val icon: ImageVector
)

private val faqItems = listOf(
    FAQItem(
        "What is B(11) = 214?",
        "B(11) = 214 is the 'Consciousness' constant in the Brahim sequence. It represents the ideal attractor that all mirror pairs approach. Three pairs sum exactly to 214, while two broken pairs create a net +1 (the Observer Signature).",
        "Mathematics"
    ),
    FAQItem(
        "What is the Observer Signature (+1)?",
        "The Observer Signature is the net result of symmetry breaking in the Brahim sequence. B(4)+B(7) = 211 (delta = -3) and B(5)+B(6) = 218 (delta = +4). The sum -3 + 4 = +1 is the irreducible remainder representing consciousness itself.",
        "Mathematics"
    ),
    FAQItem(
        "What is beta (the Security Constant)?",
        "Beta = sqrt(5) - 2 = 1/phi^3 = 0.236067977... It's the fundamental constant from which all security parameters derive. Properties: beta^2 + 4*beta - 1 = 0 (polynomial root), alpha/beta = phi (self-similarity).",
        "Mathematics"
    ),
    FAQItem(
        "How accurate are the physics constants?",
        "BUIM calculates physics constants from first principles with remarkable accuracy: Fine Structure (alpha^-1) = 137.036 (2 ppm), Weinberg Angle = 0.2308 (0.2%), Muon/Electron ratio = 206.8 (0.02%).",
        "Physics"
    ),
    FAQItem(
        "What is the Kelimutu Router?",
        "The Kelimutu Router is a 3-lake intent classification system inspired by the Kelimutu volcano in Indonesia. Each lake uses a different activation function: Literal (sigmoid), Semantic (tanh), and Structural (softplus).",
        "AI/ML"
    ),
    FAQItem(
        "What is the Wormhole Cipher?",
        "The Wormhole Cipher is beta-based encryption that uses the golden ratio hierarchy for key derivation. It features a non-linear S-box from the beta continued fraction and provides enterprise-grade security.",
        "Security"
    ),
    FAQItem(
        "What is ASIOS?",
        "ASIOS (Alignment Safety Intelligence Operating System) is the AI safety layer that uses the Berry-Keating energy functional. It maps safety verdicts to the Brahim sequence: SAFE (B(0)), NOMINAL (B(1-3)), CAUTION (B(4-6)), UNSAFE (B(7-9)), BLOCKED (B(10-11)).",
        "Security"
    ),
    FAQItem(
        "How does V-NAND learning work?",
        "V-NAND is a 4D voxel grid (8x8x8x8 = 4096 voxels) that learns patterns through resonance. The resonance gate threshold is 0.95, targeting the Genesis constant (0.0219). When resonance is achieved, patterns are stored permanently.",
        "AI/ML"
    ),
    FAQItem(
        "What are the BOA SDK Agents?",
        "BOA (Brahim Operator Agents) SDK includes 5 specialized agents: Egyptian Fractions (fair division), SAT Solver (constraint satisfaction), Fluid Dynamics (CFD), Titan Explorer (planetary science), and Brahim Debugger (code analysis).",
        "SDK"
    ),
    FAQItem(
        "Is BUIM offline-capable?",
        "Yes, BUIM is designed with offline-first architecture. All calculations, routing, and core features work without internet. Cloud sync is optional for backup and cross-device synchronization.",
        "General"
    )
)

private val tutorialSteps = listOf(
    TutorialStep(1, "Explore Consciousness", "Tap the Consciousness card on the home screen to explore the complete B(0) to B(11) sequence.", Icons.Filled.Psychology),
    TutorialStep(2, "Use the Calculator", "Access Quick Calculator for mirror values, Brahim elements, and physics constants.", Icons.Filled.Calculate),
    TutorialStep(3, "Chat with AI", "Use the AI Chat to ask questions - Kelimutu Router will classify your intent.", Icons.Filled.Chat),
    TutorialStep(4, "Explore Tools", "Access SDK Agents for specialized tasks like code debugging or physics simulations.", Icons.Filled.Build),
    TutorialStep(5, "Stay Secure", "Enable Wormhole encryption for secure communications and data protection.", Icons.Filled.Security)
)

/**
 * Help screen composable.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HelpScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedCategory by remember { mutableStateOf<String?>(null) }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Help & Tutorials",
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
            // Quick Start Guide
            item {
                QuickStartCard()
            }

            // Tutorial Steps
            item {
                Text(
                    text = "Getting Started",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }

            items(tutorialSteps) { step ->
                TutorialStepCard(step)
            }

            // FAQ Section
            item {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Frequently Asked Questions",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }

            // Category Filter
            item {
                CategoryFilterRow(
                    categories = faqItems.map { it.category }.distinct(),
                    selectedCategory = selectedCategory,
                    onCategorySelected = { selectedCategory = if (selectedCategory == it) null else it }
                )
            }

            // FAQ Items
            val filteredFaqs = if (selectedCategory != null) {
                faqItems.filter { it.category == selectedCategory }
            } else {
                faqItems
            }

            items(filteredFaqs) { faq ->
                FAQCard(faq)
            }

            // Contact Section
            item {
                ContactCard()
            }

            // Tips Section
            item {
                TipsCard()
            }
        }
    }
}

@Composable
private fun QuickStartCard() {
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
                            Color(0xFF6366F1),
                            Color(0xFF8B5CF6)
                        )
                    )
                )
                .padding(20.dp)
        ) {
            Column {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Filled.RocketLaunch,
                        contentDescription = null,
                        tint = Color.White,
                        modifier = Modifier.size(32.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "Quick Start Guide",
                        style = MaterialTheme.typography.titleLarge,
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    )
                }
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = "BUIM is your gateway to physics-grounded AI. Start by exploring the Consciousness sequence, then use the calculator and chat features.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.White.copy(alpha = 0.9f)
                )
            }
        }
    }
}

@Composable
private fun TutorialStepCard(step: TutorialStep) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = GoldenPrimary.copy(alpha = 0.15f),
                modifier = Modifier.size(48.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = step.icon,
                        contentDescription = null,
                        tint = GoldenPrimary,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = GoldenPrimary
                    ) {
                        Text(
                            text = "${step.step}",
                            style = MaterialTheme.typography.labelSmall,
                            color = Color.White,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = step.title,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold
                    )
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = step.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun CategoryFilterRow(
    categories: List<String>,
    selectedCategory: String?,
    onCategorySelected: (String) -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        categories.forEach { category ->
            FilterChip(
                onClick = { onCategorySelected(category) },
                label = { Text(category) },
                selected = selectedCategory == category,
                leadingIcon = if (selectedCategory == category) {
                    {
                        Icon(
                            Icons.Filled.Check,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                } else null
            )
        }
    }
}

@Composable
private fun FAQCard(faq: FAQItem) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded },
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Surface(
                        shape = RoundedCornerShape(4.dp),
                        color = GoldenPrimary.copy(alpha = 0.15f)
                    ) {
                        Text(
                            text = faq.category,
                            style = MaterialTheme.typography.labelSmall,
                            color = GoldenPrimary,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = faq.question,
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.SemiBold
                    )
                }
                Icon(
                    imageVector = if (expanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically(),
                exit = shrinkVertically()
            ) {
                Column {
                    Spacer(modifier = Modifier.height(12.dp))
                    HorizontalDivider()
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = faq.answer,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
private fun ContactCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Filled.Support,
                    contentDescription = null,
                    tint = GoldenPrimary
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Need More Help?",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "For questions, feedback, or bug reports:",
                style = MaterialTheme.typography.bodyMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            ContactItem(Icons.Filled.Email, "support@buim.io")
            ContactItem(Icons.Filled.Code, "github.com/Cloudhabil/BUIM")
            ContactItem(Icons.Filled.Language, "buim.io/docs")
        }
    }
}

@Composable
private fun ContactItem(icon: ImageVector, text: String) {
    Row(
        modifier = Modifier.padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(16.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.bodySmall,
            color = GoldenPrimary
        )
    }
}

@Composable
private fun TipsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Filled.Lightbulb,
                    contentDescription = null,
                    tint = Color(0xFFF59E0B)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Pro Tips",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Spacer(modifier = Modifier.height(12.dp))

            TipItem("Use 107 as a reference point - it's the center where M(107) = 107.")
            TipItem("The mirror function: M(x) = 214 - x. Try it with any number!")
            TipItem("Enable dark mode for better visibility of the golden accents.")
            TipItem("Check the Resonance Gauge - values near 0.0219 indicate optimal alignment.")
            TipItem("All calculations work offline - no internet required.")
        }
    }
}

@Composable
private fun TipItem(tip: String) {
    Row(
        modifier = Modifier.padding(vertical = 4.dp),
        verticalAlignment = Alignment.Top
    ) {
        Text(
            text = "\u2022",
            style = MaterialTheme.typography.bodyMedium,
            color = GoldenPrimary
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = tip,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
