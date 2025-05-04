#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instalar dependencias
pip install --no-cache-dir -r requirements.txt

# Convertir archivos estáticos
python manage.py collectstatic --no-input

# Aplicar migraciones (no usas BD ahora, pero lo dejamos por si acaso)
python manage.py migrate || echo "No hay migraciones necesarias"
