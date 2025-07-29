// Este script asegura que AFRAME esté disponible globalmente antes de cargar nipple-controls.js
console.log("Inicializando cargador de A-Frame...");

// Verifica si AFRAME ya está disponible
if (typeof AFRAME === 'undefined') {
    console.log("AFRAME no disponible, cargando desde CDN...");
    
    // Función para cargar nipple-controls una vez que A-Frame esté listo
    function loadNippleControls() {
        console.log("A-Frame cargado correctamente, cargando nipple-controls...");
        
        // Crear script para nipple-controls
        var nippleScript = document.createElement('script');
        nippleScript.src = '/nipple-controls.js';
        nippleScript.onerror = function() {
            console.error("Error al cargar nipple-controls.js");
        };
        document.head.appendChild(nippleScript);
    }
    
    // Si el script A-Frame ya existe pero AFRAME no está definido, esperamos a que se defina
    if (document.querySelector('script[src*="aframe.min.js"]')) {
        console.log("Script de A-Frame ya existe, esperando inicialización...");
        
        // Verificar periódicamente hasta que AFRAME esté disponible
        var checkInterval = setInterval(function() {
            if (typeof AFRAME !== 'undefined') {
                clearInterval(checkInterval);
                loadNippleControls();
            }
        }, 100);
    } else {
        console.log("Agregando script de A-Frame dinámicamente...");
        
        // Crear script para A-Frame
        var aframeScript = document.createElement('script');
        aframeScript.src = 'https://aframe.io/releases/1.4.2/aframe.min.js';
        aframeScript.onload = loadNippleControls;
        aframeScript.onerror = function() {
            console.error("Error al cargar A-Frame desde CDN");
        };
        document.head.appendChild(aframeScript);
    }
} else {
    console.log("AFRAME ya está disponible, cargando nipple-controls directamente...");
    
    // AFRAME ya está disponible, cargar nipple-controls directamente
    var nippleScript = document.createElement('script');
    nippleScript.src = '/nipple-controls.js';
    document.head.appendChild(nippleScript);
}
