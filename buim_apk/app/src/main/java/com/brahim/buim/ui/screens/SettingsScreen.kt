/**
 * Settings Screen - App Preferences
 * ==================================
 *
 * Settings and preferences for BUIM app.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.ui.theme.GoldenPrimary

/**
 * Settings state.
 */
data class SettingsState(
    val darkMode: Boolean = true,
    val dynamicColor: Boolean = false,
    val safetyEnabled: Boolean = true,
    val resonanceThreshold: Float = 0.95f,
    val cloudSyncEnabled: Boolean = false,
    val biometricEnabled: Boolean = false,
    val apiKey: String = ""
)

/**
 * Settings screen composable.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    state: SettingsState,
    onStateChange: (SettingsState) -> Unit,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Settings") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Appearance section
            item {
                SettingsSection(title = "Appearance")
            }

            item {
                SwitchSetting(
                    title = "Dark Mode",
                    subtitle = "Use dark color theme",
                    icon = Icons.Filled.DarkMode,
                    checked = state.darkMode,
                    onCheckedChange = { onStateChange(state.copy(darkMode = it)) }
                )
            }

            item {
                SwitchSetting(
                    title = "Dynamic Colors",
                    subtitle = "Use Material You colors (Android 12+)",
                    icon = Icons.Filled.Palette,
                    checked = state.dynamicColor,
                    onCheckedChange = { onStateChange(state.copy(dynamicColor = it)) }
                )
            }

            // Safety section
            item {
                SettingsSection(title = "Safety")
            }

            item {
                SwitchSetting(
                    title = "ASIOS Guard",
                    subtitle = "Enable Berry-Keating safety checking",
                    icon = Icons.Filled.Security,
                    checked = state.safetyEnabled,
                    onCheckedChange = { onStateChange(state.copy(safetyEnabled = it)) }
                )
            }

            item {
                SliderSetting(
                    title = "Resonance Threshold",
                    subtitle = "V-NAND gate threshold (%.2f)".format(state.resonanceThreshold),
                    icon = Icons.Filled.Tune,
                    value = state.resonanceThreshold,
                    onValueChange = { onStateChange(state.copy(resonanceThreshold = it)) },
                    valueRange = 0.8f..0.99f
                )
            }

            // Security section
            item {
                SettingsSection(title = "Security")
            }

            item {
                SwitchSetting(
                    title = "Biometric Authentication",
                    subtitle = "Require fingerprint or face to open",
                    icon = Icons.Filled.Fingerprint,
                    checked = state.biometricEnabled,
                    onCheckedChange = { onStateChange(state.copy(biometricEnabled = it)) }
                )
            }

            item {
                SwitchSetting(
                    title = "Cloud Sync",
                    subtitle = "Sync conversations to secure cloud",
                    icon = Icons.Filled.CloudSync,
                    checked = state.cloudSyncEnabled,
                    onCheckedChange = { onStateChange(state.copy(cloudSyncEnabled = it)) }
                )
            }

            // API section
            item {
                SettingsSection(title = "API Configuration")
            }

            item {
                TextInputSetting(
                    title = "API Key",
                    subtitle = "OpenAI/Anthropic API key",
                    icon = Icons.Filled.Key,
                    value = state.apiKey,
                    onValueChange = { onStateChange(state.copy(apiKey = it)) },
                    isPassword = true
                )
            }

            // About section
            item {
                SettingsSection(title = "About")
            }

            item {
                AboutCard()
            }
        }
    }
}

@Composable
private fun SettingsSection(
    title: String,
    modifier: Modifier = Modifier
) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleSmall,
        color = GoldenPrimary,
        modifier = modifier.padding(top = 16.dp, bottom = 8.dp)
    )
}

@Composable
private fun SwitchSetting(
    title: String,
    subtitle: String,
    icon: ImageVector,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.bodyLarge
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Switch(
                checked = checked,
                onCheckedChange = onCheckedChange
            )
        }
    }
}

@Composable
private fun SliderSetting(
    title: String,
    subtitle: String,
    icon: ImageVector,
    value: Float,
    onValueChange: (Float) -> Unit,
    valueRange: ClosedFloatingPointRange<Float>,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.bodyLarge
                    )
                    Text(
                        text = subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Slider(
                value = value,
                onValueChange = onValueChange,
                valueRange = valueRange,
                modifier = Modifier.padding(top = 8.dp)
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TextInputSetting(
    title: String,
    subtitle: String,
    icon: ImageVector,
    value: String,
    onValueChange: (String) -> Unit,
    isPassword: Boolean = false,
    modifier: Modifier = Modifier
) {
    var showPassword by remember { mutableStateOf(false) }

    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Column {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.bodyLarge
                    )
                    Text(
                        text = subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            OutlinedTextField(
                value = value,
                onValueChange = onValueChange,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
                singleLine = true,
                visualTransformation = if (isPassword && !showPassword) {
                    androidx.compose.ui.text.input.PasswordVisualTransformation()
                } else {
                    androidx.compose.ui.text.input.VisualTransformation.None
                },
                trailingIcon = if (isPassword) {
                    {
                        IconButton(onClick = { showPassword = !showPassword }) {
                            Icon(
                                if (showPassword) Icons.Filled.VisibilityOff else Icons.Filled.Visibility,
                                contentDescription = if (showPassword) "Hide" else "Show"
                            )
                        }
                    }
                } else null
            )
        }
    }
}

@Composable
private fun AboutCard(
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "BUIM",
                style = MaterialTheme.typography.titleLarge,
                color = GoldenPrimary
            )
            Text(
                text = "Brahim Unified IAAS Manifold",
                style = MaterialTheme.typography.bodyMedium
            )
            Text(
                text = "Version 1.0.0",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Mathematical foundation
            Text(
                text = "β = √5 - 2 = 1/φ³ ≈ ${BrahimConstants.BETA_SECURITY}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "© 2026 Elias Oulad Brahim",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
