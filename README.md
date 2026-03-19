# 🏥 Asistente Médico Virtual

Un asistente médico virtual simple y educativo que proporciona recomendaciones básicas para síntomas comunes, orientación sobre emergencias y consejos de primeros auxilios.

---

## 📋 Tabla de Contenidos

1. [¿Cómo funciona?](#-cómo-funciona)
2. [Estructura del proyecto](#-estructura-del-proyecto)
3. [Requisitos](#-requisitos)
4. [Instalación](#-instalación)
5. [Cómo ejecutar](#-cómo-ejecutar)
6. [Categorías de respuestas](#-categorías-de-respuestas)
7. [¿Cómo agregar más síntomas?](#-cómo-agregar-más-síntomas)
8. [Notas importantes](#-notas-importantes)

---

## 🔧 ¿Cómo funciona?

### Flujo general:

```
Usuario escribe un síntoma
        ↓
El navegador envía el texto a Flask (backend)
        ↓
Flask busca palabras clave en respuestas.json
        ↓
Si encuentra coincidencia → devuelve la respuesta
Si NO encuentra → devuelve mensaje genérico
        ↓
La respuesta aparece en el chat
```

### Proceso de búsqueda de palabras clave:

1. **Se convierte todo a minúsculas**: "Tengo FIEBRE" → "tengo fiebre"
2. **Se busca en las categorías**: Se revisan las categorías de `respuestas.json` (emergencia primero, luego las otras)
3. **Se validan las palabras clave**: Si la palabra del usuario coincide con una palabra clave, se devuelve la respuesta
4. **Prioridad de emergencia**: Si el usuario menciona una emergencia, se devuelve esa respuesta aunque coincida con otra categoría

**Ejemplo:**
- Usuario escribe: `"Me duele mucho la cabeza"`
- Se convierte a: `"me duele mucho la cabeza"`
- Se busca en palabras clave de "dolor_cabeza": `["dolor de cabeza", "migraña", "cefalea"]`
- ✅ Coincide con "dolor de cabeza" → se devuelve la respuesta

---

## 📁 Estructura del proyecto

```
AsistenteMedico/
├── app.py                  # Backend en Flask (servidor)
├── index.html              # Frontend (interfaz del usuario)
├── respuestas.json         # Base de datos de síntomas y respuestas
└── README.md               # Este archivo (documentación)
```

### `app.py` - Backend (Flask)

El servidor que procesa las solicitudes del usuario.

**Componentes principales:**

```python
from flask import Flask, request, jsonify, send_from_directory
import json

app = Flask(__name__)

# 1. Se cargan las respuestas al iniciar
with open("respuestas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. Función que busca la respuesta correcta
def obtener_respuesta(mensaje):
    mensaje = (mensaje or "").lower()
    
    # Prioridad: emergencias primero
    emergencia = data.get("emergencia")
    if emergencia:
        for keyword in emergencia["keywords"]:
            if keyword in mensaje:
                return emergencia["respuesta"]
    
    # Luego busca en otras categorías
    for categoria in data.values():
        if categoria is emergencia:
            continue
        for keyword in categoria["keywords"]:
            if keyword in mensaje:
                return categoria["respuesta"]
    
    return "No tengo suficiente información. Consulta a un profesional de salud."

# 3. Ruta para la página principal
@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

# 4. Ruta que recibe el mensaje del usuario
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("mensaje")
    respuesta = obtener_respuesta(user_msg)
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True)
```

**Explicación:**
- **Línea 1-3**: Importa Flask y JSON
- **Línea 6-8**: Lee `respuestas.json` al iniciar el servidor
- **Línea 10-29**: Función que busca palabras clave en el mensaje
- **Línea 31-38**: Ruta GET que sirve el archivo HTML
- **Línea 40-44**: Ruta POST que recibe mensajes y devuelve respuestas

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
- **Navegador web**: Chrome, Firefox, Safari, Edge

---

## 🚀 Instalación

### Paso 1: Instalar Flask

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install flask
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

## ⚠️ Notas importantes

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

1. **Agregar más síntomas**: Agrega diabetes, presión alta, alergias, etc.
2. **Base de datos**: Reemplaza JSON con una base de datos SQL (SQLite, MySQL)
3. **Historial de conversaciones**: Guarda las conversaciones para análisis
4. **Interfaz mejorada**: Usa Bootstrap o Tailwind CSS para un diseño más profesional
5. **Disponibilidad 24/7**: Despliega en la nube (Heroku, Replit, PythonAnywhere)
6. **IA avanzada**: Usa NLP (Natural Language Processing) para entender mejor el lenguaje natural
7. **Múltiples idiomas**: Agrega soporte para otros idiomas

---

## 👨‍💻 Autor

Proyecto creado como tarea educativa de un asistente médico virtual.

**¡Que te mejores! 💙**
