import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import { getAllDivestments } from '../services/api';
import DivestmentItem from '../components/DivestmentItem';

export default function DivestmentsScreen() {
  const [divestments, setDivestments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllDivestments()
      .then(data => setDivestments(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Your Divestments</Text>
      {loading ? (
        <ActivityIndicator size="large" />
      ) : (
        <FlatList
          data={divestments}
          keyExtractor={item => item.id.toString()}
          renderItem={({ item }) => <DivestmentItem divestment={item} />}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 10 },
});
