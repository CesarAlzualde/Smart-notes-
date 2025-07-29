import React, { useState } from 'react';
import './NoteMetadata.css';

interface NoteMetadataProps {
  note: {
    id?: number;
    summary?: string;
    tags?: Array<{ id: number; name: string }>;
    topics?: Array<{ id: number; name: string }>;
    main_topic?: string;
    related_notes?: Array<{ id: number; title: string }>;
    ai_keywords?: Array<string>;
    ai_entities?: Array<{ name: string; type: string }>;
    ai_sentiment?: { score: number; label: string };
    ai_analysis_ready?: boolean;
    created_at: string;
    updated_at?: string;
    source_type?: string;
  };
  onGenerateAnalysis: () => void;
  isAnalyzing: boolean;
}

const NoteMetadata: React.FC<NoteMetadataProps> = ({ note, onGenerateAnalysis, isAnalyzing }) => {
  const [showAIAnalysis, setShowAIAnalysis] = useState(true);

  return (
    <>
      {/* Panel de análisis y resumen */}
      <div className="metadata-panel">
        <div className="metadata-header">
          <h3 className="section-title">Análisis de Resumen</h3>
          <button 
            className="toggle-button" 
            onClick={() => setShowAIAnalysis(!showAIAnalysis)}
            aria-expanded={showAIAnalysis}
            aria-label={showAIAnalysis ? 'Contraer análisis de resumen' : 'Expandir análisis de resumen'}
            type="button"
          >
            <i className={`fas fa-chevron-${showAIAnalysis ? 'up' : 'down'}`}></i>
          </button>
        </div>
        
        {showAIAnalysis && (
          <div className="metadata-content">
            <div className="summary-section">
              <h4 className="section-title">Resumen</h4>
              {note.summary ? (
                <p>{note.summary}</p>
              ) : (
                <p className="empty-text">No hay resumen disponible</p>
              )}
            </div>
            
            {note.ai_keywords && note.ai_keywords.length > 0 && (
              <div className="metadata-section">
                <h4 className="section-title">Palabras Clave</h4>
                <div>
                  {note.ai_keywords.map((keyword, index) => (
                    <span className="keyword-badge" key={index}>
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {note.ai_entities && note.ai_entities.length > 0 && (
              <div className="metadata-section">
                <h4 className="section-title">Entidades Detectadas</h4>
                <div>
                  {note.ai_entities.map((entity, index) => (
                    <span className="entity-badge" key={index} title={`Tipo: ${entity.type}`}>
                      {entity.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {note.ai_sentiment && (
              <div className="metadata-section">
                <h4 className="section-title">Análisis de Sentimiento</h4>
                <div className="sentiment-section">
                  <span 
                    className={`sentiment-indicator ${
                      note.ai_sentiment.label === 'positive' ? 'positive' : 
                      note.ai_sentiment.label === 'negative' ? 'negative' : 'neutral'
                    }`}
                  ></span>
                  <span className="sentiment-text">
                    {note.ai_sentiment.label === 'positive' ? 'Positivo' : 
                     note.ai_sentiment.label === 'negative' ? 'Negativo' : 'Neutral'} 
                    ({(note.ai_sentiment.score * 100).toFixed(1)}%)
                  </span>
                </div>
              </div>
            )}
            
            {note.id && (
              <div className="metadata-section">
                <button 
                  className="generate-analysis-btn"
                  onClick={onGenerateAnalysis}
                  disabled={isAnalyzing}
                >
                  {isAnalyzing ? (
                    <><i className="fas fa-spinner fa-spin"></i><span>Generando...</span></>
                  ) : (
                    <><i className="fas fa-magic"></i><span>Generar Análisis IA</span></>
                  )}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Panel de clasificación y tags */}
      <div className="metadata-panel">
        <div className="metadata-header">
          <h3 className="section-title">Clasificación</h3>
        </div>
        <div className="metadata-content">
          <div className="metadata-section">
            <h4 className="section-title">Tema Principal</h4>
            {note.main_topic ? (
              <p className="main-topic">{note.main_topic}</p>
            ) : (
              <p className="empty-text">Sin tema principal</p>
            )}
          </div>
          
          <div className="metadata-section">
            <h4 className="section-title">Temas Relacionados</h4>
            {note.topics && note.topics.length > 0 ? (
              <div className="topics-list">
                {note.topics.map((topic) => (
                  <span className="topic-badge" key={topic.id}>
                    {topic.name}
                  </span>
                ))}
              </div>
            ) : (
              <p className="empty-text">No hay temas relacionados</p>
            )}
          </div>
          
          <div className="metadata-section">
            <h4 className="section-title">Etiquetas</h4>
            {note.tags && note.tags.length > 0 ? (
              <div className="tags-list">
                {note.tags.map((tag) => (
                  <span className="tag-badge" key={tag.id}>
                    {tag.name}
                  </span>
                ))}
              </div>
            ) : (
              <p className="empty-text">No hay etiquetas</p>
            )}
          </div>
        </div>
      </div>
      
      {/* Panel de notas relacionadas */}
      {note.related_notes && note.related_notes.length > 0 && (
        <div className="metadata-panel">
          <div className="metadata-header">
            <h3 className="section-title">Notas Relacionadas</h3>
          </div>
          <div className="metadata-content">
            <ul className="related-notes-list">
              {note.related_notes.map((relatedNote) => (
                <li key={relatedNote.id}>
                  <a href={`/notes/${relatedNote.id}`}>{relatedNote.title}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </>
  );
};

export default NoteMetadata;
