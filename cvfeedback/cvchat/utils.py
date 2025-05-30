import openai
from django.conf import settings

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
        return f"Error inesperado: {str(e)}"
