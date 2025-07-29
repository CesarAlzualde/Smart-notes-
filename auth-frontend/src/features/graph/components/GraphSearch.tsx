import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { graphApi } from '../../../api/graph';
import './GraphSearch.modern.css';

import type { GraphNode } from '../types/graph.types';

interface GraphSearchProps {
  onSelectNode: (node: GraphNode) => void;
}

const GraphSearch: React.FC<GraphSearchProps> = ({ onSelectNode }) => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<GraphNode[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [showResults, setShowResults] = useState<boolean>(false);
  const [activeIndex, setActiveIndex] = useState<number>(-1);
  
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Efecto para cerrar el dropdown al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
        setActiveIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  // Limpiar timeout al desmontar
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

  // Función para buscar nodos con manejo de errores mejorado
  const searchNodes = useCallback(async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      setShowResults(false);
      setActiveIndex(-1);
      return;
    }

    setIsSearching(true);
    try {
      const results = await graphApi.searchNodes(query);
      setSearchResults(results);
      setShowResults(true);
      setActiveIndex(-1);
    } catch (err) {
      console.error('Error al buscar nodos:', err);
      setSearchResults([]);
      // Mostrar mensaje de error en interfaz
    } finally {
      setIsSearching(false);
    }
  }, []);

  // Función para manejar cambios en el input con debounce mejorado
  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchQuery(value);
    
    // Limpiar timeout anterior si existe
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    // Debounce para no hacer demasiadas peticiones
    searchTimeoutRef.current = setTimeout(() => {
      searchNodes(value);
    }, 300);
  }, [searchNodes]);

  // Función para manejar la selección de un nodo
  const handleSelectNode = useCallback((node: GraphNode) => {
    onSelectNode(node);
    setSearchQuery(node.label);
    setShowResults(false);
    setActiveIndex(-1);
    inputRef.current?.blur();
  }, [onSelectNode]);

  // Función para manejar las teclas de navegación (Enter, Up, Down, Escape)
  const handleKeyDown = useCallback((event: React.KeyboardEvent<HTMLInputElement>) => {
    const resultsLength = searchResults.length;
    
    if (resultsLength === 0) return;
    
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setActiveIndex(prev => (prev < resultsLength - 1 ? prev + 1 : 0));
        break;
      case 'ArrowUp':
        event.preventDefault();
        setActiveIndex(prev => (prev > 0 ? prev - 1 : resultsLength - 1));
        break;
      case 'Enter':
        event.preventDefault();
        if (activeIndex >= 0 && activeIndex < resultsLength) {
          handleSelectNode(searchResults[activeIndex]);
        } else if (resultsLength > 0) {
          handleSelectNode(searchResults[0]);
        }
        break;
      case 'Escape':
        event.preventDefault();
        setShowResults(false);
        setActiveIndex(-1);
        inputRef.current?.blur();
        break;
      default:
        break;
    }
  }, [searchResults, activeIndex, handleSelectNode]);

  // Crear estado de aria-activedescendant basado en activeIndex
  const activeDescendant = useMemo(() => 
    activeIndex >= 0 && activeIndex < searchResults.length 
      ? `search-result-item-${searchResults[activeIndex].id}` 
      : "", 
    [activeIndex, searchResults]
  );

  return (
    <div className="graph-search-box" ref={searchRef} role="search">
      <label htmlFor="graph-search-input" className="visually-hidden">
        Buscar nodos en el grafo
      </label>
      <div className="graph-search-container">
        <input
          id="graph-search-input"
          ref={inputRef}
          type="search"
          className="graph-search-input"
          placeholder="Buscar conceptos..."
          value={searchQuery}
          onChange={handleSearchChange}
          onKeyDown={handleKeyDown}
          onClick={() => searchQuery && searchNodes(searchQuery)}
          autoComplete="off"
          aria-autocomplete="list"
          aria-controls="search-results-list"
          aria-activedescendant={activeDescendant}
          aria-label="Buscar conceptos, temas o notas"
          role="combobox"
          aria-expanded={showResults && searchResults.length > 0 ? "true" : "false"}
        />
        <button 
          className="graph-search-button" 
          type="submit"
          onClick={() => searchNodes(searchQuery)}
          disabled={isSearching}
          aria-label={isSearching ? "Buscando" : "Buscar"}
        >
          {isSearching ? (
            <span className="search-spinner" role="status" aria-hidden="true">
              <span className="visually-hidden">Buscando...</span>
            </span>
          ) : (
            <i className="fas fa-search" aria-hidden="true"></i>
          )}
        </button>
      </div>

      {showResults && searchResults.length > 0 && (
        <div 
          className="search-results"
          id="search-results-list"
          aria-label="Resultados de búsqueda"
        >
          <ul 
            className="search-results-list" 
            role="listbox"
            aria-label="Lista de resultados de búsqueda"
          >
            {searchResults.map((node, index) => {
              const handleKeyPress = (event: React.KeyboardEvent) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  handleSelectNode(node);
                }
              };
              
              return (
                <li
                  id={`search-result-item-${node.id}`}
                  key={node.id.toString()}
                  className={`search-result-item ${index === activeIndex ? 'active' : ''}`}
                  onClick={() => handleSelectNode(node)}
                  onKeyDown={handleKeyPress}
                  onMouseEnter={() => setActiveIndex(index)}
                  role="option"
                  aria-selected={index === activeIndex ? true : false}
                  tabIndex={0}
                >
                <span className="search-result-label">{node.label}</span>
                <span 
                  className={`search-result-badge search-badge-${getBadgeColor(node.type || 'default')}`}
                  title={`Tipo: ${node.type || 'Sin tipo'}`}
                >
                  {node.type || 'Sin tipo'}
                </span>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {showResults && searchResults.length === 0 && searchQuery.trim() !== '' && !isSearching && (
        <div 
          className="search-results" 
          role="status"
        >
          <div className="search-no-results">
            <i className="fas fa-info-circle" aria-hidden="true"></i>
            No se encontraron resultados
          </div>
        </div>
      )}
      
      {/* Texto de ayuda para el componente de búsqueda */}
      <div className="search-help-text" aria-live="polite" aria-atomic="true">
        {showResults && searchResults.length > 0 && (
          <span className="visually-hidden">
            {searchResults.length} resultados encontrados. Use las flechas arriba/abajo para navegar y Enter para seleccionar.
          </span>
        )}
      </div>
    </div>
  );
};

// Función auxiliar para asignar colores a los badges según el tipo de nodo
function getBadgeColor(type: string): string {
  switch (type.toLowerCase()) {
    case 'concept': return 'primary';
    case 'topic': return 'success';
    case 'note': return 'warning';
    case 'tag': return 'danger';
    default: return 'secondary';
  }
}

export default GraphSearch;
