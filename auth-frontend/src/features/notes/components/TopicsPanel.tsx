import React, { useState } from 'react';
import type { TopicDistribution } from '../../../api/analysis';
import { Form, Button, Badge, ProgressBar } from 'react-bootstrap';
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
  onSaveTopics?: (mainTopic: string, topics: Array<Topic>) => void;
  availableTopics?: Array<Topic>;
}

const TopicsPanel: React.FC<TopicsPanelProps> = ({
  mainTopic = '',
  topics = [],
  suggestedTopics = [],
  topicsDistribution = [],
  confidence = 0,
  onSaveTopics,
  availableTopics = [],
}) => {
  const [showPanel, setShowPanel] = useState<boolean>(true);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  
  // State for editing, initialized empty
  const [editMainTopic, setEditMainTopic] = useState<string>('');
  const [editTopics, setEditTopics] = useState<Topic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<string>('');

  // Function to enter edit mode and initialize edit state from props
  const handleEnterEditMode = () => {
    setEditMainTopic(mainTopic);
    setEditTopics(topics);
    setIsEditing(true);
  };

  // Function to cancel editing
  const handleCancel = () => {
    setIsEditing(false);
    // No need to reset state, it will be re-initialized on next edit
  };

  // Function to save changes
  const handleSave = () => {
    if (onSaveTopics) {
      onSaveTopics(editMainTopic, editTopics);
    }
    setIsEditing(false);
  };

  const handleAddTopic = (topicName: string) => {
    const topicToAdd = availableTopics?.find(t => t.name === topicName);
    if (topicToAdd && !editTopics.some(t => t.id === topicToAdd.id)) {
      setEditTopics(prev => [...prev, topicToAdd]);
    }
  };

  const handleRemoveTopic = (topicId: number) => {
    setEditTopics(prev => prev.filter(t => t.id !== topicId));
  };

  const handleHeaderClick = () => setShowPanel(!showPanel);
  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      handleHeaderClick();
    }
  };
  
  // Función helper para calcular y formatear porcentajes de manera robusta
  const calculatePercentage = (confidence?: number, score?: number, weight?: number): number => {
    // Caso 1: Si weight está presente (campo usado por el backend)
    if (weight !== undefined) {
      // Si es un decimal (0-1)
      if (weight >= 0 && weight <= 1) {
        return Math.round(weight * 100);
      } 
      // Si ya es un porcentaje (1-100)
      else if (weight > 1 && weight <= 100) {
        return Math.round(weight);
      }
    }
    // Caso 2: Si confidence está presente y es un decimal (0-1)
    if (confidence !== undefined && confidence >= 0 && confidence <= 1) {
      return Math.round(confidence * 100);
    }
    // Caso 3: Si confidence está presente y ya es un porcentaje (1-100)
    else if (confidence !== undefined && confidence > 1 && confidence <= 100) {
      return Math.round(confidence);
    }
    // Caso 4: Si score está presente y es un decimal (0-1)
    else if (score !== undefined && score >= 0 && score <= 1) {
      return Math.round(score * 100);
    }
    // Caso 5: Si score está presente y ya es un porcentaje (1-100)
    else if (score !== undefined && score > 1 && score <= 100) {
      return Math.round(score);
    }
    // Caso por defecto
    return 0;
  };

  return (
    <div className="topics-panel">
      <div
        className="panel-header"
        onClick={handleHeaderClick}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        aria-expanded={showPanel}
        aria-controls="topics-panel-content"
      >
        <h3>
          <i className="fas fa-tags"></i>
          Clasificación temática
          <i className={`fas fa-chevron-${showPanel ? 'up' : 'down'} toggle-icon`}></i>
        </h3>
      </div>

      {showPanel && (
        <div className="panel-content" id="topics-panel-content">
          {!isEditing ? (
            // VIEW MODE
            <>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">Clasificación Actual</h5>
                <Button variant="outline-primary" size="sm" onClick={handleEnterEditMode}>
                  <i className="fas fa-edit"></i> Editar
                </Button>
              </div>

              {mainTopic && (
                <div className="mb-3">
                  <h6><i className="fas fa-star"></i> Tema Principal</h6>
                  <div>
                    <Badge bg="primary">{mainTopic}</Badge>
                    {(confidence || 0) > 0 && <span className="ms-2 text-muted">({((confidence || 0) * 100).toFixed(0)}%)</span>}
                  </div>
                  {(confidence || 0) > 0 && (
                    <ProgressBar 
                      now={(confidence || 0) * 100} 
                      label={`${((confidence || 0) * 100).toFixed(0)}%`}
                      variant="info"
                      className="mt-2"
                    />
                  )}
                </div>
              )}

              {topics.length > 0 && (
                <div className="mb-3">
                  <h6><i className="fas fa-tags"></i> Temas Relacionados</h6>
                  <div className="d-flex flex-wrap gap-1">
                    {topics.map((topic: Topic) => (
                      <Badge key={topic.id} bg="secondary">{topic.name}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* AI-Generated Topic Distribution */}
              {topicsDistribution && topicsDistribution.length > 0 && (
                <div className="mb-3">
                  <h6 className="panel-subtitle"><i className="fas fa-brain"></i> Distribución de Temas (IA)</h6>
                  {topicsDistribution.map((dist: TopicDistribution) => (
                    <div key={dist.topic} className="mb-2 topic-distribution-item">
                      <span className="topic-distribution-name">
                        {dist.topic}
                        <span className="topic-percentage ms-2">{`${calculatePercentage(dist.confidence, dist.score, dist.weight)}%`}</span>
                      </span>
                      <ProgressBar 
                        now={calculatePercentage(dist.confidence, dist.score, dist.weight)} 
                        variant="success"
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* AI-Generated Suggested Topics */}
              {suggestedTopics && suggestedTopics.length > 0 && (
                <div className="mb-3">
                  <h6><i className="fas fa-lightbulb"></i> Sugerencias de la IA</h6>
                  <div className="d-flex flex-wrap gap-1">
                    {suggestedTopics.map((topic: string, index: number) => (
                      <Badge bg="info" text="dark" key={index} className="suggested-topic-badge">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            // EDIT MODE
            <>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">Editar Clasificación</h5>
              </div>

              <div className="mb-3">
                <Form.Label>Tema principal</Form.Label>
                <Form.Select
                  value={editMainTopic}
                  onChange={(e) => setEditMainTopic(e.target.value)}
                >
                  <option value="">Seleccionar tema principal...</option>
                  {availableTopics?.map((topic: Topic) => (
                    <option key={topic.id} value={topic.name}>
                      {topic.name}
                    </option>
                  ))}
                </Form.Select>
              </div>

              <div className="mb-3">
                <Form.Label>Temas relacionados</Form.Label>
                <div className="selected-topics mb-2">
                  {editTopics.map((topic: Topic) => (
                    <Badge
                      bg="primary"
                      className="me-1 mb-1 topic-badge"
                      key={topic.id}
                    >
                      {topic.name}
                      <span
                        className="topic-remove-btn ms-1"
                        onClick={() => handleRemoveTopic(topic.id)}
                        onKeyDown={(e) => e.key === 'Enter' && handleRemoveTopic(topic.id)}
                        role="button"
                        tabIndex={0}
                        aria-label={`Quitar tema ${topic.name}`}
                      >
                        ×
                      </span>
                    </Badge>
                  ))}
                  {editTopics.length === 0 && (
                    <div className="text-muted small">Sin temas seleccionados</div>
                  )}
                </div>

                <div className="d-flex mb-2">
                  <Form.Select
                    value={selectedTopic}
                    onChange={(e) => {
                      if (e.target.value) handleAddTopic(e.target.value);
                      setSelectedTopic(''); // Reset after adding
                    }}
                    className="me-2"
                  >
                    <option value="">Añadir un tema...</option>
                    {availableTopics
                      ?.filter((topic: Topic) => !editTopics.some((t: Topic) => t.name === topic.name))
                      .map((topic: Topic) => (
                        <option key={topic.id} value={topic.name}>
                          {topic.name}
                        </option>
                      ))}
                  </Form.Select>
                </div>
              </div>

              {suggestedTopics && suggestedTopics.length > 0 && (
                <div className="mt-3 mb-3">
                  <h6><i className="fas fa-lightbulb"></i> Sugerencias</h6>
                  <div className="d-flex flex-wrap gap-1 mt-2">
                    {suggestedTopics
                      .filter((topic: string) => !editTopics.some((t: Topic) => t.name === topic))
                      .map((topic: string, index: number) => (
                        <Badge
                          bg="light"
                          text="dark"
                          className="me-1 mb-1 topic-badge"
                          key={index}
                          style={{ cursor: 'pointer' }}
                          onClick={() => handleAddTopic(topic)}
                          onKeyDown={(e) => e.key === 'Enter' && handleAddTopic(topic)}
                          role="button"
                          tabIndex={0}
                        >
                          {topic} <span className="ms-1 text-primary">+</span>
                        </Badge>
                      ))}
                  </div>
                </div>
              )}

              <div className="d-flex justify-content-end mt-3">
                <Button
                  variant="outline-secondary"
                  size="sm"
                  className="me-2"
                  onClick={handleCancel}
                >
                  <i className="fas fa-times"></i> Cancelar
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleSave}
                >
                  <i className="fas fa-save"></i> Guardar clasificación
                </Button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default TopicsPanel; 
