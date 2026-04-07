import requests

BASE_URL = "http://127.0.0.1:8000/api/"
AUTH = ('admin', 'password')  # ton superuser ou utilisateur

# -------------------------------
# 1️⃣ Lister tous les produits
response = requests.get(f"{BASE_URL}produits/", auth=AUTH)
print("Produits :", response.json())

# -------------------------------
# 2️⃣ Ajouter un nouveau produit
nouveau_produit = {
    "nom": "Ordinateur Portable",
    "stock": 10,
    "prix": "450000.00",
    "seuil_alerte": 2,
    "boutique": 1
}

response = requests.post(f"{BASE_URL}produits/", json=nouveau_produit, auth=AUTH)
print("Ajout produit :", response.json())

# -------------------------------
# 3️⃣ Ajouter une entrée de stock
entree = {
    "produit": 1,  # id du produit existant
    "quantite": 5
}

response = requests.post(f"{BASE_URL}entrees/", json=entree, auth=AUTH)
print("Ajout entrée stock :", response.json())

# -------------------------------
# 4️⃣ Créer une vente avec montant raisonnable
vente = {
    "boutique": 1,
    "produit": 1,
    "quantite": 2,
    "montant_paye": 1000  # paiement ≤ total automatique
}

response = requests.post(f"{BASE_URL}ventes/", json=vente, auth=AUTH)
vente_data = response.json()
print("Nouvelle vente :", vente_data)

# -------------------------------
# 5️⃣ Créer un paiement partiel
paiement = {
    "vente": vente_data['id'],
    "montant": 500,
    "methode": "Cash"
}

response = requests.post(f"{BASE_URL}paiements/", json=paiement, auth=AUTH)
print("Paiement :", response.json())

# -------------------------------
# 6️⃣ Dashboard résumé simple
# Récupérer toutes les ventes et calculer total encaissé / reste
ventes = requests.get(f"{BASE_URL}ventes/", auth=AUTH).json()
total_ventes = sum(float(v['total']) for v in ventes)
montant_paye = sum(float(v['montant_paye']) for v in ventes)
reste = total_ventes - montant_paye

print(f"\n--- Dashboard résumé ---")
print(f"Total ventes : {total_ventes}")
print(f"Montant payé : {montant_paye}")
print(f"Reste à payer : {reste}")