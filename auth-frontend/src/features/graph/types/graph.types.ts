// Definiciones de tipos compartidos para los componentes del grafo

export interface GraphNode {
  id: string | number;
  label: string;
  type?: string;
  properties?: Record<string, unknown>;
  // Props para la visualización
  color?: string;
  size?: number;
  isPlaceholder?: boolean;
  expanded?: boolean;
  // Props generadas por react-force-graph durante el renderizado
  x?: number;
  y?: number;
  // Props para control de estado de expansión
  _expanding?: boolean;
}

export interface GraphEdge {
  speed?: number;
  id: string | number;
  // source y target pueden ser IDs (string|number) o referencias a objetos GraphNode
  source: string | number | GraphNode;
  target: string | number | GraphNode;
  label: string;
  properties?: Record<string, unknown>;
  // Props de visualización
  color?: string;
  width?: number;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphEdge[]; // React-force-graph usa 'links' en vez de 'edges'
}
