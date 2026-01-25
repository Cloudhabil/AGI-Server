package com.brahim.unified

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import com.brahim.unified.physics.PhysicsHubActivity
import com.brahim.unified.math.MathHubActivity
import com.brahim.unified.aviation.AviationHubActivity
import com.brahim.unified.traffic.TrafficHubActivity
import com.brahim.unified.business.BusinessHubActivity
import com.brahim.unified.solvers.SolversHubActivity
import com.brahim.unified.planetary.PlanetaryHubActivity
import com.brahim.unified.security.SecurityHubActivity
import com.brahim.unified.ml.MLHubActivity
import com.brahim.unified.visualization.VisualizationHubActivity
import com.brahim.unified.utilities.UtilitiesHubActivity
import com.brahim.unified.cosmology.CosmologyHubActivity
import com.brahim.unified.engine.EngineDashboardActivity

class MainActivity : AppCompatActivity() {

    private val categories = listOf(
        // Featured: Engine Dashboard
        Category("Engine", "CORE", "Unified Brahim Engine Status", EngineDashboardActivity::class.java),

        // Science Categories
        Category("Physics", "9 Apps", "Fine Structure, Weinberg, Coupling...", PhysicsHubActivity::class.java),
        Category("Cosmology", "5 Apps", "Dark Energy, Dark Matter, Hubble...", CosmologyHubActivity::class.java),
        Category("Mathematics", "7 Apps", "Sequence, Mirror, Egyptian, Golden...", MathHubActivity::class.java),

        // Industry Categories
        Category("Aviation", "7 Apps", "Flight Paths, Fuel, Weather, Runway...", AviationHubActivity::class.java),
        Category("Traffic", "7 Apps", "Signals, Routes, Parking, Waves...", TrafficHubActivity::class.java),
        Category("Business", "7 Apps", "Allocation, Salary, Risk, KPI...", BusinessHubActivity::class.java),

        // Technical Categories
        Category("Solvers", "6 Apps", "SAT, CFD, PDE, Optimization...", SolversHubActivity::class.java),
        Category("Planetary", "3 Apps", "Titan, Mars, Orbital Mechanics...", PlanetaryHubActivity::class.java),
        Category("Security", "3 Apps", "Wormhole Cipher, ASIOS, KeyGen...", SecurityHubActivity::class.java),
        Category("ML/AI", "3 Apps", "Intent, Wavelength, Phase...", MLHubActivity::class.java),

        // Tools Categories
        Category("Visualization", "4 Apps", "Plots, Monitor, Phase Portrait...", VisualizationHubActivity::class.java),
        Category("Utilities", "5 Apps", "Converter, Reference, Export...", UtilitiesHubActivity::class.java)
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        title = "Brahim Unified IAAS"

        val recyclerView = findViewById<RecyclerView>(R.id.categoriesRecyclerView)
        recyclerView.layoutManager = GridLayoutManager(this, 2)
        recyclerView.adapter = CategoryAdapter(categories) { category ->
            startActivity(Intent(this, category.activityClass))
        }
    }

    data class Category(val name: String, val count: String, val description: String, val activityClass: Class<*>)

    class CategoryAdapter(
        private val categories: List<Category>,
        private val onClick: (Category) -> Unit
    ) : RecyclerView.Adapter<CategoryAdapter.ViewHolder>() {

        class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            val nameText: TextView = view.findViewById(R.id.categoryName)
            val countText: TextView = view.findViewById(R.id.categoryCount)
            val descText: TextView = view.findViewById(R.id.categoryDescription)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            val view = LayoutInflater.from(parent.context).inflate(R.layout.item_category, parent, false)
            return ViewHolder(view)
        }

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val category = categories[position]
            holder.nameText.text = category.name
            holder.countText.text = category.count
            holder.descText.text = category.description
            holder.itemView.setOnClickListener { onClick(category) }
        }

        override fun getItemCount() = categories.size
    }
}
