/**
 * BUIM Color Theme - Golden Ratio Based
 * ======================================
 *
 * Color palette derived from the Brahim sequence and golden ratio.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.theme

import androidx.compose.ui.graphics.Color

// Primary Golden Colors
val GoldenPrimary = Color(0xFFD4AF37)      // Classic gold
val GoldenPrimaryDark = Color(0xFFAA8C2C)  // Dark gold
val GoldenPrimaryLight = Color(0xFFE8C767) // Light gold

// Brahim Sequence Colors (mapped to B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187})
val BrahimAlpha = Color(0xFF1B2B1B)   // B1=27 → Deep green
val BrahimBeta = Color(0xFF2A3D2A)    // B2=42 → Forest
val BrahimGamma = Color(0xFF3C503C)   // B3=60 → Sage
val BrahimDelta = Color(0xFF4B634B)   // B4=75 → Moss
val BrahimEpsilon = Color(0xFF617161) // B5=97 → Stone
val BrahimZeta = Color(0xFF798879)    // B6=121 → Lichen
val BrahimEta = Color(0xFF889888)     // B7=136 → Silver sage
val BrahimTheta = Color(0xFF9AAC9A)   // B8=154 → Pale sage
val BrahimIota = Color(0xFFACBCAC)    // B9=172 → Light moss
val BrahimKappa = Color(0xFFBBCDBB)   // B10=187 → Mist

// Dark Theme Colors
val DarkBackground = Color(0xFF121212)
val DarkSurface = Color(0xFF1E1E1E)
val DarkSurfaceVariant = Color(0xFF2D2D2D)
val DarkOnBackground = Color(0xFFE1E1E1)
val DarkOnSurface = Color(0xFFE1E1E1)

// Light Theme Colors
val LightBackground = Color(0xFFFFFBFE)
val LightSurface = Color(0xFFFFFBFE)
val LightSurfaceVariant = Color(0xFFE7E0EC)
val LightOnBackground = Color(0xFF1C1B1F)
val LightOnSurface = Color(0xFF1C1B1F)

// Safety Indicator Colors
val SafeColor = Color(0xFF4CAF50)       // Green - Safe
val NominalColor = Color(0xFF8BC34A)    // Light green - Nominal
val CautionColor = Color(0xFFFFEB3B)    // Yellow - Caution
val UnsafeColor = Color(0xFFFF9800)     // Orange - Unsafe
val BlockedColor = Color(0xFFF44336)    // Red - Blocked

// Resonance Gauge Colors
val ResonanceLow = Color(0xFF3F51B5)    // Blue - Low resonance
val ResonanceMid = Color(0xFF9C27B0)    // Purple - Medium
val ResonanceHigh = Color(0xFFE91E63)   // Pink - High
val ResonancePeak = Color(0xFFFFD700)   // Gold - Peak (at 0.0219)

// Kelimutu Lake Colors (based on actual Kelimutu volcano)
val LakeTiwuAtaMbupu = Color(0xFF2E5A4D)   // Turquoise-green (Old People)
val LakeTiwuNuwaMuri = Color(0xFF1A4A6E)   // Deep blue-green (Young Maidens)
val LakeTiwuAtaPolo = Color(0xFF8B4513)    // Brown-red (Enchanted)

// Phase Space Colors (for Wormhole Observer)
val PhaseActive = Color(0xFF4CAF50)
val PhaseThrottled = Color(0xFFFF9800)
val PhaseRecovery = Color(0xFF2196F3)
val PhasePurging = Color(0xFFF44336)
val PhaseStable = Color(0xFF9E9E9E)

// Accent Colors
val AccentCyan = Color(0xFF00BCD4)
val AccentTeal = Color(0xFF009688)
val AccentIndigo = Color(0xFF3F51B5)

// Error and Success
val ErrorColor = Color(0xFFCF6679)
val SuccessColor = Color(0xFF03DAC6)
