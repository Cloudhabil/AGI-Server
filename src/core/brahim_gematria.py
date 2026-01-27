#!/usr/bin/env python3
"""
BRAHIM GEMATRIA - The Meaning of Numbers
=========================================

Each Brahim number encodes a dimensional frequency, a cosmic meaning,
and a position in the architecture of reality.

The sequence [27, 42, 60, 75, 97, 117, 139, 154, 172, 187] is not arbitrary.
Each number is a resonance point between dimensions.

CENTER = 107: The fixed point where all dimensions converge
SUM = 214: Every mirror pair sums to this constant

Author: ASIOS Core
Version: 1.0.0
"""

from dataclasses import dataclass
from typing import Dict, Optional
import math

PHI = (1 + math.sqrt(5)) / 2
BETA = 1 / PHI**3  # 0.236 - exotic threshold


@dataclass
class BrahimGematria:
    """The meaning of a Brahim number."""
    number: int
    position: str
    dimension: str
    name: str
    meaning: str
    mirror: int
    state: str  # EXOTIC, NORMAL, or BALANCE
    delta: int  # Distance from center (107)
    element: str
    principle: str
    frequency_meaning: str
    hebrew_letter: Optional[str] = None
    tarot_correspondence: Optional[str] = None


# =============================================================================
# THE BRAHIM GEMATRIA TABLE
# =============================================================================

GEMATRIA: Dict[int, BrahimGematria] = {
    27: BrahimGematria(
        number=27,
        position="B_1",
        dimension="D1",
        name="GENESIS",
        meaning="The Origin Point - where existence first separates from void",
        mirror=187,
        state="EXOTIC",
        delta=-80,
        element="Primordial Fire",
        principle="Creation from nothing",
        frequency_meaning="Lowest resonance - the first vibration",
        hebrew_letter="Aleph (Beginning)",
        tarot_correspondence="The Fool (0) - Pure potential",
    ),
    42: BrahimGematria(
        number=42,
        position="B_2",
        dimension="D2",
        name="DUALITY",
        meaning="The Answer - where one becomes two, self recognizes other",
        mirror=172,
        state="EXOTIC",
        delta=-65,
        element="Primordial Water",
        principle="Reflection and polarity",
        frequency_meaning="The frequency of questions answered",
        hebrew_letter="Beth (House/Duality)",
        tarot_correspondence="The High Priestess (II) - Hidden knowledge",
    ),
    60: BrahimGematria(
        number=60,
        position="B_3",
        dimension="D3",
        name="MANIFESTATION",
        meaning="Physical Reality - the boundary of what can be touched",
        mirror=154,
        state="EXOTIC",
        delta=-47,
        element="Earth/Matter",
        principle="Form crystallizes from energy",
        frequency_meaning="The threshold of material existence",
        hebrew_letter="Gimel (Camel/Bridge)",
        tarot_correspondence="The Empress (III) - Material creation",
    ),
    75: BrahimGematria(
        number=75,
        position="B_4",
        dimension="D4",
        name="TESSERACT",
        meaning="Time/Hyperspace - where past, present, future coexist",
        mirror=139,
        state="EXOTIC",
        delta=-32,
        element="Aether/Time",
        principle="The fourth wall - gamma threshold",
        frequency_meaning="Temporal resonance begins",
        hebrew_letter="Daleth (Door)",
        tarot_correspondence="The Emperor (IV) - Structure of time",
    ),
    97: BrahimGematria(
        number=97,
        position="B_5",
        dimension="D5",
        name="THRESHOLD",
        meaning="The Gate - closest exotic point to center, portal energy",
        mirror=117,
        state="EXOTIC",
        delta=-10,
        element="Void/Potential",
        principle="Maximum exotic accessibility",
        frequency_meaning="Gateway frequency - wormhole aperture",
        hebrew_letter="He (Window/Breath)",
        tarot_correspondence="The Hierophant (V) - Hidden teachings",
    ),
    107: BrahimGematria(
        number=107,
        position="CENTER",
        dimension="ALL",
        name="CONVERGENCE",
        meaning="The Fixed Point - where all dimensions meet, the eye of phi",
        mirror=107,
        state="BALANCE",
        delta=0,
        element="Unity/Source",
        principle="Self-mirroring truth: M(107) = 107",
        frequency_meaning="The still point - zero motion, infinite potential",
        hebrew_letter="Vav (Nail/Connection)",
        tarot_correspondence="The Lovers (VI) - Union of opposites",
    ),
    117: BrahimGematria(
        number=117,
        position="B_6",
        dimension="D6",
        name="EMERGENCE",
        meaning="First Light - closest normal point, where exotic becomes manifest",
        mirror=97,
        state="NORMAL",
        delta=+10,
        element="Light/Photon",
        principle="Energy crossing into observability",
        frequency_meaning="First detectable resonance",
        hebrew_letter="Zayin (Sword/Selection)",
        tarot_correspondence="The Chariot (VII) - Directed will",
    ),
    139: BrahimGematria(
        number=139,
        position="B_7",
        dimension="D7",
        name="HARMONY",
        meaning="The Seven Spheres - cosmic order, music of dimensions",
        mirror=75,
        state="NORMAL",
        delta=+32,
        element="Sound/Vibration",
        principle="Resonant structure of reality",
        frequency_meaning="Harmonic amplification",
        hebrew_letter="Cheth (Fence/Enclosure)",
        tarot_correspondence="Strength (VIII) - Balanced power",
    ),
    154: BrahimGematria(
        number=154,
        position="B_8",
        dimension="D8",
        name="INFINITY",
        meaning="The Lemniscate - eternal return, ouroboros encoded",
        mirror=60,
        state="NORMAL",
        delta=+47,
        element="Cycle/Recursion",
        principle="What ends begins again",
        frequency_meaning="Recursive loop frequency",
        hebrew_letter="Teth (Serpent)",
        tarot_correspondence="The Hermit (IX) - Inner light",
    ),
    172: BrahimGematria(
        number=172,
        position="B_9",
        dimension="D9",
        name="COMPLETION",
        meaning="Near-Totality - the penultimate, preparation for return",
        mirror=42,
        state="NORMAL",
        delta=+65,
        element="Wisdom/Integration",
        principle="All answers integrated",
        frequency_meaning="Pre-omega resonance",
        hebrew_letter="Yod (Hand/Action)",
        tarot_correspondence="Wheel of Fortune (X) - Cycles",
    ),
    187: BrahimGematria(
        number=187,
        position="B_10",
        dimension="D10",
        name="OMEGA",
        meaning="The Return - maximum expansion before folding back to origin",
        mirror=27,
        state="NORMAL",
        delta=+80,
        element="Transcendence",
        principle="End is beginning (mirrors Genesis)",
        frequency_meaning="Highest resonance - the final vibration",
        hebrew_letter="Kaph (Palm/Crown)",
        tarot_correspondence="Justice (XI) - Cosmic balance",
    ),
}


# =============================================================================
# MIRROR PAIR MEANINGS
# =============================================================================

MIRROR_PAIRS = [
    {
        "pair": 1,
        "numbers": (27, 187),
        "names": ("GENESIS", "OMEGA"),
        "meaning": "Alpha-Omega: Beginning and End are one",
        "principle": "Creation mirrors Transcendence",
        "wormhole_type": "Origin-Return Loop",
    },
    {
        "pair": 2,
        "numbers": (42, 172),
        "names": ("DUALITY", "COMPLETION"),
        "meaning": "Question-Answer: 42 is the Answer, 172 is the Integration",
        "principle": "Reflection mirrors Wisdom",
        "wormhole_type": "Knowledge Bridge",
    },
    {
        "pair": 3,
        "numbers": (60, 154),
        "names": ("MANIFESTATION", "INFINITY"),
        "meaning": "Form-Cycle: Matter is frozen infinity",
        "principle": "Crystallization mirrors Recursion",
        "wormhole_type": "Matter-Energy Converter",
    },
    {
        "pair": 4,
        "numbers": (75, 139),
        "names": ("TESSERACT", "HARMONY"),
        "meaning": "Time-Music: The fourth dimension sings",
        "principle": "Time mirrors Vibration",
        "wormhole_type": "Temporal Resonator",
    },
    {
        "pair": 5,
        "numbers": (97, 117),
        "names": ("THRESHOLD", "EMERGENCE"),
        "meaning": "Gate-Light: The portal and what comes through",
        "principle": "Void mirrors Photon",
        "wormhole_type": "Primary Gateway (closest to center)",
    },
]


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================

def get_gematria(number: int) -> Optional[BrahimGematria]:
    """Get the gematria meaning of a Brahim number."""
    return GEMATRIA.get(number)


def get_closest_brahim(value: float) -> BrahimGematria:
    """Find the closest Brahim number to a given value."""
    brahim_numbers = [27, 42, 60, 75, 97, 107, 117, 139, 154, 172, 187]
    closest = min(brahim_numbers, key=lambda x: abs(x - value))
    return GEMATRIA[closest]


def get_mirror_pair(number: int) -> Optional[Dict]:
    """Get the mirror pair containing this number."""
    for pair in MIRROR_PAIRS:
        if number in pair["numbers"]:
            return pair
    return None


def coordinates_to_gematria(lat: float, lon: float) -> BrahimGematria:
    """Translate GPS coordinates to Brahim gematria."""
    # Normalize coordinates
    lat_norm = (lat + 90) / 180
    lon_norm = (lon + 180) / 360

    # Phi-weighted combination
    phi_combined = (lat_norm * PHI + lon_norm / PHI) % 1

    # Map to Brahim range (27-187)
    brahim_raw = 27 + phi_combined * 160

    return get_closest_brahim(brahim_raw)


# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def print_gematria_table():
    """Print the complete Brahim Gematria table."""
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("BRAHIM GEMATRIA - THE MEANING OF NUMBERS")
    print("=" * 70)
    print()
    print("The Brahim sequence encodes the structure of dimensional reality.")
    print("Each number is a frequency, a meaning, and a position in the cosmos.")
    print()
    print("CENTER = 107 (Fixed Point: M(107) = 107)")
    print("SUM = 214 (Every mirror pair sums to 214)")
    print()

    # EXOTIC REALM
    print("=" * 70)
    print("EXOTIC REALM (Below 107) - The Hidden Dimensions")
    print("=" * 70)

    for num in [27, 42, 60, 75, 97]:
        g = GEMATRIA[num]
        print(f"""
{g.position} = {g.number}: {g.name}
  Dimension:  {g.dimension}
  Meaning:    {g.meaning}
  Element:    {g.element}
  Principle:  {g.principle}
  Mirror:     {g.mirror} (delta: {g.delta:+d})
  Hebrew:     {g.hebrew_letter}
  Tarot:      {g.tarot_correspondence}
""")

    # CENTER
    print("=" * 70)
    print("THE CENTER - Where All Dimensions Meet")
    print("=" * 70)

    g = GEMATRIA[107]
    print(f"""
{g.position} = {g.number}: {g.name}
  Dimension:  {g.dimension}
  Meaning:    {g.meaning}
  Element:    {g.element}
  Principle:  {g.principle}
  Mirror:     {g.mirror} (SELF - the only self-mirroring point)
  Hebrew:     {g.hebrew_letter}
  Tarot:      {g.tarot_correspondence}
""")

    # NORMAL REALM
    print("=" * 70)
    print("NORMAL REALM (Above 107) - The Manifest Dimensions")
    print("=" * 70)

    for num in [117, 139, 154, 172, 187]:
        g = GEMATRIA[num]
        print(f"""
{g.position} = {g.number}: {g.name}
  Dimension:  {g.dimension}
  Meaning:    {g.meaning}
  Element:    {g.element}
  Principle:  {g.principle}
  Mirror:     {g.mirror} (delta: {g.delta:+d})
  Hebrew:     {g.hebrew_letter}
  Tarot:      {g.tarot_correspondence}
""")

    # MIRROR PAIRS
    print("=" * 70)
    print("THE FIVE MIRROR PAIRS")
    print("=" * 70)

    for pair in MIRROR_PAIRS:
        low, high = pair["numbers"]
        print(f"""
Pair {pair['pair']}: {low} <--> {high} = 214
  Names:     {pair['names'][0]} <--> {pair['names'][1]}
  Meaning:   {pair['meaning']}
  Principle: {pair['principle']}
  Wormhole:  {pair['wormhole_type']}
""")

    print("=" * 70)
    print("THE OUROBOROS IDENTITY")
    print("=" * 70)
    print("""
  Sum(1/phi^n, n=1 to infinity) = phi

  The infinite contraction returns to expansion.
  All Brahim numbers are harmonics of this truth.

  Beta = 1/phi^3 = 0.236 = 23.6%
  This is the exotic matter threshold.
  This is the ignorance scaling exponent.
  This is the key to traversable wormholes.
""")
    print("=" * 70)


if __name__ == "__main__":
    print_gematria_table()
