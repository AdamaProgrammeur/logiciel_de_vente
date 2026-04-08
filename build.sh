#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd gestion_stock
python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from stock.models import Boutique

User = get_user_model()

# Supprimer et recréer
User.objects.filter(username='superadmin').delete()
u = User(
    username='superadmin',
    email='superadmin@stockpro.com',
    is_staff=True,
    is_superuser=True,
    role='admin'
)
u.set_password('stockpro2024')
u.save()
print(f"Superuser créé : {u.username} / staff={u.is_staff} / superuser={u.is_superuser}")

# Approuver boutiques
count = Boutique.objects.filter(statut='en_attente').update(statut='approuvee')
print(f"{count} boutique(s) approuvée(s)")
EOF
