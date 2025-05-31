import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 12,
    paddingHorizontal: 4,
  },
  filter: {
    flexBasis: '30%',
    marginVertical: 6,
  },
  label: {
    fontWeight: '600',
    marginBottom: 4,
    color: '#37474F',
  },
  picker: {
    backgroundColor: '#ECEFF1',
    borderRadius: 8,
    paddingHorizontal: 6,
    height: 40,
    justifyContent: 'center',
  },
});

export default styles;
