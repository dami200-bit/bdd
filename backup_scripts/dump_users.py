from backend.database import execute_query_dict

def dump_users_1_to_5():
    print("--- Dumping Users for Student IDs 1-5 ---")
    query = """
        SELECT id as user_table_pk, user_id as student_id, username, role 
        FROM users 
        WHERE role='student' AND user_id BETWEEN 1 AND 5
        ORDER BY user_id
    """
    rows = execute_query_dict(query)
    
    if rows:
        print(f"{'PK':<10} | {'Student ID':<12} | {'Username':<20} | {'Role':<10}")
        print("-" * 60)
        for r in rows:
            print(f"{r['user_table_pk']:<10} | {r['student_id']:<12} | {r['username']:<20} | {r['role']:<10}")
    else:
        print("❌ No records found for Student IDs 1-5")

if __name__ == "__main__":
    dump_users_1_to_5()
