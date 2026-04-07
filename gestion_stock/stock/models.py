from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class Boutique(models.Model):
    nom = models.CharField(max_length=255)
    slogan = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    couleur_principale = models.CharField(max_length=7, default='#0d6efd')
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    STATUT_CHOICES = [('approuvee', 'Approuvée'), ('en_attente', 'En attente')]
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return self.nom


class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('employe', 'Employé')]
    email = models.EmailField(unique=True)
    boutique = models.ForeignKey(
        Boutique, on_delete=models.CASCADE,
        null=True, blank=True, related_name='users'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employe')

    def __str__(self):
        return self.username

    @property
    def is_admin_boutique(self):
        return self.role == 'admin'


class Categorie(models.Model):
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True)
    nom = models.CharField(max_length=255)
    stock_actuelle = models.IntegerField(default=0)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    seuil_alerte = models.IntegerField(default=0)
    alerte_stock = models.BooleanField(default=False)

    def check_alerte_stock(self):
        self.alerte_stock = self.stock_actuelle <= self.seuil_alerte
        self.save(update_fields=['alerte_stock', 'stock_actuelle'])

    def __str__(self):
        return self.nom


class Fournisseur(models.Model):
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nom


class Client(models.Model):
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nom


class EntreeStock(models.Model):
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total(self):
        return sum(p.quantite * p.prix_unitaire for p in self.produits.all())

    @property
    def reste(self):
        return self.total - self.montant_paye

    @property
    def est_paye(self):
        return self.reste <= 0

    def __str__(self):
        return f"Achat #{self.id} - {self.date.date()}"


class ProduitAchat(models.Model):
    entree = models.ForeignKey(EntreeStock, on_delete=models.CASCADE, related_name='produits')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.quantite <= 0:
            raise ValidationError("La quantité doit être supérieure à zéro.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Vente(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reste = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vente #{self.id}"


class ProduitVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='produits')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=0)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)


class Paiement(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)

    def clean(self):
        total = float(self.vente.total)
        paiements = self.vente.paiements.all()
        if self.pk:
            paiements = paiements.exclude(pk=self.pk)
        total_paye = float(sum(p.montant for p in paiements))
        reste = total - total_paye
        if float(self.montant) <= 0:
            raise ValidationError("Le montant doit être supérieur à 0")
        if float(self.montant) > reste + 0.01:
            raise ValidationError(f"Le paiement ({self.montant}) dépasse le reste à payer ({reste:.2f})")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Mettre à jour montant_paye et reste sur la vente
        total_paye = float(sum(p.montant for p in self.vente.paiements.all()))
        self.vente.montant_paye = total_paye
        self.vente.reste = max(float(self.vente.total) - total_paye, 0)
        self.vente.save(update_fields=['montant_paye', 'reste'])


class Depense(models.Model):
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.montant}"
