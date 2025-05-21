# carta_digital/forms.py
from django import forms
from django.core.exceptions import ValidationError

class ProductoForm(forms.Form):
    """
    Formulario para validar y limpiar los datos de un producto.
    """
    nombre = forms.CharField(max_length=100, required=True, label="Nombre")
    # Usamos forms.Textarea para que se renderice como un área de texto
    descripcion = forms.CharField(widget=forms.Textarea, required=True, label="Descripción")
    precio = forms.FloatField(min_value=0, required=True, label="Precio")
    # La categoría no se usa en tus JSON de producto, pero la mantengo si la necesitas para el formulario
    # Si no la usas, puedes comentarla o eliminarla.
    # categoria = forms.CharField(max_length=50, required=True, label="Categoría")
    imagen = forms.CharField(max_length=200, required=False, label="Imagen (URL)")

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")
        return precio
