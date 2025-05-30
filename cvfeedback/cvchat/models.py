# cvchat/models.py
from django.db import models
from django.contrib.auth.models import User  # Importa el modelo de usuario

class UploadedCV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.file.name} ({self.user.username})"
