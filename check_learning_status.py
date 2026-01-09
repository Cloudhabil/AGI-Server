
import sqlite3
from pathlib import Path

def check_learning():
    memory_db = Path("skills/core/selector_memory.db")
    if not memory_db.exists():
        print("Memory database not found.")
        return

    print(f"--- Learning Status from {memory_db} ---")
    conn = sqlite3.connect(memory_db)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM learned_patterns")
        count = cursor.fetchone()[0]
        print(f"Total learned patterns: {count}")
        
        if count > 0:
            print("\nTop 10 Learned Patterns:")
            cursor.execute("SELECT model, task_pattern, skill_name, confidence, observations FROM learned_patterns ORDER BY confidence DESC LIMIT 10")
            for row in cursor.fetchall():
                print(f"Model: {row[0]:15} | Pattern: {row[1]:15} | Skill: {row[2]:25} | Conf: {row[3]:.2f} | Obs: {row[4]}")
        
        cursor.execute("SELECT COUNT(*) FROM recommendations")
        rec_count = cursor.fetchone()[0]
        print(f"\nTotal recommendations recorded: {rec_count}")
        
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_learning()
