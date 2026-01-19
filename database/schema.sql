-- =============================================
-- EXAM SCHEDULING PLATFORM - DATABASE SCHEMA
-- =============================================
-- PostgreSQL Schema for University Exam Scheduling
-- Database: exams
-- Version: 2.0 (Consolidated)
-- =============================================

-- Drop existing tables if they exist (for development)
-- Order matters due to foreign keys
DROP TABLE IF EXISTS validation_state CASCADE;
DROP TABLE IF EXISTS surveillance CASCADE;
DROP TABLE IF EXISTS bloc_etudiant CASCADE;
DROP TABLE IF EXISTS exam_bloc CASCADE;
DROP TABLE IF EXISTS examens CASCADE;
DROP TABLE IF EXISTS inscriptions CASCADE;
DROP TABLE IF EXISTS lieu_examen CASCADE;
DROP TABLE IF EXISTS professeurs CASCADE;
DROP TABLE IF EXISTS etudiants CASCADE;
DROP TABLE IF EXISTS modules CASCADE;
DROP TABLE IF EXISTS formations CASCADE;
DROP TABLE IF EXISTS departements CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS exam_schedule_metadata CASCADE;
DROP TABLE IF EXISTS department_validation CASCADE; -- Drop legacy table if exists

-- =============================================
-- CORE TABLES
-- =============================================

-- Departments Table
CREATE TABLE departements (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Formations Table
CREATE TABLE formations (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    dept_id INTEGER NOT NULL REFERENCES departements(id) ON DELETE CASCADE,
    niveau INTEGER CHECK (niveau >= 1 AND niveau <= 5), -- L1, L2, L3, M1, M2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(nom, dept_id)
);

CREATE INDEX idx_formations_dept ON formations(dept_id);

-- Modules Table
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    credits INTEGER DEFAULT 6 CHECK (credits > 0),
    formation_id INTEGER NOT NULL REFERENCES formations(id) ON DELETE CASCADE,
    semestre INTEGER CHECK (semestre IN (1, 2)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_modules_formation ON modules(formation_id);

-- Students Table
CREATE TABLE etudiants (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    formation_id INTEGER NOT NULL REFERENCES formations(id) ON DELETE CASCADE,
    promo INTEGER NOT NULL CHECK (promo >= 2020 AND promo <= 2030),
    groupe VARCHAR(10) NOT NULL CHECK (groupe IN ('G1', 'G2', 'G3', 'G4')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_etudiants_formation ON etudiants(formation_id);
CREATE INDEX idx_etudiants_groupe ON etudiants(groupe);

-- Professors Table
CREATE TABLE professeurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    dept_id INTEGER NOT NULL REFERENCES departements(id) ON DELETE CASCADE,
    specialite VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_professeurs_dept ON professeurs(dept_id);

-- Student Module Inscriptions
CREATE TABLE inscriptions (
    id SERIAL PRIMARY KEY,
    etudiant_id INTEGER NOT NULL REFERENCES etudiants(id) ON DELETE CASCADE,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    annee_academique VARCHAR(10) NOT NULL, -- e.g., "2025-2026"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(etudiant_id, module_id, annee_academique)
);

CREATE INDEX idx_inscriptions_etudiant ON inscriptions(etudiant_id);
CREATE INDEX idx_inscriptions_module ON inscriptions(module_id);

-- Exam Locations (Rooms and Amphitheaters)
CREATE TABLE lieu_examen (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    capacite INTEGER NOT NULL CHECK (capacite > 0),
    type VARCHAR(20) NOT NULL CHECK (type IN ('classe', 'amphi')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lieu_type ON lieu_examen(type);

-- =============================================
-- EXAM SCHEDULING TABLES
-- =============================================

-- Exams Table (One per module)
CREATE TABLE examens (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    date_heure TIMESTAMP NOT NULL,
    duree_minutes INTEGER NOT NULL CHECK (duree_minutes > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Constraint: No exams on Friday (weekend)
    CONSTRAINT no_friday_exams CHECK (EXTRACT(DOW FROM date_heure) != 5)
);

CREATE INDEX idx_examens_module ON examens(module_id);
CREATE INDEX idx_examens_date ON examens(date_heure);

-- Exam Bloc (handles room assignment and group merging/splitting)
CREATE TABLE exam_bloc (
    id SERIAL PRIMARY KEY,
    examen_id INTEGER NOT NULL REFERENCES examens(id) ON DELETE CASCADE,
    salle_id INTEGER NOT NULL REFERENCES lieu_examen(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exam_bloc_examen ON exam_bloc(examen_id);
CREATE INDEX idx_exam_bloc_salle ON exam_bloc(salle_id);

-- Students in Exam Bloc
CREATE TABLE bloc_etudiant (
    id SERIAL PRIMARY KEY,
    bloc_id INTEGER NOT NULL REFERENCES exam_bloc(id) ON DELETE CASCADE,
    etudiant_id INTEGER NOT NULL REFERENCES etudiants(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(bloc_id, etudiant_id)
);

CREATE INDEX idx_bloc_etudiant_bloc ON bloc_etudiant(bloc_id);
CREATE INDEX idx_bloc_etudiant_etudiant ON bloc_etudiant(etudiant_id);

-- Supervision Table
CREATE TABLE surveillance (
    id SERIAL PRIMARY KEY,
    bloc_id INTEGER NOT NULL REFERENCES exam_bloc(id) ON DELETE CASCADE,
    prof_id INTEGER NOT NULL REFERENCES professeurs(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(bloc_id, prof_id)
);

CREATE INDEX idx_surveillance_bloc ON surveillance(bloc_id);
CREATE INDEX idx_surveillance_prof ON surveillance(prof_id);

-- =============================================
-- AUTHENTICATION & METADATA TABLES
-- =============================================

-- Users Table (for authentication)
-- =============================================
-- USERS TABLE (simplifiée)
-- =============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id INT,                        -- référence à etudiants, professeurs, départements
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,     -- mot de passe en clair (ou hashé si voulu)
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin','vice_doyen','chef_dept','professor','student')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_userid ON users(user_id);

-- Exam Schedule Metadata (tracks generation runs)
-- Updated with publication columns from v2
CREATE TABLE exam_schedule_metadata (
    id SERIAL PRIMARY KEY,
    generation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    start_date DATE NOT NULL,
    end_date DATE,
    execution_time_seconds DECIMAL(10, 2),
    total_exams INTEGER,
    total_blocs INTEGER,
    conflicts_detected INTEGER DEFAULT 0,
    conflicts_resolved INTEGER DEFAULT 0,
    generated_by INTEGER REFERENCES users(id),
    status VARCHAR(50) CHECK (status IN ('generating', 'completed', 'failed')),
    is_published BOOLEAN DEFAULT FALSE,
    global_validation_status VARCHAR(50) DEFAULT 'PENDING' CHECK (global_validation_status IN ('PENDING', 'VALIDATED', 'REJECTED')),
    notes TEXT
);

-- =============================================
-- VALIDATION WORKFLOW TABLES
-- =============================================

-- Validation State Table
CREATE TABLE validation_state (
    id SERIAL PRIMARY KEY,
    meta_id INTEGER REFERENCES exam_schedule_metadata(id) ON DELETE CASCADE,
    validator_role VARCHAR(50) NOT NULL CHECK (validator_role IN ('CHEF_DEPT', 'VICE_DOYEN')),
    dept_id INTEGER REFERENCES departements(id) ON DELETE CASCADE, -- Nullable for Vice Doyen
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'VALIDATED', 'INVALIDATED')),
    comment TEXT,
    validator_user_id INTEGER REFERENCES users(id),
    val_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one validation record per role/dept per schedule
    CONSTRAINT unique_validation_entry UNIQUE NULLS NOT DISTINCT (meta_id, validator_role, dept_id)
);


-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- View: Student Exam Schedule
CREATE OR REPLACE VIEW v_student_exam_schedule AS
SELECT 
    e.id AS etudiant_id,
    e.nom AS etudiant_nom,
    e.prenom AS etudiant_prenom,
    e.groupe,
    m.nom AS module_nom,
    ex.date_heure,
    ex.duree_minutes,
    l.nom AS salle_nom,
    l.type AS salle_type
FROM etudiants e
JOIN inscriptions i ON e.id = i.etudiant_id
JOIN modules m ON i.module_id = m.id
JOIN examens ex ON m.id = ex.module_id
JOIN exam_bloc eb ON ex.id = eb.examen_id
JOIN bloc_etudiant be ON eb.id = be.bloc_id AND be.etudiant_id = e.id
JOIN lieu_examen l ON eb.salle_id = l.id
ORDER BY e.id, ex.date_heure;

-- View: Professor Supervision Schedule
CREATE OR REPLACE VIEW v_professor_supervision AS
SELECT 
    p.id AS professeur_id,
    p.nom AS professeur_nom,
    p.prenom AS professeur_prenom,
    m.nom AS module_nom,
    ex.date_heure,
    ex.duree_minutes,
    l.nom AS salle_nom,
    l.type AS salle_type,
    COUNT(be.etudiant_id) AS nb_etudiants
FROM professeurs p
JOIN surveillance s ON p.id = s.prof_id
JOIN exam_bloc eb ON s.bloc_id = eb.id
JOIN examens ex ON eb.examen_id = ex.id
JOIN modules m ON ex.module_id = m.id
JOIN lieu_examen l ON eb.salle_id = l.id
LEFT JOIN bloc_etudiant be ON eb.id = be.bloc_id
GROUP BY p.id, p.nom, p.prenom, m.nom, ex.date_heure, ex.duree_minutes, l.nom, l.type
ORDER BY p.id, ex.date_heure;

-- =============================================
-- INITIAL DATA
-- =============================================

-- Create admin users (default password: 'admin123' - will be hashed in application)
INSERT INTO users (username, password_hash, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgdOwU76i', 'admin'),
('vicedoyen', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgdOwU76i', 'vice_doyen');

-- =============================================
-- END OF SCHEMA
-- =============================================
