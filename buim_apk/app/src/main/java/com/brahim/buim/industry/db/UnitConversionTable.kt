/**
 * Unit Conversion Table
 * ======================
 *
 * Deterministic unit conversions for engineering calculations.
 * Source: Engineering handbooks and SI definitions.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry.db

/**
 * Unit category for grouping conversions
 */
enum class UnitCategory {
    LENGTH,
    AREA,
    VOLUME,
    MASS,
    FORCE,
    PRESSURE,
    ENERGY,
    POWER,
    TEMPERATURE,
    ELECTRICAL,
    TIME,
    VELOCITY,
    ANGULAR
}

/**
 * Unit definition with conversion to SI base
 */
data class UnitDefinition(
    val symbol: String,
    val name: String,
    val category: UnitCategory,
    val toSI: Double,           // Multiply by this to get SI unit
    val siUnit: String,         // The SI unit symbol
    val aliases: List<String> = emptyList()
)

/**
 * Unit Conversion Engine
 */
object UnitConversionTable {

    private val units: List<UnitDefinition> = listOf(
        // =====================================================================
        // LENGTH (SI: meter)
        // =====================================================================
        UnitDefinition("m", "meter", UnitCategory.LENGTH, 1.0, "m"),
        UnitDefinition("km", "kilometer", UnitCategory.LENGTH, 1000.0, "m"),
        UnitDefinition("cm", "centimeter", UnitCategory.LENGTH, 0.01, "m"),
        UnitDefinition("mm", "millimeter", UnitCategory.LENGTH, 0.001, "m"),
        UnitDefinition("µm", "micrometer", UnitCategory.LENGTH, 1e-6, "m", listOf("um", "micron")),
        UnitDefinition("nm", "nanometer", UnitCategory.LENGTH, 1e-9, "m"),
        UnitDefinition("in", "inch", UnitCategory.LENGTH, 0.0254, "m", listOf("inch", "\"")),
        UnitDefinition("ft", "foot", UnitCategory.LENGTH, 0.3048, "m", listOf("feet")),
        UnitDefinition("yd", "yard", UnitCategory.LENGTH, 0.9144, "m"),
        UnitDefinition("mi", "mile", UnitCategory.LENGTH, 1609.344, "m", listOf("mile")),
        UnitDefinition("nmi", "nautical mile", UnitCategory.LENGTH, 1852.0, "m"),

        // =====================================================================
        // AREA (SI: m²)
        // =====================================================================
        UnitDefinition("m²", "square meter", UnitCategory.AREA, 1.0, "m²", listOf("m2", "sqm")),
        UnitDefinition("cm²", "square centimeter", UnitCategory.AREA, 1e-4, "m²", listOf("cm2")),
        UnitDefinition("mm²", "square millimeter", UnitCategory.AREA, 1e-6, "m²", listOf("mm2")),
        UnitDefinition("km²", "square kilometer", UnitCategory.AREA, 1e6, "m²", listOf("km2")),
        UnitDefinition("ha", "hectare", UnitCategory.AREA, 10000.0, "m²"),
        UnitDefinition("in²", "square inch", UnitCategory.AREA, 6.4516e-4, "m²", listOf("in2", "sq in")),
        UnitDefinition("ft²", "square foot", UnitCategory.AREA, 0.092903, "m²", listOf("ft2", "sq ft")),
        UnitDefinition("acre", "acre", UnitCategory.AREA, 4046.86, "m²"),

        // =====================================================================
        // VOLUME (SI: m³)
        // =====================================================================
        UnitDefinition("m³", "cubic meter", UnitCategory.VOLUME, 1.0, "m³", listOf("m3", "cbm")),
        UnitDefinition("L", "liter", UnitCategory.VOLUME, 0.001, "m³", listOf("l", "liter", "litre")),
        UnitDefinition("mL", "milliliter", UnitCategory.VOLUME, 1e-6, "m³", listOf("ml")),
        UnitDefinition("cm³", "cubic centimeter", UnitCategory.VOLUME, 1e-6, "m³", listOf("cm3", "cc")),
        UnitDefinition("gal", "gallon (US)", UnitCategory.VOLUME, 0.00378541, "m³", listOf("gallon")),
        UnitDefinition("ft³", "cubic foot", UnitCategory.VOLUME, 0.0283168, "m³", listOf("ft3", "cf")),
        UnitDefinition("bbl", "barrel (oil)", UnitCategory.VOLUME, 0.158987, "m³", listOf("barrel")),

        // =====================================================================
        // MASS (SI: kg)
        // =====================================================================
        UnitDefinition("kg", "kilogram", UnitCategory.MASS, 1.0, "kg"),
        UnitDefinition("g", "gram", UnitCategory.MASS, 0.001, "kg"),
        UnitDefinition("mg", "milligram", UnitCategory.MASS, 1e-6, "kg"),
        UnitDefinition("t", "metric ton", UnitCategory.MASS, 1000.0, "kg", listOf("tonne")),
        UnitDefinition("lb", "pound", UnitCategory.MASS, 0.453592, "kg", listOf("lbs", "pound")),
        UnitDefinition("oz", "ounce", UnitCategory.MASS, 0.0283495, "kg", listOf("ounce")),
        UnitDefinition("st", "short ton", UnitCategory.MASS, 907.185, "kg"),

        // =====================================================================
        // FORCE (SI: N)
        // =====================================================================
        UnitDefinition("N", "newton", UnitCategory.FORCE, 1.0, "N"),
        UnitDefinition("kN", "kilonewton", UnitCategory.FORCE, 1000.0, "N"),
        UnitDefinition("MN", "meganewton", UnitCategory.FORCE, 1e6, "N"),
        UnitDefinition("lbf", "pound-force", UnitCategory.FORCE, 4.44822, "N"),
        UnitDefinition("kgf", "kilogram-force", UnitCategory.FORCE, 9.80665, "N"),
        UnitDefinition("dyn", "dyne", UnitCategory.FORCE, 1e-5, "N"),

        // =====================================================================
        // PRESSURE (SI: Pa)
        // =====================================================================
        UnitDefinition("Pa", "pascal", UnitCategory.PRESSURE, 1.0, "Pa"),
        UnitDefinition("kPa", "kilopascal", UnitCategory.PRESSURE, 1000.0, "Pa"),
        UnitDefinition("MPa", "megapascal", UnitCategory.PRESSURE, 1e6, "Pa"),
        UnitDefinition("bar", "bar", UnitCategory.PRESSURE, 100000.0, "Pa"),
        UnitDefinition("mbar", "millibar", UnitCategory.PRESSURE, 100.0, "Pa"),
        UnitDefinition("atm", "atmosphere", UnitCategory.PRESSURE, 101325.0, "Pa"),
        UnitDefinition("psi", "pound per square inch", UnitCategory.PRESSURE, 6894.76, "Pa"),
        UnitDefinition("mmHg", "millimeter of mercury", UnitCategory.PRESSURE, 133.322, "Pa", listOf("torr")),
        UnitDefinition("inHg", "inch of mercury", UnitCategory.PRESSURE, 3386.39, "Pa"),

        // =====================================================================
        // ENERGY (SI: J)
        // =====================================================================
        UnitDefinition("J", "joule", UnitCategory.ENERGY, 1.0, "J"),
        UnitDefinition("kJ", "kilojoule", UnitCategory.ENERGY, 1000.0, "J"),
        UnitDefinition("MJ", "megajoule", UnitCategory.ENERGY, 1e6, "J"),
        UnitDefinition("Wh", "watt-hour", UnitCategory.ENERGY, 3600.0, "J"),
        UnitDefinition("kWh", "kilowatt-hour", UnitCategory.ENERGY, 3.6e6, "J"),
        UnitDefinition("MWh", "megawatt-hour", UnitCategory.ENERGY, 3.6e9, "J"),
        UnitDefinition("cal", "calorie", UnitCategory.ENERGY, 4.184, "J"),
        UnitDefinition("kcal", "kilocalorie", UnitCategory.ENERGY, 4184.0, "J"),
        UnitDefinition("BTU", "British thermal unit", UnitCategory.ENERGY, 1055.06, "J", listOf("btu")),
        UnitDefinition("eV", "electron volt", UnitCategory.ENERGY, 1.60218e-19, "J"),

        // =====================================================================
        // POWER (SI: W)
        // =====================================================================
        UnitDefinition("W", "watt", UnitCategory.POWER, 1.0, "W"),
        UnitDefinition("kW", "kilowatt", UnitCategory.POWER, 1000.0, "W"),
        UnitDefinition("MW", "megawatt", UnitCategory.POWER, 1e6, "W"),
        UnitDefinition("GW", "gigawatt", UnitCategory.POWER, 1e9, "W"),
        UnitDefinition("hp", "horsepower", UnitCategory.POWER, 745.7, "W", listOf("HP")),
        UnitDefinition("PS", "metric horsepower", UnitCategory.POWER, 735.499, "W"),
        UnitDefinition("BTU/h", "BTU per hour", UnitCategory.POWER, 0.293071, "W"),
        UnitDefinition("ton", "ton of refrigeration", UnitCategory.POWER, 3516.85, "W"),

        // =====================================================================
        // ELECTRICAL
        // =====================================================================
        UnitDefinition("V", "volt", UnitCategory.ELECTRICAL, 1.0, "V"),
        UnitDefinition("mV", "millivolt", UnitCategory.ELECTRICAL, 0.001, "V"),
        UnitDefinition("kV", "kilovolt", UnitCategory.ELECTRICAL, 1000.0, "V"),
        UnitDefinition("A", "ampere", UnitCategory.ELECTRICAL, 1.0, "A"),
        UnitDefinition("mA", "milliampere", UnitCategory.ELECTRICAL, 0.001, "A"),
        UnitDefinition("µA", "microampere", UnitCategory.ELECTRICAL, 1e-6, "A", listOf("uA")),
        UnitDefinition("Ω", "ohm", UnitCategory.ELECTRICAL, 1.0, "Ω", listOf("ohm")),
        UnitDefinition("kΩ", "kilohm", UnitCategory.ELECTRICAL, 1000.0, "Ω", listOf("kohm")),
        UnitDefinition("MΩ", "megohm", UnitCategory.ELECTRICAL, 1e6, "Ω", listOf("Mohm")),
        UnitDefinition("F", "farad", UnitCategory.ELECTRICAL, 1.0, "F"),
        UnitDefinition("µF", "microfarad", UnitCategory.ELECTRICAL, 1e-6, "F", listOf("uF")),
        UnitDefinition("nF", "nanofarad", UnitCategory.ELECTRICAL, 1e-9, "F"),
        UnitDefinition("pF", "picofarad", UnitCategory.ELECTRICAL, 1e-12, "F"),
        UnitDefinition("H", "henry", UnitCategory.ELECTRICAL, 1.0, "H"),
        UnitDefinition("mH", "millihenry", UnitCategory.ELECTRICAL, 0.001, "H"),
        UnitDefinition("µH", "microhenry", UnitCategory.ELECTRICAL, 1e-6, "H", listOf("uH")),

        // =====================================================================
        // TIME (SI: s)
        // =====================================================================
        UnitDefinition("s", "second", UnitCategory.TIME, 1.0, "s", listOf("sec")),
        UnitDefinition("ms", "millisecond", UnitCategory.TIME, 0.001, "s"),
        UnitDefinition("µs", "microsecond", UnitCategory.TIME, 1e-6, "s", listOf("us")),
        UnitDefinition("ns", "nanosecond", UnitCategory.TIME, 1e-9, "s"),
        UnitDefinition("min", "minute", UnitCategory.TIME, 60.0, "s"),
        UnitDefinition("h", "hour", UnitCategory.TIME, 3600.0, "s", listOf("hr")),
        UnitDefinition("d", "day", UnitCategory.TIME, 86400.0, "s", listOf("day")),

        // =====================================================================
        // VELOCITY (SI: m/s)
        // =====================================================================
        UnitDefinition("m/s", "meter per second", UnitCategory.VELOCITY, 1.0, "m/s"),
        UnitDefinition("km/h", "kilometer per hour", UnitCategory.VELOCITY, 0.277778, "m/s", listOf("kph")),
        UnitDefinition("mph", "miles per hour", UnitCategory.VELOCITY, 0.44704, "m/s"),
        UnitDefinition("kn", "knot", UnitCategory.VELOCITY, 0.514444, "m/s", listOf("knot")),
        UnitDefinition("ft/s", "feet per second", UnitCategory.VELOCITY, 0.3048, "m/s"),

        // =====================================================================
        // ANGULAR (SI: rad)
        // =====================================================================
        UnitDefinition("rad", "radian", UnitCategory.ANGULAR, 1.0, "rad"),
        UnitDefinition("°", "degree", UnitCategory.ANGULAR, 0.0174533, "rad", listOf("deg")),
        UnitDefinition("'", "arcminute", UnitCategory.ANGULAR, 2.90888e-4, "rad", listOf("arcmin")),
        UnitDefinition("\"", "arcsecond", UnitCategory.ANGULAR, 4.84814e-6, "rad", listOf("arcsec")),
        UnitDefinition("rev", "revolution", UnitCategory.ANGULAR, 6.28319, "rad"),
        UnitDefinition("rpm", "revolutions per minute", UnitCategory.ANGULAR, 0.10472, "rad/s")
    )

    /**
     * Convert value between units
     */
    fun convert(value: Double, fromUnit: String, toUnit: String): Double? {
        val from = findUnit(fromUnit) ?: return null
        val to = findUnit(toUnit) ?: return null

        // Must be same category
        if (from.category != to.category) return null

        // Convert: value -> SI -> target
        val siValue = value * from.toSI
        return siValue / to.toSI
    }

    /**
     * Find unit by symbol or alias
     */
    fun findUnit(symbol: String): UnitDefinition? {
        val normalized = symbol.trim()
        return units.find {
            it.symbol.equals(normalized, ignoreCase = true) ||
            it.aliases.any { alias -> alias.equals(normalized, ignoreCase = true) }
        }
    }

    /**
     * Get all units in a category
     */
    fun getUnitsByCategory(category: UnitCategory): List<UnitDefinition> {
        return units.filter { it.category == category }
    }

    /**
     * Get all available categories
     */
    fun getCategories(): List<UnitCategory> = UnitCategory.values().toList()

    /**
     * Format conversion result
     */
    fun formatConversion(value: Double, fromUnit: String, toUnit: String): String? {
        val result = convert(value, fromUnit, toUnit) ?: return null
        val from = findUnit(fromUnit) ?: return null
        val to = findUnit(toUnit) ?: return null

        return "$value ${from.symbol} = ${"%.6g".format(result)} ${to.symbol}"
    }

    /**
     * Temperature conversion (special case - not linear)
     */
    fun convertTemperature(value: Double, from: String, to: String): Double? {
        val fromNorm = from.uppercase()
        val toNorm = to.uppercase()

        // Convert to Kelvin first
        val kelvin = when (fromNorm) {
            "K", "KELVIN" -> value
            "C", "°C", "CELSIUS" -> value + 273.15
            "F", "°F", "FAHRENHEIT" -> (value - 32) * 5/9 + 273.15
            "R", "°R", "RANKINE" -> value * 5/9
            else -> return null
        }

        // Convert from Kelvin to target
        return when (toNorm) {
            "K", "KELVIN" -> kelvin
            "C", "°C", "CELSIUS" -> kelvin - 273.15
            "F", "°F", "FAHRENHEIT" -> (kelvin - 273.15) * 9/5 + 32
            "R", "°R", "RANKINE" -> kelvin * 9/5
            else -> null
        }
    }

    /**
     * Get unit count
     */
    fun getUnitCount(): Int = units.size
}
