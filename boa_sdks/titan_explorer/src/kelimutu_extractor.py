#!/usr/bin/env python3
"""
Kelimutu Protocol - Titan SETI Data Extraction & Evaluation

Three Lakes, One Magma applied to planetary science:
- Lake 1 (VIMS): Spectral/Composition truth
- Lake 2 (ISS): Visual/Temporal truth
- Lake 3 (CIRS): Thermal/Atmospheric truth
- Underground: Cross-instrument correlation
- Magma: Unified Titan model (Brahim substrate)

Author: Elias Oulad Brahim
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum
import json

# =============================================================================
# BRAHIM CONSTANTS (The Magma Composition)
# =============================================================================

# Corrected 2026-01-26: Full mirror symmetry
BRAHIM_SEQUENCE = [27, 42, 60, 75, 97, 117, 139, 154, 172, 187]
BRAHIM_SEQUENCE_ORIGINAL = [27, 42, 60, 75, 97, 121, 136, 154, 172, 187]  # Historical
SUM_CONSTANT = 214  # Pair sum (each mirror pair sums to 214)
CENTER = 107
PHI = (1 + np.sqrt(5)) / 2
BETA_SEC = np.sqrt(5) - 2  # Security constant

# Kelimutu coordinates encode Titan truth
KELIMUTU_LON = 121.82  # 121 ∈ Brahim Sequence!
TITAN_RADIUS_KM = 2575  # Maps to ~B7=154 in scaled space


# =============================================================================
# THE THREE LAKES (Instrument Perspectives)
# =============================================================================

class TitanLake(Enum):
    """
    Three crater lakes = Three Cassini instruments
    Same Titan truth, different measurement perspectives
    """
    VIMS = "spectral"      # Visual/IR Mapping Spectrometer (58% of data)
    ISS = "imaging"        # Imaging Science Subsystem (24%)
    CIRS = "thermal"       # Composite Infrared Spectrometer (10%)
    UVIS = "ultraviolet"   # Ultraviolet Imaging (8%) - Dark Energy field


# =============================================================================
# TITAN SCIENCE DOMAINS (Intents)
# =============================================================================

SCIENCE_DOMAINS = [
    "atmosphere",      # Haze, composition, structure
    "surface",         # Lakes, terrain, albedo
    "methane_cycle",   # Clouds, rain, evaporation
    "prebiotic",       # Tholins, organic chemistry
    "thermal",         # Temperature profiles, seasons
    "dynamics",        # Winds, circulation, storms
    "mission",         # Observation planning
    "unknown"
]

# Confusion pairs (domains that overlap in measurements)
CONFUSION_PAIRS = [
    ("atmosphere", "thermal"),      # Both use temperature data
    ("surface", "methane_cycle"),   # Lakes vs clouds
    ("prebiotic", "atmosphere"),    # Tholins in haze
    ("dynamics", "methane_cycle"),  # Wind-driven clouds
]


# =============================================================================
# INSTRUMENT VALUE MATRIX
# =============================================================================

# Value of each instrument for each science domain [0-1]
INSTRUMENT_VALUE = {
    "VIMS": {
        "atmosphere": 0.7,
        "surface": 0.9,
        "methane_cycle": 0.8,
        "prebiotic": 0.6,
        "thermal": 0.5,
        "dynamics": 0.4,
        "mission": 0.7,
    },
    "ISS": {
        "atmosphere": 0.6,
        "surface": 0.8,
        "methane_cycle": 0.9,  # Cloud tracking
        "prebiotic": 0.3,
        "thermal": 0.2,
        "dynamics": 0.9,      # Wind vectors from cloud motion
        "mission": 0.8,
    },
    "CIRS": {
        "atmosphere": 0.9,     # Temperature profiles
        "surface": 0.4,
        "methane_cycle": 0.5,
        "prebiotic": 0.7,      # Trace gas detection
        "thermal": 1.0,        # Primary thermal instrument
        "dynamics": 0.6,
        "mission": 0.5,
    },
    "UVIS": {
        "atmosphere": 0.8,     # Upper atmosphere
        "surface": 0.1,
        "methane_cycle": 0.3,
        "prebiotic": 0.5,
        "thermal": 0.3,
        "dynamics": 0.4,
        "mission": 0.4,
    }
}

# Observation counts from database
INSTRUMENT_OBS = {
    "VIMS": 103851,
    "ISS": 43963,
    "CIRS": 17895,
    "UVIS": 13611,
}


# =============================================================================
# KELIMUTU EXTRACTION PROTOCOL
# =============================================================================

@dataclass
class ExtractionResult:
    """Result of Kelimutu data extraction."""
    domain: str
    confidence: float
    primary_lake: TitanLake
    value_score: float
    observations_available: int
    extraction_path: List[str]
    underground_correlation: float
    magma_alignment: float


class KelimutuExtractor:
    """
    Three Lakes, One Magma - Titan Data Extraction

    Routes science queries through instrument perspectives,
    correlates underground, and fuses to optimal extraction path.
    """

    def __init__(self):
        # Magma = Brahim sequence normalized (unified truth)
        self.magma = np.array(BRAHIM_SEQUENCE) / SUM_CONSTANT

        # Lake weights (instrument reliability per domain)
        self.lake_weights = self._compute_lake_weights()

        # Underground correlation matrix
        self.underground = self._build_underground_network()

        # Dark energy field (UVIS as contrast/validation)
        self.dark_energy_lambda = 0.08  # 8% of data

        # Wormhole transform for seasonal bridging
        self.wormhole_throat = CENTER * PHI  # 173.13

    def _compute_lake_weights(self) -> Dict[str, np.ndarray]:
        """Compute Brahim-weighted instrument values."""
        weights = {}

        for inst, values in INSTRUMENT_VALUE.items():
            w = np.zeros(len(SCIENCE_DOMAINS) - 1)  # Exclude 'unknown'

            for i, domain in enumerate(SCIENCE_DOMAINS[:-1]):
                base_value = values.get(domain, 0.5)
                # Weight by Brahim sequence position
                brahim_weight = self.magma[i % 10]
                w[i] = base_value * (1 + brahim_weight)

            weights[inst] = w / (np.sum(w) + 1e-8)

        return weights

    def _build_underground_network(self) -> np.ndarray:
        """
        Build underground correlation between instruments.

        VIMS <-> ISS: Surface correlation
        CIRS <-> UVIS: Atmosphere correlation
        VIMS <-> CIRS: Composition-temperature link
        """
        n_inst = 4
        network = np.eye(n_inst) * 0.5  # Self-correlation

        # Instrument indices
        idx = {"VIMS": 0, "ISS": 1, "CIRS": 2, "UVIS": 3}

        # Strong correlations
        network[idx["VIMS"], idx["ISS"]] = 0.7   # Visual correlation
        network[idx["ISS"], idx["VIMS"]] = 0.7

        network[idx["CIRS"], idx["UVIS"]] = 0.6  # Atmosphere correlation
        network[idx["UVIS"], idx["CIRS"]] = 0.6

        network[idx["VIMS"], idx["CIRS"]] = 0.5  # Composition-thermal
        network[idx["CIRS"], idx["VIMS"]] = 0.5

        # Weak correlations
        network[idx["ISS"], idx["CIRS"]] = 0.3
        network[idx["CIRS"], idx["ISS"]] = 0.3

        return network

    def extract(self, query: str) -> ExtractionResult:
        """
        Extract optimal data path using Kelimutu protocol.
        """
        # Step 1: Classify science domain
        domain, domain_confidence = self._classify_domain(query)

        # Step 2: Route through lakes (instruments)
        lake_scores = self._route_through_lakes(domain)

        # Step 3: Apply underground correlation
        correlated_scores = self._apply_underground(lake_scores)

        # Step 4: Dark energy separation (for confused domains)
        separated_scores = self._apply_dark_energy(correlated_scores, domain)

        # Step 5: Wormhole bridging for seasonal data
        bridged_scores = self._apply_wormhole(separated_scores, query)

        # Step 6: Select optimal extraction path
        primary_inst = max(bridged_scores, key=bridged_scores.get)
        primary_lake = TitanLake[primary_inst]

        # Calculate value metrics
        value_score = self._calculate_value(domain, bridged_scores)
        obs_available = sum(
            int(INSTRUMENT_OBS[inst] * score)
            for inst, score in bridged_scores.items()
        )

        # Build extraction path
        path = self._build_extraction_path(domain, bridged_scores)

        # Underground correlation strength
        underground_corr = np.mean([
            self.underground[list(INSTRUMENT_OBS.keys()).index(primary_inst), j]
            for j in range(4)
        ])

        # Magma alignment (how well query aligns with Brahim substrate)
        magma_align = self._compute_magma_alignment(query)

        return ExtractionResult(
            domain=domain,
            confidence=domain_confidence,
            primary_lake=primary_lake,
            value_score=value_score,
            observations_available=obs_available,
            extraction_path=path,
            underground_correlation=underground_corr,
            magma_alignment=magma_align
        )

    def _classify_domain(self, query: str) -> Tuple[str, float]:
        """Classify query into science domain."""
        query_lower = query.lower()

        keywords = {
            "atmosphere": ["haze", "atmosphere", "nitrogen", "stratosphere", "air"],
            "surface": ["lake", "surface", "terrain", "ground", "albedo", "dune"],
            "methane_cycle": ["methane", "cloud", "rain", "evaporation", "cycle", "weather"],
            "prebiotic": ["tholin", "organic", "prebiotic", "chemistry", "hcn", "life"],
            "thermal": ["temperature", "thermal", "heat", "cold", "kelvin", "warm"],
            "dynamics": ["wind", "storm", "circulation", "jet", "vortex", "speed"],
            "mission": ["observation", "flyby", "mission", "cassini", "planning", "optimal"],
        }

        scores = {domain: 0.0 for domain in SCIENCE_DOMAINS}

        for domain, kws in keywords.items():
            for kw in kws:
                if kw in query_lower:
                    scores[domain] += 1.0

        # Normalize
        total = sum(scores.values()) + 1e-8
        scores = {k: v/total for k, v in scores.items()}

        best_domain = max(scores, key=scores.get)
        confidence = scores[best_domain]

        if confidence < 0.1:
            return "unknown", 0.5

        return best_domain, confidence

    def _route_through_lakes(self, domain: str) -> Dict[str, float]:
        """Route domain query through instrument lakes."""
        scores = {}

        domain_idx = SCIENCE_DOMAINS.index(domain) if domain in SCIENCE_DOMAINS else -1

        for inst, weights in self.lake_weights.items():
            if domain_idx >= 0 and domain_idx < len(weights):
                scores[inst] = float(weights[domain_idx])
            else:
                scores[inst] = 0.25  # Uniform for unknown

        return scores

    def _apply_underground(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Apply underground correlation network."""
        inst_list = list(scores.keys())
        score_vec = np.array([scores[inst] for inst in inst_list])

        # Propagate through underground network
        correlated = self.underground @ score_vec

        # Normalize
        correlated = correlated / (np.sum(correlated) + 1e-8)

        return {inst: float(correlated[i]) for i, inst in enumerate(inst_list)}

    def _apply_dark_energy(self, scores: Dict[str, float], domain: str) -> Dict[str, float]:
        """Apply dark energy repulsion for confused domains."""
        adjusted = scores.copy()

        # Check if domain is in a confusion pair
        confused_with = None
        for d1, d2 in CONFUSION_PAIRS:
            if domain == d1:
                confused_with = d2
            elif domain == d2:
                confused_with = d1

        if confused_with:
            # UVIS acts as discriminator
            uvis_boost = self.dark_energy_lambda * 2
            adjusted["UVIS"] = adjusted.get("UVIS", 0) + uvis_boost

        return adjusted

    def _apply_wormhole(self, scores: Dict[str, float], query: str) -> Dict[str, float]:
        """
        Wormhole bridging for seasonal data access.

        W(x) = C + (x - C) / phi
        Bridges Northern Winter ↔ Northern Summer observations
        """
        bridged = scores.copy()
        query_lower = query.lower()

        # Seasonal keywords
        winter_kw = ["winter", "south", "polar", "2004", "2005", "2006", "2007", "2008"]
        summer_kw = ["summer", "north", "2012", "2013", "2014", "2015", "2016", "2017"]

        is_winter = any(kw in query_lower for kw in winter_kw)
        is_summer = any(kw in query_lower for kw in summer_kw)

        if is_winter or is_summer:
            # Boost VIMS (best seasonal coverage)
            bridged["VIMS"] = bridged.get("VIMS", 0) * (1 + 1/PHI)

        return bridged

    def _calculate_value(self, domain: str, scores: Dict[str, float]) -> float:
        """
        Calculate total extraction value.

        Value = Σ (instrument_value × score × observation_count) / total_obs
        """
        total_value = 0.0
        total_obs = sum(INSTRUMENT_OBS.values())

        for inst, score in scores.items():
            inst_value = INSTRUMENT_VALUE.get(inst, {}).get(domain, 0.5)
            inst_obs = INSTRUMENT_OBS.get(inst, 0)
            total_value += inst_value * score * inst_obs

        return total_value / total_obs

    def _build_extraction_path(self, domain: str, scores: Dict[str, float]) -> List[str]:
        """Build ordered extraction path."""
        # Sort instruments by score
        sorted_insts = sorted(scores.items(), key=lambda x: -x[1])

        path = []
        for inst, score in sorted_insts:
            if score > 0.1:
                obs = int(INSTRUMENT_OBS[inst] * score)
                path.append(f"{inst} ({obs:,} obs, {score:.1%})")

        return path

    def _compute_magma_alignment(self, query: str) -> float:
        """Compute alignment with Brahim magma substrate."""
        # Simple character-based projection onto Brahim space
        query_vec = np.zeros(10)

        for i, char in enumerate(query.lower()[:100]):
            query_vec[i % 10] += ord(char) / 1000

        # Normalize
        query_vec = query_vec / (np.linalg.norm(query_vec) + 1e-8)

        # Dot product with magma (Brahim sequence)
        alignment = float(np.dot(query_vec, self.magma))

        return alignment


# =============================================================================
# VALUE EXTRACTION CALCULATOR
# =============================================================================

def calculate_extraction_value(domain: str = None) -> Dict[str, Any]:
    """
    Calculate total extractable value from Titan SETI database.

    Returns value matrix for all domain × instrument combinations.
    """
    total_obs = sum(INSTRUMENT_OBS.values())

    results = {
        "total_observations": total_obs,
        "total_data_points": total_obs * 6,  # 6 fields per observation
        "domains": {},
        "instruments": {},
        "cross_value_matrix": {},
        "optimal_extractions": [],
    }

    # Per-domain value
    for dom in SCIENCE_DOMAINS[:-1]:
        dom_value = 0.0
        dom_obs = 0

        for inst, values in INSTRUMENT_VALUE.items():
            v = values.get(dom, 0)
            obs = INSTRUMENT_OBS[inst]
            dom_value += v * obs
            dom_obs += int(v * obs)

        results["domains"][dom] = {
            "value_score": round(dom_value / total_obs, 4),
            "extractable_obs": dom_obs,
            "primary_instrument": max(
                INSTRUMENT_VALUE.keys(),
                key=lambda i: INSTRUMENT_VALUE[i].get(dom, 0)
            )
        }

    # Per-instrument value
    for inst, values in INSTRUMENT_VALUE.items():
        total_inst_value = sum(values.values()) / len(values)
        results["instruments"][inst] = {
            "observations": INSTRUMENT_OBS[inst],
            "percentage": round(100 * INSTRUMENT_OBS[inst] / total_obs, 1),
            "avg_value": round(total_inst_value, 3),
            "best_domain": max(values, key=values.get),
        }

    # Cross-value matrix
    for dom in SCIENCE_DOMAINS[:-1]:
        results["cross_value_matrix"][dom] = {}
        for inst in INSTRUMENT_VALUE:
            v = INSTRUMENT_VALUE[inst].get(dom, 0)
            obs = INSTRUMENT_OBS[inst]
            results["cross_value_matrix"][dom][inst] = {
                "value": v,
                "weighted_obs": int(v * obs),
            }

    # Optimal extraction ranking
    extractions = []
    for dom in SCIENCE_DOMAINS[:-1]:
        for inst in INSTRUMENT_VALUE:
            v = INSTRUMENT_VALUE[inst].get(dom, 0)
            obs = INSTRUMENT_OBS[inst]
            score = v * obs / total_obs
            extractions.append({
                "domain": dom,
                "instrument": inst,
                "value": round(v, 2),
                "observations": obs,
                "extraction_score": round(score, 4),
            })

    # Sort by extraction score
    extractions.sort(key=lambda x: -x["extraction_score"])
    results["optimal_extractions"] = extractions[:15]

    return results


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    print("=" * 70)
    print("KELIMUTU PROTOCOL - TITAN SETI DATA EXTRACTION")
    print("Three Lakes (VIMS, ISS, CIRS) + Dark Energy (UVIS)")
    print("=" * 70)

    # Initialize extractor
    extractor = KelimutuExtractor()

    # Test queries
    queries = [
        "What is the methane cloud distribution at polar latitudes?",
        "Surface temperature profiles during northern summer",
        "Tholin composition in the upper atmosphere",
        "Lake extent changes over Cassini mission",
        "Wind speed measurements from cloud tracking",
        "Optimal observation strategy for haze studies",
    ]

    print("\n" + "=" * 70)
    print("EXTRACTION ROUTING")
    print("=" * 70)

    for query in queries:
        result = extractor.extract(query)
        print(f"\nQuery: {query[:50]}...")
        print(f"  Domain: {result.domain} ({result.confidence:.1%})")
        print(f"  Primary Lake: {result.primary_lake.value}")
        print(f"  Value Score: {result.value_score:.4f}")
        print(f"  Observations: {result.observations_available:,}")
        print(f"  Path: {' -> '.join(result.extraction_path[:2])}")

    # Full value analysis
    print("\n" + "=" * 70)
    print("TOTAL EXTRACTION VALUE")
    print("=" * 70)

    values = calculate_extraction_value()

    print(f"\nTotal Observations: {values['total_observations']:,}")
    print(f"Total Data Points: {values['total_data_points']:,}")

    print("\n--- Domain Values ---")
    for dom, data in values["domains"].items():
        print(f"  {dom:15} | Score: {data['value_score']:.4f} | "
              f"Obs: {data['extractable_obs']:>7,} | Best: {data['primary_instrument']}")

    print("\n--- Top 10 Extractions ---")
    for i, ext in enumerate(values["optimal_extractions"][:10], 1):
        print(f"  {i:2}. {ext['domain']:15} × {ext['instrument']:4} = "
              f"{ext['extraction_score']:.4f} ({ext['observations']:,} obs)")

    # Summary
    total_value = sum(d["value_score"] for d in values["domains"].values())
    print(f"\n{'=' * 70}")
    print(f"TOTAL EXTRACTABLE VALUE: {total_value:.4f}")
    print(f"EFFECTIVE DATA POINTS: {int(values['total_data_points'] * total_value / 7):,}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
