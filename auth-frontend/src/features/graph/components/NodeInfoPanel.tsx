import React from 'react';
import { Link } from 'react-router-dom';
import './NodeInfoPanel.css';

import type { GraphNode } from '../types/graph.types';

interface NodeInfoPanelProps {
  node: GraphNode;
  onClose: () => void;
}

const NodeInfoPanel: React.FC<NodeInfoPanelProps> = ({ node, onClose }) => {
  // Función para obtener ruta según tipo de nodo
  const getNodeLink = () => {
    switch (node.type.toLowerCase()) {
      case 'note':
        return `/notes/${node.id}`;
      case 'topic':
        return `/notes?topic=${encodeURIComponent(node.label)}`;
      case 'tag':
        return `/notes?tag=${encodeURIComponent(node.label)}`;
      default:
        return null;
    }
  };
  
  // Obtiene un color de fondo basado en el color del nodo (ligero)
  const getBackgroundColor = () => {
    if (node.color) {
      // Convertir a fondo claro añadiendo transparencia
      return `${node.color}20`;
    }
    return '';
  };
  
  // Formatear la fecha si existe en las propiedades
  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric' 
      });
    } catch (e) {
      return dateString;
    }
  };
  
  // Obtener la propiedad de descripción si existe
  const getDescription = () => {
    if (!node.properties) return '';
    
    if (node.properties.description) {
      return node.properties.description;
    } else if (node.properties.content) {
      // Si hay contenido, mostrar un extracto
      return node.properties.content.length > 200 
        ? `${node.properties.content.substring(0, 200)}...` 
        : node.properties.content;
    }
    
    return '';
  };

  return (
    <div className="node-info-panel" style={{ borderColor: node.color }}>
      <div 
        className="node-info-header" 
        style={{ backgroundColor: getBackgroundColor() }}
      >
        <h5 className="node-info-title">{node.label}</h5>
        <button 
          className="btn-close" 
          onClick={onClose} 
          aria-label="Cerrar"
        ></button>
      </div>
      
      <div className="node-info-body">
        <div className="node-info-type">
          <span 
            className="badge"
            style={{ backgroundColor: node.color }}
          >
            {node.type}
          </span>
        </div>
        
        {getDescription() && (
          <div className="node-info-description mt-3">
            <h6>Descripción</h6>
            <p>{getDescription()}</p>
          </div>
        )}
        
        {/* Mostrar propiedades relevantes */}
        <div className="node-info-props mt-3">
          <h6>Propiedades</h6>
          <ul className="list-group">
            {node.properties?.created_at && (
              <li className="list-group-item d-flex justify-content-between align-items-center">
                <span>Fecha creación</span>
                <span className="badge bg-light text-dark">
                  {formatDate(node.properties.created_at)}
                </span>
              </li>
            )}
            
            {node.properties?.author && (
              <li className="list-group-item d-flex justify-content-between align-items-center">
                <span>Autor</span>
                <span className="badge bg-light text-dark">
                  {node.properties.author}
                </span>
              </li>
            )}
            
            {node.properties?.sentiment && (
              <li className="list-group-item d-flex justify-content-between align-items-center">
                <span>Sentimiento</span>
                <span className={`badge bg-${getSentimentBadgeColor(node.properties.sentiment)}`}>
                  {getSentimentLabel(node.properties.sentiment)}
                </span>
              </li>
            )}
          </ul>
        </div>
        
        {/* Botón de acción según tipo de nodo */}
        {getNodeLink() && (
          <div className="d-grid gap-2 mt-3">
            <Link 
              to={getNodeLink() || '#'} 
              className="btn btn-primary"
            >
              {getActionButtonText(node.type)}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

// Funciones auxiliares
function getActionButtonText(type: string): string {
  switch (type.toLowerCase()) {
    case 'note':
      return 'Ver Nota';
    case 'topic':
      return 'Ver Notas del Tema';
    case 'tag':
      return 'Ver Notas con esta Etiqueta';
    default:
      return 'Ver Detalles';
  }
}

function getSentimentBadgeColor(sentiment: number | string): string {
  const value = typeof sentiment === 'string' ? parseFloat(sentiment) : sentiment;
  if (value > 0.1) return 'success';
  if (value < -0.1) return 'danger';
  return 'secondary';
}

function getSentimentLabel(sentiment: number | string): string {
  const value = typeof sentiment === 'string' ? parseFloat(sentiment) : sentiment;
  if (value > 0.1) return 'Positivo';
  if (value < -0.1) return 'Negativo';
  return 'Neutral';
}

export default NodeInfoPanel;
