"""
Vistas para la gestión de pedidos
"""
import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone

from .models import Pedido, ItemPedido, ConjuntoPedido, ImportacionExcel
from .forms import (
    PedidoForm, ItemPedidoForm, ConjuntoPedidoForm,
    ImportarExcelForm, ConfirmarImportacionForm, PedidoFilterForm,
    ItemPedidoFormSet, ConjuntoPedidoFormSet
)


@login_required
def lista_pedidos(request):
    """Vista para listar todos los pedidos con filtros"""
    form_filtro = PedidoFilterForm(request.GET or None)
    pedidos = Pedido.objects.select_related('cliente').all()
    
    # Aplicar filtros
    if form_filtro.is_valid():
        data = form_filtro.cleaned_data
        
        if data.get('cliente'):
            pedidos = pedidos.filter(
                Q(cliente__nombre__icontains=data['cliente'])
            )
        
        if data.get('gestion'):
            pedidos = pedidos.filter(gestion=data['gestion'])
        
        if data.get('estado'):
            pedidos = pedidos.filter(estado=data['estado'])
        
        if data.get('tipo_pedido'):
            pedidos = pedidos.filter(tipo_pedido=data['tipo_pedido'])
        
        if data.get('fecha_desde'):
            pedidos = pedidos.filter(creado_en__date__gte=data['fecha_desde'])
        
        if data.get('fecha_hasta'):
            pedidos = pedidos.filter(creado_en__date__lte=data['fecha_hasta'])
    
    # Paginación
    paginator = Paginator(pedidos.order_by('-creado_en'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form_filtro': form_filtro,
        'total_pedidos': pedidos.count(),
    }
    return render(request, 'pedidos/lista.html', context)


@login_required
def detalle_pedido(request, pk):
    """Vista para ver el detalle de un pedido"""
    pedido = get_object_or_404(Pedido.objects.select_related('cliente'), pk=pk)
    
    # Obtener ítems agrupados por tipo de prenda
    items_por_prenda = pedido.items.values('tipo_prenda').annotate(
        total=Sum('cantidad')
    ).order_by('tipo_prenda')
    
    # Obtener resumen por género y talla
    resumen_detallado = pedido.items.values(
        'tipo_prenda', 'genero', 'talla'
    ).annotate(
        total=Sum('cantidad')
    ).order_by('tipo_prenda', 'genero', 'talla')
    
    context = {
        'pedido': pedido,
        'items': pedido.items.all(),
        'conjuntos': pedido.conjuntos.all(),
        'items_por_prenda': items_por_prenda,
        'resumen_detallado': resumen_detallado,
        'total_prendas': pedido.get_total_prendas(),
    }
    return render(request, 'pedidos/detalle.html', context)


@login_required
def crear_pedido(request):
    """Vista para crear un nuevo pedido"""
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save()
            messages.success(request, f'Pedido "{pedido.codigo}" creado exitosamente.')
            return redirect('pedidos:agregar_items', pk=pedido.pk)
    else:
        form = PedidoForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Pedido',
    }
    return render(request, 'pedidos/formulario.html', context)


@login_required
def editar_pedido(request, pk):
    """Vista para editar un pedido existente"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            pedido = form.save()
            messages.success(request, f'Pedido "{pedido.codigo}" actualizado exitosamente.')
            return redirect('pedidos:detalle', pk=pedido.pk)
    else:
        form = PedidoForm(instance=pedido)
    
    context = {
        'form': form,
        'pedido': pedido,
        'titulo': 'Editar Pedido',
    }
    return render(request, 'pedidos/formulario.html', context)


@login_required
def agregar_items_pedido(request, pk):
    """Vista para agregar ítems a un pedido (prendas individuales o conjuntos)"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_prenda':
            form = ItemPedidoForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.pedido = pedido
                item.save()
                messages.success(request, 'Prenda agregada exitosamente.')
                return redirect('pedidos:agregar_items', pk=pedido.pk)
        
        elif action == 'add_conjunto':
            form = ConjuntoPedidoForm(request.POST)
            if form.is_valid():
                conjunto = form.save(commit=False)
                conjunto.pedido = pedido
                conjunto.save()
                messages.success(
                    request, 
                    f'Conjunto agregado exitosamente. Se generaron automáticamente '
                    f'{conjunto.cantidad * 4} prendas individuales.'
                )
                return redirect('pedidos:agregar_items', pk=pedido.pk)
    
    else:
        item_form = ItemPedidoForm()
        conjunto_form = ConjuntoPedidoForm()
    
    context = {
        'pedido': pedido,
        'item_form': ItemPedidoForm(),
        'conjunto_form': ConjuntoPedidoForm(),
        'items': pedido.items.all(),
        'conjuntos': pedido.conjuntos.all(),
    }
    return render(request, 'pedidos/agregar_items.html', context)


@login_required
def eliminar_item_pedido(request, pedido_pk, item_pk):
    """Vista para eliminar un ítem de pedido"""
    pedido = get_object_or_404(Pedido, pk=pedido_pk)
    item = get_object_or_404(ItemPedido, pk=item_pk, pedido=pedido)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Ítem eliminado exitosamente.')
        return redirect('pedidos:agregar_items', pk=pedido.pk)
    
    context = {
        'pedido': pedido,
        'item': item,
    }
    return render(request, 'pedidos/confirmar_eliminar_item.html', context)


@login_required
def eliminar_conjunto_pedido(request, pedido_pk, conjunto_pk):
    """Vista para eliminar un conjunto de pedido"""
    pedido = get_object_or_404(Pedido, pk=pedido_pk)
    conjunto = get_object_or_404(ConjuntoPedido, pk=conjunto_pk, pedido=pedido)
    
    if request.method == 'POST':
        prendas_eliminadas = conjunto.cantidad * 4
        conjunto.delete()
        messages.success(
            request, 
            f'Conjunto eliminado exitosamente. Se eliminaron {prendas_eliminadas} prendas individuales.'
        )
        return redirect('pedidos:agregar_items', pk=pedido.pk)
    
    context = {
        'pedido': pedido,
        'conjunto': conjunto,
    }
    return render(request, 'pedidos/confirmar_eliminar_conjunto.html', context)


@login_required
def importar_excel(request, pk):
    """Vista para importar datos desde Excel"""
    pedido = get_object_or_404(Pedido, pk=pk)
    preview_data = None
    errores = []
    importacion = None

    if request.method == 'POST':
        form = ImportarExcelForm(request.POST, request.FILES)
        
        if 'preview' in request.POST:
            # Modo vista previa: validar y guardar archivo temporalmente
            if form.is_valid():
                archivo = request.FILES['archivo']
                # Crear registro de importación asociado al pedido
                importacion = ImportacionExcel.objects.create(
                    archivo=archivo,
                    pedido=pedido,          # <-- CRUCIAL: asignar el pedido
                    estado='pendiente',
                    filas_procesadas=0,
                    filas_con_error=0
                )
                preview_data, errores = procesar_excel_preview(archivo)
                # Si deseas guardar preview_data en el objeto (opcional)
                # importacion.datos_preview = preview_data
                # importacion.save()
            else:
                errores.append("Por favor, seleccione un archivo válido.")
        
        elif 'confirmar' in request.POST:
            importacion_id = request.POST.get('importacion_id')
            if not importacion_id:
                messages.error(request, 'No se encontró la importación temporal.')
                return redirect('pedidos:importar_excel', pk=pedido.pk)
            
            try:
                importacion = ImportacionExcel.objects.get(pk=importacion_id, pedido=pedido)
                if importacion.estado != 'pendiente':
                    messages.error(request, 'Esta importación ya fue procesada.')
                    return redirect('pedidos:importar_excel', pk=pedido.pk)
                
                filas_procesadas, errores = procesar_importacion_confirmada(importacion, pedido)
                
                if errores:
                    messages.warning(request, f'Importación completada con {len(errores)} errores.')
                else:
                    messages.success(request, f'Importación completada. {filas_procesadas} filas procesadas.')
                
                return redirect('pedidos:detalle', pk=pedido.pk)
            
            except ImportacionExcel.DoesNotExist:
                messages.error(request, 'La importación temporal no existe o no pertenece a este pedido.')
                return redirect('pedidos:importar_excel', pk=pedido.pk)
    
    else:
        form = ImportarExcelForm()
    
    context = {
        'form': form,
        'pedido': pedido,
        'preview_data': preview_data,
        'errores': errores,
        'importacion_id': importacion.id if importacion else None,
    }
    return render(request, 'pedidos/importar_excel.html', context)

    
def procesar_excel_preview(archivo):
    """
    Procesa el archivo Excel y retorna datos para vista previa.
    Retorna: (preview_data, errores)
    """
    preview_data = []
    errores = []
    
    try:
        df = pd.read_excel(archivo)
        
        # Mapeo flexible de nombres de columnas (más completo)
        mapeo_columnas = {
            # Tipo de prenda
            'prenda': 'tipo_prenda',
            'tipo': 'tipo_prenda',
            'tipo_prenda': 'tipo_prenda',
            'tipo_de_prenda': 'tipo_prenda',   # <-- NUEVO
            'tipo prenda': 'tipo_prenda',      # <-- NUEVO
            # Género
            'genero': 'genero',
            'género': 'genero',
            'sexo': 'genero',
            # Talla
            'talla': 'talla',
            'tamaño': 'talla',
            'size': 'talla',
            # Cantidad
            'cantidad': 'cantidad',
            'cant': 'cantidad',
            'qty': 'cantidad',
        }
        
        columnas_mapeadas = {}
        for col in df.columns:
            col_norm = col.lower().strip().replace(' ', '_')
            if col_norm in mapeo_columnas:
                columnas_mapeadas[mapeo_columnas[col_norm]] = col
        
        if len(columnas_mapeadas) < 4:
            errores.append(f'Columnas encontradas: {list(df.columns)}')
            errores.append('Se requieren al menos las columnas: Tipo de Prenda, Género, Talla, Cantidad')
            return None, errores
        
        # Procesar filas (resto igual)
        for idx, row in df.iterrows():
            try:
                tipo_prenda = str(row[columnas_mapeadas.get('tipo_prenda')]).strip()
                genero = str(row[columnas_mapeadas.get('genero')]).strip()
                talla = str(row[columnas_mapeadas.get('talla')]).strip()
                cantidad = row[columnas_mapeadas.get('cantidad')]
                
                # Validar tipo de prenda
                tipos_validos = ['chamarra', 'buso', 'polera', 'short']
                if tipo_prenda.lower() not in tipos_validos:
                    errores.append(f'Fila {idx + 2}: Tipo de prenda "{tipo_prenda}" no válido')
                    continue
                
                # Validar género
                generos_validos = ['varón', 'varon', 'mujer', 'unisex']
                if genero.lower() not in generos_validos:
                    errores.append(f'Fila {idx + 2}: Género "{genero}" no válido')
                    continue
                
                # Normalizar género
                if genero.lower() in ['varón', 'varon']:
                    genero = 'varon'
                elif genero.lower() == 'mujer':
                    genero = 'mujer'
                else:
                    genero = 'unisex'
                
                # Validar talla
                tallas_validas = ['4', '6', '8', '10', '12', '14', '16', 's', 'm', 'l', 'xl', 'xxl']
                if talla.lower() not in tallas_validas:
                    errores.append(f'Fila {idx + 2}: Talla "{talla}" no válida')
                    continue
                
                # Validar cantidad
                try:
                    cantidad = int(float(cantidad))
                    if cantidad <= 0:
                        errores.append(f'Fila {idx + 2}: La cantidad debe ser mayor a 0')
                        continue
                except (ValueError, TypeError):
                    errores.append(f'Fila {idx + 2}: Cantidad no válida')
                    continue
                
                preview_data.append({
                    'tipo_prenda': tipo_prenda.lower(),
                    'genero': genero,
                    'talla': talla.upper(),
                    'cantidad': cantidad,
                })
                
            except Exception as e:
                errores.append(f'Fila {idx + 2}: Error al procesar - {str(e)}')
    
    except Exception as e:
        errores.append(f'Error al leer el archivo: {str(e)}')
    
    return preview_data, errores


def procesar_importacion_confirmada(importacion, pedido):
    """
    Procesa la importación confirmada y crea los ítems en el pedido.
    Retorna: (filas_procesadas, errores)
    """
    filas_procesadas = 0
    errores = []
    
    try:
        df = pd.read_excel(importacion.archivo)
        
        # Mismo mapeo mejorado
        mapeo_columnas = {
            'prenda': 'tipo_prenda',
            'tipo': 'tipo_prenda',
            'tipo_prenda': 'tipo_prenda',
            'tipo_de_prenda': 'tipo_prenda',
            'tipo prenda': 'tipo_prenda',
            'genero': 'genero',
            'género': 'genero',
            'sexo': 'genero',
            'talla': 'talla',
            'tamaño': 'talla',
            'size': 'talla',
            'cantidad': 'cantidad',
            'cant': 'cantidad',
            'qty': 'cantidad',
        }
        
        columnas_mapeadas = {}
        for col in df.columns:
            col_norm = col.lower().strip().replace(' ', '_')
            if col_norm in mapeo_columnas:
                columnas_mapeadas[mapeo_columnas[col_norm]] = col
        
        for idx, row in df.iterrows():
            try:
                tipo_prenda = str(row[columnas_mapeadas.get('tipo_prenda')]).strip().lower()
                genero_raw = str(row[columnas_mapeadas.get('genero')]).strip().lower()
                talla = str(row[columnas_mapeadas.get('talla')]).strip().upper()
                cantidad = int(float(row[columnas_mapeadas.get('cantidad')]))
                
                # Normalizar género
                if genero_raw in ['varón', 'varon']:
                    genero = 'varon'
                elif genero_raw == 'mujer':
                    genero = 'mujer'
                else:
                    genero = 'unisex'
                
                # Crear el ítem
                ItemPedido.objects.create(
                    pedido=pedido,
                    tipo_prenda=tipo_prenda,
                    genero=genero,
                    talla=talla,
                    cantidad=cantidad,
                    notas=f'Importado desde Excel el {timezone.now().strftime("%Y-%m-%d %H:%M")}'
                )
                
                filas_procesadas += 1
                
            except Exception as e:
                errores.append(f'Fila {idx + 2}: {str(e)}')
        
        # Actualizar estado de la importación
        importacion.estado = 'completado'
        importacion.filas_procesadas = filas_procesadas
        importacion.filas_con_error = len(errores)
        importacion.errores_detalle = {'errores': errores}
        importacion.procesado_en = timezone.now()
        importacion.save()
        
    except Exception as e:
        importacion.estado = 'error'
        importacion.errores_detalle = {'error_general': str(e)}
        importacion.save()
        errores.append(str(e))
    
    return filas_procesadas, errores

@login_required
def resumen_pedido_produccion(request, pk):
    """Vista para ver el resumen de un pedido listo para producción"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    # Agrupar por tipo de prenda, género y talla
    resumen = pedido.items.values(
        'tipo_prenda', 'genero', 'talla'
    ).annotate(
        cantidad_total=Sum('cantidad')
    ).order_by('tipo_prenda', 'genero', 'talla')
    
    # Totales por tipo de prenda
    totales_por_prenda = pedido.items.values('tipo_prenda').annotate(
        total=Sum('cantidad')
    ).order_by('tipo_prenda')
    
    # Totales por género
    totales_por_genero = pedido.items.values('genero').annotate(
        total=Sum('cantidad')
    ).order_by('genero')
    
    context = {
        'pedido': pedido,
        'resumen': resumen,
        'totales_por_prenda': totales_por_prenda,
        'totales_por_genero': totales_por_genero,
        'total_prendas': pedido.get_total_prendas(),
    }
    return render(request, 'pedidos/resumen_produccion.html', context)