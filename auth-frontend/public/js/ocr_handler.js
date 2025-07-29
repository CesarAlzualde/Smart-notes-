/**
 * ocr_handler.js
 * Maneja la funcionalidad de OCR en la aplicación de Apuntes
 */

// Objeto global para manejar funcionalidades de OCR
const ocrHandler = {
    // Estado de procesamiento
    processing: false,
    
    // Inicializar el manejador
    init: function() {
        console.log("OCR Handler inicializado");
        this.bindEventListeners();
    },
    
    // Vincular eventos a elementos del DOM
    bindEventListeners: function() {
        // Vincular cuando el DOM esté listo
        document.addEventListener('DOMContentLoaded', () => {
            // Botón de procesamiento de archivo
            const processButton = document.getElementById('process-file-button');
            if (processButton) {
                processButton.addEventListener('click', this.processFile.bind(this));
            }
            
            // Selector de tipo de OCR
            const ocrTypeRadios = document.querySelectorAll('input[name="ocr-type"]');
            if (ocrTypeRadios.length > 0) {
                ocrTypeRadios.forEach(radio => {
                    radio.addEventListener('change', this.updateOcrType.bind(this));
                });
            }
        });
    },
    
    // Actualizar el tipo de OCR seleccionado
    updateOcrType: function(event) {
        console.log("Tipo de OCR cambiado a:", event.target.value);
    },
    
    // Procesar archivo para OCR
    processFile: function() {
        if (this.processing) {
            console.log("Ya hay un procesamiento en curso");
            return;
        }
        
        const fileInput = document.querySelector('input[type="file"]');
        if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
            console.error("No se seleccionó ningún archivo");
            this.showError("Por favor seleccione un archivo");
            return;
        }
        
        const file = fileInput.files[0];
        if (!this.validateFile(file)) {
            return;
        }
        
        this.setProcessingState(true);
        this.uploadFile(file);
    },
    
    // Validar tipo y tamaño de archivo
    validateFile: function(file) {
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
        const maxSize = 16 * 1024 * 1024; // 16MB
        
        if (!allowedTypes.includes(file.type)) {
            this.showError("Tipo de archivo no permitido. Use PNG, JPG o PDF.");
            return false;
        }
        
        if (file.size > maxSize) {
            this.showError("El archivo excede el tamaño máximo de 16MB.");
            return false;
        }
        
        return true;
    },
    
    // Subir archivo al servidor
    uploadFile: function(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Determinar el endpoint correcto según el contexto
        const endpoint = window.location.pathname.includes('/upload') 
            ? '/process' 
            : '/api/notes/image';
        
        fetch(endpoint, {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Archivo procesado:", data);
            this.handleSuccess(data);
        })
        .catch(error => {
            console.error("Error al procesar archivo:", error);
            this.showError("Error al procesar archivo: " + error.message);
        })
        .finally(() => {
            this.setProcessingState(false);
        });
    },
    
    // Manejar respuesta exitosa
    handleSuccess: function(data) {
        // Redirigir o mostrar resultados según el contexto
        if (data.redirect) {
            window.location.href = data.redirect;
        } else if (data.text) {
            this.displayOcrResults(data);
        }
    },
    
    // Mostrar resultados del OCR
    displayOcrResults: function(data) {
        const resultsContainer = document.getElementById('ocr-results');
        if (resultsContainer) {
            resultsContainer.textContent = data.text;
            resultsContainer.classList.remove('hidden');
        }
    },
    
    // Mostrar mensaje de error
    showError: function(message) {
        const errorContainer = document.getElementById('error-message');
        if (errorContainer) {
            errorContainer.textContent = message;
            errorContainer.classList.remove('hidden');
            
            // Ocultar después de 5 segundos
            setTimeout(() => {
                errorContainer.classList.add('hidden');
            }, 5000);
        } else {
            alert(message);
        }
    },
    
    // Cambiar el estado de procesamiento y la UI
    setProcessingState: function(isProcessing) {
        this.processing = isProcessing;
        
        const processButton = document.getElementById('process-file-button');
        const loadingIndicator = document.getElementById('loading-indicator');
        
        if (processButton) {
            processButton.disabled = isProcessing;
            processButton.textContent = isProcessing ? "Procesando..." : "Procesar Archivo";
        }
        
        if (loadingIndicator) {
            if (isProcessing) {
                loadingIndicator.classList.remove('hidden');
            } else {
                loadingIndicator.classList.add('hidden');
            }
        }
    }
};

// Inicializar cuando la página cargue
document.addEventListener('DOMContentLoaded', () => {
    ocrHandler.init();
});
