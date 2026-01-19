from backend.database import execute_update

def update_matricule_format():
    """Update matricules to new ID-based format"""
    print("--- Updating Matricule Format ---")
    
    # Update Students: MATETUD-[id]
    # Postgres concatenation with || and casting id to text
    try:
        print("Updating students to 'MATETUD-[id]'...")
        count_etu = execute_update("UPDATE etudiants SET matricule = 'MATETUD-' || id::TEXT")
        print(f"✅ Updated {count_etu} students.")
    except Exception as e:
        print(f"❌ Error updating students: {e}")

    # Update Professors: MATPROF-[id]
    try:
        print("Updating professors to 'MATPROF-[id]'...")
        count_prof = execute_update("UPDATE professeurs SET matricule = 'MATPROF-' || id::TEXT")
        print(f"✅ Updated {count_prof} professors.")
    except Exception as e:
        print(f"❌ Error updating professors: {e}")

if __name__ == "__main__":
    update_matricule_format()
