/**
 * Sudoku Screen - Brahim Sudoku Game Interface
 * =============================================
 *
 * UI for playing 10x10 Brahim Sudoku with mirror constraint.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.brahim.buim.games.*
import com.brahim.buim.ui.theme.*

/**
 * Sudoku game screen.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SudokuScreen(
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val game = remember { BrahimSudoku() }
    var gameState by remember { mutableStateOf<SudokuGameState?>(null) }
    var selectedCell by remember { mutableStateOf<Pair<Int, Int>?>(null) }
    var notesMode by remember { mutableStateOf(false) }
    var showDifficultyDialog by remember { mutableStateOf(true) }
    var showCompletionDialog by remember { mutableStateOf(false) }

    // Check for completion
    LaunchedEffect(gameState?.isSolved) {
        if (gameState?.isSolved == true) {
            showCompletionDialog = true
        }
    }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Brahim Sudoku")
                        gameState?.let {
                            Text(
                                text = "${it.difficulty.name} • Moves: ${it.moves}",
                                style = MaterialTheme.typography.labelSmall
                            )
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    // Notes mode toggle
                    IconButton(onClick = { notesMode = !notesMode }) {
                        Icon(
                            if (notesMode) Icons.Filled.Edit else Icons.Filled.EditOff,
                            contentDescription = "Notes mode",
                            tint = if (notesMode) GoldenPrimary else LocalContentColor.current
                        )
                    }
                    // New game
                    IconButton(onClick = { showDifficultyDialog = true }) {
                        Icon(Icons.Filled.Refresh, contentDescription = "New game")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Mirror property reminder
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(8.dp),
                color = GoldenPrimary.copy(alpha = 0.1f)
            ) {
                Text(
                    text = "Mirror Property: α + ω = 214",
                    style = MaterialTheme.typography.labelMedium,
                    color = GoldenPrimary,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(8.dp)
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Game grid
            gameState?.let { state ->
                SudokuGrid(
                    state = state,
                    selectedCell = selectedCell,
                    onCellClick = { row, col ->
                        selectedCell = if (selectedCell == row to col) null else row to col
                    },
                    modifier = Modifier.weight(1f)
                )

                Spacer(modifier = Modifier.height(8.dp))

                // Number pad
                NumberPad(
                    onNumberClick = { number ->
                        selectedCell?.let { (row, col) ->
                            gameState = if (notesMode) {
                                game.toggleNote(state, row, col, number)
                            } else {
                                game.makeMove(state, row, col, number)
                            }
                        }
                    },
                    onClearClick = {
                        selectedCell?.let { (row, col) ->
                            gameState = game.makeMove(state, row, col, null)
                        }
                    },
                    onHintClick = {
                        game.getHint(state)?.let { (row, col) ->
                            gameState = game.revealCell(state, row, col)
                        }
                    },
                    possibleValues = selectedCell?.let { (row, col) ->
                        game.getPossibleValues(state, row, col)
                    } ?: emptySet()
                )
            } ?: run {
                // No game - show start prompt
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Select difficulty to start")
                }
            }
        }
    }

    // Difficulty selection dialog
    if (showDifficultyDialog) {
        DifficultyDialog(
            onDismiss = { showDifficultyDialog = false },
            onSelect = { difficulty ->
                gameState = game.generatePuzzle(difficulty)
                selectedCell = null
                showDifficultyDialog = false
            }
        )
    }

    // Completion dialog
    if (showCompletionDialog) {
        CompletionDialog(
            stats = gameState?.let { game.getStats(it) } ?: emptyMap(),
            onDismiss = { showCompletionDialog = false },
            onNewGame = {
                showCompletionDialog = false
                showDifficultyDialog = true
            }
        )
    }
}

/**
 * The 10x10 Sudoku grid.
 */
@Composable
private fun SudokuGrid(
    state: SudokuGameState,
    selectedCell: Pair<Int, Int>?,
    onCellClick: (Int, Int) -> Unit,
    modifier: Modifier = Modifier
) {
    val cellSize = 34.dp

    Column(
        modifier = modifier
            .border(2.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(4.dp))
            .padding(2.dp)
    ) {
        for (row in 0 until BrahimSudoku.SIZE) {
            Row {
                for (col in 0 until BrahimSudoku.SIZE) {
                    val cell = state.grid[row][col]
                    val isSelected = selectedCell == row to col
                    val isInSelectedRow = selectedCell?.first == row
                    val isInSelectedCol = selectedCell?.second == col
                    val isInSelectedBox = selectedCell?.let { (sr, sc) ->
                        (row / BrahimSudoku.BOX_ROWS == sr / BrahimSudoku.BOX_ROWS) &&
                        (col / BrahimSudoku.BOX_COLS == sc / BrahimSudoku.BOX_COLS)
                    } ?: false

                    // Mirror highlight
                    val isMirrorCell = selectedCell?.let { (sr, sc) ->
                        row == BrahimSudoku.SIZE - 1 - sr && col == BrahimSudoku.SIZE - 1 - sc
                    } ?: false

                    SudokuCell(
                        cell = cell,
                        isSelected = isSelected,
                        isHighlighted = isInSelectedRow || isInSelectedCol || isInSelectedBox,
                        isMirror = isMirrorCell,
                        onClick = { onCellClick(row, col) },
                        modifier = Modifier
                            .size(cellSize)
                            .border(
                                width = when {
                                    col % BrahimSudoku.BOX_COLS == 0 && col > 0 -> 2.dp
                                    else -> 0.5.dp
                                },
                                color = if (col % BrahimSudoku.BOX_COLS == 0 && col > 0)
                                    MaterialTheme.colorScheme.outline
                                else
                                    MaterialTheme.colorScheme.outlineVariant
                            )
                            .border(
                                width = when {
                                    row % BrahimSudoku.BOX_ROWS == 0 && row > 0 -> 2.dp
                                    else -> 0.dp
                                },
                                color = MaterialTheme.colorScheme.outline
                            )
                    )
                }
            }
        }
    }
}

/**
 * Individual Sudoku cell.
 */
@Composable
private fun SudokuCell(
    cell: SudokuCell,
    isSelected: Boolean,
    isHighlighted: Boolean,
    isMirror: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val backgroundColor = when {
        isSelected -> GoldenPrimary.copy(alpha = 0.3f)
        isMirror -> AccentCyan.copy(alpha = 0.2f)
        isHighlighted -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        else -> Color.Transparent
    }

    val textColor = when {
        !cell.isValid -> MaterialTheme.colorScheme.error
        cell.isFixed -> MaterialTheme.colorScheme.onSurface
        else -> GoldenPrimary
    }

    Box(
        modifier = modifier
            .background(backgroundColor)
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center
    ) {
        if (cell.value != null) {
            Text(
                text = cell.value.toString(),
                fontSize = 11.sp,
                fontWeight = if (cell.isFixed) FontWeight.Bold else FontWeight.Normal,
                color = textColor
            )
        } else if (cell.notes.isNotEmpty()) {
            // Show notes in a mini-grid
            Text(
                text = cell.notes.sorted().joinToString(" ") {
                    it.toString().takeLast(2)
                },
                fontSize = 6.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
                lineHeight = 7.sp
            )
        }
    }
}

/**
 * Number pad for input.
 */
@Composable
private fun NumberPad(
    onNumberClick: (Int) -> Unit,
    onClearClick: () -> Unit,
    onHintClick: () -> Unit,
    possibleValues: Set<Int>,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // First row: 27, 42, 60, 75, 97
        Row(
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            BrahimSudoku.BRAHIM_NUMBERS.take(5).forEach { number ->
                NumberButton(
                    number = number,
                    isEnabled = number in possibleValues || possibleValues.isEmpty(),
                    onClick = { onNumberClick(number) }
                )
            }
        }

        Spacer(modifier = Modifier.height(4.dp))

        // Second row: 121, 136, 154, 172, 187
        Row(
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            BrahimSudoku.BRAHIM_NUMBERS.drop(5).forEach { number ->
                NumberButton(
                    number = number,
                    isEnabled = number in possibleValues || possibleValues.isEmpty(),
                    onClick = { onNumberClick(number) }
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Action buttons
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedButton(onClick = onClearClick) {
                Icon(Icons.Filled.Clear, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text("Clear")
            }
            Button(
                onClick = onHintClick,
                colors = ButtonDefaults.buttonColors(containerColor = GoldenPrimary)
            ) {
                Icon(Icons.Filled.Lightbulb, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text("Hint")
            }
        }
    }
}

/**
 * Number button for the pad.
 */
@Composable
private fun NumberButton(
    number: Int,
    isEnabled: Boolean,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier
            .size(56.dp, 40.dp)
            .clip(RoundedCornerShape(8.dp))
            .clickable(enabled = isEnabled, onClick = onClick),
        color = if (isEnabled)
            MaterialTheme.colorScheme.primaryContainer
        else
            MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
    ) {
        Box(contentAlignment = Alignment.Center) {
            Text(
                text = number.toString(),
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = if (isEnabled)
                    MaterialTheme.colorScheme.onPrimaryContainer
                else
                    MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
        }
    }
}

/**
 * Difficulty selection dialog.
 */
@Composable
private fun DifficultyDialog(
    onDismiss: () -> Unit,
    onSelect: (SudokuDifficulty) -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Select Difficulty") },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "Brahim Sudoku uses the sacred sequence:\n{27, 42, 60, 75, 97, 121, 136, 154, 172, 187}",
                    style = MaterialTheme.typography.bodySmall
                )

                Spacer(modifier = Modifier.height(8.dp))

                SudokuDifficulty.values().forEach { difficulty ->
                    OutlinedButton(
                        onClick = { onSelect(difficulty) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("${difficulty.name} (${100 - difficulty.cellsToRemove}% filled)")
                    }
                }
            }
        },
        confirmButton = {},
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

/**
 * Completion celebration dialog.
 */
@Composable
private fun CompletionDialog(
    stats: Map<String, Any>,
    onDismiss: () -> Unit,
    onNewGame: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        icon = {
            Icon(
                Icons.Filled.EmojiEvents,
                contentDescription = null,
                tint = GoldenPrimary,
                modifier = Modifier.size(48.dp)
            )
        },
        title = { Text("Congratulations!") },
        text = {
            Column {
                Text("You solved the Brahim Sudoku!")

                Spacer(modifier = Modifier.height(8.dp))

                Text("Time: ${stats["elapsed_seconds"]} seconds", style = MaterialTheme.typography.bodySmall)
                Text("Moves: ${stats["moves"]}", style = MaterialTheme.typography.bodySmall)
                Text("Hints: ${stats["hints_used"]}", style = MaterialTheme.typography.bodySmall)

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    "The mirror property α + ω = 214 is preserved throughout!",
                    style = MaterialTheme.typography.labelSmall,
                    color = GoldenPrimary
                )
            }
        },
        confirmButton = {
            Button(onClick = onNewGame) {
                Text("New Game")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Close")
            }
        }
    )
}
