"""
Formularios para la gestión de pedidos
"""
from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Button, HTML
from .models import Pedido, ItemPedido, ConjuntoPedido, ImportacionExcel


class PedidoForm(forms.ModelForm):
    """Formulario para crear y editar pedidos"""
    
    class Meta:
        model = Pedido
        fields = [
            'cliente',
            'gestion',
            'tipo_pedido',
            'estado',
            'fecha_entrega',
            'notas'
        ]
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('cliente', css_class='form-group col-md-6'),
                Column('gestion', css_class='form-group col-md-3'),
                Column('tipo_pedido', css_class='form-group col-md-3'),
            ),
            Row(
                Column('estado', css_class='form-group col-md-4'),
                Column('fecha_entrega', css_class='form-group col-md-4'),
            ),
            'notas',
            Row(
                Column(
                    Submit('submit', 'Guardar Pedido', css_class='btn btn-primary'),
                    Button('cancel', 'Cancelar', css_class='btn btn-secondary',
                           onclick="window.history.back();"),
                    css_class='form-group col-md-12'
                ),
            ),
        )


class ItemPedidoForm(forms.ModelForm):
    """Formulario para agregar ítems individuales a un pedido"""
    
    class Meta:
        model = ItemPedido
        fields = ['tipo_prenda', 'genero', 'talla', 'cantidad', 'notas']
        widgets = {
            'notas': forms.TextInput(attrs={'placeholder': 'Notas opcionales'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class ConjuntoPedidoForm(forms.ModelForm):
    """Formulario para agregar conjuntos a un pedido"""
    
    class Meta:
        model = ConjuntoPedido
        fields = ['genero', 'talla', 'cantidad', 'notas']
        widgets = {
            'notas': forms.TextInput(attrs={'placeholder': 'Notas opcionales'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class ImportarExcelForm(forms.ModelForm):
    """Formulario para importar archivos Excel"""
    
    preview_mode = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = ImportacionExcel
        fields = ['archivo']
        widgets = {
            'archivo': forms.FileInput(attrs={'accept': '.xlsx,.xls'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'archivo',
            'preview_mode',
            HTML("""
                <div class="alert alert-info">
                    <strong>Formato esperado:</strong>
                    <ul class="mb-0">
                        <li>Columna A: Tipo de Prenda (Chamarra, Buso, Polera, Short)</li>
                        <li>Columna B: Género (Varón, Mujer, Unisex)</li>
                        <li>Columna C: Talla (4, 6, 8, 10, 12, 14, 16, S, M, L, XL)</li>
                        <li>Columna D: Cantidad</li>
                    </ul>
                </div>
            """),
            Submit('submit', 'Vista Previa', css_class='btn btn-primary'),
        )

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            extension = archivo.name.split('.')[-1].lower()
            if extension not in ['xlsx', 'xls']:
                raise forms.ValidationError('El archivo debe ser de tipo Excel (.xlsx o .xls)')
        return archivo


class ConfirmarImportacionForm(forms.Form):
    """Formulario para confirmar la importación de datos de Excel"""
    importacion_id = forms.IntegerField(widget=forms.HiddenInput())
    confirmar = forms.BooleanField(
        required=True,
        label='Confirmo que los datos son correctos y deseo importarlos'
    )


class PedidoFilterForm(forms.Form):
    """Formulario para filtrar pedidos"""
    cliente = forms.CharField(required=False, label='Cliente')
    gestion = forms.IntegerField(required=False, label='Gestión/Año')
    estado = forms.ChoiceField(
        choices=[('', 'Todos')] + list(Pedido.ESTADO_CHOICES),
        required=False
    )
    tipo_pedido = forms.ChoiceField(
        choices=[('', 'Todos')] + list(Pedido.TIPO_PEDIDO_CHOICES),
        required=False,
        label='Tipo de Pedido'
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Desde'
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Hasta'
    )


# Formsets para ítems dinámicos
ItemPedidoFormSet = inlineformset_factory(
    Pedido,
    ItemPedido,
    form=ItemPedidoForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)

ConjuntoPedidoFormSet = inlineformset_factory(
    Pedido,
    ConjuntoPedido,
    form=ConjuntoPedidoForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False
)