from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-panel/', views.panel_admin, name='panel_admin'),

    
    path('productos/<str:tipo>/', views.mostrar_productos, name='mostrar_productos'),
    path('productos/<str:tipo>/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/<str:tipo>/eliminar/<str:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/<str:tipo>/editar/<str:id_producto>/', views.editar_producto, name='editar_producto'),

]