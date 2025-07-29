import React from 'react';
import type { GraphNode } from '../types/graph.types';
import './NodeDetailPanel.css';

interface NodeDetailPanelProps {
  node: GraphNode | null;
  onClose: () => void;
}

const NodeDetailPanel: React.FC<NodeDetailPanelProps> = ({ node, onClose }) => {
  if (!node) {
    return null;
  }

  return (
    <div className="node-detail-panel">
      <button className="close-btn" onClick={onClose}>&times;</button>
      <h3>Detalles del Nodo</h3>
      <p><strong>ID:</strong> {node.id}</p>
      <p><strong>Etiqueta:</strong> {node.label}</p>
      {/* Aquí se pueden añadir más detalles del nodo en el futuro */}
    </div>
  );
};

export default NodeDetailPanel;
