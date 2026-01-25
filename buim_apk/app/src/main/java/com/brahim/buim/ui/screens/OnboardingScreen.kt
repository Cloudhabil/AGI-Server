/**
 * Onboarding Screen
 * =================
 *
 * First-time user welcome flow introducing BUIM concepts.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
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
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.brahim.buim.ui.theme.GoldenPrimary
import kotlinx.coroutines.launch

/**
 * Onboarding page data.
 */
data class OnboardingPage(
    val title: String,
    val subtitle: String,
    val description: String,
    val icon: ImageVector,
    val gradientColors: List<Color>,
    val highlight: String? = null
)

private val onboardingPages = listOf(
    OnboardingPage(
        title = "Welcome to BUIM",
        subtitle = "Brahim Unified IAAS Manifold",
        description = "The world's first physics-grounded AGI platform. 83 applications. One mathematical kernel. Infinite possibilities.",
        icon = Icons.Filled.AutoAwesome,
        gradientColors = listOf(Color(0xFF6366F1), Color(0xFF8B5CF6)),
        highlight = "83 Apps"
    ),
    OnboardingPage(
        title = "From Void to Consciousness",
        subtitle = "B(0) = 0  ...  B(11) = 214",
        description = "12 elements spanning existence. Three exact mirror pairs. Two broken pairs. One observer signature.",
        icon = Icons.Filled.Psychology,
        gradientColors = listOf(Color(0xFF8B5CF6), Color(0xFFEC4899)),
        highlight = "+1 Observer"
    ),
    OnboardingPage(
        title = "The Golden Hierarchy",
        subtitle = "phi -> alpha -> beta -> gamma",
        description = "beta = sqrt(5) - 2 = 1/phi^3 is the security constant. All cryptography and resonance derives from this single truth.",
        icon = Icons.Filled.AutoGraph,
        gradientColors = listOf(Color(0xFFD4AF37), Color(0xFFF59E0B)),
        highlight = "beta = 0.236"
    ),
    OnboardingPage(
        title = "Physics from First Principles",
        subtitle = "2 ppm Accuracy",
        description = "Calculate the fine structure constant, Weinberg angle, and mass ratios directly from the Brahim sequence. No empirical fitting.",
        icon = Icons.Filled.Science,
        gradientColors = listOf(Color(0xFFEC4899), Color(0xFFF43F5E)),
        highlight = "alpha^-1 = 137.036"
    ),
    OnboardingPage(
        title = "Enterprise Security",
        subtitle = "Wormhole Cipher + ASIOS",
        description = "Beta-based encryption with golden ratio key derivation. AI safety via Berry-Keating energy functional.",
        icon = Icons.Filled.Security,
        gradientColors = listOf(Color(0xFF14B8A6), Color(0xFF22C55E)),
        highlight = "Zero Trust"
    ),
    OnboardingPage(
        title = "Ready to Explore",
        subtitle = "Your Journey Begins",
        description = "From Void (0) to Consciousness (214). Tap 'Get Started' to begin exploring the manifold.",
        icon = Icons.Filled.RocketLaunch,
        gradientColors = listOf(Color(0xFF6366F1), Color(0xFFD4AF37)),
        highlight = "Let's Go!"
    )
)

/**
 * Onboarding screen composable.
 */
@Composable
fun OnboardingScreen(
    onComplete: () -> Unit,
    modifier: Modifier = Modifier
) {
    val pagerState = rememberPagerState(pageCount = { onboardingPages.size })
    val coroutineScope = rememberCoroutineScope()

    Box(
        modifier = modifier.fillMaxSize()
    ) {
        // Pager
        HorizontalPager(
            state = pagerState,
            modifier = Modifier.fillMaxSize()
        ) { page ->
            OnboardingPageContent(
                page = onboardingPages[page],
                pageIndex = page
            )
        }

        // Bottom Controls
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Page Indicators
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                repeat(onboardingPages.size) { index ->
                    PageIndicator(
                        isSelected = pagerState.currentPage == index,
                        color = onboardingPages[index].gradientColors[0]
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Navigation Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Skip Button
                if (pagerState.currentPage < onboardingPages.size - 1) {
                    TextButton(onClick = onComplete) {
                        Text("Skip")
                    }
                } else {
                    Spacer(modifier = Modifier.width(64.dp))
                }

                // Next/Get Started Button
                val isLastPage = pagerState.currentPage == onboardingPages.size - 1
                val currentPage = onboardingPages[pagerState.currentPage]

                Button(
                    onClick = {
                        if (isLastPage) {
                            onComplete()
                        } else {
                            coroutineScope.launch {
                                pagerState.animateScrollToPage(pagerState.currentPage + 1)
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = currentPage.gradientColors[0]
                    ),
                    modifier = Modifier.height(48.dp)
                ) {
                    Text(
                        text = if (isLastPage) "Get Started" else "Next",
                        fontWeight = FontWeight.SemiBold
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Icon(
                        imageVector = if (isLastPage) Icons.Filled.Check else Icons.Filled.ArrowForward,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun OnboardingPageContent(
    page: OnboardingPage,
    pageIndex: Int
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        page.gradientColors[0].copy(alpha = 0.1f),
                        page.gradientColors[1].copy(alpha = 0.05f),
                        Color.Transparent
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp)
                .padding(bottom = 120.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Animated Icon
            AnimatedIcon(
                icon = page.icon,
                colors = page.gradientColors
            )

            Spacer(modifier = Modifier.height(32.dp))

            // Title
            Text(
                text = page.title,
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Subtitle
            Text(
                text = page.subtitle,
                style = MaterialTheme.typography.titleMedium,
                color = page.gradientColors[0],
                fontWeight = FontWeight.Medium,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(24.dp))

            // Description
            Text(
                text = page.description,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(horizontal = 16.dp)
            )

            // Highlight Badge
            page.highlight?.let { highlight ->
                Spacer(modifier = Modifier.height(24.dp))
                HighlightBadge(
                    text = highlight,
                    colors = page.gradientColors
                )
            }

            // Special content for specific pages
            when (pageIndex) {
                1 -> SequencePreview()
                2 -> GoldenHierarchyPreview()
            }
        }
    }
}

@Composable
private fun AnimatedIcon(
    icon: ImageVector,
    colors: List<Color>
) {
    var animationPlayed by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (animationPlayed) 1f else 0.5f,
        animationSpec = tween(500),
        label = "iconScale"
    )

    LaunchedEffect(Unit) {
        animationPlayed = true
    }

    Surface(
        shape = CircleShape,
        modifier = Modifier
            .size(120.dp)
            .scale(scale),
        color = colors[0].copy(alpha = 0.15f)
    ) {
        Box(
            contentAlignment = Alignment.Center
        ) {
            Surface(
                shape = CircleShape,
                modifier = Modifier.size(80.dp),
                color = colors[0].copy(alpha = 0.3f)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = colors[0],
                        modifier = Modifier.size(48.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun HighlightBadge(
    text: String,
    colors: List<Color>
) {
    Surface(
        shape = RoundedCornerShape(20.dp),
        color = colors[0].copy(alpha = 0.15f)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = colors[0],
            modifier = Modifier.padding(horizontal = 20.dp, vertical = 10.dp)
        )
    }
}

@Composable
private fun PageIndicator(
    isSelected: Boolean,
    color: Color
) {
    val width by animateFloatAsState(
        targetValue = if (isSelected) 24f else 8f,
        animationSpec = tween(200),
        label = "indicatorWidth"
    )

    Box(
        modifier = Modifier
            .height(8.dp)
            .width(width.dp)
            .clip(CircleShape)
            .background(
                if (isSelected) color else color.copy(alpha = 0.3f)
            )
    )
}

@Composable
private fun SequencePreview() {
    Spacer(modifier = Modifier.height(24.dp))

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                SequencePreviewItem("B(0)", "0", "Void")
                Text("...", color = MaterialTheme.colorScheme.onSurfaceVariant)
                SequencePreviewItem("B(5)", "97", "Security")
                Text("...", color = MaterialTheme.colorScheme.onSurfaceVariant)
                SequencePreviewItem("B(11)", "214", "Consciousness")
            }
        }
    }
}

@Composable
private fun SequencePreviewItem(
    index: String,
    value: String,
    name: String
) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = index,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = GoldenPrimary
        )
        Text(
            text = name,
            style = MaterialTheme.typography.labelSmall,
            fontSize = 9.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun GoldenHierarchyPreview() {
    Spacer(modifier = Modifier.height(24.dp))

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            GoldenHierarchyRow("phi", "1.618...", "Golden Ratio")
            GoldenHierarchyRow("alpha", "0.382...", "1/phi^2")
            GoldenHierarchyRow("beta", "0.236...", "1/phi^3 = sqrt(5)-2")
            GoldenHierarchyRow("gamma", "0.146...", "1/phi^4")
        }
    }
}

@Composable
private fun GoldenHierarchyRow(
    name: String,
    value: String,
    formula: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = name,
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold,
            color = GoldenPrimary
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium
        )
        Text(
            text = formula,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
