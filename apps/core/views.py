"""
Vistas principales del sistema
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.pedidos.models import Pedido
from apps.clientes.models import Cliente
from apps.produccion.models import OrdenProduccion


@login_required
def dashboard(request):
    """Vista del dashboard principal del sistema"""
    # Estadísticas generales
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_en_proceso = Pedido.objects.filter(estado='en_proceso').count()
    pedidos_completados = Pedido.objects.filter(estado='completado').count()
    
    total_clientes = Cliente.objects.filter(activo=True).count()
    
    ordenes_activas = OrdenProduccion.objects.filter(
        estado__in=['pendiente', 'en_corte', 'en_confeccion', 'en_acabados']
    ).count()
    
    # Últimos pedidos
    ultimos_pedidos = Pedido.objects.select_related('cliente').order_by('-creado_en')[:5]
    
    # Pedidos próximos a vencer (fecha de entrega en los próximos 7 días)
    from datetime import datetime, timedelta
    fecha_limite = datetime.now() + timedelta(days=7)
    pedidos_urgentes = Pedido.objects.filter(
        fecha_entrega__lte=fecha_limite,
        estado__in=['pendiente', 'en_proceso']
    ).select_related('cliente').order_by('fecha_entrega')[:5]
    
    context = {
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_en_proceso': pedidos_en_proceso,
        'pedidos_completados': pedidos_completados,
        'total_clientes': total_clientes,
        'ordenes_activas': ordenes_activas,
        'ultimos_pedidos': ultimos_pedidos,
        'pedidos_urgentes': pedidos_urgentes,
    }
    return render(request, 'core/dashboard.html', context)