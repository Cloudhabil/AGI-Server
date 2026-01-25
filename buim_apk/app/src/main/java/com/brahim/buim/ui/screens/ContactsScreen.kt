/**
 * BUIM - Contacts Screen
 * Contact management with BNP addresses
 */
package com.brahim.buim.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * Contacts list screen
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ContactsScreen(
    onContactClick: (Contact) -> Unit = {},
    onNewChat: () -> Unit = {},
    onBack: () -> Unit = {}
) {
    var searchQuery by remember { mutableStateOf("") }
    var showAddContact by remember { mutableStateOf(false) }

    // Sample contacts (in production, load from database)
    val contacts = remember {
        listOf(
            Contact(
                id = "1",
                name = "Alice",
                bnpAddress = "BNP:136:949486203882100:60:3:7",
                status = ContactStatus.ONLINE,
                lastSeen = System.currentTimeMillis()
            ),
            Contact(
                id = "2",
                name = "Bob",
                bnpAddress = "BNP:136:123456789012345:60:5:2",
                status = ContactStatus.OFFLINE,
                lastSeen = System.currentTimeMillis() - 3600000
            ),
            Contact(
                id = "3",
                name = "Charlie",
                bnpAddress = "BNP:172:987654321098765:172:7:9",
                status = ContactStatus.ONLINE,
                lastSeen = System.currentTimeMillis()
            ),
            Contact(
                id = "4",
                name = "Diana",
                bnpAddress = "BNP:136:555666777888999:60:3:1",
                status = ContactStatus.AWAY,
                lastSeen = System.currentTimeMillis() - 900000
            )
        )
    }

    val filteredContacts = contacts.filter {
        it.name.contains(searchQuery, ignoreCase = true) ||
        it.bnpAddress.contains(searchQuery, ignoreCase = true)
    }

    val primaryGold = Color(0xFFFFD700)
    val deepBlue = Color(0xFF0F0F23)
    val surfaceColor = Color(0xFF1A1A2E)

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Secure Contacts",
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.Default.ArrowBack,
                            contentDescription = "Back",
                            tint = Color.White
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { showAddContact = true }) {
                        Icon(
                            Icons.Default.PersonAdd,
                            contentDescription = "Add Contact",
                            tint = primaryGold
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = surfaceColor
                )
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = onNewChat,
                containerColor = primaryGold,
                contentColor = Color.Black
            ) {
                Icon(Icons.Default.Message, contentDescription = "New Chat")
            }
        },
        containerColor = deepBlue
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Search bar
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                placeholder = {
                    Text(
                        "Search contacts or BNP address",
                        color = Color.White.copy(alpha = 0.5f)
                    )
                },
                leadingIcon = {
                    Icon(
                        Icons.Default.Search,
                        contentDescription = null,
                        tint = Color.White.copy(alpha = 0.7f)
                    )
                },
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = primaryGold,
                    unfocusedBorderColor = Color.White.copy(alpha = 0.3f),
                    focusedTextColor = Color.White,
                    unfocusedTextColor = Color.White,
                    cursorColor = primaryGold
                ),
                shape = RoundedCornerShape(12.dp),
                singleLine = true
            )

            // My BNP Address
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = primaryGold.copy(alpha = 0.1f)
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.QrCode,
                        contentDescription = null,
                        tint = primaryGold,
                        modifier = Modifier.size(32.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            "My BNP Address",
                            color = Color.White.copy(alpha = 0.7f),
                            fontSize = 12.sp
                        )
                        Text(
                            "BNP:136:949486203882100:60:3:7",
                            color = primaryGold,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Mono
                        )
                    }
                    IconButton(onClick = { /* Share */ }) {
                        Icon(
                            Icons.Default.Share,
                            contentDescription = "Share",
                            tint = Color.White
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Online count
            Text(
                text = "${filteredContacts.count { it.status == ContactStatus.ONLINE }} online",
                color = primaryGold,
                fontSize = 12.sp,
                modifier = Modifier.padding(horizontal = 16.dp)
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Contacts list
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(filteredContacts) { contact ->
                    ContactItem(
                        contact = contact,
                        onClick = { onContactClick(contact) }
                    )
                }
            }
        }
    }

    // Add contact dialog
    if (showAddContact) {
        AddContactDialog(
            onDismiss = { showAddContact = false },
            onAdd = { name, bnpAddress ->
                // Add contact logic
                showAddContact = false
            }
        )
    }
}

@Composable
fun ContactItem(
    contact: Contact,
    onClick: () -> Unit
) {
    val primaryGold = Color(0xFFFFD700)
    val surfaceColor = Color(0xFF1A1A2E)

    val statusColor = when (contact.status) {
        ContactStatus.ONLINE -> Color(0xFF4CAF50)
        ContactStatus.AWAY -> Color(0xFFFF9800)
        ContactStatus.OFFLINE -> Color.Gray
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = surfaceColor
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Avatar with status
            Box {
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(primaryGold.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = contact.name.first().toString(),
                        color = primaryGold,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                // Status indicator
                Box(
                    modifier = Modifier
                        .size(14.dp)
                        .clip(CircleShape)
                        .background(Color(0xFF0F0F23))
                        .padding(2.dp)
                        .align(Alignment.BottomEnd)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .clip(CircleShape)
                            .background(statusColor)
                    )
                }
            }

            Spacer(modifier = Modifier.width(16.dp))

            // Name and BNP
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = contact.name,
                    color = Color.White,
                    fontWeight = FontWeight.Medium,
                    fontSize = 16.sp
                )
                Text(
                    text = contact.bnpAddress.take(30) + "...",
                    color = Color.White.copy(alpha = 0.5f),
                    fontSize = 12.sp
                )
            }

            // Actions
            Row {
                IconButton(onClick = { /* Voice call */ }) {
                    Icon(
                        Icons.Default.Call,
                        contentDescription = "Call",
                        tint = primaryGold
                    )
                }
                IconButton(onClick = onClick) {
                    Icon(
                        Icons.Default.Message,
                        contentDescription = "Message",
                        tint = Color.White
                    )
                }
            }
        }
    }
}

@Composable
fun AddContactDialog(
    onDismiss: () -> Unit,
    onAdd: (String, String) -> Unit
) {
    var name by remember { mutableStateOf("") }
    var bnpAddress by remember { mutableStateOf("") }

    val primaryGold = Color(0xFFFFD700)

    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = Color(0xFF1A1A2E),
        title = {
            Text("Add Contact", color = Color.White)
        },
        text = {
            Column {
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("Name", color = Color.White.copy(alpha = 0.7f)) },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = primaryGold,
                        unfocusedBorderColor = Color.White.copy(alpha = 0.3f),
                        focusedTextColor = Color.White,
                        unfocusedTextColor = Color.White
                    ),
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(16.dp))

                OutlinedTextField(
                    value = bnpAddress,
                    onValueChange = { bnpAddress = it },
                    label = { Text("BNP Address", color = Color.White.copy(alpha = 0.7f)) },
                    placeholder = { Text("BNP:136:...", color = Color.White.copy(alpha = 0.3f)) },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = primaryGold,
                        unfocusedBorderColor = Color.White.copy(alpha = 0.3f),
                        focusedTextColor = Color.White,
                        unfocusedTextColor = Color.White
                    ),
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(8.dp))

                // QR Scanner option
                OutlinedButton(
                    onClick = { /* Open QR scanner */ },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = primaryGold
                    )
                ) {
                    Icon(Icons.Default.QrCodeScanner, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Scan QR Code")
                }
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onAdd(name, bnpAddress) },
                enabled = name.isNotBlank() && bnpAddress.startsWith("BNP:")
            ) {
                Text("Add", color = primaryGold)
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel", color = Color.White.copy(alpha = 0.7f))
            }
        }
    )
}

// Data classes

data class Contact(
    val id: String,
    val name: String,
    val bnpAddress: String,
    val status: ContactStatus,
    val lastSeen: Long,
    val avatar: String? = null
)

enum class ContactStatus {
    ONLINE,
    AWAY,
    OFFLINE
}
