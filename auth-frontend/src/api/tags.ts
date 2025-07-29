import apiClient from './client';

interface Tag {
  id: number;
  name: string;
  count?: number; // Número de notas que tienen esta etiqueta
}

interface TagsFilters {
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

// Exportar las interfaces para que puedan ser importadas por otros módulos
export type { Tag, TagsFilters };

export const tagsApi = {
  getAllTags: async (filters?: TagsFilters) => {
    const response = await apiClient.get('/api/tags', { params: filters });
    return response.data;
  },
  
  // Nuevo método getTags con el mismo comportamiento pero con nombre consistente
  getTags: async (filters?: TagsFilters) => {
    const response = await apiClient.get('/api/tags', { params: filters });
    return response.data;
  },
  
  getTagById: async (id: number) => {
    const response = await apiClient.get(`/api/tags/${id}`);
    return response.data;
  },
  
  getTagByName: async (name: string) => {
    const response = await apiClient.get('/api/tags/by-name', { params: { name } });
    return response.data;
  },
  
  createTag: async (name: string) => {
    const response = await apiClient.post('/api/tags', { name });
    return response.data;
  },
  
  updateTag: async (id: number, name: string) => {
    const response = await apiClient.put(`/api/tags/${id}`, { name });
    return response.data;
  },
  
  deleteTag: async (id: number) => {
    const response = await apiClient.delete(`/api/tags/${id}`);
    return response.data;
  },
  
  getTagsStatistics: async () => {
    const response = await apiClient.get('/api/tags/statistics');
    return response.data;
  },
  
  getPopularTags: async (limit: number = 10) => {
    const response = await apiClient.get('/api/tags/popular', { params: { limit } });
    return response.data;
  }
};
