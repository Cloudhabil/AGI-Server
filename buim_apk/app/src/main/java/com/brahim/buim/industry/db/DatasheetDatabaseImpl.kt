/**
 * Datasheet Database Implementation
 * ==================================
 *
 * Component and product specifications database.
 * Manufacturer-level trust (99%).
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry.db

import com.brahim.buim.industry.*

/**
 * Component datasheet entry
 */
data class DatasheetEntry(
    val partNumber: String,
    val manufacturer: String,
    val description: String,
    val category: String,
    val specs: Map<String, String>,   // Key specs
    val sector: Sector,
    val keywords: List<String>,
    val itemId: Long
)

/**
 * Embedded Datasheet Database
 *
 * Contains common component specifications for quick lookup.
 */
class DatasheetDatabaseImpl : DatasheetDatabase {

    private val datasheets: List<DatasheetEntry> = listOf(
        // =====================================================================
        // ELECTRICAL COMPONENTS
        // =====================================================================
        DatasheetEntry(
            partNumber = "LM7805",
            manufacturer = "Texas Instruments / ON Semi",
            description = "5V Linear Voltage Regulator",
            category = "Voltage Regulator",
            specs = mapOf(
                "Output Voltage" to "5V",
                "Max Input Voltage" to "35V",
                "Max Output Current" to "1.5A",
                "Dropout Voltage" to "2V",
                "Package" to "TO-220, TO-263"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("regulator", "5v", "linear", "7805", "voltage"),
            itemId = 7805
        ),
        DatasheetEntry(
            partNumber = "NE555",
            manufacturer = "Texas Instruments",
            description = "Precision Timer IC",
            category = "Timer",
            specs = mapOf(
                "Supply Voltage" to "4.5V - 16V",
                "Timing Range" to "µs to hours",
                "Max Frequency" to "500kHz",
                "Output Current" to "200mA",
                "Package" to "DIP-8, SOIC-8"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("timer", "555", "oscillator", "pwm", "pulse"),
            itemId = 555
        ),
        DatasheetEntry(
            partNumber = "IRFZ44N",
            manufacturer = "International Rectifier / Infineon",
            description = "N-Channel Power MOSFET",
            category = "MOSFET",
            specs = mapOf(
                "VDS Max" to "55V",
                "ID Max" to "49A",
                "RDS(on)" to "17.5mΩ",
                "Gate Threshold" to "2-4V",
                "Package" to "TO-220"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("mosfet", "transistor", "switch", "power", "n-channel"),
            itemId = 44
        ),
        DatasheetEntry(
            partNumber = "1N4007",
            manufacturer = "Various",
            description = "General Purpose Rectifier Diode",
            category = "Diode",
            specs = mapOf(
                "Max Reverse Voltage" to "1000V",
                "Max Forward Current" to "1A",
                "Forward Voltage Drop" to "1.1V",
                "Recovery Time" to "30µs",
                "Package" to "DO-41"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("diode", "rectifier", "1n4007", "bridge"),
            itemId = 4007
        ),
        DatasheetEntry(
            partNumber = "LM358",
            manufacturer = "Texas Instruments / ON Semi",
            description = "Dual Operational Amplifier",
            category = "Op-Amp",
            specs = mapOf(
                "Supply Voltage" to "3V - 32V (single), ±1.5V - ±16V (dual)",
                "Gain Bandwidth" to "1MHz",
                "Input Offset Voltage" to "2mV",
                "Slew Rate" to "0.5V/µs",
                "Package" to "DIP-8, SOIC-8"
            ),
            sector = Sector.ELECTRICAL,
            keywords = listOf("opamp", "amplifier", "operational", "lm358", "dual"),
            itemId = 358
        ),

        // =====================================================================
        // ENERGY / SOLAR COMPONENTS
        // =====================================================================
        DatasheetEntry(
            partNumber = "JA Solar JAM72S30-545/MR",
            manufacturer = "JA Solar",
            description = "545W Mono PERC Solar Module",
            category = "Solar Panel",
            specs = mapOf(
                "Max Power" to "545W",
                "Efficiency" to "21.3%",
                "Voc" to "49.65V",
                "Isc" to "13.92A",
                "Vmpp" to "41.52V",
                "Impp" to "13.13A",
                "Dimensions" to "2278×1134×35mm"
            ),
            sector = Sector.ENERGY,
            keywords = listOf("solar", "panel", "module", "pv", "photovoltaic", "mono", "perc"),
            itemId = 545001
        ),
        DatasheetEntry(
            partNumber = "SMA Sunny Tripower 10.0",
            manufacturer = "SMA Solar Technology",
            description = "10kW Three-Phase Solar Inverter",
            category = "Inverter",
            specs = mapOf(
                "Max DC Power" to "15kW",
                "Max AC Power" to "10kW",
                "Max Efficiency" to "98.4%",
                "MPP Voltage Range" to "175V - 800V",
                "Max Input Current" to "33A",
                "AC Output" to "3-phase 400V"
            ),
            sector = Sector.ENERGY,
            keywords = listOf("inverter", "solar", "sma", "three phase", "grid"),
            itemId = 100001
        ),
        DatasheetEntry(
            partNumber = "BYD Battery-Box Premium HVS",
            manufacturer = "BYD",
            description = "High Voltage Lithium Battery System",
            category = "Battery Storage",
            specs = mapOf(
                "Usable Capacity" to "5.12kWh per module",
                "Nominal Voltage" to "204.8V",
                "Max Charge/Discharge" to "5.12kW",
                "Round-trip Efficiency" to "95.3%",
                "Cycles" to ">6000 @ 90% DoD",
                "Chemistry" to "LiFePO4"
            ),
            sector = Sector.ENERGY,
            keywords = listOf("battery", "storage", "lithium", "byd", "lfp", "lifepo4"),
            itemId = 512001
        ),
        DatasheetEntry(
            partNumber = "Fronius Symo GEN24 10.0 Plus",
            manufacturer = "Fronius",
            description = "Hybrid Inverter with Battery Interface",
            category = "Hybrid Inverter",
            specs = mapOf(
                "Max PV Power" to "15kW",
                "Max AC Power" to "10kW",
                "Battery Interface" to "48V",
                "Backup Power" to "5kW",
                "Max Efficiency" to "98.0%"
            ),
            sector = Sector.ENERGY,
            keywords = listOf("hybrid", "inverter", "battery", "backup", "fronius"),
            itemId = 100002
        ),

        // =====================================================================
        // MECHANICAL COMPONENTS
        // =====================================================================
        DatasheetEntry(
            partNumber = "SKF 6205-2RS",
            manufacturer = "SKF",
            description = "Deep Groove Ball Bearing",
            category = "Bearing",
            specs = mapOf(
                "Inner Diameter" to "25mm",
                "Outer Diameter" to "52mm",
                "Width" to "15mm",
                "Dynamic Load Rating" to "14.8kN",
                "Static Load Rating" to "7.8kN",
                "Max Speed" to "11000 RPM"
            ),
            sector = Sector.MECHANICAL,
            keywords = listOf("bearing", "ball", "skf", "6205", "deep groove"),
            itemId = 6205
        ),
        DatasheetEntry(
            partNumber = "Festo DSBC-50-100-PPVA-N3",
            manufacturer = "Festo",
            description = "ISO 15552 Pneumatic Cylinder",
            category = "Pneumatic Cylinder",
            specs = mapOf(
                "Bore" to "50mm",
                "Stroke" to "100mm",
                "Operating Pressure" to "1-10 bar",
                "Theoretical Force" to "1178N @ 6 bar",
                "Cushioning" to "Adjustable"
            ),
            sector = Sector.MECHANICAL,
            keywords = listOf("cylinder", "pneumatic", "festo", "actuator", "iso"),
            itemId = 50100
        ),

        // =====================================================================
        // DIGITAL / SENSORS
        // =====================================================================
        DatasheetEntry(
            partNumber = "DHT22 / AM2302",
            manufacturer = "Aosong",
            description = "Digital Temperature and Humidity Sensor",
            category = "Sensor",
            specs = mapOf(
                "Temperature Range" to "-40°C to 80°C",
                "Temperature Accuracy" to "±0.5°C",
                "Humidity Range" to "0-100% RH",
                "Humidity Accuracy" to "±2% RH",
                "Interface" to "1-Wire digital"
            ),
            sector = Sector.DIGITAL,
            keywords = listOf("sensor", "temperature", "humidity", "dht22", "digital"),
            itemId = 2302
        ),
        DatasheetEntry(
            partNumber = "ESP32-WROOM-32",
            manufacturer = "Espressif",
            description = "WiFi + Bluetooth MCU Module",
            category = "Microcontroller",
            specs = mapOf(
                "CPU" to "Dual-core Xtensa 240MHz",
                "Flash" to "4MB",
                "RAM" to "520KB SRAM",
                "WiFi" to "802.11 b/g/n",
                "Bluetooth" to "BLE 4.2",
                "GPIO" to "34 programmable"
            ),
            sector = Sector.DIGITAL,
            keywords = listOf("esp32", "wifi", "bluetooth", "microcontroller", "iot"),
            itemId = 32
        ),
        DatasheetEntry(
            partNumber = "Modbus RTU",
            manufacturer = "Protocol Standard",
            description = "Industrial Serial Communication Protocol",
            category = "Protocol",
            specs = mapOf(
                "Physical Layer" to "RS-485 / RS-232",
                "Baud Rate" to "9600-115200",
                "Data Format" to "8N1, 8E1, 8O1",
                "Max Devices" to "247 (RS-485)",
                "Functions" to "Read/Write Coils, Registers"
            ),
            sector = Sector.DIGITAL,
            keywords = listOf("modbus", "rtu", "protocol", "industrial", "rs485", "plc"),
            itemId = 485
        )
    )

    override suspend fun search(keywords: List<String>, sector: Sector): SearchHit? {
        val normalizedKeywords = keywords.map { it.lowercase() }

        val scored = datasheets
            .filter { it.sector == sector }
            .map { datasheet ->
                val keywordMatches = datasheet.keywords.count { kw ->
                    normalizedKeywords.any { it.contains(kw) || kw.contains(it) }
                }
                val partMatch = if (normalizedKeywords.any {
                    datasheet.partNumber.lowercase().contains(it)
                }) 5 else 0
                val categoryMatch = if (normalizedKeywords.any {
                    datasheet.category.lowercase().contains(it)
                }) 2 else 0

                val score = (keywordMatches + partMatch + categoryMatch).toDouble() /
                           (datasheet.keywords.size + 7).toDouble()

                datasheet to score
            }
            .filter { it.second > 0.1 }
            .maxByOrNull { it.second }

        return scored?.let { (datasheet, score) ->
            val specsStr = datasheet.specs.entries.take(3)
                .joinToString(", ") { "${it.key}: ${it.value}" }

            SearchHit(
                value = "${datasheet.partNumber}: ${datasheet.description} ($specsStr)",
                source = Source.MANUFACTURER_SPEC,
                itemId = datasheet.itemId,
                citation = "${datasheet.manufacturer} - ${datasheet.partNumber} Datasheet",
                relevanceScore = score.coerceIn(0.0, 1.0)
            )
        }
    }

    override suspend fun getByPartNumber(partNumber: String): SearchHit? {
        val datasheet = datasheets.find {
            it.partNumber.equals(partNumber, ignoreCase = true) ||
            it.partNumber.replace("-", "").equals(partNumber.replace("-", ""), ignoreCase = true)
        }

        return datasheet?.let {
            val specsStr = it.specs.entries.take(3)
                .joinToString(", ") { "${it.key}: ${it.value}" }

            SearchHit(
                value = "${it.partNumber}: ${it.description} ($specsStr)",
                source = Source.MANUFACTURER_SPEC,
                itemId = it.itemId,
                citation = "${it.manufacturer} - ${it.partNumber} Datasheet",
                relevanceScore = 1.0
            )
        }
    }

    /**
     * Get full datasheet details
     */
    fun getDatasheetDetails(partNumber: String): DatasheetEntry? {
        return datasheets.find { it.partNumber.equals(partNumber, ignoreCase = true) }
    }

    /**
     * Get all datasheets for a category
     */
    fun getByCategory(category: String): List<DatasheetEntry> {
        return datasheets.filter { it.category.equals(category, ignoreCase = true) }
    }

    /**
     * Get datasheet count
     */
    fun getDatasheetCount(): Int = datasheets.size
}
