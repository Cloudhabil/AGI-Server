package com.brahim.unified.business

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class SchedulerActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dual_input)

        title = "Project Scheduler"

        val durationField = findViewById<EditText>(R.id.inputField1)
        val tasksField = findViewById<EditText>(R.id.inputField2)
        val calculateBtn = findViewById<Button>(R.id.calculateButton)
        val resultText = findViewById<TextView>(R.id.resultText)

        durationField.hint = "Project Duration (days)"
        tasksField.hint = "Number of Milestones"

        calculateBtn.setOnClickListener {
            val duration = durationField.text.toString().toIntOrNull() ?: 100
            val milestones = tasksField.text.toString().toIntOrNull()?.coerceIn(2, 10) ?: 5

            val phi = BrahimConstants.PHI

            // Golden ratio milestone placement
            val schedulePoints = mutableListOf<Pair<Int, String>>()
            schedulePoints.add(0 to "Project Start")

            // Generate milestones at golden ratio intervals
            var remaining = duration.toDouble()
            var elapsed = 0.0

            for (i in 1 until milestones) {
                val nextGap = remaining / phi
                elapsed += nextGap
                remaining -= nextGap
                val day = elapsed.toInt()
                schedulePoints.add(day to "Milestone $i")
            }
            schedulePoints.add(duration to "Project End")

            // Calculate phase durations
            val phases = schedulePoints.zipWithNext { a, b ->
                Triple(a.second, b.second, b.first - a.first)
            }

            resultText.text = buildString {
                append("PROJECT SCHEDULE\n")
                append("Golden Ratio Milestones\n\n")
                append("Duration: $duration days\n")
                append("Milestones: $milestones\n\n")
                append("GOLDEN SCHEDULE:\n")
                schedulePoints.forEach { (day, name) ->
                    val pct = day.toDouble() / duration * 100
                    append("  Day ${String.format("%3d", day)}: $name")
                    append(" (${String.format("%.0f", pct)}%)\n")
                }
                append("\nPHASE DURATIONS:\n")
                phases.forEachIndexed { i, (from, to, days) ->
                    val pct = days.toDouble() / duration * 100
                    append("  Phase ${i + 1}: $days days (${String.format("%.1f", pct)}%)\n")
                }
                append("\nGOLDEN RATIO PRINCIPLE:\n")
                append("  φ = ${String.format("%.6f", phi)}\n")
                append("  Each phase = remaining/φ\n\n")
                append("Benefits:\n")
                append("  - Natural review cadence\n")
                append("  - Accelerating delivery\n")
                append("  - Fibonacci sprint pattern\n\n")
                append("Sprint suggestion:\n")
                val sprintDays = (duration / phi / milestones).toInt()
                append("  ~$sprintDays day sprints")
            }
        }
    }
}
