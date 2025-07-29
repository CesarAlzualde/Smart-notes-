// Tipos relacionados con análisis de texto
export interface TextStats {
  words: number;
  paragraphs: number;
  sentences: number;
  reading_time: number;
  characters: number;
}

export interface Concept {
  concept: string;
  frequency: number;
  relevance: number;
}

export interface TextAnalysisResponse {
  stats: TextStats;
  summary: string;
  concepts: Concept[];
  tone: string;
  readability_score: number;
  readability_label: string;
}
