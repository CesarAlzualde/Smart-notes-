import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ForceGraph2D } from 'react-force-graph';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash, faExpandArrowsAlt, faCompress } from '@fortawesome/free-solid-svg-icons';
import type { GraphData, GraphNode } from '../types/graph.types';
import { graphApi } from '../../../api/graph';
import { notesApi } from '../../../api/notes';
import type { NoteData as Note } from '../../notes/types';
import GraphSearch from '../components/GraphSearch';
import NodeDetailPanel from '../components/NodeDetailPanel';
import { adaptApiResponseToGraphData, type ApiGraphResponse } from '../utils/graphDataAdapter';

// Tipos para los datos
interface ConceptMapSummary {
  id: string;
  name: string;
  note_id?: number;
  note_title?: string;
  created_at: string;
}

const GraphPage: React.FC = () => {
  const [maps, setMaps] = useState<ConceptMapSummary[]>([]);
  const [selectedMapId, setSelectedMapId] = useState<string | null>(null);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedNoteForGeneration, setSelectedNoteForGeneration] = useState<string>('');
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);
  const graphContainerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  
  // Configuración de colores personalizados por tipo de nodo
  const [nodeColors, setNodeColors] = useState({
    central: '#CC73B3', // Rosa/púrpura para nodo central
    category: '#607D8B', // Gris azulado para categorías
    topic: '#9C27B0',   // Púrpura para temas
    entity: '#3F51B5',  // Azul para entidades
    keyword: '#FFA726',  // Naranja para keywords
    tag: '#4CAF50',     // Verde para etiquetas
    note: '#795548'      // Marrón para notas relacionadas
  });
  
  // Estado para controlar el zoom y ajuste automático
  const [autoFit, setAutoFit] = useState(true);

  useEffect(() => {
    const fetchNotes = async () => {
      try {
        const response = await notesApi.getAllNotes();
        // Asegurarse de que response.notes es un array antes de actualizar el estado
        if (response && Array.isArray(response.notes)) {
          setNotes(response.notes);
        } else {
          setNotes([]); // Si no hay notas, establecer un array vacío
        }
      } catch (err) {
        console.error('Error al cargar las notas:', err);
        setError('No se pudieron cargar las notas.');
      }
    };

    fetchNotes();
  }, []);

  useEffect(() => {
    const fetchMaps = async () => {
      try {
        const vizData = await graphApi.getFullGraph();
        // Filtrar mapas duplicados por ID antes de actualizar el estado
        const uniqueMaps = vizData.recent_maps.filter((map: ConceptMapSummary, index: number, self: ConceptMapSummary[]) => 
          index === self.findIndex((m: ConceptMapSummary) => m.id === map.id)
        );
        setMaps(uniqueMaps);
      } catch (err: unknown) {
        console.error('Error fetching initial data:', err);
        setError('No se pudieron cargar los mapas.');
      }
    };
    fetchMaps();
  }, []);

  useEffect(() => {
    if (selectedMapId) {
      const fetchGraphData = async () => {
        setIsLoading(true);
        setError(null);
        try {
          const data = await graphApi.getConceptMap(selectedMapId);
          setGraphData(data);
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : 'Error al cargar el grafo. Puede que no contenga nodos.';
          console.error('Error fetching graph data:', err);
          setError(message);
          setGraphData({ nodes: [], links: [] });
        } finally {
          setIsLoading(false);
        }
      };
      fetchGraphData();
    }
  }, [selectedMapId]);

  useEffect(() => {
    const handleResize = () => {
      if (graphContainerRef.current) {
        // Obtener las dimensiones del contenedor padre
        const container = graphContainerRef.current;
        const containerRect = container.getBoundingClientRect();
        
        // Ajustar las dimensiones para que ocupen todo el espacio disponible
        // restando márgenes y bordes
        setDimensions({
          width: containerRect.width,
          height: window.innerHeight - containerRect.top - 20, // Restar un pequeño margen
        });
      }
    };

    handleResize(); // Set initial size
    window.addEventListener('resize', handleResize);
    
    // Reajustar el tamaño cuando cambia el mapa seleccionado
    if (selectedMapId && autoFit) {
      const timer = setTimeout(() => {
        handleResize();
        if (fgRef.current) {
          fgRef.current.zoomToFit(400, 50); // Ajustar zoom para ver todo el gráfico
        }
      }, 500);
      
      return () => {
        window.removeEventListener('resize', handleResize);
        clearTimeout(timer);
      };
    }

    return () => window.removeEventListener('resize', handleResize);
  }, [selectedMapId, autoFit]);

  const handleSelectNodeFromSearch = (node: GraphNode) => {
    if (node && node.x !== undefined && node.y !== undefined) {
      fgRef.current?.centerAt(node.x, node.y, 1000);
      fgRef.current?.zoom(2.5, 1000);
      setSelectedNode(node);
    }
  };

  const handleMapSelect = (mapId: string) => {
    setSelectedMapId(mapId);
    setSelectedNode(null);
  };

  const handleDeleteMap = async (mapId: string) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este mapa? Esta acción no se puede deshacer.')) {
      try {
        await graphApi.deleteConceptMap(mapId);
        setMaps(prevMaps => prevMaps.filter(map => map.id !== mapId));
        if (selectedMapId === mapId) {
          setSelectedMapId(null);
          setGraphData({ nodes: [], links: [] });
        }
      } catch (err) {
        console.error('Error al eliminar el mapa:', err);
        setError('No se pudo eliminar el mapa.');
      }
    }
  };

  const handleAutoGenerate = async () => {
    if (!selectedNoteForGeneration) {
      setError('Por favor, selecciona una nota para generar el mapa.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const result = await graphApi.autoGenerateFromNote(selectedNoteForGeneration);
      
      // Usar los datos del grafo directamente de la respuesta para renderizado inmediato
      if (result.concepts && result.relations) {
        const immediateGraphData = adaptApiResponseToGraphData({
          id: result.id,
          name: result.name,
          concepts: result.concepts,
          relations: result.relations
        } as ApiGraphResponse);
        
        setGraphData(immediateGraphData);
        setSelectedMapId(result.id);
        console.log('Mapa generado y renderizado inmediatamente:', {
          nodes: immediateGraphData.nodes.length,
          links: immediateGraphData.links.length,
          mode: result.generation_mode?.mode_description || 'desconocido'
        });
      }
      
      // Actualizar la lista de mapas en segundo plano
      const vizData = await graphApi.getFullGraph();
      setMaps(vizData.recent_maps);
      
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error al generar el mapa con IA.';
      console.error('Error auto-generating map:', err);
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSemanticAnalysis = async () => {
    if (!selectedNoteForGeneration) {
      setError('Por favor, selecciona una nota para el análisis semántico.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const result = await graphApi.analyzeSemanticRelationships(selectedNoteForGeneration);
      console.log('Análisis semántico completado:', result);
      alert('Análisis semántico de la nota completado con éxito.');
      // Opcionalmente, podrías querer recargar los mapas si el análisis genera uno nuevo
      // o actualiza la información de alguna manera visible.
      // fetchMaps();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error al realizar el análisis semántico.';
      console.error('Error performing semantic analysis:', err);
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node);
    if (fgRef.current && node.x !== undefined && node.y !== undefined) {
      fgRef.current.centerAt(node.x, node.y, 1000);
      fgRef.current.zoom(2.5, 1000);
    }
  }, []);

  const handleClosePanel = () => {
    setSelectedNode(null);
  };

  const nodeCanvasObject = useCallback((node: GraphNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.label || '';
    const fontSize = 12 / globalScale;
    ctx.font = `${fontSize}px Sans-Serif`;
    
    // Usar el color personalizado según el tipo de nodo, si está disponible
    const color = node.type && nodeColors[node.type as keyof typeof nodeColors] 
      ? nodeColors[node.type as keyof typeof nodeColors]
      : (node.color || 'lightblue');
    
    // Ajustar tamaño según el tipo de nodo
    let nodeSize = 5;
    if (node.type === 'central') nodeSize = 10;
    else if (node.type === 'category') nodeSize = 8;
    else if (node.size) nodeSize = node.size / 2;
    
    // Dibujar círculo del nodo
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(node.x!, node.y!, nodeSize, 0, 2 * Math.PI, false);
    ctx.fill();

    // Borde del nodo
    ctx.strokeStyle = 'rgba(0,0,0,0.5)';
    ctx.lineWidth = 1 / globalScale;
    ctx.stroke();

    // Texto con sombra para mejor legibilidad
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Sombra de texto para destacar sobre el fondo
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.fillText(label, node.x! + 0.5, node.y! + nodeSize + 0.5);
    
    // Texto principal
    ctx.fillStyle = node.type === 'central' ? '#000' : '#333';
    ctx.fillText(label, node.x!, node.y! + nodeSize);
  }, [nodeColors]);

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      <aside className="w-80 flex flex-col bg-white shadow-lg p-4 space-y-4">
        <h1 className="text-2xl font-bold text-gray-800">Mapas Conceptuales</h1>

        <div className="space-y-4">
            <div>
              <label htmlFor="note-selector" className="block text-sm font-medium text-gray-300 mb-1">Generar desde Nota</label>
              <select
                id="note-selector"
                className="w-full p-3 border border-gray-300 rounded-lg shadow-md focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 text-gray-900 bg-white font-medium"
                value={selectedNoteForGeneration}
                onChange={(e) => setSelectedNoteForGeneration(e.target.value)}
                aria-label="Seleccionar una nota para generar mapa conceptual"
              >
                <option value="" className="font-medium">-- Seleccione una nota --</option>
                {notes.map((note) => note.id ? (
                  <option key={note.id} value={note.id.toString()} className="py-2">{note.title}</option>
                ) : null)}
              </select>
            </div>
            <button
              onClick={handleAutoGenerate}
              disabled={!selectedNoteForGeneration}
              className={`w-full px-4 py-3 rounded-md flex justify-center items-center ${!selectedNoteForGeneration ? 'bg-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'} text-white font-semibold text-lg shadow-lg`}
            >
              🤖 Generar Mapa IA
            </button>
            <div className="relative w-full" title={!selectedNoteForGeneration ? 'Selecciona una nota para activar el análisis' : ''}>
              <button 
                onClick={handleSemanticAnalysis}
                disabled={!selectedNoteForGeneration}
                className={`w-full px-4 py-3 rounded-md flex justify-center items-center ${!selectedNoteForGeneration ? 'bg-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-green-500 to-teal-600 hover:from-green-600 hover:to-teal-700'} text-white font-semibold text-lg shadow-lg`}
              >
                🔍 Análisis Semántico
              </button>
            </div>
          </div>
        
        {/* Panel de configuración visual */}
        <div className="border-t border-gray-300 pt-3 mt-3">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-md font-semibold text-gray-700">Configuración Visual</h3>
            <button 
              onClick={() => setAutoFit(!autoFit)}
              className="p-2 text-gray-600 hover:text-blue-600 transition-colors"
              title={autoFit ? "Desactivar ajuste automático" : "Activar ajuste automático"}
            >
              <FontAwesomeIcon icon={autoFit ? faCompress : faExpandArrowsAlt} />
            </button>
          </div>
          
          {/* Selector de colores para tipos de nodos */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label htmlFor="color-central" className="text-sm text-gray-600">Nodo Central:</label>
              <input 
                id="color-central"
                type="color" 
                value={nodeColors.central}
                title="Color para el nodo central" 
                onChange={(e) => setNodeColors({...nodeColors, central: e.target.value})}
                className="w-10 h-6 border-none" 
              />
            </div>
            <div className="flex justify-between items-center">
              <label htmlFor="color-category" className="text-sm text-gray-600">Categorías:</label>
              <input 
                id="color-category"
                type="color" 
                value={nodeColors.category}
                title="Color para nodos de categorías" 
                onChange={(e) => setNodeColors({...nodeColors, category: e.target.value})}
                className="w-10 h-6 border-none" 
              />
            </div>
            <div className="flex justify-between items-center">
              <label htmlFor="color-topic" className="text-sm text-gray-600">Temas:</label>
              <input 
                id="color-topic"
                type="color" 
                value={nodeColors.topic} 
                title="Color para nodos de temas"
                onChange={(e) => setNodeColors({...nodeColors, topic: e.target.value})}
                className="w-10 h-6 border-none" 
              />
            </div>
            <div className="flex justify-between items-center">
              <label htmlFor="color-entity" className="text-sm text-gray-600">Entidades:</label>
              <input 
                id="color-entity"
                type="color" 
                value={nodeColors.entity} 
                title="Color para nodos de entidades"
                onChange={(e) => setNodeColors({...nodeColors, entity: e.target.value})}
                className="w-10 h-6 border-none" 
              />
            </div>
            <div className="flex justify-between items-center">
              <label htmlFor="color-keyword" className="text-sm text-gray-600">Palabras Clave:</label>
              <input 
                id="color-keyword"
                type="color" 
                value={nodeColors.keyword}
                title="Color para nodos de palabras clave" 
                onChange={(e) => setNodeColors({...nodeColors, keyword: e.target.value})}
                className="w-10 h-6 border-none" 
              />
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto pr-2 border-t border-gray-300 pt-3 mt-3">
          <h2 className="text-xl font-bold text-gray-900 mb-4 border-b border-gray-300 pb-2">Mis Mapas</h2>
          <div className="h-full">
            {maps.length > 0 ? (
              <ul className="space-y-2">
                {maps.map(map => (
                  <li key={map.id} className="flex items-center justify-between bg-[#1a2b45] p-3 rounded-lg shadow-sm hover:shadow-md hover:brightness-110 transition-all duration-200">
                    <button
                      onClick={() => handleMapSelect(map.id)}
                      className={`flex-grow text-left transition-colors duration-200 ${selectedMapId === map.id ? 'text-white font-bold' : 'text-gray-100'}`}
                    >
                      <span className="text-lg font-medium">{map.name}</span>
                      {map.note_title && (
                        <div className="text-sm text-gray-300 mt-1">
                          Basado en: {map.note_title}
                        </div>
                      )}
                    </button>
                    <button
                      onClick={() => handleDeleteMap(map.id)}
                      className="ml-4 text-red-400 hover:text-red-300 hover:scale-110 transition-all duration-200"
                      title="Eliminar mapa"
                    >
                      <FontAwesomeIcon icon={faTrash} />
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-100 italic bg-[#1a2b45] p-4 rounded-lg shadow-sm text-center">No hay mapas disponibles.</p>
            )}
          </div>
        </div>
      </aside>

      <main ref={graphContainerRef} className="flex-1 flex flex-col relative bg-dots">
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-white bg-black bg-opacity-70">
            <p className="text-2xl font-semibold animate-pulse px-6 py-4 bg-gray-800 rounded-lg shadow-lg">Cargando y renderizando mapa...</p>
          </div>
        ) : graphData.nodes.length > 0 ? (
          <>
            <div className="absolute top-4 left-4 z-10 w-64 shadow-lg">
              <GraphSearch onSelectNode={handleSelectNodeFromSearch} />
            </div>
            <ForceGraph2D
              ref={fgRef}
              width={dimensions.width}
              height={dimensions.height}
              graphData={graphData}
              nodeLabel="label"
              nodeColor={node => {
                // Usar color personalizado según tipo o el predeterminado del nodo
                const nodeType = node.type as keyof typeof nodeColors;
                return nodeType && nodeColors[nodeType] ? nodeColors[nodeType] : (node.color || '#808080');
              }}
              nodeCanvasObject={nodeCanvasObject}
              onNodeClick={handleNodeClick as (node: object) => void}
              linkDirectionalArrowLength={3.5}
              linkDirectionalArrowRelPos={1}
              linkColor={(link) => link.color || '#999'}
              linkWidth={(link) => link.width || 1}
              cooldownTicks={100}
              onEngineStop={() => autoFit ? fgRef.current?.zoomToFit(400) : null}
              d3VelocityDecay={0.3}
              d3AlphaDecay={0.02}
              backgroundColor="rgba(255,255,255,0.9)"
            />
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center p-8 bg-white rounded-xl shadow-2xl border border-gray-200">
              <h2 className="text-3xl font-bold text-gray-900 mb-3">Bienvenido al Visualizador de Grafos</h2>
              <p className="text-lg text-gray-700 mt-2">Selecciona un mapa de la lista o genera uno nuevo usando IA.</p>
            </div>
          </div>
        )}
        {error && (
          <div className="absolute bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-xl z-20">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}
      </main>

      {selectedNode && (
        <NodeDetailPanel 
          node={selectedNode} 
          onClose={handleClosePanel} 
        />
      )}
    </div>
  );
};

export default GraphPage;
