import { describe, it, expect, test } from 'vitest';

// Prueba directa sin describe/it
test('prueba simple directa', () => {
  console.log('Ejecutando prueba simple directa');
  expect(1 + 1).toBe(2);
});

describe('Suite de pruebas básicas', () => {
  // Prueba antes de todas las pruebas
  console.log('Inicializando suite de pruebas');
  
  it('verifica que true sea true', () => {
    console.log('Ejecutando prueba de true');
    expect(true).toBe(true);
  });

  it('verifica una suma simple', () => {
    console.log('Ejecutando prueba de suma');
    expect(1 + 2).toBe(3);
  });
});
