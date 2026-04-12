from django.contrib import admin
from .models import PedidoPersonalizado, ItemPedidoPersonalizado

class ItemPedidoPersonalizadoInline(admin.TabularInline):
    model = ItemPedidoPersonalizado
    extra = 0

@admin.register(PedidoPersonalizado)
class PedidoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'cliente', 'gestion', 'categoria', 'tipo_pedido', 'estado_pedido', 'saldo')
    list_filter = ('gestion', 'tipo_pedido', 'estado_pedido', 'estado_pago', 'cliente')
    search_fields = ('nombre_completo', 'categoria')
    inlines = [ItemPedidoPersonalizadoInline]

@admin.register(ItemPedidoPersonalizado)
class ItemPedidoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'tipo_prenda', 'genero', 'talla', 'cantidad')
    list_filter = ('tipo_prenda', 'genero', 'talla')
