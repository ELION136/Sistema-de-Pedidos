"""
Modelos para el módulo de producción y planificación
"""
from django.db import models
from django.db.models import Sum
from apps.core.models import TimeStampedModel


class OrdenProduccion(TimeStampedModel):
    """
    Representa una orden de producción generada a partir de pedidos.
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_corte', 'En Corte'),
        ('en_confeccion', 'En Confección'),
        ('en_acabados', 'En Acabados'),
        ('completada', 'Completada'),
    ]

    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código de Orden'
    )
    pedidos = models.ManyToManyField(
        'pedidos.Pedido',
        related_name='ordenes_produccion',
        verbose_name='Pedidos Incluidos'
    )
    gestion = models.PositiveIntegerField(
        verbose_name='Gestión/Año'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    fecha_fin_estimada = models.DateField(
        verbose_name='Fecha de Fin Estimada'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas de Producción'
    )

    class Meta:
        verbose_name = 'Orden de Producción'
        verbose_name_plural = 'Órdenes de Producción'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.codigo} - {self.get_estado_display()}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self.generar_codigo()
        super().save(*args, **kwargs)

    def generar_codigo(self):
        """Genera un código único para la orden de producción"""
        from datetime import datetime
        prefix = "OP"
        year = datetime.now().year
        last_orden = OrdenProduccion.objects.filter(
            codigo__startswith=f"{prefix}-{year}"
        ).order_by('codigo').last()
        
        if last_orden:
            last_number = int(last_orden.codigo.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{year}-{new_number:05d}"

    def get_total_prendas(self):
        """Calcula el total de prendas en todos los pedidos de esta orden"""
        total = 0
        for pedido in self.pedidos.all():
            total += pedido.get_total_prendas()
        return total


class ResumenProduccion(models.Model):
    """
    Modelo para almacenar el resumen de producción por tipo, género y talla.
    Se actualiza automáticamente cuando cambian los pedidos.
    """
    orden_produccion = models.ForeignKey(
        OrdenProduccion,
        on_delete=models.CASCADE,
        related_name='resumen_items',
        verbose_name='Orden de Producción'
    )
    tipo_prenda = models.CharField(
        max_length=20,
        verbose_name='Tipo de Prenda'
    )
    genero = models.CharField(
        max_length=10,
        verbose_name='Género'
    )
    talla = models.CharField(
        max_length=5,
        verbose_name='Talla'
    )
    cantidad_total = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad Total'
    )

    class Meta:
        verbose_name = 'Resumen de Producción'
        verbose_name_plural = 'Resúmenes de Producción'
        ordering = ['tipo_prenda', 'genero', 'talla']
        unique_together = ['orden_produccion', 'tipo_prenda', 'genero', 'talla']

    def __str__(self):
        return f"{self.tipo_prenda} - {self.genero} - Talla {self.talla}: {self.cantidad_total}"


class MateriaPrimaRequerida(TimeStampedModel):
    """
    Registra los materiales necesarios para la producción.
    """
    TIPO_MATERIAL_CHOICES = [
        ('tela', 'Tela'),
        ('hilo', 'Hilo'),
        ('elastico', 'Elástico'),
        ('botones', 'Botones'),
        ('cremalleras', 'Cremalleras'),
        ('etiquetas', 'Etiquetas'),
        ('bolsas', 'Bolsas de Empaque'),
        ('otros', 'Otros'),
    ]

    orden_produccion = models.ForeignKey(
        OrdenProduccion,
        on_delete=models.CASCADE,
        related_name='materia_prima',
        verbose_name='Orden de Producción'
    )
    tipo_material = models.CharField(
        max_length=20,
        choices=TIPO_MATERIAL_CHOICES,
        verbose_name='Tipo de Material'
    )
    descripcion = models.CharField(
        max_length=200,
        verbose_name='Descripción'
    )
    cantidad_requerida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad Requerida'
    )
    unidad_medida = models.CharField(
        max_length=20,
        verbose_name='Unidad de Medida'
    )
    cantidad_comprada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Cantidad Comprada'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas'
    )

    class Meta:
        verbose_name = 'Materia Prima Requerida'
        verbose_name_plural = 'Materias Primas Requeridas'
        ordering = ['tipo_material']

    def __str__(self):
        return f"{self.descripcion} - {self.cantidad_requerida} {self.unidad_medida}"

    def get_pendiente_compra(self):
        """Retorna la cantidad pendiente de comprar"""
        return self.cantidad_requerida - self.cantidad_comprada

    def esta_completo(self):
        """Verifica si se ha comprado todo el material requerido"""
        return self.cantidad_comprada >= self.cantidad_requerida