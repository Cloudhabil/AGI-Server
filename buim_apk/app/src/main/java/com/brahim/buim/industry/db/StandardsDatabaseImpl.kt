/**
 * Standards Database Implementation
 * ==================================
 *
 * Embedded IEC, ISO, DIN, IEEE standards lookup.
 * Deterministic source - 100% trust level.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry.db

import com.brahim.buim.industry.*

/**
 * Standard entry in the database
 */
data class StandardEntry(
    val reference: String,      // e.g., "IEC 60617-2"
    val title: String,
    val description: String,
    val sector: Sector,
    val keywords: List<String>,
    val source: Source,
    val itemId: Long
)

/**
 * Embedded Standards Database
 */
class StandardsDatabaseImpl : StandardsDatabase {

    // Embedded standards data
    private val standards: List<StandardEntry> = listOf(
        // =====================================================================
        // ELECTRICAL (IEC)
        // =====================================================================
        StandardEntry(
            reference = "IEC 60617",
            title = "Graphical symbols for diagrams",
            description = "Standard graphical symbols for electrical and electronic diagrams",
            sector = Sector.ELECTRICAL,
            keywords = listOf("symbol", "diagram", "schematic", "electrical", "graphic"),
            source = Source.IEC_STANDARD,
            itemId = 60617
        ),
        StandardEntry(
            reference = "IEC 60364",
            title = "Low-voltage electrical installations",
            description = "Requirements for design, erection and verification of electrical installations",
            sector = Sector.ELECTRICAL,
            keywords = listOf("installation", "wiring", "low voltage", "building", "safety"),
            source = Source.IEC_STANDARD,
            itemId = 60364
        ),
        StandardEntry(
            reference = "IEC 61131-3",
            title = "Programmable controllers - Programming languages",
            description = "PLC programming languages: Ladder, FBD, ST, IL, SFC",
            sector = Sector.ELECTRICAL,
            keywords = listOf("plc", "programming", "ladder", "automation", "controller"),
            source = Source.IEC_STANDARD,
            itemId = 61131
        ),
        StandardEntry(
            reference = "IEC 61000",
            title = "Electromagnetic compatibility (EMC)",
            description = "EMC requirements for electrical and electronic equipment",
            sector = Sector.ELECTRICAL,
            keywords = listOf("emc", "electromagnetic", "compatibility", "interference", "emission"),
            source = Source.IEC_STANDARD,
            itemId = 61000
        ),
        StandardEntry(
            reference = "IEC 60909",
            title = "Short-circuit currents in three-phase AC systems",
            description = "Calculation of short-circuit currents",
            sector = Sector.ELECTRICAL,
            keywords = listOf("short circuit", "fault", "current", "three phase", "calculation"),
            source = Source.IEC_STANDARD,
            itemId = 60909
        ),

        // =====================================================================
        // ENERGY / RENEWABLES
        // =====================================================================
        StandardEntry(
            reference = "IEC 61215",
            title = "Terrestrial photovoltaic (PV) modules - Design qualification",
            description = "Design qualification and type approval for crystalline silicon PV modules",
            sector = Sector.ENERGY,
            keywords = listOf("solar", "photovoltaic", "pv", "module", "panel", "crystalline"),
            source = Source.IEC_STANDARD,
            itemId = 61215
        ),
        StandardEntry(
            reference = "IEC 61400",
            title = "Wind energy generation systems",
            description = "Design requirements for wind turbines",
            sector = Sector.ENERGY,
            keywords = listOf("wind", "turbine", "energy", "generation", "renewable"),
            source = Source.IEC_STANDARD,
            itemId = 61400
        ),
        StandardEntry(
            reference = "IEC 62619",
            title = "Secondary lithium cells and batteries for industrial applications",
            description = "Safety requirements for lithium battery systems",
            sector = Sector.ENERGY,
            keywords = listOf("battery", "lithium", "storage", "energy", "safety"),
            source = Source.IEC_STANDARD,
            itemId = 62619
        ),
        StandardEntry(
            reference = "IEC 61850",
            title = "Communication networks and systems for power utility automation",
            description = "Standard for substation automation and smart grid communication",
            sector = Sector.ENERGY,
            keywords = listOf("smart grid", "substation", "communication", "scada", "automation"),
            source = Source.IEC_STANDARD,
            itemId = 61850
        ),
        StandardEntry(
            reference = "IEC 62446",
            title = "Photovoltaic (PV) systems - Requirements for testing, documentation and maintenance",
            description = "Grid connected PV system documentation and commissioning",
            sector = Sector.ENERGY,
            keywords = listOf("solar", "pv", "commissioning", "testing", "grid connected"),
            source = Source.IEC_STANDARD,
            itemId = 62446
        ),

        // =====================================================================
        // MECHANICAL (ISO)
        // =====================================================================
        StandardEntry(
            reference = "ISO 286",
            title = "Geometrical product specifications - ISO code system for tolerances",
            description = "Limits and fits for holes and shafts",
            sector = Sector.MECHANICAL,
            keywords = listOf("tolerance", "fit", "hole", "shaft", "dimension"),
            source = Source.ISO_STANDARD,
            itemId = 286
        ),
        StandardEntry(
            reference = "ISO 1101",
            title = "Geometrical product specifications - Geometrical tolerancing",
            description = "GD&T symbols and definitions",
            sector = Sector.MECHANICAL,
            keywords = listOf("gdt", "geometric", "tolerance", "datum", "position"),
            source = Source.ISO_STANDARD,
            itemId = 1101
        ),
        StandardEntry(
            reference = "ISO 2768",
            title = "General tolerances",
            description = "General tolerances for linear and angular dimensions",
            sector = Sector.MECHANICAL,
            keywords = listOf("tolerance", "general", "dimension", "linear", "angular"),
            source = Source.ISO_STANDARD,
            itemId = 2768
        ),
        StandardEntry(
            reference = "ISO 4414",
            title = "Pneumatic fluid power - General rules for systems",
            description = "Rules for pneumatic system design",
            sector = Sector.MECHANICAL,
            keywords = listOf("pneumatic", "air", "pressure", "cylinder", "valve"),
            source = Source.ISO_STANDARD,
            itemId = 4414
        ),
        StandardEntry(
            reference = "ISO 4413",
            title = "Hydraulic fluid power - General rules for systems",
            description = "Rules for hydraulic system design",
            sector = Sector.MECHANICAL,
            keywords = listOf("hydraulic", "fluid", "pressure", "pump", "cylinder"),
            source = Source.ISO_STANDARD,
            itemId = 4413
        ),

        // =====================================================================
        // DIGITAL (IEEE)
        // =====================================================================
        StandardEntry(
            reference = "IEEE 802.3",
            title = "Ethernet",
            description = "Standard for Ethernet networking",
            sector = Sector.DIGITAL,
            keywords = listOf("ethernet", "network", "lan", "cable", "rj45"),
            source = Source.IEEE_STANDARD,
            itemId = 8023
        ),
        StandardEntry(
            reference = "IEEE 802.11",
            title = "Wireless LAN",
            description = "Standard for Wi-Fi wireless networking",
            sector = Sector.DIGITAL,
            keywords = listOf("wifi", "wireless", "wlan", "802.11", "network"),
            source = Source.IEEE_STANDARD,
            itemId = 80211
        ),
        StandardEntry(
            reference = "IEEE 1547",
            title = "Interconnection and Interoperability of DER",
            description = "Standard for distributed energy resources interconnection",
            sector = Sector.DIGITAL,
            keywords = listOf("der", "distributed", "grid", "interconnection", "inverter"),
            source = Source.IEEE_STANDARD,
            itemId = 1547
        ),
        StandardEntry(
            reference = "IEEE 754",
            title = "Floating-Point Arithmetic",
            description = "Standard for floating-point computation",
            sector = Sector.DIGITAL,
            keywords = listOf("floating", "point", "number", "precision", "computation"),
            source = Source.IEEE_STANDARD,
            itemId = 754
        ),

        // =====================================================================
        // CONSTRUCTION (DIN/ISO)
        // =====================================================================
        StandardEntry(
            reference = "DIN 1045",
            title = "Concrete, reinforced and prestressed concrete structures",
            description = "Design and construction of concrete structures",
            sector = Sector.CONSTRUCTION,
            keywords = listOf("concrete", "reinforced", "structural", "building", "construction"),
            source = Source.DIN_STANDARD,
            itemId = 1045
        ),
        StandardEntry(
            reference = "ISO 9001",
            title = "Quality management systems",
            description = "Requirements for quality management systems",
            sector = Sector.CONSTRUCTION,
            keywords = listOf("quality", "management", "iso", "certification", "process"),
            source = Source.ISO_STANDARD,
            itemId = 9001
        ),

        // =====================================================================
        // AEROSPACE
        // =====================================================================
        StandardEntry(
            reference = "AS9100",
            title = "Quality Management Systems - Aerospace",
            description = "Quality standard for aerospace industry",
            sector = Sector.AEROSPACE,
            keywords = listOf("aerospace", "quality", "aviation", "aircraft", "certification"),
            source = Source.ISO_STANDARD,
            itemId = 9100
        ),

        // =====================================================================
        // BIOMEDICAL
        // =====================================================================
        StandardEntry(
            reference = "IEC 60601",
            title = "Medical electrical equipment",
            description = "General requirements for safety and essential performance",
            sector = Sector.BIOMEDICAL,
            keywords = listOf("medical", "device", "electrical", "safety", "patient"),
            source = Source.IEC_STANDARD,
            itemId = 60601
        ),
        StandardEntry(
            reference = "ISO 13485",
            title = "Medical devices - Quality management systems",
            description = "QMS requirements for medical device manufacturers",
            sector = Sector.BIOMEDICAL,
            keywords = listOf("medical", "device", "quality", "regulatory", "fda"),
            source = Source.ISO_STANDARD,
            itemId = 13485
        ),

        // =====================================================================
        // MATERIALS
        // =====================================================================
        StandardEntry(
            reference = "ISO 6892",
            title = "Metallic materials - Tensile testing",
            description = "Method for tensile testing of metallic materials",
            sector = Sector.MATERIALS,
            keywords = listOf("tensile", "test", "metal", "strength", "yield"),
            source = Source.ISO_STANDARD,
            itemId = 6892
        ),

        // =====================================================================
        // TRANSPORT
        // =====================================================================
        StandardEntry(
            reference = "ISO 26262",
            title = "Road vehicles - Functional safety",
            description = "Functional safety for automotive E/E systems",
            sector = Sector.TRANSPORT,
            keywords = listOf("automotive", "functional", "safety", "asil", "vehicle"),
            source = Source.ISO_STANDARD,
            itemId = 26262
        ),

        // =====================================================================
        // CHEMICAL
        // =====================================================================
        StandardEntry(
            reference = "IEC 61511",
            title = "Functional safety - Safety instrumented systems for the process industry",
            description = "SIS requirements for process plants",
            sector = Sector.CHEMICAL,
            keywords = listOf("sis", "safety", "process", "sil", "instrumented"),
            source = Source.IEC_STANDARD,
            itemId = 61511
        )
    )

    override suspend fun search(keywords: List<String>, sector: Sector): SearchHit? {
        val normalizedKeywords = keywords.map { it.lowercase() }

        // Score each standard
        val scored = standards
            .filter { it.sector == sector || sector == Sector.ELECTRICAL } // Allow cross-sector for electrical
            .map { standard ->
                val keywordMatches = standard.keywords.count { kw ->
                    normalizedKeywords.any { it.contains(kw) || kw.contains(it) }
                }
                val titleMatch = if (normalizedKeywords.any { standard.title.lowercase().contains(it) }) 2 else 0
                val refMatch = if (normalizedKeywords.any { standard.reference.lowercase().contains(it) }) 3 else 0

                val score = (keywordMatches + titleMatch + refMatch).toDouble() /
                           (standard.keywords.size + 5).toDouble()

                standard to score
            }
            .filter { it.second > 0.1 }
            .maxByOrNull { it.second }

        return scored?.let { (standard, score) ->
            SearchHit(
                value = "${standard.reference}: ${standard.title}",
                source = standard.source,
                itemId = standard.itemId,
                citation = "${standard.reference} - ${standard.description}",
                relevanceScore = score.coerceIn(0.0, 1.0)
            )
        }
    }

    override suspend fun getByReference(reference: String): SearchHit? {
        val standard = standards.find {
            it.reference.equals(reference, ignoreCase = true) ||
            it.reference.replace(" ", "").equals(reference.replace(" ", ""), ignoreCase = true)
        }

        return standard?.let {
            SearchHit(
                value = "${it.reference}: ${it.title}",
                source = it.source,
                itemId = it.itemId,
                citation = "${it.reference} - ${it.description}",
                relevanceScore = 1.0
            )
        }
    }

    /**
     * Get all standards for a sector
     */
    fun getStandardsBySector(sector: Sector): List<StandardEntry> {
        return standards.filter { it.sector == sector }
    }

    /**
     * Get standard count
     */
    fun getStandardCount(): Int = standards.size
}
