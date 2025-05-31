import { useEffect, useState } from 'react';
import mqtt from 'mqtt';
import * as Notifications from 'expo-notifications';
import { saveAlerts, loadAlerts } from '../storage/alertStorage';

const MQTT_BROKER_URL = 'ws://broker.hivemq.com:8000/mqtt';
const MQTT_TOPIC = 'invernadero/alertas';

export const useMqtt = () => {
  const [client, setClient] = useState(null);
  const [messages, setMessages] = useState([]);

  //Carga los mensajes. Falta implementarlo con la base de datos.
  useEffect(() => {
    const init = async () => {
      const stored = await loadAlerts();
      setMessages(stored || []);
    };
    init();
  }, []);

  useEffect(() => {
    const mqttClient = mqtt.connect(MQTT_BROKER_URL);
    setClient(mqttClient);

    mqttClient.on('connect', () => {
      mqttClient.subscribe(MQTT_TOPIC);
    });

    mqttClient.on('message', (topic, message) => {
      try {
        const payload = JSON.parse(message.toString());

        if (!payload.zona || !payload.tipo || !payload.valor) return;

        const newMessage = {
          zona: payload.zona,
          tipo: payload.tipo,
          valor: payload.valor,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => {
          const updated = [newMessage, ...prev].slice(0, 50);
          saveAlerts(updated);
          return updated;
        });

        Notifications.scheduleNotificationAsync({
          content: {
            title: `⚠️ Alerta en ${newMessage.zona}`,
            body: `${newMessage.tipo}: ${newMessage.valor}`,
          },
          trigger: null,
        });

      } catch (e) {
        console.error('Error al procesar mensaje MQTT:', e);
      }
    });

    return () => {
      mqttClient.end();
    };
  }, []);

  return { messages };
};
