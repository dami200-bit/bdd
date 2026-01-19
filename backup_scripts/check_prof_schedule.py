from backend.database import execute_query_dict, execute_query

# 1. Get Professor ID
prof_query = "SELECT id, nom, prenom FROM professeurs WHERE nom = 'Amrani' AND prenom = 'Bilal'"
profs = execute_query_dict(prof_query)

if not profs:
    print("ERROR: Professor 'Amrani Bilal' not found.")
    exit()

prof_id = profs[0]['id']
print(f"Professor Found: ID={prof_id}, Name={profs[0]['nom']} {profs[0]['prenom']}")

# 2. Run the exact query from the code
code_query = """
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

results = execute_query_dict(code_query, (prof_id,))
print(f"\nQuery Results for ID {prof_id}: {len(results)} rows found.")
for r in results:
    print(f"- {r['module']} on {r['date_heure']}")

# 3. Check the User mapping
user_query = "SELECT username, role, user_id FROM users WHERE user_id = %s AND role = 'professor'"
users = execute_query_dict(user_query, (prof_id,))
print(f"\nUser Mapping for Prof ID {prof_id}:")
if users:
    print(users)
else:
    print("No user found linked to this professor ID.")
