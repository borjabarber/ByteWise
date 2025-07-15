# ByteWise tu entrevistador tecnico de data science 
Este proyecto es un **entrevistador técnico virtual** para Data Science, desarrollado con FastAPI, OpenAI GPT-4 y una interfaz web moderna. El objetivo es simular una entrevista técnica real, ayudando a candidatos a practicar y mejorar sus habilidades en temas clave de ciencia de datos.


## ¿Qué hace todo este sistema?

Este proyecto implementa una **simulación de entrevista técnica en Data Science** utilizando FastAPI y la API de OpenAI (GPT-4). A continuación se resumen sus funciones principales:

**Reconoce tu presentación**: Detecta si el usuario se presenta ("me llamo...", "soy...") y responde con un saludo personalizado.
**Actúa como entrevistador técnico**: Usa un contexto predefinido para que GPT-4 se comporte como un entrevistador experto en Data Science.
**Hace preguntas una por una**: La entrevista avanza paso a paso. GPT-4 espera tu respuesta antes de continuar con la siguiente pregunta.
**Preguntas variadas**: Las preguntas cubren temas como:
  - Bias-Variance Tradeoff  
  - Cross-validation  
  - Feature engineering  
  - Métricas como Precision, Recall, F1, AUC  
  - Regularización L1/L2  
  - SQL  
  - Diseño de experimentos A/B  
**Interfaz web**: La entrevista se realiza desde una página web (`index.html`) usando FastAPI y plantillas Jinja2.  
**Memoria de contexto**: Mantiene el historial del chat para que GPT-4 entienda en qué parte de la entrevista estás.  
**Manejo de errores**: Si ocurre un fallo (por ejemplo, error en la API), te informa para que lo intentes de nuevo.  
**Interfaz moderna**: Chat visual atractivo, animaciones y experiencia de usuario fluida.  

En resumen, este sistema convierte tu navegador en una sala de entrevistas donde practicas tus habilidades de Data Science con inteligencia artificial.  

## Tecnologías utilizadas

- **Backend**: FastAPI, OpenAI GPT-4 API
- **Frontend**: HTML, CSS, JavaScript (sin frameworks)
- **Estilos**: CSS moderno con degradados y animaciones
- **Despliegue local**: Uvicorn

## Instalación y uso

1. **Clona el repositorio**
    ```bash
    git clone https://github.com/tuusuario/entrevistador2.git
    cd entrevistador2
    ```

2. **Crea un entorno virtual y activa**
    ```bash
    python -m venv venv
    # En Windows
    venv\Scripts\activate
    # En Mac/Linux
    source venv/bin/activate
    ```

3. **Instala las dependencias necesarias**
    ```bash
    pip install fastapi openai uvicorn python-dotenv
    ```

4. **Configura tu clave de OpenAI**
    - Crea un archivo `.env` en la raíz del proyecto con el contenido:
      ```
      OPENAI_API_KEY=tu_clave_de_openai
      ```

5. **Ejecuta la aplicación**
    ```bash
    uvicorn main:app --reload
    ```

6. **Abre tu navegador**
    - Ve a [http://localhost:8000](http://localhost:8000)

## Estructura del proyecto

```
entrevistador2/
│
├── main.py                # Backend FastAPI
│
├── oldvers/               # Antiguas versiones y pruebas.
│
├── static/
│   ├── css/
│   │   └── style.css      # Estilos del chat
│   └── js/
│       └── script.js      # Lógica del frontend
│
├── templates/
│   └── index.html         # Interfaz principal
```


Este proyecto es solo para fines educativos y de práctica.  
No está afiliado a OpenAI ni a ninguna empresa de selección de personal.

---


