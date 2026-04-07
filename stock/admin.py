from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Boutique, User, Produit, EntreeStock, ProduitAchat,
    Vente, ProduitVente, Paiement, Categorie, Fournisseur, Client
)


# -------------------------------
# Admin Produit
# -------------------------------
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'stock_actuelle', 'alerte_stock', 'prix', 'seuil_alerte', 'boutique')
    list_filter = ('boutique', 'categorie', 'alerte_stock')
    search_fields = ('nom',)
    readonly_fields = ('alerte_stock', 'stock_actuelle')


# -------------------------------
# Admin User
# -------------------------------
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Boutique', {'fields': ('boutique',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Boutique', {'fields': ('boutique',)}),
    )


# -------------------------------
# Admin Categorie
# -------------------------------
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'boutique')
    search_fields = ('nom',)


# -------------------------------
# Admin EntreeStock et ProduitAchat
# -------------------------------
class ProduitAchatInline(admin.TabularInline):
    model = ProduitAchat
    extra = 1
    readonly_fields = ('produit', 'quantite', 'prix_unitaire')


class EntreeStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'boutique', 'fournisseur', 'date')
    inlines = [ProduitAchatInline]


# -------------------------------
# Admin ProduitAchat directement si besoin
# -------------------------------
class ProduitAchatAdmin(admin.ModelAdmin):
    list_display = ('produit', 'entree', 'quantite', 'prix_unitaire')
    list_filter = ('entree__boutique',)
    search_fields = ('produit__nom',)


# -------------------------------
# Admin Vente et ProduitVente
# -------------------------------
class ProduitVenteInline(admin.TabularInline):
    model = ProduitVente
    extra = 1
    readonly_fields = ('produit', 'quantite', 'prix_unitaire')


from django.contrib import admin
from .models import Vente, ProduitVente

# -------------------------------
"""# Admin Vente
# -------------------------------
class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_boutique', 'get_client', 'total', 'reste', 'date')
    list_filter = ('boutique', 'date')  # fonctionne si boutique est un ForeignKey
    search_fields = ('client__nom', 'boutique__nom')

    # Méthodes pour list_display
    def get_boutique(self, obj):
        return obj.boutique.nom if obj.boutique else '-'
    get_boutique.short_description = 'Boutique'
    get_boutique.admin_order_field = 'boutique__nom'

    def get_client(self, obj):
        return obj.client.nom if obj.client else '-'
    get_client.short_description = 'Client'
    get_client.admin_order_field = 'client__nom'


# -------------------------------
# Admin ProduitVente
# -------------------------------
class ProduitVenteAdmin(admin.ModelAdmin):
    list_display = ('produit', 'vente', 'quantite', 'prix_unitaire', 'get_boutique')
    list_filter = ('produit', 'vente__boutique')  # filtre sur ForeignKey valide
    search_fields = ('produit__nom', 'vente__client__nom')

    def get_boutique(self, obj):
        return obj.vente.boutique.nom if obj.vente and obj.vente.boutique else '-'
    get_boutique.short_description = 'Boutique'
    get_boutique.admin_order_field = 'vente__boutique__nom'
"""

# -------------------------------
# Enregistrement dans l’admin
# -------------------------------
# Admin Paiement
# -------------------------------
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('id', 'vente', 'boutique', 'montant', 'methode', 'date')
    list_filter = ('boutique', 'methode')
    search_fields = ('vente__id',)


# -------------------------------
# Admin Fournisseur et Client
# -------------------------------
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'boutique', 'telephone', 'adresse')
    search_fields = ('nom',)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'boutique', 'telephone', 'adresse')
    search_fields = ('nom',)


# -------------------------------
# Register Models
# -------------------------------

class BoutiqueAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email', 'statut', 'date_creation')
    list_filter = ('statut',)
    search_fields = ('nom',)
    list_editable = ('statut',)
    actions = ['approuver_boutiques', 'mettre_en_attente']

    def approuver_boutiques(self, request, queryset):
        queryset.update(statut='approuvee')
        self.message_user(request, f"{queryset.count()} boutique(s) approuvée(s).")
    approuver_boutiques.short_description = "✅ Approuver les boutiques sélectionnées"

    def mettre_en_attente(self, request, queryset):
        queryset.update(statut='en_attente')
        self.message_user(request, f"{queryset.count()} boutique(s) mises en attente.")
    mettre_en_attente.short_description = "⏳ Mettre en attente les boutiques sélectionnées"


admin.site.register(User, CustomUserAdmin)
admin.site.register(Boutique, BoutiqueAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(EntreeStock, EntreeStockAdmin)
admin.site.register(ProduitAchat, ProduitAchatAdmin)   # <-- ajouté
#admin.site.register(Vente, VenteAdmin)
#admin.site.register(ProduitVente, ProduitVenteAdmin)   # <-- ajouté
admin.site.register(Paiement, PaiementAdmin)
admin.site.register(Fournisseur, FournisseurAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Vente)
admin.site.register(ProduitVente)