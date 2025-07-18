from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cvchat.urls')),     # Rutas principales (login, analizar-cv, etc.)
    path('users/', include('users.urls')),  # Añade esto para que 'register', 'logout' funcionen
]
