from flask import Flask, request, jsonify, send_from_directory
import json
import numpy as np

app = Flask(__name__)

# ==============================
# 1. CARGAR RESPUESTAS
# ==============================
with open("respuestas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

categorias = list(data.keys())  # ['saludos', 'fiebre', ...]

# ==============================
# 2. CREAR VOCABULARIO
# ==============================
# Aquí convertimos palabras en números
vocabulario = set()

for categoria in data.values():
    for keyword in categoria["keywords"]:
        for palabra in keyword.split():
            vocabulario.add(palabra)

vocabulario = list(vocabulario)

# ==============================
# 3. VECTOR DE TEXTO
# ==============================
def vectorizar(texto):
    texto = texto.lower()
    vector = [0] * len(vocabulario)

    for i, palabra in enumerate(vocabulario):
        if palabra in texto:
            vector[i] = 1

    return np.array(vector)

# ==============================
# 4. CREAR NEURONAS (UNA POR CATEGORÍA)
# ==============================
class Neurona:
    def __init__(self, input_size):
        self.pesos = np.random.rand(input_size)
        self.bias = np.random.rand()

    def activar(self, x):
        return 1 / (1 + np.exp(-x))  # función sigmoide

    def predecir(self, x):
        return self.activar(np.dot(x, self.pesos) + self.bias)

# Creamos una neurona por categoría
neuronas = [Neurona(len(vocabulario)) for _ in categorias]

# ==============================
# 5. ENTRENAMIENTO
# ==============================
def entrenar():
    ejemplos = []

    # Generamos ejemplos automáticamente desde el JSON
    for idx, (nombre, categoria) in enumerate(data.items()):
        for keyword in categoria["keywords"]:
            ejemplos.append((keyword, idx))

    # Entrenamiento
    for _ in range(1000):
        for texto, etiqueta in ejemplos:
            x = vectorizar(texto)

            for i, neurona in enumerate(neuronas):
                y = 1 if i == etiqueta else 0  # one-hot

                pred = neurona.predecir(x)
                error = y - pred

                neurona.pesos += 0.1 * error * x
                neurona.bias += 0.1 * error

# Entrenamos al iniciar
entrenar()

# ==============================
# 6. CLASIFICACIÓN
# ==============================
def clasificar(mensaje):
    x = vectorizar(mensaje)

    resultados = [neurona.predecir(x) for neurona in neuronas]

    indice = np.argmax(resultados)
    return categorias[indice]

# ==============================
# 7. RESPUESTA FINAL
# ==============================

def obtener_respuesta(mensaje):
    x = vectorizar(mensaje)

    resultados = [neurona.predecir(x) for neurona in neuronas]
    indice = int(np.argmax(resultados))

    categoria = categorias[indice]

    probabilidad = resultados[indice]
    if probabilidad < 0.5:
        return {
        "respuesta": "No estoy muy seguro de lo que quieres decir 🤔 ¿Puedes elegir una categoría?",
        "categoria": "desconocido",
        "opciones": categorias
    }

    return {
        "respuesta": data[categoria]["respuesta"],
        "categoria": categoria,
        "probabilidad": float(probabilidad)
    }
# ==============================
# 8. RUTAS FLASK (igual que antes)
# ==============================
@app.route("/")
def home():
    return send_from_directory('.', 'index.html')


@app.route("/aprender", methods=["POST"])
def aprender():
    mensaje = request.json.get("mensaje")
    categoria = request.json.get("categoria")
    
    # Agregar al JSON
    if categoria in data:
        data[categoria]["keywords"].append(mensaje)
    
    # Guardar JSON
    with open("respuestas.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Re-entrenar modelo (actualizar vocabulario y neuronas)
    global vocabulario, neuronas
    vocabulario = set()
    for cat in data.values():
        for keyword in cat["keywords"]:
            for palabra in keyword.split():
                vocabulario.add(palabra)
    vocabulario = list(vocabulario)
    
    neuronas = [Neurona(len(vocabulario)) for _ in categorias]
    entrenar()
    
    return jsonify({"success": True, "mensaje": f"¡Aprendí! Ahora '{mensaje}' pertenece a '{categoria}'"})
    
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("mensaje")
    resultado = obtener_respuesta(user_msg)
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(debug=True)