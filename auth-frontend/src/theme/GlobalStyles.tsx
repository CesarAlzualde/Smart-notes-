import React from 'react';
import { Global, css } from '@emotion/react';
import { useTheme, useCurrentTheme } from './themeHooks';

export const GlobalStyles: React.FC = () => {
  // Obtener el objeto tema de Emotion
  const theme = useCurrentTheme();
  // Obtener el contexto del tema (light/dark)
  const { theme: themeMode } = useTheme();

  return (
    <Global
      styles={css`
        /* Reset y estilos base */
        *, *::before, *::after {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }
        
        /* Estilos del html y body */
        html, body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
          font-size: 16px;
          line-height: 1.5;
          background-color: ${theme.background};
          color: ${theme.text};
          transition: background-color 0.3s ease, color 0.3s ease;
          overflow: hidden;
          height: 100%;
          width: 100%;
        }
        
        /* Contenedor raíz */
        #root {
          height: 100%;
          width: 100%;
        }
        
        /* Estilos de tipografía reducidos */
        h1, h2, h3, h4, h5, h6 {
          margin-bottom: 0.5rem;
          font-weight: 600;
          line-height: 1.2;
        }
        
        h1 { font-size: 1.75rem; }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.25rem; }
        h4 { font-size: 1.125rem; }
        h5 { font-size: 1rem; }
        h6 { font-size: 0.875rem; }
        
        p {
          margin-bottom: 0.75rem;
        }
        
        /* Enlaces */
        a {
          color: ${theme.primary};
          text-decoration: none;
          transition: color 0.2s ease;
        }
        
        a:hover {
          color: ${theme.primaryDark};
        }
        
        /* Estilos para formularios con espacios reducidos */
        form {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        
        label {
          display: block;
          margin-bottom: 0.25rem;
          font-weight: 500;
          font-size: 0.875rem;
        }
        
        input, textarea, select {
          padding: 0.5rem;
          border: 1px solid ${theme.input.border};
          border-radius: 0.25rem;
          font-size: 0.875rem;
          background-color: ${theme.input.background};
          color: ${theme.text};
          transition: border-color 0.2s ease;
          width: 100%;
          
          &:focus {
            outline: none;
            border-color: ${theme.input.focusBorder};
          }
          
          &::placeholder {
            color: ${theme.input.placeholder};
          }
        }
        
        /* Estilo de botones ya gestionado por componente Button */
        
        /* Estilos para cards con menos espacio */
        .card {
          background-color: ${theme.card.background};
          border-radius: 0.5rem;
          box-shadow: ${theme.card.shadow};
          overflow: hidden;
          transition: box-shadow 0.3s ease;
          padding: 0.75rem;
          margin-bottom: 0.75rem;
          
          &:hover {
            box-shadow: ${theme.card.highlightShadow};
          }
        }
        
        /* Grid con menos espacio */
        .grid {
          display: grid;
          grid-template-columns: repeat(12, 1fr);
          gap: 0.75rem;
        }
        
        /* Listas con menos espacio */
        ul, ol {
          padding-left: 1.25rem;
          margin-bottom: 0.75rem;
        }
        
        li {
          margin-bottom: 0.25rem;
        }
        
        /* Tablas con menos espacio */
        table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 0.75rem;
        }
        
        th, td {
          padding: 0.5rem;
          text-align: left;
          border-bottom: 1px solid ${theme.border};
        }
        
        th {
          font-weight: 600;
        }
        
        /* Estilos de scrollbar personalizados */
        ::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        
        ::-webkit-scrollbar-track {
          background: ${themeMode === 'light' ? '#f1f1f1' : '#333'};
        }
        
        ::-webkit-scrollbar-thumb {
          background: ${themeMode === 'light' ? '#c1c1c1' : '#666'};
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: ${themeMode === 'light' ? '#a8a8a8' : '#888'};
        }
        
        /* Clases de utilidad */
        .text-muted {
          color: ${theme.textMuted};
        }
        
        .text-primary {
          color: ${theme.primary};
        }
        
        .bg-primary {
          background-color: ${theme.primary};
          color: white;
        }
        
        /* Estilos específicos de bootstrap para dropdown */
        .dropdown-menu {
          background-color: ${theme.card.background};
          border: 1px solid ${theme.border};
          border-radius: 0.25rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          padding: 0.25rem 0;
        }
        
        .dropdown-item {
          padding: 0.5rem 1rem;
          color: ${theme.text};
          transition: background-color 0.2s ease;
          
          &:hover {
            background-color: ${themeMode === 'light' ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)'};
          }
        }
        
        .dropdown-divider {
          border-top: 1px solid ${theme.border};
          margin: 0.25rem 0;
        }
      `}
    />
  );
};

export default GlobalStyles;
