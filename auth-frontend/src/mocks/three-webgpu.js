/**
 * Mock para three/webgpu
 * Este archivo proporciona implementaciones vacías de las clases y funciones
 * que se importan desde three/webgpu en three-render-objects
 */

export class WebGPURenderer {
  constructor() {}
  render() {}
  setSize() {}
  domElement = document.createElement('div');
}

export const WebGPU = { 
  isAvailable: false
};

// Exportación por defecto
export default {
  WebGPURenderer,
  WebGPU
};
