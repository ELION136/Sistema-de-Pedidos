from django import forms
from .models import PedidoPersonalizado, ItemPedidoPersonalizado

class PedidoPersonalizadoForm(forms.ModelForm):
    class Meta:
        model = PedidoPersonalizado
        fields = [
            'cliente', 'nombre_completo', 'gestion', 'categoria', 
            'tipo_pedido', 'talla_conjunto', 'genero_conjunto',
            'aporte', 'total', 'estado_pago', 'tipo_pago', 'estado_pedido'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'gestion': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_pedido': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_pedido_pers'}),
            'talla_conjunto': forms.Select(attrs={'class': 'form-select'}),
            'genero_conjunto': forms.Select(attrs={'class': 'form-select'}),
            'aporte': forms.NumberInput(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado_pago': forms.Select(attrs={'class': 'form-select'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-select'}),
            'estado_pedido': forms.Select(attrs={'class': 'form-select'}),
        }

class ItemPedidoPersonalizadoForm(forms.ModelForm):
    class Meta:
        model = ItemPedidoPersonalizado
        fields = ['tipo_prenda', 'genero', 'talla', 'cantidad']
        widgets = {
            'tipo_prenda': forms.Select(attrs={'class': 'form-select'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'talla': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class FiltrosPedidoPersonalizadoForm(forms.Form):
    buscar = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar beneficiario...'}))
    cliente = forms.ModelChoiceField(queryset=None, required=False, empty_label="Todos los clientes", widget=forms.Select(attrs={'class': 'form-select'}))
    gestion = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Año'}))
    categoria = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoría'}))
    estado_pedido = forms.ChoiceField(choices=[('', 'Todos')] + PedidoPersonalizado.ESTADO_PEDIDO_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    estado_pago = forms.ChoiceField(choices=[('', 'Todos')] + PedidoPersonalizado.ESTADO_PAGO_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.clientes.models import Cliente
        self.fields['cliente'].queryset = Cliente.objects.all()

class ImportarExcelPersonalizadoForm(forms.Form):
    archivo = forms.FileField(
        label='Archivo Excel (.xlsx)',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'})
    )
