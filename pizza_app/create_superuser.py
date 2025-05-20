import os
import django
from django.contrib.auth import get_user_model

# Asegúrate de que la ruta al archivo de configuración sea correcta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pizza_app.settings')  # Reemplaza 'carta_digital.settings' con la ruta a tu archivo settings.py
django.setup()

User = get_user_model()

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('capricho', 'cristianmarcus34@gmail.com', 'capricho2025')  # Reemplaza con tus datos
    print('Superuser creado exitosamente.')
else:
    print('Ya existe un superusuario.')
