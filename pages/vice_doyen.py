# =============================================
# VICE-DOYEN DASHBOARD
# =============================================

import streamlit as st
import pandas as pd
import plotly.express as px
from backend.queries import (
    get_global_kpis, get_department_statistics, get_conflicts_report,
    get_room_occupancy_stats, get_department_exam_count,
    get_conflicts_by_dept, get_professor_hours_stats,
    get_latest_schedule_metadata, get_validation_state,
    publish_schedule
)

def show():
    """Show Vice-Doyen Dashboard"""
    
    st.title("🎓 Tableau de Bord Vice-Doyen")
    st.markdown("### Vue Stratégique Globale")
    
    # ----------------------------------------------------
    # GLOBAL VALIDATION SECTION
    # ----------------------------------------------------
    latest_meta = get_latest_schedule_metadata()
    
    if latest_meta:
        st.markdown("### 🚦 État de la Validation")
        
        # 1. Fetch ALL Validations (Chefs + Vice Doyen)
        all_validations = get_validation_state(latest_meta['id'])
        
        # Filter for Chef Depts only for the count/table
        chef_validations = [v for v in all_validations if v['validator_role'] == 'CHEF_DEPT']
        
        # Calculate summary
        total_depts = len(chef_validations) 
        validated_count = sum(1 for v in chef_validations if v['status'] == 'VALIDATED')
        rejected_count = sum(1 for v in chef_validations if v['status'] == 'INVALIDATED')
        pending_count = sum(1 for v in chef_validations if v['status'] == 'PENDING')
        
        # Display Progress
        col_prog1, col_prog2, col_prog3 = st.columns(3)
        col_prog1.metric("✅ Validés (Dépts)", f"{validated_count}/{total_depts}")
        col_prog2.metric("❌ Rejetés (Dépts)", rejected_count)
        col_prog3.metric("⏳ En Attente", pending_count)
        
        # Detailed Table
        if chef_validations:
            df_val = pd.DataFrame(chef_validations)
            # Add simple icon column
            status_map = {'VALIDATED': '✅', 'INVALIDATED': '❌', 'PENDING': '⏳'}
            df_val['Icon'] = df_val['status'].map(status_map)
            st.dataframe(
                df_val[['Icon', 'departement', 'status', 'comment', 'val_date']], 
                use_container_width=True,
                hide_index=True
            )
        
        # 2. Global Action
        st.markdown("#### Action Finale")
        if latest_meta.get('is_published'):
             st.success("✅ **L'emploi du temps est PUBLIC et VALIDÉ par le Vice-Doyen.**")
        else:
            if rejected_count > 0:
                st.error(f"⚠️ **Attention :** {rejected_count} département(s) ont rejeté le planning.")
                
            with st.form("global_publish"):
                st.write("Une fois validé, **l'emploi du temps sera visible pour tous les étudiants et professeurs.**")
                if st.form_submit_button("🚀 Valider & Publier l'Emploi du Temps", type="primary", use_container_width=True):
                    # We pass user_id if we want, but currently not getting it in this block. 
                    # Simpler is passing None or fetching current user.
                    # Ideally: user = get_current_user(); publish_schedule(..., user['id'])
                    if publish_schedule(latest_meta['id']): 
                        st.balloons()
                        st.success("Emploi du temps publié avec succès !")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la publication.")
    else:
        st.info("Aucun emploi du temps généré.")

    st.markdown("---")
    
    try:
        kpis = get_global_kpis()
        
        # Global KPIs Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📝 Examens", kpis['total_exams'])
        with col2:
            st.metric("👥 Étudiants", kpis['total_students'])
        with col3:
            st.metric("📦 Blocs", kpis['total_blocs'])
        with col4:
            st.metric("🏢 Occupation", f"{kpis.get('room_utilization', 0)}%")
        with col5:
            conflicts = kpis.get('total_conflicts', 0)
            conflict_icon = "✅" if conflicts == 0 else "⚠️"
            st.metric(f"{conflict_icon} Conflits", conflicts)
        
        st.markdown("---")
        
        # Conflict Analysis by Department
        if kpis.get('total_conflicts', 0) > 0:
            st.subheader("🚨 Analyse des Conflits par Département")
            conflicts_by_dept = get_conflicts_by_dept()
            if conflicts_by_dept:
                df_conflicts = pd.DataFrame(conflicts_by_dept)
                fig_c = px.bar(
                    df_conflicts, 
                    x='departement', 
                    y='conflict_count',
                    title="Nombre de Conflits par Département",
                    color='conflict_count',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_c, use_container_width=True)
        
        col_stats1, col_stats2 = st.columns(2)
        
        with col_stats1:
            # Professor Hours Stats
            st.subheader("👨‍🏫 Charge Horaire Professeurs")
            prof_hours = get_professor_hours_stats()
            if prof_hours:
                df_hours = pd.DataFrame(prof_hours)
                fig_h = px.bar(
                    df_hours,
                    x='departement',
                    y=['avg_hours', 'max_hours'],
                    barmode='group',
                    title="Heures de Surveillance (Moyenne vs Max)",
                    labels={'value': 'Heures', 'variable': 'Métrique'}
                )
                st.plotly_chart(fig_h, use_container_width=True)
                
        with col_stats2:
            # Room occupancy
            st.subheader("🏢 Occupation des Salles")
            room_stats = get_room_occupancy_stats()
            if room_stats:
                df_rooms = pd.DataFrame(room_stats)
                fig_r = px.pie(
                    df_rooms, 
                    values='rooms_used', 
                    names='type', 
                    title="Répartition Usage Salles"
                )
                st.plotly_chart(fig_r, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erreur lors du chargement: {e}")
