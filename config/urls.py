"""
URL Configuration for Gestion Pedidos Project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # ¡AÑADE ESTA LÍNEA!
    path('', include('apps.core.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('pedidos/', include('apps.pedidos.urls')),
    path('produccion/', include('apps.produccion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)