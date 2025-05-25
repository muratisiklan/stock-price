import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function DivestmentItem({ divestment }) {
  return (
    <View style={styles.card}>
      <Text style={styles.company}>{divestment.company}</Text>
      <Text>Quantity: {divestment.quantity}</Text>
      <Text>Unit Price: ${divestment.unit_price}</Text>
      <Text>Revenue: ${divestment.revenue}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#f5f5f5',
    padding: 15,
    marginBottom: 10,
    borderRadius: 10,
  },
  company: {
    fontWeight: 'bold',
    fontSize: 18,
    marginBottom: 5,
  },
});
