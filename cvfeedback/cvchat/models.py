
from django.db import models
from django.contrib.auth.models import User  # Importa el modelo de usuario

class AuditLog(models.Model):
    event_type = models.CharField(max_length=255)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class UploadedCV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación con el usuario
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"{self.file.name} ({self.user.username})"

class HistorialCV(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    archivo_pdf = models.FileField(upload_to='cvs/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=20, default="1.0")
    estado = models.CharField(max_length=50, default="Analizado")
    recomendaciones = models.TextField(blank=True)

    def __str__(self):
        return f"CV de {self.usuario.username} ({self.fecha_subida.strftime('%d/%m/%Y %H:%M')})"
