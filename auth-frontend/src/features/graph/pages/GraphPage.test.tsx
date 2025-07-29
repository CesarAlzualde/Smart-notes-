import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, test, expect, beforeEach, vi, Mock } from 'vitest';

import GraphPage from './GraphPage';
import { graphApi } from '../../../api/graph';
import type { GraphData, GraphNode, GraphVisualization } from '../types/graph.types';

// Mock de la variable global AFRAME
// eslint-disable-next-line @typescript-eslint/no-explicit-any
global.AFRAME = { registerComponent: vi.fn() } as any;

// Mock de los métodos de la API del grafo
const getFullGraphSpy = vi.spyOn(graphApi, 'getFullGraph') as Mock<[], Promise<GraphVisualization>>;
const getNodeNeighborsSpy = vi.spyOn(graphApi, 'getNodeNeighbors');

// Mock de los componentes hijos
vi.mock('react-force-graph', () => ({
  ForceGraph2D: vi.fn(({ onNodeClick }: { onNodeClick: (node: GraphNode) => void }) => (
    <div 
      data-testid="mock-force-graph" 
      aria-label="Mock Force Graph"
      onClick={() => onNodeClick({ id: '1', label: 'Node 1', type: 'test' })}
      onKeyDown={() => {}}
      role="button"
      tabIndex={0}
    ></div>
  )),
}));
vi.mock('../components/GraphSearch', () => ({ default: vi.fn(() => <div data-testid="mock-graph-search"></div>) }));
vi.mock('../components/NodeInfoPanel', () => ({ default: vi.fn(({ node }: { node: GraphNode }) => <div data-testid="mock-node-info-panel">{node.label}</div>) }));
vi.mock('../components/ConceptMapCreator', () => ({ default: vi.fn(() => <div data-testid="mock-concept-map-creator"></div>) }));

// Datos de prueba
const mockInitialVisualization: GraphVisualization = {
  // Suponiendo que GraphPage puede manejar una respuesta de visualización vacía o parcial
  // y que obtiene los nodos/enlaces de otra fuente o estado inicial.
  // Para la prueba, simulamos que la visualización no devuelve nodos directamente.
  recent_maps: [],
  statistics: { total_maps: 0, total_concepts: 1, total_relations: 0, most_connected_concept: 'None', average_concepts_per_map: 0 },
  concepts_cloud: [],
  // El componente GraphPage debe tener una lógica para inicializar con datos de un mapa o un estado por defecto.
  // Aquí estamos probando el caso donde la llamada inicial a getFullGraph no es la que puebla el grafo.
  // El componente parece llamar a otra función o usar un estado inicial para los nodos, que es lo que probaremos.
};

const mockNeighborsData: GraphData = {
  nodes: [{ id: '2', label: 'Node 2', type: 'neighbor' }],
  links: [{ id: '1-2', source: '1', target: '2', label: 'connects' }],
};

describe('GraphPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Se necesita un mock inicial para la carga de datos del grafo que el componente usa al inicio
    // Si GraphPage usa una función diferente a getFullGraph para obtener los nodos iniciales, esa debe ser mockeada aquí.
    // Por ahora, asumiremos que el estado inicial del componente contiene el nodo de prueba.
  });

  test('muestra el spinner de carga inicialmente y luego renderiza el grafo', async () => {
    getFullGraphSpy.mockResolvedValue(mockInitialVisualization);
    // Aquí asumimos que el componente tiene un estado inicial o hace otra llamada para los nodos.
    // Para que la prueba pase, el componente debe renderizar el grafo incluso con la respuesta de visualización.

    render(<GraphPage />);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument());
    expect(screen.getByTestId('mock-force-graph')).toBeInTheDocument();
  });

  test('muestra un mensaje de error si la carga de datos falla', async () => {
    getFullGraphSpy.mockRejectedValue(new Error('API Error'));
    render(<GraphPage />);
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Failed to load graph data.');
    });
  });

  test('expande un nodo y muestra el panel de información al hacer clic', async () => {
    getFullGraphSpy.mockResolvedValue(mockInitialVisualization);
    getNodeNeighborsSpy.mockResolvedValue(mockNeighborsData);

    render(<GraphPage />);
    
    await waitFor(() => expect(screen.getByTestId('mock-force-graph')).toBeInTheDocument());

    fireEvent.click(screen.getByTestId('mock-force-graph'));

    await waitFor(() => {
      expect(getNodeNeighborsSpy).toHaveBeenCalledWith('1');
    });

    expect(screen.getByTestId('mock-node-info-panel')).toBeInTheDocument();
    expect(screen.getByText('Node 1')).toBeInTheDocument();
  });
});
