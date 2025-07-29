import React, { useState, useEffect, useRef } from 'react';
import './TagsManager.modern.css';

import type { Tag } from '../types';

interface TagsManagerProps {
  tags: Tag[];
  availableTags?: Tag[];
  onSaveTags?: (tags: Tag[]) => void | Promise<void>;
  onCreateTag?: (tagName: string) => Promise<Tag>;
}

const TagsManager: React.FC<TagsManagerProps> = ({ 
  tags = [], 
  availableTags = [],
  onSaveTags,
  onCreateTag
}) => {
  const [showPanel, setShowPanel] = useState<boolean>(true);
  const [isEditMode, setIsEditMode] = useState<boolean>(false);
  const [tagInput, setTagInput] = useState<string>('');
  const [filteredTags, setFilteredTags] = useState<Tag[]>([]);
  const [currentTags, setCurrentTags] = useState<Tag[]>(tags);
  const tagInputRef = useRef<HTMLInputElement>(null);

  // Filtrar etiquetas disponibles en función del input
  useEffect(() => {
    if (tagInput.trim()) {
      const filtered = availableTags.filter(
        tag => tag.name.toLowerCase().includes(tagInput.toLowerCase())
      ).filter(
        // Filtrar las que ya están seleccionadas
        tag => !currentTags.some(t => t.name === tag.name)
      );
      setFilteredTags(filtered);
    } else {
      setFilteredTags([]);
    }
  }, [tagInput, availableTags, currentTags]);

  // Manejar entrada en modo edición
  const handleEnterEditMode = () => {
    setIsEditMode(true);
    setTagInput('');
    setCurrentTags([...tags]);
    // Focus en el input una vez que esté renderizado
    setTimeout(() => {
      if (tagInputRef.current) {
        tagInputRef.current.focus();
      }
    }, 50);
  };

  // Cancelar edición
  const handleCancelEdit = () => {
    setIsEditMode(false);
    setTagInput('');
    setCurrentTags([...tags]);
  };

  // Guardar cambios en etiquetas
  const handleSaveTags = () => {
    if (onSaveTags) {
      onSaveTags(currentTags);
    }
    setIsEditMode(false);
    setTagInput('');
  };

  // Añadir etiqueta desde el input
  const handleAddTag = async () => {
    if (!tagInput.trim()) return;
    
    // Verificar si la etiqueta ya existe
    const existingTag = availableTags.find(
      tag => tag.name.toLowerCase() === tagInput.toLowerCase()
    );
    
    if (existingTag) {
      if (!currentTags.some(t => t.name === existingTag.name)) {
        setCurrentTags([...currentTags, existingTag]);
      }
    } else if (onCreateTag) {
      try {
        // Crear nueva etiqueta a través de la API
        const newTag = await onCreateTag(tagInput.trim());
        setCurrentTags([...currentTags, newTag]);
      } catch (error) {
        console.error('Error al crear etiqueta:', error);
      }
    } else {
      // Crear etiqueta localmente (sin API)
      const newTag: Tag = {
        id: Math.floor(Math.random() * -1000), // ID temporal negativo
        name: tagInput.trim()
      };
      setCurrentTags([...currentTags, newTag]);
    }
    
    setTagInput('');
    if (tagInputRef.current) {
      tagInputRef.current.focus();
    }
  };

  // Añadir etiqueta desde la lista de sugerencias
  const handleAddSuggestion = (tag: Tag) => {
    if (!currentTags.some(t => t.name === tag.name)) {
      setCurrentTags([...currentTags, tag]);
      setTagInput('');
      if (tagInputRef.current) {
        tagInputRef.current.focus();
      }
    }
  };

  // Eliminar etiqueta
  const handleRemoveTag = (index: number) => {
    const newTags = [...currentTags];
    newTags.splice(index, 1);
    setCurrentTags(newTags);
  };

  // Manejar teclas especiales
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    } else if (e.key === 'Escape') {
      setTagInput('');
      setFilteredTags([]);
    }
  };

  return (
    <div className="tags-panel">
      <div className="tags-header">
        <h3 className="tags-title">
          <i className="fas fa-tags"></i> Etiquetas
        </h3>
        <div className="header-actions">
          {!isEditMode && onSaveTags && (
            <button 
              className="action-button" 
              onClick={handleEnterEditMode}
              aria-label="Gestionar etiquetas"
            >
              <i className="fas fa-edit"></i>
            </button>
          )}
          <button 
            className="toggle-button" 
            onClick={() => setShowPanel(!showPanel)}
            aria-expanded={showPanel ? 'true' : 'false'}
            aria-label={showPanel ? "Ocultar panel" : "Mostrar panel"}
          >
            <i className={`fas fa-chevron-${showPanel ? 'up' : 'down'}`}></i>
          </button>
        </div>
      </div>
      
      {showPanel && (
        <div className="tags-content">
          {!isEditMode ? (
            // Modo vista
            <div className="tags-container">
              {currentTags.length > 0 ? (
                currentTags.map((tag, index) => (
                  <span 
                    className="tag-badge" 
                    key={tag.id || index}
                  >
                    {tag.name}
                  </span>
                ))
              ) : (
                <p className="empty-text">No hay etiquetas asignadas</p>
              )}
            </div>
          ) : (
            // Modo edición
            <>
              <div className="tags-container">
                {currentTags.map((tag, index) => (
                  <span 
                    className="tag-badge editable" 
                    key={tag.id || index}
                  >
                    {tag.name}
                    <button 
                      className="remove-button" 
                      onClick={() => handleRemoveTag(index)}
                      aria-label={`Eliminar etiqueta ${tag.name}`}
                    >
                      ×
                    </button>
                  </span>
                ))}
                {currentTags.length === 0 && (
                  <p className="empty-text">No hay etiquetas seleccionadas</p>
                )}
              </div>
              
              <div className="tag-input-wrapper">
                <div className="tag-input-container">
                  <input
                    ref={tagInputRef}
                    className="tag-input"
                    placeholder="Escribe para añadir una etiqueta..."
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                  />
                  <button 
                    className="add-button"
                    onClick={handleAddTag}
                    aria-label="Añadir etiqueta"
                  >
                    <i className="fas fa-plus"></i>
                  </button>
                </div>
                
                {filteredTags.length > 0 && (
                  <div className="tags-dropdown">
                    {filteredTags.map((tag) => (
                      <div 
                        className="tag-item" 
                        key={tag.id}
                        onClick={() => handleAddSuggestion(tag)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            handleAddSuggestion(tag);
                          }
                        }}
                        role="button"
                        tabIndex={0}
                      >
                        {tag.name}
                      </div>
                    ))}
                  </div>
                )}
              </div>
                            
              <div className="action-buttons">
                <button 
                  className="cancel-button" 
                  onClick={handleCancelEdit}
                >
                  <i className="fas fa-times"></i> Cancelar
                </button>
                <button 
                  className="save-button"
                  onClick={handleSaveTags}
                >
                  <i className="fas fa-save"></i> Guardar etiquetas
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default TagsManager;
