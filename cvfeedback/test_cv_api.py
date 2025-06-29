from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from django.urls import reverse

class TestCVAPI(APITestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.username = "testuser"
        self.password = "testpassword123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        
        # Crear cliente de pruebas
        self.client = APIClient()
        
        # Autenticarse (login)
        logged_in = self.client.login(username=self.username, password=self.password)
        assert logged_in, "No se pudo autenticar el usuario de prueba"

    def test_valid_pdf_upload(self):
        url = reverse('upload-cv')  # Cambia 'upload-cv' por el nombre de tu url
        with open("dummy_cv.pdf", "rb") as f:
            response = self.client.post(url, {'file': f}, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_non_pdf_upload(self):
        url = reverse('upload-cv')
        with open("test_image.jpg", "rb") as f:
            response = self.client.post(url, {'file': f}, format='multipart')
        self.assertIn(response.status_code, [400, 415])

    def test_malicious_pdf(self):
        url = reverse('upload-cv')
        with open("malicious_cv.pdf", "rb") as f:
            response = self.client.post(url, {'file': f}, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_large_pdf(self):
        url = reverse('upload-cv')
        with open("large_dummy.pdf", "rb") as f:
            response = self.client.post(url, {'file': f}, format='multipart')
        self.assertIn(response.status_code, [201, 400, 413])

    def test_invalid_endpoint(self):
        response = self.client.get("/api/invalid")
        self.assertEqual(response.status_code, 404)
