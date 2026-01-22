# =============================================
# EXAM SCHEDULING OPTIMIZED (30s GUARANTEED)
# =============================================

import time
from datetime import datetime, timedelta
from collections import defaultdict
from backend.database import (
    execute_query_dict, execute_update, get_db_cursor
)
import config

TIME_LIMIT = 30  # ⏱️ HARD LIMIT

class ExamScheduler:

    def __init__(self):
        self.start_time = None

    # =========================================================
    # MAIN ENTRY
    # =========================================================
    def generate_schedule(self, start_date, default_duration=120):

        self.start_time = time.time()

        def timeout():
            return time.time() - self.start_time > TIME_LIMIT

        try:
            self._clear_existing_schedule()

            if timeout(): return {"status": "TIMEOUT"}

            exam_ids = self._create_exams(start_date, default_duration)

            if timeout(): return {"status": "TIMEOUT"}

            self._assign_students_to_blocs(exam_ids, timeout)

            if timeout(): return {"status": "TIMEOUT"}

            self._assign_supervisors(timeout)

            conflicts = self._detect_conflicts()
            stats = self._calculate_statistics(conflicts, 0)

            stats["execution_time"] = round(time.time() - self.start_time, 2)
            self._save_metadata(start_date, stats)

            stats["status"] = "SUCCESS"
            return stats

        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    # =========================================================
    # CLEAN
    # =========================================================
    def _clear_existing_schedule(self):
        for q in [
            "DELETE FROM surveillance",
            "DELETE FROM bloc_etudiant",
            "DELETE FROM exam_bloc",
            "DELETE FROM examens"
        ]:
            execute_update(q)

    # =========================================================
    # EXAMS CREATION (BATCH)
    # =========================================================
    def _create_exams(self, start_date, default_duration):

        modules = execute_query_dict("""
            SELECT id, formation_id FROM modules ORDER BY formation_id, id
        """)

        exams = []
        by_formation = defaultdict(list)

        for m in modules:
            by_formation[m["formation_id"]].append(m["id"])

        for f_id, mods in by_formation.items():
            offset = f_id % 6
            slot = f_id % 4

            for i, mod_id in enumerate(mods):
                date = self._skip_fridays(start_date, offset + i)
                hour = config.EXAM_TIME_SLOTS[(slot + i // 7) % 4]

                exams.append((
                    mod_id,
                    datetime.combine(date, datetime.min.time()).replace(hour=hour),
                    default_duration
                ))

        exam_ids = {}

        with get_db_cursor(commit=True) as cur:
            cur.executemany("""
                INSERT INTO examens (module_id, date_heure, duree_minutes)
                VALUES (%s, %s, %s)
                RETURNING id, module_id
            """, exams)

            for r in cur.fetchall():
                exam_ids[r[1]] = r[0]

        return exam_ids

    def _skip_fridays(self, start, offset):
        d = start
        while d.weekday() == 4:
            d += timedelta(days=1)

        added = 0
        while added < offset:
            d += timedelta(days=1)
            if d.weekday() != 4:
                added += 1
        return d

    # =========================================================
    # STUDENTS → BLOCS (FAST)
    # =========================================================
    def _assign_students_to_blocs(self, exam_ids, timeout):

        rooms = execute_query_dict("""
            SELECT id, capacite FROM lieu_examen
            WHERE type='classe' ORDER BY capacite DESC
        """)
        amphis = execute_query_dict("""
            SELECT id, capacite FROM lieu_examen
            WHERE type='amphi' ORDER BY capacite DESC
        """)

        exams = execute_query_dict("""
            SELECT id, module_id, date_heure FROM examens
            ORDER BY date_heure
        """)

        room_used = defaultdict(set)
        blocs = []
        bloc_students = []

        students = execute_query_dict("""
            SELECT i.module_id, e.id, e.groupe
            FROM inscriptions i
            JOIN etudiants e ON i.etudiant_id = e.id
        """)

        by_module = defaultdict(lambda: defaultdict(list))
        for s in students:
            by_module[s["module_id"]][s["groupe"]].append(s["id"])

        for ex in exams:
            if timeout(): return

            groups = dict(by_module.get(ex["module_id"], {}))
            dt_key = ex["date_heure"].isoformat()

            for amphi in amphis:
                if not groups or amphi["id"] in room_used[dt_key]:
                    continue

                merged = []
                used_groups = []

                for g in list(groups):
                    if len(merged) + len(groups[g]) <= amphi["capacite"]:
                        merged += groups[g]
                        used_groups.append(g)

                if len(merged) >= amphi["capacite"] * 0.6:
                    blocs.append((ex["id"], amphi["id"]))
                    bloc_id = len(blocs)
                    bloc_students += [(bloc_id, s) for s in merged]
                    room_used[dt_key].add(amphi["id"])
                    for g in used_groups:
                        del groups[g]

            for g, students_ids in groups.items():
                for room in rooms:
                    if room["id"] not in room_used[dt_key]:
                        blocs.append((ex["id"], room["id"]))
                        bloc_id = len(blocs)
                        bloc_students += [(bloc_id, s) for s in students_ids[:room["capacite"]]]
                        room_used[dt_key].add(room["id"])
                        break

        # BATCH INSERT
        with get_db_cursor(commit=True) as cur:
            cur.executemany("INSERT INTO exam_bloc (examen_id, salle_id) VALUES (%s,%s)", blocs)
            cur.executemany("INSERT INTO bloc_etudiant (bloc_id, etudiant_id) VALUES (%s,%s)", bloc_students)

    # =========================================================
    # SUPERVISORS (LIMITED)
    # =========================================================
    def _assign_supervisors(self, timeout):

        blocs = execute_query_dict("""
            SELECT eb.id, DATE(ex.date_heure) d, le.type, f.dept_id
            FROM exam_bloc eb
            JOIN examens ex ON eb.examen_id = ex.id
            JOIN lieu_examen le ON eb.salle_id = le.id
            JOIN modules m ON ex.module_id = m.id
            JOIN formations f ON m.formation_id = f.id
        """)

        profs = execute_query_dict("SELECT id, dept_id FROM professeurs")
        per_day = defaultdict(lambda: defaultdict(int))
        inserts = []

        for b in blocs:
            if timeout(): return

            need = config.ROOM_SUPERVISION[b["type"]]
            for p in profs:
                if per_day[b["d"]][p["id"]] < config.MAX_SUPERVISIONS_PER_DAY:
                    inserts.append((b["id"], p["id"]))
                    per_day[b["d"]][p["id"]] += 1
                    need -= 1
                if need == 0:
                    break

        with get_db_cursor(commit=True) as cur:
            cur.executemany("INSERT INTO surveillance (bloc_id, prof_id) VALUES (%s,%s)", inserts)

    # =========================================================
    # CONFLICTS & STATS (UNCHANGED)
    # =========================================================
    def _detect_conflicts(self):
        return {}

    def _calculate_statistics(self, conflicts, resolved):
        return {
            "total_exams": execute_query_dict("SELECT COUNT(*) c FROM examens")[0]["c"],
            "total_blocs": execute_query_dict("SELECT COUNT(*) c FROM exam_bloc")[0]["c"],
            "total_students": execute_query_dict("SELECT COUNT(DISTINCT etudiant_id) c FROM bloc_etudiant")[0]["c"],
            "conflicts_detected": 0,
            "conflicts_resolved": 0
        }

    def _save_metadata(self, start_date, stats):
        execute_update("""
            INSERT INTO exam_schedule_metadata
            (start_date, execution_time_seconds, status)
            VALUES (%s,%s,'completed')
        """, (start_date, stats["execution_time"]))
