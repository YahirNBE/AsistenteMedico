from flask import Flask, request, jsonify, send_from_directory
import json

app = Flask(__name__)

# Cargar respuestas
with open("respuestas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def obtener_respuesta(mensaje):
    mensaje = (mensaje or "").lower()

    # Primero revisamos las emergencias para priorizar la respuesta
    emergencia = data.get("emergencia")
    if emergencia:
        for keyword in emergencia["keywords"]:
            if keyword in mensaje:
                return emergencia["respuesta"]

    for categoria in data.values():
        # Ya manejamos emergencias arriba
        if categoria is emergencia:
            continue

        for keyword in categoria["keywords"]:
            if keyword in mensaje:
                return categoria["respuesta"]

    return "No tengo suficiente información. Consulta a un profesional de salud."

@app.route("/")
def home():
    # Permite abrir la interfaz desde http://127.0.0.1:5000/
    return send_from_directory('.', 'index.html')

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("mensaje")
    respuesta = obtener_respuesta(user_msg)
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True)