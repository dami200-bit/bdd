# =============================================
# CONFIGURATION FILE
# =============================================
import sys

import os

# =============================================
# DATABASE CONFIGURATION
# =============================================

try:
    import streamlit as st
    # Check if we are running on Streamlit Cloud or have secrets
    if 'postgres' in st.secrets:
        DB_CONFIG = {
            'host': st.secrets.postgres.host,
            'port': st.secrets.postgres.port,
            'database': st.secrets.postgres.database,
            'user': st.secrets.postgres.user,
            'password': st.secrets.postgres.password
        }
    else:
        # Local development defaults
        DB_CONFIG = {
            'host': 'localhost',
            'port': 5432,
            'database': 'examdb',
            'user': 'postgres',
            'password': '2003'
        }
except Exception:
    # Fallback to local if streamlit is not installed or secrets not found
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'examdb',
        'user': 'postgres',
        'password': '2003'
    }

# =============================================
# APPLICATION SETTINGS
# =============================================

APP_CONFIG = {
    'page_title': 'Plateforme d\'Optimisation des Examens',
    'page_icon': '📚',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# =============================================
# ROLE DEFINITIONS
# =============================================

ROLES = {
    'vice_doyen': 'Vice-Doyen',
    'admin': 'Administrateur Examens',
    'chef_dept': 'Chef de Département',
    'student': 'Étudiant',
    'professor': 'Professeur'
}

# =============================================
# BUSINESS RULES
# =============================================

# Supervision limits
MAX_SUPERVISIONS_PER_DAY = 3

# Room types and supervisor requirements
ROOM_SUPERVISION = {
    'classe': 1,      # 1 supervisor for classroom
    'amphi': 2        # 2 supervisors for amphitheater
}

# Exam time slots (hour only, 24-hour format)
# No exams on Friday (weekend)
EXAM_TIME_SLOTS = [
    8,   # 08:00
    10,  # 10:00
    13,  # 13:00
    15   # 15:00
]

# Days of week allowed for exams (0=Monday, 6=Sunday)
# Excluding Friday (4)
ALLOWED_DAYS = [0, 1, 2, 3, 6]  # Monday, Tuesday, Wednesday, Thursday, Sunday

# Exam duration options (minutes)
EXAM_DURATIONS = [90, 120, 180]

# =============================================
# UI STYLING
# =============================================

# Professional color scheme for academic institution
COLORS = {
    'primary': '#1E3A8A',      # Academic blue
    'secondary': '#64748B',    # Slate gray
    'success': '#059669',      # Emerald
    'warning': '#D97706',      # Amber
    'danger': '#DC2626',       # Red
    'info': '#0284C7',         # Sky blue
    'light': '#F8FAFC',        # Light gray
    'dark': '#1E293B'          # Dark slate
}

# =============================================
# CONSTANTS
# =============================================

DEFAULT_PASSWORD = 'admin123'  # Users should change this immediately
SESSION_TIMEOUT_MINUTES = 60
MAX_SCHEDULE_GENERATION_TIME = 45  # seconds
