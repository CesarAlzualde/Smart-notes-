import { createContext } from 'react';

// Definir el tipo del contexto de carga
export interface LoadingContextType {
  isLoading: boolean;
  message: string | null;
  startLoading: (message?: string) => void;
  stopLoading: () => void;
}

// Crear el contexto con un valor predeterminado
export const LoadingContext = createContext<LoadingContextType>({
  isLoading: false,
  message: null,
  startLoading: () => {},
  stopLoading: () => {},
});
