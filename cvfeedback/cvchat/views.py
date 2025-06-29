from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from django.shortcuts import render
from .models import UploadedCV
from .serializers import UploadedCVSerializer
from .utils import validar_archivo_pdf, sanitizar_texto, obtener_feedback_cv
import fitz
from django.contrib.auth.decorators import login_required

class CVAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'No se proporcionó archivo.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar tipo MIME
        if file.content_type != 'application/pdf':
            return Response({'error': 'Solo se permiten archivos PDF.'}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        # Validar tamaño máximo 5MB
        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            return Response({'error': 'Archivo demasiado grande. Tamaño máximo 5MB.'}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        # Validar contenido PDF
        try:
            validar_archivo_pdf(file)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Archivo inválido o malicioso.'}, status=status.HTTP_403_FORBIDDEN)

        # Usar serializer con contexto para asignar usuario
        serializer = UploadedCVSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            texto_cv = sanitizar_texto(self.extract_text(file))
            feedback = obtener_feedback_cv(texto_cv)

            return Response({'cv_data': serializer.data, 'feedback': feedback}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def extract_text(self, file):
        text = ""
        file.seek(0)  # importante para leer desde el inicio
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text


@login_required
def analizar_cv(request):
    feedback = None
    if request.method == 'POST' and request.FILES.get('cv'):
        archivo_pdf = request.FILES['cv']
        try:
            validar_archivo_pdf(archivo_pdf)
            texto_cv = sanitizar_texto(extraer_texto_pdf(archivo_pdf))
            feedback = obtener_feedback_cv(texto_cv)
        except Exception as e:
            feedback = f'Error: {str(e)}'
    return render(request, 'cvchat/analizar-cv.html', {'feedback': feedback})

def extraer_texto_pdf(archivo_pdf):
    texto = ""
    archivo_pdf.seek(0)
    with fitz.open(stream=archivo_pdf.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto
