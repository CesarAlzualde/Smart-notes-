import React, { useState } from 'react';
import styled from '@emotion/styled';
import type { Theme } from '../theme/themeConstants';
import { LoadingContext } from './loadingContext';

// Componente Spinner para usar dentro del contexto
const SpinnerOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(3px);
`;

const SpinnerContainer = styled.div`
  position: relative;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SpinnerCircle = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: ${props => (props.theme as Theme).spinner.primary};
  border-bottom-color: ${props => (props.theme as Theme).spinner.secondary};
  animation: spin 1.2s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  &:before {
    content: "";
    position: absolute;
    top: 4px;
    left: 4px;
    right: 4px;
    bottom: 4px;
    border-radius: 50%;
    border: 4px solid transparent;
    border-right-color: ${props => (props.theme as Theme).spinner.primary};
    border-left-color: ${props => (props.theme as Theme).spinner.secondary};
    animation: spin 1.8s linear infinite reverse;
  }
`;

const LoadingText = styled.div`
  margin-top: 16px;
  font-weight: 500;
  font-size: 1.1rem;
  color: white;
  text-align: center;
  max-width: 80%;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
`;

// Nota: LoadingContext y LoadingContextType ahora se importan desde loadingContext.ts
// El hook useLoading se ha movido a loadingHooks.ts

// Props para el proveedor
interface LoadingProviderProps {
  children: React.ReactNode;
}

// Componente proveedor que envuelve la aplicación
export const LoadingProvider: React.FC<LoadingProviderProps> = ({ children }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // Función para iniciar el estado de carga
  const startLoading = (message: string = 'Cargando...') => {
    setMessage(message);
    setIsLoading(true);
  };

  // Función para detener el estado de carga
  const stopLoading = () => {
    setIsLoading(false);
    setMessage(null);
  };

  return (
    <LoadingContext.Provider value={{ isLoading, message, startLoading, stopLoading }}>
      {children}
      {isLoading && (
        <SpinnerOverlay>
          <div>
            <SpinnerContainer>
              <SpinnerCircle />
            </SpinnerContainer>
            {message && <LoadingText>{message}</LoadingText>}
          </div>
        </SpinnerOverlay>
      )}
    </LoadingContext.Provider>
  );
};

export default LoadingProvider;
