from django.urls import path
from cvchat.views import register_view, login_view, logout_view, analizar_cv, CVAPIView
from . import views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('analizar-cv/', analizar_cv, name='analizar_cv'),
    path('historial/', views.historial_cvs, name='historial_cvs'),
    path('api/cv/', CVAPIView.as_view(), name='cv_api'),
]
