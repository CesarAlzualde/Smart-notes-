import React, { useState } from 'react';
import FileUploader from './FileUploader';
import './NoteFileUploader.css';

interface UploadedFile {
  id?: string;
  file: File;
  preview?: string;
  progress: number;
}

interface NoteFileUploaderProps {
  sourceType: string;
  onFileSelect: (file: File) => Promise<void>;
}

const NoteFileUploader: React.FC<NoteFileUploaderProps> = ({ sourceType, onFileSelect }) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Definimos tipos para la configuración del uploader
  type FileUploaderConfig = {
    accept: string;
    maxSize: number;
    multiple: boolean;
    hidden?: boolean;
  };

  type HiddenConfig = {
    hidden: boolean;
  };

  // Mapeo de tipo de fuente a configuración de uploader
  const uploaderConfig: Record<string, FileUploaderConfig | HiddenConfig> = {
    'PDF': {
      accept: 'application/pdf',
      maxSize: 10485760, // 10MB
      multiple: false,
    },
    'OCR': {
      accept: 'image/*',
      maxSize: 5242880, // 5MB
      multiple: false,
    },
    'URL': {
      hidden: true,
    },
    'Texto': {
      hidden: true,
    }
  };

  const config = uploaderConfig[sourceType] || { hidden: true };

  // Si es tipo URL o Texto, no mostramos el uploader
  if ('hidden' in config && config.hidden) {
    return null;
  }

  const handleFileSelected = async (file: File) => {
    try {
      // Crear un ID único para este archivo
      const fileId = Date.now().toString();
      
      // Crear un objeto URL para la previsualización si es una imagen
      let preview = undefined;
      if (file.type.startsWith('image/')) {
        preview = URL.createObjectURL(file);
      }
      
      // Añadir archivo a la lista con progreso inicial
      const newFile: UploadedFile = {
        id: fileId,
        file,
        preview,
        progress: 0
      };
      
      setUploadedFiles([...uploadedFiles, newFile]);
      setIsUploading(true);
      setError(null);
      
      // Simular progreso de carga
      const updateProgress = setInterval(() => {
        setUploadedFiles(prevFiles => 
          prevFiles.map(prevFile => 
            prevFile.id === fileId 
              ? {...prevFile, progress: Math.min(prevFile.progress + 10, 90)} 
              : prevFile
          )
        );
      }, 300);
      
      // Procesar el archivo
      await onFileSelect(file);
      
      // Actualizar progreso a 100%
      clearInterval(updateProgress);
      setUploadedFiles(prevFiles => 
        prevFiles.map(prevFile => 
          prevFile.id === fileId 
            ? {...prevFile, progress: 100} 
            : prevFile
        )
      );
      
      setIsUploading(false);
    } catch (err) {
      console.error('Error al procesar archivo:', err);
      setError('Error al procesar el archivo. Inténtalo de nuevo.');
      setIsUploading(false);
    }
  };

  const handleRemoveFile = (fileId: string) => {
    // Liberar URL de previsualización para evitar pérdidas de memoria
    const fileToRemove = uploadedFiles.find(f => f.id === fileId);
    if (fileToRemove?.preview) {
      URL.revokeObjectURL(fileToRemove.preview);
    }
    
    // Eliminar archivo de la lista
    setUploadedFiles(uploadedFiles.filter(f => f.id !== fileId));
  };

  return (
    <div className="note-file-uploader">
      {uploadedFiles.length === 0 ? (
        <FileUploader 
          onFileSelect={handleFileSelected}
          accept={'accept' in config ? config.accept : undefined}
          multiple={'multiple' in config ? config.multiple : false}
          maxSize={'maxSize' in config ? config.maxSize : undefined}
        />
      ) : (
        <div className="upload-summary">
          {uploadedFiles.map(file => (
            <div className="uploaded-file" key={file.id}>
              <div className="file-preview">
                {file.preview ? (
                  <img src={file.preview} alt={file.file.name} className="preview-thumbnail" />
                ) : (
                  <div className="file-icon">
                    <i className={file.file.type.includes('pdf') ? 'far fa-file-pdf' : 'far fa-file'}></i>
                  </div>
                )}
                <div className="file-info">
                  <div className="file-name">{file.file.name}</div>
                  <div className="file-size">{(file.file.size / 1024).toFixed(1)} KB</div>
                  <div className="upload-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-indicator" 
                        style={{ width: `${file.progress}%` }}
                      ></div>
                    </div>
                    <div className="progress-text">
                      <span>{file.progress}%</span>
                      <span>{file.progress === 100 ? 'Completado' : 'Procesando...'}</span>
                    </div>
                  </div>
                </div>
                <button 
                  className="remove-file" 
                  onClick={() => handleRemoveFile(file.id!)}
                  disabled={file.progress < 100}
                >
                  <i className="fas fa-times"></i>
                </button>
              </div>
            </div>
          ))}
          
          {uploadedFiles.length > 0 && !isUploading && (
            <button 
              className="upload-another" 
              onClick={() => setUploadedFiles([])}
            >
              <i className="fas fa-plus"></i> Subir otro archivo
            </button>
          )}
        </div>
      )}
      
      {error && (
        <div className="upload-error">
          <i className="fas fa-exclamation-circle"></i> {error}
        </div>
      )}
    </div>
  );
};

export default NoteFileUploader;
