import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import './Unauthorized.css';

const Unauthorized = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  const handleGoBack = () => {
    // Si el usuario está autenticado, ir al dashboard
    // Si no, ir a la página de login
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };
  
  return (
    <div className="unauthorized-page">
      <div className="unauthorized-container">
        <div className="unauthorized-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line>
          </svg>
        </div>
        
        <h1>Acceso denegado</h1>
        
        <p className="error-message">
          No tienes permisos para acceder a esta página.
        </p>
        
        <p className="error-details">
          Esta área está restringida a usuarios con roles específicos.
          Si crees que deberías tener acceso, contacta al administrador del sistema.
        </p>
        
        <div className="action-buttons">
          <button
            onClick={handleGoBack}
            className="btn-primary"
          >
            {isAuthenticated ? 'Volver al Dashboard' : 'Iniciar sesión'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Unauthorized;
