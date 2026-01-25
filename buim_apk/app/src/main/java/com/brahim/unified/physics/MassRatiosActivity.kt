package com.brahim.unified.physics

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.brahim.unified.R
import com.brahim.unified.core.BrahimConstants

class MassRatiosActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_calculator)

        title = "Mass Ratios"

        val resultText = findViewById<TextView>(R.id.resultText)
        val formulaText = findViewById<TextView>(R.id.formulaText)
        val accuracyText = findViewById<TextView>(R.id.accuracyText)

        val muonRatio = BrahimConstants.muonElectronRatio()
        val protonRatio = BrahimConstants.protonElectronRatio()

        val muonExp = 206.7682830
        val protonExp = 1836.15267343

        val (muonDev, muonUnit) = BrahimConstants.accuracy(muonRatio, muonExp)
        val (protonDev, protonUnit) = BrahimConstants.accuracy(protonRatio, protonExp)

        resultText.text = "m_muon/m_e = ${BrahimConstants.formatScientific(muonRatio)}\nm_proton/m_e = ${BrahimConstants.formatScientific(protonRatio)}"
        formulaText.text = "Muon: B(4)^2 / B(7) * 5\nProton: (B(5) + B(10)) * phi * 4"
        accuracyText.text = "Muon CODATA: $muonExp (${String.format("%.2f", muonDev)} $muonUnit)\nProton CODATA: $protonExp (${String.format("%.2f", protonDev)} $protonUnit)"
    }
}
