from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum
from apps.core.models import TimeStampedModel

class PedidoPersonalizado(TimeStampedModel):
    TIPO_PEDIDO_CHOICES = [
        ('conjunto', 'Conjunto Completo'),
        ('separado', 'Prendas Separadas'),
    ]
    
    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('parcial', 'Parcial'),
        ('pagado', 'Pagado'),
    ]
    
    TIPO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('qr', 'QR'),
    ]
    
    ESTADO_PEDIDO_CHOICES = [
        ('registrado', 'Registrado'),
        ('en_produccion', 'En Producción'),
        ('entregado', 'Entregado'),
    ]

    GENERO_CHOICES = [
        ('varon', 'Varón'),
        ('mujer', 'Mujer'),
        ('unisex', 'Unisex'),
    ]
    
    TALLA_CHOICES = [
        ('4', '4'), ('6', '6'), ('8', '8'), ('10', '10'), ('12', '12'), 
        ('14', '14'), ('16', '16'), ('S', 'S'), ('M', 'M'), ('L', 'L'), 
        ('XL', 'XL'), ('XXL', 'XXL'),
    ]

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='pedidos_personalizados',
        verbose_name='Institución / Cliente'
    )
    nombre_completo = models.CharField(
        max_length=255, 
        verbose_name='Nombre Completo (Beneficiario)'
    )
    gestion = models.PositiveIntegerField(
        verbose_name='Gestión/Año'
    )
    categoria = models.CharField(
        max_length=100, 
        verbose_name='Curso/Grado/Categoría',
        help_text='Ej: 6to Secundaria, Promoción 2025, Docentes'
    )
    tipo_pedido = models.CharField(
        max_length=20, 
        choices=TIPO_PEDIDO_CHOICES, 
        default='separado',
        verbose_name='Tipo de Pedido'
    )
    
    # Campos base para cuando tipo_pedido == 'conjunto'
    talla_conjunto = models.CharField(
        max_length=5, choices=TALLA_CHOICES, blank=True, null=True,
        verbose_name='Talla del Conjunto'
    )
    genero_conjunto = models.CharField(
        max_length=10, choices=GENERO_CHOICES, blank=True, null=True,
        verbose_name='Género del Conjunto'
    )

    # Pagos
    aporte = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente')
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, null=True, blank=True)
    
    estado_pedido = models.CharField(max_length=20, choices=ESTADO_PEDIDO_CHOICES, default='registrado')

    class Meta:
        verbose_name = 'Pedido Personalizado'
        verbose_name_plural = 'Pedidos Personalizados'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.nombre_completo} - {self.cliente.nombre} ({self.gestion})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # Calcular saldo si hay total y aporte
        if self.total is not None and self.aporte is not None:
            self.saldo = self.total - self.aporte
            
        super().save(*args, **kwargs)
        
        # Generar prendas si es conjunto
        if self.tipo_pedido == 'conjunto' and self.talla_conjunto and self.genero_conjunto:
            self.generar_items_conjunto()

    def generar_items_conjunto(self):
        # Primero eliminamos anteriores si es que se actualiza la configuración
        self.items.filter(es_generado_automaticamente=True).delete()
        
        prendas = ['chamarra', 'buso', 'polera', 'short']
        for prenda in prendas:
            ItemPedidoPersonalizado.objects.create(
                pedido=self,
                tipo_prenda=prenda,
                talla=self.talla_conjunto,
                genero=self.genero_conjunto,
                cantidad=1,
                es_generado_automaticamente=True
            )

    @classmethod
    def get_resumen_prendas(cls):
        from django.db.models import Sum
        return ItemPedidoPersonalizado.objects.filter(
            pedido__estado_pedido='registrado'
        ).values(
            'tipo_prenda', 'talla', 'genero'
        ).annotate(
            total=Sum('cantidad')
        ).order_by('tipo_prenda', 'genero', 'talla')


class ItemPedidoPersonalizado(TimeStampedModel):
    TIPO_PRENDA_CHOICES = [
        ('chamarra', 'Chamarra'),
        ('buso', 'Buso'),
        ('polera', 'Polera'),
        ('short', 'Short'),
    ]
    
    pedido = models.ForeignKey(
        PedidoPersonalizado,
        on_delete=models.CASCADE,
        related_name='items'
    )
    tipo_prenda = models.CharField(max_length=20, choices=TIPO_PRENDA_CHOICES)
    genero = models.CharField(max_length=10, choices=PedidoPersonalizado.GENERO_CHOICES)
    talla = models.CharField(max_length=5, choices=PedidoPersonalizado.TALLA_CHOICES)
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    es_generado_automaticamente = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Ítem Personalizado'
        verbose_name_plural = 'Ítems Personalizados'
        ordering = ['tipo_prenda', 'genero', 'talla']

    def __str__(self):
        return f"{self.get_tipo_prenda_display()} - {self.talla} - {self.get_genero_display()}"
