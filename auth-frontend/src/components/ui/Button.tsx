import React from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import type { IconType } from 'react-icons';
import type { Theme } from '../../theme/themeConstants';

// Define variantes de botón
export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'text';
export type ButtonSize = 'small' | 'medium' | 'large';

// Keyframes para animación del spinner
const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

// Props para el componente Button
export interface ButtonProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
  icon?: IconType;
  iconPosition?: 'left' | 'right';
  isLoading?: boolean;
  loadingText?: string;
  className?: string;
}

// Definir tamaños de botón
const sizes = {
  small: {
    padding: '0.375rem 0.75rem',
    fontSize: '0.875rem',
  },
  medium: {
    padding: '0.5rem 1rem',
    fontSize: '0.9375rem',
  },
  large: {
    padding: '0.625rem 1.25rem',
    fontSize: '1rem',
  },
};

// Componente Spinner para estado de carga
const ButtonSpinner = styled.div`
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: ${spin} 0.75s linear infinite;
  margin-right: ${props => props.children ? '0.5rem' : '0'};
`;

// Componente de botón estilizado
const StyledButton = styled.button<{
  variant: ButtonVariant;
  size: ButtonSize;
  fullWidth: boolean;
  hasIcon: boolean;
  iconPosition: 'left' | 'right';
  isLoading: boolean;
}>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  gap: ${props => (props.hasIcon || props.isLoading) ? '0.5rem' : '0'};
  white-space: nowrap;
  width: ${props => props.fullWidth ? '100%' : 'auto'};
  flex-direction: ${props => props.iconPosition === 'right' ? 'row-reverse' : 'row'};
  
  /* Estilos de tamaño */
  padding: ${props => sizes[props.size].padding};
  font-size: ${props => sizes[props.size].fontSize};
  
  /* Estilos de variante */
  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background: ${(props.theme as Theme).button.primaryBg};
          color: ${(props.theme as Theme).button.primaryText};
          border: none;
          
          &:hover:not(:disabled) {
            background: ${(props.theme as Theme).button.primaryHoverBg};
          }
        `;
      case 'secondary':
        return `
          background: ${(props.theme as Theme).button.secondaryBg};
          color: ${(props.theme as Theme).button.secondaryText};
          border: none;
          
          &:hover:not(:disabled) {
            background: ${(props.theme as Theme).button.secondaryHoverBg};
          }
        `;
      case 'outline':
        return `
          background: transparent;
          color: ${(props.theme as Theme).primary};
          border: 1px solid ${(props.theme as Theme).primary};
          
          &:hover:not(:disabled) {
            background: rgba(71, 118, 230, 0.08);
          }
        `;
      case 'text':
        return `
          background: transparent;
          color: ${(props.theme as Theme).primary};
          border: none;
          padding-left: 0.5rem;
          padding-right: 0.5rem;
          
          &:hover:not(:disabled) {
            background: rgba(71, 118, 230, 0.08);
          }
        `;
      default:
        return '';
    }
  }}
  
  /* Estado deshabilitado */
  &:disabled {
    background: ${props => props.variant === 'outline' || props.variant === 'text' 
      ? 'transparent' 
      : (props.theme as Theme).button.disabledBg};
    color: ${props => (props.theme as Theme).button.disabledText};
    border-color: ${props => props.variant === 'outline' ? (props.theme as Theme).button.disabledText : 'transparent'};
    cursor: not-allowed;
    opacity: 0.7;
  }
`;

// Contenedor de icono para espaciado consistente
const IconContainer = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
`;

// Componente Botón
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  disabled = false,
  type = 'button',
  onClick,
  children,
  icon: Icon,
  iconPosition = 'left',
  isLoading = false,
  loadingText,
  className,
}) => {
  const hasIcon = !!Icon;
  
  return (
    <StyledButton
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      disabled={disabled || isLoading}
      type={type}
      onClick={onClick}
      hasIcon={hasIcon}
      iconPosition={iconPosition}
      isLoading={isLoading}
      className={className}
    >
      {isLoading ? (
        <>
          <ButtonSpinner>{null}</ButtonSpinner>
          {loadingText || children}
        </>
      ) : (
        <>
          {Icon && (
            <IconContainer>
              <Icon />
            </IconContainer>
          )}
          {children}
        </>
      )}
    </StyledButton>
  );
};

export default Button;
