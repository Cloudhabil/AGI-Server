package com.brahim.unified.math

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import com.brahim.unified.R

class MathHubActivity : AppCompatActivity() {

    private val apps = listOf(
        AppItem("Brahim Sequence", "B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}", SequenceActivity::class.java),
        AppItem("Mirror Operator", "M(x) = 214 - x symmetry", MirrorActivity::class.java),
        AppItem("Egyptian Fractions", "Greedy fraction decomposition", EgyptianActivity::class.java),
        AppItem("Resonance Calculator", "R(t) = Σ(1/(d²+ε)) × e^(-λt)", ResonanceActivity::class.java),
        AppItem("Golden Hierarchy", "φ → α → β → γ chain", GoldenActivity::class.java),
        AppItem("Prime Factorization", "Factor Brahim sequence elements", PrimeActivity::class.java),
        AppItem("Continued Fractions", "Infinite expansions of constants", ContinuedFractionActivity::class.java)
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_hub)
        title = "Mathematics"

        val recyclerView = findViewById<RecyclerView>(R.id.hubRecyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = AppAdapter(apps) { app ->
            startActivity(Intent(this, app.activityClass))
        }
    }

    data class AppItem(val name: String, val description: String, val activityClass: Class<*>)

    class AppAdapter(private val apps: List<AppItem>, private val onClick: (AppItem) -> Unit) :
        RecyclerView.Adapter<AppAdapter.ViewHolder>() {
        class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val nameText: TextView = view.findViewById(R.id.appName)
            val descText: TextView = view.findViewById(R.id.appDescription)
        }
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_app, parent, false)
            return ViewHolder(view)
        }
        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val app = apps[position]
            holder.nameText.text = app.name
            holder.descText.text = app.description
            holder.itemView.setOnClickListener { onClick(app) }
        }
        override fun getItemCount() = apps.size
    }
}
