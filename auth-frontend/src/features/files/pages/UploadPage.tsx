import React, { useState, useMemo, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { filesApi } from '../../../api/files';
import { useNavigate } from 'react-router-dom';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './UploadPage.css';

const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const [ocrEngine, setOcrEngine] = useState<string>('tesseract');
  const [isWhiteboard, setIsWhiteboard] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [processingDetails, setProcessingDetails] = useState<string>('');
  const [checkingAvailability, setCheckingAvailability] = useState<boolean>(true);
  const [googleVisionError, setGoogleVisionError] = useState<{
    reason?: string;
    troubleshooting?: string[];
  } | null>(null);
  const navigate = useNavigate();

  // Verificar disponibilidad de Google Vision API al cargar el componente
  useEffect(() => {
    const checkGoogleVision = async () => {
      try {
        setCheckingAvailability(true);
        const response = await filesApi.checkGoogleVisionAvailable();
        
        if (!response.available) {
          setGoogleVisionError({
            reason: response.error_reason || response.error || 'Razón desconocida',
            troubleshooting: response.troubleshooting || [
              'Verifique que la API de Google Vision esté habilitada',
              'Asegúrese de que la variable GOOGLE_APPLICATION_CREDENTIALS esté configurada'
            ]
          });
          
          if (ocrEngine === 'google_vision') {
            setOcrEngine('tesseract');
          }
        } else {
          setGoogleVisionError(null);
        }
      } catch (error) {
        console.error('Error verificando Google Vision:', error);
        setGoogleVisionError({
          reason: error instanceof Error ? error.message : 'Error desconocido al verificar disponibilidad',
          troubleshooting: ['Revise la conexión al servidor']
        });
      } finally {
        setCheckingAvailability(false);
      }
    };
    
    checkGoogleVision();
  }, [ocrEngine]);

  const onDrop = useMemo(() => {
    return (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const currentFile = acceptedFiles[0];
        setFile(currentFile);

        if (currentFile.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onloadend = () => {
            setFilePreview(reader.result as string);
          };
          reader.readAsDataURL(currentFile);
        } else {
          setFilePreview(null); // No preview for non-image files like PDFs
        }
      }
    };
  }, []);

  const handleRemoveFile = () => {
    setFile(null);
    setFilePreview(null);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
  });

  const handleProcessFile = async () => {
    if (!file) {
      alert("Por favor, seleccione un archivo para procesar.");
      return;
    }

    setIsProcessing(true);
    setProcessingDetails('Subiendo archivo...');

    let pollInterval: NodeJS.Timeout | null = null;

    try {
      // 1. Subir el archivo
      const uploadResponse = await filesApi.uploadFile(file);
      if (!uploadResponse || !uploadResponse.id) {
        throw new Error('La subida del archivo no devolvió un ID válido.');
      }
      const fileId = parseInt(uploadResponse.id, 10);

      setProcessingDetails('Iniciando procesamiento OCR...');

      // 2. Iniciar el procesamiento OCR
      await filesApi.processOCR(fileId.toString(), { engine: ocrEngine, isWhiteboard });

      // 3. Empezar a sondear el estado
      setProcessingDetails('Procesamiento en curso, esperando resultado...');
      
      pollInterval = setInterval(async () => {
        try {
          const fileStatus = await filesApi.getFileById(fileId);
          if (fileStatus.processing_status === 'SUCCESS') {
            if (pollInterval) clearInterval(pollInterval);
            setProcessingDetails('¡Procesamiento completado!');
            navigate(`/ocr-preview/${fileId}?engine=${ocrEngine}`);
          } else if (fileStatus.processing_status === 'FAILED') {
            if (pollInterval) clearInterval(pollInterval);
            throw new Error('El procesamiento del archivo falló en el servidor.');
          }
        } catch (error) {
          if (pollInterval) clearInterval(pollInterval);
          console.error('Error durante el sondeo de estado:', error);
          alert(`Error al verificar el estado: ${error instanceof Error ? error.message : 'Error desconocido'}`);
          setIsProcessing(false);
        }
      }, 2000); // Sondear cada 2 segundos

      // Timeout para evitar sondeo infinito
      setTimeout(() => {
        if (pollInterval && pollInterval !== null) clearInterval(pollInterval);
        if (isProcessing) {
          setIsProcessing(false);
          alert('El procesamiento está tardando más de lo esperado. Por favor, revise el estado del archivo más tarde.');
        }
      }, 60000); // Timeout de 60 segundos

    } catch (error) {
      if (pollInterval && pollInterval !== null) {
        clearInterval(pollInterval);
      }
      console.error('Error durante el proceso de OCR:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Error desconocido'}`);
      setIsProcessing(false);
    }
  };

  return (
    <div className="container-fluid py-4">
      <h1 className="mb-4">Extraer Texto de Imágenes y PDFs</h1>

      <div className="row">
        <div className="col-md-8">
          <div className="card mb-4">
            <div className="card-header">
              <h5 className="card-title mb-0">Subir Archivo</h5>
            </div>
            <div className="card-body">
              <div {...getRootProps({ className: 'dropzone' })}>
                <input {...getInputProps()} />
                {isDragActive ? (
                  <p className="dz-message">Suelta el archivo aquí...</p>
                ) : (
                  <p className="dz-message">
                    Arrastra un archivo aquí o haz clic para seleccionarlo<br />
                    <small>Formatos aceptados: Imágenes (JPG, PNG, etc.) y PDF</small>
                  </p>
                )}
              </div>

              {file ? (
                <div className="text-center">
                  {filePreview && <img src={filePreview} alt="Previsualización" className="img-fluid file-preview-image" />}
                  <div className="file-info-container">
                    <p>{file.name}</p>
                    <button onClick={handleRemoveFile} className="btn btn-sm btn-outline-danger">Quitar</button>
                  </div>
                </div>
              ) : (
                <></>
              )}
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card mb-4">
            <div className="card-header">
              <h5 className="card-title mb-0">Opciones de OCR</h5>
            </div>
            <div className="card-body">
              <div className="form-group mb-3">
                <label htmlFor="ocrEngineSelect" className="form-label">Motor de OCR:</label>
                <select
                  id="ocrEngineSelect"
                  className="form-select"
                  value={ocrEngine}
                  onChange={(e) => setOcrEngine(e.target.value)}
                  disabled={checkingAvailability}
                >
                  <option value="tesseract">Tesseract (Local)</option>
                  {googleVisionError ? (
                    <option value="google_vision" disabled>Google Vision (No disponible)</option>
                  ) : checkingAvailability ? (
                    <option value="google_vision" disabled>Google Vision (Verificando disponibilidad...)</option>
                  ) : (
                    <option value="google_vision">Google Vision (Cloud - Mejor calidad)</option>
                  )}
                </select>
                
                {googleVisionError && (
                  <div className="alert alert-warning mt-2 google-vision-error-alert">
                    <p className="mb-1"><strong>Google Vision no está disponible:</strong> {googleVisionError.reason}</p>
                    {googleVisionError.troubleshooting && googleVisionError.troubleshooting.length > 0 && (
                      <>
                        <p className="mb-1"><strong>Sugerencias para solucionar:</strong></p>
                        <ul className="mb-0">
                          {googleVisionError.troubleshooting.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                )}
              </div>

              <fieldset className="mb-3">
                <legend className="form-label fs-6">Tipo de imagen:</legend>
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="imageType"
                    id="type_document"
                    value="document"
                    checked={!isWhiteboard}
                    onChange={() => setIsWhiteboard(false)}
                  />
                  <label className="form-check-label" htmlFor="type_document">
                    Documento impreso / libro
                  </label>
                </div>
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="imageType"
                    id="type_whiteboard"
                    value="whiteboard"
                    checked={isWhiteboard}
                    onChange={() => setIsWhiteboard(true)}
                  />
                  <label className="form-check-label" htmlFor="type_whiteboard">
                    Pizarra / notas a mano
                  </label>
                </div>
              </fieldset>

              <button
                type="button"
                className="btn btn-primary w-100"
                onClick={handleProcessFile}
                disabled={!file || isProcessing}
              >
                <i className="bi bi-gear-fill me-2"></i> Procesar Archivo
              </button>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">Información</h5>
            </div>
            <div className="card-body">
              <div className="mb-2">
                <p className="mb-1"><strong>Tipos de archivo soportados:</strong></p>
                <small>Imágenes: JPG, PNG, GIF, BMP, etc.</small><br />
                <small>Documentos: PDF</small>
              </div>
              <div>
                <p className="mb-1"><strong>Recomendaciones:</strong></p>
                <small>Use Tesseract para documentos simples y bien escaneados.</small><br />
                <small>Mejor calidad de OCR con Google Vision para pizarras y documentos complejos.</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay de procesamiento */}
      {isProcessing && (
        <div className="processing-overlay">
          <div className="processing-info">
            <div className="spinner-border text-primary mb-3" role="status">
              <span className="visually-hidden">Procesando...</span>
            </div>
            <h5>Procesando Archivo</h5>
            <p>Por favor espere mientras se procesa el archivo...</p>
            <p id="processing-detail" className="text-muted">
              {processingDetails}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
