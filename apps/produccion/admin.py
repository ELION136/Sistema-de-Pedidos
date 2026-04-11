"""
Configuración del panel de administración para Producción
"""
from django.contrib import admin
from .models import OrdenProduccion, ResumenProduccion, MateriaPrimaRequerida


class ResumenProduccionInline(admin.TabularInline):
    model = ResumenProduccion
    extra = 0
    fields = ['tipo_prenda', 'genero', 'talla', 'cantidad_total']
    readonly_fields = ['tipo_prenda', 'genero', 'talla', 'cantidad_total']
    can_delete = False


class MateriaPrimaRequeridaInline(admin.TabularInline):
    model = MateriaPrimaRequerida
    extra = 1
    fields = ['tipo_material', 'descripcion', 'cantidad_requerida', 'unidad_medida', 'cantidad_comprada']


@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display = [
        'codigo',
        'gestion',
        'estado',
        'get_total_prendas',
        'fecha_inicio',
        'fecha_fin_estimada'
    ]
    list_filter = ['estado', 'gestion', 'fecha_inicio']
    search_fields = ['codigo', 'notas']
    date_hierarchy = 'fecha_inicio'
    filter_horizontal = ['pedidos']
    inlines = [ResumenProduccionInline, MateriaPrimaRequeridaInline]

    def get_total_prendas(self, obj):
        return obj.get_total_prendas()
    get_total_prendas.short_description = 'Total Prendas'


@admin.register(ResumenProduccion)
class ResumenProduccionAdmin(admin.ModelAdmin):
    list_display = ['orden_produccion', 'tipo_prenda', 'genero', 'talla', 'cantidad_total']
    list_filter = ['tipo_prenda', 'genero', 'talla']
    search_fields = ['orden_produccion__codigo']


@admin.register(MateriaPrimaRequerida)
class MateriaPrimaRequeridaAdmin(admin.ModelAdmin):
    list_display = [
        'orden_produccion',
        'tipo_material',
        'descripcion',
        'cantidad_requerida',
        'unidad_medida',
        'cantidad_comprada',
        'esta_completo'
    ]
    list_filter = ['tipo_material']
    search_fields = ['descripcion', 'orden_produccion__codigo']