import React, { useState } from 'react';
import { ProgressBar, Button, Spinner } from 'react-bootstrap';
import { analysisApi } from '../../../api/analysis';
import './TextAnalysisPanel.modern.css';

// Define the props for the component
interface TextAnalysisPanelProps {
  summary?: string;
  sentiment?: { score: number; label: string };
  readability?: { score: number; grade: string; };
  keywords?: string[];
  entities?: { [key: string]: string[] };
  isAnalyzing?: boolean;
  stats?: { words: number; paragraphs?: number; reading_time: number; };
  correctedText?: string;
  originalText?: string; // Para comparar y decidir si mostrar la corrección
  noteId?: number;       // ID de la nota para solicitar corrección gramatical
  onTextCorrected?: (correctedText: string) => void; // Callback para cuando se corrige el texto
}

const TextAnalysisPanel: React.FC<TextAnalysisPanelProps> = ({ 
  summary, 
  sentiment, 
  readability, 
  keywords,
  entities, 
  isAnalyzing, 
  stats, 
  correctedText, 
  originalText, 
  noteId, 
  onTextCorrected 
}) => {
  const [showAnalysis, setShowAnalysis] = useState<boolean>(true);
  const [copied, setCopied] = useState(false);
  const [isCorrecting, setIsCorrecting] = useState(false);
  const [correctionError, setCorrectionError] = useState<string | null>(null);

  // Helper to get color for readability progress bar
  const getReadabilityVariant = (score: number): string => {
    if (score > 60) return 'success';
    if (score > 30) return 'warning';
    return 'danger';
  };

  // Helper to get color for sentiment progress bar
  const getSentimentVariant = (label: string): string => {
    if (label === 'positive') return 'success';
    if (label === 'negative') return 'danger';
    return 'info'; // Usar 'info' para neutral, que es más adecuado que 'warning'
  };

  // Solicitar corrección gramatical independiente
  const handleRequestGrammarCorrection = async () => {
    if (!originalText || isCorrecting) return;
    
    setIsCorrecting(true);
    setCorrectionError(null);
    
    try {
      const result = await analysisApi.correctGrammar(originalText, noteId, { timeout: 180000 });
      
      if (result.has_changes) {
        // Notificar al componente padre sobre el texto corregido
        if (onTextCorrected && result.corrected_text) {
          onTextCorrected(result.corrected_text);
        }
      } else {
        // No hubo cambios necesarios
        setCorrectionError("No se detectaron cambios gramaticales necesarios");
      }
    } catch (error) {
      console.error('Error al solicitar corrección gramatical:', error);
      setCorrectionError("Error al procesar la corrección gramatical");
    } finally {
      setIsCorrecting(false);
    }
  };

  const handleCopy = () => {
    if (correctedText) {
      navigator.clipboard.writeText(correctedText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const hasAnalysisData = summary || sentiment || readability || stats;
  const showCorrection = correctedText && correctedText.trim() !== '' && correctedText !== originalText;

  return (
    <div className="analysis-panel-modern">
      <div className="analysis-header">
        <h3 className="analysis-title">Análisis de Texto</h3>
        <div className="header-actions">
          <button
            className="toggle-button"
            onClick={() => setShowAnalysis(!showAnalysis)}
            aria-expanded={showAnalysis}
            aria-label={showAnalysis ? 'Contraer análisis' : 'Expandir análisis'}
            type="button"
          >
            <i className={`fas fa-chevron-${showAnalysis ? 'up' : 'down'}`}></i>
          </button>
        </div>
      </div>

      {showAnalysis && (
        <div className="analysis-content">
          {/* Botón para solicitar corrección gramatical independiente */}
          {originalText && !isAnalyzing && (
            <div className="analysis-action-buttons mb-3">
              <Button 
                onClick={handleRequestGrammarCorrection}
                disabled={isCorrecting}
                variant="outline-primary"
                className="btn-primary-modern correction-request-button"
              >
                {isCorrecting ? (
                  <>
                    <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                    <span className="ml-2">Corrigiendo...</span>
                  </>
                ) : (
                  <>
                    <i className="fas fa-spell-check mr-2"></i>Solicitar corrección gramatical
                  </>
                )}
              </Button>
            </div>
          )}
          
          {/* Mostrar errores de corrección */}
          {correctionError && (
            <div className="alert alert-info mb-3">
              <i className="fas fa-info-circle mr-2"></i> {correctionError}
            </div>
          )}

          <div className="analysis-item summary-section">
            <h4 className="item-title"><i className="fas fa-file-alt"></i> Resumen Generado por IA</h4>
            <div className="item-content">
              {isAnalyzing ? (
                <div className="spinner-container"><div className="spinner"></div></div>
              ) : summary ? (
                <p className="analysis-text-content">{summary}</p>
              ) : (
                <p className="empty-text">Aún no hay análisis. Genere uno para ver el resumen y otros datos.</p>
              )}
            </div>
          </div>

          {showCorrection && !isAnalyzing && (
            <div className="analysis-item correction-section">
              <h4 className="item-title"><i className="fas fa-spell-check"></i> Corrección Gramatical</h4>
              <div className="item-content">
                <p className="analysis-text-content">{correctedText}</p>
                <Button 
                  variant="outline-secondary" 
                  size="sm" 
                  onClick={handleCopy}
                  disabled={copied}
                  className="copy-button btn-primary-modern"
                >
                  <i className={`fas ${copied ? 'fa-check' : 'fa-copy'}`}></i>
                  {copied ? ' Copiado' : ' Copiar'}
                </Button>
              </div>
            </div>
          )}

          {hasAnalysisData && !isAnalyzing && (
            <>
              {sentiment && (
                <div className="analysis-item">
                  <h4 className="item-title"><i className="fas fa-brain"></i> Sentimiento</h4>
                  <div className="item-content">
                    <span 
                      className={`sentiment-indicator ${sentiment.label === 'positive' ? 'positive' : sentiment.label === 'negative' ? 'negative' : 'neutral'}`}
                    ></span>
                    <span className="sentiment-text">
                      {sentiment.label === 'positive' ? 'Positivo' : sentiment.label === 'negative' ? 'Negativo' : 'Neutral'} 
                      ({(sentiment.score * 100).toFixed(1)}%)
                    </span>
                    <ProgressBar
                      now={sentiment.score * 100}
                      label={`Sentimiento: ${(sentiment.score * 100).toFixed(1)}%`}
                      variant={getSentimentVariant(sentiment.label)}
                    />
                  </div>
                </div>
              )}

              {readability && (
                <div className="analysis-item">
                  <h4 className="item-title"><i className="fas fa-book-open"></i> Legibilidad</h4>
                  <div className="item-content">
                    <ProgressBar
                      now={readability.score}
                      label={readability.grade}
                      variant={getReadabilityVariant(readability.score)}
                    />
                  </div>
                </div>
              )}

              {stats && (
                <div className="analysis-item">
                    <h4 className="item-title"><i className="fas fa-chart-bar"></i> Estadísticas</h4>
                    <div className="stats-grid">
                        <div className="stat-item">
                            <span className="stat-value">{stats.words}</span>
                            <span className="stat-label">Palabras</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-value">{stats.paragraphs ?? 'N/A'}</span>
                            <span className="stat-label">Párrafos</span>
                        </div>
                        <div className="stat-item">
                            <span className="stat-label">Tiempo lectura:</span>
                            <span className="stat-value">{stats.reading_time} min</span>
                        </div>
                    </div>
                </div>
              )}

              {keywords && keywords.length > 0 && (
                <div className="analysis-item">
                  <h4 className="item-title"><i className="fas fa-key"></i> Palabras Clave</h4>
                  <div className="keywords-container">
                    {keywords.map((keyword, index) => (
                      <span key={index} className="keyword-badge">{keyword}</span>
                    ))}
                  </div>
                </div>
              )}

              {entities && Object.keys(entities).length > 0 && (
                <div className="analysis-item">
                  <h4 className="item-title"><i className="fas fa-tags"></i> Entidades Detectadas</h4>
                  <div className="entities-container-modern">
                    {Object.entries(entities).map(([type, items]) => (
                      <div key={type} className="entity-group">
                        <h5 className="entity-type-title">{type}</h5>
                        <div className="entity-items">
                          {items.map((item, index) => (
                            <span key={index} className="entity-badge-modern">{item}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

        </div>
      )}
    </div>
  );
};

export default TextAnalysisPanel;


