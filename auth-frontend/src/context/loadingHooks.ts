import { useContext } from 'react';
import { LoadingContext } from './loadingContext.js';
import type { LoadingContextType } from './loadingContext.js';

// Hook personalizado para usar el contexto de carga
export const useLoading = (): LoadingContextType => useContext(LoadingContext);
