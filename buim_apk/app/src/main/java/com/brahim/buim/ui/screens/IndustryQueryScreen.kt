/**
 * Industry Query Screen
 * ======================
 *
 * UI for querying the deterministic-first industry database.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.brahim.buim.industry.*
import com.brahim.buim.unified.R
import kotlinx.coroutines.launch

/**
 * Fragment for industry data queries
 */
class IndustryQueryFragment : Fragment() {

    private lateinit var queryInput: EditText
    private lateinit var sectorSpinner: Spinner
    private lateinit var searchButton: Button
    private lateinit var deterministicOnlyCheckbox: CheckBox
    private lateinit var resultContainer: LinearLayout
    private lateinit var progressBar: ProgressBar

    private val queryEngine by lazy { IndustryQueryFactory.createEngine() }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_industry_query, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Initialize views
        queryInput = view.findViewById(R.id.queryInput)
        sectorSpinner = view.findViewById(R.id.sectorSpinner)
        searchButton = view.findViewById(R.id.searchButton)
        deterministicOnlyCheckbox = view.findViewById(R.id.deterministicOnlyCheckbox)
        resultContainer = view.findViewById(R.id.resultContainer)
        progressBar = view.findViewById(R.id.progressBar)

        // Setup sector spinner
        setupSectorSpinner()

        // Setup search button
        searchButton.setOnClickListener {
            performSearch()
        }

        // Show database stats
        showDatabaseStats()
    }

    private fun setupSectorSpinner() {
        val sectors = listOf("Auto-detect") + Sector.values().map { "${it.name} (${it.code})" }
        val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_item, sectors)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        sectorSpinner.adapter = adapter
    }

    private fun performSearch() {
        val queryText = queryInput.text.toString().trim()
        if (queryText.isEmpty()) {
            Toast.makeText(context, "Please enter a query", Toast.LENGTH_SHORT).show()
            return
        }

        // Get selected sector
        val sectorIndex = sectorSpinner.selectedItemPosition
        val sector = if (sectorIndex == 0) null else Sector.values()[sectorIndex - 1]

        // Show progress
        progressBar.visibility = View.VISIBLE
        resultContainer.removeAllViews()

        // Perform query
        lifecycleScope.launch {
            try {
                val query = IndustryQuery(
                    text = queryText,
                    expectedSector = sector,
                    requireDeterministic = deterministicOnlyCheckbox.isChecked
                )

                val result = queryEngine.query(query)
                displayResult(result)
            } catch (e: Exception) {
                displayError(e.message ?: "Unknown error")
            } finally {
                progressBar.visibility = View.GONE
            }
        }
    }

    private fun displayResult(result: QueryResult) {
        resultContainer.removeAllViews()

        // Main result card
        val resultView = layoutInflater.inflate(R.layout.item_query_result, resultContainer, false)

        // Set answer
        resultView.findViewById<TextView>(R.id.answerText).text = result.answer

        // Set BIL
        resultView.findViewById<TextView>(R.id.bilText).text = result.bil.fullLabel

        // Set confidence with color
        val confidenceText = resultView.findViewById<TextView>(R.id.confidenceText)
        val confidencePercent = (result.confidence * 100).toInt()
        confidenceText.text = "Confidence: $confidencePercent%"
        confidenceText.setTextColor(
            when {
                confidencePercent >= 95 -> 0xFF4CAF50.toInt()  // Green
                confidencePercent >= 80 -> 0xFFFF9800.toInt()  // Orange
                else -> 0xFFF44336.toInt()                     // Red
            }
        )

        // Set source
        resultView.findViewById<TextView>(R.id.sourceText).text =
            "Source: ${result.bil.source.description}"

        // Set citation
        resultView.findViewById<TextView>(R.id.citationText).text = result.citation

        // Show/hide warning
        val warningContainer = resultView.findViewById<LinearLayout>(R.id.warningContainer)
        val warningText = resultView.findViewById<TextView>(R.id.warningText)
        if (result.warning != null) {
            warningContainer.visibility = View.VISIBLE
            warningText.text = result.warning
        } else {
            warningContainer.visibility = View.GONE
        }

        // Deterministic badge
        val deterministicBadge = resultView.findViewById<TextView>(R.id.deterministicBadge)
        if (result.isDeterministic) {
            deterministicBadge.text = "✓ DETERMINISTIC"
            deterministicBadge.setBackgroundColor(0xFF4CAF50.toInt())
        } else {
            deterministicBadge.text = "⚠ ML PREDICTION"
            deterministicBadge.setBackgroundColor(0xFFFF9800.toInt())
        }

        resultContainer.addView(resultView)

        // Show alternatives if any
        if (result.alternatives.isNotEmpty()) {
            val altHeader = TextView(context).apply {
                text = "Alternatives:"
                textSize = 14f
                setPadding(0, 16, 0, 8)
            }
            resultContainer.addView(altHeader)

            result.alternatives.forEach { alt ->
                val altView = TextView(context).apply {
                    text = "• ${alt.answer} (${alt.source.name}, ${(alt.confidence * 100).toInt()}%)"
                    textSize = 12f
                    setPadding(16, 4, 0, 4)
                }
                resultContainer.addView(altView)
            }
        }
    }

    private fun displayError(message: String) {
        resultContainer.removeAllViews()
        val errorView = TextView(context).apply {
            text = "Error: $message"
            setTextColor(0xFFF44336.toInt())
            textSize = 14f
        }
        resultContainer.addView(errorView)
    }

    private fun showDatabaseStats() {
        val stats = IndustryQueryFactory.getStatistics()
        // Could display in a subtitle or info section
    }
}

/**
 * Activity wrapper for the query screen
 */
class IndustryQueryActivity : androidx.appcompat.app.AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_industry_query)

        supportActionBar?.apply {
            title = "Industry Query"
            subtitle = "Deterministic-First Knowledge Base"
            setDisplayHomeAsUpEnabled(true)
        }

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .replace(R.id.fragmentContainer, IndustryQueryFragment())
                .commit()
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }
}
