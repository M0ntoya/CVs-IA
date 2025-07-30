from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import UploadedCV, HistorialCV
from .serializers import UploadedCVSerializer
from .utils import validar_archivo_pdf, sanitizar_texto, obtener_feedback_cv
import fitz
import markdown



def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('analizar_cv')
    else:
        form = UserCreationForm()
    return render(request, 'cvchat/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('analizar_cv')
    else:
        form = AuthenticationForm()
    return render(request, 'cvchat/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')



class CVAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'No se proporcionó archivo.'}, status=status.HTTP_400_BAD_REQUEST)

        if file.content_type != 'application/pdf':
            return Response({'error': 'Solo se permiten archivos PDF.'}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            return Response({'error': 'Archivo demasiado grande. Tamaño máximo 5MB.'}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        try:
            validar_archivo_pdf(file)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Archivo inválido o malicioso.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UploadedCVSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            texto_cv = sanitizar_texto(self.extract_text(file))
            feedback = obtener_feedback_cv(texto_cv)

            return Response({'cv_data': serializer.data, 'feedback': feedback}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def extract_text(self, file):
        text = ""
        file.seek(0)
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text

# vista para analizar CV
@login_required
def analizar_cv(request):
    feedback_html = None

    if request.method == 'POST' and request.FILES.get('cv'):
        archivo_pdf = request.FILES['cv']
        try:
            validar_archivo_pdf(archivo_pdf)
            texto_cv = sanitizar_texto(extraer_texto_pdf(archivo_pdf))
            feedback_markdown = obtener_feedback_cv(texto_cv)

            # Obtener último CV para versión
            ultimo_cv = HistorialCV.objects.filter(usuario=request.user).order_by('-version').first()
            if ultimo_cv and ultimo_cv.version:
                try:
                    nueva_version = float(ultimo_cv.version) + 0.1
                except ValueError:
                    nueva_version = 1.0
            else:
                nueva_version = 1.0

            # Guardar nuevo CV en historial
            HistorialCV.objects.create(
                usuario=request.user,
                archivo_pdf=archivo_pdf,
                recomendaciones=feedback_markdown,
                version=f"{nueva_version:.1f}",
                estado="Analizado"
            )

            feedback_html = markdown.markdown(feedback_markdown)

        except Exception as e:
            feedback_html = f'<p class="text-danger">Error al procesar el CV: {str(e)}</p>'

    # Obtener todos los CVs del usuario para el historial lateral (actualizado)
    cvs = HistorialCV.objects.filter(usuario=request.user).order_by('-fecha_subida')

    return render(request, 'cvchat/analizar-cv.html', {'feedback': feedback_html, 'cvs': cvs})



# --- Vista del historial de CVs ---

@login_required
def historial_cvs(request):
    cvs = HistorialCV.objects.filter(usuario=request.user).order_by('-fecha_subida')
    return render(request, 'cvchat/historial.html', {'cvs': cvs})

# --- Función para extraer texto de PDF ---

def extraer_texto_pdf(archivo_pdf):
    texto = ""
    archivo_pdf.seek(0)
    with fitz.open(stream=archivo_pdf.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto
