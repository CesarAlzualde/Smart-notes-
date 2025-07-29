// Tipos relacionados con archivos y OCR
export interface OcrResult {
  text: string;
  confidence: number;
  filename?: string;
  thumbnail_url?: string;
  file_url?: string;
}

export interface FileUploadResult {
  filename: string;
  file_id: string;
  file_path: string;
  thumbnail_path?: string;
  ocr_status?: 'pending' | 'completed' | 'failed';
  ocr_id?: string;
}

export interface NoteCreationResponse {
  id: string;
  title: string;
  success: boolean;
  message?: string;
}

export interface File {
  id: number;
  filename: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  processed: boolean;
  processing_status: 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILED';
  extract_text: string | null;
  file_metadata: {
    size?: number;
    mime_type?: string;
    ocr_engine?: string;
    is_whiteboard?: boolean;
    error?: string;
  } | null;
}
