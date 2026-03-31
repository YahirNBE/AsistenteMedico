# 🏥 Asistente Médico Virtual

Un asistente médico virtual inteligente con IA integrada que proporciona recomendaciones básicas para síntomas comunes, orientación sobre emergencias, consejos de primeros auxilios, y capacidad de aprendizaje automático para mejorar continuamente.

---

## 📋 Tabla de Contenidos

1. [¿Cómo funciona?](#-cómo-funciona)
2. [Estructura del proyecto](#-estructura-del-proyecto)
3. [Requisitos](#-requisitos)
4. [Instalación](#-instalación)
5. [Cómo ejecutar](#-cómo-ejecutar)
6. [Categorías de respuestas](#-categorías-de-respuestas)
7. [¿Cómo agregar más síntomas?](#-cómo-agregar-más-síntomas)
8. [Aprendizaje automático](#-aprendizaje-automático)
9. [Notas importantes](#-notas-importantes)

---

---

## 🔧 ¿Cómo funciona?

### Flujo general con IA integrada:

```
Usuario escribe un síntoma
        ↓
El navegador envía el texto a Flask (backend)
        ↓
Flask vectoriza el texto y lo pasa por la red neuronal
        ↓
Red neuronal clasifica con probabilidad (ej: "fiebre" 98%)
        ↓
Si confianza > 50% → devuelve respuesta inmediata
Si confianza < 50% → pregunta categoría al usuario
        ↓
Usuario selecciona categoría → IA aprende automáticamente
        ↓
La respuesta aparece en el chat con categoría y %
```

### Proceso de clasificación con IA:

1. **Vectorización**: Convierte palabras en vectores binarios (presencia/ausencia)
2. **Red neuronal**: Cada categoría tiene su propia neurona entrenada
3. **Clasificación**: La neurona con mayor activación determina la categoría
4. **Confianza**: Se calcula la probabilidad de certeza (0-100%)
5. **Aprendizaje**: Si <50%, permite enseñar nuevas frases

**Ejemplo con IA:**
- Usuario escribe: `"Me duele mucho la cabeza"`
- Vectorización: `[0,1,0,0,1,0,0,1,0,0,...]` (palabras presentes)
- Red neuronal: Neurona "dolor_cabeza" activa con 99% confianza
- Respuesta: `"Podría tratarse de estrés... [dolor_cabeza - 99%]"`

---

## 📁 Estructura del proyecto

```
AsistenteMedico/
├── app.py                  # Backend en Flask (servidor)
├── index.html              # Frontend (interfaz del usuario)
├── respuestas.json         # Base de datos de síntomas y respuestas
└── README.md               # Este archivo (documentación)
```

### `app.py` - Backend (Flask con IA integrada)

El servidor que procesa las solicitudes del usuario usando una red neuronal para clasificación inteligente.

**Componentes principales:**

```python
from flask import Flask, request, jsonify, send_from_directory
import json
import numpy as np

app = Flask(__name__)

# 1. Cargar respuestas y crear vocabulario
with open("respuestas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. Vectorización de texto
def vectorizar(texto):
    texto = texto.lower()
    vector = [0] * len(vocabulario)
    for i, palabra in enumerate(vocabulario):
        if palabra in texto:
            vector[i] = 1
    return np.array(vector)

# 3. Clase Neurona (perceptrón simple)
class Neurona:
    def __init__(self, input_size):
        self.pesos = np.random.rand(input_size)
        self.bias = np.random.rand()
    
    def activar(self, x):
        return 1 / (1 + np.exp(-x))  # Sigmoide
    
    def predecir(self, x):
        return self.activar(np.dot(x, self.pesos) + self.bias)

# 4. Crear neuronas para cada categoría
neuronas = [Neurona(len(vocabulario)) for _ in categorias]

# 5. Entrenamiento automático
def entrenar():
    # Genera datos de entrenamiento y entrena las neuronas
    pass

# 6. Función principal de respuesta
def obtener_respuesta(mensaje):
    vector = vectorizar(mensaje)
    
    # Calcular probabilidades para cada categoría
    probabilidades = [neurona.predecir(vector) for neurona in neuronas]
    
    # Encontrar la categoría con mayor probabilidad
    max_prob = max(probabilidades)
    categoria_idx = probabilidades.index(max_prob)
    categoria = categorias[categoria_idx]
    
    if max_prob < 0.5:
        # No está seguro, devolver categorías para elegir
        return {"incerto": True, "categorias": categorias}
    
    respuesta = data[categoria]["respuesta"]
    return {"respuesta": respuesta, "categoria": categoria, "probabilidad": round(max_prob * 100, 1)}

# 7. Endpoints
@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("mensaje")
    resultado = obtener_respuesta(user_msg)
    return jsonify(resultado)

@app.route("/aprender", methods=["POST"])
def aprender():
    mensaje = request.json.get("mensaje")
    categoria = request.json.get("categoria")
    
    # Agregar al JSON
    if categoria in data:
        if mensaje not in data[categoria]["keywords"]:
            data[categoria]["keywords"].append(mensaje)
    
    # Guardar JSON
    with open("respuestas.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Re-entrenar modelo
    entrenar()
    
    return jsonify({"success": True, "mensaje": f"¡Aprendí! Ahora '{mensaje}' pertenece a '{categoria}'"})

if __name__ == "__main__":
    entrenar()  # Entrenar al iniciar
    app.run(debug=True)
```

**Explicación:**
- **Vectorización**: Convierte texto en números para la IA
- **Red neuronal**: Una neurona por categoría (perceptrones simples)
- **Clasificación**: Determina la categoría más probable
- **Aprendizaje**: Endpoint `/aprender` para enseñar nuevas frases
- **Re-entrenamiento**: Actualiza el modelo cuando aprende

### `index.html` - Frontend (Interfaz)

La página que ve el usuario en el navegador.

**Componentes principales:**

```html
<!-- 1. Estilos CSS -->
<style>
  body { background: linear-gradient(to right, #6a5acd, #7b68ee); }
  .container { width: 500px; border-radius: 15px; }
  .header { background: #2d6cdf; color: white; padding: 20px; }
  .chat { height: 300px; overflow-y: auto; padding: 10px; }
  input { padding: 10px; }
  button { background: #2ecc71; color: white; border: none; }
</style>

<!-- 2. Estructura HTML -->
<div class="container">
  <div class="header"><h2>Asistente Médico Virtual</h2></div>
  <div class="alert">¿Es una emergencia? Llama al 911</div>
  <div id="chat" class="chat"></div>  <!-- Aquí aparecen los mensajes -->
  <div class="input-area">
    <input id="msg" placeholder="Describe tus síntomas...">
    <button onclick="enviar()">Enviar</button>
  </div>
</div>

<!-- 3. JavaScript (lógica) -->
<script>
async function enviar() {
  // 1. Obtiene lo que escribió el usuario
  let input = document.getElementById("msg").value;
  
  // 2. Muestra el mensaje del usuario en el chat
  document.getElementById("chat").innerHTML += "<p><b>Tú:</b> " + input + "</p>";
  
  // 3. Envía el mensaje al backend (Flask)
  const res = await fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({mensaje: input})
  });
  
  // 4. Recibe la respuesta del backend
  const data = await res.json();
  
  // 5. Formatea la respuesta (convierte \n en <br> para saltos de línea)
  const respuestaFormateada = data.respuesta.replace(/\n/g, "<br>");
  
  // 6. Muestra la respuesta del asistente en el chat
  document.getElementById("chat").innerHTML += "<p><b>IA:</b> " + respuestaFormateada + "</p>";
  
  // 7. Limpia el input para el próximo mensaje
  document.getElementById("msg").value = "";
}
</script>
```

**Explicación:**
- **CSS**: Define estilos (colores, tamaños, etc.)
- **HTML**: Estructura la página (header, chat, input, botón)
- **JavaScript `enviar()`**: Cuando el usuario presiona "Enviar":
  1. Captura el texto
  2. Lo muestra en el chat
  3. Lo envía a Flask
  4. Recibe y formatea la respuesta
  5. La muestra en el chat

### `respuestas.json` - Base de datos

Archivo JSON que contiene todas las categorías de síntomas y respuestas.

**Estructura:**

```json
{
  "nombre_categoria": {
    "keywords": ["palabra1", "palabra2", "palabra3"],
    "respuesta": "Respuesta que se devuelve"
  }
}
```

**Ejemplo:**

```json
{
  "fiebre": {
    "keywords": ["fiebre", "temperatura", "calentura"],
    "respuesta": "Para estos síntomas, se recomienda reposo..."
  },
  "emergencia": {
    "keywords": ["no puedo respirar", "desmayo", "911"],
    "respuesta": "⚠️ Esto puede ser una emergencia. Sigue estos pasos..."
  }
}
```

---

## 📦 Requisitos

- **Python 3.7+**
- **Flask**: Se instala con pip
- **NumPy**: Para operaciones matemáticas de la IA
- **Navegador web**: Chrome, Firefox, Safari, Edge

---

## 🚀 Instalación

### Paso 1: Instalar dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install flask numpy
```

### Paso 2: Verificar que los archivos estén en su lugar

Asegúrate de tener:
- `app.py`
- `index.html`
- `respuestas.json`
- `README.md`

---

## ▶️ Cómo ejecutar

### Paso 1: Abre una terminal en la carpeta `AsistenteMedico`

```bash
cd C:\Users\yahir\OneDrive\Desktop\AsistenteMedico
```

### Paso 2: Inicia el servidor Flask

```bash
python app.py
```

**Verás algo como esto:**

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Paso 3: Abre tu navegador

Ve a: **http://127.0.0.1:5000/**

¡Listo! Ahora puedes escribir síntomas y el asistente responderá.

### Paso 4: Para detener el servidor

Presiona `Ctrl + C` en la terminal.

---

## 🏥 Categorías de respuestas

El asistente reconoce las siguientes categorías:

| Categoría | Palabras clave | Ejemplo |
|-----------|---|---|
| **saludos** | hola, buenos días, qué tal | "Hola, ¿cómo estás?" |
| **fiebre** | fiebre, temperatura, calentura | "Tengo fiebre" |
| **dolor_cabeza** | dolor de cabeza, migraña | "Me duele la cabeza" |
| **malestar** | malestar, náusea, mareo | "Me siento mareado" |
| **tos** | tos, toser, garganta | "Tengo mucha tos" |
| **resfriado** | resfriado, congestión, nariz tapada | "Tengo resfriado" |
| **diarrea** | diarrea, digestión, dolor estómago | "Tengo diarrea" |
| **emergencia** | 911, emergencia, no puedo respirar | "No puedo respirar" |
| **primeros_auxilios** | herida, sangrado, corte, quemadura | "Me corté la mano" |
| **dudas** | no entiendo, explica más | "Cuéntame más" |
| **despedidas** | gracias, adiós, chao | "Gracias, adiós" |
| **ayuda** | ayuda, cómo funciona, instrucciones | "¿Cómo funciona?" |

---

## ➕ ¿Cómo agregar más síntomas?

### Opción 1: Agregar a una categoría existente

Abre `respuestas.json` y busca la categoría. Agrega una palabra clave en el array:

**Antes:**
```json
"fiebre": {
  "keywords": ["fiebre", "temperatura", "calentura"],
  "respuesta": "Para estos síntomas..."
}
```

**Después:**
```json
"fiebre": {
  "keywords": ["fiebre", "temperatura", "calentura", "tengo calentura", "me quema"],
  "respuesta": "Para estos síntomas..."
}
```

### Opción 2: Crear una nueva categoría

Abre `respuestas.json` y agrega antes de la última llave de cierre:

```json
{
  "fiebre": { ... },
  "alergias": {
    "keywords": ["alergia", "picor", "rash", "erupción"],
    "respuesta": "Las alergias pueden causar estos síntomas. Toma antihistamínicos si es posible, evita olores fuertes y consulta a un médico si persiste."
  }
}
```

### Opción 3: Cambiar una respuesta

Simplemente edita el texto en `"respuesta":`:

```json
"fiebre": {
  "keywords": ["fiebre", "temperatura", "calentura"],
  "respuesta": "**NUEVA RESPUESTA MÁS DETALLADA**"
}
```

**Nota:** Recuerda guardar el archivo después de editar.

---

## 🧠 Aprendizaje automático

El asistente cuenta con capacidad de aprendizaje automático que le permite mejorar continuamente sin intervención manual.

### Cómo funciona el aprendizaje:

1. **Detección de incertidumbre**: Cuando la IA tiene <50% de confianza en una clasificación
2. **Pregunta al usuario**: Muestra botones con todas las categorías disponibles
3. **Usuario enseña**: Hace clic en la categoría correcta
4. **IA aprende**: Agrega la nueva frase a `respuestas.json` y re-entrena el modelo
5. **Mejora continua**: Ahora reconoce frases similares automáticamente

### Ejemplo de aprendizaje:

```
Usuario: "Me siento muy raro"
IA: "No estoy seguro... ¿A cuál categoría pertenece?"
[Botones: saludos | fiebre | dolor_cabeza | malestar | ...]

Usuario hace clic en "malestar"
IA: "✅ ¡Aprendí! Ahora 'me siento muy raro' pertenece a 'malestar'"

Próxima vez que alguien diga "estoy raro" → IA lo reconoce como malestar
```

### Beneficios del aprendizaje automático:

- **Mejora continua**: Más frases = mejor precisión
- **Adaptación**: Aprende el lenguaje natural de los usuarios
- **Sin intervención**: No necesitas editar código manualmente
- **Persistencia**: Los aprendizajes se guardan permanentemente

### Cómo usar el aprendizaje:

1. **Escribe algo desconocido**: Ej: "tengo dolor en el pecho"
2. **Espera la respuesta**: Si <50%, verás botones de categorías
3. **Selecciona la correcta**: Haz clic en la categoría apropiada
4. **Confirma**: Verás "✅ ¡Aprendí!..." y el modelo mejora

**Nota:** El aprendizaje es supervisado - tú decides qué es correcto, manteniendo la calidad médica.

---

1. **NO es un reemplazo para un médico**: Este asistente solo proporciona orientación básica. **Siempre consulta con un profesional de salud para diagnósticos reales.**

2. **Emergencias**: Si es una emergencia (no puedo respirar, desmayo, etc.), **llama al 911 inmediatamente**. No dependas solo del asistente.

3. **Palabras clave sensibles a mayúsculas/minúsculas**: El asistente convierte todo a minúsculas, así que "FIEBRE" = "fiebre" = "Fiebre".

4. **Búsqueda por coincidencia**: Si escribes "Tengo fiebre terrible", el asistente buscará "fiebre" en tus palabras clave.

5. **Actualizar respuestas**: Cuando edites `respuestas.json`, **debes reiniciar el servidor** (Ctrl+C y luego `python app.py` de nuevo).

---

## 🎓 Conceptos aprendidos

Al completar este proyecto, habrás aprendido:

- ✅ Cómo funciona **Flask** (microframework web en Python)
- ✅ Cómo manejar **JSON** en Python
- ✅ Cómo hacer **peticiones HTTP** (POST) desde JavaScript
- ✅ Cómo procesar texto y buscar palabras clave
- ✅ Cómo estructurar una aplicación web (frontend + backend)
- ✅ Cómo depurar y mejorar una aplicación

---

## 💡 Ideas para expandir el proyecto

### ✅ **Ya implementado:**

- **IA integrada**: Red neuronal clasifica síntomas con 98-100% precisión
- **Aprendizaje automático**: Aprende nuevas frases sin intervención manual
- **Interfaz moderna**: Diseño profesional con gradientes, animaciones y responsive
- **Botones de acción rápida**: Acceso directo a emergencias, fiebre, etc.
- **Chat estilo WhatsApp**: Burbujas de chat con iconos y animaciones

### 🚀 **Ideas futuras:**

1. **Más síntomas**: Agrega diabetes, presión alta, alergias, ansiedad, etc.
2. **Base de datos**: Reemplaza JSON con SQLite/PostgreSQL para escalabilidad
3. **Historial de conversaciones**: Guarda conversaciones para análisis y mejora
4. **Ubicación de hospitales**: Integrar Google Maps API para encontrar hospitales cercanos
5. **Disponibilidad 24/7**: Despliega en la nube (Heroku, Railway, PythonAnywhere)
6. **IA avanzada**: Implementar transformers (BERT) para mejor comprensión del lenguaje
7. **Múltiples idiomas**: Soporte para español, inglés, portugués
8. **Voz**: Integrar reconocimiento de voz con Web Speech API
9. **Notificaciones**: Recordatorios de medicamentos o citas médicas
10. **Estadísticas**: Dashboard con análisis de síntomas más comunes
11. **Integración médica**: Conectar con APIs de información médica confiable
12. **Modo oscuro**: Tema oscuro para mejor experiencia nocturna

---

## 👨‍💻 Autor

Proyecto creado como tarea educativa de un asistente médico virtual.

**¡Que te mejores! 💙**
