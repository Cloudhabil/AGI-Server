/**
 * BUIM Typography - Golden Ratio Scaling
 * =======================================
 *
 * Typography scale based on the golden ratio φ = 1.618.
 * Each step is multiplied by φ for harmonious proportions.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

// Golden ratio for typography scaling
private const val PHI = 1.618f

// Base size
private const val BASE_SIZE = 14f

// Font family (using system fonts)
val BrahimFontFamily = FontFamily.Default

// Typography using golden ratio scaling
val BuimTypography = Typography(
    // Display styles (largest)
    displayLarge = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = (BASE_SIZE * PHI * PHI * PHI).sp,  // ~57sp
        lineHeight = (BASE_SIZE * PHI * PHI * PHI * 1.12f).sp,
        letterSpacing = (-0.25).sp
    ),
    displayMedium = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = (BASE_SIZE * PHI * PHI * 1.5f).sp,  // ~45sp
        lineHeight = (BASE_SIZE * PHI * PHI * 1.5f * 1.16f).sp,
        letterSpacing = 0.sp
    ),
    displaySmall = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = (BASE_SIZE * PHI * PHI).sp,  // ~36sp
        lineHeight = (BASE_SIZE * PHI * PHI * 1.22f).sp,
        letterSpacing = 0.sp
    ),

    // Headline styles
    headlineLarge = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = (BASE_SIZE * PHI * 1.4f).sp,  // ~32sp
        lineHeight = (BASE_SIZE * PHI * 1.4f * 1.25f).sp,
        letterSpacing = 0.sp
    ),
    headlineMedium = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = (BASE_SIZE * PHI).sp,  // ~28sp
        lineHeight = (BASE_SIZE * PHI * 1.29f).sp,
        letterSpacing = 0.sp
    ),
    headlineSmall = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = (BASE_SIZE * 1.7f).sp,  // ~24sp
        lineHeight = (BASE_SIZE * 1.7f * 1.33f).sp,
        letterSpacing = 0.sp
    ),

    // Title styles
    titleLarge = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = (BASE_SIZE * 1.57f).sp,  // ~22sp
        lineHeight = (BASE_SIZE * 1.57f * 1.27f).sp,
        letterSpacing = 0.sp
    ),
    titleMedium = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.15.sp
    ),
    titleSmall = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = BASE_SIZE.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp
    ),

    // Body styles
    bodyLarge = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = BASE_SIZE.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.25.sp
    ),
    bodySmall = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.4.sp
    ),

    // Label styles
    labelLarge = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = BASE_SIZE.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp
    ),
    labelMedium = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp
    ),
    labelSmall = TextStyle(
        fontFamily = BrahimFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 11.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp
    )
)

// Monospace for code and technical content
val MonospaceTypography = TextStyle(
    fontFamily = FontFamily.Monospace,
    fontWeight = FontWeight.Normal,
    fontSize = 13.sp,
    lineHeight = 18.sp,
    letterSpacing = 0.sp
)
