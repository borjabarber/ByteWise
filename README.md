# EntrevistadorDS
Este proyecto es un **entrevistador técnico virtual** para Data Science, desarrollado con FastAPI, OpenAI GPT-4 y una interfaz web moderna. El objetivo es simular una entrevista técnica real, ayudando a candidatos a practicar y mejorar sus habilidades en temas clave de ciencia de datos.

## Características

- **Simulación de entrevista técnica**: El bot actúa como un entrevistador senior y realiza preguntas técnicas de Data Science.
- **Flujo natural**: El bot se presenta, pide al usuario que se presente y luego inicia la entrevista.
- **Preguntas variadas**: Incluye temas como Machine Learning, métricas, regularización, SQL, experimentos A/B, etc.
- **Feedback inmediato**: Si la respuesta es incorrecta, el bot explica el concepto correcto.
- **Interfaz moderna**: Chat visual atractivo, animaciones y experiencia de usuario fluida.

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
├── .env                   # Tu clave de OpenAI (no subir a GitHub)
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


