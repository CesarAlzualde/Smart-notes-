import React from 'react';

interface StatCardProps {
  icon: string;
  value: number | string;
  label: string;
  color?: string;
  isLoading?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({
  icon,
  value,
  label,
  color = '#3498db',
  isLoading = false
}) => {
  // Calcular el color de fondo con baja opacidad
  const bgColor = `rgba(${hexToRgb(color)}, 0.1)`;
  
  return (
    <div className="stat-card">
      <div 
        className="stat-icon" 
        style={{ backgroundColor: bgColor, color: color }}
      >
        <i className={`fas ${icon}`}></i>
      </div>
      <div className="stat-info">
        <div className="stat-value">
          {isLoading ? (
            <i className="fas fa-spinner fa-spin" style={{ fontSize: '1.2rem' }}></i>
          ) : (
            value
          )}
        </div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
};

// Función auxiliar para convertir color hexadecimal a RGB
const hexToRgb = (hex: string): string => {
  // Eliminar el # si está presente
  hex = hex.replace('#', '');
  
  // Convertir a RGB
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  
  return `${r}, ${g}, ${b}`;
};

export default StatCard;
