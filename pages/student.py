# =============================================
# STUDENT DASHBOARD
# =============================================

import streamlit as st
import pandas as pd
from backend import auth
from backend.queries import get_student_schedule

def show():
    """Show Student Dashboard"""
    user = auth.get_current_user()
    
    # Hero Header
    st.markdown(f"""
    <div class="hero-header">
        <h1>🎓 Espace Étudiant</h1>
        <p>
            Bienvenue, <strong>{user.get('etudiant_prenom')} {user['etudiant_nom']}</strong><br>
            <span style="font-size: 0.9rem; opacity: 0.8;">Groupe : {user.get('groupe', 'Non assigné')}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    exams = get_student_schedule(user['etudiant_id'])
    
    if exams:
        st.markdown("<h3 class='title-font'>📅 Vos Examens Programmés</h3>", unsafe_allow_html=True)
        
        # Grid Layout
        cols = st.columns(2)
        
        for i, exam in enumerate(exams):
            col = cols[i % 2]
            
            # Format Data
            date_str = pd.to_datetime(exam['date_heure']).strftime('%d/%m/%Y')
            heure_str = pd.to_datetime(exam['date_heure']).strftime('%H:%M')
            module = exam['module']
            salle = exam['salle']
            duree = exam['duree_minutes']
            
            with col:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                        <h3 style="margin: 0; font-size: 1.2rem; color: #1e3a8a;">{module}</h3>
                        <span style="background: #fef3c7; color: #d97706; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;">
                            {duree} min
                        </span>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                        <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 12px;">
                            <div style="font-size: 24px;">📅</div>
                            <div style="font-weight: 600; color: #334155; margin-top: 5px;">{date_str}</div>
                            <div style="font-size: 12px; color: #64748b;">{heure_str}</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 12px;">
                            <div style="font-size: 24px;">📍</div>
                            <div style="font-weight: 600; color: #334155; margin-top: 5px;">{salle}</div>
                            <div style="font-size: 12px; color: #64748b;">Salle d'Examen</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.info("Aucun examen programmé pour le moment.")
