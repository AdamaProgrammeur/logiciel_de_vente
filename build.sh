#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd gestion_stock
python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell << 'EOF'
from stock.models import User, Boutique

# Supprimer et recréer le superuser
User.objects.filter(username='superadmin').delete()
u = User.objects.create_superuser(
    username='superadmin',
    email='superadmin@stockpro.com',
    password='stockpro2026'
)
u.is_staff = True
u.is_superuser = True
u.save()
print("Superuser superadmin créé avec succès")

# Approuver toutes les boutiques
count = Boutique.objects.filter(statut='en_attente').update(statut='approuvee')
print(f"{count} boutique(s) approuvée(s)")
EOF
