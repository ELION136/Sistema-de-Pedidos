"""
Vistas para la gestión de clientes
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Cliente
from .forms import ClienteForm, ClienteFilterForm


@login_required
def lista_clientes(request):
    """Vista para listar todos los clientes con filtros"""
    form_filtro = ClienteFilterForm(request.GET or None)
    clientes = Cliente.objects.all()
    
    # Aplicar filtros
    if form_filtro.is_valid():
        data = form_filtro.cleaned_data
        
        if data.get('nombre'):
            clientes = clientes.filter(nombre__icontains=data['nombre'])
        
        if data.get('tipo'):
            clientes = clientes.filter(tipo=data['tipo'])
        
        if data.get('ciudad'):
            clientes = clientes.filter(ciudad__icontains=data['ciudad'])
        
        if data.get('activo'):
            activo = data['activo'] == 'true'
            clientes = clientes.filter(activo=activo)
    
    # Paginación
    paginator = Paginator(clientes.order_by('nombre'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form_filtro': form_filtro,
        'total_clientes': clientes.count(),
    }
    return render(request, 'clientes/lista.html', context)


@login_required
def detalle_cliente(request, pk):
    """Vista para ver el detalle de un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    context = {
        'cliente': cliente,
        'pedidos': cliente.pedidos.all()[:10],
        'total_pedidos': cliente.get_pedidos_count(),
        'pedidos_activos': cliente.get_pedidos_activos_count(),
    }
    return render(request, 'clientes/detalle.html', context)


@login_required
def crear_cliente(request):
    """Vista para crear un nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente "{cliente.nombre}" creado exitosamente.')
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Cliente',
    }
    return render(request, 'clientes/formulario.html', context)


@login_required
def editar_cliente(request, pk):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente "{cliente.nombre}" actualizado exitosamente.')
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
        'titulo': 'Editar Cliente',
    }
    return render(request, 'clientes/formulario.html', context)


@login_required
def eliminar_cliente(request, pk):
    """Vista para eliminar (desactivar) un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        cliente.activo = False
        cliente.save()
        messages.success(request, f'Cliente "{cliente.nombre}" desactivado exitosamente.')
        return redirect('clientes:lista')
    
    context = {
        'cliente': cliente,
    }
    return render(request, 'clientes/confirmar_eliminar.html', context)


@login_required
def buscar_clientes_ajax(request):
    """Vista AJAX para búsqueda de clientes en tiempo real"""
    query = request.GET.get('q', '')
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=query) | Q(nit__icontains=query),
        activo=True
    )[:10]
    
    resultados = [
        {
            'id': c.id,
            'nombre': c.nombre,
            'ciudad': c.ciudad,
        }
        for c in clientes
    ]
    
    from django.http import JsonResponse
    return JsonResponse({'clientes': resultados})