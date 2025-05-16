# cvchat/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UploadedCV
from .serializers import UploadedCVSerializer
from django.shortcuts import get_object_or_404
import fitz
import openai
from django.conf import settings

class CVAPIView(APIView):

    def get(self, request, pk=None):
        if pk:
            cv = get_object_or_404(UploadedCV, pk=pk)
            serializer = UploadedCVSerializer(cv)
            return Response(serializer.data)
        cvs = UploadedCV.objects.all()
        serializer = UploadedCVSerializer(cvs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UploadedCVSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            file = request.FILES['file']
            text = self.extract_text(file)
            feedback = self.get_feedback(text)
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

    def get_feedback(self, text):
        openai.api_key = settings.OPENAI_API_KEY
        prompt = f"Analiza el siguiente CV y brinda recomendaciones:\n{text}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en recursos humanos."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error al obtener respuesta: {str(e)}"
