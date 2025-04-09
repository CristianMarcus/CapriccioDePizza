from django.shortcuts import render
import json
import os

def home(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'carta_digital', 'data')

    def load_json_data(filename):
        filepath = os.path.join(data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError as e:
            print(f"Error al leer el archivo {filename}: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error al decodificar el JSON en {filename}: {e}")
            return {}

    empanadas_data = load_json_data('empanadas.json').get('empanadas', [])
    pizzas_data = load_json_data('pizzas.json').get('pizzas', [])
    platos_especiales_raw = load_json_data('platos_especiales.json')
    tartas_data = load_json_data('tartas.json').get('tartas', []) # Si tienes un archivo de tartas

    hamburguesas_data = platos_especiales_raw.get('hamburguesas', [])
    churrasquitos_data = platos_especiales_raw.get('churrasquitos', [])
    promos_data = platos_especiales_raw.get('promos', [])
    combos_data = platos_especiales_raw.get('combos', [])
    platos_especiales_data = platos_especiales_raw.get('platosEspeciales', [])

    context = {
        'empanadas': empanadas_data,
        'pizzas': pizzas_data,
        'platos_especiales': platos_especiales_data,
        'hamburguesas': hamburguesas_data,
        'churrasquitos': churrasquitos_data,
        'promos': promos_data,
        'combos': combos_data,
        'tartas': tartas_data, # Si tienes tartas
    }
    return render(request, 'carta_digital/home.html', context)