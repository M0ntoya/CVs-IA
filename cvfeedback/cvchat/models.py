# cvchat/models.py
from django.db import models

class UploadedCV(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True)  # Feedback de OpenAI

    def __str__(self):
        return self.file.name
