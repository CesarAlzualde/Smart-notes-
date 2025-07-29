import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import Pagination from '../Pagination';

describe('Pagination Component', () => {
  // Verificación básica de renderizado
  it('renders without crashing', () => {
    const handlePageChange = vi.fn();
    const { container } = render(
      <Pagination 
        currentPage={1} 
        totalPages={5} 
        onPageChange={handlePageChange} 
      />
    );
    
    // Verificar que el componente se renderiza
    expect(container).toBeTruthy();
  });
});

