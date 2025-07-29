import { createContext } from 'react';

// Tipo para el contexto del tema
export type ThemeContextType = { 
  theme: 'light' | 'dark'; 
  toggleTheme: () => void; 
};

// Contexto del tema con valores predeterminados
export const ThemeContext = createContext<ThemeContextType>({ 
  theme: 'light', 
  toggleTheme: () => {} 
});
