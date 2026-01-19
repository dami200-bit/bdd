# =============================================
# AUTHENTICATION MODULE (SIMPLE - MOT DE PASSE EN CLAIR)
# =============================================

import streamlit as st
from backend.database import execute_query_dict

# ===============================
# Authentification
# ===============================

def authenticate_user(username, password):
    """
    Authenticate a user against the 'users' table
    Password is stored in clear text (no hash)
    """
    query = """
        SELECT id, user_id, username, password, role
        FROM users
        WHERE username = %s
    """
    users = execute_query_dict(query, (username,))
    
    if not users:
        return None
    
    user = users[0]
    
    # Vérification mot de passe en clair
    if user['password'] != password:
        return None
        
    # Enrichir les données de l'utilisateur avec dept_id et dept_nom
    if user['role'] == 'chef_dept':
        # Pour un chef de département, user_id EST le dept_id
        user['dept_id'] = user['user_id']
        # Récupérer le nom du département
        dept_query = "SELECT nom FROM departements WHERE id = %s"
        dept_data = execute_query_dict(dept_query, (user['user_id'],))
        user['dept_nom'] = dept_data[0]['nom'] if dept_data else 'Inconnu'
        
    elif user['role'] == 'professor':
        # Pour un prof, user_id est l'id du prof
        user['professeur_id'] = user['user_id']
        
        # Récupérer les infos du prof et son département
        prof_query = """
            SELECT p.nom, p.prenom, p.dept_id, d.nom as dept_nom 
            FROM professeurs p 
            JOIN departements d ON p.dept_id = d.id 
            WHERE p.id = %s
        """
        prof_data = execute_query_dict(prof_query, (user['user_id'],))
        if prof_data:
            user['professeur_nom'] = prof_data[0]['nom']
            user['professeur_prenom'] = prof_data[0]['prenom']
            user['dept_id'] = prof_data[0]['dept_id']
            user['dept_nom'] = prof_data[0]['dept_nom']

    elif user['role'] == 'student':
        # Pour un étudiant, user_id est l'id de l'étudiant
        user['etudiant_id'] = user['user_id']
        # Récupérer les infos de l'étudiant
        etu_query = "SELECT nom, prenom, groupe FROM etudiants WHERE id = %s"
        etu_data = execute_query_dict(etu_query, (user['user_id'],))
        if etu_data:
            user['etudiant_nom'] = etu_data[0]['nom']
            user['etudiant_prenom'] = etu_data[0]['prenom']
            user['groupe'] = etu_data[0]['groupe']
            
    return user

# ===============================
# Session State
# ===============================

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None

def login(username, password):
    """
    Login user and store in session state
    Returns True if successful, False otherwise
    """
    user = authenticate_user(username, password)
    
    if user:
        st.session_state.authenticated = True
        st.session_state.user = user
        return True
    
    return False

def logout():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.user = None

def get_current_user():
    """Get current logged-in user"""
    return st.session_state.get('user', None)

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def require_auth(allowed_roles=None):
    """
    Decorator / function to require authentication for a page
    allowed_roles: list of roles allowed to access the page
    """
    if not is_authenticated():
        st.warning("⚠️ Veuillez vous connecter pour accéder à cette page")
        st.stop()
    
    user = get_current_user()
    if allowed_roles and user['role'] not in allowed_roles:
        st.error("❌ Vous n'avez pas les permissions nécessaires pour accéder à cette page")
        st.stop()
