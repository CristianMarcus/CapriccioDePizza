# create_superuser.py
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

try:
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("capricho", "admin@email.com", "capricho2025")
        print("Superusuario creado.")
    else:
        print("El superusuario ya existe.")
except IntegrityError as e:
    print(f"Error al crear superusuario: {e}")
