import React, { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '../../../store/authStore';
import { useNavigate, Link } from 'react-router-dom';
import { notesApi } from '../../../api/notes';
import type { NotesFilters } from '../../../api/notes';
import { tagsApi } from '../../../api/tags';
import { filesApi } from '../../../api/files';
import StatCard from '../components/StatCard';
import RecentNotesList from '../components/RecentNotesList';
import './DashboardPage.css';

// Definir interfaces para los datos que se manejarán
// Definir interfaces para los datos que se manejarán
interface Topic {
  id: number;
  name: string;
  note_count?: number;
}

interface Note {
  id: number;
  title: string;
  content: string;
  summary?: string;
  created_at: string;
  updated_at: string;
  user_id: number;
  main_topic?: string;
  source_type?: string;
  tags?: { id: number; name: string }[];
}

interface Stats {
  totalNotes: number;
  totalTags: number;
  totalTopics?: number;
  totalImages: number;
}

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [stats, setStats] = useState<Stats>({ totalNotes: 0, totalTags: 0, totalImages: 0 });
  const [recentNotes, setRecentNotes] = useState<Note[]>([]);
  const [isLoadingStats, setIsLoadingStats] = useState(true);
  const [isLoadingNotes, setIsLoadingNotes] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [isLoadingTopics, setIsLoadingTopics] = useState(true);
  // Estado para ordenamiento
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest' | 'alphabetical'>('newest');
  const [frequentTags, setFrequentTags] = useState<{id: number; name: string; count: number}[]>([]);

  // Cargar estadísticas
  const fetchStats = async () => {
    setIsLoadingStats(true);
    try {
      // Realizar llamadas paralelas para optimizar la carga
      const [notesStats, tagsStats, filesStats] = await Promise.all([
        notesApi.getNotesStatistics(),
        tagsApi.getTagsStatistics(),
        filesApi.getFileStatistics()
      ]);

      setStats({
        totalNotes: notesStats.total || 0,
        totalTags: tagsStats.total || 0,
        totalTopics: notesStats.topics_count || 0,
        totalImages: filesStats.total || 0
      });
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    } finally {
      setIsLoadingStats(false);
    }
  };

  // Cargar estadísticas y etiquetas frecuentes al iniciar
  useEffect(() => {
    fetchStats();
    fetchFrequentTags();
  }, []);

  // Cargar notas recientes
  // Cargar tópicos disponibles
  useEffect(() => {
    const fetchTopics = async () => {
      setIsLoadingTopics(true);
      try {
        const response = await notesApi.getTopics();
        // La API ahora devuelve un array directamente
        setTopics(response || []);
      } catch (error) {
        console.error('Error al cargar tópicos:', error);
      } finally {
        setIsLoadingTopics(false);
      }
    };

    fetchTopics();
  }, []);

  // Función para obtener etiquetas frecuentes
  const fetchFrequentTags = async () => {
    try {
      const response = await tagsApi.getTagsStatistics();
      if (response.frequent_tags) {
        setFrequentTags(response.frequent_tags);
      }
    } catch (error) {
      console.error('Error al cargar etiquetas frecuentes:', error);
    }
  };

  // Ordenar notas según el criterio seleccionado
  const sortNotes = useCallback((notes: Note[]) => {
    const compareFn = (a: Note, b: Note) => {
      switch (sortOrder) {
        case 'newest':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'oldest':
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        case 'alphabetical':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    };
    return [...notes].sort(compareFn);
  }, [sortOrder]);

  useEffect(() => {
    const fetchRecentNotes = async () => {
      setIsLoadingNotes(true);
      try {
        // Si hay un tópico seleccionado, filtramos por él
        const params: NotesFilters = selectedTopic 
          ? { topic: selectedTopic, per_page: 6 } 
          : { per_page: 6 };
        
        const response = await notesApi.getNotes(params); 
        const sortedNotes = sortNotes(response.notes || []);
        setRecentNotes(sortedNotes);
      } catch (error) {
        console.error('Error al cargar notas recientes:', error);
      } finally {
        setIsLoadingNotes(false);
      }
    };

    fetchRecentNotes();
  }, [selectedTopic, sortOrder, sortNotes]);

  // Función para eliminar una nota
  const handleDeleteNote = async (noteId: number) => {
    try {
      await notesApi.deleteNote(noteId);
      // Actualizar el estado local para eliminar la nota sin recargar
      setRecentNotes(prevNotes => prevNotes.filter(note => note.id !== noteId));
      // Actualizar estadísticas después de eliminar
      fetchStats();
    } catch (error) {
      console.error('Error al eliminar nota:', error);
      alert('Error al eliminar la nota. Inténtalo de nuevo.');
    }
  };

  // Función para la búsqueda rápida
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/notes?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  // Función para cambiar el tópico seleccionado
  const handleTopicChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedTopic(e.target.value);
  };

  // Función para cambiar el orden de las notas
  const handleSortChange = (newOrder: 'newest' | 'oldest' | 'alphabetical') => {
    setSortOrder(newOrder);
  };

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">Inicio</h1>
      
      {/* Bienvenida y rol del usuario */}
      <div className="welcome-card">
        <h2>Bienvenido/a, {user?.name || user?.username || 'Usuario'}</h2>
        <p>Un resumen de tu actividad reciente y contenido.</p>
        <span className="user-role">{user?.role || 'estudiante'}</span>
      </div>
      
      {/* Estadísticas rápidas */}
      <div className="stats-grid">
        <StatCard 
          icon="fa-sticky-note" 
          value={isLoadingStats ? '...' : stats.totalNotes} 
          label="Notas" 
          color="#3498db"
          isLoading={isLoadingStats}
        />
        <StatCard 
          icon="fa-tag" 
          value={isLoadingStats ? '...' : stats.totalTags} 
          label="Etiquetas" 
          color="#2ecc71"
          isLoading={isLoadingStats}
        />
        <StatCard 
          icon="fa-lightbulb" 
          value={isLoadingStats ? '...' : stats.totalTopics || 0} 
          label="Temas" 
          color="#f39c12"
          isLoading={isLoadingStats}
        />
        <StatCard 
          icon="fa-image" 
          value={isLoadingStats ? '...' : stats.totalImages} 
          label="Imágenes" 
          color="#e74c3c"
          isLoading={isLoadingStats}
        />
      </div>
      
      {/* Etiquetas frecuentes */}
      {frequentTags.length > 0 && (
        <div className="actions-container mb-4">
          <h3 className="notes-title mb-3">Etiquetas más utilizadas</h3>
          <div className="note-tags-container">
            {frequentTags.slice(0, 8).map(tag => (
              <Link 
                to={`/notes?tag=${tag.id}`} 
                key={tag.id} 
                className="modern-note-tag"
                title={`${tag.count} notas con esta etiqueta`}
              >
                <i className="fas fa-tag me-1"></i> {tag.name}
                <span className="ms-1 badge rounded-pill bg-light text-dark">{tag.count}</span>
              </Link>
            ))}
          </div>
        </div>
      )}
      
      {/* Acciones rápidas */}
      <div className="actions-container">
        <div className="row">
          <div className="col-md-8">
            <form onSubmit={handleSearch}>
              <div className="search-container">
                <i className="fas fa-search search-icon"></i>
                <input 
                  type="text" 
                  className="form-control search-input" 
                  placeholder="Buscar en mis notas..."
                  aria-label="Búsqueda"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </form>
          </div>
          <div className="col-md-4 d-flex justify-content-end align-items-center">
            <Link to="/notes/new" className="btn btn-success create-note-btn">
              <i className="fas fa-plus"></i>
              <span>Nueva Nota</span>
            </Link>
          </div>
        </div>
      </div>
      
      {/* Notas recientes */}
      <div className="recent-notes-container">
        <div className="notes-header">
          <div className="notes-header-content">
            <h3 className="notes-title">Notas recientes</h3>
            
            <div className="d-flex gap-2 align-items-center">
              <select 
                className="form-select topic-selector" 
                value={selectedTopic} 
                onChange={handleTopicChange}
                aria-label="Filtrar por tema"
                disabled={isLoadingTopics}
              >
                <option value="">Todos los temas</option>
                {Array.isArray(topics) && topics.map((topic) => (
                  <option key={topic.id} value={topic.name}>{topic.name}</option>
                ))}
              </select>
              
              <div className="sorting-controls">
                <button 
                  type="button" 
                  className={`sort-button ${sortOrder === 'newest' ? 'active' : ''}`}
                  onClick={() => handleSortChange('newest')}
                  aria-label="Ordenar por más recientes"
                >
                  <i className="fas fa-clock"></i> Recientes
                </button>
                <button 
                  type="button" 
                  className={`sort-button ${sortOrder === 'oldest' ? 'active' : ''}`}
                  onClick={() => handleSortChange('oldest')}
                  aria-label="Ordenar por más antiguos"
                >
                  <i className="fas fa-history"></i> Antiguos
                </button>
                <button 
                  type="button" 
                  className={`sort-button ${sortOrder === 'alphabetical' ? 'active' : ''}`}
                  onClick={() => handleSortChange('alphabetical')}
                  aria-label="Ordenar alfabéticamente"
                >
                  <i className="fas fa-sort-alpha-down"></i> A-Z
                </button>
              </div>
              
              <Link to="/notes" className="btn btn-outline-primary btn-sm view-all-link">
                <span>Ver todas</span>
                <i className="fas fa-arrow-right"></i>
              </Link>
            </div>
          </div>
        </div>
        
        <RecentNotesList 
          notes={recentNotes}
          isLoading={isLoadingNotes}
          onDeleteNote={handleDeleteNote}
        />
      </div>
    </div>
  );
};

export default DashboardPage;
