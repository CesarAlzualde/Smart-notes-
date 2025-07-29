
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useState } from 'react';
import { useAuthStore } from '../../../store/authStore';
import './Auth.css';
import './AuthModern.css'; // Nuevo archivo CSS para estilos modernos

// Esquema de validación para el formulario de login
// Definición más explícita para resolver problemas de tipo
const loginSchema = z.object({
  email: z
    .string()
    .email('Formato de correo electrónico inválido')
    .min(1, 'El correo electrónico es requerido'),
  password: z
    .string()
    .min(1, 'La contraseña es requerida'),
});

// Inferir el tipo directamente desde el esquema Zod
type LoginFormValues = z.infer<typeof loginSchema>;

const LoginForm = () => {
  const navigate = useNavigate();
  const { login, error, clearError, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  
  // Garantizar que React Hook Form use tipos compatibles
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
    mode: 'onChange' // Validación en tiempo real
  });
  
  const onSubmit = async (data: LoginFormValues) => {
    clearError(); // Limpiar errores previos
    
    try {
      await login(data.email, data.password);
      // Si el login es exitoso, el useEffect en el componente Login redirigirá al dashboard
    } catch (error) {
      console.error('Error durante el login:', error);
    }
  };
  
  // Alternar visibilidad de la contraseña
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  return (
    <div className="modern-form login-form">
      <h2>Iniciar Sesión</h2>
      
      {/* Botones de acceso social (sin funcionalidad) */}
      <div className="social-buttons">
        <button type="button" className="social-btn">
          Google
        </button>
        <button type="button" className="social-btn">
          Microsoft
        </button>
      </div>
      
      <div className="auth-divider">
        <span>o continúa con</span>
      </div>
      
      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          <div className="alert-content">{error}</div>
          <button onClick={clearError} className="alert-close">×</button>
        </div>
      )}
      
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <div className="form-group">
          <label htmlFor="email">Correo electrónico</label>
          <div className="input-wrapper">
            <span className="input-icon">📧</span>
            <input
              id="email"
              type="email"
              {...register('email')}
              className={`modern-input ${errors.email ? 'error' : ''}`}
              placeholder="nombre@ejemplo.com"
              autoComplete="email"
            />
          </div>
          {errors.email && <div className="error-text">{errors.email.message}</div>}
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Contraseña</label>
          <div className="input-wrapper">
            <span className="input-icon">🔒</span>
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              {...register('password')}
              className={`modern-input ${errors.password ? 'error' : ''}`}
              placeholder="Ingrese su contraseña"
              autoComplete="current-password"
            />
            <button 
              type="button" 
              className="password-toggle" 
              onClick={togglePasswordVisibility}
              aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
            >
              {showPassword ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
          {errors.password && <div className="error-text">{errors.password.message}</div>}
        </div>
        

        
        <div className="form-actions">
          <button 
            type="submit" 
            disabled={isLoading}
            className="btn-modern"
          >
            {isLoading ? (
              <>
                <svg className="spinner" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="4" />
                </svg>
                Iniciando sesión...
              </>
            ) : (
              'Iniciar Sesión'
            )}
          </button>
        </div>
        
        <div className="auth-links">
          <button type="button" onClick={() => navigate('/recover-password')} className="auth-link as-button">
            ¿Olvidaste tu contraseña?
          </button>
          <span style={{ color: '#000000' }}>
            ¿No tienes una cuenta? <button type="button" onClick={() => navigate('/register')} className="auth-link as-button">Registrarse</button>
          </span>
        </div>
      </form>
    </div>
  );
};

export default LoginForm;
