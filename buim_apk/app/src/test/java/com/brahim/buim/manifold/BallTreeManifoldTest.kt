/**
 * Ball Tree Manifold Unit Tests
 * =============================
 *
 * Verifies the 384-D Ball Tree search functionality.
 *
 * Author: Elias Oulad Brahim
 * Date: 2026-01-25
 */

package com.brahim.buim.manifold

import org.junit.Test
import org.junit.Before
import org.junit.Assert.*
import kotlin.math.sqrt

class BallTreeManifoldTest {

    private lateinit var ballTree: BallTreeManifold

    @Before
    fun setup() {
        ballTree = BallTreeManifold()
    }

    @Test
    fun `initial ball tree is empty`() {
        val stats = ballTree.getStats()
        assertEquals(0, stats["size"])
    }

    @Test
    fun `insert increases size`() {
        val vector = createTestVector("test1")
        ballTree.insert(vector)

        val stats = ballTree.getStats()
        assertEquals(1, stats["size"])
    }

    @Test
    fun `search returns correct number of results`() {
        // Insert multiple vectors
        repeat(10) { i ->
            ballTree.insert(createTestVector("test$i"))
        }

        val query = DoubleArray(384) { 0.1 }
        val results = ballTree.search(query, k = 5)

        assertEquals(5, results.size)
    }

    @Test
    fun `search returns results sorted by score`() {
        repeat(10) { i ->
            ballTree.insert(createTestVector("test$i", seed = i))
        }

        val query = DoubleArray(384) { 0.5 }
        val results = ballTree.search(query, k = 5)

        // Results should be sorted by score (descending)
        for (i in 0 until results.size - 1) {
            assertTrue(results[i].score >= results[i + 1].score)
        }
    }

    @Test
    fun `exact match returns high score`() {
        val embedding = DoubleArray(384) { 0.1 }
        val vector = EmbeddingVector(
            id = "exact",
            vector = embedding,
            skillId = "exact_skill"
        )
        ballTree.insert(vector)

        val results = ballTree.search(embedding, k = 1)

        assertEquals(1, results.size)
        assertTrue(results[0].score > 0.99)  // Should be very close to 1
    }

    @Test
    fun `hyperbolic search works`() {
        repeat(5) { i ->
            ballTree.insert(createTestVector("test$i"))
        }

        val query = DoubleArray(384) { 0.1 }
        val results = ballTree.search(query, k = 3, hyperbolic = true)

        assertNotNull(results)
        assertTrue(results.size <= 3)
    }

    @Test
    fun `clear removes all vectors`() {
        repeat(10) { i ->
            ballTree.insert(createTestVector("test$i"))
        }

        ballTree.clear()

        val stats = ballTree.getStats()
        assertEquals(0, stats["size"])
    }

    @Test
    fun `quantizer reduces dimensionality`() {
        val quantizer = Quantizer()
        val fullVector = DoubleArray(384) { it.toDouble() / 384 }

        val quantized = quantizer.quantize(fullVector)

        assertTrue(quantized.size <= fullVector.size)
    }

    @Test
    fun `quantizer preserves relative ordering`() {
        val quantizer = Quantizer()
        val vector1 = DoubleArray(384) { 0.1 }
        val vector2 = DoubleArray(384) { 0.9 }

        val q1 = quantizer.quantize(vector1)
        val q2 = quantizer.quantize(vector2)

        // Average value of q2 should be higher than q1
        val avg1 = q1.average()
        val avg2 = q2.average()
        assertTrue(avg2 > avg1)
    }

    @Test
    fun `hyperbolic space distance is non-negative`() {
        val space = HyperbolicSpace()
        val p1 = doubleArrayOf(0.1, 0.1)
        val p2 = doubleArrayOf(0.5, 0.5)

        val distance = space.poincareDistance(p1, p2)

        assertTrue(distance >= 0)
    }

    @Test
    fun `hyperbolic distance to self is zero`() {
        val space = HyperbolicSpace()
        val p = doubleArrayOf(0.1, 0.2)

        val distance = space.poincareDistance(p, p)

        assertEquals(0.0, distance, 0.0001)
    }

    @Test
    fun `embedding vector equals by id`() {
        val v1 = createTestVector("test")
        val v2 = createTestVector("test")

        assertEquals(v1, v2)
    }

    @Test
    fun `search result contains correct skill id`() {
        val vector = EmbeddingVector(
            id = "my_id",
            vector = DoubleArray(384) { 0.5 },
            skillId = "my_skill"
        )
        ballTree.insert(vector)

        val results = ballTree.search(DoubleArray(384) { 0.5 }, k = 1)

        assertEquals("my_skill", results[0].vector.skillId)
    }

    @Test
    fun `get stats returns valid map`() {
        repeat(3) { i ->
            ballTree.insert(createTestVector("test$i"))
        }

        val stats = ballTree.getStats()

        assertTrue(stats.containsKey("size"))
        assertTrue(stats.containsKey("dimension"))
        assertEquals(3, stats["size"])
        assertEquals(384, stats["dimension"])
    }

    // Helper function to create test vectors
    private fun createTestVector(id: String, seed: Int = 0): EmbeddingVector {
        val embedding = DoubleArray(384) { (it + seed).toDouble() / 384 }
        // Normalize
        val norm = sqrt(embedding.map { it * it }.sum())
        for (i in embedding.indices) {
            embedding[i] /= norm
        }

        return EmbeddingVector(
            id = id,
            vector = embedding,
            skillId = "${id}_skill"
        )
    }
}
