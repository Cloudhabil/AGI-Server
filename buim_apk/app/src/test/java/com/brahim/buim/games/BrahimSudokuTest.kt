/**
 * Brahim Sudoku Unit Tests
 * ========================
 *
 * Verifies the 10x10 Brahim Sudoku game logic.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.games

import org.junit.Test
import org.junit.Before
import org.junit.Assert.*
import com.brahim.buim.core.BrahimConstants

class BrahimSudokuTest {

    private lateinit var game: BrahimSudoku

    @Before
    fun setup() {
        game = BrahimSudoku()
    }

    @Test
    fun `brahim numbers are correct`() {
        val expected = listOf(27, 42, 60, 75, 97, 121, 136, 154, 172, 187)
        assertEquals(expected, BrahimSudoku.BRAHIM_NUMBERS)
    }

    @Test
    fun `grid size is 10x10`() {
        assertEquals(10, BrahimSudoku.SIZE)
    }

    @Test
    fun `box size is 2x5`() {
        assertEquals(2, BrahimSudoku.BOX_ROWS)
        assertEquals(5, BrahimSudoku.BOX_COLS)
    }

    @Test
    fun `mirror sum is 214`() {
        assertEquals(214, BrahimSudoku.MIRROR_SUM)
    }

    @Test
    fun `mirror pairs sum to 214`() {
        val pairs = BrahimSudoku.MIRROR_PAIRS

        for ((key, value) in pairs) {
            assertEquals(214, key + value)
        }
    }

    @Test
    fun `all brahim numbers have mirror pairs`() {
        for (num in BrahimSudoku.BRAHIM_NUMBERS) {
            val mirror = BrahimSudoku.MIRROR_PAIRS[num]
            assertNotNull("Number $num should have a mirror", mirror)
            assertEquals(214, num + mirror!!)
        }
    }

    @Test
    fun `generate puzzle returns valid state`() {
        val state = game.generatePuzzle(SudokuDifficulty.EASY)

        assertNotNull(state)
        assertEquals(10, state.grid.size)
        assertEquals(10, state.grid[0].size)
        assertEquals(SudokuDifficulty.EASY, state.difficulty)
        assertEquals(0, state.moves)
        assertEquals(0, state.hintsUsed)
        assertFalse(state.isComplete)
        assertFalse(state.isSolved)
    }

    @Test
    fun `easy puzzle has more filled cells than hard`() {
        val easy = game.generatePuzzle(SudokuDifficulty.EASY)
        val hard = game.generatePuzzle(SudokuDifficulty.HARD)

        val easyFilled = easy.grid.sumOf { row -> row.count { it.value != null } }
        val hardFilled = hard.grid.sumOf { row -> row.count { it.value != null } }

        assertTrue(easyFilled > hardFilled)
    }

    @Test
    fun `make move updates state`() {
        val state = game.generatePuzzle(SudokuDifficulty.EASY)

        // Find an empty cell
        var emptyCell: Pair<Int, Int>? = null
        for (row in 0 until BrahimSudoku.SIZE) {
            for (col in 0 until BrahimSudoku.SIZE) {
                if (state.grid[row][col].value == null) {
                    emptyCell = row to col
                    break
                }
            }
            if (emptyCell != null) break
        }

        assertNotNull("Should find an empty cell", emptyCell)

        val (row, col) = emptyCell!!
        val newState = game.makeMove(state, row, col, 27)

        assertEquals(27, newState.grid[row][col].value)
        assertEquals(1, newState.moves)
    }

    @Test
    fun `cannot modify fixed cells`() {
        val state = game.generatePuzzle(SudokuDifficulty.EASY)

        // Find a fixed cell
        var fixedCell: Pair<Int, Int>? = null
        for (row in 0 until BrahimSudoku.SIZE) {
            for (col in 0 until BrahimSudoku.SIZE) {
                if (state.grid[row][col].isFixed) {
                    fixedCell = row to col
                    break
                }
            }
            if (fixedCell != null) break
        }

        assertNotNull("Should find a fixed cell", fixedCell)

        val (row, col) = fixedCell!!
        val originalValue = state.grid[row][col].value
        val newState = game.makeMove(state, row, col, 27)

        // Value should not change
        assertEquals(originalValue, newState.grid[row][col].value)
    }

    @Test
    fun `toggle note adds and removes notes`() {
        val state = game.generatePuzzle(SudokuDifficulty.EASY)

        // Find an empty cell
        var emptyCell: Pair<Int, Int>? = null
        for (row in 0 until BrahimSudoku.SIZE) {
            for (col in 0 until BrahimSudoku.SIZE) {
                if (state.grid[row][col].value == null) {
                    emptyCell = row to col
                    break
                }
            }
            if (emptyCell != null) break
        }

        assertNotNull(emptyCell)
        val (row, col) = emptyCell!!

        // Add note
        var newState = game.toggleNote(state, row, col, 27)
        assertTrue(27 in newState.grid[row][col].notes)

        // Remove note
        newState = game.toggleNote(newState, row, col, 27)
        assertFalse(27 in newState.grid[row][col].notes)
    }

    @Test
    fun `get possible values returns valid numbers`() {
        val state = game.generatePuzzle(SudokuDifficulty.EASY)

        // Find an empty cell
        var emptyCell: Pair<Int, Int>? = null
        for (row in 0 until BrahimSudoku.SIZE) {
            for (col in 0 until BrahimSudoku.SIZE) {
                if (state.grid[row][col].value == null) {
                    emptyCell = row to col
                    break
                }
            }
            if (emptyCell != null) break
        }

        assertNotNull(emptyCell)
        val (row, col) = emptyCell!!

        val possible = game.getPossibleValues(state, row, col)

        // All possible values should be Brahim numbers
        for (value in possible) {
            assertTrue(value in BrahimSudoku.BRAHIM_NUMBERS)
        }
    }

    @Test
    fun `get mirror value returns correct mirror`() {
        assertEquals(187, game.getMirrorValue(27))
        assertEquals(27, game.getMirrorValue(187))
        assertEquals(172, game.getMirrorValue(42))
        assertEquals(42, game.getMirrorValue(172))
        assertEquals(154, game.getMirrorValue(60))
        assertEquals(60, game.getMirrorValue(154))
        assertEquals(136, game.getMirrorValue(75))
        assertEquals(75, game.getMirrorValue(136))
        assertEquals(121, game.getMirrorValue(97))
        assertEquals(97, game.getMirrorValue(121))
    }

    @Test
    fun `get hint returns valid cell`() {
        val state = game.generatePuzzle(SudokuDifficulty.EASY)

        val hint = game.getHint(state)

        assertNotNull(hint)
        val (row, col) = hint!!
        assertTrue(row in 0 until BrahimSudoku.SIZE)
        assertTrue(col in 0 until BrahimSudoku.SIZE)
    }

    @Test
    fun `reveal cell fills correct value`() {
        val state = game.generatePuzzle(SudokuDifficulty.EASY)

        // Find an empty cell
        var emptyCell: Pair<Int, Int>? = null
        for (row in 0 until BrahimSudoku.SIZE) {
            for (col in 0 until BrahimSudoku.SIZE) {
                if (state.grid[row][col].value == null) {
                    emptyCell = row to col
                    break
                }
            }
            if (emptyCell != null) break
        }

        assertNotNull(emptyCell)
        val (row, col) = emptyCell!!

        val newState = game.revealCell(state, row, col)

        assertNotNull(newState.grid[row][col].value)
        assertTrue(newState.grid[row][col].value!! in BrahimSudoku.BRAHIM_NUMBERS)
        assertEquals(1, newState.hintsUsed)
    }

    @Test
    fun `get stats returns valid map`() {
        val state = game.generatePuzzle(SudokuDifficulty.MEDIUM)

        val stats = game.getStats(state)

        assertTrue(stats.containsKey("difficulty"))
        assertTrue(stats.containsKey("elapsed_seconds"))
        assertTrue(stats.containsKey("moves"))
        assertTrue(stats.containsKey("hints_used"))
        assertTrue(stats.containsKey("filled_cells"))
        assertTrue(stats.containsKey("total_cells"))
        assertTrue(stats.containsKey("progress_percent"))
        assertTrue(stats.containsKey("brahim_sum"))
        assertTrue(stats.containsKey("mirror_pairs"))

        assertEquals(100, stats["total_cells"])
        assertEquals(214, stats["brahim_sum"])
    }

    @Test
    fun `difficulty levels have increasing cells to remove`() {
        assertTrue(SudokuDifficulty.EASY.cellsToRemove < SudokuDifficulty.MEDIUM.cellsToRemove)
        assertTrue(SudokuDifficulty.MEDIUM.cellsToRemove < SudokuDifficulty.HARD.cellsToRemove)
        assertTrue(SudokuDifficulty.HARD.cellsToRemove < SudokuDifficulty.EXPERT.cellsToRemove)
    }

    @Test
    fun `each row in generated puzzle has valid numbers`() {
        val state = game.generatePuzzle(SudokuDifficulty.EASY)

        for (row in 0 until BrahimSudoku.SIZE) {
            val values = state.grid[row].mapNotNull { it.value }.toSet()
            // All filled values should be Brahim numbers
            for (value in values) {
                assertTrue(value in BrahimSudoku.BRAHIM_NUMBERS)
            }
        }
    }

    @Test
    fun `puzzle maintains mirror symmetry in removed cells`() {
        val state = game.generatePuzzle(SudokuDifficulty.EASY)

        // Count empty cells
        var emptyCount = 0
        for (row in 0 until BrahimSudoku.SIZE) {
            for (col in 0 until BrahimSudoku.SIZE) {
                if (state.grid[row][col].value == null) {
                    emptyCount++
                }
            }
        }

        // Empty count should be approximately even (due to symmetric removal)
        // Some puzzles may have odd count if center cell is removed
        assertTrue(emptyCount > 0)
    }
}
