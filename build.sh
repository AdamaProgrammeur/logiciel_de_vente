#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd gestion_stock
python manage.py collectstatic --no-input
python manage.py migrate

# Créer superuser automatiquement si pas encore créé
python manage.py shell << 'EOF'
from stock.models import User, Boutique
import os

# Créer superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@stockpro.com',
        password='Admin@1234'
    )
    print("Superuser créé")

# Approuver toutes les boutiques en attente
Boutique.objects.filter(statut='en_attente').update(statut='approuvee')
print("Boutiques approuvées")
EOF
