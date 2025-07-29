import React, { useState, useEffect, useCallback } from 'react';
import { getSummaryStatus } from '../../../api/summary';
import type { SummaryResult } from '../../../api/summary';

import './AsyncSummaryViewer.css'; // Importar estilos externos

interface AsyncSummaryViewerProps {
  summaryId?: string;
  onComplete?: (summary: string) => void;
  showControls?: boolean;
  maxHeight?: string;
  className?: string;
}

/**
 * Componente para mostrar un resumen asíncrono con estado de carga y resultados
 */
export const AsyncSummaryViewer: React.FC<AsyncSummaryViewerProps> = ({
  summaryId,
  onComplete,
  showControls = true,
  className = '',
}) => {
  // Estados locales
  const [expanded, setExpanded] = useState(false);
  const [data, setData] = useState<SummaryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isError, setIsError] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string>('');
  
  // Función para consultar el estado del resumen
  const fetchSummaryStatus = useCallback(async () => {
    if (!summaryId) return;
    
    setIsLoading(true);
    try {
      const result = await getSummaryStatus(summaryId);
      setData(result);
      setIsError(false);
      
      // Notificar cuando el resumen esté completo
      if (result.status === 'completed' && onComplete && result.summary) {
        onComplete(result.summary);
      }
    } catch (err) {
      setIsError(true);
      setErrorMsg(err instanceof Error ? err.message : 'Error desconocido');
      console.error('Error al consultar estado del resumen:', err);
    } finally {
      setIsLoading(false);
    }
  }, [summaryId, onComplete]);
  
  // Efecto para cargar los datos inicialmente
  useEffect(() => {
    if (summaryId) {
      fetchSummaryStatus();
    }
  }, [summaryId, fetchSummaryStatus]);
  
  // Efecto para actualizar periodicamente si está en proceso
  useEffect(() => {
    if (!summaryId || !data || data.status !== 'processing') return;
    
    const intervalId = setInterval(() => {
      fetchSummaryStatus();
    }, 2000); // Consultar cada 2 segundos
    
    return () => clearInterval(intervalId);
  }, [summaryId, data, fetchSummaryStatus]);

  // Determinar el estado actual para mostrarlo en la UI
  const getStatusMessage = () => {
    if (isLoading) return 'Cargando información del resumen...';
    if (!data) return 'No hay información disponible';
    if (isError) return `Error: ${errorMsg || 'Desconocido'}`;
    
    switch (data.status) {
      case 'processing':
        return 'Generando resumen...';
      case 'completed':
        return 'Resumen generado correctamente';
      case 'error':
        return `Error: ${data.error || 'Desconocido'}`;
      case 'not_found':
        return 'No se encontró información del resumen';
      default:
        return `Estado: ${data.status}`;
    }
  };

  return (
    <div className={`border rounded-md overflow-hidden ${className}`}>
      <div className="bg-gray-100 p-3">
        <div className="flex justify-between items-center">
          <div className="text-sm font-medium">
            {getStatusMessage()}
          </div>
          
          {showControls && data?.status === 'completed' && (
            <button 
              onClick={() => setExpanded(!expanded)}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              {expanded ? 'Ocultar' : 'Mostrar'} resumen
            </button>
          )}
        </div>
        
        {data?.status === 'processing' && (
          <div className="w-full h-1 bg-gray-200 mt-2">
            <div className="h-1 bg-blue-600 animate-pulse progress-bar"></div>
          </div>
        )}
      </div>
      
      {(expanded || !showControls) && data?.status === 'completed' && data.summary && (
        <div 
          className={`p-3 text-sm summary-content ${expanded ? 'expanded' : 'collapsed'}`}
        >
          {data.summary.split('\n').map((paragraph: string, idx: number) => (
            <p key={idx} className="mb-2">
              {paragraph}
            </p>
          ))}
        </div>
      )}
      
      {data?.status === 'error' && (
        <div className="p-3 bg-red-50 text-red-700 text-sm">
          {data.error || 'Error desconocido al generar el resumen'}
        </div>
      )}
      
      {(isError || data?.status === 'error' || data?.status === 'not_found') && (
        <div className="p-2 bg-gray-50 border-t">
          <button
            onClick={fetchSummaryStatus}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Reintentar
          </button>
        </div>
      )}
    </div>
  );
};
