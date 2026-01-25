/**
 * Security Hub Screen
 * ===================
 *
 * Hub for security tools using Brahim cryptography.
 * Wormhole cipher, ASIOS guard, key generation.
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

data class SecurityApp(
    val id: String,
    val name: String,
    val description: String,
    val icon: ImageVector,
    val color: Color
)

private val securityApps = listOf(
    SecurityApp("cipher", "Wormhole Cipher", "Beta-based encryption (beta = sqrt(5) - 2)",
        Icons.Filled.Lock, Color(0xFF6366F1)),
    SecurityApp("asios", "ASIOS Guard", "AI safety via Berry-Keating energy",
        Icons.Filled.Shield, Color(0xFF22C55E)),
    SecurityApp("keygen", "Key Generator", "Golden ratio key derivation",
        Icons.Filled.Key, Color(0xFFD4AF37))
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SecurityHubScreen(
    onAppSelect: (String) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Security", fontWeight = FontWeight.Bold) },
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
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(
                                Brush.horizontalGradient(
                                    listOf(Color(0xFF6366F1), Color(0xFF22C55E))
                                )
                            )
                            .padding(20.dp)
                    ) {
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Filled.Security, null, tint = Color.White)
                                Spacer(Modifier.width(8.dp))
                                Text("Brahim Security", style = MaterialTheme.typography.titleLarge,
                                    color = Color.White, fontWeight = FontWeight.Bold)
                            }
                            Spacer(Modifier.height(8.dp))
                            Text("Enterprise-grade cryptography based on golden ratio hierarchy",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.9f))
                            Spacer(Modifier.height(12.dp))
                            Text("beta = ${String.format("%.10f", BrahimConstants.BETA_SECURITY)}",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.White.copy(alpha = 0.7f),
                                fontFamily = FontFamily.Monospace)
                        }
                    }
                }
            }

            items(securityApps) { app ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onAppSelect(app.id) },
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = app.color.copy(alpha = 0.15f),
                            modifier = Modifier.size(56.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(app.icon, null, tint = app.color,
                                    modifier = Modifier.size(28.dp))
                            }
                        }
                        Spacer(Modifier.width(16.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(app.name, style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold)
                            Text(app.description, style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                }
            }

            item { SecurityConstantsCard() }
        }
    }
}

@Composable
private fun SecurityConstantsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Security Constants", style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(12.dp))

            SecurityConstantRow("beta (Security)", String.format("%.15f", BrahimConstants.BETA_SECURITY))
            SecurityConstantRow("alpha (Wormhole)", String.format("%.15f", BrahimConstants.ALPHA_WORMHOLE))
            SecurityConstantRow("gamma (Damping)", String.format("%.15f", BrahimConstants.GAMMA_DAMPING))
            SecurityConstantRow("Genesis", String.format("%.8f", BrahimConstants.GENESIS_CONSTANT))
        }
    }
}

@Composable
private fun SecurityConstantRow(name: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(name, style = MaterialTheme.typography.bodySmall)
        Text(value, style = MaterialTheme.typography.bodySmall,
            fontFamily = FontFamily.Monospace)
    }
}
