from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UploadedCV
from .serializers import UploadedCVSerializer
from django.shortcuts import get_object_or_404, render
import fitz
from .utils import obtener_feedback_cv

def extraer_texto_pdf(archivo_pdf):
    import fitz
    texto = ""
    with fitz.open(stream=archivo_pdf.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

@login_required
def analizar_cv(request):
    feedback = None

    if request.method == 'POST' and request.FILES.get('cv'):
        archivo_pdf = request.FILES['cv']
        texto_cv = extraer_texto_pdf(archivo_pdf)
        feedback = obtener_feedback_cv(texto_cv)

    return render(request, 'cvchat/analizar-cv.html', {'feedback': feedback})

class CVAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            cv = get_object_or_404(UploadedCV, pk=pk, user=request.user)
            serializer = UploadedCVSerializer(cv)
            return Response(serializer.data)

        cvs = UploadedCV.objects.filter(user=request.user)
        serializer = UploadedCVSerializer(cvs, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id  # Asocia el CV al usuario logueado
        serializer = UploadedCVSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            file = request.FILES.get('file')
            if file:
                text = self.extract_text(file)
                feedback = obtener_feedback_cv(text)
            else:
                feedback = "No se proporcionó archivo para analizar."
            return Response({'cv_data': serializer.data, 'feedback': feedback}, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        cv = get_object_or_404(UploadedCV, pk=pk)
        serializer = UploadedCVSerializer(cv, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        cv = get_object_or_404(UploadedCV, pk=pk)
        cv.delete()
        return Response(status=204)

    def extract_text(self, file):
        text = ""
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
