import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import LoadingScreen from '../components/common/LoadingScreen';

interface PrivateRouteProps {
  requiredRole?: string;
}

const PrivateRoute = ({ requiredRole }: PrivateRouteProps) => {
  // Obtenemos el estado de autenticación y el usuario del store
  const { isAuthenticated, user, isLoading } = useAuthStore();
  
  // Mientras se está verificando la autenticación, mostramos el loading
  if (isLoading) {
    return <LoadingScreen message="Verificando acceso..." />;
  }
  
  // Si el usuario no está autenticado, redirigimos al login
  if (!isAuthenticated) {
    console.log('Usuario no autenticado, redirigiendo a login');
    return <Navigate to="/login" replace />;
  }
  
  // Si se requiere un rol específico, verificar si el usuario tiene ese rol
  if (requiredRole && user?.role !== requiredRole) {
    console.log(`Usuario no tiene rol ${requiredRole}, redirigiendo a unauthorized`);
    return <Navigate to="/unauthorized" replace />;
  }
  
  console.log('Usuario autenticado, renderizando ruta privada');
  // Si todo está bien, renderizar los componentes hijos
  return <Outlet />;
};

export default PrivateRoute;
