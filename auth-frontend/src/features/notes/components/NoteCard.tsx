import React from 'react';
import { Link } from 'react-router-dom';
import './NoteCard.css';

export interface NoteCardProps {
  id: number;
  title: string;
  content: string;
  summary?: string;
  created_at: string;
  updated_at: string;
  user_id?: number;
  main_topic?: string;
  source_type?: string;
  tags?: { id: number; name: string }[];
  thumbnail_url?: string;
  onDelete?: (id: number) => void;
}

interface NoteCardComponentProps {
  note: NoteCardProps;
  viewMode: 'grid' | 'list';
  onDelete?: (id: number) => void;
}

const NoteCard: React.FC<NoteCardComponentProps> = ({ 
  note, 
  viewMode, 
  onDelete 
}) => {
  // Formatear fecha para mostrar de forma legible
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Truncar texto para mostrar un resumen
  const truncateText = (text: string, maxLength: number = 150): string => {
    if (!text) return 'Sin contenido';
    if (text.length <= maxLength) return text;
    
    // Buscar el último espacio antes del maxLength para cortar en palabras completas
    const lastSpace = text.substring(0, maxLength).lastIndexOf(' ');
    const truncateAt = lastSpace > 0 ? lastSpace : maxLength;
    return text.substring(0, truncateAt) + '...';
  };
  
  // Obtener un color de tema basado en el nombre
  const getTopicColor = (topic?: string): string => {
    if (!topic) return '#b2bec3'; // Color por defecto
    
    const colors: Record<string, string> = {
      'Informática': '#6c5ce7',
      'Tecnología': '#1a2b45', // Azul oscuro para coincidir con el header
      'Matemáticas': '#e17055',
      'Física': '#00b894',
      'Química': '#fdcb6e',
      'Biología': '#00cec9',
      'Historia': '#d63031',
      'Geografía': '#74b9ff',
      'Literatura': '#a29bfe',
      'Filosofía': '#636e72',
      'Economía': '#00b5ad',
      'Arte': '#e84393',
      'Música': '#6c5ce7',
      'Deportes': '#e67e22',
      'Salud': '#badc58',
      'Psicología': '#ff7675',
      'Estadística': '#ff9ff3',
      'Otro': '#b2bec3'
    };
    
    return colors[topic] || colors['Otro'];
  };

  // Confirmar eliminación antes de llamar a la función onDelete
  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (window.confirm('¿Estás seguro de que deseas eliminar esta nota?')) {
      onDelete?.(note.id);
    }
  };

  return (
    <div 
      className={`note-card ${viewMode === 'list' ? 'list-view-card' : ''}`} 
      aria-label={`Nota: ${note.title || 'Sin título'}`}
    >
      <div className="note-header">
        <div className="note-header-content">
          {note.main_topic && (
            <span 
              className="topic-badge"
              style={{ backgroundColor: getTopicColor(note.main_topic) }}
            >
              {note.main_topic}
            </span>
          )}
          <h3 className="note-title">{note.title || 'Sin título'}</h3>
        </div>
        
        <div className="note-actions">
          <Link 
            to={`/notes/${note.id}`}
            className="action-button view-button"
            title="Ver nota"
            aria-label="Ver nota"
          >
            <i className="fas fa-eye"></i>
          </Link>
          
          <Link 
            to={`/notes/edit/${note.id}`}
            className="action-button edit-button"
            title="Editar nota"
            aria-label="Editar nota"
          >
            <i className="fas fa-edit"></i>
          </Link>
          
          {onDelete && (
            <button 
              type="button" 
              className="action-button delete-button"
              onClick={handleDelete}
              title="Eliminar nota"
              aria-label="Eliminar nota"
            >
              <i className="fas fa-trash-alt"></i>
            </button>
          )}
        </div>
      </div>
      
      <Link to={`/notes/${note.id}`} className="note-content-link" aria-label={`Ver nota ${note.title || 'Sin título'}`}>
        {note.thumbnail_url && (
          <div 
            className="note-thumbnail" 
            style={{ backgroundImage: `url(${note.thumbnail_url})` }}
            role="img"
            aria-label="Miniatura de la nota"
          />
        )}
        
        <div className="note-body">
          <div className="note-summary">
            {note.summary || truncateText(note.content) || 'Sin contenido'}
          </div>
          
          <div className="note-tags">
            {note.tags?.map(tag => (
              <span 
                key={tag.id}
                className="tag-badge"
              >
                {tag.name}
              </span>
            ))}
          </div>
        </div>
      </Link>
      
      <div className="note-footer">
        <div className="note-meta">
          <span title={`Creado el ${new Date(note.created_at).toLocaleString()}`}>
            <i className="fas fa-calendar-alt" aria-hidden="true"></i>
            <span className="visually-hidden">Fecha:</span>
            {formatDate(note.created_at)}
          </span>
          <span>
            <i className="fas fa-file-alt" aria-hidden="true"></i>
            <span className="visually-hidden">Tipo:</span>
            {note.source_type || 'Texto'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default NoteCard;
