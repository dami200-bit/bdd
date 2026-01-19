import streamlit as st
from backend.database import execute_query_dict
import config

print("\n--- Debugging Student Credentials ---")
student_id = 250
user_info = execute_query_dict("SELECT * FROM users WHERE user_id=%s AND role='student'", (student_id,))
if user_info:
    print(f"User Record Found: {user_info[0]}")
    # Verify password
    # In seed_data.sql: password = nom + prenom
    # Let's get the student's name
    student_details = execute_query_dict("SELECT nom, prenom FROM etudiants WHERE id=%s", (student_id,))
    if student_details:
         print(f"Student Details: {student_details[0]}")
         expected_password = student_details[0]['nom'] + student_details[0]['prenom']
         print(f"Expected Password (Nom+Prenom): {expected_password}")
         print(f"Stored Password: {user_info[0]['password']}")
         
         if user_info[0]['password'] == 'admin123':
             print("Password is 'admin123' (Default in seed script comment but maybe logic differed)")
    else:
         print("Student details not found")
else:
    print("User record not found")
