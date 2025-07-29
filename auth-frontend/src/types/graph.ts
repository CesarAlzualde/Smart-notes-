export interface Node {
  id: string;
  label: string;
  type?: string;
  color?: string;
  x?: number;
  y?: number;
  size?: number;
  [key: string]: unknown;
}

export interface Edge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type?: string;
  color?: string;
  size?: number;
  [key: string]: unknown;
}

export interface GraphData {
  nodes: Node[];
  edges: Edge[];
}
