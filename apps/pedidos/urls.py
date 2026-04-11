"""
URLs de la aplicación pedidos
"""
from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('', views.lista_pedidos, name='lista'),
    path('nuevo/', views.crear_pedido, name='crear'),
    path('<int:pk>/', views.detalle_pedido, name='detalle'),
    path('<int:pk>/editar/', views.editar_pedido, name='editar'),
    path('<int:pk>/items/', views.agregar_items_pedido, name='agregar_items'),
    path('<int:pedido_pk>/items/<int:item_pk>/eliminar/', views.eliminar_item_pedido, name='eliminar_item'),
    path('<int:pedido_pk>/conjuntos/<int:conjunto_pk>/eliminar/', views.eliminar_conjunto_pedido, name='eliminar_conjunto'),
    path('<int:pk>/importar/', views.importar_excel, name='importar_excel'),
    path('<int:pk>/resumen-produccion/', views.resumen_pedido_produccion, name='resumen_produccion'),
]