"""
Modelos para la gestión de pedidos de ropa deportiva
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum
from apps.core.models import TimeStampedModel


class Pedido(TimeStampedModel):
    """
    Representa un pedido completo realizado por un cliente.
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_PEDIDO_CHOICES = [
        ('completo', 'Conjunto Completo'),
        ('parcial', 'Pedido Parcial'),
    ]

    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código de Pedido'
    )
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Cliente'
    )
    gestion = models.PositiveIntegerField(
        verbose_name='Gestión/Año',
        help_text='Año o gestión del pedido (ej: 2024)'
    )
    tipo_pedido = models.CharField(
        max_length=20,
        choices=TIPO_PEDIDO_CHOICES,
        default='parcial',
        verbose_name='Tipo de Pedido'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    fecha_entrega = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Entrega Estimada'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas del Pedido'
    )

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['cliente', 'gestion']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_entrega']),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.cliente.nombre} ({self.gestion})"

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self.generar_codigo()
        super().save(*args, **kwargs)

    def generar_codigo(self):
        """Genera un código único para el pedido"""
        from datetime import datetime
        prefix = "PED"
        year = datetime.now().year
        last_pedido = Pedido.objects.filter(
            codigo__startswith=f"{prefix}-{year}"
        ).order_by('codigo').last()
        
        if last_pedido:
            last_number = int(last_pedido.codigo.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{year}-{new_number:05d}"

    def get_total_prendas(self):
        """Calcula el total de prendas en el pedido"""
        total = self.items.aggregate(
            total=Sum('cantidad')
        )['total'] or 0
        return total

    def get_resumen_por_prenda(self):
        """Retorna un resumen agrupado por tipo de prenda"""
        from django.db.models import Count
        return self.items.values('tipo_prenda', 'genero').annotate(
            total=Sum('cantidad')
        ).order_by('tipo_prenda', 'genero')

    def get_items_conteo_detallado(self):
        """Retorna el conteo detallado de cada ítem"""
        return self.items.select_related().all()


class ItemPedido(TimeStampedModel):
    """
    Representa un ítem individual dentro de un pedido.
    Puede ser una prenda individual o parte de un conjunto.
    """
    TIPO_PRENDA_CHOICES = [
        ('chamarra', 'Chamarra'),
        ('buso', 'Buso'),
        ('polera', 'Polera'),
        ('short', 'Short'),
    ]
    
    GENERO_CHOICES = [
        ('varon', 'Varón'),
        ('mujer', 'Mujer'),
        ('unisex', 'Unisex'),
    ]
    
    TALLA_CHOICES = [
        ('4', '4'),
        ('6', '6'),
        ('8', '8'),
        ('10', '10'),
        ('12', '12'),
        ('14', '14'),
        ('16', '16'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido'
    )
    tipo_prenda = models.CharField(
        max_length=20,
        choices=TIPO_PRENDA_CHOICES,
        verbose_name='Tipo de Prenda'
    )
    genero = models.CharField(
        max_length=10,
        choices=GENERO_CHOICES,
        verbose_name='Género'
    )
    talla = models.CharField(
        max_length=5,
        choices=TALLA_CHOICES,
        verbose_name='Talla'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Cantidad'
    )
    es_parte_de_conjunto = models.BooleanField(
        default=False,
        verbose_name='Es parte de conjunto',
        help_text='Indica si este ítem fue generado automáticamente de un conjunto'
    )
    conjunto_padre_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='ID del Conjunto Padre',
        help_text='ID del ítem conjunto que generó esta prenda'
    )
    notas = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Notas'
    )

    class Meta:
        verbose_name = 'Ítem de Pedido'
        verbose_name_plural = 'Ítems de Pedido'
        ordering = ['tipo_prenda', 'genero', 'talla']
        indexes = [
            models.Index(fields=['pedido', 'tipo_prenda']),
            models.Index(fields=['pedido', 'genero']),
            models.Index(fields=['pedido', 'talla']),
            models.Index(fields=['tipo_prenda', 'genero', 'talla']),
        ]

    def __str__(self):
        return f"{self.get_tipo_prenda_display()} - {self.get_genero_display()} - Talla {self.talla} ({self.cantidad} uds)"


class ConjuntoPedido(TimeStampedModel):
    """
    Representa un conjunto completo de prendas registrado en un pedido.
    Cuando se guarda, automáticamente genera los ítems individuales.
    """
    GENERO_CHOICES = [
        ('varon', 'Varón'),
        ('mujer', 'Mujer'),
        ('unisex', 'Unisex'),
    ]
    
    TALLA_CHOICES = [
        ('4', '4'),
        ('6', '6'),
        ('8', '8'),
        ('10', '10'),
        ('12', '12'),
        ('14', '14'),
        ('16', '16'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='conjuntos',
        verbose_name='Pedido'
    )
    genero = models.CharField(
        max_length=10,
        choices=GENERO_CHOICES,
        verbose_name='Género'
    )
    talla = models.CharField(
        max_length=5,
        choices=TALLA_CHOICES,
        verbose_name='Talla'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Cantidad de Conjuntos'
    )
    notas = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Notas'
    )

    class Meta:
        verbose_name = 'Conjunto de Pedido'
        verbose_name_plural = 'Conjuntos de Pedido'
        ordering = ['genero', 'talla']

    def __str__(self):
        return f"Conjunto {self.get_genero_display()} - Talla {self.talla} ({self.cantidad} uds)"

    def save(self, *args, **kwargs):
        """
        Al guardar un conjunto, primero eliminamos los ítems anteriores
        generados por este conjunto (si es una actualización) y luego
        generamos los nuevos ítems individuales.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Si es una actualización, eliminar ítems previos generados por este conjunto
        if not is_new:
            ItemPedido.objects.filter(
                pedido=self.pedido,
                conjunto_padre_id=self.pk
            ).delete()
        
        # Generar los ítems individuales del conjunto
        self.generar_items_individuales()

    def delete(self, *args, **kwargs):
        """Al eliminar un conjunto, eliminar también sus ítems generados"""
        ItemPedido.objects.filter(
            pedido=self.pedido,
            conjunto_padre_id=self.pk
        ).delete()
        super().delete(*args, **kwargs)

    def generar_items_individuales(self):
        """
        Genera automáticamente los ítems individuales para cada prenda del conjunto.
        Un conjunto completo incluye: chamarra, buso, polera y short.
        """
        prendas_conjunto = ['chamarra', 'buso', 'polera', 'short']
        
        for prenda in prendas_conjunto:
            ItemPedido.objects.create(
                pedido=self.pedido,
                tipo_prenda=prenda,
                genero=self.genero,
                talla=self.talla,
                cantidad=self.cantidad,
                es_parte_de_conjunto=True,
                conjunto_padre_id=self.pk,
                notas=f"Generado de conjunto #{self.pk}"
            )

    def get_prendas_incluidas(self):
        """Retorna la lista de prendas incluidas en el conjunto"""
        return ['Chamarra', 'Buso', 'Polera', 'Short']


class ImportacionExcel(TimeStampedModel):
    """
    Registra las importaciones de archivos Excel realizadas.
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='importaciones',
        verbose_name='Pedido'
    )
    archivo = models.FileField(
        upload_to='importaciones/%Y/%m/',
        verbose_name='Archivo Excel'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    filas_procesadas = models.PositiveIntegerField(
        default=0,
        verbose_name='Filas Procesadas'
    )
    filas_con_error = models.PositiveIntegerField(
        default=0,
        verbose_name='Filas con Error'
    )
    errores_detalle = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Detalle de Errores'
    )
    procesado_en = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Procesado el'
    )

    class Meta:
        verbose_name = 'Importación Excel'
        verbose_name_plural = 'Importaciones Excel'
        ordering = ['-creado_en']

    def __str__(self):
        return f"Importación {self.archivo.name} - {self.get_estado_display()}"