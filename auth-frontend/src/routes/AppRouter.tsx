import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Register from '../features/auth/pages/Register';
import Login from '../features/auth/pages/Login';
import PasswordRecovery from '../features/auth/pages/PasswordRecovery';
import SecurityQuestionSetup from '../features/auth/pages/SecurityQuestionSetup';
import DashboardPage from '../features/dashboard/pages/DashboardPage';
import NotesListPage from '../features/notes/pages/NotesListPage';
import NoteDetailPage from '../features/notes/pages/NoteDetailPage';
import UploadPage from '../features/files/pages/UploadPage';
import OcrPreviewPage from '../features/files/pages/OcrPreviewPage';
import GraphPage from '../features/graph/pages/GraphPage';
import ProfilePage from '../features/user/pages/ProfilePage';
import Unauthorized from '../pages/Unauthorized';
import AppLayout from '../layouts/AppLayout';
import PrivateRoute from './PrivateRoute';

const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Ruta raíz - redirecciona a dashboard si está autenticado, de lo contrario a login */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        
        {/* Rutas públicas */}
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/recover-password" element={<PasswordRecovery />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
        
        {/* Rutas privadas - requieren autenticación */}
        <Route element={<PrivateRoute />}>
          {/* AppLayout se usa como wrapper para todas las rutas protegidas */}
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/notes" element={<NotesListPage />} />
            <Route path="/notes/new" element={<NoteDetailPage />} />
            <Route path="/notes/edit/:id" element={<NoteDetailPage />} />
            <Route path="/notes/:id" element={<NoteDetailPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/ocr-preview/:fileId" element={<OcrPreviewPage />} />
            <Route path="/graph" element={<GraphPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/setup-security-question" element={<SecurityQuestionSetup />} />
          </Route>
        </Route>
        
        {/* Rutas privadas con roles específicos */}
        <Route element={<PrivateRoute requiredRole="admin" />}>
          {/* <Route path="/admin" element={<AdminDashboard />} /> */}
        </Route>
        
        {/* Ruta 404 - página no encontrada */}
        <Route path="*" element={<div>Página no encontrada</div>} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
