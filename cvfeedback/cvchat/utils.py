import openai
from django.conf import settings
from django.core.exceptions import ValidationError
import logging
import bleach

logger = logging.getLogger(__name__)

def validar_archivo_pdf(file):
    #maximos 5MB
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("El archivo no puede superar 5MB.")
    # tipo de contenido
    if not file.content_type in ["application/pdf"]:
        raise ValidationError("Solo se permiten archivos PDF.")
    

def sanitizar_texto(texto):
    """
    Limpia el texto extraído del PDF para eliminar etiquetas HTML
    u otros elementos no deseados. Ayuda a prevenir XSS.
    """
    return bleach.clean(texto)


def obtener_feedback_cv(texto_cv):
    openai.api_key = settings.OPENAI_API_KEY
    client = openai.OpenAI()

    prompt = f"Analiza el siguiente CV y brinda recomendaciones:\n{texto_cv}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en recursos humanos."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error al obtener feedback: {e}")
        return "Ocurrió un error interno. Intenta de nuevo más tarde."