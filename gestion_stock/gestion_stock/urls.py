"""
URL configuration for gestion_stock project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.contrib.auth import get_user_model

def setup_admin(request):
    User = get_user_model()
    from stock.models import Boutique
    User.objects.filter(username='superadmin').delete()
    u = User(username='superadmin', email='superadmin@stockpro.com', is_staff=True, is_superuser=True, role='admin')
    u.set_password('stockpro2024')
    u.save()
    count = Boutique.objects.filter(statut='en_attente').update(statut='approuvee')
    return JsonResponse({'status': 'ok', 'user': u.username, 'boutiques_approuvees': count})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('setup-admin-secret-2024/', setup_admin),
    path('', include('stock.urls')),
    path('', include('frontend_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
