import React from 'react';
import { Link } from 'react-router-dom';
import './NotesList.css'; // Crearemos este archivo para los estilos modernos

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
  thumbnail_url?: string;
  file_type?: string;
}

interface RecentNotesListProps {
  notes: Note[];
  isLoading: boolean;
  onDeleteNote?: (id: number) => void;
}

const RecentNotesList: React.FC<RecentNotesListProps> = ({
  notes,
  isLoading,
  onDeleteNote
}) => {
  // Formatear fecha para mostrar en formato legible
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Truncar texto para mostrar un resumen
  const truncateText = (text: string, maxLength: number = 150): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (isLoading) {
    return (
      <div className="notes-loading">
        <div className="spinner-border text-primary spinner" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
        <p>Cargando notas...</p>
      </div>
    );
  }

  if (!notes || notes.length === 0) {
    return (
      <div className="no-notes-message">
        <i className="fas fa-sticky-note"></i>
        <p>No hay notas disponibles</p>
        <Link to="/notes/new" className="btn btn-sm btn-primary mt-2">
          <i className="fas fa-plus me-2"></i>Crear una nota
        </Link>
      </div>
    );
  }

  // Función para determinar el icono correcto según el tipo de nota
  const getNoteIcon = (note: Note) => {
    if (note.file_type?.includes('image')) return 'fa-image';
    if (note.file_type?.includes('pdf')) return 'fa-file-pdf';
    if (note.file_type?.includes('word') || note.file_type?.includes('document')) return 'fa-file-word';
    if (note.source_type === 'Audio') return 'fa-music';
    if (note.source_type === 'Video') return 'fa-video';
    return 'fa-sticky-note';
  };

  // Determinar si la nota tiene una miniatura para mostrar
  const hasValidThumbnail = (note: Note) => {
    return note.thumbnail_url && note.thumbnail_url !== '';
  };

  return (
    <div className="note-grid">
      {notes.map(note => (
        <div key={note.id} className="modern-note-card">
          <div className="modern-card-header">
            <h3 className="modern-note-title" title={note.title || 'Sin título'}>
              {note.title || 'Sin título'}
            </h3>
            <div className="dropdown">
              <button 
                className="note-actions-btn" 
                type="button" 
                data-bs-toggle="dropdown"
                aria-expanded="false"
                aria-label="Acciones de nota"
                title="Opciones de nota"
              >
                <i className="fas fa-ellipsis-v"></i>
              </button>
              <ul className="dropdown-menu dropdown-menu-end modern-dropdown-menu">
                <li>
                  <Link className="modern-dropdown-item" to={`/notes/${note.id}`}>
                    <i className="fas fa-eye"></i> Ver
                  </Link>
                </li>
                <li>
                  <Link className="modern-dropdown-item" to={`/notes/edit/${note.id}`}>
                    <i className="fas fa-edit"></i> Editar
                  </Link>
                </li>
                {onDeleteNote && (
                  <>
                    <li><hr className="dropdown-divider" /></li>
                    <li>
                      <button 
                        className="modern-dropdown-item danger-item" 
                        onClick={() => {
                          if (window.confirm('¿Estás seguro de que deseas eliminar esta nota?')) {
                            onDeleteNote(note.id);
                          }
                        }}
                      >
                        <i className="fas fa-trash-alt"></i> Eliminar
                      </button>
                    </li>
                  </>
                )}
              </ul>
            </div>
          </div>
          
          {/* Miniatura o icono del tipo de nota */}
          {hasValidThumbnail(note) ? (
            <div className="note-thumbnail-container">
              <img 
                className="note-thumbnail" 
                src={note.thumbnail_url} 
                alt={note.title || 'Miniatura de nota'} 
              />
            </div>
          ) : (
            <div className="note-thumbnail-container">
              <div className="no-thumbnail">
                <i className={`fas ${getNoteIcon(note)}`}></i>
              </div>
            </div>
          )}
          
          <div className="modern-card-body">
            <p className="modern-note-summary">
              {note.summary || truncateText(note.content, 150) || 'Sin contenido'}
            </p>
            
            <div className="note-tags-container">
              {note.main_topic && (
                <span className="modern-note-tag modern-note-topic">
                  <i className="fas fa-lightbulb me-1"></i> {note.main_topic}
                </span>
              )}
              {note.tags && note.tags.map(tag => (
                <span key={tag.id} className="modern-note-tag">
                  <i className="fas fa-tag me-1"></i> {tag.name}
                </span>
              ))}
            </div>
          </div>
          
          <div className="modern-card-footer">
            <div className="modern-note-meta">
              <span className="meta-item">
                <i className="far fa-calendar-alt meta-icon"></i>
                {formatDate(note.created_at)}
              </span>
              <span className="meta-item">
                <i className={`fas ${getNoteIcon(note)} meta-icon`}></i>
                {note.source_type || 'Texto'}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default RecentNotesList;
