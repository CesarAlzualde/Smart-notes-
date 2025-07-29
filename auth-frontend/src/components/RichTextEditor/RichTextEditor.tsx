import React, { useEffect, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import { Extension } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Image from '@tiptap/extension-image';
import Link from '@tiptap/extension-link';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { common, createLowlight } from 'lowlight'
import Placeholder from '@tiptap/extension-placeholder';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import mermaid from 'mermaid';
import './RichTextEditor.css';

// Configuración inicial de Mermaid
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: 'monospace',
  fontSize: 14
});

// Extensión personalizada para renderizado de LaTeX
const MathExtension = (): Extension => Extension.create({
  name: 'math',
  
  addGlobalAttributes() {
    return [
      {
        types: ['textContent'],
        attributes: {
          'data-math': {
            default: false,
            parseHTML: (element: HTMLElement) => element.getAttribute('data-math') === 'true',
            renderHTML: (attributes: Record<string, any>) => {
              if (!attributes['data-math']) return {};
              return { 'data-math': 'true' };
            }
          }
        }
      }
    ];
  },
  
  renderHTML({ node }: { node: Record<string, any> }) {
    if (node.attrs['data-math']) {
      try {
        const html = katex.renderToString(node.textContent, {
          throwOnError: false,
          displayMode: true
        });
        return ['div', { class: 'math-block', innerHTML: html }];
      } catch (error: unknown) {
        console.error('Error rendering LaTeX:', error);
        return ['div', { class: 'math-block math-error' }, node.textContent];
      }
    }
    return null;
  }
});

// Extensión personalizada para diagramas Mermaid
const MermaidExtension = (): Extension => Extension.create({
  name: 'mermaid',
  
  addNodeView() {
    return ({ node }: { node: Record<string, any> }) => {
      const container = document.createElement('div');
      container.classList.add('mermaid-container');
      
      const renderMermaid = () => {
        try {
          container.innerHTML = '';
          const id = `mermaid-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
          container.id = id;
          
          // Renderizar el diagrama
          // La función render de mermaid tiene una firma diferente
          // Usando un enfoque más seguro con la API actual
          mermaid.render(id, node.attrs.content).then((result) => {
            container.innerHTML = result.svg;
          }).catch((error) => {
            console.error('Error rendering Mermaid diagram:', error);
            const errorMessage = error instanceof Error ? error.message : String(error);
            container.innerHTML = `<div class="mermaid-error">Error en el diagrama: ${errorMessage}</div>`;
          });
        } catch (error: unknown) {
          console.error('Error rendering Mermaid diagram:', error);
          const errorMessage = error instanceof Error ? error.message : String(error);
          container.innerHTML = `<div class="mermaid-error">Error en el diagrama: ${errorMessage}</div>`;
        }
      };
      
      renderMermaid();
      return { dom: container };
    };
  }
});

interface RichTextEditorProps {
  content: string;
  onChange: (content: string) => void;
  placeholder?: string;
  editable?: boolean;
}

const RichTextEditor: React.FC<RichTextEditorProps> = ({
  content,
  onChange,
  placeholder = 'Escribe aquí tu contenido...',
  editable = true
}) => {
  const [renderedMermaid, setRenderedMermaid] = useState<boolean>(false);
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      Image,
      Link.configure({
        openOnClick: false,
      }),
      CodeBlockLowlight.configure({
        lowlight: createLowlight(common),
      }),
      Placeholder.configure({
        placeholder,
      }),
      MathExtension(),
      MermaidExtension(),
    ],
    content,
    editable,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });
  
  // Renderizar diagramas Mermaid después de que el contenido sea actualizado
  useEffect(() => {
    if (!editor || renderedMermaid) return;
    
    // Buscar bloques de código con lenguaje 'mermaid'
    const mermaidBlocks = document.querySelectorAll('pre code.language-mermaid');
    if (mermaidBlocks.length > 0) {
      setRenderedMermaid(true);
      // Reiniciar Mermaid para renderizar nuevos diagramas
      setTimeout(() => {
        try {
          mermaid.contentLoaded();
        } catch (error: unknown) {
          console.error('Error loading Mermaid diagrams:', error);
        }
      }, 100);
    }
  }, [editor, content, renderedMermaid]);
  
  return (
    <div className="rich-text-editor">
      <div className="editor-content">
        <EditorContent editor={editor} />
      </div>
      
      {editable && (
        <div className="editor-toolbar">
          <button
            onClick={() => editor?.chain().focus().toggleBold().run()}
            className={editor?.isActive('bold') ? 'is-active' : ''}
            title="Negrita"
          >
            <i className="fas fa-bold"></i>
          </button>
          <button
            onClick={() => editor?.chain().focus().toggleItalic().run()}
            className={editor?.isActive('italic') ? 'is-active' : ''}
            title="Cursiva"
          >
            <i className="fas fa-italic"></i>
          </button>
          <button
            onClick={() => editor?.chain().focus().toggleCode().run()}
            className={editor?.isActive('code') ? 'is-active' : ''}
            title="Código"
          >
            <i className="fas fa-code"></i>
          </button>
          <button
            onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
            className={editor?.isActive('heading', { level: 2 }) ? 'is-active' : ''}
            title="Encabezado"
          >
            <i className="fas fa-heading"></i>
          </button>
          <button
            onClick={() => editor?.chain().focus().toggleBulletList().run()}
            className={editor?.isActive('bulletList') ? 'is-active' : ''}
            title="Lista"
          >
            <i className="fas fa-list-ul"></i>
          </button>
          <button
            onClick={() => editor?.chain().focus().toggleOrderedList().run()}
            className={editor?.isActive('orderedList') ? 'is-active' : ''}
            title="Lista numerada"
          >
            <i className="fas fa-list-ol"></i>
          </button>
          <button
            onClick={() => editor?.chain().focus().toggleCodeBlock().run()}
            className={editor?.isActive('codeBlock') ? 'is-active' : ''}
            title="Bloque de código"
          >
            <i className="fas fa-file-code"></i>
          </button>
          <button
            onClick={() => {
              const url = window.prompt('URL del enlace');
              if (url) {
                editor?.chain().focus().setLink({ href: url }).run();
              }
            }}
            className={editor?.isActive('link') ? 'is-active' : ''}
            title="Enlace"
          >
            <i className="fas fa-link"></i>
          </button>
        </div>
      )}
    </div>
  );
};

export default RichTextEditor;
