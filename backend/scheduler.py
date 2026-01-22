# =============================================
# EXAM SCHEDULING OPTIMIZATION ALGORITHM
# =============================================

import time
from datetime import datetime, timedelta
from backend.database import execute_query_dict, execute_update, execute_many, get_db_cursor
import config

class ExamScheduler:
    """
    Exam scheduling optimization algorithm
    Implements room/amphi merging and group splitting logic
    """
    
    def __init__(self):
        self.start_time = None
        self.execution_time = None
        
    def generate_schedule(self, start_date, default_duration=120):
        """
        Generate complete exam schedule
        
        Args:
            start_date: Start date for exams (datetime.date)
            default_duration: Default exam duration in minutes
            
        Returns:
            dict with generation statistics
        """
        self.start_time = time.time()
        
        try:
            # Step 1: Clear existing schedule
            self._clear_existing_schedule()
            
            # Step 2: Create exams for all modules
            exam_ids = self._create_exams(start_date, default_duration)
            
            # Step 3: Assign students to exam blocs with room assignment
            self._assign_students_to_blocs(exam_ids)
            
            # Step 4: Assign supervisors
            self._assign_supervisors()
            
            # Step 5: Detect and resolve conflicts
            conflicts = self._detect_conflicts()
            resolved = self._resolve_conflicts(conflicts)
            
            # Step 6: Calculate statistics
            stats = self._calculate_statistics(conflicts, resolved)
            
            self.execution_time = time.time() - self.start_time
            stats['execution_time'] = round(self.execution_time, 2)
            
            # Step 7: Save metadata
            self._save_metadata(start_date, stats)
            
            return stats
            
        except Exception as e:
            print(f"Scheduling error: {e}")
            raise e
    
    def _clear_existing_schedule(self):
        """Clear all existing exam schedule data"""
        queries = [
            "DELETE FROM surveillance",
            "DELETE FROM bloc_etudiant",
            "DELETE FROM exam_bloc",
            "DELETE FROM examens"
        ]
        
        for query in queries:
            execute_update(query)
    
    def _create_exams(self, start_date, default_duration):
        """
        Create exam records for all modules
        SMART STRATEGY: Group by formation to avoid student conflicts
        """
        # Get all modules with formation_id
        modules = execute_query_dict("""
            SELECT id, nom, formation_id 
            FROM modules 
            ORDER BY formation_id, id
        """)
        
        exams_created = []
        
        # Group modules by formation
        from collections import defaultdict
        formation_modules = defaultdict(list)
        for m in modules:
            formation_modules[m['formation_id']].append(m)
            
        print(f"Scheduling {len(modules)} modules across {len(formation_modules)} formations...")
        
        # Schedule each formation
        for f_id, f_modules in formation_modules.items():
            # Spread strategy:
            # 1. Start offset based on formation ID (balances global load)
            # 2. Each module in formation gets a distinct day (prevents student conflicts)
            # 3. Time slot rotates based on formation (balances daily room usage)
            
            start_offset = (f_id % 6) # Spread starts over first 6 days
            slot_base = (f_id % 4)    # Assign specific slot to this formation
            
            for i, module in enumerate(f_modules):
                # Calculate target day index (skipping Fridays logic needed)
                # Spacing: 1 module per day per formation
                # day_index 0 is start_date
                
                day_offset = start_offset + i
                
                # Calculate actual date skipping Fridays
                exam_date = self._get_date_skipping_fridays(start_date, day_offset)
                
                # Determine time slot (rotate slightly to fill gaps)
                # But kept constant for formation usually better for mental model
                # Let's use fixed slot for formation, unless overridden
                slot_index = (slot_base + (i // 7)) % 4 # Shift slot only after a week
                
                hour = config.EXAM_TIME_SLOTS[slot_index]
                
                exam_time = datetime.combine(
                    exam_date,
                    datetime.min.time()
                ).replace(hour=hour)
                
                exams_created.append({
                    'module_id': module['id'],
                    'date_heure': exam_time,
                    'duree_minutes': default_duration
                })
        
        # Batch insert exams
        query = """
            INSERT INTO examens (module_id, date_heure, duree_minutes)
            VALUES (%s, %s, %s)
            RETURNING id, module_id
        """
        
        exam_ids = {}
        with get_db_cursor(commit=True) as cursor:
            # Optimization: Use executemany? No, we need returning IDs.
            # Stick to loop for now, 1200 queries is fast enough (order of ms)
            for exam in exams_created:
                cursor.execute(query, (exam['module_id'], exam['date_heure'], exam['duree_minutes']))
                result = cursor.fetchone()
                exam_ids[result[1]] = result[0]  # module_id -> exam_id
        
        return exam_ids

    def _get_date_skipping_fridays(self, start_date, day_offset):
        """
        Calculate date adding offset but skipping Fridays
        Logic: 
        1. Find first valid day (if start is Friday, move to Saturday)
        2. From there, add 'day_offset' valid days
        """
        current_date = start_date
        
        # 1. Normalize start date
        while current_date.weekday() == 4: # If Friday
             current_date += timedelta(days=1)
             
        # 2. Add offset days skipping Fridays
        days_added = 0
        while days_added < day_offset:
            current_date += timedelta(days=1)
            if current_date.weekday() != 4: # If not Friday
                days_added += 1
                
        return current_date
    
    
    def _assign_students_to_blocs(self, exam_ids):
        """
        Assign students to exam blocs with room assignment
        Implements merge/split logic with TIME-AWARE room tracking
        """
        # Get rooms and amphitheaters
        rooms = execute_query_dict("""
            SELECT id, nom, capacite, type 
            FROM lieu_examen 
            WHERE type = 'classe'
            ORDER BY capacite DESC
        """)
        
        amphitheaters = execute_query_dict("""
            SELECT id, nom, capacite
            FROM lieu_examen 
            WHERE type = 'amphi'
            ORDER BY capacite DESC
        """)
        
        # Track room availability: date_time_str -> set(room_ids)
        room_schedule = {} # stores occupied room_ids for each datetime
        
        # Helper to check availability
        def is_room_free(room_id, exam_dt):
            time_key = exam_dt.isoformat()
            if time_key not in room_schedule:
                return True
            return room_id not in room_schedule[time_key]
            
        # Helper to book room
        def book_room(room_id, exam_dt):
            time_key = exam_dt.isoformat()
            if time_key not in room_schedule:
                room_schedule[time_key] = set()
            room_schedule[time_key].add(room_id)

        # Get exam details (need time for collision detection)
        if not exam_ids:
            return

        exam_details_map = {}
        # Fetch all exams at once
        all_exams = execute_query_dict("SELECT id, date_heure, module_id FROM examens")
        for ex in all_exams:
            exam_details_map[ex['id']] = ex

        # Process exams
        # Ideally, we should process exams by time to emulate reality, or by size?
        # Let's process by time then by size to ensure fairness
        sorted_exams = sorted(
            [exam_details_map[eid] for eid in exam_ids.values()],
            key=lambda x: x['date_heure']
        )
        
        for exam in sorted_exams:
            exam_id = exam['id']
            module_id = exam['module_id']
            exam_time = exam['date_heure']
            
            students_by_group = self._get_students_by_group(module_id)
            
            if not students_by_group:
                continue
            
            # Try to merge groups in amphitheaters first
            remaining_groups = self._try_merge_in_amphitheaters(
                exam_id, students_by_group, amphitheaters, 
                exam_time, is_room_free, book_room
            )
            
            # Assign remaining groups to rooms
            if remaining_groups:
                self._assign_groups_to_rooms(
                    exam_id, remaining_groups, rooms,
                    exam_time, is_room_free, book_room
                )
    
    def _get_students_by_group(self, module_id):
        """Get students enrolled in a module, grouped by their group"""
        query = """
            SELECT e.id, e.groupe
            FROM inscriptions i
            JOIN etudiants e ON i.etudiant_id = e.id
            WHERE i.module_id = %s
            ORDER BY e.groupe, e.id
        """
        
        students = execute_query_dict(query, (module_id,))
        
        # Group students
        groups = {}
        for student in students:
            group = student['groupe']
            if group not in groups:
                groups[group] = []
            groups[group].append(student['id'])
        
        return groups
    
    def _try_merge_in_amphitheaters(self, exam_id, students_by_group, amphitheaters, 
                                  exam_time, is_room_free_func, book_room_func):
        """
        Try to merge multiple groups in amphitheaters
        """
        remaining_groups = dict(students_by_group)
        
        # Sort amphis by capacity descending (already sorted), but we iterate looking for free ones
        for amphi in amphitheaters:
            if not remaining_groups:
                break
                
            # STRICT CHECK: Only use if free
            if not is_room_free_func(amphi['id'], exam_time):
                continue
            
            # Try to fit as many groups as possible in this amphi
            merged_students = []
            merged_group_names = []
            
            # Greedy fit: take largest groups first or just order?
            # Let's stick to simple iteration for now, but we can improve
            for group_name in list(remaining_groups.keys()):
                if len(merged_students) + len(remaining_groups[group_name]) <= amphi['capacite']:
                    merged_students.extend(remaining_groups[group_name])
                    merged_group_names.append(group_name)
                    # Don't delete yet, wait until confirmed used
            
            # Create bloc if we merged at least 2 groups or filled the amphi well (>60%)
            # OR if it's a huge group that needs an amphi anyway
            should_use = False
            if len(merged_group_names) >= 2:
                should_use = True
            elif len(merged_students) >= amphi['capacite'] * 0.6:
                should_use = True
            elif len(merged_group_names) == 1 and len(merged_students) > 50: 
                # Single large group
                should_use = True

            if should_use:
                self._create_exam_bloc(exam_id, amphi['id'], merged_students)
                book_room_func(amphi['id'], exam_time) # BOOK IT
                
                # Remove assigned groups
                for name in merged_group_names:
                    del remaining_groups[name]
        
        return remaining_groups
    
    def _assign_groups_to_rooms(self, exam_id, students_by_group, rooms,
                              exam_time, is_room_free_func, book_room_func):
        """
        Assign groups to regular rooms
        """
        # Sort rooms by capacity ASCENDING to find best fit (smallest room that fits)
        # But for splitting we might want large rooms.
        # Strategy: 
        # 1. Try to fit whole group in a specific room (Best Fit)
        # 2. If fail, split group
        
        sorted_rooms_asc = sorted(rooms, key=lambda x: x['capacite'])
        
        for group_name, student_ids in students_by_group.items():
            num_students = len(student_ids)
            
            # Find Best Fit room
            suitable_room = None
            for room in sorted_rooms_asc:
                if room['capacite'] >= num_students and is_room_free_func(room['id'], exam_time):
                    suitable_room = room
                    break
            
            if suitable_room:
                # perfect match
                self._create_exam_bloc(exam_id, suitable_room['id'], student_ids)
                book_room_func(suitable_room['id'], exam_time)
            else:
                # Split group across multiple rooms
                self._split_group_to_rooms(
                    exam_id, student_ids, rooms, 
                    exam_time, is_room_free_func, book_room_func
                )
    
    def _split_group_to_rooms(self, exam_id, student_ids, rooms,
                            exam_time, is_room_free_func, book_room_func):
        """Split a large group across multiple rooms"""
        remaining_students = list(student_ids)
        
        # Use largest available rooms for splitting to minimize fragmentation
        # 'rooms' is passed as default sort (Descending capacity usually)
        sorted_rooms_desc = sorted(rooms, key=lambda x: x['capacite'], reverse=True)

        for room in sorted_rooms_desc:
            if not remaining_students:
                break
                
            if not is_room_free_func(room['id'], exam_time):
                continue
            
            # Take as many students as fit in this room
            chunk_size = min(len(remaining_students), room['capacite'])
            room_students = remaining_students[:chunk_size]
            remaining_students = remaining_students[chunk_size:]
            
            self._create_exam_bloc(exam_id, room['id'], room_students)
            book_room_func(room['id'], exam_time)
            
        if remaining_students:
            print(f"WARNING: Could not house {len(remaining_students)} students for exam {exam_id} at {exam_time}!")
            # Fallback: overload the last room or create a virtual overflow room?
            # For now, let's just log it. In reality this triggers the 'student_no_seat' conflict.
                                
    def _create_exam_bloc(self, exam_id, salle_id, student_ids):
        """Create an exam bloc and assign students"""
        # Create bloc
        query_bloc = """
            INSERT INTO exam_bloc (examen_id, salle_id)
            VALUES (%s, %s)
            RETURNING id
        """
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query_bloc, (exam_id, salle_id))
            bloc_id = cursor.fetchone()[0]
            
            # Assign students to bloc
            query_students = """
                INSERT INTO bloc_etudiant (bloc_id, etudiant_id)
                VALUES (%s, %s)
            """
            
            student_data = [(bloc_id, student_id) for student_id in student_ids]
            cursor.executemany(query_students, student_data)
    
    def _assign_supervisors(self):
        """Assign supervisors to exam blocs"""
        # Get all blocs that need supervision
        blocs = execute_query_dict("""
            SELECT eb.id as bloc_id, eb.salle_id, ex.date_heure, ex.module_id,
                   le.type as salle_type, m.formation_id, f.dept_id
            FROM exam_bloc eb
            JOIN examens ex ON eb.examen_id = ex.id
            JOIN lieu_examen le ON eb.salle_id = le.id
            JOIN modules m ON ex.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
            ORDER BY ex.date_heure, eb.id
        """)
        
        # Track professor assignments per day
        prof_assignments = {}  # date -> prof_id -> count
        
        for bloc in blocs:
            supervisors_needed = config.ROOM_SUPERVISION[bloc['salle_type']]
            exam_date = bloc['date_heure'].date()
            
            # Get available professors (prefer same department)
            available_profs = self._get_available_professors(
                exam_date, bloc['dept_id'], prof_assignments
            )
            
            # Assign supervisors
            assigned = 0
            for prof in available_profs:
                if assigned >= supervisors_needed:
                    break
                
                # Assign professor
                execute_update(
                    "INSERT INTO surveillance (bloc_id, prof_id) VALUES (%s, %s)",
                    (bloc['bloc_id'], prof['id'])
                )
                
                # Track assignment
                if exam_date not in prof_assignments:
                    prof_assignments[exam_date] = {}
                prof_assignments[exam_date][prof['id']] = \
                    prof_assignments[exam_date].get(prof['id'], 0) + 1
                
                assigned += 1
    
    def _get_available_professors(self, exam_date, preferred_dept_id, prof_assignments):
        """Get professors available for supervision on a given date"""
        # Get all professors, prefer same department
        all_profs = execute_query_dict("""
            SELECT id, dept_id
            FROM professeurs
            ORDER BY CASE WHEN dept_id = %s THEN 0 ELSE 1 END, id
        """, (preferred_dept_id,))
        
        # Filter by availability (max 3 per day)
        available = []
        for prof in all_profs:
            current_count = prof_assignments.get(exam_date, {}).get(prof['id'], 0)
            if current_count < config.MAX_SUPERVISIONS_PER_DAY:
                available.append(prof)
        
        return available
    
    def _detect_conflicts(self):
        """Detect scheduling conflicts"""
        conflicts = {
            'student_multiple_exams': [],
            'professor_overloaded': [],
            'room_capacity': []
        }
        
        # Conflict 1: Students with multiple exams same day
        query_student = """
            SELECT e.id, e.nom, e.prenom, DATE(ex.date_heure) as exam_date, 
                   COUNT(*) as exam_count
            FROM etudiants e
            JOIN bloc_etudiant be ON e.id = be.etudiant_id
            JOIN exam_bloc eb ON be.bloc_id = eb.id
            JOIN examens ex ON eb.examen_id = ex.id
            GROUP BY e.id, e.nom, e.prenom, DATE(ex.date_heure)
            HAVING COUNT(*) > 1
        """
        conflicts['student_multiple_exams'] = execute_query_dict(query_student)
        
        # Conflict 2: Professors with >3 supervisions per day
        query_prof = """
            SELECT p.id, p.nom, p.prenom, DATE(ex.date_heure) as exam_date,
                   COUNT(*) as supervision_count
            FROM professeurs p
            JOIN surveillance s ON p.id = s.prof_id
            JOIN exam_bloc eb ON s.bloc_id = eb.id
            JOIN examens ex ON eb.examen_id = ex.id
            GROUP BY p.id, p.nom, p.prenom, DATE(ex.date_heure)
            HAVING COUNT(*) > %s
        """
        conflicts['professor_overloaded'] = execute_query_dict(
            query_prof, (config.MAX_SUPERVISIONS_PER_DAY,)
        )
        
        # Conflict 3: Room capacity violations
        query_capacity = """
            SELECT eb.id as bloc_id, le.nom as salle, le.capacite,
                   COUNT(be.etudiant_id) as student_count
            FROM exam_bloc eb
            JOIN lieu_examen le ON eb.salle_id = le.id
            LEFT JOIN bloc_etudiant be ON eb.id = be.bloc_id
            GROUP BY eb.id, le.nom, le.capacite
            HAVING COUNT(be.etudiant_id) > le.capacite
        """
        conflicts['room_capacity'] = execute_query_dict(query_capacity)
        
        return conflicts
    
    def _resolve_conflicts(self, conflicts):
        """Attempt to automatically resolve conflicts"""
        resolved_count = 0
        
        # For now, conflicts should be minimal due to proper assignment logic
        # Manual resolution would be needed for complex cases
        
        return resolved_count
    
    def _calculate_statistics(self, conflicts, resolved):
        """Calculate generation statistics"""
        stats = {}
        
        # Total exams
        result = execute_query_dict("SELECT COUNT(*) as count FROM examens")
        stats['total_exams'] = result[0]['count'] if result else 0
        
        # Total blocs
        result = execute_query_dict("SELECT COUNT(*) as count FROM exam_bloc")
        stats['total_blocs'] = result[0]['count'] if result else 0
        
        # Total students scheduled
        result = execute_query_dict("""
            SELECT COUNT(DISTINCT etudiant_id) as count FROM bloc_etudiant
        """)
        stats['total_students'] = result[0]['count'] if result else 0
        
        # Conflicts
        stats['conflicts_detected'] = (
            len(conflicts.get('student_multiple_exams', [])) +
            len(conflicts.get('professor_overloaded', [])) +
            len(conflicts.get('room_capacity', []))
        )
        stats['conflicts_resolved'] = resolved
        
        # Room utilization
        result = execute_query_dict("""
            SELECT 
                le.type,
                COUNT(DISTINCT eb.salle_id) as used_count,
                (SELECT COUNT(*) FROM lieu_examen WHERE type = le.type) as total_count
            FROM exam_bloc eb
            JOIN lieu_examen le ON eb.salle_id = le.id
            GROUP BY le.type
        """)
        
        stats['room_utilization'] = {row['type']: row for row in result}
        
        return stats
    
    def _save_metadata(self, start_date, stats):
        """Save generation metadata"""
        # Get end date from last exam
        result = execute_query_dict("""
            SELECT MAX(DATE(date_heure)) as end_date FROM examens
        """)
        end_date = result[0]['end_date'] if result else start_date
        
        query = """
            INSERT INTO exam_schedule_metadata 
            (start_date, end_date, execution_time_seconds, total_exams, total_blocs,
             conflicts_detected, conflicts_resolved, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed')
        """
        
        execute_update(query, (
            start_date,
            end_date,
            stats.get('execution_time', 0),
            stats.get('total_exams', 0),
            stats.get('total_blocs', 0),
            stats.get('conflicts_detected', 0),
            stats.get('conflicts_resolved', 0)
        ))

        # Get the ID of the inserted metadata
        result = execute_query_dict("SELECT id FROM exam_schedule_metadata ORDER BY generation_date DESC LIMIT 1")
        if result:
            meta_id = result[0]['id']
            
            # Initialize validation states
            # 1. Departments (CHEF_DEPT)
            execute_update("""
                INSERT INTO validation_state (meta_id, validator_role, dept_id, status)
                SELECT %s, 'CHEF_DEPT', id, 'PENDING'
                FROM departements
            """, (meta_id,))
            
            # 2. Vice Doyen (VICE_DOYEN)
            execute_update("""
                INSERT INTO validation_state (meta_id, validator_role, dept_id, status)
                VALUES (%s, 'VICE_DOYEN', NULL, 'PENDING')
            """, (meta_id,))
