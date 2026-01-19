from backend.database import execute_query_dict

def check_student_1():
    print("--- Inspecting Student 1 ---")
    
    # Get Student Details
    stu = execute_query_dict("SELECT * FROM etudiants WHERE id=1")[0]
    print(f"Student 1: Nom={stu['nom']}, Prenom={stu['prenom']}, Matricule={stu['matricule']}")
    
    # Get User Details
    user = execute_query_dict("SELECT * FROM users WHERE user_id=1 AND role='student'")
    if user:
        u = user[0]
        print(f"User 1: Username={u['username']}, Password={u['password']}")
        
        expected_username = stu['matricule']
        expected_password = stu['nom'] + stu['prenom']
        
        if u['username'] == expected_username and u['password'] == expected_password:
             print("✅ Credentials Match Expected Format.")
        else:
             print(f"❌ Mismatch! \n   Expected User: {expected_username}\n   Expected Pass: {expected_password}")
    else:
        print("❌ User 1 NOT FOUND in users table.")

if __name__ == "__main__":
    check_student_1()
