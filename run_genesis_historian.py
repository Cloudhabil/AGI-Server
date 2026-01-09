"""
Script to trigger the Genesis Historian Skill.
This forces the system to self-audit and produce THE_GENESIS_CODEX.md.
"""

import sys
import logging
from skills.documentation.genesis_historian import GenesisHistorianSkill
from skills.base import SkillContext

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GenesisTrigger")

def main():
    logger.info("Awakening Genesis Historian...")
    
    # Initialize Skill
    historian = GenesisHistorianSkill()
    
    # Create Dummy Context (Autonomous Run)
    context = SkillContext(
        session_id="GENESIS_AUDIT_001",
        agent_role="GPIA_CORE"
    )
    
    # Execute
    logger.info("Executing Synthesis Protocol...")
    result = historian.execute({}, context)
    
    if result.success:
        logger.info("SUCCESS: The Codex has been forged.")
        logger.info(f"Artifact Path: {result.output['path']}")
        logger.info(f"Size: {result.output['size']} bytes")
    else:
        logger.error(f"FAILURE: {result.error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
