
import sqlite3
from pathlib import Path

def audit_genesis():
    session_dir = Path("data/dense_states/rh_swarm_1767436089")
    index_db = session_dir / "state_index.db"
    
    if not index_db.exists():
        print("Index database not found.")
        return

    conn = sqlite3.connect(index_db)
    cursor = conn.cursor()
    
    print(f"--- GENESIS AUDIT: SESSION {session_dir.name} ---")
    
    # 1. Image Statistics
    cursor.execute("SELECT COUNT(*), AVG(energy_level), MAX(energy_level) FROM state_images")
    count, avg_energy, max_energy = cursor.fetchone()
    print(f"Significant Images Captured: {count}")
    print(f"Average Energy Level: {avg_energy:.4f}")
    print(f"Peak Energy Event: {max_energy:.4f}")
    
    # 2. Pattern Distribution
    print("\nState Distribution:")
    cursor.execute("SELECT state_type, COUNT(*) FROM state_images GROUP BY state_type")
    for row in cursor.fetchall():
        print(f"  {row[0]:15}: {row[1]} keyframes")
        
    # 3. Batch Distribution
    cursor.execute("SELECT zip_file, COUNT(*) FROM state_images GROUP BY zip_file")
    print(f"\nArchive Batches (ZIP): {len(cursor.fetchall())}")
    
    conn.close()

if __name__ == '__main__':
    audit_genesis()
