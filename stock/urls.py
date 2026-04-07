from rest_framework import routers
from django.urls import path, include
from .views import (
    BoutiqueViewSet, CategorieViewSet, DashboardView, UserViewSet, ProduitViewSet,
    EntreeStockViewSet, VenteViewSet, PaiementViewSet, ClientViewSet,
    FournisseurViewSet, DepenseViewSet, change_password, RapportView, TracesView, AlertesView
)

router = routers.DefaultRouter()
router.register(r'boutiques', BoutiqueViewSet, basename='boutique')
router.register(r'utilisateurs', UserViewSet, basename='user')
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'entrees', EntreeStockViewSet, basename='entree')
router.register(r'ventes', VenteViewSet, basename='ventes')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'fournisseurs', FournisseurViewSet, basename='fournisseur')
router.register(r'paiements', PaiementViewSet, basename='paiement')
router.register(r'depenses', DepenseViewSet, basename='depense')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/dashboard/', DashboardView.as_view(), name='api_dashboard'),
    path('api/change-password/', change_password, name='change_password'),
    path('api/rapport/', RapportView.as_view(), name='api_rapport'),
    path('api/traces/', TracesView.as_view(), name='api_traces'),
    path('api/alertes/', AlertesView.as_view(), name='api_alertes'),
]
