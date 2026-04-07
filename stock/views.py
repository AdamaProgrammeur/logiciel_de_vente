from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json

from .models import (
    Boutique, ProduitAchat, ProduitVente, User, Produit, Categorie,
    EntreeStock, Vente, Paiement, Client, Fournisseur, Depense
)
from .serializers import (
    BoutiqueSerializer, ProduitAchatSerializer, UserSerializer, ProduitSerializer,
    CategorieSerializer, EntreeStockSerializer, VenteSerializer, PaiementSerializer,
    ClientSerializer, FournisseurSerializer, DepenseSerializer
)


class BoutiqueViewSet(viewsets.ModelViewSet):
    serializer_class = BoutiqueSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Boutique.objects.filter(id=self.request.user.boutique.id)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return User.objects.filter(boutique=self.request.user.boutique)
    def perform_create(self, serializer):
        serializer.save(boutique=self.request.user.boutique)


class ProduitViewSet(viewsets.ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Produit.objects.filter(boutique=self.request.user.boutique)
    def perform_create(self, serializer):
        serializer.save(boutique=self.request.user.boutique)


class CategorieViewSet(viewsets.ModelViewSet):
    serializer_class = CategorieSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Categorie.objects.filter(boutique=self.request.user.boutique)
    def perform_create(self, serializer):
        serializer.save()
    def perform_update(self, serializer):
        serializer.save()


class EntreeStockViewSet(viewsets.ModelViewSet):
    serializer_class = EntreeStockSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return EntreeStock.objects.filter(
            boutique=self.request.user.boutique
        ).prefetch_related('produits__produit', 'fournisseur').order_by('-date')
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(boutique=self.request.user.boutique)
    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save()


class VenteViewSet(viewsets.ModelViewSet):
    serializer_class = VenteSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Vente.objects.filter(
            boutique=self.request.user.boutique
        ).prefetch_related('produits__produit', 'paiements').order_by('-date')
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['boutique'] = self.request.user.boutique
        return context
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Client.objects.filter(boutique=self.request.user.boutique)
    def perform_create(self, serializer):
        serializer.save(boutique=self.request.user.boutique)


class FournisseurViewSet(viewsets.ModelViewSet):
    serializer_class = FournisseurSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Fournisseur.objects.filter(boutique=self.request.user.boutique)
    def perform_create(self, serializer):
        serializer.save(boutique=self.request.user.boutique)


class PaiementViewSet(viewsets.ModelViewSet):
    serializer_class = PaiementSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Paiement.objects.filter(
            boutique=self.request.user.boutique
        ).select_related('vente__client').order_by('-date')
    def perform_create(self, serializer):
        serializer.save(boutique=self.request.user.boutique)


class DepenseViewSet(viewsets.ModelViewSet):
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Depense.objects.filter(boutique=self.request.user.boutique).order_by('-date')
    def perform_create(self, serializer):
        serializer.save(boutique=self.request.user.boutique)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        boutique = request.user.boutique

        # 1. Cartes
        stock_total = Produit.objects.filter(boutique=boutique).aggregate(
            t=Sum('stock_actuelle'))['t'] or 0

        nb_ventes = Vente.objects.filter(boutique=boutique).count()

        total_paiements = float(Paiement.objects.filter(boutique=boutique).aggregate(
            t=Sum('montant'))['t'] or 0)

        total_depenses = float(Depense.objects.filter(boutique=boutique).aggregate(
            t=Sum('montant'))['t'] or 0)

        # reste = somme des restes de toutes les ventes
        reste_total = float(Vente.objects.filter(boutique=boutique).aggregate(
            t=Sum('reste'))['t'] or 0)

        # 2. Stock par produit
        stock_par_produit = [
            {
                "nom": p.nom,
                "stock": p.stock_actuelle,
                "alerte": p.alerte_stock
            }
            for p in Produit.objects.filter(boutique=boutique).order_by('nom')
        ]

        # 3. Historique paiements par jour
        historique = list(
            Paiement.objects.filter(boutique=boutique)
            .annotate(jour=TruncDate('date'))
            .values('jour')
            .annotate(total=Sum('montant'))
            .order_by('jour')
        )
        historique_data = [
            {
                "date": h['jour'].strftime("%d/%m/%Y"),
                "total": float(h['total'])
            }
            for h in historique
        ]

        # 4. Toutes les ventes avec produits
        ventes_data = []
        for v in Vente.objects.filter(boutique=boutique).prefetch_related(
            'produits__produit', 'paiements', 'client'
        ).order_by('-date'):
            montant_paye = float(sum(p.montant for p in v.paiements.all()))
            reste = max(float(v.total) - montant_paye, 0)

            if reste <= 0:
                statut = "OK"
            elif montant_paye > 0:
                statut = "Partiel"
            else:
                statut = "En attente"

            produits_noms = ", ".join(
                f"{pv.produit.nom} x{pv.quantite}" for pv in v.produits.all()
            )

            ventes_data.append({
                "id": v.id,
                "client": v.client.nom if v.client else "Anonyme",
                "produits": produits_noms,
                "total": float(v.total),
                "paye": montant_paye,
                "reste": reste,
                "statut": statut,
                "date": v.date.strftime("%d/%m/%Y %H:%M"),
            })

        return Response({
            "stock_total": stock_total,
            "nb_ventes": nb_ventes,
            "total_paiements": total_paiements,
            "total_depenses": total_depenses,
            "reste_total": reste_total,
            "stock_par_produit": stock_par_produit,
            "historique_paiements": historique_data,
            "ventes": ventes_data,
        })


class AlertesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        boutique = request.user.boutique
        produits = Produit.objects.filter(boutique=boutique, alerte_stock=True).select_related('categorie')
        data = [{
            'id': p.id,
            'nom': p.nom,
            'stock_actuelle': p.stock_actuelle,
            'seuil_alerte': p.seuil_alerte,
            'prix': float(p.prix),
            'categorie': p.categorie.nom if p.categorie else None,
            'statut': 'rupture' if p.stock_actuelle <= 0 else 'faible',
        } for p in produits]
        return Response({'count': len(data), 'produits': data})


class RapportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        boutique = request.user.boutique
        date_debut = request.query_params.get('debut')
        date_fin = request.query_params.get('fin')

        ventes_qs = Vente.objects.filter(boutique=boutique)
        paiements_qs = Paiement.objects.filter(boutique=boutique)
        depenses_qs = Depense.objects.filter(boutique=boutique)
        entrees_qs = EntreeStock.objects.filter(boutique=boutique).prefetch_related('produits')

        if date_debut:
            ventes_qs = ventes_qs.filter(date__date__gte=date_debut)
            paiements_qs = paiements_qs.filter(date__date__gte=date_debut)
            depenses_qs = depenses_qs.filter(date__date__gte=date_debut)
            entrees_qs = entrees_qs.filter(date__date__gte=date_debut)
        if date_fin:
            ventes_qs = ventes_qs.filter(date__date__lte=date_fin)
            paiements_qs = paiements_qs.filter(date__date__lte=date_fin)
            depenses_qs = depenses_qs.filter(date__date__lte=date_fin)
            entrees_qs = entrees_qs.filter(date__date__lte=date_fin)

        total_ventes = float(ventes_qs.aggregate(t=Sum('total'))['t'] or 0)
        total_encaisse = float(paiements_qs.aggregate(t=Sum('montant'))['t'] or 0)
        total_depenses = float(depenses_qs.aggregate(t=Sum('montant'))['t'] or 0)
        total_achats = float(sum(
            sum(p.quantite * p.prix_unitaire for p in e.produits.all())
            for e in entrees_qs
        ))
        benefice = total_encaisse - total_achats - total_depenses

        return Response({
            'total_ventes': total_ventes,
            'total_encaisse': total_encaisse,
            'total_achats': total_achats,
            'total_depenses': total_depenses,
            'benefice': benefice,
            'nb_ventes': ventes_qs.count(),
            'nb_achats': entrees_qs.count(),
        })


class TracesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        boutique = request.user.boutique
        traces = []

        for v in Vente.objects.filter(boutique=boutique).prefetch_related('produits__produit', 'client').order_by('-date'):
            traces.append({
                'type': 'vente',
                'icone': 'bag-check',
                'couleur': '#16a34a',
                'description': f"Vente #{v.id} — {v.client.nom if v.client else 'Anonyme'}",
                'montant': float(v.total),
                'date': v.date.strftime('%d/%m/%Y %H:%M'),
                'detail': ', '.join(f"{pv.produit.nom} x{pv.quantite}" for pv in v.produits.all()),
            })

        for e in EntreeStock.objects.filter(boutique=boutique).prefetch_related('produits__produit', 'fournisseur').order_by('-date'):
            total = float(sum(p.quantite * p.prix_unitaire for p in e.produits.all()))
            traces.append({
                'type': 'achat',
                'icone': 'cart-plus',
                'couleur': '#2563eb',
                'description': f"Achat #{e.id} — {e.fournisseur.nom if e.fournisseur else 'Sans fournisseur'}",
                'montant': total,
                'date': e.date.strftime('%d/%m/%Y %H:%M'),
                'detail': ', '.join(f"{p.produit.nom} x{p.quantite}" for p in e.produits.all()),
            })

        for p in Paiement.objects.filter(boutique=boutique).select_related('vente__client').order_by('-date'):
            traces.append({
                'type': 'paiement',
                'icone': 'wallet2',
                'couleur': '#7c3aed',
                'description': f"Paiement — {p.vente.client.nom if p.vente.client else 'Anonyme'} ({p.methode})",
                'montant': float(p.montant),
                'date': p.date.strftime('%d/%m/%Y %H:%M'),
                'detail': f"Vente #{p.vente.id}",
            })

        for d in Depense.objects.filter(boutique=boutique).order_by('-date'):
            traces.append({
                'type': 'depense',
                'icone': 'cash-stack',
                'couleur': '#dc2626',
                'description': f"Dépense — {d.description}",
                'montant': float(d.montant),
                'date': d.date.strftime('%d/%m/%Y %H:%M'),
                'detail': '',
            })

        traces.sort(key=lambda x: x['date'], reverse=True)
        return Response(traces)


@login_required
@csrf_exempt
def change_password(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Méthode non autorisée"}, status=405)
    data = json.loads(request.body)
    user = request.user
    if not user.check_password(data.get('old_password', '')):
        return JsonResponse({"detail": "Ancien mot de passe incorrect"}, status=400)
    p1, p2 = data.get('new_password1', ''), data.get('new_password2', '')
    if p1 != p2:
        return JsonResponse({"detail": "Les mots de passe ne correspondent pas"}, status=400)
    user.set_password(p1)
    user.save()
    update_session_auth_hash(request, user)
    return JsonResponse({"detail": "Mot de passe changé avec succès"})
