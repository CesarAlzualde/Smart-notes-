import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ForceGraph2D } from 'react-force-graph';
import { graphApi } from '../../../api/graph';
import type { GraphData, GraphNode } from '../types/graph.types';
import { Button, Form, Modal, Container, Row, Col, Spinner, Badge, Alert } from 'react-bootstrap';
import './ConceptMapCreator.css';

interface ConceptMapCreatorProps {
  noteIds?: number[];
  directText?: string;
  onMapCreated?: (mapId: string) => void;
}

/**
 * Componente para crear un mapa conceptual interactivo basado en notas o texto directo
 */
const ConceptMapCreator: React.FC<ConceptMapCreatorProps> = ({ noteIds = [], directText = '', onMapCreated }) => {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState<boolean>(false);
  const [mapName, setMapName] = useState<string>(`Mapa Conceptual ${new Date().toLocaleDateString()}`);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [alertMessage, setAlertMessage] = useState<{type: string; message: string} | null>(null);

  // Colores para los diferentes tipos de nodos
  const nodeColors = useMemo(() => ({
    main_topic: '#E53E3E',  // rojo
    topic: '#DD6B20',       // naranja
    entity: '#38A169',      // verde
    keyword: '#3182CE',     // azul
    note: '#805AD5',        // morado
    default: '#718096'      // gris
  }), []);

  // Función para generar el mapa conceptual
  const generateMap = useCallback(async () => {
    try {
      setLoading(true);
      const result = await graphApi.generateConceptMap(directText, noteIds.length > 0 ? noteIds : undefined);
      
      // Asignar colores a los nodos según su tipo
      const nodesWithColors = result.nodes.map(node => ({
        ...node,
        color: nodeColors[node.type as keyof typeof nodeColors] || nodeColors.default,
        size: node.type === 'main_topic' ? 12 : 
              node.type === 'topic' ? 9 : 
              node.type === 'entity' ? 8 : 6
      }));
      
      setGraphData({
        nodes: nodesWithColors,
        links: result.links
      });
      
      setLoading(false);
    } catch (error) {
      console.error('Error al generar mapa conceptual:', error);
      setAlertMessage({
        type: 'danger',
        message: 'No se pudo generar el mapa conceptual'
      });
      setLoading(false);
    }
  }, [directText, nodeColors, noteIds]);
  
  // Generar el mapa conceptual al cargar el componente si hay noteIds o directText
  useEffect(() => {
    if ((noteIds && noteIds.length > 0) || directText) {
      generateMap();
    }
  }, [noteIds, directText, generateMap]);

  // Guardar el mapa conceptual en Neo4j
  const saveMap = async () => {
    try {
      setLoading(true);
      const result = await graphApi.saveConceptMap(mapName, graphData, noteIds);
      setLoading(false);
      
      setAlertMessage({
        type: 'success',
        message: 'Mapa conceptual guardado correctamente'
      });
      
      if (onMapCreated && result.id) {
        onMapCreated(result.id);
      }
      
      setShowModal(false);
    } catch (error) {
      console.error('Error al guardar mapa conceptual:', error);
      setAlertMessage({
        type: 'danger',
        message: 'No se pudo guardar el mapa conceptual'
      });
      setLoading(false);
    }
  };

  return (
    <Container fluid className="concept-map-creator">
      {alertMessage && (
        <Alert variant={alertMessage.type} dismissible onClose={() => setAlertMessage(null)}>
          {alertMessage.message}
        </Alert>
      )}
      
      <Row className="mb-4">
        <Col>
          <h2>Mapa Conceptual</h2>
        </Col>
        <Col xs="auto">
          <Button 
            variant="primary" 
            className="me-2" 
            onClick={generateMap} 
            disabled={loading}
          >
            {loading ? (
              <>
                <Spinner as="span" animation="border" size="sm" className="me-2" />
                Generando...
              </>
            ) : "Regenerar Mapa"}
          </Button>
          <Button 
            variant="success" 
            onClick={() => setShowModal(true)}
            disabled={graphData.nodes.length === 0}
          >
            Guardar Mapa
          </Button>
        </Col>
      </Row>

      {loading ? (
        <div className="loading-container">
          <Spinner animation="border" />
          <p className="mt-3">Generando mapa conceptual...</p>
        </div>
      ) : graphData.nodes.length > 0 ? (
        <div className="concept-map-container">
          <ForceGraph2D
            graphData={graphData}
            nodeLabel={(node) => `${(node as GraphNode).label}: ${(node as GraphNode).type}`}
            nodeColor={(node) => (node as GraphNode).color || '#999'}
            nodeVal={(node) => (node as GraphNode).size || 5}
            linkLabel={(link) => link.label || 'relación'}
            linkWidth={2}
            linkDirectionalParticles={2}
            linkDirectionalParticleWidth={2}
            onNodeClick={(node) => setSelectedNode(node as GraphNode)}
            cooldownTicks={100}
            enableZoomInteraction={true}
            enablePanInteraction={true}
            width={window.innerWidth * 0.8}
            height={500}
            d3AlphaDecay={0.02}
            d3VelocityDecay={0.3}
            onEngineStop={() => {
              // Ajustar el zoom al final para asegurar que todo el grafo es visible
              setTimeout(() => {
                // Usar un timeout para dar tiempo a que el grafo se estabilice
                try {
                  if (graphData.nodes.length > 0) {
                    // Forzar un reajuste de zoom programaticamente
                    const container = document.querySelector('.concept-map-creator .force-graph-container');
                    if (container) {
                      const width = container.clientWidth;
                      const height = container.clientHeight;
                      if (width && height) {
                        // Si tenemos dimensiones, podemos calcular un zoom adecuado
                        console.log('Ajustando zoom para el mapa conceptual');
                      }
                    }
                  }
                } catch (err) {
                  console.error('Error al ajustar zoom:', err);
                }
              }, 500);
            }}
          />
        </div>
      ) : (
        <div className="empty-graph-container">
          <p className="text-muted">
            {noteIds.length > 0 || directText ? 
              'No hay suficiente información para generar un mapa conceptual. Intenta con notas más largas o más detalladas.' : 
              'Selecciona notas o proporciona texto para generar un mapa conceptual'}
          </p>
        </div>
      )}

      {selectedNode && (
        <div className="node-info-panel">
          <h4>{selectedNode.label}</h4>
          <div className="mt-2">
            <Badge 
              bg={selectedNode.type === 'main_topic' ? 'danger' :
                  selectedNode.type === 'topic' ? 'warning' :
                  selectedNode.type === 'entity' ? 'success' :
                  selectedNode.type === 'keyword' ? 'primary' :
                  selectedNode.type === 'note' ? 'info' : 'secondary'}
            >
              {selectedNode.type || 'sin tipo'}
            </Badge>
            {selectedNode.properties && typeof selectedNode.properties === 'object' && 'entity_type' in selectedNode.properties && (
              <Badge className="ms-2" bg="info">{String(selectedNode.properties.entity_type)}</Badge>
            )}
          </div>
          {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
            <div className="mt-2">
              <p className="fw-bold mb-2">Propiedades:</p>
              <div className="ps-3">
                {Object.entries(selectedNode.properties)
                  .filter(([key]) => key !== 'entity_type')
                  .map(([key, value]) => (
                    <p key={key} className="mb-1"><strong>{key}:</strong> {String(value || '')}</p>
                  ))}
              </div>
            </div>
          )}
          <Button size="sm" className="mt-3" variant="outline-secondary" onClick={() => setSelectedNode(null)}>Cerrar</Button>
        </div>
      )}

      {/* Modal para guardar el mapa */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Guardar Mapa Conceptual</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Nombre del mapa</Form.Label>
            <Form.Control 
              type="text"
              value={mapName}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMapName(e.target.value)}
              placeholder="Ingresa un nombre descriptivo"
            />
          </Form.Group>
          <div className="mt-4">
            <p className="fw-bold">Información del mapa:</p>
            <p>Conceptos: {graphData.nodes.length}</p>
            <p>Relaciones: {graphData.links.length}</p>
            {noteIds.length > 0 && (
              <p>Notas vinculadas: {noteIds.length}</p>
            )}
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cancelar
          </Button>
          <Button 
            variant="primary" 
            onClick={saveMap} 
            disabled={loading}
          >
            {loading ? (
              <>
                <Spinner as="span" animation="border" size="sm" className="me-2" />
                Guardando...
              </>
            ) : "Guardar"}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default ConceptMapCreator;
