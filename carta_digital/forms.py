# carta_digital/forms.py
from django import forms
from django.core.exceptions import ValidationError

class ProductoForm(forms.Form):
    """
    Formulario para validar y limpiar los datos de un producto.
    """
    nombre = forms.CharField(max_length=100, required=True, label="Nombre")
    descripcion = forms.CharField(widget=forms.Textarea, required=True, label="Descripción")
    precio = forms.FloatField(min_value=0, required=True, label="Precio")
    
    # CAMBIO: De ImageField a FileField para una validación inicial menos estricta
    # La validación real de la imagen se hará en la vista con Pillow
    imagen = forms.FileField(required=False, label="Imagen del Producto", 
                             widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")
        return precio
