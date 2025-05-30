from django.urls import path
from .views import analizar_cv, CVAPIView

urlpatterns = [
    path('', analizar_cv, name='analizar_cv'),
    path('api/cvs/', CVAPIView.as_view(), name='cv_list_create'),
    path('api/cvs/<int:pk>/', CVAPIView.as_view(), name='cv_detail'),
]
