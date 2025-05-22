# carta_digital/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import json
import os
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import Http404
import re # Para expresiones regulares en la generación de IDs
from django.conf import settings # Importar settings para MEDIA_ROOT

# Importa el formulario
from .forms import ProductoForm


# --- Funciones auxiliares para la gestión de JSON ---

def _get_filepath(tipo_archivo):
    """Obtiene la ruta completa de un archivo JSON en la carpeta 'data'."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'carta_digital', 'data')
    return os.path.join(data_dir, f'{tipo_archivo}.json')

def load_json_data(file_base_name, key_in_json=None):
    """
    Carga datos JSON desde un archivo.
    Si key_in_json es None, devuelve el contenido completo (dict o list).
    Si key_in_json es una cadena, intenta extraer la lista asociada a esa clave.
    """
    filepath = _get_filepath(file_base_name)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data is None:
            print(f"Advertencia: El archivo {filepath} está vacío o contiene null.")
            return []

        if key_in_json:
            if isinstance(data, dict):
                result = data.get(key_in_json, [])
                if not isinstance(result, list):
                    print(f"Advertencia: La clave '{key_in_json}' en {filepath} no contiene una lista. Devolviendo [].")
                    return []
                return result
            else:
                print(f"Advertencia: Se proporcionó la clave '{key_in_json}', pero {filepath} no es un diccionario. Devolviendo [].")
                return []
        else:
            return data # Devuelve el contenido completo (lista o dict)

    except FileNotFoundError:
        print(f"Error: Archivo no encontrado: {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Error al decodificar JSON en {filepath}.")
        return []
    except Exception as e:
        print(f"Error inesperado al procesar {filepath}: {e}")
        return []


def _guardar_json(file_base_name, data_to_save, key_in_json=None):
    """
    Guarda datos JSON en un archivo.
    Si key_in_json es una cadena, asume que data_to_save es una lista que
    debe ser insertada en el diccionario existente bajo esa clave.
    Si key_in_json es None, data_to_save se guarda directamente.
    """
    filepath = _get_filepath(file_base_name)
    
    if key_in_json:
        # Cargar el diccionario completo, actualizar la lista y guardar
        full_data = load_json_data(file_base_name) # Carga el diccionario completo
        if isinstance(full_data, dict):
            full_data[key_in_json] = data_to_save
            data_to_dump = full_data
        else:
            print(f"Error: El archivo {file_base_name}.json no es un diccionario, no se puede usar key_in_json.")
            return # No se puede guardar en la estructura esperada
    else:
        data_to_dump = data_to_save # Guardar la lista/diccionario directamente

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_dump, f, indent=4, ensure_ascii=False)
        print(f"{filepath} guardado correctamente.")
    except Exception as e:
        print(f"Error al guardar {filepath}: {e}")


def _generate_new_id(current_products, prefix):
    """
    Genera un nuevo ID único de tipo string con un prefijo.
    Ej: "emp1", "piz2", "hamb3".
    """
    max_numeric_id = 0
    for p in current_products:
        p_id = str(p.get('id', ''))
        if p_id.startswith(prefix):
            try:
                numeric_part = int(re.search(r'\d+', p_id[len(prefix):]).group())
                max_numeric_id = max(max_numeric_id, numeric_part)
            except (ValueError, AttributeError):
                continue # Ignorar IDs mal formados o sin parte numérica
        elif re.fullmatch(r'\d+', p_id): # Si es un ID puramente numérico (como en tartas.json)
             try:
                max_numeric_id = max(max_numeric_id, int(p_id))
             except ValueError:
                pass

    return f"{prefix}{max_numeric_id + 1}"

def _handle_uploaded_image(image_file):
    """
    Guarda un archivo de imagen subido en MEDIA_ROOT y devuelve su URL relativa.
    """
    if not image_file:
        return None
    
    # Crea el directorio media si no existe
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    # Define la ruta completa donde se guardará el archivo
    file_path = os.path.join(settings.MEDIA_ROOT, image_file.name)
    
    # Escribe el archivo en el disco
    with open(file_path, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)
    
    # Devuelve la URL relativa para almacenar en el JSON
    return os.path.join(settings.MEDIA_URL, image_file.name)


# Mapeo de tipos de URL a configuraciones de JSON
# Esto centraliza la lógica de qué archivo y qué clave usar para cada "tipo"
JSON_CONFIG = {
    'empanadas': {'file': 'empanadas', 'key': None, 'prefix': 'emp'}, # key es None porque es una lista directa
    'pizzas': {'file': 'pizzas', 'key': 'pizzas', 'prefix': 'piz'},
    'tartas': {'file': 'tartas', 'key': None, 'prefix': 'tar'}, # key es None porque es una lista directa
    'platosEspeciales': {'file': 'platos_especiales', 'key': 'platosEspeciales', 'prefix': 'pla'},
    'hamburguesas': {'file': 'platos_especiales', 'key': 'hamburguesas', 'prefix': 'hamb'},
    'churrasquitos': {'file': 'platos_especiales', 'key': 'churrasquitos', 'prefix': 'churra'},
    'promos': {'file': 'platos_especiales', 'key': 'promos', 'prefix': 'promo'},
    'combos': {'file': 'platos_especiales', 'key': 'combos', 'prefix': 'combo'},
}


# --- Vistas de la aplicación ---

def home(request):
    """
    Carga y organiza los datos de los productos desde archivos JSON para la página de inicio.
    """
    context = {}
    todos_los_productos = []

    for tipo_url, config in JSON_CONFIG.items():
        # Para las categorías que están dentro de platos_especiales.json,
        # necesitamos cargar el archivo 'platos_especiales' y luego la clave específica.
        if config['file'] == 'platos_especiales':
            productos = load_json_data(config['file'], config['key'])
        else:
            # Para los archivos JSON que son listas directas, la clave es None
            productos = load_json_data(config['file'], config['key'])
        
        # Asegurarse de que el tipo de URL se mapee al contexto correcto
        context[tipo_url] = productos
        todos_los_productos.extend(productos)
    
    # Asegurarse de que 'platos_especiales' en el contexto se refiera a 'platosEspeciales' del JSON
    # Esto es para compatibilidad con tu home.html
    context['platos_especiales'] = context.get('platosEspeciales', [])

    context['todos_los_productos'] = todos_los_productos

    return render(request, 'carta_digital/home.html', context)


def login_view(request):
    """
    Muestra y procesa el formulario de inicio de sesión.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Limpiar cualquier mensaje existente de solicitudes/sesiones anteriores.
            storage = messages.get_messages(request)
            for _ in storage:
                pass
            storage.used = True

            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}!')
            return redirect('panel_admin')
        else:
            messages.error(request, 'Error al iniciar sesión. Por favor, verifica tus credenciales.')
    else:
        form = AuthenticationForm()
    return render(request, 'carta_digital/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Cierra la sesión del usuario y lo redirige a la página de inicio de sesión.
    """
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('home')


@login_required
def panel_admin(request):
    """
    Muestra el panel de administración.
    """
    productos_por_tipo = {}
    for tipo_url, config in JSON_CONFIG.items():
        # Carga los productos usando la configuración definida
        productos = load_json_data(config['file'], config['key'])
        productos_por_tipo[tipo_url] = productos

    resumen = {tipo: len(productos) for tipo, productos in productos_por_tipo.items()}

    context = {
        'productos_por_tipo': productos_por_tipo,
        'resumen': resumen,
        'tipos': JSON_CONFIG.keys() # Pasar todas las claves de JSON_CONFIG para el template
    }

    return render(request, 'carta_digital/panel_admin.html', context)


@login_required
def mostrar_productos(request, tipo):
    """
    Muestra la lista de productos para un tipo específico.
    """
    config = JSON_CONFIG.get(tipo)
    if not config:
        raise Http404(f"Tipo de producto '{tipo}' no válido.")

    productos = load_json_data(config['file'], config['key'])

    context = {
        'productos': productos,
        'tipo': tipo,
    }
    return render(request, 'carta_digital/lista_productos.html', context)


@login_required
def agregar_producto(request, tipo):
    """
    Permite agregar un nuevo producto al archivo JSON.
    """
    config = JSON_CONFIG.get(tipo)
    if not config:
        messages.error(request, f"Tipo de producto '{tipo}' no válido para agregar.")
        return redirect('panel_admin')

    if request.method == 'POST':
        # CAMBIO: Pasar request.FILES al formulario
        form = ProductoForm(request.POST, request.FILES) 
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            descripcion = form.cleaned_data['descripcion']
            precio = form.cleaned_data['precio']
            
            # CAMBIO: Manejar la subida de la imagen
            imagen_file = form.cleaned_data.get('imagen')
            imagen_url = _handle_uploaded_image(imagen_file) if imagen_file else ""

            # Cargar el contenido completo del archivo JSON (lista o dict)
            full_data = load_json_data(config['file'])
            
            # Obtener la lista de productos a la que se agregará el nuevo producto
            if config['key']:
                if isinstance(full_data, dict):
                    productos_list = full_data.get(config['key'], [])
                else:
                    productos_list = []
            else:
                productos_list = full_data if isinstance(full_data, list) else []

            # Generar el nuevo ID
            new_id = _generate_new_id(productos_list, config['prefix'])

            nuevo_producto = {
                'id': new_id,
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'imagen': imagen_url # Guardar la URL relativa de la imagen
            }

            productos_list.append(nuevo_producto)

            # Guardar el JSON completo de vuelta
            _guardar_json(config['file'], productos_list, config['key'])

            messages.success(request, 'Producto agregado con éxito.')
            return redirect('mostrar_productos', tipo=tipo)
        else:
            messages.error(request, 'Error al agregar producto. Por favor, revisa los datos.')
            return render(request, 'carta_digital/agregar_producto.html', {'tipo': tipo, 'form': form})
    else:
        form = ProductoForm()
    return render(request, 'carta_digital/agregar_producto.html', {'tipo': tipo, 'form': form})


@login_required
def eliminar_producto(request, tipo, id_producto):
    """
    Elimina un producto existente del archivo JSON.
    """
    config = JSON_CONFIG.get(tipo)
    if not config:
        messages.error(request, f"Tipo de producto '{tipo}' no válido para eliminar.")
        return redirect('panel_admin')

    productos_list = load_json_data(config['file'], config['key'])
    
    initial_len = len(productos_list)
    productos_list_filtered = [p for p in productos_list if str(p.get('id')) != str(id_producto)]

    if len(productos_list_filtered) < initial_len:
        _guardar_json(config['file'], productos_list_filtered, config['key'])
        messages.success(request, 'Producto eliminado con éxito.')
    else:
        messages.error(request, 'Producto no encontrado.')

    return redirect('mostrar_productos', tipo=tipo)


@login_required
def editar_producto(request, tipo, id_producto):
    """
    Permite editar un producto existente.
    """
    config = JSON_CONFIG.get(tipo)
    if not config:
        raise Http404(f"Tipo de producto '{tipo}' no válido para editar.")

    productos_list = load_json_data(config['file'], config['key'])
    
    producto_a_editar = next((p for p in productos_list if str(p.get('id')) == str(id_producto)), None)

    if not producto_a_editar:
        raise Http404(f"Producto con ID '{id_producto}' no encontrado en la categoría '{tipo}'.")

    if request.method == 'POST':
        # CAMBIO: Pasar request.FILES al formulario para la edición
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            nuevos_datos = {
                'nombre': form.cleaned_data['nombre'],
                'descripcion': form.cleaned_data['descripcion'],
                'precio': form.cleaned_data['precio'],
            }

            # CAMBIO: Manejar la subida de la nueva imagen o mantener la existente
            imagen_file = form.cleaned_data.get('imagen')
            if imagen_file:
                nuevos_datos['imagen'] = _handle_uploaded_image(imagen_file)
            elif 'imagen-clear' in request.POST and request.POST['imagen-clear'] == 'on':
                # Si se marcó la casilla "Clear" para la imagen
                nuevos_datos['imagen'] = '' # Vaciar la URL de la imagen
            else:
                # Mantener la imagen existente si no se subió una nueva y no se marcó "Clear"
                nuevos_datos['imagen'] = producto_a_editar.get('imagen', '')

            # Actualizar el producto en la lista referenciada
            for p in productos_list:
                if str(p.get('id')) == str(id_producto):
                    p.update(nuevos_datos)
                    break
            
            _guardar_json(config['file'], productos_list, config['key'])

            messages.success(request, 'Producto actualizado con éxito.')
            return redirect('mostrar_productos', tipo=tipo)
        else:
            messages.error(request, 'Error al actualizar el producto. Por favor, revisa los datos.')
            return render(request, 'carta_digital/editar_producto.html', {'form': form, 'tipo': tipo, 'producto': producto_a_editar})
    else:
        # Inicializar el formulario con los datos actuales del producto
        form = ProductoForm(initial=producto_a_editar)
    
    return render(request, 'carta_digital/editar_producto.html', {'form': form, 'tipo': tipo, 'producto': producto_a_editar})

