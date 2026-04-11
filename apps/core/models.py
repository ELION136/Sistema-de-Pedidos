"""
Modelos base y utilidades compartidas
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    Modelo abstracto base que proporciona campos de fecha de creación y modificación.
    Todos los modelos del sistema heredarán de esta clase.
    """
    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        abstract = True


class AuditableModel(TimeStampedModel):
    """
    Modelo abstracto que extiende TimeStampedModel agregando campos de auditoría.
    """
    creado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_creado'
    )
    modificado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_modificado'
    )

    class Meta:
        abstract = True