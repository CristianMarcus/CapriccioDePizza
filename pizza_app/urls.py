from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('carta_digital.urls')),  # <-- Cambia a solo 'carta_digital.urls'
]