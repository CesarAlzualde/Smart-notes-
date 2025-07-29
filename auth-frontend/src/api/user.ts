import apiClient from './client';

/**
 * Obtiene el perfil del usuario actual
 * @returns Promise con los datos del perfil del usuario
 */
export const getCurrentUserProfile = async () => {
  const response = await apiClient.get('/api/users/me');
  return response.data;
};

/**
 * Actualiza el perfil del usuario actual
 * @param userData - Los datos a actualizar
 * @returns Promise con los datos actualizados
 */
export const updateUserProfile = async (userData: {
  name?: string;
  email?: string;
}) => {
  const response = await apiClient.put('/api/users/me', userData);
  return response.data;
};

/**
 * Interfaz para el perfil de usuario
 */
export interface UserProfile {
  id: number;
  username: string;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
