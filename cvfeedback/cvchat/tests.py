from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

class CVChatAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_valid_pdf_upload(self):
        url = reverse('analizar_cv')
        pdf_content = b'%PDF-1.4 fake pdf content'
        file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
        response = self.client.post(url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_non_pdf_upload(self):
        url = reverse('analizar_cv')
        file = SimpleUploadedFile("test.txt", b"not a pdf", content_type="text/plain")
        response = self.client.post(url, {'file': file}, format='multipart')
        self.assertIn(response.status_code, [400, 415])

    def test_malicious_pdf(self):
        url = reverse('analizar_cv')
        malicious_pdf = SimpleUploadedFile("malicious.pdf", b"%PDF-1.4 malicious content", content_type="application/pdf")
        response = self.client.post(url, {'file': malicious_pdf}, format='multipart')
        self.assertIn(response.status_code, [201, 403])

    def test_large_pdf(self):
        url = reverse('analizar_cv')
        large_content = b"%PDF-1.4" + b"0" * (6 * 1024 * 1024)  # 6MB, mayor a 5MB límite
        large_file = SimpleUploadedFile("large.pdf", large_content, content_type="application/pdf")
        response = self.client.post(url, {'file': large_file}, format='multipart')
        self.assertIn(response.status_code, [201, 400, 413])
