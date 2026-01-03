"""
Verification script for Semantic Intelligence.

This script tests if the skill discovery mechanism is semantic or keyword-based.
"""
import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

# Suppress verbose logging from the application
logging.basicConfig(level=logging.ERROR)

from skills.discovery import discover_skills
from skills.loader import SkillLoader

def run_verification():
    """Executes the verification test."""
    print("--- Verifying Semantic Intelligence ---")
    
    # Setup: Ensure the skill registry is populated by scanning the skills directory
    skills_dir = Path(__file__).resolve().parent / "skills"
    print(f"Scanning for skills in: {skills_dir}")
    
    # Use the SkillLoader to find and register all skills
    loader = SkillLoader()
    loader.scan_directory(skills_dir)
    
    print(f"Total skills registered: {len(loader.registry.list_skills())}")

    # Define queries for the 'meta-code-generator' skill
    # This skill's description is "Code that writes better code - closing the loop on self-evolution"
    semantic_query = "refine this algorithm for better performance"
    keyword_query = "generate meta code"
    
    print(f"\n1. Testing Semantic Query: '{semantic_query}'")
    semantic_results = discover_skills(semantic_query, max_results=1)
    
    print(f"\n2. Testing Keyword Query: '{keyword_query}'")
    keyword_results = discover_skills(keyword_query, max_results=1)

    # Analyze results
    print("\n--- Analysis ---")
    semantic_top_skill = semantic_results[0].metadata.id if semantic_results else "None"
    keyword_top_skill = keyword_results[0].metadata.id if keyword_results else "None"

    print(f"Semantic Query found: {semantic_top_skill}")
    print(f"Keyword Query found:  {keyword_top_skill}")
    
    # Verdict
    is_semantic = "meta-code-generator" in semantic_top_skill
    
    print("\n--- Verdict ---")
    if is_semantic:
        print("Result: PROVEN")
        print("Reason: The query with no keyword overlap correctly identified the 'meta-code-generator' skill, indicating semantic understanding.")
    else:
        print("Result: FALSIFIED")
        print("Reason: The semantic query failed to identify the correct skill, suggesting the system relies on keyword matching.")

if __name__ == "__main__":
    run_verification()