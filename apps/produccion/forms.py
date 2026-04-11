"""
Formularios para el módulo de producción
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Button
from .models import OrdenProduccion, MateriaPrimaRequerida


class OrdenProduccionForm(forms.ModelForm):
    """Formulario para crear y editar órdenes de producción"""
    
    class Meta:
        model = OrdenProduccion
        fields = [
            'pedidos',
            'gestion',
            'estado',
            'fecha_inicio',
            'fecha_fin_estimada',
            'notas'
        ]
        widgets = {
            'pedidos': forms.CheckboxSelectMultiple(),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_estimada': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar pedidos que no tienen orden de producción asignada
        from apps.pedidos.models import Pedido
        self.fields['pedidos'].queryset = Pedido.objects.filter(
            estado__in=['pendiente', 'en_proceso']
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'pedidos',
            Row(
                Column('gestion', css_class='form-group col-md-4'),
                Column('estado', css_class='form-group col-md-4'),
            ),
            Row(
                Column('fecha_inicio', css_class='form-group col-md-4'),
                Column('fecha_fin_estimada', css_class='form-group col-md-4'),
            ),
            'notas',
            Row(
                Column(
                    Submit('submit', 'Guardar Orden', css_class='btn btn-primary'),
                    Button('cancel', 'Cancelar', css_class='btn btn-secondary',
                           onclick="window.history.back();"),
                    css_class='form-group col-md-12'
                ),
            ),
        )


class MateriaPrimaForm(forms.ModelForm):
    """Formulario para registrar materia prima requerida"""
    
    class Meta:
        model = MateriaPrimaRequerida
        fields = [
            'tipo_material',
            'descripcion',
            'cantidad_requerida',
            'unidad_medida',
            'cantidad_comprada',
            'notas'
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('tipo_material', css_class='form-group col-md-4'),
                Column('descripcion', css_class='form-group col-md-8'),
            ),
            Row(
                Column('cantidad_requerida', css_class='form-group col-md-4'),
                Column('unidad_medida', css_class='form-group col-md-4'),
                Column('cantidad_comprada', css_class='form-group col-md-4'),
            ),
            'notas',
            Row(
                Column(
                    Submit('submit', 'Guardar', css_class='btn btn-primary'),
                    css_class='form-group col-md-12'
                ),
            ),
        )


class GenerarOrdenProduccionForm(forms.Form):
    """Formulario para generar automáticamente una orden de producción"""
    pedidos = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label='Seleccionar Pedidos'
    )
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha de Inicio'
    )
    fecha_fin_estimada = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha de Fin Estimada'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.pedidos.models import Pedido
        self.fields['pedidos'].queryset = Pedido.objects.filter(
            estado__in=['pendiente', 'en_proceso']
        )
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'pedidos',
            Row(
                Column('fecha_inicio', css_class='form-group col-md-6'),
                Column('fecha_fin_estimada', css_class='form-group col-md-6'),
            ),
            Submit('submit', 'Generar Orden de Producción', css_class='btn btn-success'),
        )