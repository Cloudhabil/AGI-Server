/**
 * Resonance Gauge Component
 * =========================
 *
 * Visual gauge for V-NAND resonance at GENESIS_CONSTANT = 0.0219.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.ui.theme.*
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.sin

/**
 * Circular resonance gauge showing proximity to GENESIS_CONSTANT.
 */
@Composable
fun ResonanceGauge(
    resonance: Double,
    modifier: Modifier = Modifier,
    showLabel: Boolean = true
) {
    val targetResonance = BrahimConstants.GENESIS_CONSTANT
    val proximityToTarget = 1.0 - abs(resonance - targetResonance).coerceIn(0.0, 1.0)

    // Determine color based on proximity to target
    val gaugeColor = when {
        proximityToTarget > 0.95 -> ResonancePeak  // Gold - at target
        proximityToTarget > 0.8 -> ResonanceHigh   // Pink
        proximityToTarget > 0.5 -> ResonanceMid    // Purple
        else -> ResonanceLow                        // Blue
    }

    val animatedResonance by animateFloatAsState(
        targetValue = resonance.toFloat(),
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "resonance"
    )

    // Glow animation when at peak
    val infiniteTransition = rememberInfiniteTransition(label = "glow")
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = if (proximityToTarget > 0.95) 0.8f else 0.3f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow_alpha"
    )

    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            modifier = Modifier.size(120.dp),
            contentAlignment = Alignment.Center
        ) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val strokeWidth = 12.dp.toPx()
                val radius = (size.minDimension - strokeWidth) / 2
                val center = Offset(size.width / 2, size.height / 2)

                // Background arc
                drawArc(
                    color = Color.Gray.copy(alpha = 0.2f),
                    startAngle = 135f,
                    sweepAngle = 270f,
                    useCenter = false,
                    topLeft = Offset(center.x - radius, center.y - radius),
                    size = Size(radius * 2, radius * 2),
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                )

                // Value arc
                val sweepAngle = (animatedResonance * 270f).coerceIn(0f, 270f)
                drawArc(
                    color = gaugeColor,
                    startAngle = 135f,
                    sweepAngle = sweepAngle,
                    useCenter = false,
                    topLeft = Offset(center.x - radius, center.y - radius),
                    size = Size(radius * 2, radius * 2),
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                )

                // Glow effect at peak
                if (proximityToTarget > 0.95) {
                    drawArc(
                        color = ResonancePeak.copy(alpha = glowAlpha),
                        startAngle = 135f,
                        sweepAngle = sweepAngle,
                        useCenter = false,
                        topLeft = Offset(center.x - radius, center.y - radius),
                        size = Size(radius * 2, radius * 2),
                        style = Stroke(width = strokeWidth + 8.dp.toPx(), cap = StrokeCap.Round)
                    )
                }

                // Target marker at 0.0219 position
                val targetAngle = 135f + (targetResonance.toFloat() * 270f)
                val markerRadius = radius - strokeWidth / 2
                val markerX = center.x + markerRadius * cos(Math.toRadians(targetAngle.toDouble())).toFloat()
                val markerY = center.y + markerRadius * sin(Math.toRadians(targetAngle.toDouble())).toFloat()

                drawCircle(
                    color = GoldenPrimary,
                    radius = 6.dp.toPx(),
                    center = Offset(markerX, markerY)
                )
            }

            // Center text
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "%.4f".format(resonance),
                    style = MaterialTheme.typography.titleLarge,
                    color = gaugeColor
                )
                if (showLabel) {
                    Text(
                        text = "Resonance",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }

        // Target indicator
        Row(
            modifier = Modifier.padding(top = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .background(GoldenPrimary, RoundedCornerShape(4.dp))
            )
            Text(
                text = "Target: 0.0219",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        // Gate status
        val gateOpen = resonance in 0.02..0.025
        Surface(
            modifier = Modifier.padding(top = 4.dp),
            shape = RoundedCornerShape(4.dp),
            color = if (gateOpen) SafeColor.copy(alpha = 0.2f) else Color.Gray.copy(alpha = 0.1f)
        ) {
            Text(
                text = if (gateOpen) "GATE OPEN" else "GATE CLOSED",
                style = MaterialTheme.typography.labelSmall,
                color = if (gateOpen) SafeColor else Color.Gray,
                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
            )
        }
    }
}

/**
 * Compact resonance bar for inline use.
 */
@Composable
fun ResonanceBar(
    resonance: Double,
    modifier: Modifier = Modifier
) {
    val targetResonance = BrahimConstants.GENESIS_CONSTANT
    val proximityToTarget = 1.0 - abs(resonance - targetResonance).coerceIn(0.0, 1.0)

    val color = when {
        proximityToTarget > 0.95 -> ResonancePeak
        proximityToTarget > 0.8 -> ResonanceHigh
        proximityToTarget > 0.5 -> ResonanceMid
        else -> ResonanceLow
    }

    val animatedResonance by animateFloatAsState(
        targetValue = resonance.toFloat().coerceIn(0f, 1f),
        animationSpec = tween(300),
        label = "resonance_bar"
    )

    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Box(
            modifier = Modifier
                .weight(1f)
                .height(6.dp)
                .background(Color.Gray.copy(alpha = 0.2f), RoundedCornerShape(3.dp))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(animatedResonance)
                    .fillMaxHeight()
                    .background(color, RoundedCornerShape(3.dp))
            )

            // Target marker
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .width(2.dp)
                    .offset(x = ((targetResonance * 100).dp))
                    .background(GoldenPrimary)
            )
        }

        Text(
            text = "%.3f".format(resonance),
            style = MaterialTheme.typography.labelSmall,
            color = color
        )
    }
}
