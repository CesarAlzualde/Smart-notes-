import React, { useState, useEffect } from 'react';
import { analysisApi } from '../../../api/analysis';
import type { TopicDistribution } from '../../../api/analysis';
import './TopicsPanel.modern.css';

interface Topic {
  id: number;
  name: string;
  confidence?: number;
}

interface TopicsPanelProps {
  mainTopic?: string;
  topics?: Array<Topic>;
  suggestedTopics?: Array<string>;
  topicsDistribution?: Array<TopicDistribution>;
  confidence?: number;
  availableTopics?: Array<Topic>;
  onSaveTopics?: (mainTopic: string, topics: Array<Topic>) => void;
  noteId?: number;
  content?: string;
}

const TopicsPanel: React.FC<TopicsPanelProps> = ({ 
  mainTopic = '', 
  topics = [], 
  suggestedTopics = [],
  topicsDistribution = [],
  confidence = 0,
  availableTopics = [],
  onSaveTopics,
  noteId,
  content = ''
}) => {
  const [showPanel, setShowPanel] = useState<boolean>(true);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editMainTopic, setEditMainTopic] = useState<string>(mainTopic);
  const [editTopics, setEditTopics] = useState<Topic[]>(topics);
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  
  // Estado para análisis de temas
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [localTopicsDistribution, setLocalTopicsDistribution] = useState<TopicDistribution[]>(topicsDistribution);
  const [localSuggestedTopics, setLocalSuggestedTopics] = useState<string[]>(suggestedTopics);
  const [localConfidence, setLocalConfidence] = useState<number>(confidence);
  const [localMainTopic, setLocalMainTopic] = useState<string>(mainTopic);
  
  // Analizar temas cuando cambia el contenido
  useEffect(() => {
    if (content && content.trim().length > 50) {
      analyzeTopics(content);
    }
  }, [content, noteId]);
  
  // Función para analizar temas
  const analyzeTopics = async (textContent: string) => {
    // No analizamos si estamos en modo edición
    if (isEditing) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await analysisApi.analyzeTopics(textContent, noteId);
      
      setLocalTopicsDistribution(result.topics_distribution);
      setLocalSuggestedTopics(result.suggested_topics);
      setLocalConfidence(result.main_topic_confidence * 100); // Convertir a porcentaje
      setLocalMainTopic(result.main_topic);
      
      // Solo actualizar con nuevos valores si no estamos en modo edición
      if (!isEditing && onSaveTopics && result.main_topic) {
        // Crear estructura de temas basada en la distribución
        // Nota: guardamos el análisis en las variables locales, pero no llamamos
        // a onSaveTopics aquí para evitar loops - el componente padre debe manejar la persistencia
        // cuando decide que es apropiado (por ejemplo, al guardar explícitamente)
        
        // El código siguiente está comentado para evitar llamadas automáticas que puedan generar loops
        /*
        const newTopics = result.topics_distribution
          .filter(item => item.topic !== result.main_topic && item.percentage > 0.05) // Solo temas con más de 5% de relevancia
          .map(item => {
            const existingTopic = availableTopics.find(t => t.name === item.topic);
            return existingTopic || {
              id: Math.floor(Math.random() * -1000), // ID temporal negativo
              name: item.topic
            };
          });
        
        onSaveTopics(result.main_topic, newTopics);
        */
      }
    } catch (err) {
      console.error('Error al analizar temas:', err);
      setError('Error al analizar temas');
    } finally {
      setLoading(false);
    }
  };

  // Manejar modo de edición
  const handleEditMode = () => {
    setIsEditing(true);
    setEditMainTopic(mainTopic);
    setEditTopics([...topics]);
  };

  // Cancelar edición
  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditMainTopic(mainTopic);
    setEditTopics([...topics]);
  };

  // Guardar cambios en temas
  const handleSaveTopics = () => {
    if (onSaveTopics) {
      onSaveTopics(editMainTopic, editTopics);
      setIsEditing(false);
    }
  };

  // Añadir tema seleccionado
  const handleAddTopic = () => {
    if (!selectedTopic) return;
    
    // Buscar si el tema ya existe en availableTopics
    const existingTopic = availableTopics.find(t => t.name === selectedTopic);
    
    if (existingTopic && !editTopics.some(t => t.id === existingTopic.id)) {
      setEditTopics([...editTopics, existingTopic]);
    } else if (!existingTopic && !editTopics.some(t => t.name === selectedTopic)) {
      // Crear un tema temporal con ID negativo
      const newTopic = {
        id: Math.floor(Math.random() * -1000), // ID temporal negativo
        name: selectedTopic
      };
      setEditTopics([...editTopics, newTopic]);
    }
    
    setSelectedTopic('');
  };

  // Eliminar tema
  const handleRemoveTopic = (topicId: number) => {
    setEditTopics(editTopics.filter(topic => topic.id !== topicId));
  };

  // Añadir tema sugerido
  const handleAddSuggested = (topicName: string) => {
    // No añadir si ya existe
    if (editTopics.some(t => t.name === topicName)) return;
    
    // Buscar si el tema ya existe en availableTopics
    const existingTopic = availableTopics.find(t => t.name === topicName);
    
    if (existingTopic) {
      setEditTopics([...editTopics, existingTopic]);
    } else {
      // Crear un tema temporal con ID negativo
      const newTopic = {
        id: Math.floor(Math.random() * -1000), // ID temporal negativo
        name: topicName
      };
      setEditTopics([...editTopics, newTopic]);
    }
  };

  // Determina qué clase usar para la barra de progreso según el porcentaje
  const getProgressColorClass = (percentage: number): string => {
    if (percentage >= 60) return 'high';
    if (percentage >= 40) return 'medium';
    return 'low';
  };

  return (
    <div className="topics-panel">
      <div className="topics-header">
        <h3 className="topics-title">
          <i className="fas fa-tags"></i> Clasificación temática
        </h3>
        <div className="header-actions">
          {!isEditing && onSaveTopics && (
            <button 
              className="action-button" 
              onClick={handleEditMode}
              disabled={loading}
            >
              <i className="fas fa-edit"></i>
            </button>
          )}
          <button 
            className="toggle-button" 
            onClick={() => setShowPanel(!showPanel)}
          >
            <i className={`fas fa-chevron-${showPanel ? 'up' : 'down'}`}></i>
          </button>
        </div>
      </div>

      {showPanel && (
        <div className="topics-content">
          {error && (
            <div className="alert alert-danger">
              <i className="fas fa-exclamation-circle"></i> {error}
            </div>
          )}
          
          {loading && (
            <div className="text-center">
              <div className="spinner"></div>
              <p className="mt-2">Analizando contenido...</p>
            </div>
          )}
          
          {!isEditing && (
            <>
              {/* Tema principal */}
              <div className="section">
                <h4 className="section-title">
                  <i className="fas fa-bookmark"></i> Tema principal
                </h4>
                
                {mainTopic ? (
                  <div className="topic-badge primary">{mainTopic}</div>
                ) : (
                  <p className="empty-text">Sin tema principal asignado</p>
                )}
                
                {localMainTopic && localMainTopic !== mainTopic && (
                  <div className="mt-2">
                    <p className="text-muted small">Sugerido por el análisis: </p>
                    <div className="topic-badge light">
                      {localMainTopic} 
                    </div>
                  </div>
                )}
                
                {localConfidence > 0 && (
                  <div className="progress-container mt-2">
                    <div className="progress-header">
                      <span className="progress-label">Confianza</span>
                      <span className="progress-value">{Math.round(localConfidence)}%</span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className={`progress-indicator ${getProgressColorClass(localConfidence)}`}
                        style={{ width: `${localConfidence}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Temas relacionados */}
              <div className="section">
                <h4 className="section-title">
                  <i className="fas fa-layer-group"></i> Temas relacionados
                </h4>
                
                {topics.length > 0 ? (
                  <div className="topic-badges">
                    {topics.map((topic) => (
                      <div 
                        className="topic-badge" 
                        key={topic.id}
                      >
                        {topic.name}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="empty-text">Sin temas relacionados</p>
                )}
              </div>
              
              {/* Distribución de temas */}
              {localTopicsDistribution.length > 0 && (
                <div className="section">
                  <h4 className="section-title">
                    <i className="fas fa-chart-bar"></i> Distribución de temas
                  </h4>
                  
                  {localTopicsDistribution.map((item, index) => (
                    <div className="progress-container" key={index}>
                      <div className="progress-header">
                        <span className="progress-label">{item.topic}</span>
                        <span className="progress-value">{Math.round(item.percentage * 100)}%</span>
                      </div>
                      <div className="progress-bar">
                        <div 
                          className="progress-indicator"
                          style={{ width: `${item.percentage * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Temas sugeridos */}
              {localSuggestedTopics.length > 0 && (
                <div className="section">
                  <h4 className="section-title">
                    <i className="fas fa-lightbulb"></i> Temas sugeridos
                  </h4>
                  
                  <div className="topic-badges">
                    {localSuggestedTopics.map((topic, index) => (
                      <div 
                        className="topic-badge light" 
                        key={index}
                      >
                        {topic}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
          
          {/* Modo edición */}
          {isEditing && (
            <>
              <div className="form-section">
                <label className="form-label" htmlFor="edit-main-topic">
                  Tema principal
                </label>
                <select 
                  id="edit-main-topic" 
                  className="form-select"
                  value={editMainTopic}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setEditMainTopic(e.target.value)}
                >
                  <option value="">Sin tema principal</option>
                  {availableTopics.map((topic) => (
                    <option key={topic.id} value={topic.name}>
                      {topic.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="form-section">
                <label className="form-label">Temas relacionados</label>
                <div className="selected-topics">
                  {editTopics.map((topic) => (
                    <div 
                      className="topic-badge"
                      key={topic.id}
                    >
                      {topic.name}
                      <span 
                        className="topic-remove-btn"
                        onClick={() => handleRemoveTopic(topic.id)}
                      >
                        ×
                      </span>
                    </div>
                  ))}
                  {editTopics.length === 0 && (
                    <div className="empty-text">Sin temas seleccionados</div>
                  )}
                </div>
                
                <div className="input-group mt-2">
                  <select
                    className="form-select"
                    value={selectedTopic}
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedTopic(e.target.value)}
                  >
                    <option value="">Seleccionar tema...</option>
                    {availableTopics
                      .filter(t => !editTopics.some(et => et.id === t.id))
                      .map((topic) => (
                        <option key={topic.id} value={topic.name}>
                          {topic.name}
                        </option>
                      ))}
                  </select>
                  <button 
                    className="action-button"
                    onClick={handleAddTopic}
                  >
                    <i className="fas fa-plus"></i>
                  </button>
                </div>
              </div>
              
              {/* Temas sugeridos (modo edición) */}
              {suggestedTopics.length > 0 && (
                <div className="section">
                  <h4 className="section-title">
                    <i className="fas fa-lightbulb"></i> Sugerencias
                  </h4>
                  <div className="topic-badges">
                    {suggestedTopics
                      .filter(topic => !editTopics.some(t => t.name === topic))
                      .map((topic, index) => (
                        <div 
                          className="topic-badge light" 
                          key={index}
                          onClick={() => handleAddSuggested(topic)}
                          style={{ cursor: 'pointer' }}
                        >
                          {topic} <span className="topic-add-btn">+</span>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              <div className="button-group">
                <button 
                  className="button button-secondary"
                  onClick={handleCancelEdit}
                >
                  <i className="fas fa-times"></i> Cancelar
                </button>
                <button 
                  className="button button-primary"
                  onClick={handleSaveTopics}
                >
                  <i className="fas fa-save"></i> Guardar clasificación
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default TopicsPanel;
