import json
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class GestionCarta:
    data_dir = os.path.join(settings.BASE_DIR, 'carta_digital', 'data')

    @staticmethod
    def _get_path(tipo):
        return os.path.join(GestionCarta.data_dir, f"{tipo}.json")

    @staticmethod
    def _tipo_real(tipo):
        # Si es una subcategoría de platos especiales, el archivo es 'platos_especiales.json'
        if tipo in ['hamburguesas', 'churrasquitos', 'promos', 'combos', 'platosEspeciales']:
            return 'platos_especiales'
        return tipo

    @staticmethod
    def cargar_productos(tipo, subcategoria=None):
        tipo_real = GestionCarta._tipo_real(tipo)
        path = GestionCarta._get_path(tipo_real)

        if not os.path.exists(path):
            logger.warning(f"Archivo no encontrado para tipo {tipo_real} en {path}")
            return [] if subcategoria else {}

        try:
            with open(path, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error cargando {tipo_real}: {e}")
            return [] if subcategoria else {}

        if subcategoria:
            # Si se pide una subcategoría, extraemos solo esa lista
            if isinstance(datos, dict):
                productos = datos.get(subcategoria, [])
                if isinstance(productos, list):
                    return productos
                else:
                    logger.warning(f"Subcategoría {subcategoria} no es una lista válida.")
                    return []
            else:
                logger.warning(f"Datos para {tipo_real} no es dict, no hay subcategorías.")
                return []

        return datos

    @staticmethod
    def guardar_productos(tipo, productos, subcategoria=None):
        tipo_real = GestionCarta._tipo_real(tipo)
        path = GestionCarta._get_path(tipo_real)

        datos = {}
        if subcategoria:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as archivo:
                        datos = json.load(archivo)
                except Exception as e:
                    logger.error(f"Error cargando datos para guardar productos: {e}")
                    datos = {}
            datos[subcategoria] = productos
        else:
            datos = productos

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error guardando productos en {path}: {e}")

    @staticmethod
    def _generar_nuevo_id(productos):
        if not productos:
            return 1
        try:
            max_id = max(int(p['id']) for p in productos if 'id' in p)
            return max_id + 1
        except Exception as e:
            logger.error(f"Error generando nuevo ID: {e}")
            return len(productos) + 1

    @staticmethod
    def agregar_producto(tipo, producto):
        tipo_real = GestionCarta._tipo_real(tipo)

        if tipo_real == 'platos_especiales':
            productos_json = GestionCarta.cargar_productos(tipo_real)
            productos = productos_json.get(tipo, [])
            nuevo_id = GestionCarta._generar_nuevo_id(productos)
            producto['id'] = nuevo_id
            productos.append(producto)
            productos_json[tipo] = productos
            GestionCarta.guardar_productos(tipo_real, productos_json)
        else:
            productos = GestionCarta.cargar_productos(tipo_real)
            nuevo_id = GestionCarta._generar_nuevo_id(productos)
            producto['id'] = nuevo_id
            productos.append(producto)
            GestionCarta.guardar_productos(tipo_real, productos)

    @staticmethod
    def eliminar_producto(tipo, id_producto):
        tipo_real = GestionCarta._tipo_real(tipo)
        id_producto_str = str(id_producto)

        if tipo_real == 'platos_especiales':
            productos_json = GestionCarta.cargar_productos(tipo_real)
            productos = productos_json.get(tipo, [])
            nuevos_productos = [p for p in productos if str(p.get('id')) != id_producto_str]
            if len(productos) == len(nuevos_productos):
                logger.warning(f"No se encontró producto con id {id_producto} en subcategoría {tipo}")
                return False
            productos_json[tipo] = nuevos_productos
            GestionCarta.guardar_productos(tipo_real, productos_json)
            return True
        else:
            productos = GestionCarta.cargar_productos(tipo_real)
            nuevos_productos = [p for p in productos if str(p.get('id')) != id_producto_str]
            if len(productos) == len(nuevos_productos):
                logger.warning(f"No se encontró producto con id {id_producto} en tipo {tipo}")
                return False
            GestionCarta.guardar_productos(tipo_real, nuevos_productos)
            return True

    @staticmethod
    def actualizar_producto(tipo, id_producto, nuevos_datos):
        tipo_real = GestionCarta._tipo_real(tipo)
        id_producto_str = str(id_producto)

        if tipo_real == 'platos_especiales':
            productos_json = GestionCarta.cargar_productos(tipo_real)
            productos = productos_json.get(tipo, [])
            for producto in productos:
                if str(producto.get('id')) == id_producto_str:
                    producto.update(nuevos_datos)
                    break
            else:
                logger.warning(f"Producto con ID {id_producto} no encontrado en {tipo}")
                return False
            productos_json[tipo] = productos
            GestionCarta.guardar_productos(tipo_real, productos_json)
            return True
        else:
            productos = GestionCarta.cargar_productos(tipo_real)
            for producto in productos:
                if str(producto.get('id')) == id_producto_str:
                    producto.update(nuevos_datos)
                    break
            else:
                logger.warning(f"Producto con ID {id_producto} no encontrado en {tipo}")
                return False
            GestionCarta.guardar_productos(tipo_real, productos)
            return True
