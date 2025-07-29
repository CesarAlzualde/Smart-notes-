import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuthStore } from '../../../store/authStore';
import './Auth.css';

// Preguntas de seguridad preestablecidas
const SECURITY_QUESTIONS = [
  '¿Cuál es el nombre de tu primera mascota?',
  '¿En qué ciudad naciste?',
  '¿Cuál era el nombre de tu escuela primaria?',
  '¿Cuál es el segundo nombre de tu madre?',
  '¿Cuál fue tu primer número de teléfono?',
  '¿Cuál es tu película favorita de la infancia?',
  'Personalizada (especificar)'
];

// Esquema de validación para el formulario
const securityQuestionSchema = z.object({
  questionIndex: z.string().min(1, 'Debe seleccionar una pregunta'),
  customQuestion: z.string().optional(),
  answer: z.string().min(3, 'La respuesta debe tener al menos 3 caracteres')
});

// Inferencia de tipos desde el esquema
type SecurityQuestionFormValues = z.infer<typeof securityQuestionSchema>;

const SecurityQuestionForm = () => {
  const { setSecurityQuestion, error, clearError, isLoading } = useAuthStore();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showCustomQuestion, setShowCustomQuestion] = useState(false);
  
  const { register, handleSubmit, watch, formState: { errors } } = useForm<SecurityQuestionFormValues>({
    resolver: zodResolver(securityQuestionSchema),
    defaultValues: {
      questionIndex: ''
    }
  });
  
  // Observar cambios en el select para mostrar/ocultar campo de pregunta personalizada
  const selectedQuestionIndex = watch('questionIndex');
  
  // Efecto para mostrar/ocultar el campo de pregunta personalizada
  if (selectedQuestionIndex === '6' && !showCustomQuestion) {
    setShowCustomQuestion(true);
  } else if (selectedQuestionIndex !== '6' && showCustomQuestion) {
    setShowCustomQuestion(false);
  }
  
  const onSubmit = async (data: SecurityQuestionFormValues) => {
    // Determinar qué pregunta usar
    const question = data.questionIndex === '6' 
      ? data.customQuestion 
      : SECURITY_QUESTIONS[parseInt(data.questionIndex)];
    
    if (!question) {
      return;
    }
    
    try {
      await setSecurityQuestion(question, data.answer);
      setSuccessMessage('Pregunta de seguridad configurada exitosamente');
      
      // Limpiar mensaje de éxito después de 3 segundos
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (error) {
      console.error('Error al configurar pregunta de seguridad:', error);
    }
  };
  
  return (
    <div className="security-question-form">
      <h2>Configurar Pregunta de Seguridad</h2>
      
      <p className="form-description">
        La pregunta de seguridad te ayudará a recuperar tu contraseña en caso de que la olvides.
        Elige una pregunta cuya respuesta sea fácil de recordar para ti, pero difícil de adivinar para otros.
      </p>
      
      {error && (
        <div className="error-message">
          {error}
          <button onClick={clearError} className="close-btn">×</button>
        </div>
      )}
      
      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="form-group">
          <label htmlFor="questionIndex">Pregunta de seguridad</label>
          <select
            id="questionIndex"
            {...register('questionIndex')}
            className={errors.questionIndex ? 'input-error' : ''}
          >
            <option value="">-- Selecciona una pregunta --</option>
            {SECURITY_QUESTIONS.map((question, index) => (
              <option key={index} value={index.toString()}>
                {question}
              </option>
            ))}
          </select>
          {errors.questionIndex && <span className="error">{errors.questionIndex.message}</span>}
        </div>
        
        {showCustomQuestion && (
          <div className="form-group">
            <label htmlFor="customQuestion">Tu pregunta personalizada</label>
            <input
              id="customQuestion"
              type="text"
              {...register('customQuestion')}
              placeholder="Escribe tu pregunta de seguridad"
              className={errors.customQuestion ? 'input-error' : ''}
            />
            {errors.customQuestion && <span className="error">{errors.customQuestion.message}</span>}
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="answer">Tu respuesta</label>
          <input
            id="answer"
            type="text"
            {...register('answer')}
            placeholder="Respuesta a la pregunta de seguridad"
            className={errors.answer ? 'input-error' : ''}
          />
          {errors.answer && <span className="error">{errors.answer.message}</span>}
          <p className="field-hint">
            Esta respuesta NO es sensible a mayúsculas y minúsculas.
          </p>
        </div>
        
        <div className="form-actions">
          <button 
            type="submit" 
            disabled={isLoading}
            className="btn-primary"
          >
            {isLoading ? 'Guardando...' : 'Guardar pregunta de seguridad'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SecurityQuestionForm;
