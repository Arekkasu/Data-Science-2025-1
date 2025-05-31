import { StyleSheet } from 'react-native';

export default StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 60,
    backgroundColor: '#ECEFF1', // Fondo suave gris-azulado
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    marginBottom: 16,
    textAlign: 'center',
    color: '#1565C0', // Azul fuerte y profesional
  },
  messagesContainer: {
    flex: 1,
    marginTop: 8,
  },
  messageBox: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#263238', // Gris oscuro azulado
    marginBottom: 2,
  },
  value: {
    fontSize: 14,
    fontWeight: '400',
    color: '#546E7A', // Gris medio
    marginBottom: 6,
  },
});
