"""
Formularios para la gestión de clientes
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Button
from .models import Cliente


class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes"""
    
    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'tipo',
            'nit',
            'contacto_nombre',
            'contacto_cargo',
            'telefono',
            'email',
            'direccion',
            'ciudad',
            'notas',
            'activo'
        ]
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='form-group col-md-6'),
                Column('tipo', css_class='form-group col-md-3'),
                Column('nit', css_class='form-group col-md-3'),
            ),
            Row(
                Column('contacto_nombre', css_class='form-group col-md-6'),
                Column('contacto_cargo', css_class='form-group col-md-6'),
            ),
            Row(
                Column('telefono', css_class='form-group col-md-4'),
                Column('email', css_class='form-group col-md-4'),
                Column('ciudad', css_class='form-group col-md-4'),
            ),
            'direccion',
            'notas',
            'activo',
            Row(
                Column(
                    Submit('submit', 'Guardar', css_class='btn btn-primary'),
                    Button('cancel', 'Cancelar', css_class='btn btn-secondary', 
                           onclick="window.history.back();"),
                    css_class='form-group col-md-12'
                ),
            ),
        )


class ClienteFilterForm(forms.Form):
    """Formulario para filtrar clientes"""
    nombre = forms.CharField(required=False)
    tipo = forms.ChoiceField(
        choices=[('', 'Todos')] + list(Cliente.TIPO_CLIENTE_CHOICES),
        required=False
    )
    ciudad = forms.CharField(required=False)
    activo = forms.ChoiceField(
        choices=[('', 'Todos'), ('true', 'Activo'), ('false', 'Inactivo')],
        required=False
    )