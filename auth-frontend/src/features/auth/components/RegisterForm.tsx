import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuthStore } from '../../../store/authStore';
import './Auth.css';
import './AuthModern.css';

// Esquema de validación de contraseña
const passwordSchema = z
  .string()
  .min(8, 'La contraseña debe tener al menos 8 caracteres')
  .refine(
    (password) => /[A-Z]/.test(password),
    { message: 'La contraseña debe contener al menos una letra mayúscula' }
  )
  .refine(
    (password) => /[0-9]/.test(password),
    { message: 'La contraseña debe contener al menos un número' }
  );

// Esquema de validación completo para el formulario de registro
const registerSchema = z.object({
  username: z
    .string()
    .min(3, 'El nombre de usuario debe tener al menos 3 caracteres')
    .regex(/^[a-zA-Z0-9_]+$/, 'Solo se permiten letras, números y guiones bajos'),
  email: z
    .string()
    .email('Ingrese un correo electrónico válido'),
  name: z
    .string()
    .min(2, 'El nombre debe tener al menos 2 caracteres'),
  password: passwordSchema,
  confirmPassword: z.string(),
  acceptTerms: z
    .boolean()
    .refine((value) => value === true, {
      message: 'Debes aceptar los términos y condiciones',
    }),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Las contraseñas no coinciden',
  path: ['confirmPassword'],
});

// Tipo derivado del esquema
type RegisterFormValues = z.infer<typeof registerSchema>;

const RegisterForm = () => {
  const navigate = useNavigate();
  const { register: registerUser, error, clearError, isLoading } = useAuthStore();
  
  // Estados para la UI mejorada
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0); // 0: nada, 1: débil, 2: regular, 3: buena, 4: fuerte
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const { register, handleSubmit, formState: { errors }, watch } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: '',
      email: '',
      name: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false,
    },
    mode: 'onChange' // Validación en tiempo real
  });
  
  // Observar el valor de la contraseña para el indicador de fortaleza
  const watchPassword = watch('password');
  
  // Evaluar la fortaleza de la contraseña
  const evaluatePasswordStrength = (password: string): number => {
    if (!password) return 0;
    
    let strength = 0;
    // Longitud mínima
    if (password.length >= 8) strength += 1;
    // Contiene letras minúsculas
    if (/[a-z]/.test(password)) strength += 1;
    // Contiene letras mayúsculas
    if (/[A-Z]/.test(password)) strength += 1;
    // Contiene números
    if (/[0-9]/.test(password)) strength += 1;
    // Contiene caracteres especiales
    if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
    
    return Math.min(Math.floor(strength * 4 / 5), 4); // Escalar de 0-5 a 0-4
  };
  
  // Actualizar la fortaleza de la contraseña cuando cambie
  useEffect(() => {
    setPasswordStrength(evaluatePasswordStrength(watchPassword || ''));
  }, [watchPassword]);
  
  // Obtener el texto y clase CSS según la fortaleza de la contraseña
  const getPasswordStrengthInfo = (): { text: string; className: string } => {
    switch (passwordStrength) {
      case 0:
        return { text: '', className: '' };
      case 1:
        return { text: 'Débil', className: 'strength-weak' };
      case 2:
        return { text: 'Regular', className: 'strength-fair' };
      case 3:
        return { text: 'Buena', className: 'strength-good' };
      case 4:
        return { text: 'Fuerte', className: 'strength-strong' };
      default:
        return { text: '', className: '' };
    }
  };
  
  const strengthInfo = getPasswordStrengthInfo();

  const onSubmit = async (data: RegisterFormValues) => {
    // Extraer datos de usuario omitiendo campos de confirmación
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { confirmPassword, acceptTerms, ...userData } = data;
    
    clearError(); // Limpiar errores previos
    console.log('Iniciando registro con datos:', { ...userData, password: '[OCULTO]' });
    
    try {
      console.log('Llamando a función registerUser del authStore...');
      await registerUser(userData);
      console.log('Registro completado con éxito');
      setSuccessMessage('Registro exitoso. Ahora puedes iniciar sesión.');
      
      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        console.log('Redirigiendo a login...');
        navigate('/login');
      }, 2000);
    } catch (error) {
      console.error('Error durante el registro:', error);
    }
  };

  // Funciones para alternar la visibilidad de las contraseñas
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };
  
  return (
    <div className="modern-form register-form">
      <h2>Crear una nueva cuenta</h2>
      
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
        <span>o regístrate con tu correo</span>
      </div>
      
      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          <div className="alert-content">{error}</div>
          <button onClick={clearError} className="alert-close">×</button>
        </div>
      )}
      
      {successMessage && (
        <div className="alert alert-success">
          <span className="alert-icon">✅</span>
          <div className="alert-content">{successMessage}</div>
        </div>
      )}
      
      <form onSubmit={(e) => {
          e.preventDefault();
          handleSubmit(onSubmit)(e);
        }}>
        <div className="form-group">
          <label htmlFor="username">Nombre de usuario*</label>
          <div className="input-wrapper">
            <span className="input-icon">👤</span>
            <input
              id="username"
              type="text"
              {...register('username')}
              placeholder="Ingrese un nombre de usuario único"
              className={`modern-input ${errors.username ? 'error' : ''}`}
              autoComplete="username"
            />
          </div>
          {errors.username && <div className="error-text">{errors.username.message}</div>}
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Correo electrónico*</label>
          <div className="input-wrapper">
            <span className="input-icon">📧</span>
            <input
              id="email"
              type="email"
              {...register('email')}
              placeholder="ejemplo@correo.com"
              className={`modern-input ${errors.email ? 'error' : ''}`}
              autoComplete="email"
            />
          </div>
          {errors.email && <div className="error-text">{errors.email.message}</div>}
        </div>
        
        <div className="form-group">
          <label htmlFor="name">Nombre completo*</label>
          <div className="input-wrapper">
            <span className="input-icon">📝</span>
            <input
              id="name"
              type="text"
              {...register('name')}
              placeholder="Su nombre completo"
              className={`modern-input ${errors.name ? 'error' : ''}`}
              autoComplete="name"
            />
          </div>
          {errors.name && <div className="error-text">{errors.name.message}</div>}
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Contraseña*</label>
          <div className="input-wrapper">
            <span className="input-icon">🔒</span>
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              {...register('password')}
              placeholder="********"
              className={`modern-input ${errors.password ? 'error' : ''}`}
              autoComplete="new-password"
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
          
          {/* Indicador de fortaleza de contraseña */}
          {watchPassword && (
            <div className="password-strength">
              <div className="strength-meter">
                <div className={`strength-meter-fill ${strengthInfo.className}`}></div>
              </div>
              <div className="strength-text">{strengthInfo.text}</div>
            </div>
          )}
          
          <div className="password-requirements">
            <p>La contraseña debe tener:</p>
            <ul>
              <li>Al menos 8 caracteres</li>
              <li>Al menos una letra mayúscula</li>
              <li>Al menos un número</li>
            </ul>
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirmar contraseña*</label>
          <div className="input-wrapper">
            <span className="input-icon">🔒</span>
            <input
              id="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              {...register('confirmPassword')}
              placeholder="********"
              className={`modern-input ${errors.confirmPassword ? 'error' : ''}`}
              autoComplete="new-password"
            />
            <button 
              type="button" 
              className="password-toggle" 
              onClick={toggleConfirmPasswordVisibility}
              aria-label={showConfirmPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
            >
              {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
          {errors.confirmPassword && <div className="error-text">{errors.confirmPassword.message}</div>}
        </div>
        
        <div className="form-group checkbox-group">
          <div className="checkbox-wrapper">
            <input
              type="checkbox"
              id="acceptTerms"
              {...register('acceptTerms')}
            />
            <label htmlFor="acceptTerms">Acepto los <button type="button" className="link-button" onClick={(e) => { e.preventDefault(); }}>términos y condiciones</button></label>
          </div>
          {errors.acceptTerms && <div className="error-text">{errors.acceptTerms.message}</div>}
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
                Registrando...
              </>
            ) : (
              'Registrarse'
            )}
          </button>
        </div>
        
        <div className="auth-footer" style={{ color: '#000000' }}>
          ¿Ya tienes una cuenta? <button type="button" onClick={() => navigate('/login')} className="auth-link as-button">Iniciar sesión</button>
        </div>
      </form>
    </div>
  );
};

export default RegisterForm;
