import AsyncStorage from '@react-native-async-storage/async-storage'; 

const STORAGE_KEY = 'alertas_mqtt';

export const saveAlerts = async (alerts) => {
  try {
    const json = JSON.stringify(alerts); //convierte las alertas a JSON
    await AsyncStorage.setItem(STORAGE_KEY, json); //guarda las alertas en el almacenamiento local
  } catch (e) {
    console.error('Error al guardar alertas', e);
  }
};

export const loadAlerts = async () => {
  try {
    const json = await AsyncStorage.getItem(STORAGE_KEY); //carga las alertas del almacenamiento local
    return json ? JSON.parse(json) : []; 
  } catch (e) {
    console.error('Error al cargar alertas', e);
    return [];
  }
};

