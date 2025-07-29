"""
Enhanced Concept Map Service para generación automática de mapas mentales interactivos
Integra con el análisis de IA existente para crear mapas semánticos automáticamente
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import re
import math
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.note import Note
from ..models.tag import Tag
from ..models.topic import Topic
from ..services.text_summarizer import TextSummarizer
from ..database import get_session
# Importación movida dentro de los métodos para evitar importaciones circulares

logger = logging.getLogger(__name__)

@dataclass
class ConceptNode:
    """Representa un nodo en el mapa conceptual"""
    id: str
    label: str
    type: str  # 'central', 'topic', 'entity', 'tag'
    properties: Dict[str, Any]
    color: Optional[str] = None
    size: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None

@dataclass
class ConceptEdge:
    """Representa una conexión en el mapa conceptual"""
    id: str
    source: str
    target: str
    label: str
    type: str  # 'contains', 'relates_to', 'mentions', 'tagged_as'
    properties: Dict[str, Any]
    color: Optional[str] = None
    width: Optional[int] = None

@dataclass
class ConceptMap:
    """Representa un mapa conceptual completo"""
    id: str
    name: str
    nodes: List[ConceptNode]
    edges: List[ConceptEdge]
    metadata: Dict[str, Any]

class EnhancedConceptMapService:
    """Servicio mejorado para generación automática de mapas conceptuales"""
    
    def __init__(self):
        # Carga perezosa: No inicializar TextSummarizer hasta que sea necesario
        self._text_summarizer = None
        
        # Configuración de colores por tipo de nodo
        self.node_colors = {
            'central': '#FF6B6B',      # Rojo para nodo central
            'topic': '#4ECDC4',        # Turquesa para temas
            'entity': '#45B7D1',       # Azul para entidades
            'tag': '#96CEB4',          # Verde para etiquetas
            'related_note': '#FFEAA7'  # Amarillo para notas relacionadas
        }
        
        # Configuración de tamaños por tipo
        self.node_sizes = {
            'central': 20,
            'topic': 15,
            'entity': 12,
            'tag': 10,
            'related_note': 13
        }
        # Neo4j driver inicializado bajo demanda para evitar importaciones circulares
    
    @property
    def text_summarizer(self):
        """Carga perezosa de TextSummarizer para evitar saturación de memoria"""
        if self._text_summarizer is None:
            logger.info("Inicializando TextSummarizer bajo demanda...")
            self._text_summarizer = TextSummarizer()
        return self._text_summarizer

    def generate_and_save_map(self, note_id: int, user_id: int, use_ai_analysis: bool = False) -> Optional[str]:
        """
        Genera un mapa conceptual jerárquico a partir de una nota
        usando los datos de análisis de IA existentes en analysis_cache
        """
        with get_session() as session:
            try:
                # 1. Recuperar la nota por su ID
                note = session.query(Note).filter(Note.id == note_id).first()
                if not note:
                    logger.error(f"No se encontró nota con ID {note_id}")
                    return None
                
                logger.info(f"Generando mapa conceptual para nota: {note.title}")
                
                # 2. Crear nodo central
                central_node = self._create_central_node(note)
                
                # 3. Crear nodos de categorías para organizar la estructura
                category_nodes = self._create_category_nodes(note)
                
                # 4. Crear nodos según el modo de análisis
                if use_ai_analysis:
                    logger.info("Modo IA: Creando nodos con análisis completo")
                    # Crear nodos de temas principales
                    topic_nodes = self._create_topic_nodes(note)
                    # Crear nodos de entidades usando datos persistentes o análisis
                    entity_nodes = self._create_entity_nodes_with_ai(note) 
                    # Crear nodos de keywords usando análisis avanzado
                    keyword_nodes = self._create_keyword_nodes_with_ai(note)
                else:
                    logger.info("Modo básico: Creando nodos sin análisis IA pesado")
                    # Usar solo datos básicos disponibles
                    topic_nodes = self._create_basic_topic_nodes(note)
                    entity_nodes = self._create_basic_entity_nodes(note)
                    keyword_nodes = self._create_basic_keyword_nodes(note)
                
                # 5. Crear nodos para etiquetas asociadas (siempre disponible)
                tag_nodes = self._create_tag_nodes(note, session)
                
                # 6. Buscar notas relacionadas y crear conexiones (siempre disponible)
                related_note_nodes, related_note_edges = self._create_related_notes_nodes(note, session)
                
                # 9. Crear estructura jerárquica de relaciones
                edges = []
                
                # Agregar los edges de las notas relacionadas
                edges.extend(related_note_edges)
                
                # Conectar nodo central con categorías con tipo HAS_CATEGORY
                for category_node in category_nodes:
                    edges.append(ConceptEdge(
                        id=f"{central_node.id}_{category_node.id}",
                        source=central_node.id,
                        target=category_node.id,
                        label="Contiene",
                        type="HAS_CATEGORY",
                        properties={"primary": True},
                        color="#666666",
                        width=2
                    ))
                
                # Conectar categoría 'Temas' con nodos de temas
                if topic_nodes and len(category_nodes) >= 1:
                    for i, topic_node in enumerate(topic_nodes):
                        edges.append(ConceptEdge(
                            id=f"{category_nodes[0].id}_{topic_node.id}",
                            source=category_nodes[0].id,  # Categoría 'Temas'
                            target=topic_node.id,
                            label="Contiene",
                            type="CONTAINS",
                            properties={"order": i},
                            color="#9C27B0", # Color que coincida con la categoría
                            width=1
                        ))
                
                # Conectar categoría 'Entidades' con nodos de entidades
                if entity_nodes and len(category_nodes) >= 2:
                    for i, entity_node in enumerate(entity_nodes):
                        edges.append(ConceptEdge(
                            id=f"{category_nodes[1].id}_{entity_node.id}",
                            source=category_nodes[1].id,  # Categoría 'Entidades'
                            target=entity_node.id,
                            label="Contiene",
                            type="CONTAINS",
                            properties={"entity_type": entity_node.properties.get("entity_type", "OTH")},
                            color="#3F51B5", # Color que coincida con la categoría
                            width=1
                        ))
                
                # Conectar categoría 'Palabras clave' con nodos de palabras clave
                if keyword_nodes and len(category_nodes) >= 3:
                    for i, keyword_node in enumerate(keyword_nodes):
                        edges.append(ConceptEdge(
                            id=f"{category_nodes[2].id}_{keyword_node.id}",
                            source=category_nodes[2].id,  # Categoría 'Palabras clave'
                            target=keyword_node.id,
                            label="Contiene",
                            type="CONTAINS",
                            properties={"importance": len(keyword_nodes) - i},
                            color="#FFA726", # Color que coincida con la categoría
                            width=1
                        ))
                
                # Conectar categoría 'Etiquetas' con nodos de etiquetas
                if tag_nodes and len(category_nodes) >= 4:
                    for i, tag_node in enumerate(tag_nodes):
                        edges.append(ConceptEdge(
                            id=f"{category_nodes[3].id}_{tag_node.id}",
                            source=category_nodes[3].id,  # Categoría 'Etiquetas'
                            target=tag_node.id,
                            label="Contiene",
                            type="CONTAINS",
                            properties={"order": i},
                            color="#4CAF50", # Color que coincida con la categoría
                            width=1
                        ))
                
                # Crear conexiones semánticas entre nodos relacionados
                
                # 1. Relaciones entre temas y keywords
                for topic_node in topic_nodes:
                    for keyword_node in keyword_nodes:
                        if self._are_semantically_related(topic_node.label, keyword_node.label):
                            edges.append(ConceptEdge(
                                id=f"rel_{topic_node.id}_{keyword_node.id}",
                                source=topic_node.id,
                                target=keyword_node.id,
                                label="Relacionado",
                                type="RELATED_TO",
                                properties={"strength": 0.8},
                                color="#E91E63",  # Color para relaciones semánticas
                                width=1
                            ))
                
                # 2. Relaciones entre entidades y keywords
                for entity_node in entity_nodes:
                    for keyword_node in keyword_nodes:
                        if self._are_semantically_related(entity_node.label, keyword_node.label):
                            edges.append(ConceptEdge(
                                id=f"rel_{entity_node.id}_{keyword_node.id}",
                                source=entity_node.id,
                                target=keyword_node.id,
                                label="Relacionado",
                                type="RELATED_TO",
                                properties={"strength": 0.7},
                                color="#E91E63",  # Color para relaciones semánticas
                                width=1
                            ))
                
                # 3. Relaciones entre entidades y temas
                for entity_node in entity_nodes:
                    for topic_node in topic_nodes:
                        if self._are_semantically_related(entity_node.label, topic_node.label):
                            edges.append(ConceptEdge(
                                id=f"rel_{entity_node.id}_{topic_node.id}",
                                source=entity_node.id,
                                target=topic_node.id,
                                label="Relacionado",
                                type="RELATED_TO",
                                properties={"strength": 0.75},
                                color="#E91E63",  # Color para relaciones semánticas
                                width=1
                            ))
                
                # Conectar notas relacionadas a su categoría
                if related_note_nodes and len(category_nodes) >= 5:
                    for i, related_note_node in enumerate(related_note_nodes):
                        edges.append(ConceptEdge(
                            id=f"{category_nodes[4].id}_{related_note_node.id}",
                            source=category_nodes[4].id,  # Categoría 'Notas Relacionadas'
                            target=related_note_node.id,
                            label="Relacionado",
                            type="RELATED_TO",
                            properties={"order": i},
                            color="#607D8B", # Color que coincida con la categoría
                            width=1
                        ))
                
                # Aplicar posicionamiento jerárquico para visualización
                all_nodes = [central_node] + category_nodes + topic_nodes + entity_nodes + tag_nodes + keyword_nodes + related_note_nodes
                
                # Aplicar coordenadas para visualización jerárquica
                self._apply_hierarchical_layout(all_nodes, edges)
                
                # Crear objeto ConceptMap
                concept_map = ConceptMap(
                    id=f"note_{note_id}_auto",
                    name=f"Mapa conceptual: {note.title}",
                    nodes=all_nodes,
                    edges=edges,
                    metadata={
                        "description": f"Mapa conceptual jerárquico para la nota: {note.title}",
                        "user_id": str(note.user_id),
                        "source_id": str(note_id),
                        "source_type": "note",
                        "created_at": datetime.now().isoformat(),
                        "layout": "hierarchical"
                    }
                )
                
                # Guardar en Neo4j
                save_success = self.save_concept_map(
                    map_id=concept_map.id,
                    map_name=concept_map.name,
                    note_id=note.id,
                    user_id=user_id,
                    concepts=all_nodes,
                    relations=edges,
                    metadata=concept_map.metadata
                )
                if save_success:
                    logger.info(f"Mapa conceptual generado exitosamente con ID {concept_map.id}")
                    return concept_map.id
                
                logger.error("No se pudo guardar el mapa conceptual en Neo4j")
                return None
                
            except Exception as e:
                logger.error(f"Error al generar mapa conceptual: {str(e)}")
                return None

    def _create_central_node(self, note: Note) -> ConceptNode:
        """Crea un nodo central para el mapa conceptual basado en la nota"""
        return ConceptNode(
            id=f"central_{note.id}",
            label=note.title,
            type="central",
            properties={
                "note_id": str(note.id),
                "created_at": note.created_at.isoformat() if note.created_at else None
            },
            color="#CC73B3"  # Rosa/púrpura para nodo central como en la imagen de referencia
        )

    def _create_category_nodes(self, note: Note) -> List[ConceptNode]:
        """Crea nodos de categoría para organizar la estructura del mapa"""
        categories = [
            {"id": "temas", "label": "Temas", "color": "#9C27B0"},  # Púrpura
            {"id": "entidades", "label": "Entidades", "color": "#3F51B5"},  # Azul
            {"id": "keywords", "label": "Palabras clave", "color": "#FFA726"},  # Naranja
            {"id": "etiquetas", "label": "Etiquetas", "color": "#4CAF50"},  # Verde
            {"id": "notas_relacionadas", "label": "Notas Relacionadas", "color": "#607D8B"}  # Gris azulado
        ]
        
        category_nodes = []
        for cat in categories:
            category_nodes.append(ConceptNode(
                id=f"category_{cat['id']}_{note.id}",
                label=cat['label'],
                type="category",
                properties={"category_type": cat['id']},
                color=cat['color']
            ))
            
        return category_nodes
        
    def _create_tag_nodes(self, note: Note, session: Session) -> List[ConceptNode]:
        """Crea nodos para las etiquetas asociadas a la nota"""
        nodes = []
        
        if note.tags:
            for tag in note.tags:
                tag_node = ConceptNode(
                    id=f"tag_{tag.id}",
                    label=tag.name,
                    type="tag",
                    properties={
                        "tag_id": str(tag.id),
                        "tag_name": tag.name,
                        "created_at": tag.created_at.isoformat() if hasattr(tag, 'created_at') and tag.created_at else None
                    },
                    color=self.node_colors['tag'],
                    size=self.node_sizes['tag']
                )
                nodes.append(tag_node)
        
        logger.info(f"Creados {len(nodes)} nodos de etiquetas para nota {note.id}")
        return nodes
        
    def _are_semantically_related(self, text1: str, text2: str) -> bool:
        """Determina si dos textos están semánticamente relacionados
        Implementación simple basada en coincidencia de palabras"""
        # Simplificación: si una palabra aparece en ambos textos, los consideramos relacionados
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Si hay al menos una palabra en común (excepto palabras muy comunes)
        common_words = words1.intersection(words2)
        stopwords = {'de', 'la', 'el', 'en', 'y', 'a', 'que', 'los', 'del', 'las', 'un', 'por', 'con', 'una', 'su'}
        relevant_common_words = common_words - stopwords
        
        return len(relevant_common_words) > 0 or len(common_words) >= 2
        
    def _create_topic_nodes(self, note: Note) -> List[ConceptNode]:
        """Crea nodos para los temas principales de la nota"""
        nodes = []
        
        # Tema principal
        if note.main_topic:
            main_topic_node = ConceptNode(
                id=f"main_topic_{note.id}",
                label=note.main_topic,
                type="topic",
                properties={
                    'topic_type': 'main',
                    'confidence': 1.0
                },
                color=self.node_colors['topic'],
                size=self.node_sizes['topic']
            )
            nodes.append(main_topic_node)
        
        # Temas secundarios
        if note.topics:
            for i, topic in enumerate(note.topics):
                topic_node = ConceptNode(
                    id=f"topic_{note.id}_{i}",
                    label=topic.name,
                    type="topic",
                    properties={
                        'topic_type': 'secondary',
                        'confidence': 0.8
                    },
                    color=self.node_colors['topic'],
                    size=self.node_sizes['topic'] - 2
                )
                nodes.append(topic_node)
        
        return nodes

    def _create_entity_nodes(self, note: Note) -> List[ConceptNode]:
        """Crea nodos para las entidades importantes usando analysis_cache"""
        nodes = []
        
        # Primero intentar usar datos desde analysis_cache (nuevo sistema)
        if hasattr(note, 'analysis_cache') and note.analysis_cache:
            try:
                analysis_data = note.analysis_cache
                entities = analysis_data.get('entities', {})
                
                logger.info(f"Usando entidades desde analysis_cache para nota {note.id}: {entities}")
                
                # Crear nodos para cada tipo de entidad
                entity_counter = 0
                for entity_type, entity_list in entities.items():
                    if not entity_list or entity_counter >= 15:  # Límite total de entidades
                        continue
                        
                    # Colores específicos por tipo de entidad
                    entity_colors = {
                        'PER': '#FF6B6B',  # Rojo para personas
                        'ORG': '#4ECDC4',  # Turquesa para organizaciones  
                        'LOC': '#45B7D1',  # Azul para ubicaciones
                        'OTH': '#96CEB4'   # Verde para otros
                    }
                    
                    for entity_name in entity_list[:5]:  # Máximo 5 por tipo
                        if entity_counter >= 15:
                            break
                            
                        entity_node = ConceptNode(
                            id=f"entity_{note.id}_{entity_type}_{entity_counter}",
                            label=str(entity_name),
                            type="entity",
                            properties={
                                'entity_type': entity_type,
                                'source': 'analysis_cache'
                            },
                            color=entity_colors.get(entity_type, self.node_colors['entity']),
                            size=self.node_sizes.get('entity', 20)
                        )
                        nodes.append(entity_node)
                        entity_counter += 1
                        
            except Exception as e:
                logger.warning(f"Error al parsear entidades desde analysis_cache para nota {note.id}: {e}")
        
        # Sistema de respaldo: usar el campo entities antiguo
        elif hasattr(note, 'entities') and note.entities:
            try:
                if isinstance(note.entities, str):
                    entities = json.loads(note.entities)
                else:
                    entities = note.entities
                
                for i, entity in enumerate(entities[:10]):  # Limitar a 10 entidades
                    entity_node = ConceptNode(
                        id=f"entity_{note.id}_{i}",
                        label=entity.get('text', f'Entity {i}'),
                        type="entity",
                        properties={
                            'entity_type': entity.get('label', 'UNKNOWN'),
                            'confidence': entity.get('confidence', 0.5),
                            'start_pos': entity.get('start', 0),
                            'end_pos': entity.get('end', 0),
                            'source': 'legacy_entities'
                        },
                        color=self.node_colors['entity'],
                        size=self.node_sizes['entity']
                    )
                    nodes.append(entity_node)
                    
            except (json.JSONDecodeError, AttributeError):
                logger.warning(f"Could not parse legacy entities for note {note.id}")
        
        logger.info(f"Creados {len(nodes)} nodos de entidades para nota {note.id}")
        return nodes

    def _create_keyword_nodes(self, note: Note) -> List[ConceptNode]:
        """Crea nodos para las palabras clave importantes usando analysis_cache"""
        nodes = []
        
        # Usar keywords desde analysis_cache (nuevo sistema)
        if hasattr(note, 'analysis_cache') and note.analysis_cache:
            try:
                analysis_data = note.analysis_cache
                keywords = analysis_data.get('keywords', [])
                
                logger.info(f"Usando keywords desde analysis_cache para nota {note.id}: {keywords[:10]}...")
                
                # Crear nodos para las keywords más importantes (máximo 12)
                for i, keyword in enumerate(keywords[:12]):
                    if not keyword or len(str(keyword).strip()) < 2:
                        continue
                        
                    keyword_node = ConceptNode(
                        id=f"keyword_{note.id}_{i}",
                        label=str(keyword).capitalize(),
                        type="keyword",
                        properties={
                            'keyword': str(keyword),
                            'source': 'analysis_cache',
                            'importance': len(keywords) - i  # Mayor índice = mayor importancia
                        },
                        color='#FFA726',  # Naranja para keywords
                        size=self.node_sizes.get('topic', 15)
                    )
                    nodes.append(keyword_node)
                        
            except Exception as e:
                logger.warning(f"Error al procesar keywords para nota {note.id}: {str(e)}")
        
        logger.info(f"Creados {len(nodes)} nodos de keywords para nota {note.id}")
        return nodes

    def _create_related_notes_nodes(self, note: Note, session: Session) -> Tuple[List[ConceptNode], List[ConceptEdge]]:
        """Crea nodos para notas semánticamente relacionadas"""
        nodes = []
        edges = []
        
        try:
            # Buscar notas relacionadas por tags similares
            related_notes = self._find_related_notes(session, note)
            
            # ID consistente para el nodo central
            central_node_id = f"central_{note.id}"
            
            for related_note in related_notes[:5]:  # Limitar a 5 notas relacionadas
                related_node = ConceptNode(
                    id=f"related_note_{related_note.id}",
                    label=related_note.title,
                    type="related_note",
                    properties={
                        'note_id': related_note.id,
                        'similarity_score': 0.7  # Placeholder
                    },
                    color=self.node_colors['related_note'],
                    size=self.node_sizes['related_note']
                )
                nodes.append(related_node)
                
                # Crear conexión (usando el ID correcto del nodo central)
                edge = ConceptEdge(
                    id=f"central_{note.id}_to_{related_note.id}",
                    source=central_node_id,  # ID correcto del nodo central
                    target=related_node.id,
                    label="relates_to",
                    type="relates_to",
                    properties={'similarity': 0.7},
                    color='#F39C12',
                    width=2
                )
                edges.append(edge)
        
        except Exception as e:
            logger.warning(f"Could not create related notes: {str(e)}")
        
        return nodes, edges

    def _find_related_notes(self, session: Session, note: Note) -> List[Note]:
        """Encuentra notas relacionadas por tags y temas similares"""
        related_notes = []
        
        if note.tags:
            # Buscar notas con tags similares
            tag_ids = [tag.id for tag in note.tags]
            related_by_tags = session.query(Note).join(Note.tags).filter(
                Tag.id.in_(tag_ids),
                Note.id != note.id
            ).limit(3).all()
            related_notes.extend(related_by_tags)
        
        return related_notes
        
    # Esta función ha sido eliminada porque duplicaba la funcionalidad de _create_related_notes_nodes
    # y causaba problemas de IDs duplicados en el mapa conceptual

    def _apply_automatic_layout(self, nodes: List[ConceptNode], edges: List[ConceptEdge]):
        """Aplica un layout automático a los nodos"""
        # Centro del grafo
        center_x, center_y = 0, 0
        
        # Aplicar layout circular simple por ahora
        if nodes:
            # Asignar posición central al primer nodo (nodo central)
            if len(nodes) > 0:
                nodes[0].x = center_x
                nodes[0].y = center_y
            
            # Organizar el resto de nodos en círculo alrededor
            if len(nodes) > 1:
                radius = 300  # Radio del círculo
                self._arrange_in_circle(nodes[1:], radius)
                
        logger.info("Layout automático aplicado a los nodos del grafo")
        return nodes
        
    def _apply_hierarchical_layout(self, nodes: List[ConceptNode], edges: List[ConceptEdge]):
        """Aplica un layout jerárquico tipo árbol para mejor visualización"""
        if not nodes:
            return nodes
            
        # 1. Identificar nodos por tipo
        central_node = None
        category_nodes = []
        child_nodes = []
        
        for node in nodes:
            if node.type == "central":
                central_node = node
            elif node.type == "category":
                category_nodes.append(node)
            else:
                child_nodes.append(node)
        
        if not central_node or not category_nodes:
            logger.warning("No se encontró nodo central o categorías para aplicar layout jerárquico")
            return self._apply_automatic_layout(nodes, edges)  # Fallback al layout automático
        
        # 2. Posicionar nodo central en el medio
        central_node.x = 0
        central_node.y = 0
        
        # 3. Posicionar categorías alrededor del nodo central
        category_count = len(category_nodes)
        if category_count > 0:
            radius = 200  # Distancia desde el centro
            for i, category in enumerate(category_nodes):
                angle = (2 * math.pi / category_count) * i
                category.x = radius * math.cos(angle)
                category.y = radius * math.sin(angle)
        
        # 4. Identificar nodos hijos por categoría usando las relaciones
        category_children = {cat.id: [] for cat in category_nodes}
        
        for edge in edges:
            # Si el origen es una categoría y el destino no es el nodo central ni otra categoría
            if any(edge.source == cat.id for cat in category_nodes):
                # Encontrar nodo destino
                for node in child_nodes:
                    if node.id == edge.target:
                        # Añadir a la lista de hijos de esta categoría
                        category_children[edge.source].append(node)
                        break
        
        # 5. Posicionar nodos hijos alrededor de sus categorías
        for i, category in enumerate(category_nodes):
            children = category_children[category.id]
            child_count = len(children)
            
            if child_count > 0:
                child_radius = 150  # Radio para los hijos alrededor de la categoría
                start_angle = (2 * math.pi / category_count) * i - (math.pi / category_count)
                end_angle = (2 * math.pi / category_count) * (i + 1) - (math.pi / category_count)
                
                for j, child in enumerate(children):
                    # Distribuir uniformemente en el sector angular asignado a esta categoría
                    if child_count == 1:
                        angle = (start_angle + end_angle) / 2
                    else:
                        angle = start_angle + (end_angle - start_angle) * (j / (child_count - 1))
                    
                    # Posicionar el nodo hijo
                    distance = radius + child_radius  # Distancia desde el centro
                    child.x = distance * math.cos(angle)
                    child.y = distance * math.sin(angle)
        
        logger.info("Layout jerárquico aplicado exitosamente a los nodos")
        return nodes

    def save_concept_map(self, map_id, map_name, note_id, user_id, concepts, relations, metadata=None):
        """Guarda un mapa conceptual en Neo4j y lo vincula a su nota de origen."""
        # Importación local para evitar ciclo de dependencias
        from ..api.health import get_neo4j_driver
        neo4j_driver = get_neo4j_driver()
        
        if not neo4j_driver:
            logger.error("No se pudo guardar el mapa conceptual: driver de Neo4j no disponible.")
            return False

        with neo4j_driver.session() as session:
            # Usar una transacción para asegurar la atomicidad
            tx = session.begin_transaction()
            try:
                # 1. Crear o actualizar el nodo ConceptMap
                tx.run("""MERGE (cm:ConceptMap {id: $id})
                   ON CREATE SET cm.created_at = $timestamp
                   SET cm.name = $name, cm.user_id = $user_id, cm.metadata = $metadata, cm.updated_at = $timestamp
                """, 
                   id=map_id, name=map_name, user_id=int(user_id), 
                   metadata=json.dumps(metadata or {}), timestamp=datetime.utcnow().isoformat())

                # 2. Crear o actualizar los nodos ConceptNode
                for node in concepts:
                    # Manejar tanto objetos ConceptNode como diccionarios
                    if hasattr(node, 'id'):  # Es un objeto dataclass
                        node_id = getattr(node, 'id', '')
                        node_label = getattr(node, 'label', '')
                        node_type = getattr(node, 'type', '')
                        node_x = getattr(node, 'x', 0)
                        node_y = getattr(node, 'y', 0)
                        node_props = getattr(node, 'properties', {})
                    else:  # Es un diccionario
                        node_id = node.get('id', '')
                        node_label = node.get('label', '')
                        node_type = node.get('type', '')
                        node_x = node.get('x', 0)
                        node_y = node.get('y', 0)
                        node_props = node.get('properties', {})
                    
                    tx.run("""
                        MERGE (c:ConceptNode {id: $id})
                        SET c.label = $label, c.type = $type, c.x = $x, c.y = $y, c.properties = $properties
                    """, id=node_id, label=node_label, type=node_type, x=node_x or 0, y=node_y or 0, properties=json.dumps(node_props))
                    
                    # Vincular cada nodo al mapa conceptual
                    tx.run("""
                        MATCH (cm:ConceptMap {id: $map_id})
                        MATCH (node:ConceptNode {id: $node_id})
                        MERGE (cm)-[:CONTAINS]->(node)
                    """, map_id=map_id, node_id=node_id)

                # 3. Crear las relaciones RELATES_TO
                for edge in relations:
                    # Manejar tanto objetos ConceptEdge como diccionarios
                    if hasattr(edge, 'id'):  # Es un objeto dataclass
                        edge_id = getattr(edge, 'id', '')
                        edge_source = getattr(edge, 'source', '')
                        edge_target = getattr(edge, 'target', '')
                        edge_label = getattr(edge, 'label', '')
                        edge_type = getattr(edge, 'type', '')
                        edge_props = getattr(edge, 'properties', {})
                    else:  # Es un diccionario
                        edge_id = edge.get('id', '')
                        edge_source = edge.get('source', '')
                        edge_target = edge.get('target', '')
                        edge_label = edge.get('label', '')
                        edge_type = edge.get('type', '')
                        edge_props = edge.get('properties', {})
                    
                    # Determinar el tipo de relación para Neo4j basado en el tipo en el modelo
                    neo4j_rel_type = "RELATES_TO"  # Tipo por defecto
                    if edge_type == "HAS_CATEGORY":
                        neo4j_rel_type = "HAS_CATEGORY"
                    elif edge_type == "CONTAINS":
                        neo4j_rel_type = "CONTAINS"
                    elif edge_type == "RELATED_TO":
                        neo4j_rel_type = "RELATED_TO"
                
                    # Usar una expresión parametrizada para el tipo de relación
                    cypher_query = f"""
                        MATCH (source:ConceptNode {{id: $source_id}})
                        MATCH (target:ConceptNode {{id: $target_id}})
                        MERGE (source)-[r:{neo4j_rel_type} {{id: $edge_id}}]->(target)
                        SET r.label = $label, r.type = $edge_type, r.properties = $properties
                    """
                
                    tx.run(
                        cypher_query, 
                        source_id=edge_source, 
                        target_id=edge_target, 
                        edge_id=edge_id,
                        label=edge_label, 
                        edge_type=edge_type, 
                        properties=json.dumps(edge_props)
                    )

                # 4. Vincular el ConceptMap con la Note (crear nodo Note si no existe)
                tx.run("""
                    MERGE (n:Note {id: toInteger($note_id)})
                    MERGE (cm:ConceptMap {id: $map_id})
                    MERGE (cm)-[:GENERATED_FROM]->(n)
                """, map_id=map_id, note_id=int(note_id))

                tx.commit()
                logger.info(f"Mapa conceptual '{map_id}' guardado y vinculado a la nota {note_id}.")
            except Exception as e:
                logger.error(f"Error al guardar el mapa conceptual: {e}")
                tx.rollback()
                return False
                
            return True


    def _arrange_in_circle(self, nodes: List[ConceptNode], radius: float):
        """Organiza nodos en un círculo"""
        import math
        
        if not nodes:
            return
            
        angle_step = 2 * math.pi / len(nodes)
        
        for i, node in enumerate(nodes):
            angle = i * angle_step
            node.x = radius * math.cos(angle)
            node.y = radius * math.sin(angle)

    def _analyze_note_content(self, content: str) -> Dict[str, Any]:
        """Analiza el contenido de la nota usando IA"""
        try:
            # Generar resumen
            summary = self.text_summarizer.summarize_text(content)
            
            # Extraer entidades
            entities = self.text_summarizer.extract_entities(content)
            
            # Clasificar temas
            topics = self.text_summarizer.classify_topics(content)
            
            return {
                'summary': summary,
                'entities': entities,
                'topics': topics,
                'main_topic': topics[0] if topics else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing note content: {str(e)}")
            return {}

    def _update_note_with_analysis(self, session: Session, note: Note, analysis: Dict[str, Any]):
        """Actualiza la nota con los resultados del análisis"""
        try:
            if analysis.get('summary'):
                note.summary = analysis['summary']
            
            if analysis.get('main_topic'):
                note.main_topic = analysis['main_topic']
            
            # Guardar entidades como JSON
            if analysis.get('entities'):
                note.entities = json.dumps(analysis['entities'])
            
            session.commit()
            logger.info(f"Updated note {note.id} with AI analysis")
            
        except Exception as e:
            logger.error(f"Error updating note with analysis: {str(e)}")
            session.rollback()

    def get_concept_map_by_id(self, map_id: str, user_id: int) -> Dict[str, Any]:
        """Obtiene un mapa conceptual por su ID desde Neo4j"""
        # Importación local para evitar ciclo de dependencias
        from ..api.health import get_neo4j_driver
        neo4j_driver = get_neo4j_driver()
        
        try:
            if not neo4j_driver:
                logger.warning("Neo4j no disponible, retornando None")
                return None
                
            with neo4j_driver.session() as session:
                # Consultar el mapa conceptual y sus nodos/relaciones
                # Usar toInteger para la comparación de user_id
                result = session.run("""
                    MATCH (cm:ConceptMap {id: $map_id})
                    OPTIONAL MATCH (cm)-[:GENERATED_FROM]->(n:Note)
                    WHERE toInteger(n.user_id) = $user_id OR $user_id IS NULL
                    OPTIONAL MATCH (cm)-[:CONTAINS]->(node:ConceptNode)
                    OPTIONAL MATCH (node)-[rel:RELATES_TO|CONTAINS|TAGGED_AS|HAS_CATEGORY|RELATED_TO]->(target:ConceptNode)
                    RETURN cm, n, 
                           collect(DISTINCT {node: node, props: node}) as nodes,
                           collect(DISTINCT {rel: rel, source: startNode(rel), target: endNode(rel)}) as relations
                """, map_id=map_id, user_id=user_id)
                
                record = result.single()
                if not record:
                    return None
                    
                concept_map = record['cm']
                note = record['n']
                nodes = record['nodes'] or []
                relations = record['relations'] or []
                
                # Convertir a formato API
                return {
                    'id': concept_map['id'],
                    'name': concept_map.get('name', f"Mapa {map_id}"),
                    'nodes': [
                        {
                            'id': node['node']['id'],
                            'label': node['node']['label'],
                            'type': node['node'].get('type', 'unknown'),
                            'properties': json.loads(node['node'].get('properties', '{}')),
                            'color': node['node'].get('color'),
                            'size': node['node'].get('size'),
                            'x': node['node'].get('x'),
                            'y': node['node'].get('y')
                        }
                        for node in nodes if node['node']
                    ],
                    'links': [
                        {
                            'id': rel['rel']['id'],
                            'source': rel['source']['id'],
                            'target': rel['target']['id'],
                            'label': rel['rel'].get('label', ''),
                            'type': rel['rel'].get('type', 'unknown'),
                            'properties': json.loads(rel['rel'].get('properties', '{}')),
                            'color': rel['rel'].get('color'),
                            'width': rel['rel'].get('width')
                        }
                        for rel in relations if rel['rel']
                    ],
                    'metadata': {
                        'note_id': note['id'] if note else None,
                        'note_title': note['title'] if note else None,
                        'created_at': concept_map.get('created_at'),
                        'total_nodes': len(nodes),
                        'total_relations': len(relations)
                    }
                }
                
        except Exception as e:
            logger.error(f"Error al obtener mapa conceptual {map_id}: {str(e)}")
            return {'error': str(e)}
    
    def get_user_concept_maps(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los mapas conceptuales de un usuario"""
        # Importación local para evitar ciclo de dependencias
        from ..api.health import get_neo4j_driver
        neo4j_driver = get_neo4j_driver()
        
        try:
            if not user_id:
                logger.warning("user_id vacío o None")
                return []
            
            with neo4j_driver.session() as session:
                # Usar toInteger para comparación de user_id
                result = session.run("""
                MATCH (cm:ConceptMap)
                WHERE toInteger(cm.user_id) = $user_id
                OPTIONAL MATCH (cm)-[:GENERATED_FROM]->(n:Note)
                OPTIONAL MATCH (cm)-[:CONTAINS]->(node:ConceptNode)
                RETURN cm, n, count(node) as node_count
                ORDER BY cm.created_at DESC
                """, user_id=user_id)
            
                maps = []
                for record in result:
                    concept_map = record['cm']
                    note = record['n']
                    node_count = record['node_count']
                    
                    maps.append({
                        'id': concept_map['id'],
                        'name': concept_map.get('name', 'Mapa sin nombre'),
                        'note_id': note['id'] if note else None,
                        'note_title': note['title'] if note else 'Sin nota asociada',
                        'node_count': node_count,
                        'created_at': concept_map.get('created_at'),
                        'user_id': concept_map.get('user_id')
                    })
                
                return maps
                
        except Exception as e:
            logger.error(f"Error al obtener mapas conceptuales del usuario {user_id}: {str(e)}")
            return []

    def delete_concept_map(self, map_id: str, user_id: int) -> bool:
        """Elimina un mapa conceptual, sus nodos y relaciones."""
        from ..api.health import get_neo4j_driver
        neo4j_driver = get_neo4j_driver()
        if not neo4j_driver:
            logger.warning("Neo4j no disponible, no se puede eliminar el mapa.")
            return False

        try:
            # Aseguramos que user_id sea un entero
            user_id = int(user_id) if not isinstance(user_id, int) else user_id
            
            with neo4j_driver.session() as session:
                # Verificar que el mapa existe y pertenece al usuario correcto
                # Modificada la consulta para no usar la etiqueta User ni la relación OWNS
                result = session.run("""
                    MATCH (cm:ConceptMap {id: $map_id})
                    WHERE cm.user_id = $user_id
                    RETURN cm
                """, user_id=user_id, map_id=map_id)
                
                record = result.single()
                if not record:
                    logger.warning(f"Intento de eliminar mapa {map_id} por usuario {user_id} no autorizado o mapa no existe.")
                    return False

                # Si pertenece, proceder a eliminar el mapa y sus nodos asociados
                session.run("""
                    MATCH (cm:ConceptMap {id: $map_id})
                    OPTIONAL MATCH (cm)-[r]-(n)
                    DETACH DELETE cm, n
                """, map_id=map_id)
                
                logger.info(f"Mapa conceptual {map_id} eliminado exitosamente por el usuario {user_id}.")
                return True

        except Exception as e:
            logger.error(f"Error al eliminar el mapa conceptual {map_id}: {str(e)}")
            return False

    def convert_to_api_format(self, concept_map: ConceptMap) -> Dict[str, Any]:
        """Convierte el mapa conceptual al formato esperado por la API"""
        return {
            'id': concept_map.id,
            'name': concept_map.name,
            'concepts': [
                {
                    'id': node.id,
                    'label': node.label,
                    'type': node.type,
                    'properties': node.properties,
                    'color': node.color,
                    'size': node.size,
                    'x': node.x,
                    'y': node.y
                }
                for node in concept_map.nodes
            ],
            'relations': [
                {
                    'id': edge.id,
                    'source': edge.source,
                    'target': edge.target,
                    'label': edge.label,
                    'type': edge.type,
                    'properties': edge.properties,
                    'color': edge.color,
                    'width': edge.width
                }
                for edge in concept_map.edges
            ],
            'metadata': concept_map.metadata
        }
    
    # ========== MÉTODOS BÁSICOS SIN IA ==========
    
    def _create_basic_topic_nodes(self, note: Note) -> List[ConceptNode]:
        """Crea nodos de temas usando solo datos básicos sin IA"""
        nodes = []
        
        # Solo usar el tema principal si está disponible
        if hasattr(note, 'main_topic') and note.main_topic:
            main_topic_node = ConceptNode(
                id=f"basic_topic_{note.id}",
                label=note.main_topic,
                type="topic",
                properties={'source': 'basic', 'topic_type': 'main'},
                color=self.node_colors['topic'],
                size=self.node_sizes['topic']
            )
            nodes.append(main_topic_node)
        
        logger.info(f"Creados {len(nodes)} nodos de temas básicos para nota {note.id}")
        return nodes
    
    def _create_basic_entity_nodes(self, note: Note) -> List[ConceptNode]:
        """Crea nodos de entidades usando solo datos ya persistidos"""
        nodes = []
        
        # Solo usar analysis_cache si existe (sin cargar modelos)
        if hasattr(note, 'analysis_cache') and note.analysis_cache:
            try:
                entities = note.analysis_cache.get('entities', {})
                entity_counter = 0
                
                for entity_type, entity_list in entities.items():
                    if entity_counter >= 8:  # Límite reducido para modo básico
                        break
                    
                    for entity_name in entity_list[:3]:  # Máximo 3 por tipo
                        if entity_counter >= 8:
                            break
                            
                        entity_node = ConceptNode(
                            id=f"basic_entity_{note.id}_{entity_counter}",
                            label=str(entity_name),
                            type="entity",
                            properties={
                                'entity_type': entity_type,
                                'source': 'basic_cache'
                            },
                            color=self.node_colors['entity'],
                            size=self.node_sizes['entity'] - 2
                        )
                        nodes.append(entity_node)
                        entity_counter += 1
                        
            except Exception as e:
                logger.warning(f"Error en modo básico de entidades para nota {note.id}: {e}")
        
        logger.info(f"Creados {len(nodes)} nodos de entidades básicos para nota {note.id}")
        return nodes
    
    def _create_basic_keyword_nodes(self, note: Note) -> List[ConceptNode]:
        """Crea nodos de palabras clave usando solo datos simples"""
        nodes = []
        
        # Solo usar keywords ya persistidas
        if hasattr(note, 'analysis_cache') and note.analysis_cache:
            try:
                keywords = note.analysis_cache.get('keywords', [])
                
                for i, keyword in enumerate(keywords[:5]):  # Máximo 5 keywords
                    keyword_node = ConceptNode(
                        id=f"basic_keyword_{note.id}_{i}",
                        label=str(keyword),
                        type="keyword",
                        properties={'source': 'basic_cache', 'importance': len(keywords) - i},
                        color="#FFA726",
                        size=10
                    )
                    nodes.append(keyword_node)
                    
            except Exception as e:
                logger.warning(f"Error en modo básico de keywords para nota {note.id}: {e}")
        
        logger.info(f"Creados {len(nodes)} nodos de keywords básicos para nota {note.id}")
        return nodes
    
    # ========== MÉTODOS CON IA (AVANZADOS) ==========
    
    def _create_entity_nodes_with_ai(self, note: Note) -> List[ConceptNode]:
        """Crea nodos de entidades con análisis IA completo"""
        # Reutilizar el método existente optimizado
        return self._create_entity_nodes(note)
    
    def _create_keyword_nodes_with_ai(self, note: Note) -> List[ConceptNode]:
        """Crea nodos de keywords con análisis IA completo"""
        # Reutilizar el método existente optimizado
        return self._create_keyword_nodes(note)
