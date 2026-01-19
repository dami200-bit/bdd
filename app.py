# =============================================
# MAIN APPLICATION - LOGIN & ROUTING
# =============================================

import streamlit as st
from backend import auth, database
import config

# Initialize session state
auth.init_session_state()

# Page configuration
st.set_page_config(
    page_title=config.APP_CONFIG['page_title'],
    page_icon=config.APP_CONFIG['page_icon'],
    layout=config.APP_CONFIG['layout'],
    initial_sidebar_state=config.APP_CONFIG['initial_sidebar_state']
)

# Custom CSS for Radical "Decor" Redesign
def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Inter:wght@300;400;500;600&display=swap');

    /* ANIMATIONS */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translate3d(0, 20px, 0); }
        to { opacity: 1; transform: translate3d(0, 0, 0); }
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ROOT & GLOBAL */
    :root {
        --primary: #1e40af;
        --secondary: #f97316;
        --glass-bg: rgba(255, 255, 255, 0.85);
        --glass-border: rgba(255, 255, 255, 0.5);
        --text-main: #0f172a;
        --text-sub: #475569;
    }

    .stApp {
        background: linear-gradient(-45deg, #eff6ff, #dbeafe, #bfdbfe, #e0e7ff);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        font-family: 'Inter', sans-serif;
    }
    
    /* Decoration Circle (Pseudo-element idea replaced by simple CSS classes due to Streamlit limitations) */
    
    /* TYPOGRAPHY */
    h1, h2, h3, .title-font {
        font-family: 'Merriweather', serif;
        color: var(--primary);
    }
    
    /* HIDE STREAMLIT UI */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stSidebarNav"] {display: none;}
    
    /* GLASS CARD */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 20px;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15);
        transition: all 0.3s ease;
    }

    /* LOGIN CONTAINER */
    .login-wrapper {
        display: flex;
        justify-content: center;
        padding-top: 5vh;
        animation: fadeInUp 1s ease-out;
    }
    
    .login-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 50px;
        border-radius: 24px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 480px;
        text-align: center;
        border-top: 8px solid var(--primary);
    }
    
    .univ-icon {
        font-size: 60px;
        margin-bottom: 20px;
        display: inline-block;
        background: -webkit-linear-gradient(#1e40af, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* DASHBOARD HEADER HERO */
    .hero-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(30, 64, 175, 0.3);
        margin-bottom: 40px;
        animation: fadeInUp 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .hero-header h1 {
        font-family: 'Merriweather', serif;
        color: white !important;
        margin: 0;
        font-size: 2.2rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 10px;
    }

    /* INPUTS */
    .stTextInput input {
        border-radius: 12px !important;
        padding: 12px 15px !important;
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.2s;
    }
    .stTextInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
    }

    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(45deg, #1e40af, #2563eb) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        border: none !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.3s !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4) !important;
    }
    
    /* METRICS */
    .metric-nice {
        text-align: center;
        padding: 20px;
        background: rgba(255,255,255,0.6);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.8);
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

def show_login_page():
    """Display cinematic login page"""
    
    # We use columns to center, but wrapped in a container styling
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-box">
                <div class="univ-icon">🏛️</div>
                <h2 style="margin-bottom: 5px; color:#1e3a8a;">Université M'Hamed Bougara</h2>
                <h3 style="margin-top: 0; font-size: 16px; color:#64748b; font-family: 'Inter', sans-serif;">Plateforme Numérique des Examens</h3>
                <br>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.text_input("Identifiant Académique", key="username", placeholder="Ex: MATETUD-250")
            st.text_input("Mot de Passe", type="password", key="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Accéder à l'Espace", use_container_width=True)
        
        st.markdown("""
                <div style="margin-top: 30px; border-top: 1px solid #f1f5f9; padding-top: 20px;">
                    <p style="font-size: 12px; color: #94a3b8;">
                        © 2026 UMBB - Direction des Systèmes d'Information<br>
                        Besoin d'aide ? Contactez le support numérique.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if submit:
             username = st.session_state.username
             password = st.session_state.password
             if auth.login(username, password):
                 st.success("Bienvenue sur le campus numérique.")
                 st.rerun()
             else:
                 st.error("Accès refusé. Vérifiez vos identifiants.")

def show_dashboard():
    """Display appropriate dashboard based on user role"""
    user = auth.get_current_user()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        ### 👤 {user['username']}
        **Rôle:** {config.ROLES.get(user['role'], user['role'])}
        """)
       
        if user['role'] == 'student' and user.get('etudiant_nom'):
            st.markdown(f"**Nom:** {user['etudiant_prenom']} {user['etudiant_nom']}")
            st.markdown(f"**Groupe:** {user.get('groupe', 'N/A')}")
        elif user['role'] == 'professor' and user.get('professeur_nom'):
            st.markdown(f"**Nom:** {user['professeur_prenom']} {user['professeur_nom']}")
        elif user['role'] == 'chef_dept' and user.get('dept_nom'):
            st.markdown(f"**Département:** {user['dept_nom']}")
        
        st.markdown("---")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            auth.logout()
            st.rerun()
    
    # Route to appropriate dashboard
    if user['role'] == 'vice_doyen':
        from pages import vice_doyen
        vice_doyen.show()
    elif user['role'] == 'admin':
        from pages import exam_admin
        exam_admin.show()
    elif user['role'] == 'chef_dept':
        from pages import chef_dept
        chef_dept.show()
    elif user['role'] == 'student':
        from pages import student
        student.show()
    elif user['role'] == 'professor':
        from pages import professor
        professor.show()
    else:
        st.error("❌ Rôle non reconnu")

# Main app logic
def main():
    """Main application entry point"""
    
    # Test database connection
    if not database.test_connection():
        st.error("❌ Impossible de se connecter à la base de données PostgreSQL")
        st.info("Vérifiez que PostgreSQL est en cours d'exécution et que les identifiants dans config.py sont corrects")
        st.stop()
    
    # Show login or dashboard based on authentication state
    if auth.is_authenticated():
        show_dashboard()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
