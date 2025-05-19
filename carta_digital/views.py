from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
import os
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout



def home(request):
    """
    Carga y organiza los datos de los productos desde archivos JSON para la página de inicio.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'carta_digital', 'data')

    archivos_lista = {
        'empanadas': 'empanadas.json',
        'pizzas': 'pizzas.json',
        'tartas': 'tartas.json',
    }

    archivos_dict = {
        'platos_especiales': 'platos_especiales.json',
    }

    context = {}

    def cargar_json(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error al cargar {path}: {e}")
            return {}

    # Carga archivos que podrían contener una lista directa o un dict con clave
    for clave, archivo in archivos_lista.items():
        ruta = os.path.join(data_dir, archivo)
        datos = cargar_json(ruta)

        if isinstance(datos, list):
            context[clave] = datos
        elif isinstance(datos, dict):
            context[clave] = datos.get(clave, [])  # busca una clave que coincida con el nombre
        else:
            context[clave] = []

    # Carga archivos con subcategorías (dict de listas)
    for clave_base, archivo in archivos_dict.items():
        ruta = os.path.join(data_dir, archivo)
        datos_dict = cargar_json(ruta)
        if isinstance(datos_dict, dict):
            for subclave, lista in datos_dict.items():
                context[subclave] = lista if isinstance(lista, list) else []

        # Agrega platos_especiales como alias de platosEspeciales si está presente
        if 'platosEspeciales' in datos_dict and isinstance(datos_dict['platosEspeciales'], list):
            context['platos_especiales'] = datos_dict['platosEspeciales']


    # Combina todos los productos cargados que sean listas
    todos_los_productos = []
    for categoria, productos in context.items():
        if isinstance(productos, list):
            todos_los_productos.extend(productos)
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
            login(request, user)
            return redirect('panel_admin')
    else:
        form = AuthenticationForm()
    return render(request, 'carta_digital/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Cierra la sesión del usuario y lo redirige a la página de inicio de sesión.
    """
    logout(request)
    return redirect('login')

@login_required
def panel_admin(request):
    """
    Muestra el panel de administración.
    """
    tipos = [
        'empanadas', 'pizzas', 'tartas',
        'platos_especiales',
        'hamburguesas', 'churrasquitos', 'promos', 'combos'
    ]
    return render(request, 'carta_digital/panel_admin.html', {'tipos': tipos})

@login_required
def mostrar_productos(request, tipo):
    """
    Muestra la lista de productos para un tipo específico.
    """
    # Mapea el tipo de la URL al nombre real del tipo de producto
    tipo_real = tipo  # Usa directamente el valor de 'tipo'
    productos_json = load_json_data(f'{tipo_real}.json', tipo_real) #carga el json usando el tipo
    productos = productos_json

    context = {
        'productos': productos,
        'tipo': tipo,
    }
    return render(request, 'carta_digital/lista_productos.html', context)

def load_json_data(filename, key=None):
    """
    Función para cargar datos JSON desde un archivo.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'carta_digital', 'data')
    filepath = os.path.join(data_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data[key] if key else data #devuelve los datos filtrados por la key
    except FileNotFoundError:
        print(f"Archivo no encontrado: {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error al decodificar JSON: {filepath}")
        return []

@login_required
def agregar_producto(request, tipo):
    """
    Permite agregar un nuevo producto al archivo JSON.
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = float(request.POST.get('precio'))
        categoria = request.POST.get('categoria')
        imagen = request.POST.get('imagen')

        # Determina el ID del nuevo producto (esto es importante)
        productos = load_json_data(f'{tipo}.json', tipo)
        nuevo_producto_id = max((p['id'] for p in productos), default=0) + 1

        nuevo_producto = {
            'id': nuevo_producto_id,
            'nombre': nombre,
            'descripcion': descripcion,
            'precio': precio,
            'imagen': imagen
        }

        # Carga el JSON, agrega el nuevo producto, y guarda.
        productos_json = load_json_data(f'{tipo}.json')
        productos_json[tipo].append(nuevo_producto) #agrega el producto a la lista correspondiente
        _guardar_json(tipo, productos_json) #guarda los cambios

        return redirect('mostrar_productos', tipo=tipo)

    return render(request, 'carta_digital/agregar_producto.html', {'tipo': tipo})


@login_required
def eliminar_producto(request, tipo, id_producto):
    """
    Elimina un producto existente del archivo JSON.
    """
    productos_json = load_json_data(f'{tipo}.json')
    productos_json[tipo] = [p for p in productos_json[tipo] if p['id'] != int(id_producto)] #filtra el producto por id
    _guardar_json(tipo, productos_json)
    return redirect('mostrar_productos', tipo=tipo)



@login_required
def editar_producto(request, tipo, id_producto):
    """
    Permite editar un producto existente.
    """
    productos_json = load_json_data(f'{tipo}.json', tipo)
    producto = next((p for p in productos_json if p['id'] == int(id_producto)), None)

    if request.method == 'POST':
        nuevos_datos = {
            'nombre': request.POST.get('nombre'),
            'descripcion': request.POST.get('descripcion'),
            'precio': float(request.POST.get('precio')),
            'imagen': request.POST.get('imagen')
        }
        for p in productos_json:
            if p['id'] == int(id_producto):
                p.update(nuevos_datos) #actualiza los datos del producto
                break
        _guardar_json(tipo, productos_json)
        return redirect('mostrar_productos', tipo=tipo)

    return render(request, 'carta_digital/editar_producto.html', {'producto': producto, 'tipo': tipo})


def _guardar_json(tipo, data):
    """
    Función interna para guardar datos JSON a un archivo.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'carta_digital', 'data')
    filepath = os.path.join(data_dir, f'{tipo}.json')
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error al guardar JSON en {filepath}: {e}")
