import streamlit as st
from backend.auth import authenticate_user
from backend.database import execute_query_dict
import config

print("--- 1. Testing Chef Dept Login (unchanged) ---")
# Chef credentials were NOT changed (chef_physique / admin123)
user = authenticate_user('chef_physique', 'admin123')
if user and user.get('dept_nom') == 'Physique':
    print("✅ SUCCESS: Chef Dept login and data load.")
else:
    print("❌ FAILURE: Chef Dept login.")

print("\n--- 2. Testing Professor Login (New Creds) ---")
# Get a random professor
profs = execute_query_dict("SELECT id, matricule, nom, prenom FROM professeurs LIMIT 1")
if profs:
    p = profs[0]
    username = p['matricule']
    password = p['nom'] + p['prenom']
    print(f"Testing Professor: {username} / {password}")
    
    user_prof = authenticate_user(username, password)
    if user_prof and user_prof.get('professeur_id'):
        print(f"✅ SUCCESS: Professor login. Found Prof ID: {user_prof['professeur_id']}, Name: {user_prof.get('professeur_nom')}")
        if not user_prof.get('professeur_nom'):
             print("❌ WARNING: Professor Name missing.")
    else:
        print("❌ FAILURE: Professor login or missing ID.")
else:
    print("⚠️ No professors found.")

print("\n--- 3. Testing Student Login (New Creds) ---")
student_id = 250
stu_data = execute_query_dict("SELECT matricule, nom, prenom FROM etudiants WHERE id=%s", (student_id,))
if stu_data:
    s = stu_data[0]
    username = s['matricule']
    password = s['nom'] + s['prenom']
    print(f"Testing Student: {username} / {password}")
    
    user_stu = authenticate_user(username, password)
    if user_stu and user_stu.get('etudiant_id') == student_id:
         print("✅ SUCCESS: Student login and data load.")
    else:
         print("❌ FAILURE: Student login.")
else:
    print("⚠️ Student 250 not found.")
