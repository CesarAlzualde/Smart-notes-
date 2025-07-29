import React, { useState, useEffect } from 'react';
import './NotesFilterBar.css';

interface Topic {
  id: number;
  name: string;
}

interface Tag {
  id: number;
  name: string;
}

export interface NotesFilter {
  search?: string;
  topic?: string | number;
  tag?: string;
  source_types?: string[];
  date?: string;
  date_filter?: string; // Para el backend
  date_from?: string;
  date_to?: string;
  sort?: string;
  page?: number;
}

interface NotesFilterBarProps {
  initialFilters: NotesFilter;
  onFilterChange: (filters: NotesFilter) => void;
  topics: Topic[];
  tags: Tag[];
  isLoading?: boolean;
  onViewModeChange: (mode: 'grid' | 'list') => void;
  currentViewMode: 'grid' | 'list';
  onScrollModeChange?: (mode: 'pagination' | 'infinite') => void;
  currentScrollMode?: 'pagination' | 'infinite';
}

const NotesFilterBar: React.FC<NotesFilterBarProps> = ({
  initialFilters,
  onFilterChange,
  topics,
  tags,
  isLoading = false,
  onViewModeChange,
  currentViewMode,
  onScrollModeChange,
  currentScrollMode = 'pagination'
}) => {
  // Estado local para los filtros
  const [filters, setFilters] = useState<NotesFilter>(initialFilters);
  const [sourceTypes, setSourceTypes] = useState<string[]>(initialFilters.source_types || []);
  
  // Actualizar estado local cuando cambien los initialFilters
  useEffect(() => {
    setFilters(initialFilters);
    setSourceTypes(initialFilters.source_types || []);
  }, [initialFilters]);

  // Manejar cambios en los filtros básicos
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    const newFilters = { ...filters };

    // Usar un switch para manejar los casos de forma explícita y segura
    switch (name) {
      case 'search':
      case 'tag':
      case 'date':
      case 'date_from':
      case 'date_to':
      case 'sort':
        newFilters[name] = value || undefined;
        break;
      case 'topic':
        if (value) {
          const numericValue = Number(value);
          newFilters.topic = !isNaN(numericValue) ? numericValue : value;
        } else {
          delete newFilters.topic;
        }
        break;
    }

    // Si se cambia el preajuste de fecha a algo que no sea personalizado, limpiar las fechas personalizadas
    if (name === 'date' && value !== 'custom') {
      delete newFilters.date_from;
      delete newFilters.date_to;
    }
    
    setFilters(newFilters);
  };

  // Manejar cambios en los checkboxes de tipo de fuente
  const handleSourceTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    
    let updatedSourceTypes: string[];
    
    if (checked) {
      updatedSourceTypes = [...sourceTypes, value];
    } else {
      updatedSourceTypes = sourceTypes.filter(type => type !== value);
    }
    
    setSourceTypes(updatedSourceTypes);
    
    setFilters({
      ...filters,
      source_types: updatedSourceTypes.length > 0 ? updatedSourceTypes : undefined
    });
  };

  // Enviar el formulario de búsqueda
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Preparar filtros finales
    const finalFilters: NotesFilter = {
      ...filters,
      // Reset to page 1 on new search
      page: 1
    };
  
    // Mapear 'date' a 'date_filter' para el backend
    if (filters.date) {
      finalFilters.date_filter = filters.date;
      delete finalFilters.date; // Eliminar el campo 'date' original
    }
  
    // El backend ahora maneja directamente los valores de ordenamiento
  
    // Añadir source_types solo si hay alguno seleccionado
    if (sourceTypes && sourceTypes.length > 0) {
      finalFilters.source_types = sourceTypes;
    } else {
      delete finalFilters.source_types;
    }

    // Si la fecha no es personalizada, eliminamos los campos date_from y date_to
    if (filters.date !== 'custom') {
      delete finalFilters.date_from;
      delete finalFilters.date_to;
    }
    
    // Aplicar los filtros
    onFilterChange(finalFilters);
  };

  // Limpiar todos los filtros
  // Limpiar todos los filtros
  const handleClearFilters = () => {
    // Se resetea al estado inicial vacío, la página se manejará en el padre
    const clearedFilters: NotesFilter = {};
    setFilters(clearedFilters);
    setSourceTypes([]);
    onFilterChange(clearedFilters);
  };

  return (
    <div className="filter-container">
      <form className="search-form" onSubmit={handleSubmit}>
        {/* Búsqueda principal */}
        <div className="search-group">
          <i className="fas fa-search search-icon"></i>
          <input
            type="text"
            className="form-control search-input"
            name="search"
            placeholder="Buscar notas por título, contenido o etiquetas..."
            value={filters.search || ''}
            onChange={handleFilterChange}
            aria-label="Buscar notas"
          />
        </div>

        {/* Filtros adicionales */}
        <div className="additional-filters">
          <div className="row">
            {/* Primera fila de filtros */}
            <div className="col-md-4 filter-section">
              <label htmlFor="sort-filter" className="filter-label">Ordenar por</label>
              <select 
                id="sort-filter"
                className="form-control filter-select"
                name="sort"
                value={filters.sort || 'relevance'}
                onChange={handleFilterChange}
                aria-label="Ordenar notas por"
              >
                <option value="relevance">Relevancia</option>
                <option value="newest">Más recientes</option>
                <option value="oldest">Más antiguas</option>
              </select>
            </div>

            <div className="col-md-4 filter-section">
              <label htmlFor="topic-filter" className="filter-label">Tema</label>
              <select 
                id="topic-filter"
                className="form-control filter-select"
                name="topic"
                value={filters.topic || ''}
                onChange={handleFilterChange}
                aria-label="Filtrar por tema"
              >
                <option value="">Todos los temas</option>
                {topics.map(topic => (
                  <option key={`topic-${topic.id}-${topic.name}`} value={topic.id}>{topic.name}</option>
                ))}
              </select>
            </div>

            <div className="col-md-4 filter-section">
              <label htmlFor="tag-filter" className="filter-label">Etiqueta</label>
              <select 
                id="tag-filter"
                className="form-control filter-select"
                name="tag"
                value={filters.tag || ''}
                onChange={handleFilterChange}
                aria-label="Filtrar por etiqueta"
              >
                <option value="">Todas las etiquetas</option>
                {tags.map(tag => (
                  <option key={`tag-${tag.id}-${tag.name}`} value={tag.id}>{tag.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="row">
            {/* Segunda fila de filtros */}
            <div className="col-md-4 filter-section">
              <fieldset className="filter-fieldset">
                <legend className="filter-label">Tipo de fuente</legend>
                <div className="button-group" role="group">
                <label htmlFor="source-text" className={`filter-checkbox ${sourceTypes.includes('Texto') ? 'active' : ''}`}>
                  <input
                    type="checkbox"
                    id="source-text"
                    value="Texto"
                    checked={sourceTypes.includes('Texto')}
                    onChange={handleSourceTypeChange}
                  />
                  <i className="fas fa-pen-alt"></i>
                  Texto
                </label>
                <label htmlFor="source-ocr" className={`filter-checkbox ${sourceTypes.includes('OCR') ? 'active' : ''}`}>
                  <input
                    type="checkbox"
                    id="source-ocr"
                    value="OCR"
                    checked={sourceTypes.includes('OCR')}
                    onChange={handleSourceTypeChange}
                  />
                  <i className="fas fa-camera"></i>
                  OCR
                </label>
                <label htmlFor="source-pdf" className={`filter-checkbox ${sourceTypes.includes('PDF') ? 'active' : ''}`}>
                  <input
                    type="checkbox"
                    id="source-pdf"
                    value="PDF"
                    checked={sourceTypes.includes('PDF')}
                    onChange={handleSourceTypeChange}
                  />
                  <i className="fas fa-file-pdf"></i>
                  PDF
                </label>
              </div>
              </fieldset>
            </div>

            <div className="col-md-4 filter-section">
              <label htmlFor="date-filter" className="filter-label">Periodo</label>
              <select 
                id="date-filter"
                className="form-control filter-select"
                name="date"
                value={filters.date || 'any'}
                onChange={handleFilterChange}
                aria-label="Seleccionar periodo"
              >
                <option value="any">Cualquier fecha</option>
                <option value="today">Hoy</option>
                <option value="yesterday">Ayer</option>
                <option value="last_7_days">Últimos 7 días</option>
                <option value="last_30_days">Últimos 30 días</option>
                <option value="this_month">Este mes</option>
                <option value="this_year">Este año</option>
                <option value="custom">Personalizado</option>
              </select>
              
              {filters.date === 'custom' && (
                <div className="custom-date-range">
                  <label htmlFor="date_from">Desde</label>
                  <input
                    type="date"
                    id="date_from"
                    className="form-control"
                    name="date_from"
                    value={filters.date_from || ''}
                    onChange={handleFilterChange}
                    aria-label="Fecha desde"
                  />
                  <label htmlFor="date_to">Hasta</label>
                  <input
                    type="date"
                    id="date_to"
                    className="form-control"
                    name="date_to"
                    value={filters.date_to || ''}
                    onChange={handleFilterChange}
                    aria-label="Fecha hasta"
                  />
                </div>
              )}
            </div>
            <div className="col-md-4 filter-section">
              <fieldset className="filter-fieldset">
                <legend className="filter-label">Vista</legend>
                <div className="button-group filter-button-group" role="group">
                <input type="radio" id="view-grid" name="viewMode" value="grid" checked={currentViewMode === 'grid'} onChange={() => onViewModeChange('grid')} />
                <label htmlFor="view-grid" className="view-button">
                  <i className="fas fa-th-large"></i> Cuadrícula
                </label>
                <input type="radio" id="view-list" name="viewMode" value="list" checked={currentViewMode === 'list'} onChange={() => onViewModeChange('list')} />
                <label htmlFor="view-list" className="view-button">
                  <i className="fas fa-list"></i> Lista
                </label>
                </div>
              </fieldset>
            </div>

            {onScrollModeChange && (
              <div className="col-md-4 filter-section">
                <fieldset className="filter-fieldset">
                  <legend className="filter-label">Navegación</legend>
                  <div className="button-group filter-button-group" role="group">
                  <input type="radio" id="scroll-pagination" name="scrollMode" value="pagination" checked={currentScrollMode === 'pagination'} onChange={() => onScrollModeChange('pagination')} />
                  <label htmlFor="scroll-pagination" className="scroll-button">
                    <i className="fas fa-file-alt"></i> Paginación
                  </label>
                  <input type="radio" id="scroll-infinite" name="scrollMode" value="infinite" checked={currentScrollMode === 'infinite'} onChange={() => onScrollModeChange('infinite')} />
                  <label htmlFor="scroll-infinite" className="scroll-button">
                    <i className="fas fa-infinity"></i> Infinita
                  </label>
                  </div>
                </fieldset>
              </div>
            )}
          </div>
        </div>
        
        {/* Botones de acción */}
        <div className="action-buttons">
          <button 
            type="button" 
            className="clear-button"
            onClick={handleClearFilters}
            aria-label="Limpiar filtros"
          >
            <i className="fas fa-times"></i>
            <span>Limpiar filtros</span>
          </button>
          
          <button 
            type="submit" 
            className="filter-button"
            disabled={isLoading}
          >
            <i className="fas fa-filter"></i>
            <span>
              {isLoading ? 'Aplicando...' : 'Aplicar filtros'}
            </span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default NotesFilterBar;
