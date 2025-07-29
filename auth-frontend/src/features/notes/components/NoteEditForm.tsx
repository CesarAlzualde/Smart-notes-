import React, { useState } from 'react';
import type { MultiValue, SingleValue } from 'react-select';
import Select from 'react-select';
import './NoteEditForm.modern.css';
import NoteFileUploader from './NoteFileUploader';
import RichTextEditor from '../../../components/RichTextEditor/RichTextEditor';
import type { Tag, Topic, NoteData } from '../types';

interface OptionType {
  value: number;
  label: string;
}



interface NoteEditFormProps {
  note: NoteData | null;
  availableTags: Tag[];
  availableTopics: Topic[];
  onSave: (noteData: NoteData) => void;
  onCancel: () => void;
  onGenerateAnalysis: () => void;
  isAnalyzing: boolean;
}

const NoteEditForm: React.FC<NoteEditFormProps> = ({
  note,
  availableTags,
  availableTopics,
  onSave,
  onCancel,
  onGenerateAnalysis,
  isAnalyzing
}) => {
  const [formData, setFormData] = useState<NoteData>(note || {
    id: undefined,
    title: '',
    content: '',
    summary: '',
    tags: [],
    topics: [],
    main_topic: '',
    created_at: '',
    source_type: 'Texto'
  });

  const sourceTypes = [
    { value: 'Texto', label: 'Texto' },
    { value: 'PDF', label: 'PDF' },
    { value: 'URL', label: 'URL' },
    { value: 'OCR', label: 'Imagen (OCR)' }
  ];

  // Convertir tags y topics para el componente Select
  const convertToOptions = (items: (Tag | Topic)[] = []): OptionType[] => {
    return items.filter(item => item.id !== undefined && item.name).map(item => ({
      value: item.id,
      label: item.name
    }));
  };

  const selectedTags = formData.tags?.filter(tag => tag.id !== undefined && tag.name).map(tag => ({
    value: tag.id,
    label: tag.name
  })) || [];

  const selectedTopics = formData.topics?.filter(topic => topic.id !== undefined && topic.name).map(topic => ({
    value: topic.id,
    label: topic.name
  })) || [];

  const selectedSourceType = sourceTypes.find(type => type.value === formData.source_type);



  // Manejar cambios en el formulario
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Manejar cambios en tags
  const handleTagsChange = (selectedOptions: MultiValue<OptionType>) => {
    const tags = selectedOptions ? selectedOptions.map(option => ({
      id: option.value,
      name: option.label
    })) : [];
    
    setFormData(prev => ({
      ...prev,
      tags
    }));
  };

  // Manejar cambios en topics
  const handleTopicsChange = (selectedOptions: MultiValue<OptionType>) => {
    const topics = selectedOptions ? selectedOptions.map(option => ({
      id: option.value,
      name: option.label
    })) : [];
    
    setFormData(prev => ({
      ...prev,
      topics
    }));
  };

  // Manejar cambios en source type
  const handleSourceTypeChange = (selectedOption: SingleValue<{ value: string; label: string }>) => {
    setFormData(prev => ({
      ...prev,
      source_type: selectedOption ? selectedOption.value : 'Texto'
    }));
  };

  // Manejar envío del formulario
  // Manejar la selección de archivo para PDF y OCR
  const handleFileSelect = async (file: File) => {
    try {
      // Aquí normalmente enviaríamos el archivo a un servicio backend
      // para procesarlo y obtener el contenido extraído
      console.log(`Procesando archivo: ${file.name}`);
      
      // Simulación de procesamiento de archivo
      // En una implementación real, esto sería una llamada a la API
      // const result = await filesApi.processFile(file, formData.source_type);
      // setFormData(prev => ({
      //   ...prev,
      //   content: result.content,
      //   file_content: result.raw_content
      // }));
    } catch (error) {
      console.error('Error al procesar el archivo:', error);
    }
  };

  // Manejar envío del formulario
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!note) {
    return null; // O un spinner de carga, si se prefiere
  }

  return (
    <form className="note-form" onSubmit={handleSubmit}>
      <div className="form-section">
        <label className="form-label" htmlFor="title">Título</label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder="Título de la nota"
          required
          className="form-control form-control-large"
        />
      </div>

      <div className="form-section">
        <label className="form-label" htmlFor="content">Contenido</label>
        <RichTextEditor
          content={formData.content}
          onChange={(newContent) => {
            setFormData(prev => ({
              ...prev,
              content: newContent
            }));
          }}
          placeholder="Contenido de la nota"
        />
        <span className="form-help-text">
          Editor con soporte para Markdown, LaTeX y diagramas Mermaid.
        </span>
      </div>

      <div className="form-section">
        <label className="form-label" htmlFor="summary">Resumen de IA</label>
        <textarea
          id="summary"
          name="summary"
          value={formData.summary || ''}
          onChange={handleChange}
          placeholder="El resumen se genera automáticamente con el análisis de IA, pero puedes editarlo aquí"
          className="form-control"
          rows={4}
        />
        <span className="form-help-text">
          Este resumen se genera automáticamente, pero puedes editarlo según tus necesidades.
        </span>
      </div>

      <div className="form-grid form-grid-2-cols">
        <div className="form-section">
          <label className="form-label" htmlFor="tags">Etiquetas</label>
          <Select
            id="tags"
            isMulti
            options={convertToOptions(availableTags)}
            value={selectedTags}
            onChange={handleTagsChange}
            placeholder="Selecciona o crea etiquetas"
            className="select-container"
            classNamePrefix="select"
          />
        </div>
        
        <div className="form-section">
          <label className="form-label" htmlFor="source_type">Tipo de Fuente</label>
          <Select
            id="source_type"
            options={sourceTypes}
            value={selectedSourceType}
            onChange={handleSourceTypeChange}
            placeholder="Selecciona el tipo de contenido"
            className="select-container"
            classNamePrefix="select"
          />
        </div>
      </div>

      <div className="form-grid form-grid-2-cols">
        <div className="form-section">
          <label className="form-label" htmlFor="main_topic">Tema Principal</label>
          <input
            type="text"
            id="main_topic"
            name="main_topic"
            value={formData.main_topic}
            onChange={handleChange}
            placeholder="Tema principal"
            className="form-control"
          />
        </div>
        
        <div className="form-section">
          <label className="form-label" htmlFor="topics">Temas Relacionados</label>
          <Select
            id="topics"
            isMulti
            options={convertToOptions(availableTopics)}
            value={selectedTopics}
            onChange={handleTopicsChange}
            placeholder="Selecciona o crea temas"
            className="select-container"
            classNamePrefix="select"
          />
        </div>
      </div>
      
      {/* Integramos el componente de carga de archivos cuando el tipo de fuente es PDF o OCR */}
      {(formData.source_type === 'PDF' || formData.source_type === 'OCR') && (
        <div className="form-section">
          <label className="form-label">
            {formData.source_type === 'PDF' ? 'Subir documento PDF' : 'Subir imagen para OCR'}
          </label>
          <NoteFileUploader
            sourceType={formData.source_type}
            onFileSelect={handleFileSelect}
          />
        </div>
      )}

      <div className="form-actions">
        <button type="button" onClick={onCancel} className="button button-secondary">
          Cancelar
        </button>
        {note?.id && (
          <button 
            type="button" 
            onClick={onGenerateAnalysis} 
            className="button button-ai"
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <><i className="fas fa-spinner fa-spin"></i> Generando...</>
            ) : (
              <><i className="fas fa-magic"></i> Generar Análisis IA</>
            )}
          </button>
        )}
        <button type="submit" className="button button-primary">
          Guardar Nota
        </button>
      </div>
    </form>
  );
};

export default NoteEditForm;
