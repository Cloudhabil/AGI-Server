/**
 * Brahim Sudoku - 10x10 Sudoku with Brahim Numbers
 * =================================================
 *
 * A unique Sudoku variant using the Brahim Sequence:
 * B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}
 *
 * Rules:
 * 1. Each row contains all 10 Brahim numbers exactly once
 * 2. Each column contains all 10 Brahim numbers exactly once
 * 3. Each 2x5 box contains all 10 Brahim numbers exactly once
 * 4. Mirror constraint: If cell (i,j) = x, then cell (9-i, 9-j) should be M(x) = 214 - x
 *
 * The mirror constraint reflects the Brahim sequence property: α + ω = 214
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.games

import com.brahim.buim.core.BrahimConstants
import kotlin.random.Random

/**
 * Difficulty levels for puzzle generation.
 */
enum class SudokuDifficulty(val cellsToRemove: Int) {
    EASY(30),
    MEDIUM(45),
    HARD(55),
    EXPERT(65)
}

/**
 * Cell state in the puzzle.
 */
data class SudokuCell(
    val value: Int?,           // null = empty
    val isFixed: Boolean,      // true = part of original puzzle
    val isValid: Boolean = true,
    val notes: Set<Int> = emptySet()  // pencil marks
)

/**
 * Game state.
 */
data class SudokuGameState(
    val grid: Array<Array<SudokuCell>>,
    val difficulty: SudokuDifficulty,
    val startTime: Long,
    val moves: Int = 0,
    val hintsUsed: Int = 0,
    val isComplete: Boolean = false,
    val isSolved: Boolean = false
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is SudokuGameState) return false
        return grid.contentDeepEquals(other.grid) && difficulty == other.difficulty
    }

    override fun hashCode(): Int = grid.contentDeepHashCode()
}

/**
 * Brahim Sudoku game engine.
 */
class BrahimSudoku {

    companion object {
        const val SIZE = 10
        const val BOX_ROWS = 2
        const val BOX_COLS = 5
        const val MIRROR_SUM = BrahimConstants.BRAHIM_SUM  // 214

        // The Brahim numbers used as symbols
        val BRAHIM_NUMBERS = BrahimConstants.BRAHIM_SEQUENCE.toList()

        // Mirror pairs: (27,187), (42,172), (60,154), (75,136), (97,121)
        val MIRROR_PAIRS = mapOf(
            27 to 187, 187 to 27,
            42 to 172, 172 to 42,
            60 to 154, 154 to 60,
            75 to 136, 136 to 75,
            97 to 121, 121 to 97
        )
    }

    // Current solution (for validation)
    private var solution: Array<IntArray>? = null

    /**
     * Generate a new puzzle.
     */
    fun generatePuzzle(difficulty: SudokuDifficulty): SudokuGameState {
        // Generate a complete valid grid
        val completeGrid = generateCompleteGrid()
        solution = completeGrid.map { it.clone() }.toTypedArray()

        // Remove cells based on difficulty
        val puzzle = createPuzzleFromSolution(completeGrid, difficulty)

        return SudokuGameState(
            grid = puzzle,
            difficulty = difficulty,
            startTime = System.currentTimeMillis()
        )
    }

    /**
     * Generate a complete valid Brahim Sudoku grid.
     */
    private fun generateCompleteGrid(): Array<IntArray> {
        val grid = Array(SIZE) { IntArray(SIZE) { 0 } }

        // Use backtracking to fill the grid
        fillGrid(grid, 0, 0)

        return grid
    }

    /**
     * Backtracking algorithm to fill the grid.
     */
    private fun fillGrid(grid: Array<IntArray>, row: Int, col: Int): Boolean {
        if (row == SIZE) return true  // All rows filled

        val nextRow = if (col == SIZE - 1) row + 1 else row
        val nextCol = if (col == SIZE - 1) 0 else col + 1

        // Shuffle numbers for randomness
        val numbers = BRAHIM_NUMBERS.shuffled()

        for (num in numbers) {
            if (isValidPlacement(grid, row, col, num)) {
                grid[row][col] = num

                // Apply mirror constraint if in first half
                if (row < SIZE / 2 || (row == SIZE / 2 - 1 && col < SIZE / 2)) {
                    val mirrorRow = SIZE - 1 - row
                    val mirrorCol = SIZE - 1 - col
                    val mirrorNum = MIRROR_PAIRS[num] ?: num

                    if (mirrorRow != row || mirrorCol != col) {
                        if (isValidPlacement(grid, mirrorRow, mirrorCol, mirrorNum)) {
                            grid[mirrorRow][mirrorCol] = mirrorNum

                            if (fillGrid(grid, nextRow, nextCol)) {
                                return true
                            }

                            grid[mirrorRow][mirrorCol] = 0
                        }
                    } else {
                        if (fillGrid(grid, nextRow, nextCol)) {
                            return true
                        }
                    }
                } else {
                    if (fillGrid(grid, nextRow, nextCol)) {
                        return true
                    }
                }

                grid[row][col] = 0
            }
        }

        return false
    }

    /**
     * Check if placing a number is valid.
     */
    private fun isValidPlacement(grid: Array<IntArray>, row: Int, col: Int, num: Int): Boolean {
        // Check row
        if (grid[row].contains(num)) return false

        // Check column
        if (grid.any { it[col] == num }) return false

        // Check 2x5 box
        val boxRowStart = (row / BOX_ROWS) * BOX_ROWS
        val boxColStart = (col / BOX_COLS) * BOX_COLS

        for (r in boxRowStart until boxRowStart + BOX_ROWS) {
            for (c in boxColStart until boxColStart + BOX_COLS) {
                if (grid[r][c] == num) return false
            }
        }

        return true
    }

    /**
     * Create puzzle by removing cells from solution.
     */
    private fun createPuzzleFromSolution(
        solution: Array<IntArray>,
        difficulty: SudokuDifficulty
    ): Array<Array<SudokuCell>> {
        val puzzle = Array(SIZE) { row ->
            Array(SIZE) { col ->
                SudokuCell(value = solution[row][col], isFixed = true)
            }
        }

        // Remove cells symmetrically (to maintain mirror property hint)
        val cellsToRemove = difficulty.cellsToRemove
        val positions = mutableListOf<Pair<Int, Int>>()

        for (r in 0 until SIZE) {
            for (c in 0 until SIZE) {
                positions.add(r to c)
            }
        }

        positions.shuffle()

        var removed = 0
        val removedSet = mutableSetOf<Pair<Int, Int>>()

        for ((row, col) in positions) {
            if (removed >= cellsToRemove) break
            if ((row to col) in removedSet) continue

            // Remove cell and its mirror
            val mirrorRow = SIZE - 1 - row
            val mirrorCol = SIZE - 1 - col

            puzzle[row][col] = SudokuCell(value = null, isFixed = false)
            removedSet.add(row to col)
            removed++

            if (mirrorRow != row || mirrorCol != col) {
                if (removed < cellsToRemove && (mirrorRow to mirrorCol) !in removedSet) {
                    puzzle[mirrorRow][mirrorCol] = SudokuCell(value = null, isFixed = false)
                    removedSet.add(mirrorRow to mirrorCol)
                    removed++
                }
            }
        }

        return puzzle
    }

    /**
     * Make a move in the game.
     */
    fun makeMove(state: SudokuGameState, row: Int, col: Int, value: Int?): SudokuGameState {
        if (state.grid[row][col].isFixed) return state

        val newGrid = state.grid.map { it.clone() }.toTypedArray()
        val isValid = value == null || isValidMove(newGrid, row, col, value)

        newGrid[row][col] = SudokuCell(
            value = value,
            isFixed = false,
            isValid = isValid,
            notes = if (value != null) emptySet() else state.grid[row][col].notes
        )

        val isComplete = checkComplete(newGrid)
        val isSolved = isComplete && checkSolved(newGrid)

        return state.copy(
            grid = newGrid,
            moves = state.moves + 1,
            isComplete = isComplete,
            isSolved = isSolved
        )
    }

    /**
     * Toggle a note (pencil mark) on a cell.
     */
    fun toggleNote(state: SudokuGameState, row: Int, col: Int, value: Int): SudokuGameState {
        if (state.grid[row][col].isFixed || state.grid[row][col].value != null) return state

        val newGrid = state.grid.map { it.clone() }.toTypedArray()
        val currentNotes = newGrid[row][col].notes
        val newNotes = if (value in currentNotes) {
            currentNotes - value
        } else {
            currentNotes + value
        }

        newGrid[row][col] = newGrid[row][col].copy(notes = newNotes)

        return state.copy(grid = newGrid)
    }

    /**
     * Check if a move is valid.
     */
    private fun isValidMove(grid: Array<Array<SudokuCell>>, row: Int, col: Int, value: Int): Boolean {
        // Check row
        for (c in 0 until SIZE) {
            if (c != col && grid[row][c].value == value) return false
        }

        // Check column
        for (r in 0 until SIZE) {
            if (r != row && grid[r][col].value == value) return false
        }

        // Check 2x5 box
        val boxRowStart = (row / BOX_ROWS) * BOX_ROWS
        val boxColStart = (col / BOX_COLS) * BOX_COLS

        for (r in boxRowStart until boxRowStart + BOX_ROWS) {
            for (c in boxColStart until boxColStart + BOX_COLS) {
                if ((r != row || c != col) && grid[r][c].value == value) return false
            }
        }

        return true
    }

    /**
     * Check if all cells are filled.
     */
    private fun checkComplete(grid: Array<Array<SudokuCell>>): Boolean {
        return grid.all { row -> row.all { it.value != null } }
    }

    /**
     * Check if the puzzle is correctly solved.
     */
    private fun checkSolved(grid: Array<Array<SudokuCell>>): Boolean {
        // Check all rows
        for (row in 0 until SIZE) {
            val values = grid[row].mapNotNull { it.value }.toSet()
            if (values != BRAHIM_NUMBERS.toSet()) return false
        }

        // Check all columns
        for (col in 0 until SIZE) {
            val values = (0 until SIZE).mapNotNull { grid[it][col].value }.toSet()
            if (values != BRAHIM_NUMBERS.toSet()) return false
        }

        // Check all 2x5 boxes
        for (boxRow in 0 until SIZE / BOX_ROWS) {
            for (boxCol in 0 until SIZE / BOX_COLS) {
                val values = mutableSetOf<Int>()
                for (r in 0 until BOX_ROWS) {
                    for (c in 0 until BOX_COLS) {
                        grid[boxRow * BOX_ROWS + r][boxCol * BOX_COLS + c].value?.let {
                            values.add(it)
                        }
                    }
                }
                if (values != BRAHIM_NUMBERS.toSet()) return false
            }
        }

        // Check mirror constraint
        for (row in 0 until SIZE / 2) {
            for (col in 0 until SIZE) {
                val value = grid[row][col].value ?: continue
                val mirrorRow = SIZE - 1 - row
                val mirrorCol = SIZE - 1 - col
                val mirrorValue = grid[mirrorRow][mirrorCol].value ?: continue

                if (value + mirrorValue != MIRROR_SUM) return false
            }
        }

        return true
    }

    /**
     * Get a hint for the current state.
     */
    fun getHint(state: SudokuGameState): Pair<Int, Int>? {
        solution?.let { sol ->
            for (row in 0 until SIZE) {
                for (col in 0 until SIZE) {
                    if (state.grid[row][col].value == null) {
                        return row to col
                    }
                    if (state.grid[row][col].value != sol[row][col] && !state.grid[row][col].isFixed) {
                        return row to col
                    }
                }
            }
        }
        return null
    }

    /**
     * Reveal a cell using the solution.
     */
    fun revealCell(state: SudokuGameState, row: Int, col: Int): SudokuGameState {
        if (state.grid[row][col].isFixed) return state

        solution?.let { sol ->
            val newGrid = state.grid.map { it.clone() }.toTypedArray()
            newGrid[row][col] = SudokuCell(
                value = sol[row][col],
                isFixed = false,
                isValid = true
            )

            return state.copy(
                grid = newGrid,
                hintsUsed = state.hintsUsed + 1,
                isComplete = checkComplete(newGrid),
                isSolved = checkComplete(newGrid) && checkSolved(newGrid)
            )
        }

        return state
    }

    /**
     * Get possible values for a cell.
     */
    fun getPossibleValues(state: SudokuGameState, row: Int, col: Int): Set<Int> {
        if (state.grid[row][col].value != null) return emptySet()

        return BRAHIM_NUMBERS.filter { num ->
            isValidMove(state.grid, row, col, num)
        }.toSet()
    }

    /**
     * Get the mirror value for a Brahim number.
     */
    fun getMirrorValue(value: Int): Int = MIRROR_PAIRS[value] ?: value

    /**
     * Get game statistics.
     */
    fun getStats(state: SudokuGameState): Map<String, Any> {
        val elapsedTime = System.currentTimeMillis() - state.startTime
        val filledCells = state.grid.sumOf { row -> row.count { it.value != null } }
        val totalCells = SIZE * SIZE

        return mapOf(
            "difficulty" to state.difficulty.name,
            "elapsed_seconds" to elapsedTime / 1000,
            "moves" to state.moves,
            "hints_used" to state.hintsUsed,
            "filled_cells" to filledCells,
            "total_cells" to totalCells,
            "progress_percent" to (filledCells * 100 / totalCells),
            "is_complete" to state.isComplete,
            "is_solved" to state.isSolved,
            "brahim_sum" to MIRROR_SUM,
            "mirror_pairs" to MIRROR_PAIRS.entries.take(5).map { "${it.key} + ${it.value} = $MIRROR_SUM" }
        )
    }
}
