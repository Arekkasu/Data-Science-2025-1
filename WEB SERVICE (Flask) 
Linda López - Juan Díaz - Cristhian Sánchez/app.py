import os
import base64
from flask import Flask, request, jsonify, send_file
from ultralytics import YOLO
from pymongo import MongoClient
import gridfs
from bson import ObjectId
from io import BytesIO
from PIL import Image
import numpy as np

# Inicialización de Flask
app = Flask(__name__)

# Configuración del modelo YOLO
MODEL_PATH = "best.pt"
model = YOLO(MODEL_PATH)

# Configuración de MongoDB
MONGO_URI = "mongodb+srv://admin:admin123@cluster0.jpyinve.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['hidroponico']
fs = gridfs.GridFS(db)
sensor_data_collection = db['sensor_data']
prediction_collection = db['prediction']

# Función auxiliar para convertir ObjectId a string
def serialize_document(doc):
    doc['_id'] = str(doc['_id'])
    return doc

# Endpoint unificado: subir imagen, guardar y analizar


@app.route('/upload-image', methods=['POST'])
def upload_image():
    data = request.get_json()
    if not data or 'imagen' not in data:
        return jsonify({'error': 'No image field in JSON'}), 400

    # Si la cadena base64 incluye el prefijo "data:image/...", eliminarlo
    base64_str = data['imagen']
    if base64_str.startswith("data:image"):
        base64_str = base64_str.split(",")[1]

    try:
        image_data = base64.b64decode(base64_str)
    except Exception:
        return jsonify({'error': 'Invalid base64 image data'}), 400

    # Guardar imagen en GridFS
    try:
        image_id = fs.put(image_data, content_type='image/jpeg')
    except Exception:
        return jsonify({'error': 'Failed to save image'}), 500

    # Convertir a formato compatible con YOLO (PIL + numpy)
    try:
        image_pil = Image.open(BytesIO(image_data)).convert("RGB")
        image_np = np.array(image_pil)
    except Exception:
        return jsonify({'error': 'Error processing image for analysis'}), 500

    # Analizar imagen con YOLO
    try:
        results = model(image_np)
    except Exception as e:
        return jsonify({'error': f'Model inference failed: {str(e)}'}), 500

    detections = []
    for result in results:
        for box in result.boxes:
            clase = int(box.cls[0])
            confianza = float(box.conf[0])
            detections.append({
                "class_id": clase,
                "class_name": model.names[clase],
                "confidence": confianza,
            })

    if not detections:
        # No hay detecciones, devolver mensaje sin guardar predicción
        return jsonify({
            'message': 'Image saved but no objects detected',
            'image_id': str(image_id)
        }), 200

    # Guardar predicción en MongoDB (solo la primera detección)
    prediction_doc = {
        "image_id": str(image_id),
        "imagen_base64": base64_str,
        "class_id": detections[0]["class_id"],
        "class_name": detections[0]["class_name"],
        "confidence": detections[0]["confidence"]
    }
    inserted = prediction_collection.insert_one(prediction_doc)
    prediction_doc['_id'] = str(inserted.inserted_id)

    return jsonify({
        'message': 'Image saved and analyzed successfully',
        "class_name": detections[0]["class_name"],
        "confidence": detections[0]["confidence"]
    }), 200

# Listar imágenes en GridFS
@app.route('/list-images', methods=['GET'])
def list_images():
    image_ids = [str(file._id) for file in fs.find()]
    return jsonify({'images': image_ids}), 200

# Obtener imagen por ID
@app.route('/get-image/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        file = fs.get(ObjectId(image_id))
        return send_file(BytesIO(file.read()), mimetype='image/jpeg')
    except Exception:
        return jsonify({'error': 'Image not found'}), 404

# Guardar datos de sensores
@app.route('/sensor-data', methods=['POST'])
def save_sensor_data():
    data = request.get_json()
    if not data or not all(k in data for k in ("zona", "tipo", "valor")):
        return jsonify({"error": "Missing fields: zona, tipo, valor"}), 400

    sensor_data_collection.insert_one({
        "zona": data["zona"],
        "tipo": data["tipo"],
        "valor": data["valor"]
    })

    return jsonify({"message": "Sensor data saved"}), 200

# Obtener datos de sensores
@app.route('/sensor-data', methods=['GET'])
def get_sensor_data():
    results = list(sensor_data_collection.find({}, {'_id': 0}))
    return jsonify({"data": results}), 200

# Obtener todas las predicciones
@app.route('/predictions', methods=['GET'])
def get_predictions():
    predictions = [serialize_document(doc) for doc in prediction_collection.find()]
    return jsonify({"predictions": predictions}), 200

# Ejecutar servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
