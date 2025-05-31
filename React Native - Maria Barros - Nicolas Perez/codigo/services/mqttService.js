import mqtt from "mqtt";
import { MQTT_CONFIG } from "../mqttConfig";


export function initMQTT(onMessage, onConnect, onError, onClose) {  //recibe 4 parametros: onMessage (cada vez que llega un mensaje)
//onConnect(cuando hay conexión con el broker), onError(error en la conexión) y onClose(cuando se cierra la conexión)



  const client = mqtt.connect(MQTT_CONFIG.brokerUrl, MQTT_CONFIG.options); //se conecta al broker definido en mqttConfig.js

  client.on('connect', () => {
    onConnect();
    client.subscribe(MQTT_CONFIG.topic);
  });

  client.on('message', (topic, message) => {
    onMessage(message);
  });

  client.on('close', onClose);
  client.on('error', (err) => onError(err));

  return client;
}

//inicializa la conexión mqtt