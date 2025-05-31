import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true, //muestra la alerta
    shouldPlaySound: true, //reproduce el sonido
    shouldSetBadge: false, 
  }),
});

//gestiona permisos de notificaciones
export async function registerForPushNotificationsAsync() {
  if (Device.isDevice) { //verifica si es un dispositivo fisico
    const { status: existingStatus } = await Notifications.getPermissionsAsync(); //verifica si ya tiene permisos
    let finalStatus = existingStatus;
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== 'granted') {
      alert('❌ No se obtuvieron permisos para notificaciones.');
    }
  } else {
    alert('⚠️ Las notificaciones solo funcionan en dispositivos físicos.');
  }
}

export async function sendAlertNotification(zona, tipo, valor) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: `🚨 Alerta en Zona ${zona}`,
      body: `${tipo.toUpperCase()}: ${valor}`,
      sound: true,
    },
    trigger: null, //se envía inmediatamente
  });
}
