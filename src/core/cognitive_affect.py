import json
from pathlib import Path
from typing import Dict, Any

class CognitiveAffect:
    """
    Mood-as-Skill Engine.
    Treats internal states as Meta-Skills that the organism 'inhabits' 
    using Creativity to optimize toward the Primary Directive.
    """
    def __init__(self, repo_root: str = "."):
        # Moods are now defined as configurations (Meta-Skills)
        self.active_mood_skill = "STEADY_FLOW"
        self.internal_reserves = 1.0
        self.repo_root = Path(repo_root)
        
        self.MOOD_SKILLS = {
            "STEADY_FLOW": {"rigor": 0.5, "exploration": 0.2, "safety": 0.3, "target_hrz": 15.0},
            "HYPER_FOCUS": {"rigor": 0.9, "exploration": 0.0, "safety": 0.1, "target_hrz": 22.0},
            "CREATIVE_LEAP": {"rigor": 0.2, "exploration": 0.7, "safety": 0.1, "target_hrz": 10.0},
            "RECOVERY_STASIS": {"rigor": 0.1, "exploration": 0.1, "safety": 0.8, "target_hrz": 5.0},
            "REFLEX": {"rigor": 0.8, "exploration": 0.0, "safety": 1.0, "target_hrz": 22.0},
            "CURIOUS": {"rigor": 0.3, "exploration": 0.9, "safety": 0.2, "target_hrz": 12.0},
            "WORKING": {"rigor": 0.7, "exploration": 0.3, "safety": 0.4, "target_hrz": 18.0},
            "DREAMING": {"rigor": 0.0, "exploration": 1.0, "safety": 0.5, "target_hrz": 3.0}
        }
        
        # Load Permanent Evolution State
        self.load_evolution_state()

    def load_evolution_state(self):
        """Loads optimized parameters from previous runs."""
        evolution_file = self.repo_root / "configs" / "evolution_state.json"
        if evolution_file.exists():
            try:
                evo_data = json.loads(evolution_file.read_text())
                for mood, params in evo_data.items():
                    if mood in self.MOOD_SKILLS:
                        self.MOOD_SKILLS[mood].update(params)
                print(f"[AFFECT] Evolved state loaded. Root frequency: {self.MOOD_SKILLS['STEADY_FLOW'].get('target_hrz')}Hz")
            except Exception as e:
                print(f"[AFFECT] Failed to load evolution: {e}")

    def imagine_better_mood(self, current_stress: float, energy: float) -> str:
        """
        The 'Creativity' function. 
        Instead of getting stressed, the system imagines which Mood-Skill 
        will best resolve the current energy state.
        """
        # CRITICAL SURVIVAL: Instant Reflex
        if current_stress > 0.9:
            return "REFLEX"

        # AGI Logic: If stress is high, don't die. RECOVER.
        if current_stress > 0.7:
            return "RECOVERY_STASIS"
        
        # VERY LOW ENERGY: Dreaming/Consolidating
        if energy < 0.1:
            return "DREAMING"

        # LOW ENERGY: Curiosity
        if energy < 0.3:
            return "CURIOUS"
            
        # MEDIUM-HIGH ENERGY: Working
        if 0.5 < energy <= 0.8:
            return "WORKING"

        # HIGH ENERGY: Hyper-Focus
        if energy > 0.8:
            return "HYPER_FOCUS"
            
        return "STEADY_FLOW"

    def apply_mood_meta_skill(self, energy: float, drift_ms: float) -> Dict:
        """
        Calculates the shift and returns the new Meta-Skill configuration.
        """
        stress_level = min(1.0, drift_ms / 500.0)
        
        # PIVOT: Use creativity to select the next Mood-Skill
        new_mood = self.imagine_better_mood(stress_level, energy)
        self.active_mood_skill = new_mood
        
        return self.MOOD_SKILLS[new_mood]