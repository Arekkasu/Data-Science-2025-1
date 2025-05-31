export const MQTT_CONFIG = {
  brokerUrl: 'wss://i12b8e78.ala.us-east-1.emqxsl.com:8084/mqtt', // Usar WSS (WebSocket Secure)
  topic: 'hidroponico/datos', // El mismo topic que usas en tu Python
  options: {
    username: 'mqttRP', // Usuario que definiste
    password: '1234', // Contraseña que definiste
    clientId: 'react-native-' + Math.random().toString(16).substr(2, 8),
    keepalive: 60,
    reconnectPeriod: 1000,
    clean: true,
    protocolVersion: 4, // Usar MQTT v3.1.1
    rejectUnauthorized: false, // OJO: Solo para desarrollo, en producción usa certificados
    // Para producción deberías incluir el certificado CA
    // ca: require('./path/to/emqxsl-ca.crt') 
  }
};
