import { describe, it, expect, test } from 'vitest';
import { render, screen } from '@testing-library/react';
import SimpleComponent from './SimpleComponent';

// Test básico para el componente simple
test('renders simple component', () => {
  render(<SimpleComponent text="Hello Testing" />);
  
  // Verificar que el texto se muestra correctamente
  const textElement = screen.getByTestId('text-content');
  expect(textElement.textContent).toBe('Hello Testing');
  
  // Verificar que el botón existe
  const button = screen.getByTestId('test-button');
  expect(button).toBeTruthy();
});

// Conjunto de pruebas más completo
describe('SimpleComponent suite', () => {
  it('renders with custom text', () => {
    const testText = 'Custom Text';
    render(<SimpleComponent text={testText} />);
    
    const textElement = screen.getByTestId('text-content');
    expect(textElement).toHaveTextContent(testText);
  });
});
