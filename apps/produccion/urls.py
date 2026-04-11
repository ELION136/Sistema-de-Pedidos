"""
URLs de la aplicación produccion
"""
from django.urls import path
from . import views

app_name = 'produccion'

urlpatterns = [
    path('', views.dashboard_produccion, name='dashboard'),
    path('ordenes/', views.lista_ordenes, name='lista_ordenes'),
    path('ordenes/nueva/', views.crear_orden, name='crear_orden'),
    path('ordenes/<int:pk>/', views.detalle_orden, name='detalle_orden'),
    path('ordenes/<int:pk>/editar/', views.editar_orden, name='editar_orden'),
    path('ordenes/<int:orden_pk>/resumen/', views.resumen_clasificacion, name='resumen_clasificacion'),
    path('ordenes/<int:orden_pk>/materia-prima/', views.reporte_materia_prima, name='reporte_materia_prima'),
    path('ordenes/<int:orden_pk>/materia-prima/agregar/', views.agregar_materia_prima, name='agregar_materia_prima'),
    path('materia-prima/<int:pk>/editar/', views.editar_materia_prima, name='editar_materia_prima'),
    path('ordenes/<int:pk>/cambiar-estado/', views.cambiar_estado_orden, name='cambiar_estado'),
]