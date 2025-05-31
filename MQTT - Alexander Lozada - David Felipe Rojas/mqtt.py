import paho.mqtt.client as mqtt
import ssl
import json
import time
import os
from dotenv import load_dotenv
from requests.exceptions import RequestException, Timeout
import requests
from mongo_utils import guardar_dato, sincronizar_periodicamente

load_dotenv()

LOCAL_MQTT_HOST = os.getenv("LOCAL_MQTT_HOST")
LOCAL_MQTT_PORT = int(os.getenv("LOCAL_MQTT_PORT"))
LOCAL_TOPIC = os.getenv("LOCAL_TOPIC")
FLASK_ENDPOINT = os.getenv("FLASK_ENDPOINT")

EMQX_BROKER = os.getenv("EMQX_BROKER")
EMQX_PORT = int(os.getenv("EMQX_PORT"))
EMQX_TOPIC_PREFIX = os.getenv("EMQX_TOPIC_PREFIX")
EMQX_USERNAME = os.getenv("EMQX_USERNAME")
EMQX_PASSWORD = os.getenv("EMQX_PASSWORD")
EMQX_CLIENT_ID = os.getenv("EMQX_CLIENT_ID")
EMQX_CA_CERT = os.getenv("EMQX_CA_CERT")


def enviar_a_emqx(payload):
    try:
        client = mqtt.Client(client_id=EMQX_CLIENT_ID)
        client.username_pw_set(EMQX_USERNAME, EMQX_PASSWORD)
        client.tls_set(ca_certs=EMQX_CA_CERT, tls_version=ssl.PROTOCOL_TLSv1_2)
        client.connect(EMQX_BROKER, EMQX_PORT)
        client.loop_start()

        client.publish(EMQX_TOPIC_PREFIX, json.dumps(payload, ensure_ascii=False))
        print(f"📡 Enviado a EMQX: {EMQX_TOPIC_PREFIX}")

        time.sleep(1)
        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print("⚠️ Error al enviar a EMQX:", str(e))


def enviar_a_flask(payload):
    try:
        response = requests.post(FLASK_ENDPOINT, json=payload, timeout=(3, 5))
        print("📤 Enviado a Flask. Código:", response.status_code)
        return True
    except Timeout:
        print("⏱️ Timeout al conectar con Flask - Continuando sin enviar")
    except RequestException as e:
        print(f"❌ Error de conexión con Flask ({type(e).__name__}) - Continuando sin enviar: {str(e)}")
    except Exception as e:
        print(f"❌ Error inesperado al enviar a Flask - Continuando sin enviar: {str(e)}")
    return False


def procesar_payload(topic, raw_payload):
    try:
        data = json.loads(raw_payload.decode())
        print("📦 Payload bruto:", data)

        if topic == "invernadero/imagen":
            enviar_a_flask(data)
            return

        zona = "invernadero"
        if "temperatura" in data:
            temp = f"{data['temperatura']}°C"
            guardar_dato({"zona": zona, "tipo": "temperatura", "valor": temp})
            enviar_a_emqx({"zona": zona, "tipo": "temperatura", "valor": temp})

        if "humedad" in data:
            hum = f"{data['humedad']}%"
            guardar_dato({"zona": zona, "tipo": "humedad", "valor": hum})
            enviar_a_emqx({"zona": zona, "tipo": "humedad", "valor": hum})

    except Exception as e:
        print("❌ Error al procesar payload:", str(e))


# ─── Callback MQTT ─────────────────────────────────────────────────────────────
def on_local_message(client, userdata, msg):
    print("✅ Mensaje recibido en tópico:", msg.topic)
    procesar_payload(msg.topic, msg.payload)


# ─── Cliente MQTT Local ───────────────────────────────────────────────────────
local_client = mqtt.Client()
local_client.on_message = on_local_message
local_client.connect(LOCAL_MQTT_HOST, LOCAL_MQTT_PORT, 60)
local_client.subscribe(LOCAL_TOPIC)

print("🚀 Escuchando MQTT local y reenviando a Flask / EMQX / Mongo...")

# Arranca la sincronización periódica en background
sincronizar_periodicamente(interval=60)
local_client.loop_forever()
