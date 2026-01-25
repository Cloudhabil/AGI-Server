package com.brahim.unified.solvers

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

class SolversHubActivity : AppCompatActivity() {

    private val apps = listOf(
        AppItem("SAT Solver", "Boolean satisfiability with Brahim heuristics", SATActivity::class.java),
        AppItem("CFD Calculator", "Reynolds number and flow regime", CFDActivity::class.java),
        AppItem("PDE Characteristics", "Method of characteristics solver", SATActivity::class.java),
        AppItem("Optimization", "Golden-ratio gradient descent", CFDActivity::class.java),
        AppItem("Constraint Solver", "Resonance-based constraint satisfaction", SATActivity::class.java),
        AppItem("Linear Algebra", "Matrix operations with phi scaling", CFDActivity::class.java),
        AppItem("Graph Algorithms", "Shortest paths via wormhole compression", SATActivity::class.java),
        AppItem("Root Finder", "Newton-Raphson with beta damping", CFDActivity::class.java)
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_hub)

        title = "Solver Applications"

        val recyclerView = findViewById<RecyclerView>(R.id.hubRecyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = AppAdapter(apps) { app ->
            startActivity(Intent(this, app.activityClass))
        }
    }

    data class AppItem(val name: String, val description: String, val activityClass: Class<*>)

    class AppAdapter(
        private val apps: List<AppItem>,
        private val onClick: (AppItem) -> Unit
    ) : RecyclerView.Adapter<AppAdapter.ViewHolder>() {

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
