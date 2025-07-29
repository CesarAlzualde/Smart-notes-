import apiClient from './client';
import type { NoteData as Note, Tag, Topic } from '../features/notes/types';

interface CreateNoteData {
  title: string;
  content: string;
  summary?: string; // Resumen generado por IA
  tags?: string[]; // Nombres de etiquetas
  topics?: string[]; // Nombres de temas
  main_topic?: string; // Tema principal
}

interface UpdateNoteData {
  title?: string;
  content?: string;
  summary?: string; // Resumen generado por IA
  tags?: string[]; // Nombres de etiquetas
  topics?: string[]; // Nombres de temas
  main_topic?: string; // Tema principal
}

interface NotesFilters {
  search?: string;
  tag?: string;
  topic?: string;
  tags?: string[];
  topics?: string[];
  sort?: string;
  source_types?: string[];
  date?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  per_page?: number;
}

// Exportar las interfaces para que puedan ser importadas por otros módulos
export type { Note, Tag, Topic, NotesFilters, CreateNoteData, UpdateNoteData };

export const notesApi = {
  // Mantener getAllNotes para compatibilidad con código existente
  getAllNotes: async (filters?: NotesFilters) => {
    const response = await apiClient.get('/api/notes', { params: filters });
    return response.data;
  },
  
  // Nuevo método getNotes con el mismo comportamiento pero con nombre consistente
  getNotes: async (filters?: NotesFilters) => {
    const response = await apiClient.get('/api/notes', { params: filters });
    return response.data;
  },
  
  getNote: async (noteId: number) => {
    const response = await apiClient.get(`/api/notes/${noteId}`);
    return response.data;
  },
  
  // Método para obtener temas
  getTopics: async () => {
    const response = await apiClient.get('/api/notes/topics');
    return response.data;
  },
  
  getNoteById: async (id: number) => {
    const response = await apiClient.get(`/api/notes/${id}`);
    return response.data;
  },
  
  createNote: async (noteData: CreateNoteData) => {
    const response = await apiClient.post('/api/notes', noteData);
    return response.data;
  },
  
  updateNote: async (id: number, noteData: UpdateNoteData) => {
    const response = await apiClient.put(`/api/notes/${id}`, noteData);
    return response.data;
  },
  
  deleteNote: async (id: number) => {
    const response = await apiClient.delete(`/api/notes/${id}`);
    return response.data;
  },

  getRecentNotes: async (limit: number = 5) => {
    const response = await apiClient.get('/api/notes/recent', { params: { limit } });
    return response.data;
  },
  
  getNotesStatistics: async () => {
    const response = await apiClient.get('/api/notes/statistics');
    return response.data;
  },

  searchNotes: async (query: string) => {
    const response = await apiClient.get('/api/notes/search', { params: { q: query } });
    return response.data;
  },
  
  getSemanticallyRelatedNotes: async (noteId: number) => {
    const response = await apiClient.get(`/api/notes/${noteId}/semantically-related`);
    return response.data;
  }
};
