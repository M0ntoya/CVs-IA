# cvchat/urls.py
from django.urls import path
from .views import CVAPIView

urlpatterns = [
    path('cv/', CVAPIView.as_view()),
    path('cv/<int:pk>/', CVAPIView.as_view()),
]
