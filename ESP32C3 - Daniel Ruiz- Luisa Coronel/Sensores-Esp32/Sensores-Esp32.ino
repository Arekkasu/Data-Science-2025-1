#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// Configuración WiFi
const char* ssid = "OneScreen Display 3415";
const char* password = "ia20232023";

// Configuración MQTT
const char* mqtt_server = "192.168.45.64";
const int mqtt_port = 1887;
WiFiClient espClient;
PubSubClient client(espClient);

// Sensor DHT22
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Pines de actuadores
#define PIN_VENT  3  // Ventilador
#define PIN_BOMB  2  // Bombilla

// Temporizador de lectura
unsigned long lastSensorSend = 0;
const unsigned long interval = 5000; // 5 segundos

// Modo de operación
bool modoAutomatico = true;
bool bombillaManualEstado = false;

// Conectar a WiFi
void setup_wifi() {
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi conectado");
}

// Manejo de mensajes MQTT
void callback(char* topic, byte* payload, unsigned int length) {
  String mensaje;
  for (int i = 0; i < length; i++) {
    mensaje += (char)payload[i];
  }

  Serial.printf("📩 Mensaje recibido en [%s]: %s\n", topic, mensaje.c_str());

  if (String(topic) == "invernadero/bombilla") {
    mensaje.trim();

    if (mensaje == "auto") {
      modoAutomatico = true;
      Serial.println("🔁 Modo automático activado");
    } else if (mensaje == "on") {
      modoAutomatico = false;
      bombillaManualEstado = true;
      Serial.println("💡 Bombilla encendida (modo manual)");
    } else if (mensaje == "off") {
      modoAutomatico = false;
      bombillaManualEstado = false;
      Serial.println("💡 Bombilla apagada (modo manual)");
    } else {
      Serial.println("⚠️ Comando no reconocido");
    }
  }
}

// Reconectar si se pierde la conexión
void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando al broker MQTT...");
    if (client.connect("ESP32C3_Hidroponico")) {
      Serial.println("¡Conectado!");
      client.publish("invernadero/status", "online");
      client.subscribe("invernadero/bombilla");
    } else {
      Serial.print("Fallo, rc=");
      Serial.print(client.state());
      Serial.println(" reintentando en 5s");
      delay(5000);
    }
  }
}

// Envío confiable por MQTT
void sendSensorData(float temperatura, float humedad) {
  String payload = String("{\"temperatura\":") + temperatura +
                   ",\"humedad\":" + humedad +
                   ",\"modo\":\"" + (modoAutomatico ? "auto" : "manual") + "\"}";

  while (!client.publish("invernadero/sensores", payload.c_str())) {
    Serial.println("❌ Error al enviar por MQTT. Reintentando...");
    delay(1000);  // Espera 1 segundo antes de reintentar
  }
  Serial.println("✅ Datos enviados por MQTT");
}

// Configuración inicial
void setup() {
  Serial.begin(115200);

  pinMode(PIN_VENT, OUTPUT);
  pinMode(PIN_BOMB, OUTPUT);

  digitalWrite(PIN_VENT, LOW);
  digitalWrite(PIN_BOMB, LOW);

  dht.begin();
  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

// Loop principal
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastSensorSend > interval) {
    lastSensorSend = now;

    float temperatura = dht.readTemperature();
    float humedad = dht.readHumidity();

    if (isnan(temperatura) || isnan(humedad)) {
      Serial.println("❌ Error leyendo del DHT22");
      return;
    }

    if (modoAutomatico) {
      if (temperatura > 30.0) {
        digitalWrite(PIN_VENT, HIGH);
        digitalWrite(PIN_BOMB, LOW);
      } else if (temperatura < 20.0) {
        digitalWrite(PIN_VENT, LOW);
        digitalWrite(PIN_BOMB, HIGH);
      } else {
        digitalWrite(PIN_VENT, LOW);
        digitalWrite(PIN_BOMB, LOW);
      }
    } else {
      digitalWrite(PIN_BOMB, bombillaManualEstado ? HIGH : LOW);
      digitalWrite(PIN_VENT, LOW);
    }

    Serial.printf("🌡 Temp: %.2f °C, 💧 Humedad: %.2f %%\n", temperatura, humedad);
    sendSensorData(temperatura, humedad);
  }
}
