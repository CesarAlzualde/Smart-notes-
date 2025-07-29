import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import RegisterForm from '../components/RegisterForm';
import { useAuthStore } from '../../../store/authStore';

const Register = () => {
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
            <p>Crea una nueva cuenta para acceder a todas las funcionalidades</p>
          </div>
          
          <RegisterForm />
        </div>
      </div>
    </div>
  );
};

export default Register;
