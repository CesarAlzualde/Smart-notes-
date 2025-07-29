import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Spinner } from 'react-bootstrap';
import RichTextEditor from '../../../components/RichTextEditor/RichTextEditor';
import { notesApi } from '../../../api/notes';

// Interfaz para el estado de la nota
interface NoteState {
  id?: number;
  title: string;
  content: string;
  tags: string[];
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  saved: boolean;
}

const NoteEditorPage: React.FC = () => {
  const { noteId } = useParams<{ noteId: string }>();
  const navigate = useNavigate();
  const isNewNote = !noteId || noteId === 'new';
  
  const [note, setNote] = useState<NoteState>({
    title: '',
    content: '',
    tags: [],
    isLoading: !isNewNote,
    isSaving: false,
    error: null,
    saved: false,
  });
  
  // Estado para la entrada de etiquetas
  const [tagInput, setTagInput] = useState('');
  
  // Cargar la nota existente si estamos editando
  useEffect(() => {
    if (!isNewNote) {
      const fetchNote = async () => {
        try {
          const noteData = await notesApi.getNote(parseInt(noteId));
          setNote({
            ...noteData,
            tags: noteData.tags || [],
            isLoading: false,
            isSaving: false,
            error: null,
            saved: false,
          });
        } catch (err) {
          console.error('Error fetching note:', err);
          setNote(prev => ({
            ...prev,
            isLoading: false,
            error: 'No se pudo cargar la nota. Por favor, inténtalo de nuevo.',
          }));
        }
      };
      
      fetchNote();
    }
  }, [noteId, isNewNote]);
  
  // Manejador para cambios en el título
  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNote(prev => ({ ...prev, title: e.target.value, saved: false }));
  };
  
  // Manejador para cambios en el contenido
  const handleContentChange = (content: string) => {
    setNote(prev => ({ ...prev, content, saved: false }));
  };
  
  // Manejador para añadir etiquetas
  const handleAddTag = () => {
    if (!tagInput.trim()) return;
    
    // Evitar duplicados
    if (!note.tags.includes(tagInput.trim())) {
      setNote(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()],
        saved: false,
      }));
    }
    setTagInput('');
  };
  
  // Manejador para eliminar etiquetas
  const handleRemoveTag = (tagToRemove: string) => {
    setNote(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove),
      saved: false,
    }));
  };
  
  // Manejador para guardar la nota
  const handleSaveNote = async () => {
    if (!note.title.trim() || !note.content.trim()) {
      setNote(prev => ({
        ...prev,
        error: 'El título y el contenido son obligatorios',
      }));
      return;
    }
    
    setNote(prev => ({ ...prev, isSaving: true, error: null }));
    
    try {
      let savedNote;
      if (isNewNote) {
        savedNote = await notesApi.createNote({
          title: note.title.trim(),
          content: note.content,
          tags: note.tags,
        });
      } else {
        savedNote = await notesApi.updateNote(parseInt(noteId), {
          title: note.title.trim(),
          content: note.content,
          tags: note.tags,
        });
      }
      
      setNote(prev => ({
        ...prev,
        id: savedNote.id,
        isSaving: false,
        saved: true,
        error: null,
      }));
      
      // Navegar a la nota recién creada si es nueva
      if (isNewNote) {
        navigate(`/notes/${savedNote.id}`, { replace: true });
      }
      
      // Resetear el estado de guardado después de un tiempo
      setTimeout(() => {
        setNote(prev => ({ ...prev, saved: false }));
      }, 2000);
      
    } catch (err) {
      console.error('Error saving note:', err);
      setNote(prev => ({
        ...prev,
        isSaving: false,
        error: 'Error al guardar la nota. Por favor, inténtalo de nuevo.',
      }));
    }
  };
  
  // Manejar la tecla Enter en el campo de etiquetas
  const handleTagKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };
  
  if (note.isLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" role="status" className="mx-auto">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
      </Container>
    );
  }
  
  return (
    <Container className="py-4 max-w-5xl mx-auto">
      <div className="mb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">
          {isNewNote ? 'Nueva Nota' : 'Editar Nota'}
        </h1>
        <div className="flex gap-2">
          <button
            onClick={() => navigate(-1)}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded"
          >
            Cancelar
          </button>
          <button
            onClick={handleSaveNote}
            disabled={note.isSaving}
            className={`bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center ${
              note.isSaving ? 'opacity-70 cursor-not-allowed' : ''
            }`}
          >
            {note.isSaving ? (
              <>
                <span className="mr-2">Guardando</span>
                <div className="animate-spin h-4 w-4 border-2 border-white rounded-full border-t-transparent"></div>
              </>
            ) : (
              'Guardar Nota'
            )}
          </button>
        </div>
      </div>
      
      {note.error && (
        <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {note.error}
        </div>
      )}
      
      {note.saved && (
        <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          Nota guardada correctamente
        </div>
      )}
      
      <div className="mb-4">
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Título
        </label>
        <input
          type="text"
          id="title"
          value={note.title}
          onChange={handleTitleChange}
          placeholder="Título de la nota"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          required
        />
      </div>
      
      <div className="mb-4">
        <div className="block text-sm font-medium text-gray-700 mb-1">
          Contenido
        </div>
        <RichTextEditor 
          content={note.content} 
          onChange={handleContentChange}
          placeholder="Escribe el contenido de tu nota aquí..."
        />
      </div>
      
      <div className="mb-4">
        <div className="block text-sm font-medium text-gray-700 mb-1">
          Etiquetas
        </div>
        <div className="flex flex-wrap gap-2 mb-2">
          {note.tags.map(tag => (
            <span 
              key={tag} 
              className="bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded-full flex items-center"
            >
              {tag}
              <button
                onClick={() => handleRemoveTag(tag)}
                className="ml-1 text-blue-800 hover:text-blue-900"
              >
                &times;
              </button>
            </span>
          ))}
        </div>
        <div className="flex">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagKeyDown}
            placeholder="Añadir etiqueta"
            className="flex-grow px-3 py-2 border border-gray-300 rounded-l-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={handleAddTag}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-r-md"
          >
            Añadir
          </button>
        </div>
      </div>
    </Container>
  );
};

export default NoteEditorPage;
