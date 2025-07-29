/**
 * Funciones para análisis de texto, extracción de conceptos y visualización de temas
 * Proyecto Apuntes - Módulo para análisis avanzado de contenido
 */

class TextAnalyzer {
    /**
     * Calcula estadísticas básicas del texto proporcionado
     * @param {string} text - Texto a analizar
     * @returns {object} Objeto con estadísticas
     */
    static getTextStats(text) {
        try {
            // Validación robusta del texto de entrada
            if (!text || typeof text !== 'string') {
                return { words: 0, paragraphs: 0, readingTime: 0, readability: 0 };
            }
            
            // Copia segura del texto
            const safeText = String(text);
            
            // Contar palabras (eliminar espacios múltiples y dividir)
            const wordCount = safeText.trim().split(/\s+/).length;
            
            // Contar párrafos (separados por líneas vacías)
            const paragraphCount = safeText.split(/\n\s*\n/).filter(Boolean).length || 1;
            
            // Estimar tiempo de lectura (200 palabras por minuto)
            const readingTime = Math.max(1, Math.ceil(wordCount / 200));
            
            // Calcular legibilidad aproximada (Flesch Reading Ease simplificado adaptado al español)
            // Simplificación: longitud promedio de palabras y sentencias
            const sentences = safeText.split(/[.!?]+/).filter(Boolean).length || 1;
            const avgWordsPerSentence = wordCount / sentences;
            
            // Reemplazar espacios de forma segura
            let chars = 0;
            try {
                // Intentar el reemplazo de forma segura
                chars = safeText.replace(/\s+/g, '').length;
            } catch (e) {
                console.error('Error al reemplazar espacios:', e);
                chars = safeText.length; // Usar la longitud original como fallback
            }
            
            const avgCharsPerWord = chars / wordCount || 5;
            
            // Valor entre 0-100, donde mayor número = más fácil de leer
            // Esta es una aproximación simplificada
            let readability = Math.max(0, Math.min(100, 
                206.835 - (1.015 * avgWordsPerSentence) - (60.0 * avgCharsPerWord / 5)
            ));
            
            return {
                words: wordCount,
                paragraphs: paragraphCount,
                readingTime,
                readability,
                avgWordsPerSentence,
                avgCharsPerWord
            };
        } catch (error) {
            console.error('Error en cálculo de estadísticas:', error);
            return { words: 0, paragraphs: 0, readingTime: 0, readability: 0 };
        }
    }
    
    /**
     * Analiza el tono predominante del texto
     * @param {string} text - Texto a analizar
     * @returns {string} Tono estimado
     */
    static analyzeTone(text) {
        if (!text || text.length < 20) return 'Neutral';
        
        // Palabras asociadas a diferentes tonos (simplificado)
        const tones = {
            formal: ['debe', 'concluir', 'analizar', 'según', 'estudio', 'investigación', 'determinar'],
            informal: ['quizás', 'bueno', 'genial', 'super', 'wow', 'hey', 'cool'],
            academic: ['teoría', 'metodología', 'hipótesis', 'análisis', 'estudio', 'investigación', 'paradigma'],
            technical: ['sistema', 'proceso', 'método', 'función', 'algoritmo', 'protocolo', 'interfaz'],
            emotional: ['siento', 'creo', 'amo', 'odio', 'triste', 'feliz', 'emoción']
        };
        
        // Contar apariciones de palabras de cada tono
        const textLower = text.toLowerCase();
        const counts = {};
        
        for (const [tone, keywords] of Object.entries(tones)) {
            counts[tone] = keywords.reduce((sum, keyword) => {
                const regex = new RegExp('\\b' + keyword + '\\b', 'gi');
                return sum + (textLower.match(regex) || []).length;
            }, 0);
        }
        
        // Determinar el tono predominante
        let maxTone = 'neutral';
        let maxCount = 0;
        
        for (const [tone, count] of Object.entries(counts)) {
            if (count > maxCount) {
                maxCount = count;
                maxTone = tone;
            }
        }
        
        // Si no hay un tono claro, devolver neutral
        return maxCount > 0 ? maxTone.charAt(0).toUpperCase() + maxTone.slice(1) : 'Neutral';
    }
    
    /**
     * Extrae conceptos clave del texto
     * @param {string} text - Texto del que extraer conceptos
     * @returns {array} Lista de conceptos clave
     */
    static extractKeyConcepts(text) {
        // Verificación robusta de que el texto existe y es una cadena válida
        if (!text || typeof text !== 'string' || text.length < 50) {
            return [];
        }
        
        try {
            // Eliminar palabras comunes (stop words en español)
            const stopWords = new Set([
                'a', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'como', 'con', 'contra',
                'cual', 'cuando', 'de', 'del', 'desde', 'donde', 'durante', 'e', 'el', 'ella',
                'ellas', 'ellos', 'en', 'entre', 'era', 'erais', 'eran', 'eras', 'eres', 'es',
                'esa', 'esas', 'ese', 'eso', 'esos', 'esta', 'estaba', 'estado', 'estáis', 'estamos',
                'están', 'estar', 'estas', 'este', 'esto', 'estos', 'estoy', 'etc', 'fue', 'fuera',
                'fueron', 'fui', 'fuimos', 'ha', 'hace', 'hacéis', 'hacemos', 'hacen', 'hacer', 'haces',
                'hacia', 'hago', 'hasta', 'hay', 'he', 'hemos', 'hice', 'hizo', 'la', 'las',
                'le', 'les', 'lo', 'los', 'me', 'mi', 'mía', 'mías', 'mientras', 'mío',
                'míos', 'mis', 'mucho', 'muchos', 'muy', 'ni', 'no', 'nos', 'nosotras', 'nosotros',
                'nuestra', 'nuestras', 'nuestro', 'nuestros', 'o', 'os', 'otra', 'otras', 'otro', 'otros',
                'para', 'pero', 'poco', 'por', 'porque', 'que', 'quien', 'quienes', 'qué', 'se',
                'sea', 'seáis', 'sean', 'seas', 'ser', 'si', 'sí', 'sido', 'siendo', 'sin',
                'sobre', 'sois', 'somos', 'son', 'soy', 'su', 'sus', 'suya', 'suyas', 'suyo',
                'suyos', 'también', 'tanto', 'te', 'tenéis', 'tenemos', 'tener', 'tengo', 'ti', 'tiene',
                'tienen', 'toda', 'todas', 'todo', 'todos', 'tu', 'tus', 'tú', 'un', 'una',
                'uno', 'unos', 'vosotras', 'vosotros', 'vuestra', 'vuestras', 'vuestro', 'vuestros', 'y', 'ya',
                'yo', 'él', 'ésta', 'éstas', 'éste', 'éstos'
            ]);
            
            // Normalizar texto y dividir en palabras - con verificación adicional de seguridad
            const cleanedText = (text || '').toLowerCase();
            const words = cleanedText
                .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, '')
                .split(/\s+/);
            
            // Contar frecuencias de palabras omitiendo stop words
            const wordFrequency = {};
            for (const word of words) {
                if (word && word.length > 3 && !stopWords.has(word)) {
                    wordFrequency[word] = (wordFrequency[word] || 0) + 1;
                }
            }
            
            // Extraer bigramas (frases de dos palabras)
            const bigramFrequency = {};
            for (let i = 0; i < words.length - 1; i++) {
                const word1 = words[i];
                const word2 = words[i + 1];
                
                // Verificaciones adicionales antes de procesar los bigramas
                if (word1 && word2 && 
                    word1.length > 3 && word2.length > 3 && 
                    !stopWords.has(word1) && !stopWords.has(word2)) {
                    const bigram = `${word1} ${word2}`;
                    bigramFrequency[bigram] = (bigramFrequency[bigram] || 0) + 1;
                }
            }
        
            // Combinar palabras y bigramas, y ordenar por frecuencia
            const allTerms = [...Object.entries(wordFrequency), ...Object.entries(bigramFrequency)]
                .sort((a, b) => b[1] - a[1])
                .slice(0, 20)  // Tomar los 20 más frecuentes
                .map(entry => ({
                    concept: entry[0],
                    frequency: entry[1]
                }));
            
            // Limitar a los 10 conceptos más relevantes
            return allTerms.slice(0, 10);
        } catch (error) {
            console.error('Error al extraer conceptos clave:', error);
            return []; // Devolver array vacío en caso de error
        }
    }
    
    /**
     * Calcula una descripción de legibilidad según el puntaje
     * @param {number} score - Puntuación de legibilidad (0-100)
     * @returns {string} Descripción de legibilidad
     */
    static getReadabilityLabel(score) {
        if (score >= 90) return 'Muy fácil de leer';
        if (score >= 80) return 'Fácil de leer';
        if (score >= 70) return 'Bastante fácil';
        if (score >= 60) return 'Estándar';
        if (score >= 50) return 'Medianamente difícil';
        if (score >= 30) return 'Difícil de leer';
        return 'Muy difícil';
    }
}

class TopicsVisualizer {
    /**
     * Crea visualización HTML para distribución de temas
     * @param {array} topics - Lista de temas con puntuaciones
     * @returns {string} HTML para visualizar la distribución
     */
    static createTopicsDistribution(topics) {
        if (!topics || !topics.length) return '<div class="text-muted">No hay datos disponibles</div>';
        
        // Ordenar temas por puntuación
        const sortedTopics = [...topics].sort((a, b) => b.score - a.score);
        let html = '';
        
        // Crear barras de distribución para cada tema
        sortedTopics.forEach(topic => {
            const percentage = Math.round(topic.score * 100);
            const barColor = this.getTopicColor(topic.name);
            
            html += `
            <div class="topic-bar mb-2">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <small>${topic.name}</small>
                    <small class="text-muted">${percentage}%</small>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar" role="progressbar" 
                         style="width: ${percentage}%; background-color: ${barColor};" 
                         aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
            </div>`;
        });
        
        return html;
    }
    
    /**
     * Genera color para un tema específico
     * @param {string} topic - Nombre del tema
     * @returns {string} Color en formato hexadecimal
     */
    static getTopicColor(topic) {
        // Colores predefinidos para temas comunes
        const topicColors = {
            'Tecnología': '#3498db',
            'Ciencia': '#2ecc71',
            'Historia': '#e67e22',
            'Arte': '#9b59b6',
            'Literatura': '#34495e',
            'Filosofía': '#8e44ad',
            'Matemáticas': '#1abc9c',
            'Medicina': '#e74c3c',
            'Economía': '#f1c40f',
            'Política': '#d35400',
            'Deportes': '#16a085',
            'Música': '#27ae60',
            'Cine': '#7f8c8d',
            'Psicología': '#c0392b',
            'Educación': '#2980b9'
        };
        
        // Si el tema está en nuestra lista de colores predefinidos, usar ese color
        if (topicColors[topic]) {
            return topicColors[topic];
        }
        
        // Generar un color basado en el nombre del tema (consistente)
        let hash = 0;
        for (let i = 0; i < topic.length; i++) {
            hash = topic.charCodeAt(i) + ((hash << 5) - hash);
        }
        
        // Convertir el hash a un color hexadecimal
        let color = '#';
        for (let i = 0; i < 3; i++) {
            const value = (hash >> (i * 8)) & 0xFF;
            color += ('00' + value.toString(16)).substr(-2);
        }
        
        return color;
    }
    
    /**
     * Genera HTML para mostrar temas relacionados como badges
     * @param {array} topics - Lista de temas relacionados
     * @returns {string} HTML con badges de temas
     */
    static createTopicBadges(topics) {
        if (!topics || !topics.length) return '<span class="text-muted">Sin temas relacionados</span>';
        
        return topics.map(topic => {
            const color = this.getTopicColor(topic);
            return `<span class="badge rounded-pill" style="background-color: ${color};">${topic}</span>`;
        }).join(' ');
    }
}

// Exportar clases para uso global
window.TextAnalyzer = TextAnalyzer;
window.TopicsVisualizer = TopicsVisualizer;
