import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import './App.css';
import AppRouter from './routes/AppRouter';
import { useAuthStore } from './store/authStore';
// Usar importación relativa explícita con extensión para evitar problemas de resolución
import LoadingScreen from './components/common/LoadingScreen.tsx';
// Import theme and loading providers
import { ThemeProvider } from './theme/ThemeProvider';
import { LoadingProvider } from './context/LoadingProvider';
// Import global styles
import GlobalStyles from './theme/GlobalStyles.tsx';

// Crear una instancia de QueryClient para React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  // Estado para controlar si se ha completado la verificación de autenticación
  const [authChecked, setAuthChecked] = useState(false);
  const { init, isLoading } = useAuthStore();
  
  // Verificar la autenticación al cargar la aplicación
  useEffect(() => {
    const checkAuthentication = async () => {
      // Inicializar el estado de autenticación (verificando si el token es válido)
      await init();
      setAuthChecked(true);
    };
    
    checkAuthentication();
  }, [init]);
  
  // Mostrar pantalla de carga mientras se verifica la autenticación
  if (!authChecked || isLoading) {
    return <LoadingScreen message="Verificando sesión..." />;
  }
  
  return (
    <ThemeProvider>
      <LoadingProvider>
        <GlobalStyles />
        <QueryClientProvider client={queryClient}>
          <AppRouter />
        </QueryClientProvider>
      </LoadingProvider>
    </ThemeProvider>
  );
}

export default App
