from pymongo import MongoClient, errors
from datetime import datetime
import os
from dotenv import load_dotenv
import threading
import time

load_dotenv()


LOCAL_MONGO_URI = os.getenv("MONGO_URL_LOCAL")
CLOUD_MONGO_URI = os.getenv("MONGO_URL_NUBE")
DB_NAME = os.getenv("MONGO_DB", "hidroponico")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "data_sensors")


# Conectar a Mongo local
local_client = MongoClient(LOCAL_MONGO_URI)
local_collection = local_client[DB_NAME][COLLECTION_NAME]
print("💾 Conectado a Mongo local")

# Intentar conectar a Mongo nube
try:
    cloud_client = MongoClient(CLOUD_MONGO_URI, serverSelectionTimeoutMS=3000)
    cloud_client.server_info()
    cloud_collection = cloud_client[DB_NAME][COLLECTION_NAME]
    print("☁️ Conectado a Mongo nube")
except errors.ServerSelectionTimeoutError:
    cloud_collection = None
    print("⚠️ No se pudo conectar a MongoDB en la nube")


# Función guardar_dato actualizada
def guardar_dato(payload):

    timestamp = datetime.now().isoformat()
    payload["timestamp"] = timestamp
    # Insertar en MongoDB local
    result = local_collection.insert_one(payload)
    print("✅ Guardado en Mongo local")

    if cloud_collection is not None:
        try:
            # Crear copia sin _id para la nube
            payload_cloud = payload.copy()
            payload_cloud.pop('_id', None)  # Eliminar _id si existe
            # Insertar en MongoDB nube
            cloud_collection.insert_one(payload_cloud)
            print("✅ Guardado en Mongo nube y marcado como sincronizado")
        except Exception as e:
            print("⚠️ Error al sincronizar con nube:", e)

# Intentar sincronizar datos locales no sincronizados
def sincronizar_datos():
    if cloud_collection is None:
        print("🌐 Nube no disponible, no se puede sincronizar")
        return

    pendientes = local_collection.find()
    for doc in pendientes:
        try:
            # Verificamos si ya existe en la nube por timestamp
            if cloud_collection.find_one({"timestamp": doc.get("timestamp")}):
                continue

            doc_copy = doc.copy()
            doc_copy.pop('_id', None)
            cloud_collection.insert_one(doc_copy)
            print(f"🔄 Sincronizado con la nube: {doc['tipo']} - {doc['valor']}")
        except Exception as e:
            print("⚠️ Error sincronizando un documento:", e)




def sincronizar_periodicamente(interval=60):
    def worker():
        global cloud_collection
        while True:
            if cloud_collection is None:
                try:
                    print("🔁 Intentando reconectar a MongoDB nube...")
                    new_client = MongoClient(CLOUD_MONGO_URI, serverSelectionTimeoutMS=3000)
                    new_client.server_info()
                    cloud_collection = new_client[DB_NAME][COLLECTION_NAME]
                    print("✅ Reconexión exitosa con MongoDB en la nube")
                except Exception as e:
                    print("❌ Fallo en reconexión a Mongo nube:", e)

            if cloud_collection is not None:
                try:
                    cloud_collection.database.client.admin.command('ping')
                    sincronizar_datos()
                except Exception as e:
                    print("🌐 Error al acceder a la nube durante sincronización:", e)
                    cloud_collection = None  # Forzar reconexión

            time.sleep(interval)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
