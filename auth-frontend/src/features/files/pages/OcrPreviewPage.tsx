import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Form, Badge, Alert, Spinner, InputGroup, ProgressBar } from 'react-bootstrap';
import { filesApi } from '../../../api/files';
import type { File as FileType, OcrResult } from '../../../types/files';
import './OcrPreviewPage.css';

// Tipo para errores de API con estructura conocida
interface ApiError extends Error {
  response?: {
    data?: {
      message?: string;
      error?: string;
    };
  };
}

const OcrPreviewPage: React.FC = () => {
  const { fileId: fileIdStr } = useParams<{ fileId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const engine = searchParams.get('engine');
  const isWhiteboard = searchParams.get('is_whiteboard') === 'true';

  // Estados de la página y datos
  const [error, setError] = useState<string | null>(null);
  const [fileData, setFileData] = useState<FileType | null>(null);
  const [noteText, setNoteText] = useState<string>('');
  const [noteTitle, setNoteTitle] = useState<string>('');
  const [tags, setTags] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState<string>('');
  const [copySuccess, setCopySuccess] = useState(false);
  const [creatingNote, setCreatingNote] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [processingStatus, setProcessingStatus] = useState<'idle' | 'processing' | 'polling' | 'success' | 'failed'>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('Cargando datos del archivo...');

  // Efecto 1: Iniciar el proceso de OCR
  useEffect(() => {

    if (!fileIdStr || !engine) {
      setStatusMessage('Esperando parámetros de la URL...');
      return;
    }

    if (processingStatus !== 'idle') {
      return; // Solo se ejecuta una vez
    }

    const startProcessing = async () => {
      setProcessingStatus('processing');
      setStatusMessage('Iniciando el procesamiento del archivo...');
      setError(null);

      try {
        await filesApi.processOCR(fileIdStr, { engine, isWhiteboard });
        console.log(`✅ Procesamiento iniciado para ID: ${fileIdStr}.`);
        setProcessingStatus('polling'); // Transición al estado de sondeo
      } catch (err) {
        const apiError = err as ApiError;
        setError(apiError.response?.data?.message || apiError.message || 'No se pudo iniciar el procesamiento.');
        setProcessingStatus('failed');
      }
    };

    startProcessing();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fileIdStr, engine, isWhiteboard]);

  // Efecto 2: Manejar la lógica de sondeo (polling)
  useEffect(() => {

    if (processingStatus !== 'polling' || !fileIdStr) {
      return; // Solo se ejecuta cuando estamos en modo sondeo
    }

    let isCancelled = false;
    let timeoutId: number | undefined;

    const pollFileStatus = async () => {
      const numericFileId = parseInt(fileIdStr, 10);
      if (isNaN(numericFileId) || isCancelled) return;

      try {
        const response = await filesApi.getFileById(numericFileId);
        if (isCancelled) return;

        console.log('--- [POLLING] ---');
        console.log('Estado:', response.processing_status);
        console.log('Texto extraído longitud:', response.extract_text?.length || 0);

        setFileData(response);
        const status = response.processing_status?.toUpperCase() || '';

        if (status === 'SUCCESS' || (response.extract_text && response.extract_text.length > 0)) {
          setProcessingStatus('success');
          setStatusMessage('¡Procesamiento completado!');
          setNoteText(response.extract_text || '');
          setNoteTitle(response.filename?.split('.').slice(0, -1).join('.') || 'Nota sin título');
        } else if (status === 'FAILED') {
          setProcessingStatus('failed');
          setError(response.file_metadata?.error || 'El procesamiento del archivo falló.');
          setStatusMessage('Error en el procesamiento.');
        } else {
          setStatusMessage('El archivo se está procesando, por favor espere...');
          timeoutId = window.setTimeout(pollFileStatus, 2000);
        }
      } catch (err) {
        if (isCancelled) return;
        const apiError = err as ApiError;
        setError(apiError.response?.data?.message || apiError.message || 'No se pudo obtener el estado del archivo.');
        setProcessingStatus('failed');
      }
    };

    pollFileStatus();

    return () => {
      isCancelled = true;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [processingStatus, fileIdStr, engine]);

  const handleCopyText = () => {
    if (textareaRef.current) {
      textareaRef.current.select();
      document.execCommand('copy');
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const handleAddTag = () => {
    if (currentTag.trim() && !tags.includes(currentTag.trim())) {
      setTags([...tags, currentTag.trim()]);
      setCurrentTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleTagKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleCreateNote = async () => {
    if (!noteText || !noteTitle.trim() || !fileData) {
      setError('No se puede crear la nota. Faltan datos del archivo o de la nota.');
      return;
    }
    setCreatingNote(true);
    setError(null);

    const ocrResult: OcrResult = {
      text: fileData.extract_text || noteText,
      confidence: 0.9, // Confianza no disponible, se usa un valor por defecto
      filename: fileData.filename,
      thumbnail_url: `/api/files/${fileData.id}/thumbnail`,
    };

    try {
      await filesApi.createNoteFromOCR(ocrResult, noteTitle, noteText, { tags });
      alert('¡Nota creada correctamente!');
      navigate('/notes');
    } catch (err: unknown) {
      console.error('Error al crear la nota:', err);
      const apiError = err as ApiError;
      setError(apiError.response?.data?.error || 'No se pudo crear la nota.');
    } finally {
      setCreatingNote(false);
    }
  };

  // Si tenemos texto extraído, mostramos la vista de éxito independientemente del estado
  const hasExtractedText = fileData?.extract_text && fileData.extract_text.length > 0;
  
  // Log para diagnosticar estado
  console.log('Estado de procesamiento:', processingStatus);
  console.log('¿Tiene texto extraído?', hasExtractedText);
  console.log('Longitud del texto:', fileData?.extract_text?.length || 0);
  
  // Si tenemos texto extraído o el estado es success, mostramos la interfaz de éxito
  if (hasExtractedText || processingStatus === 'success') {
    console.log('✅ Renderizando interfaz de texto OCR');
    // Continuamos con la interfaz principal (la que muestra el texto)
  } else if (['idle', 'processing', 'polling'].includes(processingStatus)) {
    return (
      <Container className="ocr-preview-page py-5">
        <Row className="justify-content-center">
          <Col md={8} lg={6}>
            <Card className="text-center shadow-sm">
              <Card.Body>
                <Card.Title as="h2">Procesando Archivo</Card.Title>
                <div className="my-4">
                  <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
                </div>
                <p className="text-muted">{statusMessage}</p>
                <ProgressBar animated now={100} />
                {/* Botón para forzar actualización */}
                <Button 
                  variant="link" 
                  className="mt-3" 
                  onClick={() => {
                    const numId = fileIdStr ? parseInt(fileIdStr, 10) : 0;
                    if (numId) {
                      console.log('Forzando actualización de datos...');
                      filesApi.getFileById(numId).then(data => {
                        console.log('Datos actualizados:', data);
                        if (data.extract_text) {
                          setFileData(data);
                          setNoteText(data.extract_text);
                          setProcessingStatus('success');
                        }
                      });
                    }
                  }}
                >
                  Actualizar estado
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  if (processingStatus === 'failed') {
    return (
      <Container className="ocr-preview-page py-5">
        <Alert variant="danger" className="shadow-sm">
          <h4><i className="fas fa-exclamation-triangle me-2"></i>Error en el Procesamiento</h4>
          <p>{error || 'Ocurrió un error inesperado.'}</p>
          <hr />
          <Button variant="outline-danger" onClick={() => navigate('/upload')}>
            <i className="fas fa-arrow-left me-2"></i>Volver a Cargar Archivos
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container fluid className="ocr-preview-page py-4">
      <Row>
        <Col md={8}>
          <Card className="mb-4 shadow-sm">
            <Card.Header className="d-flex align-items-center justify-content-between">
              <h5 className="mb-0">Texto Extraído</h5>
              <Button variant="outline-secondary" size="sm" onClick={handleCopyText} disabled={!noteText}>
                {copySuccess ? (<><i className="fas fa-check me-1"></i>Copiado</>) : (<><i className="fas fa-copy me-1"></i>Copiar</>)}
              </Button>
            </Card.Header>
            <Card.Body>
              <Form.Control 
                as="textarea"
                ref={textareaRef}
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                rows={25}
              />
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Header><h5 className="mb-0"><i className="fas fa-save me-2"></i>Crear Nota</h5></Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Título</Form.Label>
                  <Form.Control type="text" value={noteTitle} onChange={(e) => setNoteTitle(e.target.value)} placeholder="Título para la nota" />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Etiquetas</Form.Label>
                  <InputGroup>
                    <Form.Control type="text" value={currentTag} onChange={(e) => setCurrentTag(e.target.value)} onKeyPress={handleTagKeyPress} placeholder="Añadir etiqueta" />
                    <Button variant="outline-secondary" onClick={handleAddTag} disabled={!currentTag.trim()}><i className="fas fa-plus"></i></Button>
                  </InputGroup>
                  <div className="mt-2">
                    {tags.map((tag, index) => (
                      <Badge bg="secondary" className="me-2 mb-2 tag-badge" key={index}>
                        {tag}
                        <span 
                          onClick={() => handleRemoveTag(tag)} 
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              handleRemoveTag(tag);
                            }
                          }}
                          role="button"
                          tabIndex={0}
                          aria-label={`Quitar etiqueta ${tag}`}
                          className="ms-1 tag-remove-btn"
                        >&times;</span>
                      </Badge>
                    ))}
                    {tags.length === 0 && (<span className="text-muted small">No hay etiquetas</span>)}
                  </div>
                </Form.Group>
                <div className="d-grid">
                  <Button variant="primary" onClick={handleCreateNote} disabled={creatingNote || !noteTitle.trim()}>
                    {creatingNote ? (<><Spinner animation="border" size="sm" className="me-2" />Creando...</>) : (<>Crear Nota</>)}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
          
          {fileData?.id && (
            <Card className="shadow-sm">
              <Card.Header><h5 className="mb-0">Archivo Original</h5></Card.Header>
              <Card.Body className="text-center">
                <img src={`/api/files/${fileData.id}/thumbnail`} alt="Miniatura del archivo" className="img-thumbnail ocr-thumbnail" />
                <p className="mt-2 mb-0 text-muted small">{fileData.filename}</p>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default OcrPreviewPage;