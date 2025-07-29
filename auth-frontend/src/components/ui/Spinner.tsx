import React from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

// Tipos para el componente Spinner
export interface SpinnerProps {
  size?: 'small' | 'medium' | 'large' | 'xl';
  color?: 'primary' | 'secondary' | 'inherit';
  text?: string;
  fullScreen?: boolean;
  className?: string;
}

// Keyframes para la animación
const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

// Configuración de tamaños
const sizes = {
  small: {
    width: '20px',
    height: '20px',
    borderWidth: '2px',
  },
  medium: {
    width: '32px',
    height: '32px',
    borderWidth: '3px',
  },
  large: {
    width: '48px',
    height: '48px',
    borderWidth: '4px',
  },
  xl: {
    width: '64px',
    height: '64px',
    borderWidth: '5px',
  },
};

// Overlay de pantalla completa para bloquear la UI
const SpinnerOverlay = styled.div<{ fullScreen: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  
  ${props => props.fullScreen ? `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(3px);
  ` : ''}
`;

// Contenedor para el spinner con texto
const SpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
`;

// El elemento spinner en sí
const SpinnerElement = styled.div<{
  size: 'small' | 'medium' | 'large' | 'xl';
  colorVariant: 'primary' | 'secondary' | 'inherit';
}>`
  width: ${props => sizes[props.size].width};
  height: ${props => sizes[props.size].height};
  border: ${props => sizes[props.size].borderWidth} solid transparent;
  border-radius: 50%;
  animation: ${spin} 1.2s linear infinite;
  
  ${props => {
    if (props.colorVariant === 'inherit') {
      return `
        border-top-color: currentColor;
        border-bottom-color: currentColor;
        opacity: 0.6;
      `;
    } else if (props.colorVariant === 'primary') {
      return `
        border-top-color: ${props.theme?.spinner?.primary || '#4776E6'};
        border-bottom-color: ${props.theme?.spinner?.secondary || '#8E54E9'};
      `;
    } else {
      return `
        border-top-color: ${props.theme?.spinner?.secondary || '#8E54E9'};
        border-bottom-color: ${props.theme?.spinner?.primary || '#4776E6'};
      `;
    }
  }}
  
  &::after {
    content: "";
    width: 100%;
    height: 100%;
    position: absolute;
    border: ${props => sizes[props.size].borderWidth} solid transparent;
    border-radius: 50%;
    
    ${props => {
      if (props.colorVariant === 'inherit') {
        return `
          border-left-color: currentColor;
          border-right-color: currentColor;
          opacity: 0.3;
        `;
      } else if (props.colorVariant === 'primary') {
        return `
          border-left-color: ${props.theme?.spinner?.primary || '#4776E6'};
          border-right-color: ${props.theme?.spinner?.secondary || '#8E54E9'};
          opacity: 0.6;
        `;
      } else {
        return `
          border-left-color: ${props.theme?.spinner?.secondary || '#8E54E9'};
          border-right-color: ${props.theme?.spinner?.primary || '#4776E6'};
          opacity: 0.6;
        `;
      }
    }}
    
    animation: ${spin} 1.8s linear infinite reverse;
  }
`;

// Texto estilizado para el spinner
const SpinnerText = styled.div<{ fullScreen: boolean }>`
  font-size: ${props => props.fullScreen ? '1rem' : '0.875rem'};
  font-weight: 500;
  color: ${props => props.fullScreen ? 'white' : (props.theme?.text || '#2D3748')};
  margin-top: 0.5rem;
  text-align: center;
  ${props => props.fullScreen ? 'text-shadow: 0 1px 2px rgba(0,0,0,0.3);' : ''}
`;

// Componente Spinner
export const Spinner: React.FC<SpinnerProps> = ({
  size = 'medium',
  color = 'primary',
  text,
  fullScreen = false,
  className,
}) => {
  return (
    <SpinnerOverlay fullScreen={fullScreen} className={className}>
      <SpinnerContainer>
        <SpinnerElement
          size={size}
          colorVariant={color}
        />
        {text && <SpinnerText fullScreen={fullScreen}>{text}</SpinnerText>}
      </SpinnerContainer>
    </SpinnerOverlay>
  );
};

export default Spinner;
