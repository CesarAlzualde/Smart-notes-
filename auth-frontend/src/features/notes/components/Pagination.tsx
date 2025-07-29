import React, { useState } from 'react';
import './Pagination.modern.css';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  isLoading?: boolean;
  totalItems?: number;
  itemsPerPage?: number;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  isLoading = false,
  totalItems = 0,
  itemsPerPage = 10
}) => {
  // Estado para manejar la animación de transición de páginas
  const [animating, setAnimating] = useState(false);
  const [lastDirection, setLastDirection] = useState<'prev' | 'next' | null>(null);

  // No mostrar paginación si no hay páginas o solo hay una
  if (totalPages <= 1) {
    return null;
  }

  // Determinar qué páginas mostrar (siempre mostramos primera, última y las cercanas a la actual)
  const getPageNumbers = () => {
    const pageNumbers: (number | string)[] = [];
    
    // Siempre incluir primera página
    pageNumbers.push(1);
    
    // Mostrar elipsis después de la primera página si la página actual está lejos
    if (currentPage > 3) {
      pageNumbers.push('...');
    }
    
    // Mostrar páginas cercanas a la actual
    for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
      if (i === 1 || i === totalPages) continue; // Ya incluimos primera y última
      pageNumbers.push(i);
    }
    
    // Mostrar elipsis antes de la última página si la página actual está lejos
    if (currentPage < totalPages - 2) {
      pageNumbers.push('...');
    }
    
    // Siempre incluir última página si hay más de una página
    if (totalPages > 1) {
      pageNumbers.push(totalPages);
    }
    
    return pageNumbers;
  };

  // Manejar cambio de página con animación
  const handlePageChange = (newPage: number) => {
    if (newPage === currentPage || isLoading) return;
    
    // Determinar dirección
    const direction = newPage > currentPage ? 'next' : 'prev';
    setLastDirection(direction);
    
    // Aplicar animación
    setAnimating(true);
    setTimeout(() => {
      onPageChange(newPage);
      setTimeout(() => setAnimating(false), 300); // Duración de la animación
    }, 150);
  };

  // Calcular el rango de elementos que se están mostrando actualmente
  const startItem = Math.min(((currentPage - 1) * itemsPerPage) + 1, totalItems);
  const endItem = Math.min(startItem + itemsPerPage - 1, totalItems);

  return (
    <div className={`pagination-container ${animating ? `animating ${lastDirection}` : ''}`}>
      <ul className="pagination">
        {/* Botón Anterior */}
        <li className={`page-item page-nav-button ${currentPage === 1 || isLoading ? 'disabled' : ''}`}>
          <button
            className="page-link"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1 || isLoading}
            aria-label="Anterior"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
        </li>
        
        {/* Botones de página */}
        {getPageNumbers().map((page, index) => {
          if (page === '...') {
            return (
              <li key={`ellipsis-${index}`} className="page-item ellipsis">
                <span className="page-link">···</span>
              </li>
            );
          }
          
          return (
            <li 
              key={page} 
              className={`page-item ${page === currentPage ? 'active' : ''} ${isLoading ? 'disabled' : ''}`}
            >
              <button
                className="page-link"
                onClick={() => handlePageChange(page as number)}
                disabled={page === currentPage || isLoading}
                aria-current={page === currentPage ? 'page' : undefined}
              >
                {page}
              </button>
            </li>
          );
        })}
        
        {/* Botón Siguiente */}
        <li className={`page-item page-nav-button ${currentPage === totalPages || isLoading ? 'disabled' : ''}`}>
          <button
            className="page-link"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages || isLoading}
            aria-label="Siguiente"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </li>
      </ul>
      
      {totalItems > 0 && (
        <div className="pagination-info" role="status">
          Mostrando <strong>{startItem}</strong> - <strong>{endItem}</strong> de <strong>{totalItems}</strong> elementos
        </div>
      )}
      
      {isLoading && (
        <div className="pagination-loading" role="status">
          <div className="spinner" aria-hidden="true"></div>
          <span>Cargando página {currentPage}...</span>
        </div>
      )}
    </div>
  );
};

export default Pagination;
