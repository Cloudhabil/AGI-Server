/**
 * Unit Tests for Unit Conversion System
 * ======================================
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-26
 */

package com.brahim.buim.industry

import com.brahim.buim.industry.db.UnitConversionTable
import com.brahim.buim.industry.db.UnitCategory
import org.junit.Assert.*
import org.junit.Test

class UnitConversionTest {

    // =========================================================================
    // Length Conversions
    // =========================================================================

    @Test
    fun `convert meters to feet`() {
        val result = UnitConversionTable.convert(1.0, "m", "ft")
        assertNotNull(result)
        assertEquals(3.28084, result!!, 0.0001)
    }

    @Test
    fun `convert inches to millimeters`() {
        val result = UnitConversionTable.convert(1.0, "in", "mm")
        assertNotNull(result)
        assertEquals(25.4, result!!, 0.0001)
    }

    @Test
    fun `convert kilometers to miles`() {
        val result = UnitConversionTable.convert(100.0, "km", "mi")
        assertNotNull(result)
        assertEquals(62.137, result!!, 0.001)
    }

    // =========================================================================
    // Energy Conversions
    // =========================================================================

    @Test
    fun `convert kWh to MJ`() {
        val result = UnitConversionTable.convert(1.0, "kWh", "MJ")
        assertNotNull(result)
        assertEquals(3.6, result!!, 0.001)
    }

    @Test
    fun `convert BTU to joules`() {
        val result = UnitConversionTable.convert(1.0, "BTU", "J")
        assertNotNull(result)
        assertEquals(1055.06, result!!, 0.1)
    }

    @Test
    fun `convert MWh to kWh`() {
        val result = UnitConversionTable.convert(1.0, "MWh", "kWh")
        assertNotNull(result)
        assertEquals(1000.0, result!!, 0.001)
    }

    // =========================================================================
    // Power Conversions
    // =========================================================================

    @Test
    fun `convert horsepower to kW`() {
        val result = UnitConversionTable.convert(1.0, "hp", "kW")
        assertNotNull(result)
        assertEquals(0.7457, result!!, 0.0001)
    }

    @Test
    fun `convert MW to W`() {
        val result = UnitConversionTable.convert(1.0, "MW", "W")
        assertNotNull(result)
        assertEquals(1e6, result!!, 1.0)
    }

    // =========================================================================
    // Pressure Conversions
    // =========================================================================

    @Test
    fun `convert bar to psi`() {
        val result = UnitConversionTable.convert(1.0, "bar", "psi")
        assertNotNull(result)
        assertEquals(14.5038, result!!, 0.001)
    }

    @Test
    fun `convert atm to kPa`() {
        val result = UnitConversionTable.convert(1.0, "atm", "kPa")
        assertNotNull(result)
        assertEquals(101.325, result!!, 0.001)
    }

    @Test
    fun `convert MPa to bar`() {
        val result = UnitConversionTable.convert(1.0, "MPa", "bar")
        assertNotNull(result)
        assertEquals(10.0, result!!, 0.001)
    }

    // =========================================================================
    // Electrical Conversions
    // =========================================================================

    @Test
    fun `convert kV to V`() {
        val result = UnitConversionTable.convert(1.0, "kV", "V")
        assertNotNull(result)
        assertEquals(1000.0, result!!, 0.001)
    }

    @Test
    fun `convert uF to nF`() {
        val result = UnitConversionTable.convert(1.0, "µF", "nF")
        assertNotNull(result)
        assertEquals(1000.0, result!!, 0.001)
    }

    @Test
    fun `convert mA to A`() {
        val result = UnitConversionTable.convert(500.0, "mA", "A")
        assertNotNull(result)
        assertEquals(0.5, result!!, 0.001)
    }

    // =========================================================================
    // Temperature Conversions (Special)
    // =========================================================================

    @Test
    fun `convert Celsius to Fahrenheit`() {
        val result = UnitConversionTable.convertTemperature(100.0, "C", "F")
        assertNotNull(result)
        assertEquals(212.0, result!!, 0.001)
    }

    @Test
    fun `convert Fahrenheit to Celsius`() {
        val result = UnitConversionTable.convertTemperature(32.0, "F", "C")
        assertNotNull(result)
        assertEquals(0.0, result!!, 0.001)
    }

    @Test
    fun `convert Celsius to Kelvin`() {
        val result = UnitConversionTable.convertTemperature(25.0, "C", "K")
        assertNotNull(result)
        assertEquals(298.15, result!!, 0.001)
    }

    @Test
    fun `absolute zero conversions`() {
        val celsius = UnitConversionTable.convertTemperature(0.0, "K", "C")
        assertEquals(-273.15, celsius!!, 0.001)

        val fahrenheit = UnitConversionTable.convertTemperature(0.0, "K", "F")
        assertEquals(-459.67, fahrenheit!!, 0.01)
    }

    // =========================================================================
    // Mass Conversions
    // =========================================================================

    @Test
    fun `convert kg to lb`() {
        val result = UnitConversionTable.convert(1.0, "kg", "lb")
        assertNotNull(result)
        assertEquals(2.20462, result!!, 0.0001)
    }

    @Test
    fun `convert metric ton to kg`() {
        val result = UnitConversionTable.convert(1.0, "t", "kg")
        assertNotNull(result)
        assertEquals(1000.0, result!!, 0.001)
    }

    // =========================================================================
    // Volume Conversions
    // =========================================================================

    @Test
    fun `convert liters to gallons`() {
        val result = UnitConversionTable.convert(3.78541, "L", "gal")
        assertNotNull(result)
        assertEquals(1.0, result!!, 0.001)
    }

    @Test
    fun `convert cubic meters to liters`() {
        val result = UnitConversionTable.convert(1.0, "m³", "L")
        assertNotNull(result)
        assertEquals(1000.0, result!!, 0.001)
    }

    // =========================================================================
    // Error Handling
    // =========================================================================

    @Test
    fun `incompatible categories return null`() {
        val result = UnitConversionTable.convert(1.0, "m", "kg")
        assertNull(result)
    }

    @Test
    fun `unknown unit returns null`() {
        val result = UnitConversionTable.convert(1.0, "xyz", "m")
        assertNull(result)
    }

    @Test
    fun `findUnit with alias works`() {
        val unit = UnitConversionTable.findUnit("micron")
        assertNotNull(unit)
        assertEquals("µm", unit!!.symbol)
    }

    // =========================================================================
    // Category Tests
    // =========================================================================

    @Test
    fun `all categories have units`() {
        UnitCategory.values().forEach { category ->
            val units = UnitConversionTable.getUnitsByCategory(category)
            assertTrue("Category $category should have units", units.isNotEmpty())
        }
    }

    @Test
    fun `format conversion produces readable output`() {
        val result = UnitConversionTable.formatConversion(100.0, "km", "mi")
        assertNotNull(result)
        assertTrue(result!!.contains("km"))
        assertTrue(result.contains("mi"))
        assertTrue(result.contains("62"))  // ~62.137 miles
    }

    // =========================================================================
    // Velocity Conversions
    // =========================================================================

    @Test
    fun `convert km/h to m/s`() {
        val result = UnitConversionTable.convert(36.0, "km/h", "m/s")
        assertNotNull(result)
        assertEquals(10.0, result!!, 0.001)
    }

    @Test
    fun `convert mph to km/h`() {
        val result = UnitConversionTable.convert(60.0, "mph", "km/h")
        assertNotNull(result)
        assertEquals(96.5606, result!!, 0.001)
    }

    // =========================================================================
    // Angular Conversions
    // =========================================================================

    @Test
    fun `convert degrees to radians`() {
        val result = UnitConversionTable.convert(180.0, "°", "rad")
        assertNotNull(result)
        assertEquals(3.14159, result!!, 0.0001)
    }

    @Test
    fun `convert revolutions to degrees`() {
        val result = UnitConversionTable.convert(1.0, "rev", "°")
        assertNotNull(result)
        assertEquals(360.0, result!!, 0.1)
    }
}
