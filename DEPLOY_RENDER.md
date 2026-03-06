Déploiement sur Render — guide pas-à-pas

Ce document décrit comment déployer SmartApp sur Render (service PaaS simple et gratuit pour petits projets).

1) Pré-requis
- Compte GitHub avec votre repo `hamzap-ux/SmartApp` poussé sur `main`.
- Compte Render (https://render.com).

2) Vérifications locales (optionnel)
- Assurez-vous que `requirements.txt` contient `gunicorn` (déjà fait).
- `main.py` lit `SECRET_KEY` depuis la variable d'environnement (déjà fait).

Tester localement avec gunicorn :
```bash
pip install -r requirements.txt
pip install gunicorn
gunicorn main:app --workers 3 --bind 0.0.0.0:5000
# ouvrir http://localhost:5000
```

3) Créer un nouveau service sur Render
- Connectez-vous à Render et choisissez "New" → "Web Service".
- Connectez votre compte GitHub et sélectionnez le repository `hamzap-ux/SmartApp`.
- Branch: `main`.
- Root Directory: (laisser vide si la racine du repo contient `main.py`).

4) Settings (Build & Start)
- Build Command: `pip install -r requirements.txt` (Render détecte Python automatiquement si présent).
- Start Command: `gunicorn main:app --workers 3 --bind 0.0.0.0:$PORT`
  - Vous pouvez aussi laisser Render utiliser le `Procfile` que j'ai ajouté.
- Environment: choisissez `Python 3.11` (ou similaire).

5) Variables d'environnement (Environment > Environment Variables)
- `SECRET_KEY`: valeur forte aléatoire (ex: `openssl rand -hex 32`).
- `AWS_REGION`, `SENDER_EMAIL`: si vous utilisez AWS SES pour envois d'email.
- Toute autre variable dont vous auriez besoin.

6) Persistances et base de données
- Par défaut l'app utilise SQLite (`data/database.sqlite`). Render propose un disque persistant pour un service Web standard, mais pour production multi-instance, préférez Postgres.
- Si vous restez avec SQLite, assurez-vous que la table `data/` est écrite dans le répertoire persisté et que vous avez un plan de backup.

7) Lancer et vérifier
- Déployez (Render va builder et lancer l’app).
- Ouvrez l’URL fournie par Render. Testez les pages, login/register.

8) Logs et debugging
- Utilisez le panneau « Logs » de Render pour voir stderr/stdout pendant le build et l’exécution.
- Activez ou inspectez les messages d’erreur pour corriger rapidement.

9) Optionnel — stocker avatars et fichiers
- Pour stockage durable et scalable, configurez un bucket S3 (ou équivalent) et mettez à jour le code pour envoyer/servir les avatars depuis ce bucket.

10) Sécurité
- Ne stockez pas `SECRET_KEY` dans le repo.
- Configurez HTTPS (Render fournit un TLS automatiquement pour les services publics).

Si vous voulez, je peux maintenant :
- tenter de pousser les commits (je peux exécuter `git push` ici si vous voulez que j'essaie), ou
- créer un petit script de migration pour initialiser la DB sur le serveur, ou
- ajouter des instructions pour configurer Postgres et migrer depuis SQLite.
