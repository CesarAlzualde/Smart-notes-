import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, type UseFormReturn } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { authApi } from '../../../api/auth';
import './Auth.css';
import './AuthModern.css';

// Definir pasos del formulario como constantes numéricas en lugar de enum
const RecoveryStep = {
  USERNAME: 0,
  SECURITY_QUESTION: 1,
  NEW_PASSWORD: 2,
  SUCCESS: 3
} as const;

type RecoveryStepType = typeof RecoveryStep[keyof typeof RecoveryStep];

// Esquema para validar nombre de usuario
const usernameSchema = z.object({
  username: z.string().min(1, 'El nombre de usuario es requerido')
});

// Esquema para validar respuesta de seguridad
const answerSchema = z.object({
  answer: z.string().min(1, 'La respuesta es requerida')
});

// Esquema para validar nueva contraseña (igual que en registro)
const passwordSchema = z.object({
  password: z
    .string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .refine(
      (password) => /[A-Z]/.test(password),
      { message: 'La contraseña debe contener al menos una letra mayúscula' }
    )
    .refine(
      (password) => /[0-9]/.test(password),
      { message: 'La contraseña debe contener al menos un número' }
    ),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Las contraseñas no coinciden',
  path: ['confirmPassword']
});

// Tipos para los formularios
type UsernameFormValues = z.infer<typeof usernameSchema>;
type AnswerFormValues = z.infer<typeof answerSchema>;
type PasswordFormValues = z.infer<typeof passwordSchema>;

// --- Tipos para los props de los subcomponentes ---
type UsernameStepProps = {
  form: UseFormReturn<UsernameFormValues>;
  onSubmit: (data: UsernameFormValues) => Promise<void>;
  isLoading: boolean;
};

type SecurityQuestionStepProps = {
  form: UseFormReturn<AnswerFormValues>;
  onSubmit: (data: AnswerFormValues) => void;
  onBack: () => void;
  question: string;
};

type NewPasswordStepProps = {
  form: UseFormReturn<PasswordFormValues>;
  onSubmit: (data: PasswordFormValues) => Promise<void>;
  onBack: () => void;
  isLoading: boolean;
};

type SuccessStepProps = {
  onRedirect: () => void;
};

// Helper para manejar errores de API
const getApiErrorMessage = (error: unknown): string => {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const response = error.response as { data?: { error?: string } };
    if (response.data && typeof response.data.error === 'string') {
      return response.data.error;
    }
  }
  return 'Ocurrió un error inesperado';
};

// --- Subcomponentes para cada paso ---

const UsernameStep = ({ form, onSubmit, isLoading }: UsernameStepProps) => (
  <form onSubmit={form.handleSubmit(onSubmit)}>
    <div className="form-group">
      <label htmlFor="username" style={{ color: '#000000', fontWeight: 'bold' }}>Nombre de usuario</label>
      <div className="input-wrapper">
        <span className="input-icon">👤</span>
        <input
          id="username"
          type="text"
          {...form.register('username')}
          className={`modern-input ${form.formState.errors.username ? 'error' : ''}`}
          placeholder="Escribe tu nombre de usuario"
          style={{ color: '#000000' }}
        />
      </div>
      {form.formState.errors.username && (
        <div className="error-text">{form.formState.errors.username.message}</div>
      )}
    </div>
    <div className="form-actions">
      <button type="submit" disabled={isLoading} className="btn-modern">
        {isLoading ? 'Verificando...' : 'Siguiente'}
      </button>
    </div>
  </form>
);

const SecurityQuestionStep = ({ form, onSubmit, onBack, question }: SecurityQuestionStepProps) => (
  <form onSubmit={form.handleSubmit(onSubmit)}>
    <div className="form-group">
      <label htmlFor="security-question" style={{ color: '#000000', fontWeight: 'bold' }}>Pregunta de seguridad</label>
      <p style={{ color: '#000000' }}>{question}</p>
    </div>
    <div className="form-group">
      <label htmlFor="answer" style={{ color: '#000000', fontWeight: 'bold' }}>Tu respuesta</label>
      <div className="input-wrapper">
        <span className="input-icon">📝</span>
        <input
          id="answer"
          type="text"
          {...form.register('answer')}
          className={`modern-input ${form.formState.errors.answer ? 'error' : ''}`}
          placeholder="Escribe tu respuesta"
          style={{ color: '#000000' }}
        />
      </div>
      {form.formState.errors.answer && (
        <div className="error-text">{form.formState.errors.answer.message}</div>
      )}
    </div>
    <div className="form-actions">
      <button type="button" onClick={onBack} className="btn-secondary">Atrás</button>
      <button type="submit" className="btn-modern">Siguiente</button>
    </div>
  </form>
);

const NewPasswordStep = ({ form, onSubmit, onBack, isLoading }: NewPasswordStepProps) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <div className="form-group">
        <label htmlFor="password" style={{ color: '#000000', fontWeight: 'bold' }}>Nueva Contraseña</label>
        <div className="input-wrapper">
          <span className="input-icon">🔒</span>
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            {...form.register('password')}
            className={`modern-input ${form.formState.errors.password ? 'error' : ''}`}
            placeholder="Escribe tu nueva contraseña"
            style={{ color: '#000000' }}
          />
          <button type="button" className="password-toggle" onClick={() => setShowPassword(!showPassword)}>
            {showPassword ? '👁️' : '👁️‍🗨️'}
          </button>
        </div>
        {form.formState.errors.password && (
          <div className="error-text">{form.formState.errors.password.message}</div>
        )}
      </div>
      <div className="form-group">
        <label htmlFor="confirmPassword" style={{ color: '#000000', fontWeight: 'bold' }}>Confirmar Contraseña</label>
        <div className="input-wrapper">
          <span className="input-icon">🔒</span>
          <input
            id="confirmPassword"
            type={showConfirmPassword ? 'text' : 'password'}
            {...form.register('confirmPassword')}
            className={`modern-input ${form.formState.errors.confirmPassword ? 'error' : ''}`}
            placeholder="Confirma tu nueva contraseña"
            style={{ color: '#000000' }}
          />
          <button type="button" className="password-toggle" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
            {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
          </button>
        </div>
        {form.formState.errors.confirmPassword && (
          <div className="error-text">{form.formState.errors.confirmPassword.message}</div>
        )}
      </div>
      <div className="form-actions">
        <button type="button" onClick={onBack} className="btn-secondary">Atrás</button>
        <button type="submit" disabled={isLoading} className="btn-modern">
          {isLoading ? 'Restableciendo...' : 'Restablecer contraseña'}
        </button>
      </div>
    </form>
  );
};

const SuccessStep = ({ onRedirect }: SuccessStepProps) => (
  <div className="success-step">
    <div className="alert alert-success">
      <span className="alert-icon">✅</span>
      <div>
        <h4>¡Contraseña restablecida!</h4>
        <p>Ya puedes iniciar sesión con tu nueva contraseña.</p>
      </div>
    </div>
    <div className="form-actions">
      <button type="button" onClick={onRedirect} className="btn-modern">
        Ir al inicio de sesión
      </button>
    </div>
  </div>
);

const PasswordRecoveryForm = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<RecoveryStepType>(RecoveryStep.USERNAME);
  const [username, setUsername] = useState<string>('');
  const [securityQuestion, setSecurityQuestion] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const usernameForm = useForm<UsernameFormValues>({ resolver: zodResolver(usernameSchema) });
  const answerForm = useForm<AnswerFormValues>({ resolver: zodResolver(answerSchema) });
  const passwordForm = useForm<PasswordFormValues>({ resolver: zodResolver(passwordSchema) });

  const handleUsernameSubmit = async (data: UsernameFormValues) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authApi.getSecurityQuestion(data.username);
      setUsername(data.username);
      setSecurityQuestion(response.security_question);
      setCurrentStep(RecoveryStep.SECURITY_QUESTION);
    } catch (error: unknown) {
      setError(getApiErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerSubmit = () => {
    setCurrentStep(RecoveryStep.NEW_PASSWORD);
  };

  const handlePasswordSubmit = async (data: PasswordFormValues) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.resetPasswordWithAnswer({
        username: username,
        answer: answerForm.getValues().answer,
        new_password: data.password
      });
      setCurrentStep(RecoveryStep.SUCCESS);
    } catch (error: unknown) {
      setError(getApiErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case RecoveryStep.USERNAME:
        return <UsernameStep form={usernameForm} onSubmit={handleUsernameSubmit} isLoading={isLoading} />;
      case RecoveryStep.SECURITY_QUESTION:
        return <SecurityQuestionStep form={answerForm} onSubmit={handleAnswerSubmit} onBack={() => setCurrentStep(RecoveryStep.USERNAME)} question={securityQuestion} />;
      case RecoveryStep.NEW_PASSWORD:
        return <NewPasswordStep form={passwordForm} onSubmit={handlePasswordSubmit} onBack={() => setCurrentStep(RecoveryStep.SECURITY_QUESTION)} isLoading={isLoading} />;
      case RecoveryStep.SUCCESS:
        return <SuccessStep onRedirect={() => navigate('/login')} />;
      default:
        return null;
    }
  };

  return (
    <div className="modern-form password-recovery-form">
      <h2 style={{ color: '#000000' }}>Recuperar Contraseña</h2>
      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          <div className="alert-content">{error}</div>
          <button onClick={() => setError(null)} className="alert-close">×</button>
        </div>
      )}
      <div className="recovery-progress">
        <div className={`progress-step ${currentStep >= RecoveryStep.USERNAME ? 'active' : ''}`}>
          <div className="progress-indicator"><span className="step-number">1</span></div>
          <span className="step-text">Usuario</span>
        </div>
        <div className="progress-line"></div>
        <div className={`progress-step ${currentStep >= RecoveryStep.SECURITY_QUESTION ? 'active' : ''}`}>
          <div className="progress-indicator"><span className="step-number">2</span></div>
          <span className="step-text">Pregunta</span>
        </div>
        <div className="progress-line"></div>
        <div className={`progress-step ${currentStep >= RecoveryStep.NEW_PASSWORD ? 'active' : ''}`}>
          <div className="progress-indicator"><span className="step-number">3</span></div>
          <span className="step-text">Contraseña</span>
        </div>
      </div>
      {renderCurrentStep()}
      <div className="auth-footer" style={{ color: '#000000' }}>
        <button type="button" onClick={() => navigate('/login')} className="auth-link as-button">
          Volver al inicio de sesión
        </button>
      </div>
    </div>
  );
};

export default PasswordRecoveryForm;
