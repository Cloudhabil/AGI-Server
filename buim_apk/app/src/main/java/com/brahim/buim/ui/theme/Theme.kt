/**
 * BUIM Theme - Material 3 with Brahim Aesthetics
 * ===============================================
 *
 * Golden ratio inspired theming with Brahim sequence colors.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// Dark color scheme
private val DarkColorScheme = darkColorScheme(
    primary = GoldenPrimary,
    onPrimary = DarkBackground,
    primaryContainer = GoldenPrimaryDark,
    onPrimaryContainer = GoldenPrimaryLight,
    secondary = AccentTeal,
    onSecondary = DarkBackground,
    secondaryContainer = BrahimEpsilon,
    onSecondaryContainer = BrahimKappa,
    tertiary = AccentCyan,
    onTertiary = DarkBackground,
    tertiaryContainer = BrahimZeta,
    onTertiaryContainer = BrahimKappa,
    error = ErrorColor,
    onError = DarkBackground,
    errorContainer = BlockedColor,
    onErrorContainer = DarkOnSurface,
    background = DarkBackground,
    onBackground = DarkOnBackground,
    surface = DarkSurface,
    onSurface = DarkOnSurface,
    surfaceVariant = DarkSurfaceVariant,
    onSurfaceVariant = DarkOnSurface,
    outline = BrahimEta
)

// Light color scheme
private val LightColorScheme = lightColorScheme(
    primary = GoldenPrimaryDark,
    onPrimary = LightBackground,
    primaryContainer = GoldenPrimaryLight,
    onPrimaryContainer = BrahimAlpha,
    secondary = AccentTeal,
    onSecondary = LightBackground,
    secondaryContainer = BrahimIota,
    onSecondaryContainer = BrahimBeta,
    tertiary = AccentIndigo,
    onTertiary = LightBackground,
    tertiaryContainer = BrahimKappa,
    onTertiaryContainer = BrahimGamma,
    error = ErrorColor,
    onError = LightBackground,
    errorContainer = CautionColor,
    onErrorContainer = BrahimAlpha,
    background = LightBackground,
    onBackground = LightOnBackground,
    surface = LightSurface,
    onSurface = LightOnSurface,
    surfaceVariant = LightSurfaceVariant,
    onSurfaceVariant = LightOnSurface,
    outline = BrahimEta
)

/**
 * BUIM Theme composable.
 */
@Composable
fun BuimTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color is available on Android 12+
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = BuimTypography,
        content = content
    )
}
