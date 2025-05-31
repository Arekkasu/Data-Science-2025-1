#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include "base64.h" // Archivo adicional para codificación Base64

// WiFi
const char* ssid = "OneScreen Display 3415";
const char* password = "ia20232023";

// MQTT
const char* mqtt_server = "192.168.45.64";  // Cambia según IP de tu broker
const int mqtt_port = 1887;
WiFiClient espClient;
PubSubClient client(espClient);

// Temporizador de envío
unsigned long lastCaptureTime = 0;
const unsigned long captureInterval = 10000; // cada 10 segundos

// Configuración de la cámara
void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sccb_sda = 26;
  config.pin_sccb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_CIF;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Error al iniciar la cámara: 0x%x\n", err);
  }
}

void setup_wifi() {
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando al broker MQTT...");
    if (client.connect("ESP32-CAM")) {
      Serial.println("conectado");
    } else {
      Serial.print("Fallo, rc=");
      Serial.print(client.state());
      Serial.println(" reintentando en 5 segundos");
      delay(5000);
    }
  }
}

void sendImageMQTT() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("❌ Error al capturar imagen");
    return;
  }

  String base64Image = base64::encode(fb->buf, fb->len);
  String jsonPayload = String("{\"imagen\":\"") + base64Image + "\"}";
  bool ok = client.publish("invernadero/imagen", (uint8_t*)jsonPayload.c_str(), jsonPayload.length(), false);

  // Reintento si falla el envío
  int retryCount = 0;
  while (!ok) {
    retryCount++;
    Serial.printf("❌ Fallo al enviar imagen (reintento %d)\n", retryCount);
    delay(1000);  // Espera de 1 segundo antes de reintentar

    // Verifica conexión MQTT antes de reintentar
    if (!client.connected()) {
      reconnect();
    }
    ok = client.publish("invernadero/imagen", (uint8_t*)jsonPayload.c_str(), jsonPayload.length(), false);
  }

  Serial.println("✅ Imagen enviada por MQTT");
  esp_camera_fb_return(fb);
}

void setup() {
  Serial.begin(115200);
  setupCamera();
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastCaptureTime > captureInterval) {
    lastCaptureTime = now;
    sendImageMQTT();
  }
}
