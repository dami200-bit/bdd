# =============================================
# PROFESSOR DASHBOARD
# =============================================

import streamlit as st
import pandas as pd
from backend import auth
from backend.queries import get_professor_schedule

def show():
    """Show Professor Dashboard"""
    user = auth.get_current_user()
    
    # Hero Header
    st.markdown(f"""
    <div class="hero-header">
        <h1>👨‍🏫 Espace Professeur</h1>
        <p>
            Bienvenue, <strong>Prof. {user.get('professeur_prenom')} {user.get('professeur_nom')}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    schedule = get_professor_schedule(user['professeur_id'])
    
    if schedule:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.7); backdrop-filter: blur(5px); color: #1e40af; padding: 5px 15px; border-radius: 20px; font-weight: 600; font-size: 14px; border: 1px solid rgba(255,255,255,0.9);">
                📌 {len(schedule)} surveillances programmées
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Grid Layout for Surveillances
        cols = st.columns(2)
        
        for i, task in enumerate(schedule):
            col = cols[i % 2]
            
            # Format Data
            date_str = pd.to_datetime(task['date_heure']).strftime('%d/%m/%Y')
            heure_str = pd.to_datetime(task['date_heure']).strftime('%H:%M')
            module = task['module']
            salle = task['salle']
            nb_etu = task.get('nb_etudiants', 'N/A')
            
            with col:
                st.markdown(f"""
                <div class="glass-card">
                    <div style="border-left: 4px solid #f97316; padding-left: 15px;">
                        <div style="font-size: 12px; font-weight: 700; color: #f97316; text-transform: uppercase; letter-spacing: 0.5px;">
                            SURVEILLANCE
                        </div>
                        <h3 style="margin: 5px 0; font-size: 1.2rem; color: #1e3a8a;">{module}</h3>
                    </div>
                    
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(0,0,0,0.05); display: flex; flex-direction: column; gap: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; color: #475569;">
                            <span>📅</span> <strong>{date_str}</strong> à <strong>{heure_str}</strong>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; color: #475569;">
                            <span>📍</span> Salle : <strong>{salle}</strong>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px; font-size: 14px; color: #475569;">
                            <span>👥</span> Effectif : <strong>{nb_etu} étudiants</strong>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.info("Aucune surveillance assignée pour le moment.")
