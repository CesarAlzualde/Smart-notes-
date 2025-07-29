import apiClient from './client';
import type { OcrResult } from '../types/files';

interface OCROptions {
  engine?: string; // tesseract, easyocr, etc.
  language?: string; // eng, spa, etc.
  preprocessing?: boolean;
  isWhiteboard?: boolean; // Indica si es una imagen de pizarra o dibujo a mano
}

interface UploadResponseData {
  id?: string;           // ID del archivo subido
  file_id?: string;      // Alternativa al ID
  filename: string;      // Nombre del archivo
  path: string;          // Ruta del archivo
  mimetype: string;      // Tipo MIME
  size: number;          // Tamaño en bytes
  thumbnail_url?: string; // URL de la miniatura
  ocr_result?: string;   // ID o token del resultado OCR
}

interface GoogleVisionAvailability {
  available: boolean;
  error_reason?: string;
  troubleshooting?: string[];
  error?: string;
}

interface CreateNoteOptions {
  is_whiteboard?: boolean;
  summary_id?: string;
  main_topic?: string;
  tags?: string[];
}

interface BackendOCROptions {
  engine?: string;
  language?: string;
  preprocessing?: boolean;
  is_whiteboard?: boolean;
}

export const filesApi = {
  uploadFile: async (file: File, options: OCROptions = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options.engine) {
      formData.append('engine', options.engine);
    }
    
    if (options.language) {
      formData.append('language', options.language);
    }
    
    if (options.preprocessing !== undefined) {
      formData.append('preprocessing', options.preprocessing.toString());
    }
    
    // Corregido para usar la ruta API correcta
    const response = await apiClient.post('/api/files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data as UploadResponseData;
  },
  
  processOCR: async (fileId: string, options: OCROptions = {}): Promise<{ taskId: string }> => {
    console.log(`Iniciando procesamiento OCR para archivo con ID: ${fileId}`);

    const { isWhiteboard, ...restOptions } = options;

    const backendOptions: BackendOCROptions = {
      ...restOptions,
    };

    if (isWhiteboard !== undefined) {
      backendOptions.is_whiteboard = isWhiteboard;
    }

    const response = await apiClient.post(`/api/files/${fileId}/process`, backendOptions);
    return response.data; // Devuelve { message, task_id, status_url }
  },

  getTaskStatus: async (taskId: string) => {
    const response = await apiClient.get(`/api/tasks/${taskId}/status`);
    return response.data; // Devuelve el estado y resultado de la tarea
  },

  checkGoogleVisionAvailable: async (): Promise<GoogleVisionAvailability> => {
    try {
      const response = await apiClient.get('/api/files/check-google-vision-available');
      return response.data as GoogleVisionAvailability;
    } catch (error) {
      console.error('Error checking Google Vision availability:', error);
      return { 
        available: false,
        error: error instanceof Error ? error.message : 'Error desconocido'
      };
    }
  },
  
  getAllFiles: async (page: number = 1, perPage: number = 20) => {
    const response = await apiClient.get('/api/files', { 
      params: { page, per_page: perPage } 
    });
    
    return response.data;
  },
  
  getFileById: async (id: number) => {
    const response = await apiClient.get(`/api/files/${id}`);
    return response.data;
  },
  
  deleteFile: async (id: number) => {
    const response = await apiClient.delete(`/api/files/${id}`);
    return response.data;
  },
  
  getFileStatistics: async () => {
    const response = await apiClient.get('/api/files/statistics');
    return response.data;
  },
  
  createNoteFromOCR: async (ocrResult: OcrResult, title: string, content: string, options: CreateNoteOptions = {}) => {
    const response = await apiClient.post('/api/files/create-note', {
      ocr_result: ocrResult, // Enviar el objeto OCR completo
      title,
      content, // Enviar el texto (potencialmente editado)
      ...options
    });
    
    return response.data;
  },

  createNoteFromFile: async (fileId: number, title: string, content: string, tags: string[] = []) => {
    const response = await apiClient.post('/api/notes/from-file', {
      file_id: fileId,
      title,
      content,
      tags,
    });
    return response.data;
  }
};
