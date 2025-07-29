// LoadingScreen component - Para mostrar estados de carga
import React from 'react';

interface LoadingScreenProps {
  message?: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ message = 'Cargando...' }) => {
  return (
    <div className="loading-screen">
      <div className="loading-container">
        <div className="spinner"></div>
        <p className="loading-message">{message}</p>
      </div>

      {/* Aplicar estilos inline en lugar de styled-jsx */}
      <style>{`
        .loading-screen {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: rgba(255, 255, 255, 0.9);
          z-index: 9999;
        }
        
        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
        
        .spinner {
          width: 50px;
          height: 50px;
          border: 5px solid #f3f3f3;
          border-top: 5px solid #3498db;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 20px;
        }
        
        .loading-message {
          font-size: 18px;
          color: #333;
          font-weight: 500;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingScreen;
