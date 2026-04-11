"""
Vistas para el módulo de producción
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.core.paginator import Paginator

from .models import OrdenProduccion, ResumenProduccion, MateriaPrimaRequerida
from .forms import OrdenProduccionForm, MateriaPrimaForm, GenerarOrdenProduccionForm


@login_required
def dashboard_produccion(request):
    """Dashboard principal del módulo de producción"""
    # Estadísticas generales
    ordenes_activas = OrdenProduccion.objects.filter(
        estado__in=['pendiente', 'en_corte', 'en_confeccion', 'en_acabados']
    ).count()
    
    ordenes_completadas = OrdenProduccion.objects.filter(
        estado='completada'
    ).count()
    
    total_prendas_en_produccion = 0
    for orden in OrdenProduccion.objects.filter(
        estado__in=['pendiente', 'en_corte', 'en_confeccion', 'en_acabados']
    ):
        total_prendas_en_produccion += orden.get_total_prendas()
    
    # Últimas órdenes
    ultimas_ordenes = OrdenProduccion.objects.all()[:5]
    
    context = {
        'ordenes_activas': ordenes_activas,
        'ordenes_completadas': ordenes_completadas,
        'total_prendas_en_produccion': total_prendas_en_produccion,
        'ultimas_ordenes': ultimas_ordenes,
    }
    return render(request, 'produccion/dashboard.html', context)


@login_required
def lista_ordenes(request):
    """Vista para listar todas las órdenes de producción"""
    ordenes = OrdenProduccion.objects.prefetch_related('pedidos').all()
    
    # Paginación
    paginator = Paginator(ordenes.order_by('-creado_en'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_ordenes': ordenes.count(),
    }
    return render(request, 'produccion/lista_ordenes.html', context)


@login_required
def detalle_orden(request, pk):
    """Vista para ver el detalle de una orden de producción"""
    orden = get_object_or_404(
        OrdenProduccion.objects.prefetch_related('pedidos', 'resumen_items', 'materia_prima'),
        pk=pk
    )
    
    # Resumen por tipo de prenda
    resumen_por_prenda = orden.resumen_items.values('tipo_prenda').annotate(
        total=Sum('cantidad_total')
    ).order_by('tipo_prenda')
    
    # Resumen detallado
    resumen_detallado = orden.resumen_items.all()
    
    # Materia prima
    materia_prima = orden.materia_prima.all()
    
    context = {
        'orden': orden,
        'pedidos': orden.pedidos.all(),
        'resumen_por_prenda': resumen_por_prenda,
        'resumen_detallado': resumen_detallado,
        'materia_prima': materia_prima,
        'total_prendas': orden.get_total_prendas(),
    }
    return render(request, 'produccion/detalle_orden.html', context)


@login_required
def crear_orden(request):
    """Vista para crear una nueva orden de producción"""
    if request.method == 'POST':
        form = OrdenProduccionForm(request.POST)
        if form.is_valid():
            orden = form.save()
            
            # Generar resumen de producción automáticamente
            generar_resumen_produccion(orden)
            
            messages.success(request, f'Orden de producción "{orden.codigo}" creada exitosamente.')
            return redirect('produccion:detalle_orden', pk=orden.pk)
    else:
        form = OrdenProduccionForm()
    
    context = {
        'form': form,
        'titulo': 'Nueva Orden de Producción',
    }
    return render(request, 'produccion/formulario_orden.html', context)


@login_required
def editar_orden(request, pk):
    """Vista para editar una orden de producción"""
    orden = get_object_or_404(OrdenProduccion, pk=pk)
    
    if request.method == 'POST':
        form = OrdenProduccionForm(request.POST, instance=orden)
        if form.is_valid():
            orden = form.save()
            
            # Regenerar resumen de producción
            orden.resumen_items.all().delete()
            generar_resumen_produccion(orden)
            
            messages.success(request, f'Orden "{orden.codigo}" actualizada exitosamente.')
            return redirect('produccion:detalle_orden', pk=orden.pk)
    else:
        form = OrdenProduccionForm(instance=orden)
    
    context = {
        'form': form,
        'orden': orden,
        'titulo': 'Editar Orden de Producción',
    }
    return render(request, 'produccion/formulario_orden.html', context)


def generar_resumen_produccion(orden):
    """
    Genera automáticamente el resumen de producción agregando
    todas las prendas de los pedidos incluidos en la orden.
    """
    from apps.pedidos.models import ItemPedido
    
    # Obtener todos los ítems de los pedidos de esta orden
    pedidos_ids = orden.pedidos.values_list('id', flat=True)
    
    # Agrupar por tipo_prenda, genero, talla y sumar cantidades
    items_agrupados = ItemPedido.objects.filter(
        pedido_id__in=pedidos_ids
    ).values('tipo_prenda', 'genero', 'talla').annotate(
        total=Sum('cantidad')
    )
    
    # Crear registros de ResumenProduccion
    for item in items_agrupados:
        ResumenProduccion.objects.create(
            orden_produccion=orden,
            tipo_prenda=item['tipo_prenda'],
            genero=item['genero'],
            talla=item['talla'],
            cantidad_total=item['total']
        )


@login_required
def resumen_clasificacion(request, orden_pk):
    """
    Vista para ver el resumen clasificado de una orden de producción.
    Muestra la tabla clara lista para producción.
    """
    orden = get_object_or_404(OrdenProduccion, pk=orden_pk)
    
    # Obtener resumen detallado
    resumen = orden.resumen_items.values(
        'tipo_prenda', 'genero', 'talla', 'cantidad_total'
    ).order_by('tipo_prenda', 'genero', 'talla')
    
    # Organizar datos en formato de tabla
    tipos_prenda = orden.resumen_items.values_list('tipo_prenda', flat=True).distinct()
    generos = orden.resumen_items.values_list('genero', flat=True).distinct()
    tallas = ['4', '6', '8', '10', '12', '14', '16', 'S', 'M', 'L', 'XL', 'XXL']
    
    # Crear estructura de tabla
    tabla_resumen = {}
    for tipo in tipos_prenda:
        tabla_resumen[tipo] = {}
        for genero in generos:
            tabla_resumen[tipo][genero] = {}
            for talla in tallas:
                cantidad = orden.resumen_items.filter(
                    tipo_prenda=tipo,
                    genero=genero,
                    talla=talla
                ).first()
                tabla_resumen[tipo][genero][talla] = cantidad.cantidad_total if cantidad else 0
    
    context = {
        'orden': orden,
        'tabla_resumen': tabla_resumen,
        'tipos_prenda': tipos_prenda,
        'generos': generos,
        'tallas': tallas,
        'total_prendas': orden.get_total_prendas(),
    }
    return render(request, 'produccion/resumen_clasificacion.html', context)


@login_required
def agregar_materia_prima(request, orden_pk):
    """Vista para agregar materia prima a una orden de producción"""
    orden = get_object_or_404(OrdenProduccion, pk=orden_pk)
    
    if request.method == 'POST':
        form = MateriaPrimaForm(request.POST)
        if form.is_valid():
            materia = form.save(commit=False)
            materia.orden_produccion = orden
            materia.save()
            messages.success(request, 'Materia prima agregada exitosamente.')
            return redirect('produccion:detalle_orden', pk=orden.pk)
    else:
        form = MateriaPrimaForm()
    
    context = {
        'form': form,
        'orden': orden,
    }
    return render(request, 'produccion/agregar_materia_prima.html', context)


@login_required
def editar_materia_prima(request, pk):
    """Vista para editar materia prima"""
    materia = get_object_or_404(MateriaPrimaRequerida, pk=pk)
    orden = materia.orden_produccion
    
    if request.method == 'POST':
        form = MateriaPrimaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia prima actualizada exitosamente.')
            return redirect('produccion:detalle_orden', pk=orden.pk)
    else:
        form = MateriaPrimaForm(instance=materia)
    
    context = {
        'form': form,
        'orden': orden,
        'materia': materia,
    }
    return render(request, 'produccion/editar_materia_prima.html', context)


@login_required
def reporte_materia_prima(request, orden_pk):
    """Vista para generar reporte de materia prima requerida"""
    orden = get_object_or_404(OrdenProduccion, pk=orden_pk)
    
    # Agrupar materia prima por tipo
    materia_por_tipo = {}
    for materia in orden.materia_prima.all():
        if materia.tipo_material not in materia_por_tipo:
            materia_por_tipo[materia.tipo_material] = []
        materia_por_tipo[materia.tipo_material].append(materia)
    
    context = {
        'orden': orden,
        'materia_por_tipo': materia_por_tipo,
    }
    return render(request, 'produccion/reporte_materia_prima.html', context)


@login_required
def cambiar_estado_orden(request, pk):
    """Vista para cambiar el estado de una orden de producción"""
    orden = get_object_or_404(OrdenProduccion, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in [e[0] for e in OrdenProduccion.ESTADO_CHOICES]:
            orden.estado = nuevo_estado
            orden.save()
            messages.success(request, f'Estado actualizado a: {orden.get_estado_display()}')
        else:
            messages.error(request, 'Estado no válido')
        
        return redirect('produccion:detalle_orden', pk=orden.pk)
    
    context = {
        'orden': orden,
        'estados_disponibles': OrdenProduccion.ESTADO_CHOICES,
    }
    return render(request, 'produccion/cambiar_estado.html', context)