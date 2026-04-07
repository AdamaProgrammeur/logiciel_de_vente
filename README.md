# 🏪 Gestion Stock Online

Application web de gestion de stock multi-boutiques développée avec Django REST Framework et Bootstrap 5.

---

## ✨ Fonctionnalités

- 🔐 Authentification JWT (cookies sécurisés)
- 🏬 Gestion multi-boutiques avec système d'approbation
- 👥 Gestion des utilisateurs (Admin / Employé)
- 📦 Gestion des produits et catégories
- 🛒 Achats fournisseurs avec suivi des paiements
- 💰 Ventes clients avec facturation PDF
- 💳 Suivi des paiements et restes à payer
- 📉 Gestion des dépenses
- 🔔 Alertes stock (rupture / stock faible)
- 📊 Rapports financiers avec filtres par période
- 🕓 Traces d'activité (historique complet)
- ⚠️ Alertes montant dépassé en temps réel

---

## 🛠️ Technologies

| Côté | Stack |
|------|-------|
| Backend | Django 5.1, Django REST Framework, SimpleJWT |
| Frontend | Bootstrap 5, Bootstrap Icons, JS Vanilla |
| Base de données | PostgreSQL |
| Authentification | JWT via cookies httponly |
| Déploiement | Render + Gunicorn + Whitenoise |

---

## 🚀 Installation locale

### 1. Cloner le projet

```bash
git clone https://github.com/AdamaProgrammeur/Gestion_Stock.git
cd Gestion_Stock
```

### 2. Créer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurer le fichier `.env`

Crée un fichier `.env` à la racine du projet :

```env
SECRET_KEY=ta-cle-secrete-ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=gestion_stock_db
DB_USER=ton_user
DB_PASSWORD=ton_mot_de_passe
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:8000
```

### 4. Créer la base de données PostgreSQL

```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE gestion_stock_db;
CREATE USER ton_user WITH PASSWORD 'ton_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE gestion_stock_db TO ton_user;
\q
```

### 5. Appliquer les migrations et lancer

```bash
cd gestion_stock
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Accède à l'app sur : **http://localhost:8000**

---

## 📁 Structure du projet

```
gestion_stock_online/
├── gestion_stock/
│   ├── gestion_stock/        # Configuration Django (settings, urls, wsgi)
│   ├── stock/                # API REST (models, views, serializers, urls)
│   ├── frontend_app/         # Templates HTML + vues frontend
│   └── manage.py
├── requirements.txt
├── build.sh                  # Script de déploiement Render
├── .env                      # Variables d'environnement (non versionné)
└── .gitignore
```

---

## 🌐 Déploiement sur Render

1. Crée une base **PostgreSQL** sur [render.com](https://render.com)
2. Crée un **Web Service** connecté à ce repo
3. Configure :
   - **Build Command** : `./build.sh`
   - **Start Command** : `cd gestion_stock && gunicorn gestion_stock.wsgi:application`
4. Ajoute les variables d'environnement (voir `.env` ci-dessus avec les infos Render)

---

## 👤 Auteur

**Adama Programmeur**
- 📞 +223 78 74 66 43
- GitHub : [@AdamaProgrammeur](https://github.com/AdamaProgrammeur)

---

## 📄 Licence

Ce projet est sous licence MIT.
