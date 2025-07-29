import { create } from 'zustand';
import { authApi } from '../api/auth';
import { AxiosError } from 'axios';

interface User {
  id: number;
  username: string;
  name: string;
  email: string;
  role: string;
}

// Tipo para errores de API, usando el tipo genérico de Axios
type ApiError = AxiosError<{ error: string }>;

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  init: () => Promise<void>;  // Inicializa y verifica el estado de autenticación
  checkAuth: () => Promise<boolean>;  // Verifica manualmente la autenticación
  login: (email: string, password: string) => Promise<void>;
  register: (userData: { username: string; email: string; name: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
  setSecurityQuestion: (question: string, answer: string) => Promise<void>;
  resetPasswordWithAnswer: (username: string, answer: string, newPassword: string) => Promise<void>;
  clearError: () => void;
}

// Create store with Zustand
export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('auth_token'),
  // Inicialmente asumimos que NO estamos autenticados hasta verificar el token
  isAuthenticated: false,
  isLoading: true, // Comenzamos con loading=true mientras verificamos el token
  error: null,
  
  // Inicialización del estado de autenticación - se ejecuta automáticamente
  init: async () => {
    const token = localStorage.getItem('auth_token');
    
    // Si no hay token, definitivamente no estamos autenticados
    if (!token) {
      console.log('No hay token en localStorage');
      set({ isLoading: false, isAuthenticated: false });
      return;
    }
    
    // Si hay token, intentamos verificarlo con el backend
    try {
      console.log('Verificando validez del token...');
      // Intentamos obtener el perfil del usuario para verificar que el token es válido
      const userData = await authApi.getMe();
      console.log('Token verificado, usuario autenticado:', userData);
      set({ 
        user: userData, 
        isAuthenticated: true,
        isLoading: false 
      });
    } catch (error) {
      // Si hay un error (401), el token no es válido
      console.error('Error al verificar token, probablemente expirado:', error);
      // Limpiamos el token inválido
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      set({ 
        isAuthenticated: false, 
        token: null, 
        user: null,
        isLoading: false 
      });
    }
  },
  
  // Función para verificar token manualmente
  checkAuth: async () => {
    const { init } = get();
    await init();
    return get().isAuthenticated;
  },
  
  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      console.log('DEBUG: Intentando iniciar sesión con:', { email, password: '****' });
      
      // Verificar si se puede acceder a localStorage
      try {
        const testValue = 'test_value_' + new Date().getTime();
        localStorage.setItem('test_storage', testValue);
        const retrievedValue = localStorage.getItem('test_storage');
        console.log('DEBUG: Prueba de localStorage:', { stored: testValue, retrieved: retrievedValue, success: testValue === retrievedValue });
        localStorage.removeItem('test_storage');
      } catch (storageError) {
        console.error('DEBUG: ERROR en localStorage:', storageError);
      }
      
      // Intentar el login
      console.log('DEBUG: Enviando petición a /api/auth/login');
      const data = await authApi.login({ email, password });
      console.log('DEBUG: Respuesta del servidor login completa:', JSON.stringify(data));
      
      // Verificar estructura de los datos
      console.log('DEBUG: Verificando campos de la respuesta:', {
        'data.user': data.user ? 'presente' : 'ausente',
        'data.access_token': data.access_token ? 'presente' : 'ausente', 
        'data.refresh_token': data.refresh_token ? 'presente' : 'ausente'
      });
      
      // Actualizar estado en el store
      console.log('DEBUG: Actualizando estado...');
      set({
        user: data.user,
        token: data.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
      
      // IMPORTANTE: Guardar tokens en localStorage
      try {
        console.log('DEBUG: Guardando auth_token:', data.access_token?.substring(0, 10) + '...');
        localStorage.setItem('auth_token', data.access_token);
        console.log('DEBUG: Token guardado en localStorage');
        
        if (data.refresh_token) {
          console.log('DEBUG: Guardando refresh_token...');
          localStorage.setItem('refresh_token', data.refresh_token);
        }
      } catch (storageError) {
        console.error('DEBUG: ERROR guardando tokens:', storageError);
      }
    } catch (err) {
      const error = err as ApiError;
      console.error('Error en login:', error);
      console.error('Detalles de la respuesta:', error.response?.data);
      
      set({ 
        error: error.response?.data?.error || 'Error al iniciar sesión', 
        isLoading: false 
      });
      throw error;
    }
  },
  
  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      console.log('Intentando registrar usuario:', { ...userData, password: '****' });
      const response = await authApi.register(userData);
      console.log('Respuesta del servidor registro:', response);
      
      // Después de un registro exitoso, autenticar automáticamente al usuario
      // usando los tokens y datos de usuario devueltos por el backend
      if (response.access_token && response.user) {
        console.log('Registro exitoso, autenticando usuario:', response.user);
        
        // Guardar tokens
        localStorage.setItem('auth_token', response.access_token);
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
        }
        
        // Actualizar estado para mostrar usuario como autenticado
        set({
          user: response.user,
          token: response.access_token,
          isAuthenticated: true,
          isLoading: false
        });
      } else {
        // Si no hay tokens en la respuesta, solo actualizar el estado de carga
        console.log('Registro exitoso pero sin tokens de autenticación');
        set({ isLoading: false });
      }
    } catch (err) {
      const error = err as ApiError;
      console.error('Error en registro:', error);
      console.error('Detalles de la respuesta:', error.response?.data);
      
      set({ 
        error: error.response?.data?.error || 'Error al registrarse', 
        isLoading: false 
      });
      throw error;
    }
  },
  
  logout: async () => {
    set({ isLoading: true, error: null });
    try {
      // Intentar hacer logout en el servidor
      await authApi.logout();
    } catch (error) {
      console.error('Error en logout:', error);
    }
    
    // Independientemente del resultado, limpiar estado local
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  },
  
  setSecurityQuestion: async (question, answer) => {
    set({ isLoading: true, error: null });
    try {
      await authApi.setSecurityQuestion({ question, answer });
      set({ isLoading: false });
    } catch (err) {
      const error = err as ApiError;
      set({ 
        error: error.response?.data?.error || 'Error al configurar pregunta de seguridad', 
        isLoading: false 
      });
      throw error;
    }
  },
  
  resetPasswordWithAnswer: async (username, answer, newPassword) => {
    set({ isLoading: true, error: null });
    try {
      await authApi.resetPassword({
        username,
        answer,
        new_password: newPassword
      });
      set({ isLoading: false });
    } catch (err) {
      const error = err as ApiError;
      set({ 
        error: error.response?.data?.error || 'Error al restablecer contraseña', 
        isLoading: false 
      });
      throw error;
    }
  },
  
  clearError: () => set({ error: null }),
}));
