import React, { useState, useRef } from 'react';
import './FileUploader.css';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  multiple?: boolean;
  maxSize?: number; // en bytes
  className?: string;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  onFileSelect,
  accept = 'image/*,application/pdf',
  multiple = false,
  maxSize = 10485760, // 10MB por defecto
  className = ''
}) => {
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragging) {
      setIsDragging(true);
    }
  };

  const validateFile = (file: File): boolean => {
    // Validar tamaño del archivo
    if (maxSize && file.size > maxSize) {
      setError(`El archivo es demasiado grande. Tamaño máximo: ${(maxSize / (1024 * 1024)).toFixed(2)}MB`);
      return false;
    }

    // Validar tipo de archivo si accept está especificado
    if (accept) {
      const acceptedTypes = accept.split(',').map(type => type.trim());
      const fileType = file.type;
      
      // Verificar si el tipo de archivo está permitido
      const isAccepted = acceptedTypes.some(type => {
        if (type.includes('*')) {
          // Para casos como "image/*"
          return fileType.startsWith(type.split('*')[0]);
        }
        return type === fileType;
      });

      if (!isAccepted) {
        setError(`Tipo de archivo no permitido. Por favor, sube un archivo de tipo: ${accept}`);
        return false;
      }
    }

    // Si pasó todas las validaciones
    setError(null);
    return true;
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const files = e.dataTransfer.files;
      handleFiles(files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = e.target.files;
      handleFiles(files);
    }
  };

  const handleFiles = (files: FileList) => {
    if (!multiple && files.length > 1) {
      setError('Solo se permite un archivo');
      return;
    }

    const validFiles: File[] = [];

    for (let i = 0; i < files.length; i++) {
      if (validateFile(files[i])) {
        validFiles.push(files[i]);
      }
    }

    if (validFiles.length > 0) {
      if (multiple) {
        validFiles.forEach(file => onFileSelect(file));
      } else {
        onFileSelect(validFiles[0]);
      }

      // Limpiar el input para poder seleccionar el mismo archivo de nuevo si es necesario
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleClickUpload = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className={`file-uploader ${className}`}>
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''}`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClickUpload}
      >
        <div className="upload-icon">
          <i className="fas fa-cloud-upload-alt"></i>
        </div>
        <div className="upload-text">
          <p>Arrastra y suelta aquí o <span className="upload-link">busca en tu dispositivo</span></p>
          <span className="upload-hint">
            {multiple ? 'Puedes subir varios archivos' : 'Sube un archivo'} 
            {accept !== '*' ? ` (${accept.replace('image/*', 'imágenes').replace('application/pdf', 'PDF')})` : ''}
            {maxSize ? ` hasta ${(maxSize / (1024 * 1024)).toFixed(2)}MB` : ''}
          </span>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          className="file-input"
          onChange={handleFileInput}
          accept={accept}
          multiple={multiple}
        />
      </div>
      
      {error && (
        <div className="upload-error">
          <i className="fas fa-exclamation-circle"></i> {error}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
