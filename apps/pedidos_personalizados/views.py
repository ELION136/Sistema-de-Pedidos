from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
import pandas as pd
from decimal import Decimal

from .models import PedidoPersonalizado, ItemPedidoPersonalizado
from .forms import (
    PedidoPersonalizadoForm, ItemPedidoPersonalizadoForm,
    FiltrosPedidoPersonalizadoForm, ImportarExcelPersonalizadoForm
)
from apps.clientes.models import Cliente

@login_required
def dashboard_personalizados(request):
    pedidos = PedidoPersonalizado.objects.all()
    
    total_personas = pedidos.count()
    total_prendas = ItemPedidoPersonalizado.objects.aggregate(t=Sum('cantidad'))['t'] or 0
    total_aportes = pedidos.aggregate(t=Sum('aporte'))['t'] or 0
    total_saldos = pedidos.aggregate(t=Sum('saldo'))['t'] or 0

    # Resumen por categoría para gráfico
    categorias_qs = pedidos.values('categoria').annotate(total=Count('id')).order_by('-total')[:10]
    labels_categorias = [c['categoria'] for c in categorias_qs]
    datos_categorias = [c['total'] for c in categorias_qs]

    resumen_prendas = PedidoPersonalizado.get_resumen_prendas()

    context = {
        'total_personas': total_personas,
        'total_prendas': total_prendas,
        'total_aportes': total_aportes,
        'total_saldos': total_saldos,
        'labels_categorias': labels_categorias,
        'datos_categorias': datos_categorias,
        'resumen_prendas': resumen_prendas,
    }
    return render(request, 'pedidos_personalizados/dashboard.html', context)

@login_required
def lista_pedidos(request):
    form_filtros = FiltrosPedidoPersonalizadoForm(request.GET)
    pedidos = PedidoPersonalizado.objects.select_related('cliente').all()

    if form_filtros.is_valid():
        buscar = form_filtros.cleaned_data.get('buscar')
        cliente = form_filtros.cleaned_data.get('cliente')
        gestion = form_filtros.cleaned_data.get('gestion')
        categoria = form_filtros.cleaned_data.get('categoria')
        estado_pedido = form_filtros.cleaned_data.get('estado_pedido')
        estado_pago = form_filtros.cleaned_data.get('estado_pago')

        if buscar:
            pedidos = pedidos.filter(nombre_completo__icontains=buscar)
        if cliente:
            pedidos = pedidos.filter(cliente=cliente)
        if gestion:
            pedidos = pedidos.filter(gestion=gestion)
        if categoria:
            pedidos = pedidos.filter(categoria__icontains=categoria)
        if estado_pedido:
            pedidos = pedidos.filter(estado_pedido=estado_pedido)
        if estado_pago:
            pedidos = pedidos.filter(estado_pago=estado_pago)

    paginator = Paginator(pedidos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pedidos_personalizados/lista.html', {
        'page_obj': page_obj,
        'form_filtros': form_filtros,
    })

@login_required
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoPersonalizadoForm(request.POST)
        if form.is_valid():
            pedido = form.save()
            messages.success(request, 'Pedido personalizado creado exitosamente.')
            if pedido.tipo_pedido == 'separado':
                return redirect('pedidos_personalizados:agregar_item', pedido_pk=pedido.pk)
            return redirect('pedidos_personalizados:lista')
    else:
        form = PedidoPersonalizadoForm()
    
    return render(request, 'pedidos_personalizados/formulario.html', {'form': form, 'titulo': 'Nuevo Pedido Personalizado'})

@login_required
def editar_pedido(request, pk):
    pedido = get_object_or_404(PedidoPersonalizado, pk=pk)
    if request.method == 'POST':
        form = PedidoPersonalizadoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido actualizado.')
            return redirect('pedidos_personalizados:lista')
    else:
        form = PedidoPersonalizadoForm(instance=pedido)
        
    return render(request, 'pedidos_personalizados/formulario.html', {
        'form': form, 
        'titulo': f'Editar Pedido: {pedido.nombre_completo}',
        'pedido': pedido
    })

@login_required
def eliminar_pedido(request, pk):
    pedido = get_object_or_404(PedidoPersonalizado, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, 'Pedido eliminado.')
        return redirect('pedidos_personalizados:lista')
    return render(request, 'pedidos_personalizados/confirmar_eliminar.html', {'pedido': pedido})

@login_required
def agregar_item(request, pedido_pk):
    pedido = get_object_or_404(PedidoPersonalizado, pk=pedido_pk)
    items = pedido.items.all()
    
    if request.method == 'POST':
        form = ItemPedidoPersonalizadoForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.pedido = pedido
            item.save()
            messages.success(request, 'Ítem agregado.')
            return redirect('pedidos_personalizados:agregar_item', pedido_pk=pedido.pk)
    else:
        form = ItemPedidoPersonalizadoForm()
        
    return render(request, 'pedidos_personalizados/agregar_items.html', {
        'pedido': pedido, 'form': form, 'items': items
    })

@login_required
def eliminar_item(request, item_pk):
    item = get_object_or_404(ItemPedidoPersonalizado, pk=item_pk)
    pedido_pk = item.pedido.pk
    item.delete()
    messages.success(request, 'Ítem eliminado.')
    return redirect('pedidos_personalizados:agregar_item', pedido_pk=pedido_pk)

@login_required
def importar_excel(request):
    if request.method == 'POST':
        form = ImportarExcelPersonalizadoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_excel(request.FILES['archivo'])
                
                required_cols = ['Cliente', 'Nombre Completo', 'Gestión', 'Categoría', 'Tipo Pedido']
                missing_cols = [c for c in required_cols if c not in df.columns]
                if missing_cols:
                    messages.error(request, f"Faltan columnas requeridas: {', '.join(missing_cols)}")
                    return redirect('pedidos_personalizados:importar')
                
                # Agrupamos por persona
                for index, row in df.iterrows():
                    cliente_nombre = str(row['Cliente']).strip()
                    nombre = str(row['Nombre Completo']).strip()
                    gestion = int(row['Gestión']) if pd.notna(row['Gestión']) else 2024
                    categoria = str(row['Categoría']).strip()
                    tipo_pedido = str(row['Tipo Pedido']).strip().lower()
                    
                    cliente, _ = Cliente.objects.get_or_create(nombre=cliente_nombre)
                    
                    # Tipo pedido puede ser 'conjunto' o 'separado'
                    is_conjunto = 'conjunto' in tipo_pedido
                    t_pedido = 'conjunto' if is_conjunto else 'separado'
                    
                    # Manejar valores numéricos que puedan venir vacíos (NaN)
                    aporte = Decimal(str(row['Aporte'])) if 'Aporte' in df.columns and pd.notna(row['Aporte']) else Decimal('0')
                    total = Decimal(str(row['Total'])) if 'Total' in df.columns and pd.notna(row['Total']) else Decimal('0')
                    
                    # Buscar si ya existe el pedido para agrupar (en caso de prendas separadas en múltiples filas)
                    pedido, created = PedidoPersonalizado.objects.get_or_create(
                        cliente=cliente,
                        nombre_completo=nombre,
                        gestion=gestion,
                        defaults={
                            'categoria': categoria,
                            'tipo_pedido': t_pedido,
                            'aporte': aporte,
                            'total': total,
                            'estado_pedido': 'registrado'
                        }
                    )
                    
                    # Si creó el pedido y era conjunto o separado, se actualiza
                    if created and is_conjunto:
                        talla = str(row['Talla']).strip() if 'Talla' in df.columns and pd.notna(row['Talla']) else 'M'
                        genero = str(row['Género']).strip().lower() if 'Género' in df.columns and pd.notna(row['Género']) else 'unisex'
                        pedido.talla_conjunto = talla
                        pedido.genero_conjunto = genero
                        pedido.save() # auto-generates items
                        
                    elif not is_conjunto:
                        # Si es separado o agrupando
                        if 'Prenda' in df.columns and pd.notna(row['Prenda']):
                            prenda = str(row['Prenda']).strip().lower()
                            talla = str(row['Talla']).strip() if 'Talla' in df.columns and pd.notna(row['Talla']) else 'M'
                            genero = str(row['Género']).strip().lower() if 'Género' in df.columns and pd.notna(row['Género']) else 'unisex'
                            cantidad = int(row['Cantidad']) if 'Cantidad' in df.columns and pd.notna(row['Cantidad']) else 1
                            
                            ItemPedidoPersonalizado.objects.create(
                                pedido=pedido,
                                tipo_prenda=prenda,
                                talla=talla,
                                genero=genero,
                                cantidad=cantidad
                            )
                            
                messages.success(request, 'Archivo procesado exitosamente.')
                return redirect('pedidos_personalizados:lista')
            except Exception as e:
                messages.error(request, f'Error al procesar archivo: {str(e)}')
    else:
        form = ImportarExcelPersonalizadoForm()
        
    return render(request, 'pedidos_personalizados/importar.html', {'form': form})

@login_required
def exportar_excel(request):
    import io
    from django.http import HttpResponse

    form_filtros = FiltrosPedidoPersonalizadoForm(request.GET)
    pedidos = PedidoPersonalizado.objects.select_related('cliente').all()

    if form_filtros.is_valid():
        buscar = form_filtros.cleaned_data.get('buscar')
        cliente = form_filtros.cleaned_data.get('cliente')
        gestion = form_filtros.cleaned_data.get('gestion')
        categoria = form_filtros.cleaned_data.get('categoria')
        estado_pedido = form_filtros.cleaned_data.get('estado_pedido')
        estado_pago = form_filtros.cleaned_data.get('estado_pago')

        if buscar:
            pedidos = pedidos.filter(nombre_completo__icontains=buscar)
        if cliente:
            pedidos = pedidos.filter(cliente=cliente)
        if gestion:
            pedidos = pedidos.filter(gestion=gestion)
        if categoria:
            pedidos = pedidos.filter(categoria__icontains=categoria)
        if estado_pedido:
            pedidos = pedidos.filter(estado_pedido=estado_pedido)
        if estado_pago:
            pedidos = pedidos.filter(estado_pago=estado_pago)

    data = []
    for p in pedidos:
        base_dict = {
            'Cliente': p.cliente.nombre,
            'Nombre Completo': p.nombre_completo,
            'Gestión': p.gestion,
            'Categoría': p.categoria,
            'Tipo Pedido': p.get_tipo_pedido_display(),
            'Aporte': float(p.aporte) if p.aporte else 0,
            'Saldo': float(p.saldo) if p.saldo else 0,
            'Total': float(p.total) if p.total else 0,
            'Estado Pago': p.get_estado_pago_display(),
            'Estado Pedido': p.get_estado_pedido_display(),
        }
        items = p.items.all()
        if not items:
            # Caso sin items
            base_dict['Prenda'] = ''
            base_dict['Talla'] = ''
            base_dict['Género'] = ''
            base_dict['Cantidad'] = 0
            data.append(base_dict)
        else:
            for item in items:
                row = base_dict.copy()
                row['Prenda'] = item.get_tipo_prenda_display()
                row['Talla'] = item.talla
                row['Género'] = item.get_genero_display()
                row['Cantidad'] = item.cantidad
                data.append(row)

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Pedidos Custom')
    
    output.seek(0)
    response = HttpResponse(
        output.read(), 
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="pedidos_personalizados.xlsx"'
    return response
