import React from 'react';
import { View, Text, Button } from 'react-native';
import styles from '../styles';
import { useState } from 'react';
import { es } from 'date-fns/locale';
import { format, parseISO } from 'date-fns';

const MessageList = ({ messages }) => {

  const [visibleCount, setVisibleCount] = useState(15);
  const formatearFecha = (timestamp) => {
    const fecha = parseISO(timestamp);
    const fechaFormateada = format(fecha, "dd 'de' MMMM yyyy, hh:mm a", { locale: es });
    return fechaFormateada
  }

  const capitalize = (text) =>
    text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();

  const mensajesVisibles = messages
    .filter((msg) => msg.zona && msg.tipo && msg.valor)
    .slice(0, visibleCount);

  const cargarMas = () => {
    setVisibleCount((prev) => prev + 15);
  };
  return (
    <>
      {mensajesVisibles.map((msg, index) => (
        <View key={index} style={styles.messageBox}>
          <Text style={styles.label}>
            📍 Zona: <Text style={styles.value}>{capitalize(msg.zona)}</Text>
          </Text>
          <Text style={styles.label}>
            ⚠️ Tipo: <Text style={styles.value}>{capitalize(msg.tipo)}</Text>
          </Text>
          <Text style={styles.label}>
            🌡 Mensaje: <Text style={styles.value}>{capitalize(msg.valor)}</Text>
          </Text>
          <Text style={styles.label}>
            📅 Fecha: <Text style={styles.value}>{formatearFecha(msg.timestamp)}</Text>
          </Text>
        </View>
      ))}

      {visibleCount < messages.length && (
        <View style={{ marginVertical: 10, alignItems: 'center' }}>
          <Button title="Cargar más" onPress={cargarMas} />
        </View>
      )}
    </>
  );
};

export default MessageList;
