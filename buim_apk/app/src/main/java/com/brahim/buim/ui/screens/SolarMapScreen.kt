/**
 * Solar Map Screen - Brahim Solar System Navigator
 * =================================================
 *
 * Interactive exploration of the Solar System using Brahim Numbers.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
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
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.brahim.buim.core.BrahimConstants
import com.brahim.buim.solar.*
import com.brahim.buim.ui.theme.GoldenPrimary
import java.time.LocalDate
import kotlin.math.*

/**
 * Solar Map Screen composable.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SolarMapScreen(
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedBody by remember { mutableStateOf<CelestialBody?>(null) }
    var showSnapshot by remember { mutableStateOf(false) }
    var currentTab by remember { mutableIntStateOf(0) }

    val solarMap = remember { BrahimSolarMap.generateSolarSystemMap() }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Solar System Map") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { showSnapshot = !showSnapshot }) {
                        Icon(
                            if (showSnapshot) Icons.Filled.Public else Icons.Filled.Timeline,
                            contentDescription = "Toggle View"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Tab Row
            TabRow(selectedTabIndex = currentTab) {
                Tab(
                    selected = currentTab == 0,
                    onClick = { currentTab = 0 },
                    text = { Text("Map") },
                    icon = { Icon(Icons.Filled.Public, null) }
                )
                Tab(
                    selected = currentTab == 1,
                    onClick = { currentTab = 1 },
                    text = { Text("Bodies") },
                    icon = { Icon(Icons.Filled.List, null) }
                )
                Tab(
                    selected = currentTab == 2,
                    onClick = { currentTab = 2 },
                    text = { Text("Resonances") },
                    icon = { Icon(Icons.Filled.Insights, null) }
                )
            }

            when (currentTab) {
                0 -> SolarSystemVisualizer(
                    map = solarMap,
                    selectedBody = selectedBody,
                    onBodySelected = { selectedBody = it }
                )
                1 -> BodyList(
                    map = solarMap,
                    selectedBody = selectedBody,
                    onBodySelected = { selectedBody = it }
                )
                2 -> ResonancesList(map = solarMap)
            }

            // Selected body details
            selectedBody?.let { body ->
                SelectedBodyCard(
                    body = body,
                    onDismiss = { selectedBody = null }
                )
            }
        }
    }
}

/**
 * Visual representation of the Solar System.
 */
@Composable
private fun SolarSystemVisualizer(
    map: SolarSystemMap,
    selectedBody: CelestialBody?,
    onBodySelected: (CelestialBody?) -> Unit
) {
    val sunColor = Color(0xFFFFD700)
    val orbitColor = Color(0xFF444444)

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(300.dp)
            .padding(16.dp)
    ) {
        Canvas(
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(Unit) {
                    detectTapGestures { offset ->
                        // Simple tap detection - could be enhanced
                        onBodySelected(null)
                    }
                }
        ) {
            val centerX = size.width / 2
            val centerY = size.height / 2
            val maxRadius = minOf(centerX, centerY) * 0.9f

            // Draw Sun
            drawCircle(
                color = sunColor,
                radius = 15f,
                center = Offset(centerX, centerY)
            )

            // Draw orbits and planets
            val innerPlanets = map.bodies.filter { it.body.semiMajorAxisAU <= 2.0 }
            val outerPlanets = map.bodies.filter { it.body.semiMajorAxisAU > 2.0 && it.body.semiMajorAxisAU <= 40 }

            // Inner solar system (logarithmic scale)
            for (mapping in innerPlanets) {
                val radius = (mapping.body.semiMajorAxisAU * maxRadius / 2.5).toFloat()
                drawOrbitAndPlanet(
                    centerX = centerX,
                    centerY = centerY,
                    orbitRadius = radius,
                    planetRadius = 6f,
                    orbitColor = orbitColor,
                    planetColor = getPlanetColor(mapping.body.name),
                    isSelected = mapping.body == selectedBody
                )
            }

            // Outer planets (compressed scale)
            for (mapping in outerPlanets) {
                val logScale = ln(mapping.body.semiMajorAxisAU) / ln(40.0)
                val radius = (maxRadius * 0.4 + logScale * maxRadius * 0.5).toFloat()
                drawOrbitAndPlanet(
                    centerX = centerX,
                    centerY = centerY,
                    orbitRadius = radius,
                    planetRadius = if (mapping.body.name in listOf("Jupiter", "Saturn")) 10f else 7f,
                    orbitColor = orbitColor,
                    planetColor = getPlanetColor(mapping.body.name),
                    isSelected = mapping.body == selectedBody
                )
            }
        }

        // Legend
        Column(
            modifier = Modifier
                .align(Alignment.TopStart)
                .background(
                    MaterialTheme.colorScheme.surface.copy(alpha = 0.8f),
                    RoundedCornerShape(4.dp)
                )
                .padding(8.dp)
        ) {
            Text(
                "Brahim Solar Map",
                style = MaterialTheme.typography.labelSmall
            )
            Text(
                "Tap bodies for details",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

private fun DrawScope.drawOrbitAndPlanet(
    centerX: Float,
    centerY: Float,
    orbitRadius: Float,
    planetRadius: Float,
    orbitColor: Color,
    planetColor: Color,
    isSelected: Boolean
) {
    // Draw orbit
    drawCircle(
        color = orbitColor,
        radius = orbitRadius,
        center = Offset(centerX, centerY),
        style = androidx.compose.ui.graphics.drawscope.Stroke(width = 1f)
    )

    // Draw planet at a position on the orbit
    val angle = Math.random() * 2 * PI  // Random position for visualization
    val planetX = centerX + orbitRadius * cos(angle).toFloat()
    val planetY = centerY + orbitRadius * sin(angle).toFloat()

    if (isSelected) {
        drawCircle(
            color = Color.White,
            radius = planetRadius + 4f,
            center = Offset(planetX, planetY)
        )
    }

    drawCircle(
        color = planetColor,
        radius = planetRadius,
        center = Offset(planetX, planetY)
    )
}

private fun getPlanetColor(name: String): Color = when (name) {
    "Sun" -> Color(0xFFFFD700)
    "Mercury" -> Color(0xFFB0B0B0)
    "Venus" -> Color(0xFFE6C229)
    "Earth" -> Color(0xFF4B9CD3)
    "Mars" -> Color(0xFFD4442C)
    "Jupiter" -> Color(0xFFD4A574)
    "Saturn" -> Color(0xFFE6D5A8)
    "Uranus" -> Color(0xFF82B1D0)
    "Neptune" -> Color(0xFF5B6FD4)
    "Pluto" -> Color(0xFFB8A99A)
    else -> Color(0xFF888888)
}

/**
 * List of celestial bodies with Brahim Numbers.
 */
@Composable
private fun BodyList(
    map: SolarSystemMap,
    selectedBody: CelestialBody?,
    onBodySelected: (CelestialBody) -> Unit
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        item {
            Text(
                "Planets",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }

        items(map.bodies) { mapping ->
            BodyCard(
                mapping = mapping,
                isSelected = mapping.body == selectedBody,
                onClick = { onBodySelected(mapping.body) }
            )
        }

        item {
            Text(
                "Major Moons",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }

        items(map.moons) { mapping ->
            BodyCard(
                mapping = mapping,
                isSelected = mapping.body == selectedBody,
                onClick = { onBodySelected(mapping.body) }
            )
        }
    }
}

@Composable
private fun BodyCard(
    mapping: BodyMapping,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick,
        colors = if (isSelected) {
            CardDefaults.cardColors(containerColor = GoldenPrimary.copy(alpha = 0.2f))
        } else {
            CardDefaults.cardColors()
        }
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    mapping.body.name,
                    style = MaterialTheme.typography.titleSmall
                )
                Text(
                    "${mapping.body.semiMajorAxisAU} AU",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Column(horizontalAlignment = Alignment.End) {
                Text(
                    "BN: ${mapping.id.brahimNumber}",
                    style = MaterialTheme.typography.labelMedium,
                    color = GoldenPrimary
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        "DR: ${mapping.id.digitalRoot}",
                        style = MaterialTheme.typography.labelSmall
                    )
                    Text(
                        "mod214: ${mapping.id.mod214}",
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
        }
    }
}

/**
 * List of sequence resonances.
 */
@Composable
private fun ResonancesList(map: SolarSystemMap) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "Brahim Sequence",
                        style = MaterialTheme.typography.titleSmall
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        BrahimConstants.BRAHIM_SEQUENCE.joinToString(", ") { it.toString() },
                        style = MaterialTheme.typography.bodyMedium,
                        color = GoldenPrimary
                    )
                    Text(
                        "Sum = ${BrahimConstants.BRAHIM_SUM}",
                        style = MaterialTheme.typography.labelSmall
                    )
                }
            }
        }

        item {
            Text(
                "Orbital Resonances Found",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }

        if (map.resonances.isEmpty()) {
            item {
                Text(
                    "No direct resonances found",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        } else {
            items(map.resonances) { (body, resonance) ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            body.name,
                            style = MaterialTheme.typography.titleSmall
                        )
                        Text(
                            resonance,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }

        item {
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                "Known Connections",
                style = MaterialTheme.typography.titleMedium
            )
        }

        item {
            ResonanceCard(
                title = "Kelimutu Longitude",
                value = "121.82° ≈ B[5] = 121",
                description = "The Kelimutu volcano longitude matches Brahim sequence element 5"
            )
        }

        item {
            ResonanceCard(
                title = "Venus-Earth Synodic",
                value = "583.9 days ≈ 214 × φ² = 560",
                description = "The synodic period relates to Brahim Sum × golden ratio squared"
            )
        }

        item {
            ResonanceCard(
                title = "214 Days",
                value = "214 / 365.25 = 0.586 years",
                description = "Brahim Sum 214 as days is approximately 7 months"
            )
        }
    }
}

@Composable
private fun ResonanceCard(
    title: String,
    value: String,
    description: String
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(title, style = MaterialTheme.typography.titleSmall)
            Text(
                value,
                style = MaterialTheme.typography.bodyMedium,
                color = GoldenPrimary
            )
            Text(
                description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Card showing selected body details.
 */
@Composable
private fun SelectedBodyCard(
    body: CelestialBody,
    onDismiss: () -> Unit
) {
    val bodyID = remember(body) {
        BrahimSolarMap.createBodyID(body)
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.secondaryContainer
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    body.name,
                    style = MaterialTheme.typography.titleMedium
                )
                IconButton(onClick = onDismiss) {
                    Icon(Icons.Filled.Close, "Close")
                }
            }

            Divider(modifier = Modifier.padding(vertical = 8.dp))

            // Physical properties
            Text("Physical Properties", style = MaterialTheme.typography.labelMedium)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                PropertyChip("Type", body.type.name)
                PropertyChip("Radius", "${body.radiusKm.toLong()} km")
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Orbital properties
            Text("Orbital Properties", style = MaterialTheme.typography.labelMedium)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                PropertyChip("Distance", "${body.semiMajorAxisAU} AU")
                PropertyChip("Period", "${body.orbitalPeriodDays.toLong()} days")
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Brahim properties
            Text("Brahim Properties", style = MaterialTheme.typography.labelMedium)
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = MaterialTheme.colorScheme.surface,
                shape = RoundedCornerShape(8.dp)
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text(
                        "Human ID: ${bodyID.humanId}",
                        style = MaterialTheme.typography.bodySmall
                    )
                    Text(
                        "Brahim Number: ${bodyID.brahimNumber}",
                        style = MaterialTheme.typography.bodySmall,
                        color = GoldenPrimary
                    )
                    Text(
                        "3D Brahim Number: ${bodyID.brahimNumber3D}",
                        style = MaterialTheme.typography.bodySmall
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                        Text(
                            "Digital Root: ${bodyID.digitalRoot}",
                            style = MaterialTheme.typography.bodySmall
                        )
                        Text(
                            "mod 214: ${bodyID.mod214}",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                    bodyID.sequenceResonance?.let { resonance ->
                        Text(
                            "Resonance: $resonance",
                            style = MaterialTheme.typography.bodySmall,
                            color = GoldenPrimary
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun PropertyChip(label: String, value: String) {
    Surface(
        shape = RoundedCornerShape(8.dp),
        color = MaterialTheme.colorScheme.surface
    ) {
        Column(
            modifier = Modifier.padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(value, style = MaterialTheme.typography.bodyMedium)
            Text(
                label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
