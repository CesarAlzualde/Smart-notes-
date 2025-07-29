import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SecurityQuestionForm from '../components/SecurityQuestionForm';
import { useAuthStore } from '../../../store/authStore';

const SecurityQuestionSetup = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  
  // Si el usuario NO está autenticado, redirigir al login
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);
  
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Seguridad de la Cuenta</h1>
            <p>Configura tu pregunta de seguridad para proteger tu cuenta</p>
          </div>
          
          <SecurityQuestionForm />
          
          <div className="links">
            <p>
              <a href="#" onClick={(e) => { e.preventDefault(); navigate('/dashboard'); }}>
                Volver al Dashboard
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityQuestionSetup;
