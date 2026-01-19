-- =============================================
-- DATA SEEDING SCRIPT
-- =============================================
-- Realistic data for 13,000+ students
-- Arabic names for students and professors
-- 7 departments, 200+ formations
-- =============================================

-- =============================================
-- 1. DEPARTMENTS
-- =============================================

INSERT INTO departements (nom) VALUES
('Informatique'),
('Mathématiques'), 
('Physique'),
('Chimie'),
('Sciences de la Vie'),
('Sciences Économiques'),
('Lettres et Langues');

-- =============================================
-- 2. FORMATIONS (200+ formations across levels)
-- =============================================

-- Informatique Formations
INSERT INTO formations (nom, dept_id, niveau) 
SELECT 
    'Licence Informatique ' || spec || ' - L' || niveau,
    (SELECT id FROM departements WHERE nom = 'Informatique'),
    niveau
FROM 
    unnest(ARRAY['Systèmes d''Information', 'Réseaux', 'Intelligence Artificielle', 'Génie Logiciel', 
                  'Cybersécurité', 'Informatique Générale', 'Systèmes Embarqués', 'Big Data']) AS spec,
    generate_series(1, 3) AS niveau;

INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Master ' || spec || ' - M' || (niveau - 3),
    (SELECT id FROM departements WHERE nom = 'Informatique'),
    niveau
FROM 
    unnest(ARRAY['IA et Apprentissage', 'Cybersécurité Avancée', 'Cloud Computing', 
                  'Réseaux Avancés', 'Génie Logiciel', 'Data Science']) AS spec,
    generate_series(4, 5) AS niveau;

-- Mathématiques Formations
INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Licence Mathématiques ' || spec || ' - L' || niveau,
    (SELECT id FROM departements WHERE nom = 'Mathématiques'),
    niveau
FROM 
    unnest(ARRAY['Pures', 'Appliquées', 'Statistiques', 'Actuariat', 'Modélisation', 
                  'Mathématiques Générales', 'Analyse Numérique']) AS spec,
    generate_series(1, 3) AS niveau;

INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Master Mathématiques ' || spec || ' - M' || (niveau - 3),
    (SELECT id FROM departements WHERE nom = 'Mathématiques'),
    niveau
FROM 
    unnest(ARRAY['Recherche Opérationnelle', 'Statistiques Avancées', 'Modélisation', 
                  'Analyse Numérique', 'Cryptographie']) AS spec,
    generate_series(4, 5) AS niveau;

-- Physique Formations
INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Licence Physique ' || spec || ' - L' || niveau,
    (SELECT id FROM departements WHERE nom = 'Physique'),
    niveau
FROM 
    unnest(ARRAY['Fondamentale', 'Appliquée', 'Énergétique', 'Matériaux', 
                  'Physique Médicale', 'Optique']) AS spec,
    generate_series(1, 3) AS niveau;

INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Master Physique ' || spec || ' - M' || (niveau - 3),
    (SELECT id FROM departements WHERE nom = 'Physique'),
    niveau
FROM 
    unnest(ARRAY['Physique Théorique', 'Nanotechnologie', 'Énergies Renouvelables', 
                  'Physique Nucléaire']) AS spec,
    generate_series(4, 5) AS niveau;

-- Chimie Formations
INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Licence Chimie ' || spec || ' - L' || niveau,
    (SELECT id FROM departements WHERE nom = 'Chimie'),
    niveau
FROM 
    unnest(ARRAY['Organique', 'Inorganique', 'Analytique', 'Industrielle', 
                  'Pharmaceutique', 'Environnementale']) AS spec,
    generate_series(1, 3) AS niveau;

INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Master Chimie ' || spec || ' - M' || (niveau - 3),
    (SELECT id FROM departements WHERE nom = 'Chimie'),
    niveau
FROM 
    unnest(ARRAY['Chimie Fine', 'Polymères', 'Catalyse', 'Chimie Verte']) AS spec,
    generate_series(4, 5) AS niveau;

-- Sciences de la Vie Formations
INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Licence Biologie ' || spec || ' - L' || niveau,
    (SELECT id FROM departements WHERE nom = 'Sciences de la Vie'),
    niveau
FROM 
    unnest(ARRAY['Cellulaire', 'Moléculaire', 'Écologie', 'Microbiologie', 
                  'Génétique', 'Biochimie']) AS spec,
    generate_series(1, 3) AS niveau;

INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Master Biologie ' || spec || ' - M' || (niveau - 3),
    (SELECT id FROM departements WHERE nom = 'Sciences de la Vie'),
    niveau
FROM 
    unnest(ARRAY['Biotechnologie', 'Génomique', 'Immunologie', 'Neurosciences']) AS spec,
    generate_series(4, 5) AS niveau;

-- Sciences Économiques Formations
INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Licence ' || spec || ' - L' || niveau,
    (SELECT id FROM departements WHERE nom = 'Sciences Économiques'),
    niveau
FROM 
    unnest(ARRAY['Économie', 'Gestion', 'Finance', 'Commerce International', 
                  'Marketing', 'Comptabilité', 'Management']) AS spec,
    generate_series(1, 3) AS niveau;

INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Master ' || spec || ' - M' || (niveau - 3),
    (SELECT id FROM departements WHERE nom = 'Sciences Économiques'),
    niveau
FROM 
    unnest(ARRAY['Finance d''Entreprise', 'Audit', 'Marketing Stratégique', 
                  'Management International', 'Économie Quantitative']) AS spec,
    generate_series(4, 5) AS niveau;

-- Lettres et Langues Formations
INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Licence ' || spec || ' - L' || niveau,
    (SELECT id FROM departements WHERE nom = 'Lettres et Langues'),
    niveau
FROM 
    unnest(ARRAY['Langue Arabe', 'Langue Française', 'Langue Anglaise', 
                  'Traduction', 'Littérature', 'Linguistique']) AS spec,
    generate_series(1, 3) AS niveau;

INSERT INTO formations (nom, dept_id, niveau)
SELECT 
    'Master ' || spec || ' - M' || (niveau - 3),
    (SELECT id FROM departements WHERE nom = 'Lettres et Langues'),
    niveau
FROM 
    unnest(ARRAY['Traduction Spécialisée', 'Linguistique Appliquée', 
                  'Littérature Comparée', 'Didactique']) AS spec,
    generate_series(4, 5) AS niveau;

-- =============================================
-- 3. MODULES (6-9 modules per formation)
-- =============================================

-- Helper function to create modules for a formation
DO $$
DECLARE
    formation_rec RECORD;
    module_names TEXT[] := ARRAY[
        'Analyse Mathématique', 'Algèbre Linéaire', 'Algorithmique', 'Programmation',
        'Bases de Données', 'Systèmes d''Exploitation', 'Réseaux Informatiques',
        'Génie Logiciel', 'Intelligence Artificielle', 'Théorie des Graphes',
        'Probabilités et Statistiques', 'Physique Générale', 'Chimie Générale',
        'Thermodynamique', 'Mécanique Quantique', 'Optique', 'Électromagnétisme',
        'Biologie Cellulaire', 'Génétique', 'Biochimie', 'Microbiologie',
        'Économie Générale', 'Microéconomie', 'Macroéconomie', 'Comptabilité',
        'Finance', 'Marketing', 'Management', 'Droit Commercial',
        'Langue Arabe', 'Grammaire', 'Littérature', 'Traduction', 'Linguistique',
        'Philosophie', 'Logique', 'Méthodologie', 'Recherche Opérationnelle'
    ];
    num_modules INTEGER;
    i INTEGER;
BEGIN
    FOR formation_rec IN SELECT id, nom FROM formations LOOP
        num_modules := 6 + floor(random() * 4)::INTEGER; -- 6-9 modules
        
        FOR i IN 1..num_modules LOOP
            INSERT INTO modules (nom, credits, formation_id, semestre)
            VALUES (
                module_names[(floor(random() * array_length(module_names, 1)) + 1)::INTEGER] || ' ' || i,
                6,
                formation_rec.id,
                CASE WHEN i <= num_modules / 2 THEN 1 ELSE 2 END
            );
        END LOOP;
    END LOOP;
END $$;

-- =============================================
-- 4. EXAM LOCATIONS
-- =============================================

-- Classrooms (capacity ~20)
INSERT INTO lieu_examen (nom, capacite, type)
SELECT 
    'Classe ' || floor_num || '.' || room_num,
    18 + floor(random() * 5)::INTEGER, -- 18-22
    'classe'
FROM 
    generate_series(1, 5) AS floor_num,
    generate_series(1, 30) AS room_num;

-- Amphitheaters (capacity ~90)
INSERT INTO lieu_examen (nom, capacite, type)
SELECT 
    'Amphithéâtre ' || chr(64 + amphi_num),
    85 + floor(random() * 15)::INTEGER, -- 85-99
    'amphi'
FROM 
    generate_series(1, 15) AS amphi_num;

-- =============================================
-- 5. PROFESSORS (Realistic Arabic Names)
-- =============================================

DO $$
DECLARE
    dept_rec RECORD;
    first_names TEXT[] := ARRAY[
        'Ahmed', 'Mohamed', 'Ali', 'Omar', 'Youssef', 'Karim', 'Nabil', 'Samir',
        'Mehdi', 'Bilal', 'Rami', 'Tarek', 'Walid', 'Farid', 'Hicham', 'Rachid',
        'Amine', 'Sofiane', 'Reda', 'Hamza', 'Fatima', 'Amina', 'Khadija',
        'Aicha', 'Samira', 'Malika', 'Nadia', 'Salma', 'Meriem', 'Yasmine',
        'Leila', 'Karima', 'Souad', 'Wafa', 'Hanane'
    ];
    last_names TEXT[] := ARRAY[
        'Benali', 'Hassani', 'Mansouri', 'Kaddour', 'Brahimi', 'Saadi', 'Rahmani',
        'Meziane', 'Gharbi', 'Cherif', 'Bouazza', 'Hamdi', 'Boumediene', 'Yahia',
        'Belkacem', 'Djebbar', 'Ouali', 'Mammeri', 'Amrani', 'Taleb', 'Bouzid',
        'Slimani', 'Zaidi', 'Fergani', 'Boukhari', 'Chaoui'
    ];
    specialties TEXT[] := ARRAY[
        'Algorithmique', 'Bases de Données', 'Intelligence Artificielle', 'Réseaux',
        'Analyse Mathématique', 'Algèbre', 'Statistiques', 'Physique Théorique',
        'Chimie Organique', 'Biologie Moléculaire', 'Économie', 'Gestion',
        'Linguistique', 'Littérature'
    ];
    num_profs INTEGER;
    i INTEGER;
BEGIN
    FOR dept_rec IN SELECT id FROM departements LOOP
        num_profs := 25 + floor(random() * 16)::INTEGER; -- 25-40 professors per dept
        
        FOR i IN 1..num_profs LOOP
            INSERT INTO professeurs (nom, prenom, dept_id, specialite)
            VALUES (
                last_names[(floor(random() * array_length(last_names, 1)) + 1)::INTEGER],
                first_names[(floor(random() * array_length(first_names, 1)) + 1)::INTEGER],
                dept_rec.id,
                specialties[(floor(random() * array_length(specialties, 1)) + 1)::INTEGER]
            );
        END LOOP;
    END LOOP;
END $$;

-- =============================================
-- 6. STUDENTS (13,000+ with Arabic Names)
-- =============================================

DO $$
DECLARE
    formation_rec RECORD;
    first_names_m TEXT[] := ARRAY[
        'Mohamed', 'Ahmed', 'Ali', 'Omar', 'Youssef', 'Amine', 'Karim', 'Mehdi',
        'Bilal', 'Hamza', 'Rami', 'Samir', 'Tarek', 'Walid', 'Sofiane', 'Reda',
        'Nabil', 'Farid', 'Hicham', 'Rachid', 'Abdallah', 'Ibrahim', 'Ismail',
        'Khalil', 'Mourad', 'Nadir', 'Oussama', 'Sami', 'Zakaria', 'Adel'
    ];
    first_names_f TEXT[] := ARRAY[
        'Fatima', 'Amina', 'Khadija', 'Aicha', 'Meriem', 'Yasmine', 'Samira',
        'Salma', 'Nadia', 'Leila', 'Karima', 'Malika', 'Hanane', 'Wafa', 'Souad',
        'Houria', 'Latifa', 'Naima', 'Sabrina', 'Sarah', 'Zineb', 'Imane',
        'Kenza', 'Lina', 'Nesrine', 'Rania', 'Siham', 'Widad'
    ];
    last_names TEXT[] := ARRAY[
        'Benali', 'Hassani', 'Mansouri', 'Kaddour', 'Brahimi', 'Saadi', 'Rahmani',
        'Meziane', 'Gharbi', 'Cherif', 'Bouazza', 'Hamdi', 'Boumediene', 'Yahia',
        'Belkacem', 'Djebbar', 'Ouali', 'Mammeri', 'Amrani', 'Taleb', 'Bouzid',
        'Slimani', 'Zaidi', 'Fergani', 'Boukhari', 'Chaoui', 'Mokrani', 'Benziane',
        'Khelifi', 'Guessab', 'Toumi', 'Benameur', 'Hadj', 'Bensalah', 'Djoudi'
    ];
    students_per_formation INTEGER;
    groups TEXT[] := ARRAY['G1', 'G2', 'G3', 'G4'];
    i INTEGER;
    gender BOOLEAN;
BEGIN
    FOR formation_rec IN SELECT id, niveau FROM formations LOOP
        -- More students in lower levels
        students_per_formation := CASE 
            WHEN formation_rec.niveau <= 2 THEN 80 + floor(random() * 41)::INTEGER -- 80-120
            WHEN formation_rec.niveau = 3 THEN 50 + floor(random() * 31)::INTEGER -- 50-80
            ELSE 20 + floor(random() * 21)::INTEGER -- 20-40 for Masters
        END;
        
        FOR i IN 1..students_per_formation LOOP
            gender := random() > 0.5;
            
            INSERT INTO etudiants (nom, prenom, formation_id, promo, groupe)
            VALUES (
                last_names[(floor(random() * array_length(last_names, 1)) + 1)::INTEGER],
                CASE 
                    WHEN gender THEN first_names_m[(floor(random() * array_length(first_names_m, 1)) + 1)::INTEGER]
                    ELSE first_names_f[(floor(random() * array_length(first_names_f, 1)) + 1)::INTEGER]
                END,
                formation_rec.id,
                2024 + formation_rec.niveau,
                groups[(floor(random() * 4) + 1)::INTEGER]
            );
        END LOOP;
    END LOOP;
END $$;

-- =============================================
-- 7. STUDENT INSCRIPTIONS
-- =============================================

-- Enroll all students in all modules of their formation
INSERT INTO inscriptions (etudiant_id, module_id, annee_academique)
SELECT 
    e.id,
    m.id,
    '2025-2026'
FROM etudiants e
JOIN formations f ON e.formation_id = f.id
JOIN modules m ON m.formation_id = f.id;

-- =============================================
-- 3. USERS TABLE SEEDING
-- =============================================

-- 1. Chefs de département
INSERT INTO users (user_id, username, password, role)
SELECT 
    id,                                      -- id du département
    'chef_' || LOWER(REPLACE(nom, ' ', '_')), -- username = chef_nomdepartement
    'admin123',                               -- password fixe
    'chef_dept'
FROM departements
ON CONFLICT (username) DO NOTHING;

-- 2. Professeurs
INSERT INTO users (user_id, username, password, role)
SELECT 
    id,             -- id du professeur
    id::TEXT,       -- username = id
    nom || prenom,  -- password = nom + prenom
    'professor'
FROM professeurs
ON CONFLICT (username) DO NOTHING;

-- 3. Étudiants
INSERT INTO users (user_id, username, password, role)
SELECT 
    id,             -- id de l'étudiant
    id::TEXT,       -- username = id
    nom || prenom,  -- password = nom + prenom
    'student'
FROM etudiants
ON CONFLICT (username) DO NOTHING;

-- 4. Admin et Vice-Doyen
INSERT INTO users (user_id, username, password, role) VALUES
(NULL, '1', 'adminadmin', 'admin'),
(NULL, '2', 'vicedoyenvicedoyen', 'vice_doyen')
ON CONFLICT (username) DO NOTHING;
-- =============================================
-- SUMMARY STATISTICS
-- =============================================

DO $$
DECLARE
    dept_count INTEGER;
    formation_count INTEGER;
    module_count INTEGER;
    student_count INTEGER;
    prof_count INTEGER;
    inscription_count INTEGER;
    room_count INTEGER;
    amphi_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO dept_count FROM departements;
    SELECT COUNT(*) INTO formation_count FROM formations;
    SELECT COUNT(*) INTO module_count FROM modules;
    SELECT COUNT(*) INTO student_count FROM etudiants;
    SELECT COUNT(*) INTO prof_count FROM professeurs;
    SELECT COUNT(*) INTO inscription_count FROM inscriptions;
    SELECT COUNT(*) INTO room_count FROM lieu_examen WHERE type = 'classe';
    SELECT COUNT(*) INTO amphi_count FROM lieu_examen WHERE type = 'amphi';
    
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'DATABASE SEEDING COMPLETE';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Departments: %', dept_count;
    RAISE NOTICE 'Formations: %', formation_count;
    RAISE NOTICE 'Modules: %', module_count;
    RAISE NOTICE 'Students: %', student_count;
    RAISE NOTICE 'Professors: %', prof_count;
    RAISE NOTICE 'Inscriptions: %', inscription_count;
    RAISE NOTICE 'Classrooms: %', room_count;
    RAISE NOTICE 'Amphitheaters: %', amphi_count;
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Default login credentials:';
    RAISE NOTICE '  Admin: username=admin, password=admin123';
    RAISE NOTICE '  Vice-Doyen: username=vicedoyen, password=admin123';
    RAISE NOTICE '  Chef Dept: username=chef_[dept_name], password=admin123';
    RAISE NOTICE '  Professor: username=[prenom].[nom], password=admin123';
    RAISE NOTICE '  Student: username=[prenom].[nom].[id], password=admin123';
    RAISE NOTICE '==============================================';
END $$;
