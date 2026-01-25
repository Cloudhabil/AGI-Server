package com.brahim.unified.physics

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class CosmologyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Cosmology Constants"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val hubble = BrahimConstants.hubbleConstant()
        val darkMatter = BrahimConstants.darkMatterPercent()
        val darkEnergy = BrahimConstants.darkEnergyPercent()
        val normalMatter = BrahimConstants.normalMatterPercent()
        val age = BrahimConstants.universeAge()

        resultText.text = buildString {
            append("Hubble: ${String.format("%.1f", hubble)} km/s/Mpc\n")
            append("Dark Matter: ${String.format("%.1f", darkMatter * 100)}%\n")
            append("Dark Energy: ${String.format("%.1f", darkEnergy * 100)}%\n")
            append("Normal Matter: ${String.format("%.1f", normalMatter * 100)}%\n")
            append("Universe Age: ${String.format("%.2f", age)} Gyr")
        }

        formulaText.text = "Hubble: (B(2)*B(9))/S * 2\nDark Matter: B(1)/100\nDark Energy: 31/45\nNormal Matter: phi^5/200"
        accuracyText.text = "Planck 2018 Hubble: 67.4 km/s/Mpc\nDark Matter: ~27%, Dark Energy: ~68%"
    }
}
