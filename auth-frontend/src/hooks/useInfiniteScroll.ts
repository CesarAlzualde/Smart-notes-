import { useEffect, useRef, useState } from 'react';

interface UseInfiniteScrollOptions {
  threshold?: number;  // Distancia desde el final de la página para activar el evento de carga
  isLoading?: boolean; // Si está cargando, no activar el evento
  hasMore?: boolean;   // Si hay más datos para cargar
}

/**
 * Hook personalizado para implementar scroll infinito
 * @param callback Función que se ejecuta cuando se alcanza el umbral de scroll
 * @param options Opciones de configuración
 * @returns Un objeto ref para asignar al último elemento de la lista
 */
const useInfiniteScroll = <T extends HTMLElement = HTMLDivElement>(
  callback: () => void,
  options: UseInfiniteScrollOptions = {}
) => {
  const {
    threshold = 200,
    isLoading = false,
    hasMore = true
  } = options;

  const [element, setElement] = useState<T | null>(null);
  const observer = useRef<IntersectionObserver | null>(null);
  
  useEffect(() => {
    // Si no hay más elementos para cargar o está cargando, no configuramos el observer
    if (isLoading || !hasMore) return;
    
    // Desconectar observer anterior si existe
    if (observer.current) {
      observer.current.disconnect();
    }
    
    // Crear nuevo observer
    observer.current = new IntersectionObserver(entries => {
      const first = entries[0];
      if (first.isIntersecting) {
        callback();
      }
    }, {
      rootMargin: `0px 0px ${threshold}px 0px`
    });
    
    // Observar elemento si existe
    if (element) {
      observer.current.observe(element);
    }
    
    // Limpiar observer al desmontar
    return () => {
      if (observer.current) {
        observer.current.disconnect();
      }
    };
  }, [callback, element, threshold, isLoading, hasMore]);
  
  return { setElement };
};

export default useInfiniteScroll;
