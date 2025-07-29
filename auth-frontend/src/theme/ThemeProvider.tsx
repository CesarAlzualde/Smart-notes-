import React, { useState, useEffect } from 'react';
import { ThemeProvider as EmotionThemeProvider } from '@emotion/react';
import { ThemeContext } from './themeContext';
import { lightTheme, darkTheme } from './themeConstants';
import type { Theme } from './themeConstants';

// ThemeProvider ya no contiene las definiciones de tipos ni los temas
// Esas definiciones han sido movidas a themeContext.ts y themeConstants.ts

// Proveedor del tema
export const ThemeProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  // Obtener preferencia del tema del localStorage o usar el tema del sistema
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    // Primero intentamos obtener el tema guardado
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light' || savedTheme === 'dark') {
      return savedTheme;
    }
    
    // Si no hay tema guardado, usar la preferencia del sistema
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    // Valor por defecto
    return 'light';
  });
  
  // Función para cambiar de tema
  const toggleTheme = () => {
    setTheme(prevTheme => {
      const newTheme = prevTheme === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', newTheme);
      return newTheme;
    });
  };
  
  // Aplicar clase al elemento html cuando cambia el tema
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    
    // Opcional: Cambiar el color del theme-color para móviles
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute(
        'content', 
        theme === 'light' ? '#FFFFFF' : '#1E1E1E'
      );
    }
  }, [theme]);
  
  // Proveer el tema seleccionado y la función para cambiarlo
  // Cast the theme to the correct type
  const currentTheme = theme === 'light' ? lightTheme : darkTheme;
  
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <EmotionThemeProvider theme={currentTheme as Theme}>
        {children}
      </EmotionThemeProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;
