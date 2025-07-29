// Tipos relacionados con análisis de tópicos
export interface TopicItem {
  topic: string;
  percentage: number;
}

export interface TopicsAnalysisResponse {
  main_topic: string;
  main_topic_confidence: number;
  topics_distribution: TopicItem[];
}
