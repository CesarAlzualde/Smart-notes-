/**
 * Adaptador para transformar los datos de la API al formato esperado por react-force-graph
 */

import type { GraphData, GraphNode, GraphEdge } from '../types/graph.types';

export interface ApiGraphResponse {
  id?: string;
  name?: string;
  concepts: Array<{
    id: string;
    label: string;
    type: string;
    map_id?: string;
    weight?: number;
    [key: string]: string | number | boolean | null | undefined;
  }>;
  relations: Array<{
    source: string;
    target: string;
    label: string;
    weight?: number;
    map_id?: string;
    [key: string]: string | number | boolean | null | undefined;
  }>;
  created_at?: string;
  user_id?: number;
  concept_count?: number;
  relation_count?: number;
  note_ids?: number[];
  [key: string]: unknown;
}

/**
 * Convierte la respuesta de la API de conceptos y relaciones a nodos y enlaces
 * que puede entender react-force-graph
 */
export function adaptApiResponseToGraphData(apiResponse: ApiGraphResponse): GraphData {
  // Si la respuesta es inválida o no contiene los datos esperados, devuelve un grafo vacío
  if (!apiResponse || !Array.isArray(apiResponse.concepts) || !Array.isArray(apiResponse.relations)) {
    console.warn('Respuesta de API inválida o mapa no encontrado, se devolverá un grafo vacío:', apiResponse);
    return { nodes: [], links: [] };
  }

  // Depuración para ver qué IDs están llegando
  console.debug('IDs originales recibidos:', apiResponse.concepts.map(c => c.id));
  
  // Transformar conceptos a nodos con colores y tamaños adecuados
  // Crear un Set para rastrear IDs únicos y evitar duplicados
  const uniqueIds = new Set<string>();
  const idMap = new Map<string, string>();
  
  // Pre-procesamiento: verificar si hay IDs duplicados antes de la transformación
  const idCounts = new Map<string, number>();
  apiResponse.concepts.forEach(concept => {
    const count = idCounts.get(concept.id) || 0;
    idCounts.set(concept.id, count + 1);
  });
  
  // Identificar duplicados para log de depuración
  const duplicates = Array.from(idCounts.entries())
    .filter(([, count]) => count > 1)
    .map(([id]) => id);
  
  if (duplicates.length > 0) {
    console.warn('Se detectaron IDs duplicados en la respuesta API:', duplicates);
  }
  
  const nodes = apiResponse.concepts.map((concept, index) => {
    // Asegurarse de que el ID sea único y válido
    let nodeId = concept.id;
    const isDuplicate = (idCounts.get(nodeId) ?? 0) > 1;
    const containsAuto = typeof nodeId === 'string' && 
                        (nodeId.includes('_auto') || nodeId.includes('auto'));
    
    // Generar un nuevo ID si: 
    // 1. Ya existe en nuestro Set de IDs únicos
    // 2. Es un ID duplicado según nuestro pre-procesamiento
    // 3. Contiene la palabra 'auto' en cualquier formato
    // 4. No es una string válida
    if (uniqueIds.has(nodeId) || isDuplicate || containsAuto || typeof nodeId !== 'string') {
      // Generamos un ID completamente nuevo y único
      // Formato: tipo_etiqueta-abreviada_timestamp_índice
      const timestamp = Date.now();
      const randomPart = Math.floor(Math.random() * 10000);
      nodeId = `${concept.type || 'node'}-${concept.label?.substring(0,5).replace(/\s+/g, '') || 'item'}-${timestamp}-${index}-${randomPart}`;
      
      console.debug(`ID reemplazado: ${concept.id} -> ${nodeId}`);
    }
    
    // Registrar el ID como utilizado
    uniqueIds.add(nodeId);
    
    // Mantener el mapeo para actualizar edges
    if (concept.id && concept.id !== nodeId) {
      idMap.set(concept.id, nodeId);
    }
    
    const node: GraphNode = {
      id: nodeId,
      label: concept?.label ?? 'Unlabeled',
      type: concept?.type ?? 'unknown',
      color: getNodeColorByType(concept?.type ?? 'unknown'),
      size: getNodeSizeByWeight(concept?.weight ?? 1),
      properties: {}
    };
    return node;
  });

  // Log para confirmar que no hay IDs duplicados después de la transformación
  const finalIds = nodes.map(n => n.id);
  const finalIdsSet = new Set(finalIds);
  if (finalIds.length !== finalIdsSet.size) {
    console.error('ALERTA: Aún hay IDs duplicados después de la transformación!', 
      finalIds.filter((id, i) => finalIds.indexOf(id) !== i));
  } else {
    console.debug('Verificación de IDs únicos exitosa: Todos los IDs son únicos');
  }
  
  // Transformar relaciones a enlaces asegurando que usen los IDs correctos
  const links = apiResponse.relations.map((relation, index) => {
    // Generar ID único para la relación
    const timestamp = Date.now() + index;
    const uniqueId = `edge-${timestamp}-${Math.floor(Math.random() * 1000)}`;
    
    // Usar IDs únicos para source y target, asegurándose que existen en el mapa
    // Si el nodo original fue reemplazado, usar el nuevo ID
    let sourceId = relation.source;
    let targetId = relation.target;
    
    // Verificar si necesitamos reemplazar sourceId
    if (idMap.has(sourceId)) {
      sourceId = idMap.get(sourceId)!;
    }
    
    // Verificar si necesitamos reemplazar targetId
    if (idMap.has(targetId)) {
      targetId = idMap.get(targetId)!;
    }
    
    // Verificación adicional: asegurarse de que source y target existan como nodos
    const sourceExists = nodes.some(n => n.id === sourceId);
    const targetExists = nodes.some(n => n.id === targetId);
    
    if (!sourceExists || !targetExists) {
      console.warn(`Edge con nodos inexistentes: ${sourceId} -> ${targetId}. Nodo source existe: ${sourceExists}, Nodo target existe: ${targetExists}`);
    }
      
    const edge: GraphEdge = {
      id: uniqueId,
      source: sourceId,
      target: targetId,
      label: relation.label ?? 'Unlabeled',
      width: relation.weight ?? 1,
      properties: {}
    };
    return edge;
  });

  return {
    nodes,
    links
  };
}

/**
 * Determina el color del nodo según su tipo
 */
function getNodeColorByType(type: string): string {
  switch (type) {
    case 'main':
      return '#E53E3E'; // Rojo
    case 'secondary':
      return '#DD6B20'; // Naranja
    case 'example':
      return '#38A169'; // Verde
    case 'conclusion':
      return '#3182CE'; // Azul
    default:
      return '#718096'; // Gris
  }
}

/**
 * Calcula el tamaño del nodo según su peso
 */
function getNodeSizeByWeight(weight: number): number {
  // Tamaño base de 6, con factor de multiplicación según peso
  return 6 + (weight * 3);
}
