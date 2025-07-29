import React from 'react';
import { ListGroup } from 'react-bootstrap';

interface MapSummary {
  id: string;
  name: string;
}

interface ConceptMapListProps {
  maps: MapSummary[];
  onMapSelect: (mapId: string) => void;
  selectedMapId?: string | null;
}

const ConceptMapList: React.FC<ConceptMapListProps> = ({ maps, onMapSelect, selectedMapId }) => {
  if (!maps || maps.length === 0) {
    return <p>No se encontraron mapas conceptuales.</p>;
  }

  return (
    <div className="concept-map-list">
      <h5>Mis Mapas Conceptuales</h5>
      <ListGroup>
        {maps.map((map) => (
          <ListGroup.Item
            key={map.id}
            action
            onClick={() => onMapSelect(map.id)}
            active={map.id === selectedMapId}
          >
            {map.name}
          </ListGroup.Item>
        ))}
      </ListGroup>
    </div>
  );
};

export default ConceptMapList;
