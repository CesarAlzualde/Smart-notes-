// Este archivo configura el entorno de pruebas para los componentes
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Configuración global para pruebas
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mocks para APIs del navegador que pueden no estar disponibles en JSDOM
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // Deprecated
    removeListener: vi.fn(), // Deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Silenciar advertencias específicas durante las pruebas
const originalConsoleError = console.error;
console.error = (...args: any[]) => {
  if (
    /Warning.*not wrapped in act/.test(args[0] as string) ||
    /Warning.*cannot update a component/.test(args[0] as string)
  ) {
    return;
  }
  originalConsoleError(...args);
};
