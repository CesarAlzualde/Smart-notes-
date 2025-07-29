import apiClient from './client';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  name: string;
  password: string;
}

interface SecurityQuestionData {
  question: string;
  answer: string;
}

interface PasswordResetData {
  username: string;
  answer: string;
  new_password: string;
}

export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const response = await apiClient.post('/api/auth/login', credentials);
    return response.data;
  },
  
  register: async (userData: RegisterData) => {
    const response = await apiClient.post('/api/auth/register', userData);
    return response.data;
  },
  
  logout: async () => {
    const response = await apiClient.post('/api/auth/logout');
    return response.data;
  },
  
  getSecurityQuestion: async (username: string) => {
    const response = await apiClient.get(`/api/auth/get-security-question?username=${username}`);
    return response.data;
  },
  
  setSecurityQuestion: async (data: SecurityQuestionData) => {
    const response = await apiClient.post('/api/auth/security-question', data);
    return response.data;
  },
  
  resetPassword: async (data: PasswordResetData) => {
    const response = await apiClient.post('/api/auth/reset-password', data);
    return response.data;
  },
  
  refreshToken: async () => {
    const response = await apiClient.post('/api/auth/refresh');
    return response.data;
  },
  
  getMe: async () => {
    const response = await apiClient.get('/api/auth/me');
    return response.data;
  },
  
  resetPasswordWithAnswer: async (data: any) => {
    const response = await apiClient.post('/api/auth/reset-password-answer', data);
    return response.data;
  }
};
