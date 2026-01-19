# =============================================
# CHEF DE DÉPARTEMENT DASHBOARD
# =============================================

import streamlit as st
import pandas as pd
from backend.queries import (
    get_department_statistics, 
    get_latest_schedule_metadata, 
    get_validation_state,
    update_validation_state
)
from backend.auth import get_current_user

def show():
    """Show Chef de Département Dashboard"""
    
    user = get_current_user()
    dept_id = user.get('dept_id')
    dept_name = user.get('dept_nom', 'N/A')
    
    # Header
    st.markdown(f"""
    <div class="hero-header">
        <h1>🏛️ Tableau de Bord Département</h1>
        <p>Département : <strong>{dept_name}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # ----------------------------------------------------
    # KPIs ROW
    # ----------------------------------------------------
    try:
        dept_stats = get_department_statistics(dept_id)
        if dept_stats:
            stats = dept_stats[0]
            
            st.markdown("<h3 class='title-font'>📊 Indicateurs de Performance</h3>", unsafe_allow_html=True)
            
            # Using custom HTML/CSS for metrics to ensure "University" look
            col1, col2, col3, col4 = st.columns(4)
            
            metrics_data = [
                ("📝 Examens", stats.get('total_exams', 0), "Total"),
                ("👥 Étudiants", stats.get('total_students', 0), "Planifiés"),
                ("📦 Blocs", stats.get('total_blocs', 0), "Sessions"),
                ("👨‍🏫 Profs", stats.get('professors_assigned', 0), "Mobilisés")
            ]
            
            for i, (label, value, sub) in enumerate(metrics_data):
                with [col1, col2, col3, col4][i]:
                    st.markdown(f"""
                    <div class="metric-nice">
                        <div style="font-size: 2.5rem; font-weight: 700; color: #1e40af;">{value}</div>
                        <div style="font-size: 0.9rem; font-weight: 600; color: #475569; text-transform: uppercase;">{label}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 5px;">{sub}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ----------------------------------------------------
            # VALIDATION SECTION
            # ----------------------------------------------------
            st.markdown("<h3 class='title-font'>🚦 Validation de l'Emploi du Temps</h3>", unsafe_allow_html=True)
            
            latest_meta = get_latest_schedule_metadata()
            if latest_meta:
                val_status = get_validation_state(latest_meta['id'], dept_id=dept_id, role='CHEF_DEPT')
                current_status = val_status[0]['status'] if val_status else 'PENDING'
                
                # Visual Logic for Status
                status_color = "#f59e0b" # Orange/Pending
                status_text = "En attente de validation"
                if current_status == 'VALIDATED':
                    status_color = "#10b981" # Green
                    status_text = "Emploi du temps validé"
                elif current_status == 'INVALIDATED':
                    status_color = "#ef4444" # Red
                    status_text = "Emploi du temps rejeté"

                st.markdown(f"""
                <div class="glass-card" style="border-left: 6px solid {status_color};">
                    <div style="display: flex; align-items: center; gap: 20px;">
                        <div style="font-size: 40px; color: {status_color}; text-shadow: 0 4px 10px rgba(0,0,0,0.1);">●</div>
                        <div>
                            <h3 style="margin: 0; color: #1e293b; font-size: 1.5rem;">{status_text}</h3>
                            <p style="margin: 5px 0 0 0; color: #64748b;">Version du planning : {latest_meta['created_at'].strftime('%d/%m/%Y %H:%M')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action Center
                if current_status == 'PENDING' or True: # Always allow re-decision logic
                    with st.expander("📝 Console de Décision", expanded=(current_status == 'PENDING')):
                        with st.form("validation_form"):
                            st.write("Veuillez examiner les statistiques avant de valider.")
                            comment = st.text_area("Commentaire Officiel", placeholder="Justification de la décision...")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.form_submit_button("✅ Valider l'emploi du temps", type="primary", use_container_width=True):
                                    if update_validation_state(latest_meta['id'], 'CHEF_DEPT', 'VALIDATED', dept_id=dept_id, comment=comment, user_id=user['id']):
                                        st.success("Validé !")
                                        st.rerun()
                            with c2:
                                if st.form_submit_button("❌ Rejeter", use_container_width=True):
                                     if update_validation_state(latest_meta['id'], 'CHEF_DEPT', 'INVALIDATED', dept_id=dept_id, comment=comment, user_id=user['id']):
                                        st.error("Rejeté !")
                                        st.rerun()
            else:
                st.info("Aucun planning généré pour le moment.")

        else:
             st.warning("Données du département non disponibles.")
             
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
