import apiClient from './client';

// Interfaces para el análisis de texto unificado

export interface TextStats {
  words: number;
  paragraphs?: number;
  reading_time: number;
  readability: number;
  avg_words_per_sentence?: number;
  avg_chars_per_word?: number;
}

export interface TopicDistribution {
  topic: string;
  confidence?: number;
  score?: number;
  weight?: number; // Campo usado por el backend para enviar el valor de porcentaje
}

export interface GrammarCorrectionResponse {
  corrected_text: string;
  original_text: string;
  has_changes: boolean;
  message?: string;
  saved?: boolean;
  save_error?: string;
}

export interface UnifiedAnalysisResponse {
  // Campos de análisis de texto
  stats?: TextStats;
  summary?: string;
  sentiment?: { score: number; label: string };
  readability?: { score: number; grade: string };
  corrected_text?: string;
  
  // Campos de análisis de temas
  main_topic?: string;
  main_topic_confidence?: number;
  topics_distribution?: TopicDistribution[];
  suggested_topics?: string[];

  // Campos de IA adicionales
  keywords?: string[];
  entities?: { [key: string]: string[] };
}

export const analysisApi = {
  /**
   * Analiza el texto de una nota para extraer un resumen, temas, palabras clave y más.
   * Llama a un endpoint unificado en el backend.
   */
  analyzeText: async (text: string, noteId: number, skipGrammarCorrection: boolean = false): Promise<UnifiedAnalysisResponse> => {
    const payload = { text, note_id: noteId, skip_grammar_correction: skipGrammarCorrection };
    try {
      const response = await apiClient.post<UnifiedAnalysisResponse>('/api/analysis/text', payload);
      return response.data;
    } catch (error) { 
      console.error('Error al analizar texto:', error);
      // En caso de error, devuelve un objeto vacío para evitar que la aplicación se bloquee.
      // El componente que llama debe manejar este caso.
      return {};
    }
  },

  /**
   * Solicita una corrección gramatical independiente del texto.
   * Esta función permite al usuario corregir su texto sin generar un análisis completo.
   */
  correctGrammar: async (text: string, noteId?: number, options?: { skipUndo?: boolean }) => {
    const response = await apiClient.post('/api/analysis/grammar', { 
      text, 
      note_id: noteId,
      ...options 
    });
    return response.data;
  },
  
  analyzeTopics: async (text: string, noteId: number) => {
    const response = await apiClient.post('/api/analysis/topics', { text, note_id: noteId });
    return response.data;
  }
};
