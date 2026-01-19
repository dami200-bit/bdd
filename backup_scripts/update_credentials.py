from backend.database import execute_update

def update_credentials():
    """Update users table with new username (matricule) and password (nom+prenom)"""
    print("--- Updating Credentials ---")
    
    # 1. Update Students
    # Target: username = etudiants.matricule, password = etudiants.nom || etudiants.prenom
    print("Updating Student Credentials...")
    query_students = """
        UPDATE users u
        SET 
            username = e.matricule,
            password = e.nom || e.prenom
        FROM etudiants e
        WHERE u.user_id = e.id AND u.role = 'student'
    """
    try:
        count_etu = execute_update(query_students)
        print(f"✅ Updated credentials for {count_etu} students.")
    except Exception as e:
        print(f"❌ Error updating students: {e}")

    # 2. Update Professors
    # Target: username = professeurs.matricule, password = professeurs.nom || professeurs.prenom
    print("Updating Professor Credentials...")
    query_profs = """
        UPDATE users u
        SET 
            username = p.matricule,
            password = p.nom || p.prenom
        FROM professeurs p
        WHERE u.user_id = p.id AND u.role = 'professor'
    """
    try:
        count_prof = execute_update(query_profs)
        print(f"✅ Updated credentials for {count_prof} professors.")
    except Exception as e:
        print(f"❌ Error updating professors: {e}")

if __name__ == "__main__":
    update_credentials()
