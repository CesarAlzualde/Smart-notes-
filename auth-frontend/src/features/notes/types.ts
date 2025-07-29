// Definiciones de tipos para las notas, etiquetas y temas.

export interface Tag {
  id: number;
  name: string;
  color?: string;
}

export interface Topic {
  id: number;
  name: string;
  description?: string;
}

export interface RelatedNote {
  id: number;
  title: string;
  similarity: number;
}

export interface NoteData {
  id?: number;
  title: string;
  content: string;
  summary?: string;
  tags?: Tag[];
  topics?: Topic[];
  main_topic?: string;
  created_at: string;
  updated_at?: string;
  source_type?: string;
  file_id?: number;
  file_content?: string; 
  // Campos de análisis de IA
  keywords?: string[];
  entities?: { [key: string]: string[] };
  ai_sentiment?: { score: number; label: string };
  ai_analysis_ready?: boolean;
  // Campos adicionales
  related_notes?: { id: number; title: string }[];
}
