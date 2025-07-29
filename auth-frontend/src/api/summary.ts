/**
 * Cliente API para interactuar con los endpoints de resumen
 */

import client from './client';

export interface SummaryResult {
  summary: string;
  status: 'completed' | 'processing' | 'error' | 'not_found';
  metadata?: {
    generation_time?: number;
    real_compression?: number;
    error?: string;
    [key: string]: unknown;
  };
  error?: string;
  summary_id?: string;
  timestamp?: number;
}

export interface SummaryRequest {
  text: string;
  async_mode?: boolean;
  file_id?: string;
}

/**
 * Genera un resumen de texto de manera síncrona o asíncrona
 */
export async function generateSummary(
  request: SummaryRequest
): Promise<SummaryResult> {
  const response = await client.post<SummaryResult>('/api/summary/generate', request);
  return response.data;
}

/**
 * Consulta el estado de un resumen asíncrono
 */
export async function getSummaryStatus(summaryId: string): Promise<SummaryResult> {
  const response = await client.get<SummaryResult>(`/api/summary/check/${summaryId}`);
  return response.data;
}

/**
 * Hook para polling de estado de resumen
 * Esta función debe usarse con un hook como useQuery con retry y refetchInterval
 */
export async function pollSummaryStatus(summaryId: string): Promise<SummaryResult> {
  if (!summaryId) {
    throw new Error('Se requiere un ID de resumen');
  }
  
  const response = await getSummaryStatus(summaryId);
  
  // Si el estado aún es "processing", lanzar error para que useQuery siga reintentando
  if (response.status === 'processing') {
    throw new Error('Resumen aún en procesamiento');
  }
  
  return response;
}
