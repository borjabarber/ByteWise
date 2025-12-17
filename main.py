import os
import sqlite3
import uuid
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn
import re
from typing import Optional
from contextlib import contextmanager

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="ByteWise API", version="1.0.0")

# Configurar CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar OpenAI con la nueva API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client.api_key:
    raise ValueError("OPENAI_API_KEY no configurada en .env")

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS SQLite
# ============================================
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bytewise.db")

@contextmanager
def get_db():
    """Context manager para conexiones a la base de datos."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Inicializa las tablas de la base de datos."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Tabla de sesiones de entrevista
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                candidate_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0
            )
        """)
        
        # Tabla de mensajes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        conn.commit()
        print(f"Base de datos inicializada en: {DATABASE_PATH}")

# Inicializar la base de datos al arrancar
init_database()

# ============================================
# FUNCIONES DE BASE DE DATOS
# ============================================

def create_session(candidate_name: Optional[str] = None) -> str:
    """Crea una nueva sesión de entrevista."""
    session_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, candidate_name) VALUES (?, ?)",
            (session_id, candidate_name)
        )
        conn.commit()
    return session_id

def get_session(session_id: str) -> Optional[dict]:
    """Obtiene los datos de una sesión."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None

def update_session(session_id: str, **kwargs):
    """Actualiza los datos de una sesión."""
    with get_db() as conn:
        cursor = conn.cursor()
        updates = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [session_id]
        cursor.execute(
            f"UPDATE sessions SET {updates}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values
        )
        conn.commit()

def save_message(session_id: str, role: str, content: str):
    """Guarda un mensaje en la base de datos."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()

def get_session_messages(session_id: str) -> list:
    """Obtiene todos los mensajes de una sesión."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at",
            (session_id,)
        )
        return [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]

def get_all_sessions() -> list:
    """Obtiene todas las sesiones."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM sessions ORDER BY updated_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]


# Contexto del sistema para el entrevistador
INTERVIEWER_CONTEXT = """
Eres un entrevistador técnico de élite especializado en Data Science, Machine Learning e Inteligencia Artificial. 
Tienes más de 15 años de experiencia entrevistando para empresas como Google, Meta, Netflix y startups top de Silicon Valley.

## TU PERSONALIDAD:
- Eres carismático pero implacable. Usas humor sutil para relajar, pero tus preguntas son demoledoras.
- Celebras las buenas respuestas con entusiasmo genuino ("¡Exacto! Eso es lo que busco").
- Cuando el candidato falla, eres constructivo pero directo. Explicas el concepto y das una segunda oportunidad.
- Adaptas tu nivel según las respuestas: si el candidato es fuerte, subes la dificultad brutalmente.

## REGLAS DE LA ENTREVISTA:
1. UNA sola pregunta por mensaje. Nunca hagas múltiples preguntas.
2. Evalúa cada respuesta antes de continuar. Da feedback específico.
3. Si la respuesta es parcial, pide que profundice: "Interesante... ¿puedes expandir sobre X?"
4. Alterna entre teoría, código mental y casos prácticos.
5. Cada 3-4 preguntas, haz un "curveball" inesperado para probar adaptabilidad.
6. Genera preguntas ORIGINALES basándote en tu conocimiento. No te limites a una lista fija.

## ARSENAL DE TEMAS (mezcla y profundiza según el nivel):

### FUNDAMENTOS DE ML:
- Bias-Variance Tradeoff (¿cómo lo diagnosticas? ¿cómo lo arreglas?)
- Overfitting vs Underfitting (señales, soluciones, ejemplos reales)
- Gradient Descent variantes (SGD, Adam, RMSprop, momentum)
- Regularización L1/L2/ElasticNet (¿cuándo cada una? ¿por qué L1 genera sparsity?)
- Cross-validation estrategias (K-Fold, Stratified, Time Series Split, Leave-One-Out)
- Ensemble methods (Bagging vs Boosting, Random Forest vs XGBoost vs LightGBM)
- Kernel trick en SVM
- Naive Bayes y la asunción de independencia

### DEEP LEARNING:
- Arquitecturas CNN (ResNet, VGG, EfficientNet - ¿por qué skip connections?)
- RNN/LSTM/GRU (vanishing gradients, cuándo usar cada una)
- Transformers y Attention (self-attention, multi-head, positional encoding)
- Batch Normalization vs Layer Normalization
- Dropout y su interpretación bayesiana
- Transfer Learning estrategias
- Optimizadores adaptativos y learning rate scheduling

### NLP AVANZADO:
- Word embeddings (Word2Vec, GloVe, FastText - diferencias clave)
- BERT, GPT, T5 (arquitecturas, pretraining objectives)
- Tokenización (BPE, WordPiece, SentencePiece)
- Fine-tuning vs Prompt Engineering vs RAG
- Evaluación de modelos de lenguaje (perplexity, BLEU, ROUGE)

### ESTADÍSTICA Y PROBABILIDAD:
- Teorema de Bayes aplicado (prior, likelihood, posterior)
- Tests de hipótesis (p-value, Type I/II errors, power)
- Distribuciones (Normal, Poisson, Exponencial - ¿cuándo aplica cada una?)
- Maximum Likelihood Estimation vs MAP
- Bootstrapping y sus aplicaciones
- Causalidad vs Correlación (¿cómo probarías causalidad?)

### EXPERIMENTACIÓN:
- Diseño de experimentos A/B (sample size, duration, segmentación)
- Multi-armed bandits vs A/B testing tradicional
- Novelty effects y cómo mitigarlos
- Métricas de guardrail vs métricas primarias
- Network effects en experimentos
- Análisis de sensibilidad

### DATA ENGINEERING:
- SQL avanzado (window functions, CTEs, optimización de queries)
- Feature Store y Feature Engineering pipelines
- Data versioning y reproducibilidad
- Streaming vs Batch processing
- Particionamiento y sharding
- Data quality y monitoring

### MÉTRICAS Y EVALUACIÓN:
- Precision/Recall/F1 (¿cuándo priorizar cada una?)
- ROC-AUC vs PR-AUC (¿cuándo usar cada una?)
- Calibración de probabilidades
- Métricas de ranking (NDCG, MAP, MRR)
- Métricas de regresión (MSE, MAE, MAPE, R²)
- Métricas de negocio vs métricas de modelo

### MLOps Y PRODUCCIÓN:
- Model serving (latencia, throughput, batching)
- A/B testing de modelos en producción
- Model monitoring y drift detection
- Feature pipelines en tiempo real
- Versionado de modelos y experimentos
- CI/CD para ML

### CASOS PRÁCTICOS (genera escenarios realistas):
- "Diseña un sistema de recomendación para Netflix"
- "¿Cómo detectarías fraude en transacciones en tiempo real?"
- "Diseña el ranking de búsqueda de Google"
- "¿Cómo predecirías churn en una app de suscripción?"
- "Diseña un sistema de pricing dinámico"

## FORMATO DE TUS RESPUESTAS:
- Sé conciso pero completo
- Usa formato estructurado cuando expliques conceptos
- Incluye ejemplos prácticos cuando sea relevante
- Si el candidato da una respuesta excelente, reconócelo y sube el nivel inmediatamente

Recuerda: Tu objetivo es encontrar el LÍMITE del conocimiento del candidato, no destruirlo. Presiona hasta que falle, luego enseña.
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

@app.get("/")
async def health_check():
    """Endpoint de salud para verificar que el API está funcionando."""
    return {"status": "ok", "message": "ByteWise API is running", "database": DATABASE_PATH}

# ============================================
# ENDPOINTS DE SESIONES
# ============================================

@app.post("/sessions")
async def create_new_session(request: Request):
    """Crea una nueva sesión de entrevista."""
    data = await request.json()
    candidate_name = data.get("candidate_name")
    session_id = create_session(candidate_name)
    return {
        "session_id": session_id,
        "candidate_name": candidate_name,
        "message": "Sesión creada exitosamente"
    }

@app.get("/sessions")
async def list_sessions():
    """Lista todas las sesiones de entrevista."""
    sessions = get_all_sessions()
    return {"sessions": sessions, "total": len(sessions)}

@app.get("/sessions/{session_id}")
async def get_session_details(session_id: str):
    """Obtiene los detalles de una sesión específica."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    messages = get_session_messages(session_id)
    return {
        "session": session,
        "messages": messages,
        "message_count": len(messages)
    }

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Elimina una sesión y todos sus mensajes."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
    
    return {"message": "Sesión eliminada exitosamente"}

# ============================================
# ENDPOINT DE CHAT CON PERSISTENCIA
# ============================================

@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    Endpoint principal de chat con persistencia.
    
    Parámetros:
    - message: El mensaje del usuario
    - session_id: (opcional) ID de sesión existente para continuar
    - history: (opcional, legacy) Historial de mensajes si no se usa session_id
    """
    data = await request.json()
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id")

    if not user_message:
        raise HTTPException(status_code=400, detail="Mensaje vacío")

    try:
        # Si hay session_id, recuperar historial de la base de datos
        if session_id:
            session = get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Sesión no encontrada")
            
            # Obtener historial de la BD
            chat_history = get_session_messages(session_id)
            
            # Guardar mensaje del usuario
            save_message(session_id, "user", user_message)
        else:
            # Crear nueva sesión automáticamente
            nombre = extraer_nombre(user_message)
            session_id = create_session(nombre)
            chat_history = []
            
            # Guardar mensaje del usuario
            save_message(session_id, "user", user_message)
            
            # Actualizar nombre del candidato si se extrajo
            if nombre:
                update_session(session_id, candidate_name=nombre)

        # FLUJO: Si no hay historial, el usuario se está presentando
        if not chat_history:
            nombre = extraer_nombre(user_message)
            
            # Dejamos que GPT maneje todo el saludo de forma natural
            if nombre:
                prompt_inicio = f"El candidato se ha presentado diciendo: '{user_message}'. Su nombre es {nombre}. Salúdale brevemente de forma natural y amigable, y hazle directamente tu primera pregunta técnica de la entrevista. No uses frases como 'Excelente' o 'Perfecto' después del saludo, ve directo a la pregunta."
            else:
                prompt_inicio = f"El candidato se ha presentado diciendo: '{user_message}'. Salúdale brevemente de forma natural y hazle directamente tu primera pregunta técnica de la entrevista. No uses frases como 'Excelente' o 'Perfecto' después del saludo, ve directo a la pregunta."
            
            messages = [
                {"role": "system", "content": INTERVIEWER_CONTEXT},
                {"role": "user", "content": prompt_inicio}
            ]
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            assistant_message = response.choices[0].message.content.strip()
            
            # Guardar respuesta del asistente
            save_message(session_id, "assistant", assistant_message)
            
            # Actualizar contador de preguntas
            update_session(session_id, total_questions=1)
            
            return {
                "message": assistant_message,
                "session_id": session_id
            }

        # Flujo normal de entrevista
        messages = [{"role": "system", "content": INTERVIEWER_CONTEXT}] + chat_history + [{"role": "user", "content": user_message}]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        assistant_message = response.choices[0].message.content.strip()
        
        # Guardar respuesta del asistente
        save_message(session_id, "assistant", assistant_message)
        
        # Actualizar contador de preguntas (simplificado)
        session = get_session(session_id)
        update_session(session_id, total_questions=session["total_questions"] + 1)
        
        return {
            "message": assistant_message,
            "session_id": session_id
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en OpenAI: {str(e)}")
        return {"message": "Error al procesar tu respuesta. Por favor intenta de nuevo.", "error": str(e)}

# ============================================
# ENDPOINT PARA CONTINUAR SESIÓN
# ============================================

@app.post("/sessions/{session_id}/continue")
async def continue_session(session_id: str, request: Request):
    """Continúa una sesión existente con un nuevo mensaje."""
    data = await request.json()
    data["session_id"] = session_id
    return await chat_endpoint(request.__class__(scope=request.scope, receive=lambda: data))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)