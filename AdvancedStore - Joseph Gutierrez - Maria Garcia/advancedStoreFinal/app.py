# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:14:45 2025

@author: Joseph (YO)
"""

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import gridfs_utils
from io import BytesIO

app = Flask(__name__)


#peticion para subir los datos del sensor
@app.route("/upload-data", methods=["POST"])
def upload_data():
    try:
        
        content = request.get_json()
        
        data = {
            "tipo_sensor": content.get("tipo_sensor"),
            "valor": float(content.get("valor")),
            "unidad": content.get("unidad"),
            "device_id": content.get("device_id", "esp32"),
        }
        doc_id = gridfs_utils.save_sensor_data(data)
        if not doc_id:
            return jsonify({"status": "skipped", "message": "Data received too soon, not stored."}), 200
        return jsonify({"status": "success", "document_id": str(doc_id)}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
#peticion para subir la imagen
@app.route("/upload-image", methods=["POST"])
def upload_image():
    try:
        image = request.files.get("image")
        if not image:
            return jsonify({"status": "error", "message": "No image provided"}), 400

        image.filename = secure_filename(image.filename)
        image_file_id = gridfs_utils.save_file(image)
        return jsonify({"status": "success", "file_id": str(image_file_id)}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


#obtener los  sensores
@app.route("/data", methods=["GET"])
def get_all_data():
    try:
        data = gridfs_utils.get_all_sensor_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
#obtener imagenes
@app.route("/images", methods=["GET"])
def list_images():
    try:
        files = gridfs_utils.list_all_files()
        return jsonify(files)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


#obtener una imagen por id
@app.route("/image/<file_id>", methods=["GET"])
def get_image(file_id):
    try:
        file_data, content_type = gridfs_utils.get_file_by_id(file_id)
        return send_file(BytesIO(file_data), mimetype=content_type)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404

#obtener sensor por tipo
@app.route("/sensor-data/<tipo_sensor>", methods=["GET"])
def get_data_by_tipo_sensor(tipo_sensor):
    try:
        data = gridfs_utils.get_sensor_data_by_type(tipo_sensor)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5000)

