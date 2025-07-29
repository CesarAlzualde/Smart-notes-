import axios from 'axios';
// Removemos la importación sin uso
// import { useAuthStore } from '../store/authStore';

// Control de estado de autenticación
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

// Función para suscribir solicitudes fallidas a la cola de espera
const subscribeToTokenRefresh = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback);
};

// Función para notificar a todas las solicitudes en espera
const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach(callback => callback(token));
  refreshSubscribers = [];
};

// Función para limpiar tokens y forzar logout
const handleAuthError = async () => {
  // Limpiar tokens del localStorage
  localStorage.removeItem('auth_token');
  localStorage.removeItem('refresh_token');
  // Reiniciar el estado de refresco
  isRefreshing = false;
  refreshSubscribers = [];
  // El estado de autenticación se actualizará la próxima vez que cargue la aplicación
  console.warn('Sesión cerrada debido a error de autenticación');
  
  // Redirigir a login
  window.location.href = '/login';
};

// Función para verificar si la ruta es pública o requiere autenticación
const isPublicRoute = (url: string | undefined): boolean => {
  if (!url) return false;
  const publicRoutes = [
    '/api/auth/login', 
    '/api/auth/register', 
    '/api/auth/reset-password', 
    '/api/auth/forgot-password',
    '/api/health'
  ];
  return publicRoutes.some(route => url.includes(route));
};

// Crear instancia de axios con configuración explícita al backend
const apiClient = axios.create({
  // Apuntamos explícitamente al backend en el puerto 5000
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir token a las peticiones
apiClient.interceptors.request.use(
  (config) => {
    // No añadir token a rutas públicas
    if (isPublicRoute(config.url)) {
      console.log('Ruta pública, no requiere token:', config.url);
      return config;
    }
    
    // Añadir token de autorización si existe
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Token añadido a la petición:', config.url);
    } else {
      // Si no hay token y la ruta requiere autenticación, mostrar advertencia
      console.warn('ADVERTENCIA: Petición a ruta protegida sin token:', config.url);
      // Aquí podríamos redirigir al login, pero permitimos que continúe para ver el error
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autorización y otros errores comunes
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;
    const errorMsg = error.response?.data?.error || 'Error desconocido';
    
    // Log detallado para cualquier error API
    console.error(`API Error ${status}: ${errorMsg}`, {
      url: originalRequest?.url,
      method: originalRequest?.method,
      data: error.response?.data,
      requestData: originalRequest?.data,
      headers: originalRequest?.headers ? { ...originalRequest.headers } : 'No headers'
    });
    
    // Rutas de autenticación que deberían manejar sus propios errores 401
    const authRoutes = ['/api/auth/login', '/api/auth/register', '/api/auth/reset-password', '/api/auth/forgot-password'];
    
    // Extraer la URL de la petición para verificar si es una ruta de autenticación
    const requestPath = originalRequest?.url?.replace(originalRequest.baseURL || '', '');
    const isAuthRoute = authRoutes.some(route => requestPath?.includes(route));
    
    // Manejo específico por código de error
    switch (status) {
      case 401: // No autorizado
        // Si no es una ruta de auth y no hemos intentado refrescar el token
        if (!isAuthRoute && !originalRequest._retry) {
          originalRequest._retry = true;
          
          // Si ya estamos refrescando, agregar a la cola en lugar de hacer otra petición
          if (isRefreshing) {
            console.log('Ya se está refrescando el token, agregando petición a la cola:', originalRequest.url);
            return new Promise((resolve) => {
              subscribeToTokenRefresh(token => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                resolve(apiClient(originalRequest));
              });
            });
          }
          
          // Marcar que estamos refrescando para evitar múltiples peticiones
          isRefreshing = true;
          
          try {
            console.log('Intentando renovar token expirado...');
            // Intentar refrescar el token
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) {
              throw new Error('No hay refresh token disponible');
            }
            
            console.log('Enviando refresh_token:', refreshToken.substring(0, 10) + '...');
            const response = await axios.post('http://localhost:5000/api/auth/refresh', {}, {
              headers: {
                'Authorization': `Bearer ${refreshToken}`,
              },
            });
            console.log('Respuesta de refresh token:', response.status, response.data);
            
            // Actualizar tokens
            const { access_token } = response.data;
            localStorage.setItem('auth_token', access_token);
            console.log('Token renovado exitosamente');
            
            // Notificar a todos los suscriptores
            onTokenRefreshed(access_token);
            isRefreshing = false;
            
            // Reintente con el nuevo token
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return apiClient(originalRequest);
          } catch (refreshError) {
            console.error('Error al renovar el token:', refreshError);
            // Si falla el refresh, hacer logout
            isRefreshing = false;
            refreshSubscribers = [];
            await handleAuthError();
            return Promise.reject(refreshError);
          }
        }
        break;
      
      case 422: // Error de validación
        console.error('Error de validación:', error.response?.data);
        break;
        
      case 500: // Error interno del servidor
        console.error('Error interno del servidor:', error.response?.data);
        break;
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
