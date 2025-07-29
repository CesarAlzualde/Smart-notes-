import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import { useAuthStore } from '../../../store/authStore';

const Login = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  
  // Si el usuario ya está autenticado, redirigir al dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);
  
  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>SMART NOTES</h1>
            <p>Ingresa a tu cuenta para continuar</p>
          </div>
          
          <LoginForm />
        </div>
      </div>
    </div>
  );
};

export default Login;
