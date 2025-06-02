# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:16:34 2025

@author: Joseph (YO)
"""

import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import gridfs
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_CLUSTER')}/{os.getenv('MONGO_PARAMS')}"
client = MongoClient(MONGO_URI)
db = client[os.getenv("MONGO_DB")]
fs = gridfs.GridFS(db)

from datetime import timedelta
#Verifica quue la informacion se guarde cada min_interval_seconds (10 segundos)
def should_store_data(sensor_type, device_id, min_interval_seconds=10):
    last = db.sensor_data.find_one(
        {"tipo_sensor": sensor_type, "device_id": device_id},
        sort=[("timestamp", -1)]
    )
    if not last:
        return True
    return datetime.utcnow() - last["timestamp"] >= timedelta(seconds=min_interval_seconds)

#guarda la imagen
def save_file(file):
    return fs.put(file.read(), filename=file.filename, content_type=file.content_type)

#obtiene una imagen según su id
def get_file_by_id(file_id):
    file = fs.get(ObjectId(file_id))
    return file.read(), file.content_type

#obtiene todas las imagenes
def list_all_files():
    files = fs.find()
    return [{"file_id": str(f._id), "filename": f.filename, "content_type": f.content_type} for f in files]

#guarda la informacion de los sensores (cada x tiempo)
def save_sensor_data(data, min_interval_seconds=10):
    if not should_store_data(data.get("tipo_sensor"), data.get("device_id"), min_interval_seconds):
        return None
    doc = {
        "tipo_sensor": data.get("tipo_sensor", "unknown"),
        "valor": data.get("valor"),
        "unidad": data.get("unidad"),
        "timestamp": datetime.utcnow(),
        "device_id": data.get("device_id", "esp32"),
        }
    return db.sensor_data.insert_one(doc).inserted_id

#obtener informacion por sensor
def get_sensor_data_by_type(tipo_sensor):
    data = db.sensor_data.find({"tipo_sensor": tipo_sensor}, {"_id": 0})
    return list(data)

#obtener la informacion de todos los sensores
def get_all_sensor_data():
    data = db.sensor_data.find({}, {"_id": 0})
    return list(data)

