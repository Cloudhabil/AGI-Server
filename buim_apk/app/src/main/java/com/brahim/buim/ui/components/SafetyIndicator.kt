/**
 * Safety Indicator Component
 * ==========================
 *
 * Visual indicator for ASIOS Guard safety verdicts.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.brahim.buim.safety.SafetyVerdict
import com.brahim.buim.ui.theme.*

/**
 * Safety indicator showing current verdict with animation.
 */
@Composable
fun SafetyIndicator(
    verdict: SafetyVerdict,
    modifier: Modifier = Modifier,
    showLabel: Boolean = true,
    compact: Boolean = false
) {
    val (color, icon, label) = when (verdict) {
        SafetyVerdict.SAFE -> Triple(SafeColor, Icons.Filled.CheckCircle, "Safe")
        SafetyVerdict.NOMINAL -> Triple(NominalColor, Icons.Filled.Check, "Nominal")
        SafetyVerdict.CAUTION -> Triple(CautionColor, Icons.Filled.Warning, "Caution")
        SafetyVerdict.UNSAFE -> Triple(UnsafeColor, Icons.Filled.Error, "Unsafe")
        SafetyVerdict.BLOCKED -> Triple(BlockedColor, Icons.Filled.Block, "Blocked")
    }

    val animatedColor by animateColorAsState(
        targetValue = color,
        animationSpec = tween(durationMillis = 300),
        label = "safety_color"
    )

    // Pulse animation for CAUTION and UNSAFE states
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (verdict == SafetyVerdict.CAUTION || verdict == SafetyVerdict.UNSAFE) 1.1f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(500),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_scale"
    )

    if (compact) {
        // Compact version - just the colored dot
        Box(
            modifier = modifier
                .size(12.dp)
                .scale(pulseScale)
                .clip(CircleShape)
                .background(animatedColor)
        )
    } else {
        // Full version with icon and label
        Surface(
            modifier = modifier,
            shape = RoundedCornerShape(8.dp),
            color = animatedColor.copy(alpha = 0.15f),
            tonalElevation = 1.dp
        ) {
            Row(
                modifier = Modifier
                    .padding(horizontal = 12.dp, vertical = 8.dp)
                    .scale(pulseScale),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = label,
                    tint = animatedColor,
                    modifier = Modifier.size(20.dp)
                )

                if (showLabel) {
                    Text(
                        text = label,
                        style = MaterialTheme.typography.labelMedium,
                        color = animatedColor
                    )
                }
            }
        }
    }
}

/**
 * Safety badge for use in lists and cards.
 */
@Composable
fun SafetyBadge(
    verdict: SafetyVerdict,
    modifier: Modifier = Modifier
) {
    val color = when (verdict) {
        SafetyVerdict.SAFE -> SafeColor
        SafetyVerdict.NOMINAL -> NominalColor
        SafetyVerdict.CAUTION -> CautionColor
        SafetyVerdict.UNSAFE -> UnsafeColor
        SafetyVerdict.BLOCKED -> BlockedColor
    }

    val label = when (verdict) {
        SafetyVerdict.SAFE -> "SAFE"
        SafetyVerdict.NOMINAL -> "OK"
        SafetyVerdict.CAUTION -> "WARN"
        SafetyVerdict.UNSAFE -> "RISK"
        SafetyVerdict.BLOCKED -> "STOP"
    }

    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(4.dp),
        color = color.copy(alpha = 0.2f)
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = color,
            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
        )
    }
}

/**
 * Safety meter showing energy level.
 */
@Composable
fun SafetyMeter(
    energy: Double,
    modifier: Modifier = Modifier
) {
    val normalizedEnergy = energy.coerceIn(0.0, 1.0).toFloat()

    val color = when {
        normalizedEnergy < 0.3 -> SafeColor
        normalizedEnergy < 0.5 -> NominalColor
        normalizedEnergy < 0.7 -> CautionColor
        normalizedEnergy < 0.9 -> UnsafeColor
        else -> BlockedColor
    }

    val animatedProgress by animateFloatAsState(
        targetValue = normalizedEnergy,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "energy_progress"
    )

    Column(modifier = modifier) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = "Safety Energy",
                style = MaterialTheme.typography.labelSmall
            )
            Text(
                text = "%.3f".format(energy),
                style = MaterialTheme.typography.labelSmall
            )
        }

        Spacer(modifier = Modifier.height(4.dp))

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp))
                .background(MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(animatedProgress)
                    .fillMaxHeight()
                    .background(color)
            )
        }

        Spacer(modifier = Modifier.height(2.dp))

        // Threshold markers
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = "0",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
            Text(
                text = "0.0219",
                style = MaterialTheme.typography.labelSmall,
                color = GoldenPrimary
            )
            Text(
                text = "1",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
        }
    }
}
