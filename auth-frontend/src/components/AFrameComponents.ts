// AFrameComponents.ts - Componentes personalizados para A-Frame
import 'aframe';

console.log("Inicialización de componentes A-Frame");

// IMPORTANTE: No registramos 'nipple-controls' aquí porque ya lo hace aframe-extras
// En su lugar, solo agregamos componentes personalizados que no existan en otras librerías

// Ejemplo de inicialización segura de componentes personalizados
if (!(window as any).CUSTOM_COMPONENTS_REGISTERED) {
  // Aquí puedes registrar componentes personalizados que no existan en aframe-extras
  // u otras bibliotecas que ya estés usando
  
  // Marcar que los componentes personalizados ya se registraron
  (window as any).CUSTOM_COMPONENTS_REGISTERED = true;
  console.log("Inicialización de componentes personalizados de A-Frame completada");
}
