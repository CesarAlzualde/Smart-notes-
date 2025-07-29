/**
 * Gestión básica de notas en el frontend
 * Proyecto Apuntes - Módulo para interacción con notas
 */

class NotesManager {
    constructor() {
        this.notes = [];
        this.tags = [];
        this.currentNote = null;
        this.apiBase = '/api';
        this.initialized = false;
    }

    /**
     * Obtiene los headers de autenticación con el token JWT
     * @returns {Object} Headers con autenticación
     */
    getAuthHeaders() {
        const token = localStorage.getItem('auth_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }
        
        return headers;
    }

    /**
     * Inicializa el gestor de notas
     * @returns {Promise} Promesa que se resuelve cuando se completa la inicialización
     */
    async initialize() {
        if (this.initialized) return;
        
        try {
            // Cargar datos iniciales necesarios
            await Promise.all([
                this.loadTags(),
                this.loadRecentNotes()
            ]);
            
            this.initialized = true;
            console.log('NotesManager inicializado correctamente');
            
            // Disparar evento de inicialización
            document.dispatchEvent(new CustomEvent('notesManager:initialized'));
        } catch (error) {
            console.error('Error al inicializar NotesManager:', error);
            // Reintento automático después de un retraso
            setTimeout(() => {
                if (!this.initialized) {
                    this.initialize();
                }
            }, 5000);
        }
    }

    /**
     * Carga las etiquetas disponibles
     * @returns {Promise} Promesa con las etiquetas
     */
    async loadTags() {
        try {
            const response = await fetch(`${this.apiBase}/tags`, {
                headers: this.getAuthHeaders()
            });
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            const data = await response.json();
            this.tags = data.tags || [];
            return this.tags;
        } catch (error) {
            console.error('Error al cargar etiquetas:', error);
            return [];
        }
    }

    /**
     * Carga las notas recientes
     * @param {number} limit - Número máximo de notas a cargar
     * @returns {Promise} Promesa con las notas recientes
     */
    async loadRecentNotes(limit = 5) {
        try {
            const response = await fetch(`${this.apiBase}/notes/recent?limit=${limit}`, {
                headers: this.getAuthHeaders()
            });
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            const data = await response.json();
            this.notes = data.notes || [];
            return this.notes;
        } catch (error) {
            console.error('Error al cargar notas recientes:', error);
            return [];
        }
    }

    /**
     * Obtiene una nota por su ID
     * @param {string} noteId - ID de la nota
     * @returns {Promise} Promesa con los datos de la nota
     */
    async getNote(noteId) {
        try {
            const response = await fetch(`${this.apiBase}/notes/${noteId}`);
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            const note = await response.json();
            this.currentNote = note;
            return note;
        } catch (error) {
            console.error(`Error al obtener nota ${noteId}:`, error);
            return null;
        }
    }

    /**
     * Guarda una nota (nueva o existente)
     * @param {Object} noteData - Datos de la nota a guardar
     * @returns {Promise} Promesa con la nota guardada
     */
    async saveNote(noteData) {
        try {
            const isNewNote = !noteData.id;
            const url = isNewNote ? `${this.apiBase}/notes` : `${this.apiBase}/notes/${noteData.id}`;
            const method = isNewNote ? 'POST' : 'PUT';
            
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(noteData)
            });
            
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            const savedNote = await response.json();
            
            // Actualizar la nota en la lista local si ya existe
            if (!isNewNote) {
                const index = this.notes.findIndex(note => note.id === savedNote.id);
                if (index !== -1) {
                    this.notes[index] = savedNote;
                } else {
                    // Añadir al principio si es nueva o no estaba en la lista
                    this.notes.unshift(savedNote);
                }
            } else {
                // Si es nueva, añadirla al principio
                this.notes.unshift(savedNote);
            }
            
            return savedNote;
        } catch (error) {
            console.error('Error al guardar nota:', error);
            throw error;
        }
    }

    /**
     * Elimina una nota
     * @param {string} noteId - ID de la nota a eliminar
     * @returns {Promise} Promesa que se resuelve cuando la nota ha sido eliminada
     */
    async deleteNote(noteId) {
        try {
            const response = await fetch(`${this.apiBase}/notes/${noteId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            // Eliminar la nota de la lista local
            this.notes = this.notes.filter(note => note.id !== noteId);
            
            // Si la nota actual era la eliminada, resetear
            if (this.currentNote && this.currentNote.id === noteId) {
                this.currentNote = null;
            }
            
            return true;
        } catch (error) {
            console.error(`Error al eliminar nota ${noteId}:`, error);
            throw error;
        }
    }

    /**
     * Busca notas según criterios
     * @param {Object} criteria - Criterios de búsqueda (texto, etiquetas, etc.)
     * @returns {Promise} Promesa con las notas encontradas
     */
    async searchNotes(criteria = {}) {
        try {
            // Construir parámetros de consulta
            const params = new URLSearchParams();
            
            if (criteria.query) params.append('q', criteria.query);
            if (criteria.tags && criteria.tags.length) {
                criteria.tags.forEach(tag => params.append('tag', tag));
            }
            if (criteria.startDate) params.append('start_date', criteria.startDate);
            if (criteria.endDate) params.append('end_date', criteria.endDate);
            if (criteria.limit) params.append('limit', criteria.limit);
            
            const response = await fetch(`${this.apiBase}/notes/search?${params.toString()}`);
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            const data = await response.json();
            return data.notes || [];
        } catch (error) {
            console.error('Error en búsqueda de notas:', error);
            return [];
        }
    }

    /**
     * Extrae conceptos clave del contenido de una nota
     * @param {string} content - Contenido de texto de la nota
     * @returns {Array} Lista de conceptos extraídos
     */
    extractConcepts(content) {
        if (!content || typeof content !== 'string' || content.length < 50) {
            return [];
        }
        
        try {
            // Usar TextAnalyzer si está disponible
            console.warn('TextAnalyzer no está disponible, usando fallback.');
            return [];
        } catch (error) {
            console.error('Error al extraer conceptos:', error);
            return [];
        }
    }

    /**
     * Devuelve estadísticas de las notas
     * @returns {Promise} Promesa con estadísticas
     */
    async getNotesStatistics() {
        try {
            const response = await fetch(`${this.apiBase}/notes/statistics`);
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            return await response.json();
        } catch (error) {
            console.error('Error al obtener estadísticas:', error);
            return {
                total: 0,
                by_month: {},
                by_category: {},
                average_length: 0
            };
        }
    }
}

// Instanciar el gestor de notas para uso global
const notesManager = new NotesManager();

// Inicializar automáticamente cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    notesManager.initialize();
});
