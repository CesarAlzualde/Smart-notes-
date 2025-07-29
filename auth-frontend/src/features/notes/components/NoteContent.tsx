import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import './NoteContent.css';

interface NoteContentProps {
  note: {
    title: string;
    content: string;
    summary?: string;
    created_at: string;
    updated_at?: string;
    source_type?: string;
  };
}

const NoteContent: React.FC<NoteContentProps> = ({ note }) => {
  // Formatear fecha
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return 'Fecha desconocida';
    }
  };

  return (
    <div className="note-content-view">
      <h1>{note.title || 'Sin título'}</h1>
      
      <div className="note-metadata">
        <span className="note-date">
          <i className="fas fa-calendar-alt"></i>
          <span>{formatDate(note.created_at)}</span>
        </span>
        
        {note.updated_at && note.updated_at !== note.created_at && (
          <span className="note-updated">
            <i className="fas fa-edit"></i>
            <span>Actualizada: {formatDate(note.updated_at)}</span>
          </span>
        )}
        
        {note.source_type && (
          <span className="note-source">
            <i className="fas fa-file-alt"></i>
            <span>{note.source_type}</span>
          </span>
        )}
      </div>
      
      {note.summary && (
        <div className="note-summary-section">
          <h3 className="note-summary-title">
            <i className="fas fa-robot"></i>
            Resumen IA
          </h3>
          <div className="note-summary-content">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]} 
              rehypePlugins={[rehypeRaw]}
              components={{
                div: ({ ...props}) => <div className="markdown-content" {...props} />
              }}
            >
              {note.summary}
            </ReactMarkdown>
          </div>
        </div>
      )}
      
      <div className="note-body">
        {note.content ? (
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]} 
            rehypePlugins={[rehypeRaw]}
            components={{
              // Sobrescribir el componente div para aplicar nuestra clase personalizada
              div: ({ ...props}) => <div className="markdown-content" {...props} />
            }}
          >
            {note.content}
          </ReactMarkdown>
        ) : (
          <p className="note-content-empty">No hay contenido disponible</p>
        )}
      </div>
    </div>
  );
};

export default NoteContent;
