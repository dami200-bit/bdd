from backend.database import execute_query_dict

def check_specific_range():
    print("--- Checking Students ID 1-249 ---")
    
    # Check etudiants existence
    query_exists = "SELECT COUNT(*) as c FROM etudiants WHERE id BETWEEN 1 AND 249"
    count_exists = execute_query_dict(query_exists)[0]['c']
    print(f"Students in range 1-249 in 'etudiants' table: {count_exists}")
    
    # Check users existence
    query_users = "SELECT COUNT(*) as c FROM users WHERE role='student' AND user_id BETWEEN 1 AND 249"
    count_users = execute_query_dict(query_users)[0]['c']
    print(f"Students in range 1-249 in 'users' table: {count_users}")
    
    if count_exists > 0 and count_users == 0:
        print("❌ Confirmed: Students 1-249 are MISSING from users table.")
    elif count_exists == count_users:
        print("✅ All students in range 1-249 exist in users table.")
    else:
        print(f"⚠️ Partial mismatch: {count_exists} vs {count_users}")

if __name__ == "__main__":
    check_specific_range()
