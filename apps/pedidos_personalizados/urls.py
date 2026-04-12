from django.urls import path
from . import views

app_name = 'pedidos_personalizados'

urlpatterns = [
    path('dashboard/', views.dashboard_personalizados, name='dashboard'),
    path('lista/', views.lista_pedidos, name='lista'),
    path('crear/', views.crear_pedido, name='crear'),
    path('<int:pk>/editar/', views.editar_pedido, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_pedido, name='eliminar'),
    path('<int:pedido_pk>/items/agregar/', views.agregar_item, name='agregar_item'),
    path('items/<int:item_pk>/eliminar/', views.eliminar_item, name='eliminar_item'),
    path('importar/', views.importar_excel, name='importar'),
    path('exportar/', views.exportar_excel, name='exportar'),
    path('exportar/word/', views.exportar_word, name='exportar_word'),
    path('exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
]
