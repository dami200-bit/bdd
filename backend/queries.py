# =============================================
# ANALYTICAL QUERIES MODULE
# =============================================

from backend.database import execute_query_dict, get_db_cursor

def get_student_schedule(etudiant_id):
    """Get personalized exam schedule for a student"""
    query = """
        SELECT 
            m.nom as module,
            ex.date_heure,
            ex.duree_minutes,
            le.nom as salle,
            le.type as salle_type,
            f.nom as formation
        FROM etudiants e
        JOIN inscriptions i ON e.id = i.etudiant_id
        JOIN modules m ON i.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN examens ex ON m.id = ex.module_id
        JOIN exam_bloc eb ON ex.id = eb.examen_id
        JOIN bloc_etudiant be ON eb.id = be.bloc_id AND be.etudiant_id = e.id
        JOIN lieu_examen le ON eb.salle_id = le.id
        WHERE e.id = %s
        AND EXISTS (
            SELECT 1 FROM (
                SELECT is_published FROM exam_schedule_metadata 
                ORDER BY generation_date DESC LIMIT 1
            ) latest WHERE latest.is_published = TRUE
        )
        ORDER BY ex.date_heure
    """
    return execute_query_dict(query, (etudiant_id,))

def get_professor_schedule(professeur_id):
    """Get supervision schedule for a professor"""
    query = """
        SELECT 
            m.nom as module,
            ex.date_heure,
            ex.duree_minutes,
            le.nom as salle,
            le.type as salle_type,
            COUNT(be.etudiant_id) as nb_etudiants,
            f.nom as formation,
            d.nom as departement
        FROM professeurs p
        JOIN surveillance s ON p.id = s.prof_id
        JOIN exam_bloc eb ON s.bloc_id = eb.id
        JOIN examens ex ON eb.examen_id = ex.id
        JOIN modules m ON ex.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        JOIN lieu_examen le ON eb.salle_id = le.id
        LEFT JOIN bloc_etudiant be ON eb.id = be.bloc_id
        WHERE p.id = %s
        AND EXISTS (
             SELECT 1 FROM (
                 SELECT is_published FROM exam_schedule_metadata 
                 ORDER BY generation_date DESC LIMIT 1
             ) latest WHERE latest.is_published = TRUE
        )
        GROUP BY m.nom, ex.date_heure, ex.duree_minutes, le.nom, le.type, f.nom, d.nom
        ORDER BY ex.date_heure
    """
    return execute_query_dict(query, (professeur_id,))

def get_department_statistics(dept_id=None):
    """Get exam statistics by department"""
    query = """
        SELECT 
            d.nom as departement,
            COUNT(DISTINCT ex.id) as total_exams,
            COUNT(DISTINCT eb.id) as total_blocs,
            COUNT(DISTINCT be.etudiant_id) as total_students,
            COUNT(DISTINCT s.prof_id) as professors_assigned
        FROM departements d
        JOIN formations f ON d.id = f.dept_id
        JOIN modules m ON f.id = m.formation_id
        LEFT JOIN examens ex ON m.id = ex.module_id
        LEFT JOIN exam_bloc eb ON ex.id = eb.examen_id
        LEFT JOIN bloc_etudiant be ON eb.id = be.bloc_id
        LEFT JOIN surveillance s ON eb.id = s.bloc_id
        WHERE (%s IS NULL OR d.id = %s)
        GROUP BY d.id, d.nom
        ORDER BY d.nom
    """
    return execute_query_dict(query, (dept_id, dept_id))

def get_room_occupancy_stats():
    """Get room and amphitheater occupancy statistics"""
    query = """
        SELECT 
            le.type,
            COUNT(DISTINCT le.id) as total_rooms,
            COUNT(DISTINCT eb.salle_id) as rooms_used,
            ROUND(COUNT(DISTINCT eb.salle_id)::NUMERIC / COUNT(DISTINCT le.id) * 100, 2) as utilization_rate,
            AVG(le.capacite) as avg_capacity,
            MAX(le.capacite) as max_capacity,
            MIN(le.capacite) as min_capacity
        FROM lieu_examen le
        LEFT JOIN exam_bloc eb ON le.id = eb.salle_id
        GROUP BY le.type
    """
    return execute_query_dict(query)

def get_supervision_fairness():
    """Get supervision distribution fairness metrics"""
    query = """
        SELECT 
            p.id,
            p.nom,
            p.prenom,
            d.nom as departement,
            COUNT(DISTINCT s.id) as total_supervisions,
            COUNT(DISTINCT DATE(ex.date_heure)) as days_assigned,
            ROUND(COUNT(DISTINCT s.id)::NUMERIC / NULLIF(COUNT(DISTINCT DATE(ex.date_heure)), 0), 2) as avg_per_day
        FROM professeurs p
        JOIN departements d ON p.dept_id = d.id
        LEFT JOIN surveillance s ON p.id = s.prof_id
        LEFT JOIN exam_bloc eb ON s.bloc_id = eb.id
        LEFT JOIN examens ex ON eb.examen_id = ex.id
        GROUP BY p.id, p.nom, p.prenom, d.nom
        HAVING COUNT(DISTINCT s.id) > 0
        ORDER BY total_supervisions DESC
    """
    return execute_query_dict(query)

def get_conflicts_report():
    """Get detailed conflicts report"""
    conflicts = {}
    
    # Student conflicts (multiple exams same day)
    query_student = """
        SELECT 
            e.id,
            e.nom,
            e.prenom,
            e.groupe,
            f.nom as formation,
            DATE(ex.date_heure) as exam_date,
            COUNT(*) as exam_count,
            STRING_AGG(m.nom, ', ' ORDER BY ex.date_heure) as modules
        FROM etudiants e
        JOIN formations f ON e.formation_id = f.id
        JOIN bloc_etudiant be ON e.id = be.etudiant_id
        JOIN exam_bloc eb ON be.bloc_id = eb.id
        JOIN examens ex ON eb.examen_id = ex.id
        JOIN modules m ON ex.module_id = m.id
        GROUP BY e.id, e.nom, e.prenom,e.groupe, f.nom, DATE(ex.date_heure)
        HAVING COUNT(*) > 1
    """
    conflicts['students'] = execute_query_dict(query_student)
    
    # Professor conflicts (>3 supervisions per day)
    query_prof = """
        SELECT 
            p.id,
            p.nom,
            p.prenom,
            d.nom as departement,
            DATE(ex.date_heure) as exam_date,
            COUNT(*) as supervision_count
        FROM professeurs p
        JOIN departements d ON p.dept_id = d.id
        JOIN surveillance s ON p.id = s.prof_id
        JOIN exam_bloc eb ON s.bloc_id = eb.id
        JOIN examens ex ON eb.examen_id = ex.id
        GROUP BY p.id, p.nom, p.prenom, d.nom, DATE(ex.date_heure)
        HAVING COUNT(*) > 3
    """
    conflicts['professors'] = execute_query_dict(query_prof)
    
    # Room capacity conflicts
    query_capacity = """
        SELECT 
            le.nom as salle,
            le.type,
            le.capacite,
            COUNT(be.etudiant_id) as student_count,
            m.nom as module,
            ex.date_heure
        FROM exam_bloc eb
        JOIN lieu_examen le ON eb.salle_id = le.id
        JOIN examens ex ON eb.examen_id = ex.id
        JOIN modules m ON ex.module_id = m.id
        LEFT JOIN bloc_etudiant be ON eb.id = be.bloc_id
        GROUP BY le.nom, le.type, le.capacite, m.nom, ex.date_heure
        HAVING COUNT(be.etudiant_id) > le.capacite
    """
    conflicts['capacity'] = execute_query_dict(query_capacity)
    
    return conflicts

def get_global_kpis():
    """Get global KPIs for dashboard"""
    kpis = {}
    
    # Total exams
    result = execute_query_dict("SELECT COUNT(*) as count FROM examens")
    kpis['total_exams'] = result[0]['count'] if result else 0
    
    # Total students scheduled
    result = execute_query_dict("""
        SELECT COUNT(DISTINCT etudiant_id) as count FROM bloc_etudiant
    """)
    kpis['total_students'] = result[0]['count'] if result else 0
    
    # Total exam blocs
    result = execute_query_dict("SELECT COUNT(*) as count FROM exam_bloc")
    kpis['total_blocs'] = result[0]['count'] if result else 0
    
    # Room utilization
    result = execute_query_dict("""
        SELECT 
            ROUND(COUNT(DISTINCT eb.salle_id)::NUMERIC / 
                  (SELECT COUNT(*) FROM lieu_examen) * 100, 2) as rate
        FROM exam_bloc eb
    """)
    kpis['room_utilization'] = result[0]['rate'] if result else 0
    
    # Conflict rate
    conflicts = get_conflicts_report()
    total_conflicts = (
        len(conflicts.get('students', [])) +
        len(conflicts.get('professors', [])) +
        len(conflicts.get('capacity', []))
    )
    kpis['total_conflicts'] = total_conflicts
    
    # Last generation metadata
    result = execute_query_dict("""
        SELECT * FROM exam_schedule_metadata
        ORDER BY generation_date DESC
        LIMIT 1
    """)
    kpis['last_generation'] = result[0] if result else None
    
    return kpis

def get_exam_timeline():
    """Get exam timeline for visualization"""
    query = """
        SELECT 
            DATE(ex.date_heure) as exam_date,
            COUNT(DISTINCT ex.id) as exam_count,
            COUNT(DISTINCT eb.id) as bloc_count,
            COUNT(DISTINCT be.etudiant_id) as student_count
        FROM examens ex
        LEFT JOIN exam_bloc eb ON ex.id = eb.examen_id
        LEFT JOIN bloc_etudiant be ON eb.id = be.bloc_id
        GROUP BY DATE(ex.date_heure)
        ORDER BY exam_date
    """
    return execute_query_dict(query)

def get_department_exam_count():
    """Get exam count by department for charts"""
    query = """
        SELECT 
            d.nom as departement,
            COUNT(DISTINCT ex.id) as exam_count
        FROM departements d
        JOIN formations f ON d.id = f.dept_id
        JOIN modules m ON f.id = m.formation_id
        LEFT JOIN examens ex ON m.id = ex.module_id
        GROUP BY d.nom
        ORDER BY exam_count DESC
    """
    return execute_query_dict(query)

# ============================================================
# NEW QUERIES FOR ROLE-BASED FEATURES
# ============================================================

def get_conflicts_by_dept():
    """
    Get conflict counts grouped by department.
    Useful for Vice-Doyen and Chef Dept.
    """
    query = """
    WITH StudentConflicts AS (
        SELECT e.id, f.dept_id
        FROM etudiants e
        JOIN formations f ON e.formation_id = f.id
        JOIN bloc_etudiant be ON e.id = be.etudiant_id
        JOIN exam_bloc eb ON be.bloc_id = eb.id
        JOIN examens ex ON eb.examen_id = ex.id
        GROUP BY e.id, f.dept_id, DATE(ex.date_heure)
        HAVING COUNT(*) > 1
    )
    SELECT 
        d.nom as departement,
        COUNT(sc.id) as conflict_count
    FROM departements d
    LEFT JOIN StudentConflicts sc ON d.id = sc.dept_id
    GROUP BY d.nom
    ORDER BY conflict_count DESC
    """
    return execute_query_dict(query)

def get_professor_hours_stats():
    """
    Get statistics on professor supervision hours.
    Useful for fairness analysis.
    """
    query = """
    SELECT 
        d.nom as departement,
        AVG(supervision_mins/60.0) as avg_hours,
        MAX(supervision_mins/60.0) as max_hours,
        MIN(supervision_mins/60.0) as min_hours
    FROM (
        SELECT 
            p.id, 
            p.dept_id,
            COALESCE(SUM(ex.duree_minutes), 0) as supervision_mins
        FROM professeurs p
        LEFT JOIN surveillance s ON p.id = s.prof_id
        LEFT JOIN exam_bloc eb ON s.bloc_id = eb.id
        LEFT JOIN examens ex ON eb.examen_id = ex.id
        GROUP BY p.id, p.dept_id
    ) prof_stats
    JOIN departements d ON prof_stats.dept_id = d.id
    GROUP BY d.nom
    ORDER BY avg_hours DESC
    """
    return execute_query_dict(query)

def search_global_schedule(dept_id=None, formation_id=None, date_filter=None):
    """
    Search global schedule with filters.
    For Students/Profs looking up other exams.
    """
    params = []
    base_query = """
        SELECT 
            m.nom as module,
            f.nom as formation,
            d.nom as departement,
            ex.date_heure,
            le.nom as salle,
            le.type as salle_type
        FROM examens ex
        JOIN modules m ON ex.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN departements d ON f.dept_id = d.id
        JOIN exam_bloc eb ON ex.id = eb.examen_id
        JOIN lieu_examen le ON eb.salle_id = le.id
        WHERE 1=1
    """
    
    if dept_id:
        base_query += " AND d.id = %s"
        params.append(dept_id)
        
    if formation_id:
        base_query += " AND f.id = %s"
        params.append(formation_id)
        
    if date_filter:
        base_query += " AND DATE(ex.date_heure) = %s"
        params.append(date_filter)

    # Enforce publication check
    base_query += """
        AND EXISTS (
            SELECT 1 FROM (
                SELECT is_published FROM exam_schedule_metadata 
                ORDER BY generation_date DESC LIMIT 1
            ) latest WHERE latest.is_published = TRUE
        )
    """
        
    base_query += " ORDER BY ex.date_heure LIMIT 100"
    
    return execute_query_dict(base_query, tuple(params))

# ============================================================
# VALIDATION WORKFLOW QUERIES
# ============================================================

def get_latest_schedule_metadata():
    """Get the latest generation metadata including validation status"""
    query = """
        SELECT * FROM exam_schedule_metadata
        ORDER BY generation_date DESC
        LIMIT 1
    """
    result = execute_query_dict(query)
    return result[0] if result else None


def get_validation_state(meta_id, dept_id=None, role=None):
    """
    Get validation status from validation_state table.
    """
    params = [meta_id]
    query = """
        SELECT 
            vs.id,
            vs.validator_role,
            vs.dept_id,
            d.nom as departement,
            vs.status,
            vs.comment,
            vs.val_date
        FROM validation_state vs
        LEFT JOIN departements d ON vs.dept_id = d.id
        WHERE vs.meta_id = %s
    """
    
    if dept_id:
        query += " AND vs.dept_id = %s"
        params.append(dept_id)
        
    if role:
        query += " AND vs.validator_role = %s"
        params.append(role)
        
    query += " ORDER BY d.nom NULLS LAST"
    
    return execute_query_dict(query, tuple(params))

def update_validation_state(meta_id, role, status, dept_id=None, comment=None, user_id=None):
    """Update validation status in validation_state table"""
    import psycopg2
    import config
    
    conn = None
    try:
        conn = psycopg2.connect(**config.DB_CONFIG)
        cur = conn.cursor()
        
        query = """
            INSERT INTO validation_state (meta_id, validator_role, dept_id, status, comment, validator_user_id, val_date)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (meta_id, validator_role, dept_id) 
            DO UPDATE SET 
                status = EXCLUDED.status,
                comment = EXCLUDED.comment,
                validator_user_id = EXCLUDED.validator_user_id,
                val_date = EXCLUDED.val_date
        """
        cur.execute(query, (meta_id, role, dept_id, status, comment, user_id))
        conn.commit()
        return True
    except Exception as e:
        if conn: conn.rollback()
        print(f"Error updating validation state: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

def publish_schedule(meta_id, user_id=None):
    """
    Publish the schedule.
    1. Update validation_state for VICE_DOYEN.
    2. Set is_published = TRUE in metadata for visibility.
    """
    import psycopg2
    import config
    
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**config.DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Update validation_state
        query_val = """
            INSERT INTO validation_state (meta_id, validator_role, dept_id, status, validator_user_id, val_date)
            VALUES (%s, 'VICE_DOYEN', NULL, 'VALIDATED', %s, CURRENT_TIMESTAMP)
            ON CONFLICT (meta_id, validator_role, dept_id) 
            DO UPDATE SET status = 'VALIDATED', val_date = CURRENT_TIMESTAMP
        """
        cur.execute(query_val, (meta_id, user_id))
        
        # 2. Update metadata visibility
        query_meta = """
            UPDATE exam_schedule_metadata
            SET is_published = TRUE,
                global_validation_status = 'VALIDATED'
            WHERE id = %s
        """
        cur.execute(query_meta, (meta_id,))
        
        conn.commit()
        return True
    except Exception as e:
        if conn: conn.rollback()
        print(f"Error publishing schedule: {e}")
        return False
    finally:
        if cur: cur.close()
        if conn: conn.close()

