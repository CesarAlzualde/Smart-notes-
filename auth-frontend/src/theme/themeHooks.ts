import { useContext } from 'react';
import type { ThemeContextType } from './themeContext';
import type { Theme } from './themeConstants';
import { ThemeContext } from './themeContext';
import { lightTheme, darkTheme } from './themeConstants';

// Hook para obtener el contexto del tema
export const useTheme = (): ThemeContextType => useContext(ThemeContext);

// Hook para obtener el tema actual basado en la selección (light/dark)
export const useCurrentTheme = (): Theme => {
  const { theme } = useContext(ThemeContext);
  return theme === 'light' ? lightTheme : darkTheme;
};
