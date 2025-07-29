import React, { useState, useRef, useEffect } from 'react';
import './GraphLegend.modern.css';

interface GraphLegendProps {
  nodeColors: Record<string, string>;
}

const GraphLegend: React.FC<GraphLegendProps> = ({ nodeColors }) => {
  const [collapsed, setCollapsed] = useState(false);
  const legendRef = useRef<HTMLDivElement>(null);
  const [legendPosition, setLegendPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);

  // Obtener nombres legibles para los tipos de nodos
  const getTypeName = (type: string): string => {
    switch (type) {
      case 'concept': return 'Concepto';
      case 'topic': return 'Tema';
      case 'note': return 'Nota';
      case 'tag': return 'Etiqueta';
      case 'default': return 'Otros';
      default: return type.charAt(0).toUpperCase() + type.slice(1);
    }
  };
  
  // Permitir arrastrar la leyenda por la pantalla
  useEffect(() => {
    const legend = legendRef.current;
    if (!legend) return;
    
    let startX: number, startY: number, startLeft: number, startTop: number;
    
    const handleMouseDown = (e: MouseEvent) => {
      if (e.target instanceof Element) {
        // Solo iniciar arrastre si es en el header
        if (e.target.closest('.legend-header')) {
          e.preventDefault();
          setIsDragging(true);
          
          // Posición inicial del ratón
          startX = e.clientX;
          startY = e.clientY;
          
          // Posición inicial del elemento
          const rect = legend.getBoundingClientRect();
          startLeft = rect.left;
          startTop = rect.top;
        }
      }
    };
    
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      
      // Calcular la nueva posición
      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;
      
      // Actualizar posición
      setLegendPosition({
        x: startLeft + deltaX,
        y: startTop + deltaY
      });
    };
    
    const handleMouseUp = () => {
      setIsDragging(false);
    };
    
    legend.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      legend.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  // Estilo dinámico para posicionamiento personalizado
  const legendStyle = {
    position: isDragging ? 'fixed' : 'absolute',
    top: isDragging ? `${legendPosition.y}px` : undefined,
    left: isDragging ? `${legendPosition.x}px` : undefined,
    cursor: isDragging ? 'grabbing' : undefined
  };
  
  return (
    <div 
      ref={legendRef}
      className={`graph-legend ${collapsed ? 'collapsed' : ''} ${isDragging ? 'dragging' : ''}`}
      style={legendStyle as React.CSSProperties}
      role="complementary"
      aria-label="Leyenda del gráfico"
    >
      <div 
        className="legend-header" 
        onClick={() => setCollapsed(!collapsed)}
        role="button"
        tabIndex={0}
        aria-expanded={!collapsed}
        aria-controls="legend-content"
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setCollapsed(!collapsed);
          }
        }}
      >
        <h6>
          <i className="fas fa-info-circle" aria-hidden="true"></i>
          Leyenda
        </h6>
        <button 
          type="button" 
          aria-label={collapsed ? "Expandir leyenda" : "Colapsar leyenda"}
        >
          {collapsed ? (
            <i className="fas fa-chevron-down" aria-hidden="true"></i>
          ) : (
            <i className="fas fa-chevron-up" aria-hidden="true"></i>
          )}
        </button>
      </div>
      
      <div 
        id="legend-content" 
        className={`legend-content ${!collapsed ? 'visible' : ''}`}
        aria-hidden={collapsed}
      >
        <div className="legend-body">
          <div className="legend-list" role="list">
            {Object.entries(nodeColors).map(([type, color]) => (
              <div 
                key={type} 
                className="legend-item" 
                role="listitem"
              >
                <span 
                  className="color-dot" 
                  style={{ backgroundColor: color }}
                  aria-hidden="true"
                ></span>
                <span className="type-name">{getTypeName(type)}</span>
              </div>
            ))}
          </div>
          <div className="legend-footer">
            <small>
              Haz clic en un nodo para ver más información.
            </small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraphLegend;
