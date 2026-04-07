from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil_view, name='accueil'),
    path('non-approuvee/', views.non_approuvee_view, name='non_approuvee'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('api/register/', views.api_register, name='api_register'),
    path('logout/', views.logout_view, name='logout'),
    path('api/login/', views.api_login, name='api_login'),
    path('dashboard/', views.dashboard_page, name='dashboard_page'),
    path('produits/', views.produits_view, name='produits'),
    path('achats/', views.entrees_view, name='achats'),
    path('clients/', views.clients_view, name='clients'),
    path('fournisseurs/', views.fournisseurs_view, name='fournisseurs'),
    path('ventes/', views.ventes_view, name='ventes'),
    path('paiements/', views.paiements_view, name='paiements'),
    path('categories/', views.categories_view, name='categories'),
    path('depenses/', views.depenses_view, name='depenses'),
    path('alertes/', views.alertes_view, name='alertes'),
    path('rapports/', views.rapports_view, name='rapports'),
    path('parametres/', views.parametres_view, name='parametres'),
    path('utilisateurs/', views.utilisateurs_view, name='utilisateurs'),
]
