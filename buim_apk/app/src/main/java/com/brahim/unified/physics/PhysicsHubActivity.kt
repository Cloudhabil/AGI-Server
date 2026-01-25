package com.brahim.unified.physics

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

class PhysicsHubActivity : AppCompatActivity() {

    private val apps = listOf(
        AppItem("Fine Structure Constant", "Calculate alpha inverse (137.036)", FineStructureActivity::class.java),
        AppItem("Weinberg Angle", "Electroweak mixing angle", WeinbergActivity::class.java),
        AppItem("Mass Ratios", "Muon/electron, proton/electron ratios", MassRatiosActivity::class.java),
        AppItem("Cosmology", "Hubble constant, dark matter percentages", CosmologyActivity::class.java),
        AppItem("Yang-Mills Mass Gap", "Quantum chromodynamics gap calculation", YangMillsActivity::class.java),
        AppItem("Coupling Constants", "Strong and weak coupling inverses", FineStructureActivity::class.java),
        AppItem("Hierarchy Ratios", "Coupling and mass hierarchies", FineStructureActivity::class.java),
        AppItem("Mirror Symmetry", "Brahim sequence symmetry verification", FineStructureActivity::class.java)
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_hub)

        title = "Physics Applications"

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
