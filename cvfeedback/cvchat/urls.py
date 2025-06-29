from django.urls import path
from . import views

urlpatterns = [
    # API REST para CVs, que usan los tests y clientes AJAX
    path('analizar-cv/', views.CVAPIView.as_view(), name='analizar_cv'),

    # Vista para mostrar la página HTML con el formulario para subir CV
    path('analizar-cv/pagina/', views.analizar_cv, name='analizar_cv_page'),

    # URLs para detalle y manejo individual de CVs vía API REST
    path('api/cv/<int:pk>/', views.CVAPIView.as_view(), name='cv_api_detail'),
]
