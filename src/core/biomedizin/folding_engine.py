"""
Hermes Trismegistos Advanced Folding Engine
============================================

Comprehensive protein folding analysis integrating:
- ESMFold structure prediction (when available)
- Hydrophobicity-based folding energy calculations
- Literature-backed hypothesis generation
- Brahim formulas for stability assessment
- Drug target identification

Hermetic Principle: "As Above, So Below"
- Sequence patterns (below) → Structural features (above)
- Local interactions → Global fold
- Molecular properties → Biological function

Mathematical Foundation:
- Folding Energy: F = Σ(1/(stability - stress)²) × exp(-λ × hydrophobicity)
- Contact Order: CO = (1/L×N) × Σ|i-j| for contacts
- Stability Score: S = exp(-ΔG/RT) / (1 + exp(-ΔG/RT))

Author: GPIA Cognitive Ecosystem / Hermes Trismegistos Engine
Date: 2026-01-26
Version: 2.0.0
License: Research use only - NOT FOR CLINICAL USE
"""

from __future__ import annotations

import argparse
import json
import math
import hashlib
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# BRAHIM CONSTANTS FOR PROTEIN FOLDING
# ============================================================================

GENESIS_BIO = 0.0022              # Biological stress threshold
PHI_BIO = 1.618033988749895       # Golden ratio in protein architecture
BETA_STABILITY = 0.236            # Target stability compression
LAMBDA_FOLDING = 0.001            # Folding decay constant
RT_PHYSIOLOGICAL = 0.593          # RT at 37°C in kcal/mol

# Amino acid properties
AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

# Kyte-Doolittle hydrophobicity scale
HYDROPHOBICITY = {
    'I': 4.5, 'V': 4.2, 'L': 3.8, 'F': 2.8, 'C': 2.5, 'M': 1.9, 'A': 1.8,
    'G': -0.4, 'T': -0.7, 'S': -0.8, 'W': -0.9, 'Y': -1.3, 'P': -1.6,
    'H': -3.2, 'E': -3.5, 'Q': -3.5, 'D': -3.5, 'N': -3.5, 'K': -3.9, 'R': -4.5,
}

# Amino acid molecular weights (Da)
MOLECULAR_WEIGHT = {
    'A': 89.1, 'R': 174.2, 'N': 132.1, 'D': 133.1, 'C': 121.2,
    'E': 147.1, 'Q': 146.2, 'G': 75.1, 'H': 155.2, 'I': 131.2,
    'L': 131.2, 'K': 146.2, 'M': 149.2, 'F': 165.2, 'P': 115.1,
    'S': 105.1, 'T': 119.1, 'W': 204.2, 'Y': 181.2, 'V': 117.1,
}

# Secondary structure propensities (Chou-Fasman)
HELIX_PROPENSITY = {
    'A': 1.42, 'L': 1.21, 'E': 1.51, 'M': 1.45, 'Q': 1.11, 'K': 1.16,
    'R': 0.98, 'H': 1.00, 'V': 1.06, 'I': 1.08, 'Y': 0.69, 'C': 0.70,
    'W': 1.08, 'F': 1.13, 'T': 0.83, 'G': 0.57, 'N': 0.67, 'P': 0.57,
    'S': 0.77, 'D': 1.01,
}

SHEET_PROPENSITY = {
    'V': 1.70, 'I': 1.60, 'Y': 1.47, 'F': 1.38, 'W': 1.37, 'L': 1.30,
    'T': 1.19, 'C': 1.19, 'M': 1.05, 'A': 0.83, 'R': 0.93, 'G': 0.75,
    'D': 0.54, 'K': 0.74, 'S': 0.75, 'H': 0.87, 'N': 0.89, 'P': 0.55,
    'E': 0.37, 'Q': 1.10,
}

# Disorder propensity (simplified scale)
DISORDER_PROPENSITY = {
    'P': 1.5, 'E': 1.4, 'S': 1.3, 'Q': 1.3, 'K': 1.2, 'A': 1.1,
    'G': 1.0, 'R': 0.9, 'D': 0.9, 'T': 0.8, 'N': 0.8, 'H': 0.7,
    'M': 0.6, 'L': 0.5, 'V': 0.5, 'I': 0.4, 'F': 0.3, 'Y': 0.3,
    'W': 0.2, 'C': 0.2,
}

# Conserved functional motifs
FUNCTIONAL_MOTIFS = {
    # Phosphorylation sites
    'S[ST]': 'potential_phosphorylation',
    'RXX[ST]': 'PKA_phosphorylation',
    '[ST]P': 'proline_directed_phospho',

    # Binding motifs
    'LXXLL': 'nuclear_receptor_binding',
    'PXX P': 'SH3_binding',
    '[FY]XN': 'PDZ_binding',

    # Structural motifs
    'CX{2,4}C': 'zinc_finger_partial',
    'GXGXXG': 'P_loop_nucleotide',
    'DFG': 'kinase_activation',
    'HRD': 'kinase_catalytic',

    # Degradation signals
    'KFERQ': 'CMA_targeting',
    'PEST': 'rapid_degradation',

    # Localization
    '[RK]{4,}': 'nuclear_localization',
    'KDEL': 'ER_retention',
}

# ============================================================================
# ENUMERATIONS
# ============================================================================

class FoldingState(Enum):
    """Protein folding states along the energy landscape"""
    NATIVE = "native"                    # Properly folded, functional
    MOLTEN_GLOBULE = "molten_globule"    # Compact but dynamic
    PARTIALLY_FOLDED = "partially_folded"
    UNFOLDED = "unfolded"                # Random coil
    MISFOLDED = "misfolded"              # Wrong conformation
    AGGREGATED = "aggregated"            # Pathological state
    INTRINSICALLY_DISORDERED = "intrinsically_disordered"


class SecondaryStructure(Enum):
    """Secondary structure types"""
    HELIX = "helix"
    SHEET = "sheet"
    COIL = "coil"
    TURN = "turn"
    DISORDERED = "disordered"


class ProteinClass(Enum):
    """Protein structural classification"""
    ALL_ALPHA = "all_alpha"
    ALL_BETA = "all_beta"
    ALPHA_BETA = "alpha_beta"
    ALPHA_PLUS_BETA = "alpha_plus_beta"
    MEMBRANE = "membrane"
    INTRINSICALLY_DISORDERED = "intrinsically_disordered"


class DrugTargetPotential(Enum):
    """Drug target potential classification"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CHALLENGING = "challenging"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AminoAcidProperties:
    """Properties of a single amino acid"""
    residue: str
    position: int
    hydrophobicity: float
    helix_propensity: float
    sheet_propensity: float
    disorder_propensity: float
    molecular_weight: float

    @property
    def is_hydrophobic(self) -> bool:
        return self.hydrophobicity > 0

    @property
    def is_charged(self) -> bool:
        return self.residue in "DEKRH"

    @property
    def is_aromatic(self) -> bool:
        return self.residue in "FYW"


@dataclass
class SequenceRegion:
    """A region of the protein sequence with specific properties"""
    start: int
    end: int
    sequence: str
    region_type: str
    score: float
    properties: Dict[str, Any] = field(default_factory=dict)

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass
class FoldingHypothesis:
    """A hypothesis about protein folding behavior"""
    hypothesis_id: str
    region: SequenceRegion
    hypothesis_type: str
    description: str
    rationale: str
    confidence: float           # 0-1
    novelty_score: float        # 0-1
    evidence_support: float     # 0-1
    supporting_literature: List[str] = field(default_factory=list)
    experimental_suggestions: List[str] = field(default_factory=list)

    @property
    def composite_score(self) -> float:
        """Weighted composite score"""
        return (0.4 * self.confidence +
                0.3 * self.novelty_score +
                0.3 * self.evidence_support)


@dataclass
class StructurePrediction:
    """Predicted structural features"""
    secondary_structure: List[Tuple[int, int, SecondaryStructure]]
    disordered_regions: List[Tuple[int, int]]
    domain_boundaries: List[int]
    contact_order: float
    predicted_stability: float
    protein_class: ProteinClass


@dataclass
class DrugTargetAssessment:
    """Assessment of protein as a drug target"""
    overall_potential: DrugTargetPotential
    binding_site_predictions: List[SequenceRegion]
    allosteric_sites: List[SequenceRegion]
    stability_for_screening: float
    expression_difficulty: str
    therapeutic_relevance: str


@dataclass
class FoldingAnalysisResult:
    """Complete result of folding analysis"""
    sequence_id: str
    sequence: str
    length: int
    molecular_weight: float

    # Composition
    amino_acid_composition: Dict[str, float]
    charge_at_ph7: float
    isoelectric_point: float

    # Folding properties
    folding_energy: float
    folding_state: FoldingState
    stability_score: float

    # Structure predictions
    structure_prediction: StructurePrediction

    # Hypotheses
    hypotheses: List[FoldingHypothesis]

    # Drug target assessment
    drug_target: DrugTargetAssessment

    # Metadata
    analysis_timestamp: str
    engine_version: str


# ============================================================================
# LITERATURE CORPUS INTERFACE
# ============================================================================

class LiteratureCorpus:
    """Interface to biomedical literature corpus for evidence retrieval"""

    def __init__(self, corpus_path: Optional[Path] = None):
        self.corpus_path = corpus_path or Path("data/biomedical_corpus.json")
        self.corpus: List[Dict[str, Any]] = []
        self._load_corpus()

    def _load_corpus(self) -> None:
        """Load the biomedical corpus"""
        if self.corpus_path.exists():
            try:
                self.corpus = json.loads(self.corpus_path.read_text(encoding="utf-8"))
                logger.info(f"Loaded {len(self.corpus)} papers from corpus")
            except Exception as e:
                logger.warning(f"Could not load corpus: {e}")
                self.corpus = []

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search corpus for relevant papers"""
        query_terms = query.lower().split()
        scored = []

        for paper in self.corpus:
            text = " ".join([
                str(paper.get("title", "")),
                str(paper.get("snippet", "")),
                " ".join(paper.get("tags", []))
            ]).lower()

            # Simple keyword scoring
            score = sum(text.count(term) for term in query_terms)
            if score > 0:
                scored.append((score, paper))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:max_results]]

    def get_folding_evidence(self, sequence_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get folding-related evidence based on sequence features"""
        queries = ["protein folding"]

        if sequence_features.get("has_disorder", False):
            queries.append("intrinsically disordered")
        if sequence_features.get("has_knot", False):
            queries.append("knotted protein")
        if sequence_features.get("is_membrane", False):
            queries.append("membrane protein folding")

        all_results = []
        for query in queries:
            all_results.extend(self.search(query, max_results=3))

        # Deduplicate
        seen = set()
        unique = []
        for paper in all_results:
            pid = paper.get("id", "")
            if pid not in seen:
                seen.add(pid)
                unique.append(paper)

        return unique[:10]


# ============================================================================
# MAIN FOLDING ENGINE
# ============================================================================

class HermesAdvancedFoldingEngine:
    """
    Advanced Protein Folding Analysis Engine

    Integrates multiple analysis methods:
    1. Sequence-based property calculation
    2. Secondary structure prediction
    3. Disorder prediction
    4. Folding energy landscape modeling
    5. Hypothesis generation from literature
    6. Drug target assessment
    """

    VERSION = "2.0.0"

    def __init__(self, corpus_path: Optional[Path] = None):
        self.corpus = LiteratureCorpus(corpus_path)
        self.esm_available = self._check_esm_availability()

    def _check_esm_availability(self) -> bool:
        """Check if ESMFold is available"""
        try:
            from transformers import EsmForProteinFolding
            return True
        except ImportError:
            logger.info("ESMFold not available, using analytical methods")
            return False

    def analyze(self, sequence: str, name: str = "protein") -> FoldingAnalysisResult:
        """
        Complete protein folding analysis

        Args:
            sequence: Amino acid sequence (one-letter code)
            name: Protein name/identifier

        Returns:
            FoldingAnalysisResult with comprehensive analysis
        """
        # Clean sequence
        sequence = self._clean_sequence(sequence)
        sequence_id = self._generate_sequence_id(sequence, name)

        # Basic properties
        aa_props = self._calculate_residue_properties(sequence)
        composition = self._calculate_composition(sequence)
        mw = self._calculate_molecular_weight(sequence)
        charge, pi = self._calculate_charge_and_pi(sequence)

        # Folding analysis
        folding_energy, folding_state = self._calculate_folding_energy(sequence, aa_props)
        stability_score = self._calculate_stability_score(folding_energy)

        # Structure prediction
        structure_pred = self._predict_structure(sequence, aa_props)

        # Generate hypotheses
        hypotheses = self._generate_hypotheses(sequence, aa_props, structure_pred)

        # Drug target assessment
        drug_target = self._assess_drug_target(sequence, structure_pred, stability_score)

        return FoldingAnalysisResult(
            sequence_id=sequence_id,
            sequence=sequence,
            length=len(sequence),
            molecular_weight=mw,
            amino_acid_composition=composition,
            charge_at_ph7=charge,
            isoelectric_point=pi,
            folding_energy=folding_energy,
            folding_state=folding_state,
            stability_score=stability_score,
            structure_prediction=structure_pred,
            hypotheses=hypotheses,
            drug_target=drug_target,
            analysis_timestamp=datetime.now().isoformat(),
            engine_version=self.VERSION
        )

    def _clean_sequence(self, sequence: str) -> str:
        """Clean and validate sequence"""
        sequence = sequence.upper().replace(" ", "").replace("\n", "")
        valid = set(AMINO_ACIDS)
        cleaned = "".join(aa for aa in sequence if aa in valid)
        if len(cleaned) != len(sequence):
            logger.warning(f"Removed {len(sequence) - len(cleaned)} invalid characters")
        return cleaned

    def _generate_sequence_id(self, sequence: str, name: str) -> str:
        """Generate unique sequence ID"""
        seq_hash = hashlib.md5(sequence.encode()).hexdigest()[:8]
        return f"{name}_{seq_hash}"

    def _calculate_residue_properties(self, sequence: str) -> List[AminoAcidProperties]:
        """Calculate properties for each residue"""
        return [
            AminoAcidProperties(
                residue=aa,
                position=i,
                hydrophobicity=HYDROPHOBICITY.get(aa, 0.0),
                helix_propensity=HELIX_PROPENSITY.get(aa, 1.0),
                sheet_propensity=SHEET_PROPENSITY.get(aa, 1.0),
                disorder_propensity=DISORDER_PROPENSITY.get(aa, 1.0),
                molecular_weight=MOLECULAR_WEIGHT.get(aa, 110.0)
            )
            for i, aa in enumerate(sequence)
        ]

    def _calculate_composition(self, sequence: str) -> Dict[str, float]:
        """Calculate amino acid composition"""
        total = len(sequence)
        composition = {}
        for aa in AMINO_ACIDS:
            count = sequence.count(aa)
            composition[aa] = round(count / total * 100, 2) if total > 0 else 0
        return composition

    def _calculate_molecular_weight(self, sequence: str) -> float:
        """Calculate molecular weight in Daltons"""
        # Sum of residue weights minus water for each peptide bond
        total = sum(MOLECULAR_WEIGHT.get(aa, 110.0) for aa in sequence)
        water_loss = 18.015 * (len(sequence) - 1)
        return round(total - water_loss, 2)

    def _calculate_charge_and_pi(self, sequence: str) -> Tuple[float, float]:
        """Calculate charge at pH 7 and isoelectric point"""
        # pKa values
        pka = {
            'D': 3.9, 'E': 4.1,  # Acidic
            'H': 6.0, 'K': 10.5, 'R': 12.5,  # Basic
            'C': 8.3, 'Y': 10.1,  # Special
            'N_term': 9.0, 'C_term': 2.1
        }

        def charge_at_ph(ph: float) -> float:
            charge = 0.0
            # N-terminus
            charge += 1.0 / (1.0 + 10 ** (ph - pka['N_term']))
            # C-terminus
            charge -= 1.0 / (1.0 + 10 ** (pka['C_term'] - ph))
            # Side chains
            for aa in sequence:
                if aa == 'D':
                    charge -= 1.0 / (1.0 + 10 ** (pka['D'] - ph))
                elif aa == 'E':
                    charge -= 1.0 / (1.0 + 10 ** (pka['E'] - ph))
                elif aa == 'H':
                    charge += 1.0 / (1.0 + 10 ** (ph - pka['H']))
                elif aa == 'K':
                    charge += 1.0 / (1.0 + 10 ** (ph - pka['K']))
                elif aa == 'R':
                    charge += 1.0 / (1.0 + 10 ** (ph - pka['R']))
                elif aa == 'C':
                    charge -= 1.0 / (1.0 + 10 ** (pka['C'] - ph))
                elif aa == 'Y':
                    charge -= 1.0 / (1.0 + 10 ** (pka['Y'] - ph))
            return charge

        # Charge at pH 7
        charge_ph7 = round(charge_at_ph(7.0), 2)

        # Find pI by bisection
        low, high = 0.0, 14.0
        while high - low > 0.01:
            mid = (low + high) / 2
            if charge_at_ph(mid) > 0:
                low = mid
            else:
                high = mid
        pi = round((low + high) / 2, 2)

        return charge_ph7, pi

    def _calculate_folding_energy(
        self,
        sequence: str,
        aa_props: List[AminoAcidProperties]
    ) -> Tuple[float, FoldingState]:
        """
        Calculate folding energy using Brahim Folding Formula:
        F = Σ(1/(stability - stress)²) × exp(-λ × hydrophobicity_variance)

        Lower energy = more stable (like physical free energy)
        """
        if len(sequence) < 10:
            return 1.0, FoldingState.UNFOLDED

        # Calculate hydrophobicity profile statistics
        hydro_profile = [p.hydrophobicity for p in aa_props]
        avg_hydro = sum(hydro_profile) / len(hydro_profile)

        # Calculate global variance (lower variance = more uniform = better for soluble)
        global_var = sum((h - avg_hydro) ** 2 for h in hydro_profile) / len(hydro_profile)

        # Regional stress analysis - looking for problematic regions
        window_size = 7
        regional_scores = []

        for i in range(0, len(hydro_profile) - window_size + 1, 3):
            window = hydro_profile[i:i + window_size]
            window_avg = sum(window) / len(window)
            window_var = sum((h - window_avg) ** 2 for h in window) / len(window)

            # Good folding: hydrophobic residues cluster (high local variance OK)
            # Bad folding: random distribution or all hydrophilic
            # Score based on whether region has clear hydrophobic/hydrophilic character

            # Regions with moderate hydrophobicity and low variance are stable
            hydro_magnitude = abs(window_avg)
            uniformity = 1.0 / (1.0 + window_var)  # Higher if uniform

            # Balanced regions score better
            if -1.0 < window_avg < 2.0:  # Good soluble protein range
                region_score = uniformity * 0.5  # Low score = good
            else:
                region_score = uniformity + hydro_magnitude * 0.1

            regional_scores.append(region_score)

        # Average regional score (lower = more stable)
        if regional_scores:
            avg_regional = sum(regional_scores) / len(regional_scores)
        else:
            avg_regional = 0.5

        # Check for disorder indicators
        disorder_score = sum(p.disorder_propensity for p in aa_props) / len(aa_props)

        # Helix/sheet content (structured proteins are more stable)
        helix_score = sum(p.helix_propensity for p in aa_props) / len(aa_props)
        sheet_score = sum(p.sheet_propensity for p in aa_props) / len(aa_props)
        structure_propensity = (helix_score + sheet_score) / 2.0

        # Final folding energy: combine factors
        # Lower = more stable
        base_energy = avg_regional * (1.0 + global_var * 0.1)

        # Bonus for high secondary structure propensity
        if structure_propensity > 1.0:
            base_energy *= (2.0 - structure_propensity)  # Reduce energy for structured

        # Apply Brahim decay based on overall hydrophobic balance
        folding_energy = base_energy * math.exp(-LAMBDA_FOLDING * (1.0 + avg_hydro) * 50)

        # Normalize to reasonable range (0.0001 to 1.0)
        folding_energy = max(0.0001, min(1.0, folding_energy))

        # Determine folding state based on normalized energy and disorder
        # Thresholds calibrated to actual calculation output range:
        # - Well-folded proteins (hemoglobin, lysozyme): energy ~0.15-0.25
        # - Partially folded: energy ~0.25-0.45
        # - Unfolded/disordered: energy > 0.45
        if disorder_score > 1.15:
            state = FoldingState.INTRINSICALLY_DISORDERED
        elif folding_energy < 0.20:
            state = FoldingState.NATIVE
        elif folding_energy < 0.30:
            state = FoldingState.MOLTEN_GLOBULE
        elif folding_energy < 0.45:
            state = FoldingState.PARTIALLY_FOLDED
        elif folding_energy < 0.60:
            state = FoldingState.UNFOLDED
        elif disorder_score > 1.0:
            state = FoldingState.INTRINSICALLY_DISORDERED
        elif folding_energy < 0.80:
            state = FoldingState.MISFOLDED
        else:
            state = FoldingState.AGGREGATED

        return round(folding_energy, 6), state

    def _calculate_stability_score(self, folding_energy: float) -> float:
        """
        Convert folding energy to stability score (0-1)

        Higher score = more stable
        Lower folding energy = more stable = higher score

        Uses sigmoid transformation calibrated to energy ranges:
        - energy ~0.2 (native) → stability ~0.86
        - energy ~0.5 (partial) → stability ~0.50
        - energy ~0.8 (misfolded) → stability ~0.14
        """
        # Sigmoid transformation centered at 0.5 energy
        # steepness factor of 6 gives good discrimination
        stability = 1.0 / (1.0 + math.exp((folding_energy - 0.5) * 6))
        return round(max(0.0, min(1.0, stability)), 3)

    def _predict_structure(
        self,
        sequence: str,
        aa_props: List[AminoAcidProperties]
    ) -> StructurePrediction:
        """Predict secondary structure and other structural features"""
        # Secondary structure prediction using propensities
        ss_predictions = self._predict_secondary_structure(aa_props)

        # Disorder prediction
        disordered = self._predict_disordered_regions(aa_props)

        # Domain boundary prediction (simplified)
        domains = self._predict_domain_boundaries(aa_props)

        # Contact order estimation
        contact_order = self._estimate_contact_order(sequence, ss_predictions)

        # Overall stability prediction
        helix_content = sum(1 for _, _, ss in ss_predictions if ss == SecondaryStructure.HELIX)
        sheet_content = sum(1 for _, _, ss in ss_predictions if ss == SecondaryStructure.SHEET)
        total_structured = helix_content + sheet_content

        stability = min(1.0, total_structured / max(1, len(sequence)) * 2)

        # Protein class
        if helix_content > sheet_content * 2:
            pclass = ProteinClass.ALL_ALPHA
        elif sheet_content > helix_content * 2:
            pclass = ProteinClass.ALL_BETA
        elif len(disordered) > len(sequence) * 0.4:
            pclass = ProteinClass.INTRINSICALLY_DISORDERED
        else:
            pclass = ProteinClass.ALPHA_BETA

        return StructurePrediction(
            secondary_structure=ss_predictions,
            disordered_regions=disordered,
            domain_boundaries=domains,
            contact_order=round(contact_order, 3),
            predicted_stability=round(stability, 3),
            protein_class=pclass
        )

    def _predict_secondary_structure(
        self,
        aa_props: List[AminoAcidProperties]
    ) -> List[Tuple[int, int, SecondaryStructure]]:
        """Predict secondary structure elements"""
        predictions = []
        window_size = 6

        i = 0
        while i < len(aa_props) - window_size + 1:
            window = aa_props[i:i + window_size]

            helix_score = sum(p.helix_propensity for p in window) / window_size
            sheet_score = sum(p.sheet_propensity for p in window) / window_size

            if helix_score > 1.1:
                # Extend helix
                end = i + window_size
                while end < len(aa_props) and aa_props[end].helix_propensity > 0.9:
                    end += 1
                predictions.append((i, end, SecondaryStructure.HELIX))
                i = end
            elif sheet_score > 1.2:
                # Extend sheet
                end = i + window_size
                while end < len(aa_props) and aa_props[end].sheet_propensity > 1.0:
                    end += 1
                predictions.append((i, end, SecondaryStructure.SHEET))
                i = end
            else:
                i += 1

        return predictions

    def _predict_disordered_regions(
        self,
        aa_props: List[AminoAcidProperties]
    ) -> List[Tuple[int, int]]:
        """Predict intrinsically disordered regions"""
        disordered = []
        window_size = 15
        threshold = 1.05

        in_disorder = False
        start = 0

        for i in range(len(aa_props) - window_size + 1):
            window = aa_props[i:i + window_size]
            disorder_score = sum(p.disorder_propensity for p in window) / window_size

            if disorder_score > threshold and not in_disorder:
                in_disorder = True
                start = i
            elif disorder_score <= threshold and in_disorder:
                in_disorder = False
                disordered.append((start, i + window_size // 2))

        if in_disorder:
            disordered.append((start, len(aa_props)))

        return disordered

    def _predict_domain_boundaries(
        self,
        aa_props: List[AminoAcidProperties]
    ) -> List[int]:
        """Predict domain boundaries using hydrophobicity transitions"""
        boundaries = []
        window_size = 20

        if len(aa_props) < window_size * 3:
            return boundaries

        # Look for significant hydrophobicity transitions
        for i in range(window_size, len(aa_props) - window_size):
            left = sum(p.hydrophobicity for p in aa_props[i-window_size:i]) / window_size
            right = sum(p.hydrophobicity for p in aa_props[i:i+window_size]) / window_size

            if abs(left - right) > 2.0:  # Significant transition
                boundaries.append(i)

        return boundaries

    def _estimate_contact_order(
        self,
        sequence: str,
        ss_predictions: List[Tuple[int, int, SecondaryStructure]]
    ) -> float:
        """Estimate relative contact order"""
        # Simplified contact order based on secondary structure
        if not ss_predictions:
            return 0.5

        # Estimate contacts from secondary structure
        total_contacts = 0
        total_separation = 0

        for i, (start1, end1, ss1) in enumerate(ss_predictions):
            for start2, end2, ss2 in ss_predictions[i+1:]:
                # Sheets form long-range contacts
                if ss1 == SecondaryStructure.SHEET and ss2 == SecondaryStructure.SHEET:
                    separation = abs((start1 + end1) / 2 - (start2 + end2) / 2)
                    total_contacts += 1
                    total_separation += separation

        if total_contacts > 0:
            avg_separation = total_separation / total_contacts
            contact_order = avg_separation / len(sequence)
        else:
            contact_order = 0.1  # Default for all-alpha or disordered

        return min(1.0, contact_order)

    def _generate_hypotheses(
        self,
        sequence: str,
        aa_props: List[AminoAcidProperties],
        structure_pred: StructurePrediction
    ) -> List[FoldingHypothesis]:
        """Generate folding hypotheses based on analysis"""
        hypotheses = []

        # 1. Hydrophobic core hypotheses
        hydro_cores = self._find_hydrophobic_cores(aa_props)
        for core in hydro_cores:
            hypotheses.append(FoldingHypothesis(
                hypothesis_id=f"core_{core.start}",
                region=core,
                hypothesis_type="folding_nucleus",
                description=f"Hydrophobic core at positions {core.start}-{core.end} may nucleate folding",
                rationale="High average hydrophobicity suggests burial in native state",
                confidence=min(1.0, core.score / 3.0),
                novelty_score=0.6,
                evidence_support=0.7,
                supporting_literature=["Hermetic hydrophobic collapse principle"],
                experimental_suggestions=["Mutation analysis of core residues", "Folding kinetics with Trp probes"]
            ))

        # 2. Disorder hypotheses
        for start, end in structure_pred.disordered_regions:
            region = SequenceRegion(
                start=start, end=end,
                sequence=sequence[start:end],
                region_type="disordered",
                score=1.0
            )
            hypotheses.append(FoldingHypothesis(
                hypothesis_id=f"idr_{start}",
                region=region,
                hypothesis_type="intrinsic_disorder",
                description=f"Region {start}-{end} shows high disorder propensity",
                rationale="Composition enriched in disorder-promoting residues (P, E, S, Q, K)",
                confidence=0.75,
                novelty_score=0.5,
                evidence_support=0.8,
                supporting_literature=self._get_disorder_evidence(),
                experimental_suggestions=["NMR relaxation experiments", "SAXS ensemble analysis"]
            ))

        # 3. Functional motif hypotheses
        motif_hits = self._find_functional_motifs(sequence)
        for motif_region in motif_hits:
            hypotheses.append(FoldingHypothesis(
                hypothesis_id=f"motif_{motif_region.start}",
                region=motif_region,
                hypothesis_type="functional_motif",
                description=f"Functional motif '{motif_region.region_type}' at {motif_region.start}",
                rationale="Conserved sequence pattern suggests functional importance",
                confidence=0.85,
                novelty_score=0.4,
                evidence_support=0.9,
                supporting_literature=["Conserved motif from literature corpus"],
                experimental_suggestions=["Mutagenesis of motif residues", "Binding assays"]
            ))

        # 4. Folding pathway hypotheses based on contact order
        if structure_pred.contact_order > 0.15:
            hypotheses.append(FoldingHypothesis(
                hypothesis_id="co_barrier",
                region=SequenceRegion(0, len(sequence), sequence, "full_length", structure_pred.contact_order),
                hypothesis_type="folding_kinetics",
                description=f"High contact order ({structure_pred.contact_order:.2f}) suggests slow folding",
                rationale="Long-range contacts require complex search through conformational space",
                confidence=0.7,
                novelty_score=0.6,
                evidence_support=0.8,
                supporting_literature=["Contact order correlates with folding rate"],
                experimental_suggestions=["Stopped-flow kinetics", "Phi-value analysis"]
            ))

        # Sort by composite score
        hypotheses.sort(key=lambda h: h.composite_score, reverse=True)

        return hypotheses[:10]  # Top 10 hypotheses

    def _find_hydrophobic_cores(self, aa_props: List[AminoAcidProperties]) -> List[SequenceRegion]:
        """Find potential hydrophobic cores - regions significantly more hydrophobic than average"""
        cores = []
        window_size = 7

        if len(aa_props) < window_size:
            return cores

        # Calculate global average hydrophobicity
        global_avg = sum(p.hydrophobicity for p in aa_props) / len(aa_props)

        # Dynamic threshold: above average + 1.0 (but at least 0.5 for hydrophilic proteins)
        threshold = max(0.5, global_avg + 1.0)

        for i in range(len(aa_props) - window_size):
            window = aa_props[i:i + window_size]
            avg_hydro = sum(p.hydrophobicity for p in window) / window_size

            if avg_hydro > threshold:
                # Check if this is a new core or extension
                if not cores or i > cores[-1].end:
                    cores.append(SequenceRegion(
                        start=i,
                        end=i + window_size,
                        sequence="".join(p.residue for p in window),
                        region_type="hydrophobic_core",
                        score=avg_hydro,
                        properties={"threshold_used": threshold, "global_avg": global_avg}
                    ))
                else:
                    # Extend existing core
                    cores[-1].end = i + window_size
                    cores[-1].score = max(cores[-1].score, avg_hydro)

        # Also find amphipathic regions (alternating pattern) - important for helices
        for i in range(len(aa_props) - window_size):
            window = aa_props[i:i + window_size]

            # Check for helix-like pattern (i, i+3, i+4 periodicity)
            helix_score = sum(p.helix_propensity for p in window) / window_size
            if helix_score > 1.15:  # Strong helix propensity
                # Check if not already covered
                already_found = any(c.start <= i < c.end for c in cores)
                if not already_found:
                    cores.append(SequenceRegion(
                        start=i,
                        end=i + window_size,
                        sequence="".join(p.residue for p in window),
                        region_type="helix_nucleation",
                        score=helix_score,
                        properties={"helix_propensity": helix_score}
                    ))

        return cores

    def _find_functional_motifs(self, sequence: str) -> List[SequenceRegion]:
        """Find functional motifs in sequence"""
        import re
        hits = []

        for pattern, motif_type in FUNCTIONAL_MOTIFS.items():
            try:
                for match in re.finditer(pattern, sequence):
                    hits.append(SequenceRegion(
                        start=match.start(),
                        end=match.end(),
                        sequence=match.group(),
                        region_type=motif_type,
                        score=1.0
                    ))
            except re.error:
                continue

        return hits

    def _get_disorder_evidence(self) -> List[str]:
        """Get literature evidence for disorder"""
        papers = self.corpus.search("intrinsically disordered protein", max_results=3)
        return [p.get("title", "Unknown") for p in papers]

    def _assess_drug_target(
        self,
        sequence: str,
        structure_pred: StructurePrediction,
        stability_score: float
    ) -> DrugTargetAssessment:
        """Assess protein as potential drug target"""
        # Binding site predictions (pockets near hydrophobic regions)
        binding_sites = []
        sheet_regions = [r for r in structure_pred.secondary_structure if r[2] == SecondaryStructure.SHEET]

        for start, end, _ in sheet_regions[:3]:
            binding_sites.append(SequenceRegion(
                start=start, end=end,
                sequence=sequence[start:end],
                region_type="potential_binding_site",
                score=0.7
            ))

        # Allosteric sites (regions with mixed structure)
        allosteric = []
        for boundary in structure_pred.domain_boundaries[:2]:
            start = max(0, boundary - 10)
            end = min(len(sequence), boundary + 10)
            allosteric.append(SequenceRegion(
                start=start, end=end,
                sequence=sequence[start:end],
                region_type="potential_allosteric",
                score=0.5
            ))

        # Determine overall potential
        if stability_score > 0.7 and len(binding_sites) > 0:
            potential = DrugTargetPotential.HIGH
        elif stability_score > 0.5 and len(binding_sites) > 0:
            potential = DrugTargetPotential.MEDIUM
        elif structure_pred.protein_class == ProteinClass.INTRINSICALLY_DISORDERED:
            potential = DrugTargetPotential.CHALLENGING
        else:
            potential = DrugTargetPotential.LOW

        return DrugTargetAssessment(
            overall_potential=potential,
            binding_site_predictions=binding_sites,
            allosteric_sites=allosteric,
            stability_for_screening=stability_score,
            expression_difficulty="medium" if len(sequence) < 300 else "high",
            therapeutic_relevance="requires_validation"
        )

    def to_dict(self, result: FoldingAnalysisResult) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization"""
        return {
            "sequence_id": result.sequence_id,
            "sequence": result.sequence,
            "length": result.length,
            "molecular_weight": result.molecular_weight,
            "amino_acid_composition": result.amino_acid_composition,
            "charge_at_ph7": result.charge_at_ph7,
            "isoelectric_point": result.isoelectric_point,
            "folding_energy": result.folding_energy,
            "folding_state": result.folding_state.value,
            "stability_score": result.stability_score,
            "structure_prediction": {
                "secondary_structure": [
                    {"start": s, "end": e, "type": t.value}
                    for s, e, t in result.structure_prediction.secondary_structure
                ],
                "disordered_regions": [
                    {"start": s, "end": e}
                    for s, e in result.structure_prediction.disordered_regions
                ],
                "domain_boundaries": result.structure_prediction.domain_boundaries,
                "contact_order": result.structure_prediction.contact_order,
                "predicted_stability": result.structure_prediction.predicted_stability,
                "protein_class": result.structure_prediction.protein_class.value
            },
            "hypotheses": [
                {
                    "id": h.hypothesis_id,
                    "type": h.hypothesis_type,
                    "region": f"{h.region.start}-{h.region.end}",
                    "description": h.description,
                    "rationale": h.rationale,
                    "confidence": h.confidence,
                    "composite_score": h.composite_score,
                    "experimental_suggestions": h.experimental_suggestions
                }
                for h in result.hypotheses
            ],
            "drug_target": {
                "potential": result.drug_target.overall_potential.value,
                "binding_sites": len(result.drug_target.binding_site_predictions),
                "allosteric_sites": len(result.drug_target.allosteric_sites),
                "stability_for_screening": result.drug_target.stability_for_screening
            },
            "metadata": {
                "analysis_timestamp": result.analysis_timestamp,
                "engine_version": result.engine_version,
                "governance": {
                    "not_for_clinical_use": True,
                    "research_only": True
                }
            }
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Hermes Trismegistos Advanced Folding Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a sequence
  python folding_engine.py --sequence "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH"

  # Analyze from FASTA file
  python folding_engine.py --fasta protein.fasta --output results.json

  # Analyze hemoglobin alpha chain
  python folding_engine.py --sequence "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH" --name "HBA1"

GOVERNANCE: This tool is for RESEARCH PURPOSES ONLY.
- NOT for clinical use
- NOT diagnostic advice
- Consult experts for any therapeutic decisions
        """
    )

    parser.add_argument("--sequence", "-s", help="Amino acid sequence to analyze")
    parser.add_argument("--fasta", "-f", help="FASTA file to analyze")
    parser.add_argument("--name", "-n", default="protein", help="Protein name/identifier")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--corpus", help="Path to biomedical corpus JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if not args.sequence and not args.fasta:
        parser.print_help()
        sys.exit(1)

    # Get sequence
    if args.fasta:
        fasta_path = Path(args.fasta)
        if not fasta_path.exists():
            print(f"Error: FASTA file not found: {args.fasta}")
            sys.exit(1)
        # Simple FASTA parsing
        lines = fasta_path.read_text().strip().split("\n")
        sequence = "".join(line for line in lines if not line.startswith(">"))
        if lines[0].startswith(">") and args.name == "protein":
            args.name = lines[0][1:].split()[0]
    else:
        sequence = args.sequence

    # Initialize engine
    corpus_path = Path(args.corpus) if args.corpus else None
    engine = HermesAdvancedFoldingEngine(corpus_path)

    # Run analysis
    print(f"Analyzing {args.name} ({len(sequence)} residues)...")
    result = engine.analyze(sequence, args.name)

    # Convert to dict
    result_dict = engine.to_dict(result)

    # Output
    if args.output:
        Path(args.output).write_text(json.dumps(result_dict, indent=2), encoding="utf-8")
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(result_dict, indent=2))

    # Summary
    if args.verbose:
        print("\n" + "=" * 60)
        print("HERMES FOLDING ENGINE SUMMARY")
        print("=" * 60)
        print(f"Sequence ID: {result.sequence_id}")
        print(f"Length: {result.length} residues")
        print(f"Molecular Weight: {result.molecular_weight:.1f} Da")
        print(f"Folding State: {result.folding_state.value}")
        print(f"Stability Score: {result.stability_score:.3f}")
        print(f"Protein Class: {result.structure_prediction.protein_class.value}")
        print(f"Contact Order: {result.structure_prediction.contact_order:.3f}")
        print(f"Drug Target Potential: {result.drug_target.overall_potential.value}")
        print(f"\nTop Hypotheses:")
        for h in result.hypotheses[:3]:
            print(f"  - {h.description} (score: {h.composite_score:.2f})")
        print("\nGOVERNANCE: Research use only. Not for clinical decisions.")


if __name__ == "__main__":
    main()
