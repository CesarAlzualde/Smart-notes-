import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, useSearchParams } from 'react-router-dom';
import { tagsApi } from '../../../api/tags';
import NoteContent from '../components/NoteContent';
import NoteEditForm from '../components/NoteEditForm';
import { type NoteData, type Tag, type Topic, type RelatedNote } from '../types';
import { notesApi, type CreateNoteData, type UpdateNoteData } from '../../../api/notes';
import { analysisApi, type UnifiedAnalysisResponse } from '../../../api/analysis';
import TextAnalysisPanel from '../components/TextAnalysisPanel';
import TopicsPanel from '../components/TopicsPanel';
import TagsManager from '../components/TagsManager';
import { Tabs, Tab } from '../../../components/ui/Tabs';
import './NoteDetailPage.css';
import '../../../components/ui/Tabs.css';

type AnalysisData = UnifiedAnalysisResponse;

const NoteDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const conceptFromUrl = searchParams.get('concept') || '';

  const [note, setNote] = useState<NoteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [relatedNotes, setRelatedNotes] = useState<RelatedNote[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        const [tagsResponse, topicsResponse] = await Promise.all([
          tagsApi.getTags(),
          notesApi.getTopics()
        ]);

        setTags(tagsResponse.items || []);
        setTopics(topicsResponse.items || []);

        if (id && id !== 'new') {
          const noteResponse = await notesApi.getNoteById(parseInt(id));
          setNote(noteResponse);
        } else {
          const initialTitle = conceptFromUrl ? `Nota sobre: ${conceptFromUrl}` : 'Nueva Nota';
          const initialContent = conceptFromUrl ? `Concepto principal: ${conceptFromUrl}\n\n` : '';

          setNote({
            title: initialTitle,
            content: initialContent,
            summary: '',
            tags: [],
            topics: [],
            main_topic: conceptFromUrl || '',
            created_at: new Date().toISOString(),
            source_type: 'Texto'
          });

          setIsEditing(true);
        }
      } catch (err) {
        console.error('Error al cargar los datos:', err);
        setError('No se pudo cargar la nota. Verifica tu conexión e intenta nuevamente.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, conceptFromUrl]);

  useEffect(() => {
    const fetchRelatedNotes = async () => {
      if (id && id !== 'new') {
        try {
          // Usar el cliente API configurado para obtener notas relacionadas semánticamente
          const response = await notesApi.getSemanticallyRelatedNotes(parseInt(id));
          setRelatedNotes(response.related_notes || []);
        } catch (error) {
          console.error('Error al obtener notas relacionadas:', error);
          // Si hay un error (incluyendo 401 de autenticación), establecer lista vacía
          setRelatedNotes([]);
        }
      }
    };
    fetchRelatedNotes();
  }, [id]);

  const handleGenerateAnalysis = async () => {
    if (!note || !note.content || !note.id) return;

    setIsAnalyzing(true);
    setAnalysisError(null);

    try {
      const result = await analysisApi.analyzeText(note.content, note.id);
      console.log('Respuesta completa del análisis IA:', JSON.stringify(result, null, 2));
      setAnalysisData(result);
      
      // Actualizar la nota con todos los datos del análisis IA
      if (result) {
        const updateData: UpdateNoteData = {
          summary: result.summary,
          main_topic: result.main_topic,
          // Convertir topics de la respuesta a nombres de string
          topics: result.suggested_topics || []
        };
        
        // Guardar automáticamente en la base de datos
        const updatedNote = await notesApi.updateNote(note.id, updateData);
        
        // Actualizar el estado local con la nota actualizada
        setNote(updatedNote);
      }
    } catch (error) {
      console.error('Error al generar el análisis de IA:', error);
      setAnalysisError('No se pudo completar el análisis. Inténtalo de nuevo más tarde.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSaveNote = async (formData: Partial<NoteData>) => {
    if (!note) return;

    try {
      let savedNote;
      if (note.id) {
        const updateData: UpdateNoteData = {
          title: formData.title,
          content: formData.content,
          summary: formData.summary,
          tags: formData.tags?.map((t: Tag) => t.name),
          topics: formData.topics?.map((t: Topic) => t.name),
          main_topic: formData.main_topic,
        };
        savedNote = await notesApi.updateNote(note.id, updateData);
      } else {
        const createData: CreateNoteData = {
          title: formData.title || 'Sin título',
          content: formData.content || '',
          summary: formData.summary,
          tags: formData.tags?.map((t: Tag) => t.name),
          topics: formData.topics?.map((t: Topic) => t.name),
          main_topic: formData.main_topic,
        };
        savedNote = await notesApi.createNote(createData);
        navigate(`/notes/${savedNote.id}`);
      }
      setNote(savedNote);
      setIsEditing(false);
    } catch (err) {
      console.error('Error al guardar la nota:', err);
      setError('No se pudo guardar la nota.');
    }
  };

  const handleUpdateTags = async (newTags: Tag[]) => {
    if (!note || !note.id) return;
    try {
      const updatedNote = await notesApi.updateNote(note.id, { tags: newTags.map(t => t.name) });
      setNote(updatedNote);
    } catch (err) {
      console.error('Error al actualizar etiquetas:', err);
      setError('No se pudieron actualizar las etiquetas.');
    }
  };

  const handleUpdateTopics = async (_mainTopic: string, newTopics: Topic[]) => {
    if (!note || !note.id) return;

    try {
      // Usar el método updateNote correcto que sí existe en la API
      await notesApi.updateNote(note.id, {
        topics: newTopics.map(t => t.name),  // Convertir objetos Topic a strings
        main_topic: _mainTopic
      });

      setNote(prev => prev ? { ...prev, main_topic: _mainTopic, topics: newTopics } : null);
    } catch (err) {
      console.error('Error al actualizar los temas de la nota:', err);
    }
  };

  const handleApplyCorrectedText = (correctedText: string) => {
    if (!note) return;

    // Actualiza el estado local con el texto corregido
    setNote(prev => prev ? { ...prev, content: correctedText } : null);
    
    // También actualizar el análisis de datos para mantener consistencia
    setAnalysisData(prev => prev ? { ...prev, corrected_text: correctedText } : null);
    
    // Si se está mostrando el editor, también actualizamos el contenido allí
    if (isEditing) {
      // El NoteEditForm debería recibir estas actualizaciones automáticamente
      // a través de las props que recibe
    }
  };

  const handleCreateTag = async (tagName: string) => {
    try {
      const newTag = await tagsApi.createTag(tagName);
      setTags(prevTags => [...prevTags, newTag]);
      return newTag;
    } catch (err) {
      console.error('Error al crear la etiqueta:', err);
      setError('No se pudo crear la etiqueta.');
      return null;
    }
  };

  const handleDeleteNote = async () => {
    if (note && note.id && window.confirm('¿Estás seguro de que quieres eliminar esta nota?')) {
      try {
        await notesApi.deleteNote(note.id);
        navigate('/notes');
      } catch (err) {
        console.error('Error al eliminar la nota:', err);
        setError('No se pudo eliminar la nota.');
      }
    }
  };

  if (loading) {
    return <div className="loading-container">Cargando nota...</div>;
  }

  if (error) {
    return <div className="error-container">{error}</div>;
  }

  if (!note) {
    return <div className="error-container">No se encontró la nota.</div>;
  }

  return (
    <div className="note-detail-page">
      <div className="note-header">
        <ul className="breadcrumb">
          <li><Link to="/notes">Notas</Link></li>
          <li className="active">{note.title || 'Cargando...'}</li>
        </ul>

        <div className="note-actions">
          {!isEditing ? (
            <>
              <button 
                className="action-button primary-button" 
                onClick={() => setIsEditing(true)}
              >
                <i className="fas fa-edit"></i>
                <span>Editar</span>
              </button>
              {note.id && (
                <button 
                  className="action-button danger-button" 
                  onClick={handleDeleteNote}
                  disabled={!note.id}
                >
                  <i className="fas fa-trash"></i>
                  <span>Eliminar</span>
                </button>
              )}
            </>
          ) : (
            <button 
              className="action-button secondary-button" 
              onClick={() => setIsEditing(false)}
            >
              <i className="fas fa-times"></i>
              <span>Cancelar</span>
            </button>
          )}
        </div>
      </div>

      <div className="note-layout">
        <div className="note-main-content">
          <div className="note-card">
            <div className="note-card-content">
              {!isEditing ? (
                <NoteContent note={note} />
              ) : (
                <NoteEditForm 
                  note={note} 
                  availableTags={tags} 
                  availableTopics={topics} 
                  onSave={handleSaveNote} 
                  onCancel={() => setIsEditing(false)} 
                  onGenerateAnalysis={handleGenerateAnalysis}
                  isAnalyzing={isAnalyzing}
                />
              )}
            </div>
          </div>
        </div>

        {!isEditing && note.id && (
          <div className="note-analysis-section">
            <Tabs>
              <Tab label="Análisis IA" icon="fa-robot">
                {analysisError && <div className="alert alert-danger">{analysisError}</div>}
                
                <div className="metadata-section">
                  <button 
                    className="generate-analysis-btn"
                    onClick={handleGenerateAnalysis}
                    disabled={isAnalyzing || !note.content}
                  >
                    {isAnalyzing ? (
                      <><i className="fas fa-spinner fa-spin"></i><span>Generando...</span></>
                    ) : (
                      <><i className="fas fa-magic"></i><span>Generar Análisis IA</span></>
                    )}
                  </button>
                </div>

                <TextAnalysisPanel 
                  summary={analysisData?.summary}
                  sentiment={analysisData?.sentiment}
                  readability={analysisData?.readability}
                  stats={analysisData?.stats}
                  keywords={analysisData?.keywords}
                  entities={analysisData?.entities}
                  isAnalyzing={isAnalyzing}
                  correctedText={analysisData?.corrected_text}
                  originalText={note.content}
                  noteId={note.id}
                  onTextCorrected={handleApplyCorrectedText}
                />
              </Tab>

              <Tab label="Clasificación" icon="fa-tags">
                <TopicsPanel
                  mainTopic={analysisData?.main_topic || note.main_topic}
                  topics={note.topics}
                  suggestedTopics={analysisData?.suggested_topics}
                  topicsDistribution={analysisData?.topics_distribution}
                  confidence={analysisData?.main_topic_confidence}
                  availableTopics={topics}
                  onSaveTopics={handleUpdateTopics}
                />
                <TagsManager
                  tags={note.tags || []}
                  availableTags={tags}
                  onSaveTags={handleUpdateTags}
                  onCreateTag={handleCreateTag}
                />
              </Tab>

              <Tab label="Metadatos" icon="fa-info-circle">
                <div className="metadata-section">
                  <h4 className="section-title">Información</h4>
                  <p className="metadata-value"><strong>Creado:</strong> {new Date(note.created_at).toLocaleString()}</p>
                  {note.updated_at && <p className="metadata-value"><strong>Actualizado:</strong> {new Date(note.updated_at).toLocaleString()}</p>}
                  {note.source_type && <p className="metadata-value"><strong>Origen:</strong> {note.source_type}</p>}
                </div>

                {relatedNotes && relatedNotes.length > 0 && (
                  <div className="metadata-section">
                    <h4 className="section-title">Notas Relacionadas Semánticamente</h4>
                    <ul className="related-notes-list">
                      {relatedNotes.map((relatedNote) => (
                        <li key={relatedNote.id}>
                          <Link to={`/notes/${relatedNote.id}`}>{relatedNote.title}</Link>
                          <span className="similarity-score"> (Similitud: {Math.round(relatedNote.similarity * 100)}%)</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </Tab>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  );
};

export default NoteDetailPage;
