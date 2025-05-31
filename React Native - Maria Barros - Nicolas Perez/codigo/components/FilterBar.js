import React from 'react';
import { View, Text } from 'react-native';
import styles from './FilterBar.styles';
import { Picker } from '@react-native-picker/picker';

const FilterBar = ({ zonas, tipos, selectedZona, setSelectedZona, selectedTipo, setSelectedTipo, selectedFecha, setSelectedFecha }) => {
  return (
    <View style={styles.container}>
      <View style={styles.filter}>
        <Text style={styles.label}>Zona:</Text>
        <Picker
          selectedValue={selectedZona}
          onValueChange={(value) => setSelectedZona(value)}
          style={styles.picker}
        >
          <Picker.Item label="Todas" value="todas" />
          {zonas.map((zona, index) => (
            <Picker.Item label={zona} value={zona} key={index} />
          ))}
        </Picker>
      </View>

      <View style={styles.filter}>
        <Text style={styles.label}>Tipo:</Text>
        <Picker
          selectedValue={selectedTipo}
          onValueChange={(value) => setSelectedTipo(value)}
          style={styles.picker}
        >
          <Picker.Item label="Todos" value="todos" />
          {tipos.map((tipo, index) => (
            <Picker.Item label={tipo} value={tipo} key={index} />
          ))}
        </Picker>
      </View>

      <View style={styles.filter}>
        <Text style={styles.label}>Fecha:</Text>
        <Picker
          selectedValue={selectedFecha}
          onValueChange={(value) => setSelectedFecha(value)}
          style={styles.picker}
        >
          <Picker.Item label="Todas" value="todas" />
          <Picker.Item label="Últimas 24 horas" value="24h" />
          <Picker.Item label="Últimos 3 días" value="3d" />
          <Picker.Item label="Última semana" value="7d" />
        </Picker>
      </View>
    </View>
  );
};


export default FilterBar;