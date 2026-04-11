"""
Configuración del panel de administración para Clientes
"""
from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'tipo',
        'contacto_nombre',
        'telefono',
        'ciudad',
        'activo',
        'creado_en'
    ]
    list_filter = ['tipo', 'activo', 'ciudad', 'creado_en']
    search_fields = ['nombre', 'contacto_nombre', 'telefono', 'email', 'nit']
    date_hierarchy = 'creado_en'
    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'tipo', 'nit')
        }),
        ('Contacto', {
            'fields': ('contacto_nombre', 'contacto_cargo', 'telefono', 'email')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )