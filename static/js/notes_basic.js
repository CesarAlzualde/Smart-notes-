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
     * Inicializa el gestor de notas
     * @returns {Promise} Promesa que se resuelve cuando se completa la inicialización
     */
    async initialize() {
        if (this.initialized) return;
        
        try {
            // Verificar si hay un token de autenticación antes de intentar cargar datos
            const token = localStorage.getItem('auth_token');
            
            if (token) {
                // Solo cargar datos si hay un token
                console.log('Token encontrado, cargando datos...');
                await Promise.all([
                    this.loadTags(),
                    this.loadRecentNotes()
                ]);
            } else {
                console.log('No hay token de autenticación. No se cargarán datos hasta que el usuario inicie sesión.');
                // No intentamos cargar datos, pero marcamos como inicializado para evitar intentos repetidos
            }
            
            this.initialized = true;
            console.log('NotesManager inicializado correctamente');
            
            // Disparar evento de inicialización
            document.dispatchEvent(new CustomEvent('notesManager:initialized'));
        } catch (error) {
            console.error('Error al inicializar NotesManager:', error);
            // Reintento automático después de un retraso, pero solo si es un error diferente a 401
            if (error.status !== 401) {
                setTimeout(() => {
                    if (!this.initialized) {
                        this.initialize();
                    }
                }, 5000);
            } else {
                // Si es un error 401, simplemente marcamos como inicializado y esperamos a que el usuario inicie sesión
                this.initialized = true;
                console.log('NotesManager: Esperando autenticación del usuario.');
            }
        }
    }

    /**
     * Carga las etiquetas disponibles
     * @returns {Promise} Promesa con las etiquetas
     */
    async loadTags() {
        try {
            const response = await fetch(`${this.apiBase}/tags`);
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            const data = await response.json();
            // Asegurarnos de que data.tags es un array o usar un array vacío si es null
            this.tags = Array.isArray(data.tags) ? data.tags : [];
            console.log('Tags cargados:', this.tags.length);
            return this.tags;
        } catch (error) {
            console.error('Error al cargar etiquetas:', error);
            this.tags = [];
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
            const response = await fetch(`${this.apiBase}/notes/recent?limit=${limit}`);
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            
            const data = await response.json();
            // Verificar que data.notes sea un array válido
            if (Array.isArray(data.notes)) {
                this.notes = data.notes;
                console.log(`Notas recientes cargadas: ${this.notes.length}`, this.notes);
            } else {
                console.warn('La respuesta no contiene un array de notas válido:', data);
                this.notes = [];
            }
            
            // Actualizar la interfaz de usuario si existe el elemento DOM
            this.updateNotesDisplay();
            
            return this.notes;
        } catch (error) {
            console.error('Error al cargar notas recientes:', error);
            this.notes = [];
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
            console.log('Nota guardada exitosamente:', savedNote);
            
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
            
            // Actualizar interfaz de usuario con las notas actualizadas
            this.updateNotesDisplay();
            
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
            
            // Actualizar la interfaz
            this.updateNotesDisplay();
            
            return true;
        } catch (error) {
            console.error(`Error al eliminar nota ${noteId}:`, error);
            throw error;
        }
    }

    /**
     * Actualiza la interfaz de usuario con las notas cargadas
     * Busca los elementos DOM relevantes y los actualiza
     */
    updateNotesDisplay() {
        // Buscar el contenedor de notas recientes si existe
        const recentNotesContainer = document.getElementById('recent-notes-container');
        if (recentNotesContainer && this.notes && this.notes.length > 0) {
            console.log('Actualizando vista de notas recientes...');
            
            // Limpiar el contenedor
            recentNotesContainer.innerHTML = '';
            
            // Crear elementos para cada nota
            this.notes.forEach(note => {
                // Crear elemento de nota
                const noteElement = document.createElement('div');
                noteElement.className = 'note-item';
                noteElement.dataset.id = note.id;
                
                // Formato de fecha
                const date = new Date(note.created_at || note.updated_at || Date.now());
                const formattedDate = date.toLocaleDateString('es-ES', { 
                    day: '2-digit', 
                    month: '2-digit', 
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                // Contenido de la nota (título, texto, fecha)
                noteElement.innerHTML = `
                    <div class="note-header">
                        <h3>${note.title || 'Nota sin título'}</h3>
                        <span class="note-date">${formattedDate}</span>
                    </div>
                    <p class="note-preview">${(note.content || '').substring(0, 100)}${note.content && note.content.length > 100 ? '...' : ''}</p>
                    <div class="note-actions">
                        <button class="btn-view" data-id="${note.id}">Ver</button>
                        <button class="btn-edit" data-id="${note.id}">Editar</button>
                        <button class="btn-delete" data-id="${note.id}">Eliminar</button>
                    </div>
                `;
                
                // Añadir al contenedor
                recentNotesContainer.appendChild(noteElement);
                
                // Agregar eventos a los botones (si es necesario)
                const viewBtn = noteElement.querySelector('.btn-view');
                if (viewBtn) viewBtn.addEventListener('click', () => this.viewNote(note.id));
                
                const editBtn = noteElement.querySelector('.btn-edit');
                if (editBtn) editBtn.addEventListener('click', () => this.editNote(note.id));
                
                const deleteBtn = noteElement.querySelector('.btn-delete');
                if (deleteBtn) deleteBtn.addEventListener('click', () => this.confirmDeleteNote(note.id));
            });
        } else if (recentNotesContainer) {
            recentNotesContainer.innerHTML = '<p class="no-notes">No hay notas recientes</p>';
        }
        
        // Actualizar contador de notas si existe
        const notesCounter = document.getElementById('notes-counter');
        if (notesCounter) {
            notesCounter.textContent = this.notes ? this.notes.length : 0;
        }
    }

    /**
     * Ver una nota - navegar a la página de detalles
     * @param {string} noteId - ID de la nota a ver
     */
    viewNote(noteId) {
        window.location.href = `/note/${noteId}`;
    }
    
    /**
     * Editar una nota - abrir el editor
     * @param {string} noteId - ID de la nota a editar
     */
    editNote(noteId) {
        window.location.href = `/edit/${noteId}`;
    }
    
    /**
     * Confirmar eliminación de nota
     * @param {string} noteId - ID de la nota a eliminar
     */
    confirmDeleteNote(noteId) {
        if (confirm('¿Está seguro de que desea eliminar esta nota? Esta acción no se puede deshacer.')) {
            this.deleteNote(noteId)
                .then(() => {
                    alert('Nota eliminada correctamente');
                    // Actualizar la lista de notas
                    this.loadRecentNotes();
                })
                .catch(error => {
                    alert('Error al eliminar la nota: ' + error.message);
                });
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
            if (typeof TextAnalyzer !== 'undefined') {
                return TextAnalyzer.extractKeyConcepts(content);
            } else {
                console.warn('TextAnalyzer no está disponible');
                return [];
            }
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
