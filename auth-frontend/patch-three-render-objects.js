const fs = require('fs');
const path = require('path');

// Ruta al archivo a modificar
const filePath = path.join(process.cwd(), 'node_modules/three-render-objects/dist/three-render-objects.mjs');

// Leer el contenido del archivo
let fileContent = fs.readFileSync(filePath, 'utf8');

// Reemplazar la importación problemática
fileContent = fileContent.replace(
  `import { WebGPURenderer } from 'three/webgpu';`, 
  `// Mock for WebGPURenderer
const WebGPURenderer = class {
  constructor() {}
  render() {}
  setSize() {}
  get domElement() { return document.createElement('div'); }
};`
);

// Si hay código que verifica WebGPU.isAvailable, podemos agregar una definición adicional
fileContent = fileContent.replace(
  /WebGPU\.isAvailable/g, 
  'false /* WebGPU mock */'
);

// Escribir el contenido modificado de vuelta al archivo
fs.writeFileSync(filePath, fileContent);
console.log('Successfully patched three-render-objects.mjs');
