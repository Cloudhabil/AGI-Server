"""
Build Skill Vector Index

This script generates semantic vector embeddings for all skills in the registry
and saves them to a file for fast, efficient semantic search.
"""
import json
import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from skills.loader import SkillLoader
from integrations.openvino_embedder import get_embeddings  # The discovered embedding function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_index():
    """
    Scans all skills, generates embeddings, and saves them to a JSON index.
    """
    output_path = Path(__file__).resolve().parent.parent / "skills" / "skill_vectors.json"
    
    logging.info("Starting skill scan...")
    loader = SkillLoader()
    loader.scan_all()
    registry = loader.registry
    all_skills = registry.list_skills()
    
    if not all_skills:
        logging.error("No skills found. Aborting index build.")
        return

    logging.info(f"Found {len(all_skills)} skills. Generating embeddings...")
    
    skill_vectors = {}
    for i, metadata in enumerate(all_skills):
        try:
            # Create a representative text string for each skill
            text_to_embed = f"Skill: {metadata.name}. Description: {metadata.description}. Tags: {', '.join(metadata.tags)}"
            
            # Generate the embedding
            vector = get_embeddings(text_to_embed)
            
            # The function returns a list of embeddings, we take the first one
            if vector:
                skill_vectors[metadata.id] = vector[0]
                logging.info(f"({i+1}/{len(all_skills)}) Indexed skill: {metadata.id}")
            else:
                logging.warning(f"Could not generate embedding for skill: {metadata.id}")
                
        except Exception as e:
            logging.error(f"Error processing skill {metadata.id}: {e}")

    logging.info(f"Successfully generated embeddings for {len(skill_vectors)} skills.")
    
    # Save the index to a file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(skill_vectors, f, indent=2)
        
    logging.info(f"Skill vector index saved to: {output_path}")

if __name__ == "__main__":
    build_index()
