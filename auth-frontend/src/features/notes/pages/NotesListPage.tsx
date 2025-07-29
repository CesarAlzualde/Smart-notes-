import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { notesApi } from '../../../api/notes';
import { tagsApi } from '../../../api/tags';
import type { Tag as ApiTag } from '../../../api/tags';
import NoteCard from '../components/NoteCard';
import type { NoteCardProps } from '../components/NoteCard';
import NotesFilterBar from '../components/NotesFilterBar';
import type { NotesFilter } from '../components/NotesFilterBar';
import Pagination from '../components/Pagination';
import useInfiniteScroll from '../../../hooks/useInfiniteScroll';
import './NotesListPage.modern.css';

interface Topic {
  id: number;
  name: string;
}

// Tipo para los parámetros de la API
type NoteApiParams = {
  [key: string]: string | number | string[] | undefined;
  page: number;
  per_page: number;
};

const NotesListPage: React.FC = () => {
  const [notes, setNotes] = useState<NoteCardProps[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [tags, setTags] = useState<ApiTag[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalNotes, setTotalNotes] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMoreNotes, setHasMoreNotes] = useState(true);

  const [searchParams, setSearchParams] = useSearchParams();

  const viewMode = (searchParams.get('view') as 'grid' | 'list') || 'grid';
  const scrollMode = (searchParams.get('scroll') as 'pagination' | 'infinite') || 'pagination';

  const getFiltersFromUrl = useCallback((params: URLSearchParams): NotesFilter => {
    const filters: NotesFilter = {};
    for (const [key, value] of params.entries()) {
      if (key === 'source_types') {
        if (!filters.source_types) {
          filters.source_types = [];
        }
        filters.source_types = params.getAll('source_types');
      } else if (key === 'page') {
        filters.page = Number(value);
      } else {
        filters[key as keyof Omit<NotesFilter, 'source_types' | 'page'>] = value;
      }
    }
    return filters;
  }, []);

  const fetchNotes = useCallback(async (page: number, filters: NotesFilter) => {
    setIsLoading(true);
    if (page === 1) {
      setNotes([]); // Limpiar notas al cambiar de filtro o en la primera carga
    }

    try {
      const queryParams: NoteApiParams = { ...filters, page, per_page: 10 };

      // Renombrar 'topic' a 'topic_id' para que coincida con el backend
      // y asegurarse de que se envía como número
      if (queryParams.topic) {
        queryParams.topic_id = Number(queryParams.topic) || queryParams.topic;
        delete queryParams.topic;
      }

      if (queryParams.date) {
        queryParams.date_filter = queryParams.date;
        delete queryParams.date;
      }

      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === undefined || queryParams[key] === null || queryParams[key] === '') {
          delete queryParams[key];
        }
      });

      const response: { notes: NoteCardProps[], total: number, page: number, pages: number } = await notesApi.getNotes(queryParams);

      setNotes(prev => (page > 1 ? [...prev, ...response.notes] : response.notes));
      setTotalPages(response.pages);
      setTotalNotes(response.total);
      setCurrentPage(response.page);
      setHasMoreNotes(response.page < response.pages);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al cargar las notas.';
      setError(message);
      console.error('Error fetching notes:', err);
    } finally {
      setIsLoading(false);
    }
  }, [setCurrentPage, setError, setHasMoreNotes, setIsLoading, setNotes, setTotalNotes, setTotalPages]);

  useEffect(() => {
    const filters = getFiltersFromUrl(searchParams);
    const page = Number(searchParams.get('page') || '1');
    fetchNotes(page, filters);
  }, [searchParams, fetchNotes, getFiltersFromUrl]);

  useEffect(() => {
    const fetchTopicsAndTags = async () => {
      setIsLoading(true);
      try {
        // Definimos temas predeterminados
        const defaultTopics = [
          { id: 1, name: 'Arquitectura' },
          { id: 2, name: 'Derecho y Leyes' },
          { id: 3, name: 'Gestión de Proyectos' },
          { id: 4, name: 'Diseño Gráfico' },
          { id: 5, name: 'Educación' },
          { id: 6, name: 'Desarrollo Personal' },
          { id: 7, name: 'Emprendimiento' },
          { id: 8, name: 'General' },
        ];

        // Intentamos obtener temas del backend
        let topicsData = [];
        try {
          const topicsResponse = await notesApi.getTopics();
          // Validamos los temas del backend
          topicsData = Array.isArray(topicsResponse) ? topicsResponse : [];
          topicsData = topicsData.filter(topic => topic && topic.id);
          console.log('Temas recibidos del backend:', topicsData);
        } catch (error) {
          console.error('Error al obtener temas del backend:', error);
        }

        // Si el backend no devuelve temas o hay error, usamos los predeterminados
        if (!topicsData || topicsData.length === 0) {
          console.log('Usando temas predeterminados');
          setTopics(defaultTopics);
        } else {
          setTopics(topicsData);
        }

        // Obtenemos etiquetas
        try {
          const tagsResponse = await tagsApi.getTags();
          setTags(Array.isArray(tagsResponse) ? tagsResponse : []);
        } catch (error) {
          console.error('Error al obtener etiquetas:', error);
          setTags([]);
        }
      } catch (err) {
        console.error('Error fetching topics or tags:', err);
        setError('Error al cargar filtros. Inténtalo de nuevo.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchTopicsAndTags();
  }, [setError]);

  const handleFilterChange = (filters: NotesFilter) => {
    console.log('🔍 Aplicando filtros:', filters); // Debug
    
    const newSearchParams = new URLSearchParams();
    
    // Procesar cada filtro individualmente
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          // Para otros arrays, convertir a string
          const arrayValue = value.filter(v => v && v.trim()).join(',');
          if (arrayValue) {
            newSearchParams.set(key, arrayValue);
          }
        } else {
          // Para valores simples
          const stringValue = String(value).trim();
          if (stringValue) {
            newSearchParams.set(key, stringValue);
          }
        }
      }
    });
    
    // Siempre resetear a página 1 cuando se cambian filtros
    newSearchParams.set('page', '1');
    
    console.log('📝 URL params finales:', newSearchParams.toString()); // Debug
    setSearchParams(newSearchParams);
  };

  const handlePageChange = (newPage: number) => {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set('page', String(newPage));
    setSearchParams(newSearchParams);
  };

  const { setElement } = useInfiniteScroll(() => {
    if (hasMoreNotes && !isLoading && scrollMode === 'infinite') {
      const nextPage = currentPage + 1;
      if (nextPage <= totalPages) {
        handlePageChange(nextPage);
      }
    }
  });

  const handleScrollModeChange = (mode: 'pagination' | 'infinite') => {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set('scroll', mode);
    setSearchParams(newSearchParams);
  };

  const handleViewModeChange = (mode: 'grid' | 'list') => {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set('view', mode);
    setSearchParams(newSearchParams);
  };

  const handleDeleteNote = async (noteId: number) => {
    try {
      await notesApi.deleteNote(noteId);
      
      // Actualizar el estado local para eliminar la nota sin recargar
      setNotes(notes.filter(note => note.id !== noteId));
      
      // Si era la última nota de la página y no es la primera página, ir a la página anterior
      if (notes.length === 1 && currentPage > 1) {
        handlePageChange(currentPage - 1);
      } else {
        // Recargar la página actual para actualizar el conteo total
        const currentFilters = getFiltersFromUrl(searchParams);
        handleFilterChange({
          ...currentFilters,
          page: currentPage
        });
      }
    } catch (error) {
      console.error('Error al eliminar nota:', error);
      setError('Error al eliminar la nota. Inténtalo de nuevo más tarde.');
    }
  };

  return (
    <div className="notes-page-container">
      <div className="notes-header">
        <h1 className="notes-title">Mis Notas</h1>
        <a href="/notes/new" className="create-note-btn">
          <i className="fas fa-plus"></i>
          <span>Nueva Nota</span>
        </a>
      </div>
      
      {/* Barra de filtros */}
      <div className="filter-container">
        <NotesFilterBar
          initialFilters={getFiltersFromUrl(searchParams)}
          onFilterChange={handleFilterChange}
          topics={topics}
          tags={tags}
          isLoading={isLoading}
          onViewModeChange={handleViewModeChange}
          currentViewMode={viewMode}
          onScrollModeChange={handleScrollModeChange}
          currentScrollMode={scrollMode}
        />
      </div>
      
      {/* Mensajes de error */}
      {error && (
        <div className="error-message" role="alert">
          <i className="fas fa-exclamation-circle"></i>
          {error}
        </div>
      )}
      
      {/* Contador de resultados */}
      {!isLoading && !error && (
        <div className="results-summary">
          <p className="results-count">
            {totalNotes === 0 ? (
              'No se encontraron notas'
            ) : totalNotes === 1 ? (
              '1 nota encontrada'
            ) : (
              `${totalNotes} notas encontradas`
            )}
            {searchParams.toString() && ' con los filtros aplicados'}
          </p>
        </div>
      )}
      
      {/* Contenedor de notas con modo de vista */}
      <div id="notes-container" className={viewMode === 'list' ? 'list-view' : 'grid-view'}>
        {isLoading ? (
          <div className="loading-container">
            <div className="spinner" role="status">
              <span className="visually-hidden">Cargando...</span>
            </div>
            <p>Buscando tus notas...</p>
          </div>
        ) : notes.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-sticky-note"></i>
            <h3>No hay notas disponibles</h3>
            <p>
              {searchParams.toString() 
                ? 'Prueba a cambiar los filtros o crear una nueva nota.'
                : 'Comienza creando una nueva nota para organizar tus ideas.'}
            </p>
            <a href="/notes/new" className="create-note-btn">
              <i className="fas fa-plus"></i>
              <span>Crear Nota</span>
            </a>
          </div>
        ) : (
          <>
            {/* Las notas se renderizan directamente como hijos del contenedor, sin filas adicionales en modo grid */}
            {viewMode === 'grid' ? (
              notes.map(note => (
                <NoteCard 
                  key={note.id}
                  note={note}
                  viewMode={viewMode}
                  onDelete={handleDeleteNote}
                />
              ))
            ) : (
              notes.map(note => (
                <NoteCard 
                  key={note.id}
                  note={note}
                  viewMode={viewMode}
                  onDelete={handleDeleteNote}
                />
              ))
            )}
          </>
        )}
      </div>
      
      {/* Paginación - Solo mostrar en modo paginación */}
      {totalPages > 1 && scrollMode === 'pagination' && (
        <div className="pagination-wrapper">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalNotes}
            itemsPerPage={10} /* Ajustar según la configuración real de la API */
            onPageChange={handlePageChange}
            isLoading={isLoading}
          />
        </div>
      )}
      
      {/* Indicador de carga para scroll infinito */}
      {isLoading && scrollMode === 'infinite' && currentPage > 1 && (
        <div className="infinite-scroll-loader">
          <div className="spinner"></div>
          <span>Cargando más notas...</span>
        </div>
      )}
      
      {/* Elemento de referencia para infinite scroll */}
      {scrollMode === 'infinite' && hasMoreNotes && !isLoading && (
        <div ref={setElement} className="infinite-scroll-trigger"></div>
      )}
    </div>
  );
};

export default NotesListPage;
