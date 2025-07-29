import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import { notesApi } from '../../../api/notes';
import type { Note } from '../../../api/notes';
import type { OnChangeValue } from 'react-select';

interface NoteOption {
  value: number;
  label: string;
}

interface NoteSelectorProps {
  onNoteSelected?: (noteId: number) => void;
  onMultiNoteSelected?: (noteIds: number[]) => void;
  isMulti: boolean;
}

const NoteSelector: React.FC<NoteSelectorProps> = ({ onNoteSelected, onMultiNoteSelected, isMulti }) => {
  const [notes, setNotes] = useState<NoteOption[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchNotes = async () => {
      try {
        const notesData = await notesApi.getNotes();
        const options = notesData.notes.map((note: Note) => ({
          value: note.id,
          label: note.title,
        }));
        setNotes(options);
      } catch (error) {
        console.error('Error fetching notes:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNotes();
  }, []);

  const handleChange = (selected: OnChangeValue<NoteOption, boolean>) => {
    if (isMulti) {
            const selectedIds = selected ? (selected as NoteOption[]).map((option: NoteOption) => option.value) : [];
      onMultiNoteSelected?.(selectedIds);
    } else {
                  const selectedOption = selected as NoteOption | null;
      if (selectedOption) {
        onNoteSelected?.(selectedOption.value);
      }
    }
  };

  return (
    <Select
      options={notes}
      isMulti={isMulti}
      onChange={handleChange}
      isLoading={isLoading}
      placeholder={isMulti ? 'Seleccionar notas...' : 'Seleccionar una nota...'}
      noOptionsMessage={() => 'No hay notas disponibles'}
      styles={{
        container: (provided) => ({ ...provided, minWidth: '300px', marginBottom: '1rem' }),
      }}
    />
  );
};

export default NoteSelector;
