// Mock para WebGPURenderer
export class WebGPURenderer {
  constructor() {
    this.domElement = document.createElement('div');
  }
  render() {}
  setSize() {}
}

export const WebGPU = { 
  isAvailable: false 
};

export default {
  WebGPURenderer,
  WebGPU
};
