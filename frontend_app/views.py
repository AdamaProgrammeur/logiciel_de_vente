from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
import json


def accueil_view(request):
    return render(request, 'frontend_app/accueil.html')


def non_approuvee_view(request):
    return render(request, 'frontend_app/non_approuvee.html')


def _check_approuvee(user):
    """Retourne True si la boutique de l'utilisateur est approuvée."""
    return user.is_staff or (user.boutique and user.boutique.statut == 'approuvee')


def boutique_approuvee_required(view_func):
    """Décorateur : redirige vers non_approuvee si boutique non approuvée."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not _check_approuvee(request.user):
            return redirect('non_approuvee')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@boutique_approuvee_required
def dashboard_page(request):
    if request.user.role != 'admin' and not request.user.is_staff:
        return redirect('ventes')
    return render(request, 'frontend_app/dashboard.html')

@boutique_approuvee_required
def categories_view(request):
    return render(request, 'frontend_app/categories.html')

@boutique_approuvee_required
def produits_view(request):
    return render(request, 'frontend_app/produits.html')

@boutique_approuvee_required
def clients_view(request):
    return render(request, 'frontend_app/clients.html')

@boutique_approuvee_required
def fournisseurs_view(request):
    return render(request, 'frontend_app/fournisseurs.html')

@boutique_approuvee_required
def entrees_view(request):
    return render(request, 'frontend_app/achats.html')

@boutique_approuvee_required
def ventes_view(request):
    return render(request, 'frontend_app/ventes.html')

@boutique_approuvee_required
def paiements_view(request):
    return render(request, 'frontend_app/paiements.html')

@boutique_approuvee_required
def depenses_view(request):
    return render(request, 'frontend_app/depenses.html')

@boutique_approuvee_required
def parametres_view(request):
    return render(request, 'frontend_app/parametres.html')

@boutique_approuvee_required
def utilisateurs_view(request):
    return render(request, 'frontend_app/utilisateurs.html')


def login_view(request):
    return render(request, 'frontend_app/login.html')

def register_view(request):
    return render(request, 'frontend_app/register.html')

@login_required
def logout_view(request):
    django_logout(request)
    response = redirect('login')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


def api_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = authenticate(request, username=data.get('username'), password=data.get('password'))
        if user is not None:
            if not _check_approuvee(user):
                # On pose quand même les tokens pour que la page non_approuvee fonctionne
                refresh = RefreshToken.for_user(user)
                response = JsonResponse({"success": False, "non_approuvee": True,
                    "error": "Votre boutique n'a pas encore été approuvée par StockPro."})
                response.set_cookie('access_token', str(refresh.access_token),
                    httponly=True, samesite='Lax', secure=False)
                response.set_cookie('refresh_token', str(refresh),
                    httponly=True, samesite='Lax', secure=False)
                return response
            refresh = RefreshToken.for_user(user)
            if user.role == 'admin' or user.is_staff:
                redirect_url = '/dashboard/'
            else:
                redirect_url = '/ventes/'
            response = JsonResponse({"success": True, "redirect_url": redirect_url})
            response.set_cookie('access_token', str(refresh.access_token),
                httponly=True, samesite='Lax', secure=False)
            response.set_cookie('refresh_token', str(refresh),
                httponly=True, samesite='Lax', secure=False)
            return response
        return JsonResponse({"success": False, "error": "Nom d'utilisateur ou mot de passe incorrect."})
    return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)


def api_register(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)
    from stock.models import Boutique, User
    data = json.loads(request.body)

    username     = data.get('username', '').strip()
    email        = data.get('email', '').strip()
    password1    = data.get('password1', '')
    boutique_nom = data.get('boutique_nom', '').strip()

    if not username or not email or not password1 or not boutique_nom:
        return JsonResponse({"error": "Tous les champs obligatoires doivent être remplis."}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Ce nom d'utilisateur est déjà pris."}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Cet email est déjà utilisé."}, status=400)

    boutique = Boutique.objects.create(
        nom=boutique_nom,
        telephone=data.get('boutique_telephone', ''),
        email=data.get('boutique_email', ''),
        adresse=data.get('boutique_adresse', ''),
        statut='en_attente',
    )

    user = User.objects.create(
        username=username,
        email=email,
        boutique=boutique,
        role='admin',
        is_staff=False,
    )
    user.set_password(password1)
    user.save()

    # On connecte avec JWT (cookie posé)
    refresh = RefreshToken.for_user(user)
    response = JsonResponse({"success": True, "redirect_url": "/non-approuvee/"})
    response.set_cookie('access_token', str(refresh.access_token),
        httponly=True, samesite='Lax', secure=False)
    response.set_cookie('refresh_token', str(refresh),
        httponly=True, samesite='Lax', secure=False)
    return response
