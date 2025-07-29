import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './index.css'
// Importamos A-Frame y nuestros componentes personalizados
import './components/AFrameComponents'
// Importar el CSS principal migrado desde Flask
import './assets/css/main.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
