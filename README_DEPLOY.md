Déploiement (Render / Heroku / Railway)

Ce guide couvre le déploiement d'une instance complète de SmartApp (Flask) en production.

1) Pré-requis
- Avoir le repository sur GitHub.
- Un compte Render / Heroku / Railway (ou un VPS).

2) Fichiers importants ajoutés
- `Procfile` : démarrage avec `gunicorn main:app`.
- `requirements.txt` : contient désormais `gunicorn`.
- `Dockerfile` + `.dockerignore` : option de déploiement conteneurisé.
- `main.py` : lit `SECRET_KEY` depuis la variable d'environnement.

3) Variables d'environnement à configurer
- `SECRET_KEY` (fortement recommandé).
- `AWS_REGION`, `SENDER_EMAIL` si vous utilisez l'envoi d'emails via AWS SES.
- Toute autre clé (`SENDER_EMAIL`, `AWS_*`, etc.).
 
Secrets / Tokens supplémentaires pour CI
- `GHCR_PAT` (optionnel) : Personal Access Token avec `write:packages` scope — utilisé en fallback pour publier sur GitHub Container Registry si `GITHUB_TOKEN` est restreint.
- `DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN` : requis pour pousser sur Docker Hub via le workflow `dockerhub-publish`.
- `GH_PAGES_PAT` (optionnel) : Personal Access Token avec `repo` scope — utilisé pour publier sur GitHub Pages si le `GITHUB_TOKEN` n'a pas les droits d'écriture.

4) Déploiement rapide sur Render
- Connectez votre repository à Render (New -> Web Service).
- Branch: `main`.
- Build command: `pip install -r requirements.txt` (Render le détecte automatiquement si vous utilisez Python).
- Start command: `gunicorn main:app --workers 3 --bind 0.0.0.0:$PORT` (ou laisser Render utiliser `Procfile`).
- Déclarez les variables d'environnement via le dashboard (au minimum `SECRET_KEY`).

5) Utilisation de SQLite en production
- SQLite est un fichier local : pour une vraie production, préférez une base distante (Postgres, MySQL).
- Si vous conservez SQLite, vérifiez la persistance des fichiers (les services serverless réinitialisent l’espace disque régulièrement).

6) Exécuter localement avec gunicorn (test de production simple)
```bash
pip install -r requirements.txt
pip install gunicorn
gunicorn main:app --workers 3 --bind 0.0.0.0:5000
```

7) Option conteneurisée (Docker)
- Construire : `docker build -t smartapp .`
- Lancer : `docker run -p 5000:5000 -e SECRET_KEY=changeme smartapp`

8) Suggestions
- Remplacer l'utilisation de SQLite par Postgres si vous avez plusieurs instances.
- Stocker les fichiers d'avatar sur un storage externe (S3/MinIO) plutôt que local.

Si vous voulez, je peux :
- créer et configurer un workflow GitHub Actions pour build/push d’image Docker automatique ;
- ajouter une migration simple pour basculer vers Postgres ;
- préparer les commandes pour Render / Railway pas à pas et variables à renseigner.
