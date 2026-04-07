from rest_framework import serializers
from django.db.models import Sum
from .models import (
    Boutique, User, Produit, Categorie, Fournisseur, Client,
    EntreeStock, ProduitAchat, Vente, ProduitVente, Paiement, Depense
)


class BoutiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boutique
        fields = ['id', 'nom', 'slogan', 'description', 'logo',
                  'couleur_principale', 'adresse', 'telephone', 'email', 'date_creation']
        read_only_fields = ['id', 'date_creation']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'boutique', 'password']
        read_only_fields = ['boutique']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CategorieSerializer(serializers.ModelSerializer):
    boutique = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'boutique']

    def create(self, validated_data):
        validated_data.pop('boutique', None)
        boutique = self.context['request'].user.boutique
        return Categorie.objects.create(boutique=boutique, **validated_data)


class ProduitSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    categorie_id = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(), source='categorie', allow_null=True, required=False
    )

    class Meta:
        model = Produit
        fields = ['id', 'nom', 'stock_actuelle', 'prix', 'seuil_alerte',
                  'categorie_nom', 'categorie_id', 'boutique', 'alerte_stock']
        read_only_fields = ['boutique', 'alerte_stock']


class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = ['id', 'nom', 'telephone', 'adresse', 'boutique']
        read_only_fields = ['boutique']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'nom', 'telephone', 'adresse', 'boutique']
        read_only_fields = ['boutique']


class ProduitAchatSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)

    class Meta:
        model = ProduitAchat
        fields = ['id', 'produit', 'produit_nom', 'quantite', 'prix_unitaire']


class EntreeStockSerializer(serializers.ModelSerializer):
    fournisseur_nom = serializers.CharField(source='fournisseur.nom', read_only=True)
    produits = ProduitAchatSerializer(many=True)
    total = serializers.SerializerMethodField()
    reste = serializers.SerializerMethodField()

    class Meta:
        model = EntreeStock
        fields = ['id', 'fournisseur', 'fournisseur_nom', 'date', 'produits', 'montant_paye', 'total', 'reste']
        read_only_fields = ['date']

    def get_total(self, obj):
        return float(sum(p.quantite * p.prix_unitaire for p in obj.produits.all()))

    def get_reste(self, obj):
        return float(self.get_total(obj) - float(obj.montant_paye))

    def create(self, validated_data):
        produits_data = validated_data.pop('produits')
        entree = EntreeStock.objects.create(**validated_data)
        for p in produits_data:
            ProduitAchat.objects.create(entree=entree, **p)
            produit = p['produit']
            produit.stock_actuelle += p['quantite']
            produit.check_alerte_stock()
        return entree

    def update(self, instance, validated_data):
        produits_data = validated_data.pop('produits', [])
        # Annuler ancien stock
        for old in instance.produits.all():
            old.produit.stock_actuelle -= old.quantite
            old.produit.save()
        instance.produits.all().delete()
        instance.fournisseur = validated_data.get('fournisseur', instance.fournisseur)
        instance.montant_paye = validated_data.get('montant_paye', instance.montant_paye)
        instance.save()
        for p in produits_data:
            ProduitAchat.objects.create(entree=instance, **p)
            produit = p['produit']
            produit.stock_actuelle += p['quantite']
            produit.check_alerte_stock()
        return instance


class ProduitVenteSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)

    class Meta:
        model = ProduitVente
        fields = ['id', 'produit', 'produit_nom', 'quantite', 'prix_unitaire', 'total']
        read_only_fields = ['total']


class VenteSerializer(serializers.ModelSerializer):
    produits = ProduitVenteSerializer(many=True)
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    montant_paye = serializers.SerializerMethodField()
    reste = serializers.SerializerMethodField()

    class Meta:
        model = Vente
        fields = ['id', 'client', 'client_nom', 'date', 'produits', 'total', 'montant_paye', 'reste']
        read_only_fields = ['date', 'total']

    def get_montant_paye(self, obj):
        return float(sum(p.montant for p in obj.paiements.all()))

    def get_reste(self, obj):
        return max(float(obj.total) - self.get_montant_paye(obj), 0)

    def create(self, validated_data):
        produits_data = validated_data.pop('produits')
        boutique = self.context['boutique']
        vente = Vente.objects.create(boutique=boutique, **validated_data)
        total_general = 0
        for prod in produits_data:
            produit = prod['produit']
            quantite = prod['quantite']
            prix = prod['prix_unitaire']
            if produit.stock_actuelle < quantite:
                vente.delete()
                raise serializers.ValidationError(
                    f"Stock insuffisant pour {produit.nom} (dispo: {produit.stock_actuelle})"
                )
            total = quantite * prix
            ProduitVente.objects.create(vente=vente, produit=produit, quantite=quantite, prix_unitaire=prix, total=total)
            produit.stock_actuelle -= quantite
            produit.save()
            total_general += total
        vente.total = total_general
        vente.reste = total_general
        vente.save()
        return vente


class PaiementSerializer(serializers.ModelSerializer):
    client_nom = serializers.SerializerMethodField()
    vente_total = serializers.SerializerMethodField()

    class Meta:
        model = Paiement
        fields = ['id', 'vente', 'client_nom', 'vente_total', 'montant', 'methode', 'date', 'boutique']
        read_only_fields = ['boutique', 'date']

    def get_client_nom(self, obj):
        return obj.vente.client.nom if obj.vente.client else "Anonyme"

    def get_vente_total(self, obj):
        return float(obj.vente.total)


class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = ['id', 'description', 'montant', 'date', 'boutique']
        read_only_fields = ['boutique', 'date']
