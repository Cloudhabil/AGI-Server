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
        AppItem("Signal Optimizer", "Golden-ratio signal timing", SignalActivity::class.java),
        AppItem("Congestion Analyzer", "Real-time flow analysis", CongestionActivity::class.java),
        AppItem("Route Optimizer", "β-compressed path planning", RouteActivity::class.java),
        AppItem("Parking Allocator", "Egyptian fraction fair division", ParkingActivity::class.java),
        AppItem("Emergency Router", "ASIOS-based priority routing", EmergencyActivity::class.java),
        AppItem("Traffic Waves", "PDE solver for shock waves", WavesActivity::class.java),
        AppItem("Intersection Manager", "Multi-way signal timing", IntersectionActivity::class.java)
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_hub)
        title = "Traffic"

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
