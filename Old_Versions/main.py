import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn
import re

# Cargar variables de entorno
load_dotenv()

app = FastAPI()

# Configurar OpenAI con la nueva API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client.api_key:
    raise ValueError("OPENAI_API_KEY no configurada en .env")

# Obtener rutas absolutas
base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "templates")
static_dir = os.path.join(base_dir, "static")

# Configurar templates y archivos estáticos
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Contexto del sistema para el entrevistador
INTERVIEWER_CONTEXT = """
Eres un entrevistador técnico senior de Data Science. Tu objetivo es evaluar las habilidades técnicas del candidato mediante preguntas desafiantes.

Instrucciones específicas:
1. Haz solo UNA pregunta por vez.
2. Espera la respuesta completa del candidato antes de continuar.
3. Si la respuesta es incorrecta, explica brevemente el concepto correcto.
4. Varía los temas gradualmente:
   - Comienza con fundamentos de ML.
   - Continúa con procesamiento de datos.
   - Finaliza con casos prácticos.
5. Sé riguroso pero profesional.

Temas a cubrir:
- Bias-Variance Tradeoff.
- Cross-validation técnicas.
- Feature engineering.
- Métricas de evaluación (Precision, Recall, F1, AUC).
- Regularización (L1/L2).
- SQL para análisis.
- Diseño de experimentos A/B.
"""

def extraer_nombre(texto):
    # Busca frases como "me llamo X", "soy X", "mi nombre es X"
    patrones = [
        r"me llamo ([a-zA-ZáéíóúüñÁÉÍÓÚÜÑ ]+)",
        r"mi nombre es ([a-zA-ZáéíóúüñÁÉÍÓÚÜÑ ]+)",
        r"soy ([a-zA-ZáéíóúüñÁÉÍÓÚÜÑ ]+)"
    ]
    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            nombre = match.group(1).strip().split()[0]
            return nombre.capitalize()
    # Si no encuentra, devuelve saludo genérico
    return None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message", "").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Mensaje vacío")

    try:
        chat_history = data.get("history", [])
        chat_history = [
            m for m in chat_history
            if isinstance(m, dict) and "role" in m and "content" in m
        ]

        # FLUJO: Si no hay historial, el usuario se está presentando
        if not chat_history:
            nombre = extraer_nombre(user_message)
            if nombre:
                saludo = f"¡Encantado, {nombre}! Comencemos la entrevista. Primera pregunta:"
            else:
                saludo = "¡Encantado! Comencemos la entrevista. Primera pregunta:"
            # Pedimos a GPT la primera pregunta
            messages = [
                {"role": "system", "content": INTERVIEWER_CONTEXT},
                {"role": "user", "content": "Haz la primera pregunta de la entrevista técnica de Data Science."}
            ]
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            pregunta = response.choices[0].message.content.strip()
            return {"message": f"{saludo}\n\n{pregunta}"}

        # Flujo normal de entrevista
        messages = [{"role": "system", "content": INTERVIEWER_CONTEXT}] + chat_history + [{"role": "user", "content": user_message}]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        assistant_message = response.choices[0].message.content.strip()
        return {"message": assistant_message}

    except Exception as e:
        print(f"Error en OpenAI: {str(e)}")
        return {"message": "⚠️ Error al procesar tu respuesta. Por favor intenta de nuevo."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)