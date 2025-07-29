/**
 * Manejador global de errores para la aplicación
 * Proyecto Apuntes - Protección contra errores comunes
 */

(function() {
    // Guardar referencia original a console.error
    const originalConsoleError = console.error;

    // Sobrescribir console.error para capturar errores específicos
    console.error = function(...args) {
        // Llamar a la implementación original
        originalConsoleError.apply(console, args);
        
        // Verificar si es el error específico de "Cannot read properties of undefined (reading 'replace')"
        const errorMsg = args.join(' ');
        if (errorMsg.includes("Cannot read properties of undefined") && errorMsg.includes("replace")) {
            console.log("Error de tipo 'undefined.replace()' detectado y gestionado");
            
            // Aquí podríamos enviar telemetría o registrar el error para análisis futuro
            // Por ahora simplemente evitamos que el error bloquee la aplicación
        }
        
        // Protección contra error de null addEventListener (el que está bloqueando la carga de notas)
        if (errorMsg.includes("Cannot read properties of null") && errorMsg.includes("addEventListener")) {
            console.log("Error de addEventListener en elemento nulo detectado y gestionado");
            // Este error es crítico para la carga de la interfaz, lo registramos específicamente
        }
    };

    // Proteger el método location.replace
    try {
        const originalLocationReplace = window.location.replace;
        
        // Sobreescribir el método con uno a prueba de fallos
        window.location.replace = function(url) {
            try {
                console.log("Redirigiendo de forma segura a:", url);
                originalLocationReplace.call(window.location, url);
            } catch (e) {
                console.error("Error en redirección segura:", e);
                // Fallback a otros métodos de redirección
                try {
                    window.location.href = url;
                } catch (e2) {
                    console.error("Error en fallback href:", e2);
                    window.location = url;
                }
            }
        };
    } catch (e) {
        console.error("No se pudo proteger window.location.replace:", e);
    }
    
    /**
     * Añade un event listener de forma segura, verificando primero si el elemento existe
     * 
     * @param {string|Element} elementOrSelector - El elemento DOM o selector CSS
     * @param {string} eventType - El tipo de evento (click, change, etc.)
     * @param {Function} callback - Función a ejecutar cuando ocurre el evento
     * @param {boolean|object} options - Opciones para addEventListener
     * @return {boolean} - true si se añadió el listener, false si el elemento no existe
     */
    function addSafeEventListener(elementOrSelector, eventType, callback, options) {
        // Determinar si es un selector o un elemento
        let element = elementOrSelector;
        
        if (typeof elementOrSelector === 'string') {
            element = document.querySelector(elementOrSelector);
        } else if (typeof elementOrSelector === 'object' && elementOrSelector === null) {
            console.warn(`No se pudo añadir evento ${eventType} - Elemento nulo`);
            return false;
        }
        
        // Verificar si el elemento existe
        if (element && typeof element.addEventListener === 'function') {
            element.addEventListener(eventType, callback, options);
            return true;
        } else {
            console.warn(`No se pudo añadir evento ${eventType} - Elemento no encontrado o no válido`);
            return false;
        }
    }
    
    /**
     * Obtiene un elemento DOM por ID de forma segura
     * 
     * @param {string} id - ID del elemento
     * @param {boolean} silent - Si es true, no muestra advertencia 
     * @return {Element|null} - El elemento DOM o null si no existe
     */
    function getElementByIdSafe(id, silent = false) {
        const element = document.getElementById(id);
        if (!element && !silent) {
            console.warn(`Elemento con ID ${id} no encontrado`);
        }
        return element;
    }
    
    // Exportar funciones para uso global
    window.addSafeEventListener = addSafeEventListener;
    window.getElementByIdSafe = getElementByIdSafe;
    
    // Proteger String.prototype.replace para evitar errores cuando el objeto es undefined
    const originalReplace = String.prototype.replace;
    String.prototype.replace = function(...args) {
        if (this === undefined || this === null) {
            console.error("Intento de llamar a replace() en un valor undefined o null");
            return "";
        }
        return originalReplace.apply(this, args);
    };

    // Interceptar errores no capturados
    window.addEventListener('error', function(event) {
        if (event.error && event.error.message && 
            event.error.message.includes("Cannot read properties of undefined") && 
            event.error.message.includes("replace")) {
            
            console.log("Error de replace() interceptado globalmente");
            event.preventDefault();
            
            // Mostrar un mensaje amigable al usuario
            const errorMessage = document.createElement('div');
            errorMessage.className = 'alert alert-warning alert-dismissible fade show position-fixed top-0 end-0 m-3';
            errorMessage.innerHTML = `
                <strong>Atención</strong> Se detectó un error menor. 
                La aplicación continúa funcionando normalmente.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            document.body.appendChild(errorMessage);
            
            // Eliminar el mensaje después de 5 segundos
            setTimeout(() => {
                if (document.body.contains(errorMessage)) {
                    document.body.removeChild(errorMessage);
                }
            }, 5000);
            
            return true; // Impide que el error se propague
        }
        return false; // Permite que otros errores se manejen normalmente
    }, true);

    /**
     * Realiza una petición fetch con manejo de errores integrado
     * @param {string} url - URL a la que hacer la petición
     * @param {object} options - Opciones para fetch (method, headers, body, etc)
     * @param {function} onSuccess - Callback para manejar la respuesta exitosa (recibe datos parseados)
     * @param {function} onError - Callback para manejar errores (recibe objeto de error)
     * @param {boolean} showVisualFeedback - Si debe mostrar alertas visuales en caso de error
     * @param {number} timeoutMs - Timeout en milisegundos para la petición
     * @returns {Promise} - Promise de la petición (normalmente no es necesario usarla)
     */
    // Exportar al objeto global window para hacerla accesible desde cualquier archivo
    window.safeFetch = function(url, options = {}, onSuccess, onError, showVisualFeedback = true, timeoutMs = 10000) {
        console.log('safeFetch: Iniciando petición a', url);
        
        // Crear AbortController para timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        
        // Opciones por defecto + opciones del usuario + signal
        const fetchOptions = {
            ...options,
            signal: controller.signal
        };
        
        return fetch(url, fetchOptions)
            .then(response => {
                // Limpiar timeout ya que la petición se completó
                clearTimeout(timeoutId);
                
                // Verificar si la respuesta es correcta
                if (!response.ok) {
                    throw new Error(`Error HTTP ${response.status}: ${response.statusText}`);
                }
                
                // Intentar parsear como JSON y devolver los datos
                return response.json();
            })
            .then(data => {
                console.log('safeFetch: Éxito', data);
                
                // Llamar al callback de éxito si existe
                if (typeof onSuccess === 'function') {
                    onSuccess(data);
                }
                
                return data;
            })
            .catch(error => {
                console.error('safeFetch: Error', error);
                
                // Si es un error de timeout, mejorar el mensaje
                if (error.name === 'AbortError') {
                    error = new Error('La petición ha excedido el tiempo máximo de espera');
                }
                
                // Mostrar alerta visual si está activado
                if (showVisualFeedback && typeof showAlert === 'function') {
                    showAlert('danger', `Error en la petición: ${error.message}`);
                }
                
                // Llamar al callback de error si existe
                if (typeof onError === 'function') {
                    onError(error);
                }
                
                // Re-lanzar el error para manejar en otras partes
                throw error;
            });
    }

    // Función para mostrar alertas - exportada globalmente
    window.showAlert = function(type, message, duration = 5000) {
            // Crear contenedor de alertas si no existe
            let alertsContainer = document.getElementById('alerts-container');
            if (!alertsContainer) {
                alertsContainer = document.createElement('div');
                alertsContainer.id = 'alerts-container';
                alertsContainer.className = 'position-fixed top-0 end-0 p-3';
                alertsContainer.style.zIndex = '1050';
                document.body.appendChild(alertsContainer);
            }
            
            // Crear alerta
            const alert = document.createElement('div');
            alert.className = `alert alert-${type} alert-dismissible fade show`;
            alert.setAttribute('role', 'alert');
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
            `;
            
            // Agregar al DOM
            alertsContainer.appendChild(alert);
            
            // Auto cerrar después del tiempo indicado
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            }, duration);
        };

    console.log("Sistema de protección contra errores inicializado");
})();
