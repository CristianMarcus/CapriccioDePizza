from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
import os
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages



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


import glob

def cargar_todos_los_productos():
    """
    Escanea todos los archivos JSON en la carpeta 'data' y extrae productos
    sin importar su estructura (lista directa o dict con subclaves).
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'carta_digital', 'data')
    productos_por_tipo = {}

    archivos_json = glob.glob(os.path.join(data_dir, '*.json'))

    for archivo in archivos_json:
        tipo = os.path.splitext(os.path.basename(archivo))[0]
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)

            if isinstance(datos, list):
                productos_por_tipo[tipo] = datos

            elif isinstance(datos, dict):
                # Buscar claves que contengan listas de productos
                productos_encontrados = []
                for clave, valor in datos.items():
                    if isinstance(valor, list) and all(isinstance(p, dict) for p in valor):
                        productos_encontrados.extend(valor)
                productos_por_tipo[tipo] = productos_encontrados

        except Exception as e:
            print(f"Error al procesar {archivo}: {e}")
            productos_por_tipo[tipo] = []

    return productos_por_tipo


@login_required
def panel_admin(request):
    """
    Muestra el panel de administración cargando todos los productos desde los archivos JSON.
    """
    productos_por_tipo = cargar_todos_los_productos()

    # Contar cantidad de productos por tipo
    resumen = {tipo: len(productos) for tipo, productos in productos_por_tipo.items()}

    context = {
        'productos_por_tipo': productos_por_tipo,
        'resumen': resumen
    }

    return render(request, 'carta_digital/panel_admin.html', context)


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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'carta_digital', 'data')
    filepath = os.path.join(data_dir, filename)

    key_mapping = {
        'platos_especiales': 'platosEspeciales'
        # Agrega más si necesitas
    }

    if key in key_mapping:
        key = key_mapping[key]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            if key:
                if key in data and isinstance(data[key], list):
                    return data[key]
                else:
                    raise ValueError(f"La clave '{key}' no existe o no contiene una lista en {filename}")
            return data

        raise TypeError(f"El contenido de {filename} no es ni dict ni list")

    except FileNotFoundError:
        print(f"Archivo no encontrado: {filename}")
    except json.JSONDecodeError as e:
        print(f"Error en el JSON {filename}: {e}")
    except ValueError as e:
        print(f"Validación de datos fallida: {e}")
    except Exception as e:
        print(f"Error inesperado en {filename}: {e}")
    return []



@login_required
def agregar_producto(request, tipo):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            precio = float(request.POST.get('precio'))
            imagen = request.POST.get('imagen')

            data = load_json_data(f'{tipo}.json')
            productos = []
            clave_con_lista = None

            if isinstance(data, list):
                productos = data
            elif isinstance(data, dict):
                for clave, lista in data.items():
                    if isinstance(lista, list) and all(isinstance(p, dict) for p in lista):
                        productos = lista
                        clave_con_lista = clave
                        break

            nuevo_id = max((p.get('id', 0) for p in productos), default=0) + 1

            nuevo_producto = {
                'id': nuevo_id,
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'imagen': imagen
            }

            productos.append(nuevo_producto)

            if isinstance(data, dict) and clave_con_lista:
                data[clave_con_lista] = productos
                _guardar_json(tipo, data)
            else:
                _guardar_json(tipo, productos)

            return redirect('mostrar_productos', tipo=tipo)

        except Exception as e:
            print(f"Error al agregar producto: {e}")
            messages.error(request, "Hubo un error al agregar el producto.")

    return render(request, 'carta_digital/agregar_producto.html', {'tipo': tipo})





def eliminar_producto(request, tipo, producto_id):
    data = load_json_data(f'{tipo}.json', tipo)

    # Si el archivo es lista de productos directamente
    if isinstance(data, list):
        productos = data
        nuevos_productos = [p for p in productos if str(p.get('id')) != str(producto_id)]
        if len(productos) == len(nuevos_productos):
            messages.error(request, "Producto no encontrado.")
        else:
            _guardar_json(tipo, nuevos_productos)  # guardamos la lista directamente
            messages.success(request, "Producto eliminado correctamente.")
    
    # Si es un diccionario con clave 'productos'
    elif isinstance(data, dict) and 'productos' in data:
        productos = data['productos']
        nuevos_productos = [p for p in productos if str(p.get('id')) != str(producto_id)]
        if len(productos) == len(nuevos_productos):
            messages.error(request, "Producto no encontrado.")
        else:
            data['productos'] = nuevos_productos
            _guardar_json(tipo, data)
            messages.success(request, "Producto eliminado correctamente.")
    
    else:
        messages.error(request, "Formato de datos no válido.")

    return redirect('mostrar_productos', tipo=tipo)




@login_required
def editar_producto(request, tipo, id_producto):
    data = load_json_data(f'{tipo}.json')  # puede ser lista o dict
    productos = []
    clave_con_lista = None

    if isinstance(data, list):
        productos = data
    elif isinstance(data, dict):
        for clave, lista in data.items():
            if isinstance(lista, list) and all(isinstance(p, dict) for p in lista):
                productos = lista
                clave_con_lista = clave
                break

    producto = None
    if id_producto:
        producto = next((p for p in productos if str(p.get("id")) == str(id_producto)), None)
        if not producto:
            messages.error(request, "Producto no encontrado.")
            return redirect('mostrar_productos', tipo=tipo)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "")
        descripcion = request.POST.get("descripcion", "")
        precio = request.POST.get("precio", "")
        categoria = request.POST.get("categoria", "")
        imagen = request.POST.get("imagen", "")

        if producto:
            # Editar producto existente
            producto.update({
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": float(precio),
                "categoria": categoria,
                "imagen": imagen,
            })
            mensaje = "Producto actualizado correctamente."
        else:
            # Agregar producto nuevo
            nuevo_id = max((p.get("id", 0) for p in productos), default=0) + 1
            nuevo_producto = {
                "id": nuevo_id,
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": float(precio),
                "categoria": categoria,
                "imagen": imagen,
            }
            productos.append(nuevo_producto)
            mensaje = "Producto agregado correctamente."

        # Reconstruye la estructura si era un dict
        if isinstance(data, dict) and clave_con_lista:
            data[clave_con_lista] = productos
            _guardar_json(tipo, data)
        else:
            _guardar_json(tipo, productos)

        messages.success(request, mensaje)
        return redirect('editar_producto', tipo=tipo, id_producto=id_producto if producto else nuevo_id)

    return render(request, "carta_digital/editar_producto.html", {
        "tipo": tipo,
        "producto": producto
    })





def _guardar_json(tipo, data):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'carta_digital', 'data')
    filepath = os.path.join(data_dir, f'{tipo}.json')

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"{filepath} guardado correctamente.")
    except Exception as e:
        print(f"Error al guardar {filepath}: {e}")
