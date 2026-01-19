# 📚 Plateforme d'Optimisation des Examens Universitaires

Système automatisé de génération et gestion des emplois du temps d'examens pour universités.

## 🎯 Caractéristiques

- **Génération Automatique**: Planning optimisé en <45 secondes
- **Gestion Intelligente des Salles**: 
  - Fusion de groupes dans les amphithéâtres
  - Division automatique des grands groupes
- **Contraintes Respectées**:
  - ✅ Pas d'examens le vendredi (weekend)
  - ✅ Maximum 1 examen par étudiant par jour
  - ✅ Maximum 3 surveillances par professeur par jour
  - ✅ Respect des capacités des salles
- **5 Dashboards Professionnels**: Vice-Doyen, Admin, Chef Dept, Étudiant, Professeur
- **Analytics Avancés**: KPIs, graphiques, détection de conflits

## 🛠️ Technologies

- **Backend**: Python 3.8+
- **Frontend**: Streamlit
- **Base de Données**: PostgreSQL 12+
- **Visualisation**: Plotly, Pandas

## 📋 Prérequis

1. **PostgreSQL** installé et en cours d'exécution (port 5432)
2. **Python 3.8+** 
3. **pgAdmin 4** (optionnel, pour gestion visuelle)

## 🚀 Installation

### 1. Créer la base de données

Ouvrir pgAdmin ou psql et créer la base de données:

```sql
CREATE DATABASE exams;
```

### 2. Installer les dépendances Python

```powershell
cd C:\Users\aBC\Desktop\crb\exam_scheduling
pip install -r requirements.txt
```

### 3. Initialiser le schéma de la base de données

Dans pgAdmin, se connecter à la base `exams` et exécuter:

1. `database/001_schema.sql` - Crée toutes les tables
2. `database/002_seed_data.sql` - Génère les données de test

**OU** via psql:

```powershell
cd database
psql -U postgres -d exams -f 001_schema.sql
psql -U postgres -d exams -f 002_seed_data.sql
```

Mot de passe PostgreSQL: `0000`

### 4. Vérifier la configuration

Ouvrir `config.py` et vérifier:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'exams',
    'user': 'postgres',
    'password': '0000'
}
```

## ▶️ Lancement de l'Application

```powershell
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à `http://localhost:8501`

## 👥 Comptes de Démonstration

### Identifiants par défaut (mot de passe: `admin123`)

| Rôle | Username | Accès |
|------|----------|-------|
| **Admin** | `admin` | Génération planning, stats globales |
| **Vice-Doyen** | `vicedoyen` | Vue globale, validation |
| **Chef Dept** | `chef_informatique` | Stats département |
| **Professeur** | `[prenom].[nom]` | Planning surveillance |
| **Étudiant** | `[prenom].[nom].[id]` | Emploi du temps perso |

**Exemples**:
- Chef Dept: `chef_informatique` / `admin123`
- Professeur: `ahmed.benali` / `admin123`
- Étudiant: `mohamed.hassani.0001` / `admin123`

## 📚 Structure du Projet

```
exam_scheduling/
├── app.py                      # Application principale
├── config.py                   # Configuration
├── requirements.txt            # Dépendances Python
├── backend/
│   ├── database.py            # Connexion PostgreSQL
│   ├── auth.py                # Authentification
│   ├── scheduler.py           # Algorithme d'optimisation
│   └── queries.py             # Requêtes analytiques
├── pages/
│   ├── vice_doyen.py          # Dashboard Vice-Doyen
│   ├── exam_admin.py          # Dashboard Admin
│   ├── chef_dept.py           # Dashboard Chef Dept
│   ├── student.py             # Dashboard Étudiant
│   └── professor.py           # Dashboard Professeur
└── database/
    ├── 001_schema.sql         # Schéma DB
    └── 002_seed_data.sql      # Données de test
```

## 🎓 Utilisation

### 1. Connexion

Utiliser un des comptes de démonstration listés ci-dessus.

### 2. Génération du Planning (Admin)

1. Se connecter avec `admin` / `admin123`
2. Aller dans l'onglet "🎯 Génération Planning"
3. Choisir la date de début (évite automatiquement les vendredis)
4. Choisir la durée des examens (90, 120 ou 180 minutes)
5. Cliquer sur "🚀 Générer le Planning"
6. Attendre <45 secondes

### 3. Consultation

Chaque rôle a accès à ses informations:
- **Vice-Doyen**: KPIs globaux, stats départements
- **Admin**: Génération, stats, conflits, calendrier
- **Chef Dept**: Stats de son département
- **Étudiant**: Emploi du temps personnel
- **Professeur**: Planning de surveillance

## 🔧 Configuration Avancée

### Modifier les créneaux horaires

Dans `config.py`:

```python
EXAM_TIME_SLOTS = [
    8,   # 08:00
    10,  # 10:00
    13,  # 13:00
    15   # 15:00
]
```

### Changer le nombre max de surveillances

```python
MAX_SUPERVISIONS_PER_DAY = 3
```

### Exclure d'autres jours

```python
ALLOWED_DAYS = [0, 1, 2, 3, 6]  # 0=Lundi, 4=Vendredi (exclu)
```

## 📊 Données Générées

- **7** départements
- **200+** formations
- **13,000+** étudiants (noms arabes réalistes)
- **180+** professeurs (noms arabes réalistes)
- **1200+** modules
- **130,000+** inscriptions
- **150+** salles de classe
- **15** amphithéâtres

## 🐛 Dépannage

### Erreur de connexion à PostgreSQL

1. Vérifier que PostgreSQL est en cours d'exécution
2. Vérifier le mot de passe dans `config.py`
3. Tester la connexion:

```powershell
psql -U postgres -d exams
```

### Base de données vide

Réexécuter les scripts SQL:

```powershell
cd database
psql -U postgres -d exams -f 001_schema.sql
psql -U postgres -d exams -f 002_seed_data.sql
```

### Erreur de module Python

Réinstaller les dépendances:

```powershell
pip install -r requirements.txt --upgrade
```

## 📝 Notes Importantes

- **Vendredi = Weekend**: Automatiquement exclu de la planification
- **Mots de passe**: Changer `admin123` en production
- **Performance**: Génération optimisée pour 13,000+ étudiants
- **Encodage**: UTF-8 pour noms arabes

## 🎯 Fonctionnalités Futures

- Export PDF des emplois du temps
- Notifications email
- API REST
- Application mobile
- Multi-session (examens rattrapages)

## 📄 Licence

Projet académique - Université

## 👨‍💻 Support

Pour toute question, vérifier:
1. Les logs de l'application Streamlit
2. Les logs PostgreSQL
3. La console Python pour les erreurs

---

**Développé avec ❤️ pour optimiser la gestion des examens universitaires**
