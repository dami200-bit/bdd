# =============================================
# EXAM ADMINISTRATOR DASHBOARD
# =============================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
from backend.scheduler import ExamScheduler
from backend.queries import (
    get_global_kpis, get_conflicts_report, get_exam_timeline,
    get_room_occupancy_stats, get_supervision_fairness
)

def show():
    """Show Exam Administrator Dashboard"""
    
    st.title("📋 Administrateur des Examens")
    st.markdown("### Génération et Gestion des Emplois du Temps")
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Génération Planning",
        "📊 Statistiques",
        "⚠️ Conflits",
        "📅 Calendrier"
    ])
    
    with tab1:
        show_generation_tab()
    
    with tab2:
        show_statistics_tab()
    
    with tab3:
        show_conflicts_tab()
    
    with tab4:
        show_calendar_tab()

def show_generation_tab():
    """Schedule generation interface"""
    
    st.markdown("### 🚀 Génération Automatique du Planning")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Génération automatique de l'emploi du temps des examens avec:
        - ✅ Attribution optimale des salles et amphithéâtres
        - ✅ Fusion de groupes dans les amphithéâtres  
        - ✅ Division des groupes si nécessaire
        - ✅ Attribution équitable des surveillances
        - ✅ Détection et résolution des conflits
        - ✅ **Aucun examen le vendredi (weekend)**
        """)
    
    with col2:
        # Generation form
        with st.form("generation_form"):
            start_date_input = st.date_input(
                "📅 Date de début des examens",
                value=date.today(),
                help="Premier jour possible pour les examens (pas de vendredi)"
            )
            
            duration = st.selectbox(
                "⏱️ Durée par défaut (minutes)",
                options=[60, 90, 120],
                index=1
            )
            
            submit = st.form_submit_button("🚀 Générer le Planning", use_container_width=True)
    
    if submit:
        with st.spinner("⏳ Génération du planning en cours..."):
            try:
                scheduler = ExamScheduler()
                stats = scheduler.generate_schedule(start_date_input, duration)
                
                # Show success message
                st.success(f"✅ Planning généré avec succès en {stats['execution_time']} secondes!")
                
                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Examens planifiés", stats['total_exams'])
                
                with col2:
                    st.metric("Blocs créés", stats['total_blocs'])
                
                with col3:
                    st.metric("Étudiants planifiés", stats['total_students'])
                
                with col4:
                    status_color = "🟢" if stats['execution_time'] < 45 else "🟡"
                    st.metric(f"{status_color} Temps", f"{stats['execution_time']}s")
                
                # Show conflicts if any
                if stats['conflicts_detected'] > 0:
                    st.warning(f"⚠️ {stats['conflicts_detected']} conflit(s) détecté(s)")
                else:
                    st.info("✅ Aucun conflit détecté")
                
                # Room utilization
                if stats.get('room_utilization'):
                    st.markdown("### 📍 Utilisation des Salles")
                    util_df = pd.DataFrame(stats['room_utilization'].values())
                    st.dataframe(util_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {e}")

def show_statistics_tab():
    """Statistics and KPIs tab"""
    
    st.markdown("### 📊 Statistiques Globales")
    
    try:
        kpis = get_global_kpis()
        
        # KPI cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{kpis['total_exams']}</div>
                <div class="metric-label">Examens Planifiés</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{kpis['total_blocs']}</div>
                <div class="metric-label">Blocs d'Examen</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{kpis['total_students']}</div>
                <div class="metric-label">Étudiants</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            util_rate = kpis.get('room_utilization', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{util_rate}%</div>
                <div class="metric-label">Utilisation Salles</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Room occupancy stats
        st.markdown("### 🏢 Occupation des Espaces")
        room_stats = get_room_occupancy_stats()
        
        if room_stats:
            df = pd.DataFrame(room_stats)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart
                fig = px.bar(
                    df,
                    x='type',
                    y='utilization_rate',
                    title="Taux d'Utilisation par Type",
                    labels={'type': 'Type', 'utilization_rate': 'Taux (%)'},
                    color='type'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(df, use_container_width=True)
        
        # Supervision fairness
        st.markdown("### ⚖️ Équité des Surveillances")
        fairness = get_supervision_fairness()
        
        if fairness:
            df_fairness = pd.DataFrame(fairness)
            
            # Top 10 most assigned
            top10 = df_fairness.head(10)
            
            fig = px.bar(
                top10,
                x='total_supervisions',
                y='nom',
                orientation='h',
                title="Top 10 - Professeurs les Plus Sollicités",
                labels={'nom': 'Professeur', 'total_supervisions': 'Surveillances'},
                color='total_supervisions',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Full table
            with st.expander("📋 Voir tous les professeurs"):
                st.dataframe(df_fairness, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des statistiques: {e}")

def show_conflicts_tab():
    """Conflicts detection and display tab"""
    
    st.markdown("### ⚠️ Détection des Conflits")
    
    try:
        conflicts = get_conflicts_report()
        
        total = (
            len(conflicts.get('students', [])) +
            len(conflicts.get('professors', [])) +
            len(conflicts.get('capacity', []))
        )
        
        if total == 0:
            st.success("✅ Aucun conflit détecté ! Le planning est optimal.")
        else:
            st.warning(f"⚠️ {total} conflit(s) détecté(s)")
        
        # Student conflicts
        st.markdown("#### 👥 Étudiants avec Plusieurs Examens le Même Jour")
        if conflicts.get('students'):
            df = pd.DataFrame(conflicts['students'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("✅ Aucun conflit étudiant")
        
        # Professor conflicts
        st.markdown("#### 👨‍🏫 Professeurs avec >3 Surveillances par Jour")
        if conflicts.get('professors'):
            df = pd.DataFrame(conflicts['professors'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("✅ Aucun conflit professeur")
        
        # Capacity conflicts
        st.markdown("#### 🏢 Dépassement de Capacité des Salles")
        if conflicts.get('capacity'):
            df = pd.DataFrame(conflicts['capacity'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("✅ Aucun dépassement de capacité")
        
    except Exception as e:
        st.error(f"Erreur lors de la détection des conflits: {e}")

def show_calendar_tab():
    """Exam calendar visualization tab"""
    
    st.markdown("### 📅 Calendrier des Examens")
    
    try:
        timeline = get_exam_timeline()
        
        if timeline:
            df = pd.DataFrame(timeline)
            df['exam_date'] = pd.to_datetime(df['exam_date'])
            
            # Timeline chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['exam_date'],
                y=df['exam_count'],
                mode='lines+markers',
                name='Examens',
                line=dict(color='#1E3A8A', width=3),
                marker=dict(size=10)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['exam_date'],
                y=df['student_count'],
                mode='lines+markers',
                name='Étudiants',
                line=dict(color='#059669', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="Évolution du Planning des Examens",
                xaxis_title="Date",
                yaxis_title="Nombre d'Examens",
                yaxis2=dict(
                    title="Nombre d'Étudiants",
                    overlaying='y',
                    side='right'
                ),
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.markdown("### 📋 Détails par Date")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ Aucun examen planifié. Veuillez générer le planning d'abord.")
    
    except Exception as e:
        st.error(f"Erreur lors du chargement du calendrier: {e}")
