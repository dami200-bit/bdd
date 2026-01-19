from backend.database import execute_query_dict, execute_many

def sync_students():
    print("--- Syncing Missing Students ---")
    
    # 1. Check counts
    count_etu = execute_query_dict("SELECT COUNT(*) as c FROM etudiants")[0]['c']
    count_users = execute_query_dict("SELECT COUNT(*) as c FROM users WHERE role='student'")[0]['c']
    
    print(f"Total Students: {count_etu}")
    print(f"Student Users: {count_users}")
    
    if count_etu == count_users:
        print("✅ All students are already in users table.")
        return

    # 2. Find missing students
    print("Finding missing students...")
    missing_query = """
        SELECT e.id, e.matricule, e.nom, e.prenom
        FROM etudiants e
        LEFT JOIN users u ON u.user_id = e.id AND u.role = 'student'
        WHERE u.id IS NULL
    """
    missing_students = execute_query_dict(missing_query)
    print(f"Found {len(missing_students)} missing students.")
    
    if not missing_students:
        print("✅ No missing students found (counts mismatch might be due to other roles check).")
        return

    # 3. Prepare inserts
    print("Preparing inserts...")
    inserts = [] # (user_id, username, password, role)
    for s in missing_students:
        username = s['matricule']
        password = s['nom'] + s['prenom']
        inserts.append((s['id'], username, password, 'student'))
    
    # 4. Execute insert
    insert_query = """
        INSERT INTO users (user_id, username, password, role)
        VALUES (%s, %s, %s, %s)
    """
    
    try:
        # Assuming simple batch insert
        print(f"Inserting {len(inserts)} users...")
        count = execute_many(insert_query, inserts)
        print(f"✅ Successfully inserted {count} users.")
        
        # Verify
        new_count = execute_query_dict("SELECT COUNT(*) as c FROM users WHERE role='student'")[0]['c']
        print(f"New Student Users Count: {new_count}")
        
    except Exception as e:
        print(f"❌ Error inserting users: {e}")

if __name__ == "__main__":
    sync_students()
