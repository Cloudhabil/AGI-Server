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

class MainActivity : AppCompatActivity() {
    
    private val categories = listOf(
        Category("Physics", "12 Apps", "Fine Structure, Weinberg, Mass Ratios...", PhysicsHubActivity::class.java),
        Category("Cosmology", "8 Apps", "Dark Matter, Hubble, Universe Age...", PhysicsHubActivity::class.java),
        Category("Mathematics", "10 Apps", "Brahim Sequence, Mirror, Egyptian...", MathHubActivity::class.java),
        Category("Aviation", "8 Apps", "Flight Paths, ATC, Maintenance...", AviationHubActivity::class.java),
        Category("Traffic", "8 Apps", "Signals, Congestion, Parking...", TrafficHubActivity::class.java),
        Category("Business", "8 Apps", "Allocation, Synergy, Compliance...", BusinessHubActivity::class.java),
        Category("Solvers", "8 Apps", "SAT, CFD, PDE Characteristics...", SolversHubActivity::class.java),
        Category("Planetary", "6 Apps", "Titan Explorer, Methane Cycle...", PlanetaryHubActivity::class.java),
        Category("Security", "6 Apps", "Wormhole Cipher, ASIOS Safety...", SecurityHubActivity::class.java),
        Category("ML/AI", "6 Apps", "Intent Classifier, Wavelength...", MLHubActivity::class.java),
        Category("Visualization", "4 Apps", "Plots, Graphs, Monitors...", PhysicsHubActivity::class.java),
        Category("Utilities", "4 Apps", "Converter, Reference...", PhysicsHubActivity::class.java)
    )
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
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
