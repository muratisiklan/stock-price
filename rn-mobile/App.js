import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import DivestmentsScreen from './screens/DivestmentsScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Divestments" component={DivestmentsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
