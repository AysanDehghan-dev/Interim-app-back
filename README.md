# InterimApp - Job Search Platform

InterimApp est une plateforme de recherche d'emploi intérim qui connecte les candidats et les entreprises.

## Structure du Projet

Le projet est divisé en deux parties principales :

- **Frontend** : Application React TypeScript
- **Backend** : API Flask avec MongoDB

## Prérequis

- Docker et Docker Compose
- Node.js et npm (pour le développement frontend)
- Python 3.9+ et Poetry (pour le développement backend)

## Installation et Lancement

### Avec Docker (Recommandé)

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/interim-app.git
   cd interim-app
   ```

2. Lancez les conteneurs avec Docker Compose :
   ```bash
   docker-compose up -d
   ```

3. Accédez à l'application :
   - Frontend : http://localhost:3000
   - Backend API : http://localhost:5000/api

### Développement Local

#### Backend (Flask)

1. Naviguez dans le dossier backend :
   ```bash
   cd backend
   ```

2. Installez les dépendances avec Poetry :
   ```bash
   poetry install
   ```

3. Initialisez la base de données avec des données de test :
   ```bash
   poetry run python seed_db.py
   ```

4. Lancez le serveur de développement :
   ```bash
   poetry run flask run --host=0.0.0.0
   ```

#### Frontend (React)

1. Naviguez dans le dossier frontend :
   ```bash
   cd frontend
   ```

2. Installez les dépendances :
   ```bash
   npm install
   ```

3. Lancez le serveur de développement :
   ```bash
   npm start
   ```

## Architecture

### Backend

- **Flask** : Framework web léger pour Python
- **MongoDB** : Base de données NoSQL
- **JWT** : Authentification basée sur les tokens
- **Marshmallow** : Sérialisation et validation des données

### Frontend

- **React** : Bibliothèque JavaScript pour construire des interfaces utilisateur
- **TypeScript** : Typage statique pour JavaScript
- **Styled Components** : CSS-in-JS pour le styling
- **React Router** : Navigation entre les pages

## API Endpoints

### Authentification

- `POST /api/auth/register/user` : Inscription utilisateur
- `POST /api/auth/register/company` : Inscription entreprise
- `POST /api/auth/login/user` : Connexion utilisateur
- `POST /api/auth/login/company` : Connexion entreprise

### Utilisateurs

- `GET /api/users/profile` : Obtenir le profil utilisateur
- `PUT /api/users/profile` : Mettre à jour le profil utilisateur
- `GET /api/users/applications` : Obtenir les candidatures de l'utilisateur
- `POST /api/users/experience` : Ajouter une expérience professionnelle
- `POST /api/users/education` : Ajouter une formation

### Entreprises

- `GET /api/companies` : Obtenir la liste des entreprises
- `GET /api/companies/{id}` : Obtenir les détails d'une entreprise
- `GET /api/companies/profile` : Obtenir le profil de l'entreprise connectée
- `PUT /api/companies/profile` : Mettre à jour le profil de l'entreprise
- `GET /api/companies/jobs` : Obtenir les offres d'emploi de l'entreprise connectée
- `GET /api/companies/{id}/jobs` : Obtenir les offres d'emploi d'une entreprise spécifique

### Offres d'Emploi

- `GET /api/jobs` : Recherche d'offres d'emploi avec filtres
- `GET /api/jobs/{id}` : Obtenir les détails d'une offre d'emploi
- `POST /api/jobs` : Créer une nouvelle offre d'emploi (entreprise uniquement)
- `PUT /api/jobs/{id}` : Mettre à jour une offre d'emploi (entreprise uniquement)
- `POST /api/jobs/{id}/apply` : Postuler à une offre d'emploi (utilisateur uniquement)
- `GET /api/jobs/{id}/applications` : Obtenir les candidatures pour une offre d'emploi (entreprise uniquement)

## Comptes de Test

### Utilisateurs
- Email: jean.dupont@example.com
- Mot de passe: password

- Email: marie.laurent@example.com
- Mot de passe: password

### Entreprises
- Email: contact@techcorp.example.com
- Mot de passe: password

- Email: contact@datainsight.example.com
- Mot de passe: password