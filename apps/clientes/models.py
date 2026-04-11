"""
Modelos para la gestión de clientes (colegios)
"""
from django.db import models
from django.core.validators import RegexValidator
from apps.core.models import TimeStampedModel


class Cliente(TimeStampedModel):
    """
    Representa un cliente del sistema (generalmente un colegio o institución educativa).
    """
    TIPO_CLIENTE_CHOICES = [
        ('colegio', 'Colegio'),
        ('instituto', 'Instituto'),
        ('universidad', 'Universidad'),
        ('empresa', 'Empresa'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Cliente',
        help_text='Nombre completo del colegio o institución'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CLIENTE_CHOICES,
        default='colegio',
        verbose_name='Tipo de Cliente'
    )
    
    # Información de contacto
    contacto_nombre = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Nombre del Contacto'
    )
    contacto_cargo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Cargo del Contacto'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^[\d\s\-\+\(\)]+$', 'Ingrese un número de teléfono válido')],
        verbose_name='Teléfono'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='Correo Electrónico'
    )
    
    # Dirección
    direccion = models.TextField(
        blank=True,
        verbose_name='Dirección'
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ciudad'
    )
    
    # Información adicional
    nit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='NIT/CI',
        help_text='Número de identificación tributaria'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas Adicionales'
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return self.nombre

    def get_pedidos_count(self):
        """Retorna el número total de pedidos del cliente"""
        return self.pedidos.count()

    def get_pedidos_activos_count(self):
        """Retorna el número de pedidos activos del cliente"""
        return self.pedidos.filter(estado__in=['pendiente', 'en_proceso']).count()