"""
Configuración del panel de administración para Pedidos
"""
from django.contrib import admin
from .models import Pedido, ItemPedido, ConjuntoPedido, ImportacionExcel


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    fields = ['tipo_prenda', 'genero', 'talla', 'cantidad', 'es_parte_de_conjunto']
    readonly_fields = ['es_parte_de_conjunto']


class ConjuntoPedidoInline(admin.TabularInline):
    model = ConjuntoPedido
    extra = 0
    fields = ['genero', 'talla', 'cantidad']


class ImportacionExcelInline(admin.TabularInline):
    model = ImportacionExcel
    extra = 0
    readonly_fields = ['archivo', 'estado', 'filas_procesadas', 'filas_con_error', 'procesado_en']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo',
        'cliente',
        'gestion',
        'tipo_pedido',
        'estado',
        'get_total_prendas',
        'fecha_entrega',
        'creado_en'
    ]
    list_filter = ['estado', 'tipo_pedido', 'gestion', 'creado_en']
    search_fields = ['codigo', 'cliente__nombre', 'notas']
    date_hierarchy = 'creado_en'
    inlines = [ConjuntoPedidoInline, ItemPedidoInline, ImportacionExcelInline]
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('codigo', 'cliente', 'gestion')
        }),
        ('Detalles', {
            'fields': ('tipo_pedido', 'estado', 'fecha_entrega')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
    )

    def get_total_prendas(self, obj):
        return obj.get_total_prendas()
    get_total_prendas.short_description = 'Total Prendas'


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = [
        'pedido',
        'tipo_prenda',
        'genero',
        'talla',
        'cantidad',
        'es_parte_de_conjunto'
    ]
    list_filter = ['tipo_prenda', 'genero', 'talla', 'es_parte_de_conjunto']
    search_fields = ['pedido__codigo', 'notas']


@admin.register(ConjuntoPedido)
class ConjuntoPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'genero', 'talla', 'cantidad', 'creado_en']
    list_filter = ['genero', 'talla']
    search_fields = ['pedido__codigo', 'notas']


@admin.register(ImportacionExcel)
class ImportacionExcelAdmin(admin.ModelAdmin):
    list_display = [
        'pedido',
        'archivo',
        'estado',
        'filas_procesadas',
        'filas_con_error',
        'creado_en'
    ]
    list_filter = ['estado', 'creado_en']
    readonly_fields = ['filas_procesadas', 'filas_con_error', 'errores_detalle', 'procesado_en']