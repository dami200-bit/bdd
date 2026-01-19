import random
import string
from backend.database import execute_update, execute_query_dict, execute_many

def generate_matricule(prefix, length=6):
    """Generate a random matricule with prefix"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}-{suffix}"

def add_columns():
    """Add matricule column if not exists"""
    print("--- Adding Columns ---")
    try:
        execute_update("ALTER TABLE etudiants ADD COLUMN IF NOT EXISTS matricule VARCHAR(20) UNIQUE;")
        print("✅ Added 'matricule' to etudiants")
    except Exception as e:
        print(f"⚠️ Error adding to etudiants (might exist): {e}")

    try:
        execute_update("ALTER TABLE professeurs ADD COLUMN IF NOT EXISTS matricule VARCHAR(20) UNIQUE;")
        print("✅ Added 'matricule' to professeurs")
    except Exception as e:
        print(f"⚠️ Error adding to professeurs (might exist): {e}")

def populate_students():
    """Populate student matricules"""
    print("\n--- Populating Students ---")
    students = execute_query_dict("SELECT id, promo FROM etudiants WHERE matricule IS NULL")
    if not students:
        print("ℹ️ No students need matricule update.")
        return

    print(f"Generating matricules for {len(students)} students...")
    
    updates = []
    generated = set()
    
    for stu in students:
        # Format: ETU-{PROMO}-{RANDOM}
        while True:
            mat = generate_matricule(f"ETU-{stu['promo']}", 6)
            if mat not in generated:
                generated.add(mat)
                break
        
        updates.append((mat, stu['id']))
    
    # Bulk update is tricky with standard SQL 'UPDATE ... WHERE ...' for different values
    # We'll use individual updates for safety given currently available helpers, 
    # or better: use execute_many with a specific query if supported properly.
    # backend.database.execute_many executes the *same* query with different params.
    
    query = "UPDATE etudiants SET matricule = %s WHERE id = %s"
    rowcount = execute_many(query, updates)
    print(f"✅ Updated {rowcount} students.")

def populate_profs():
    """Populate professor matricules"""
    print("\n--- Populating Professors ---")
    profs = execute_query_dict("SELECT id FROM professeurs WHERE matricule IS NULL")
    if not profs:
        print("ℹ️ No professors need matricule update.")
        return

    print(f"Generating matricules for {len(profs)} professors...")
    
    updates = []
    generated = set()
    
    for prof in profs:
        # Format: PROF-{RANDOM}
        while True:
            mat = generate_matricule("PROF", 6)
            if mat not in generated:
                generated.add(mat)
                break
        updates.append((mat, prof['id']))
        
    query = "UPDATE professeurs SET matricule = %s WHERE id = %s"
    rowcount = execute_many(query, updates)
    print(f"✅ Updated {rowcount} professors.")

if __name__ == "__main__":
    add_columns()
    populate_students()
    populate_profs()
    print("\n✅ Migration Complete!")
