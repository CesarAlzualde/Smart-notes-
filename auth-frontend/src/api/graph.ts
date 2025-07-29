import apiClient from './client';
import type { GraphData } from '../types/graph';
import { adaptApiResponseToGraphData } from '../features/graph/utils/graphDataAdapter';
import type { ApiGraphResponse } from '../features/graph/utils/graphDataAdapter';

// Define the structure for the auto-generation response
export interface AutoGenerateResponse {
  message: string;
  id: string;
  name: string;
  concepts: Array<{
    id: string;
    label: string;
    type: string;
    color?: string;
    size?: number;
    [key: string]: string | number | boolean | null | undefined;
  }>;
  relations: Array<{
    id: string;
    source: string;
    target: string;
    label: string;
    width?: number;
    [key: string]: string | number | boolean | null | undefined;
  }>;
  map_data: {
    id: string;
    name: string;
    concepts: Array<{
      id: string;
      label: string;
      type: string;
      [key: string]: string | number | boolean | null | undefined;
    }>;
    relations: Array<{
      id: string;
      source: string;
      target: string;
      label: string;
      [key: string]: string | number | boolean | null | undefined;
    }>;
  };
  generation_mode: {
    ai_analysis_used: boolean;
    mode_description: string;
    optimization: string;
  };
  stats: {
    nodes_created: number;
    edges_created: number;
    performance: string;
  };
}

// Define the structure for the semantic analysis response
export interface SemanticAnalysisResponse {
  message: string;
  analysis_results: {
    new_nodes_count: number;
    new_relations_count: number;
  };
}

export const graphApi = {
  getFullGraph: async () => {
    const response = await apiClient.get('/api/graph/visualization');
    return response.data;
  },

  getConceptMap: async (mapId: string) => {
    const response = await apiClient.get(`/api/graph/${mapId}`);
    const graphData = adaptApiResponseToGraphData(response.data as ApiGraphResponse);
    return {
      ...graphData,
      id: response.data.id,
      name: response.data.name,
      note_ids: response.data.note_ids
    };
  },

  autoGenerateFromNote: async (noteId: string): Promise<AutoGenerateResponse> => {
    const response = await apiClient.post(`/api/graph/generate-from-note`, { note_id: noteId });
    return response.data;
  },

  analyzeSemanticRelationships: async (noteId: string): Promise<SemanticAnalysisResponse> => {
    const response = await apiClient.post(`/api/graph/semantic-analysis`, { note_ids: [noteId] });
    return response.data;
  },
  
  generateConceptMap: async (text: string, noteIds?: string[]) => {
    const response = await apiClient.post('/api/graph/generate', { text, note_ids: noteIds });
    return response.data;
  },
  
    saveConceptMap: async (name: string, graphData: GraphData, noteIds?: string[]) => {
    const response = await apiClient.post('/api/graph/save', { name, graph_data: graphData, note_ids: noteIds });
    return response.data;
  },
  
  searchNodes: async (query: string) => {
    const response = await apiClient.get(`/api/graph/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },
  
  getNodeNeighbors: async (nodeId: string) => {
    const response = await apiClient.get(`/api/graph/neighbors/${nodeId}`);
    return response.data;
  },
  
  deleteConceptMap: async (mapId: string) => {
    const response = await apiClient.delete(`/api/graph/maps/${mapId}`);
    return response.data;
  }
};
