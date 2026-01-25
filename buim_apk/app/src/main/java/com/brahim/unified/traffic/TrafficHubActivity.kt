package com.brahim.unified.traffic

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

class TrafficHubActivity : AppCompatActivity() {

    private val apps = listOf(
        AppItem("Signal Timing", "Brahim-optimized traffic signals", SignalActivity::class.java),
        AppItem("Congestion Predictor", "Resonance-based traffic flow", CongestionActivity::class.java),
        AppItem("Route Optimizer", "Golden-ratio path selection", SignalActivity::class.java),
        AppItem("Parking Allocator", "Fair space distribution", CongestionActivity::class.java),
        AppItem("Emergency Router", "Priority routing with phi", SignalActivity::class.java),
        AppItem("Traffic Waves", "Method of characteristics flow", CongestionActivity::class.java),
        AppItem("Intersection Analysis", "Multi-way timing optimization", SignalActivity::class.java),
        AppItem("Speed Harmonizer", "Continuous flow management", CongestionActivity::class.java)
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_hub)

        title = "Traffic Applications"

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
