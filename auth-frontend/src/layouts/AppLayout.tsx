import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, Link } from 'react-router-dom';
import styled from '@emotion/styled';
import { useAuthStore } from '../store/authStore';
import { tagsApi } from '../api/tags';
import Header from '../components/layout/Header';
import { FaHome, FaStickyNote, FaProjectDiagram, FaCloudUploadAlt, FaTag, FaSpinner, FaInfoCircle } from 'react-icons/fa';

interface Tag {
  id: number;
  name: string;
  count?: number;
}

const AppLayout: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTags = async () => {
      try {
        setIsLoading(true);
        const response = await tagsApi.getPopularTags(10);
        setTags(response.tags || []);
      } catch (error) {
        console.error('Error al cargar etiquetas:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTags();
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

const AppContainer = styled.div`
    display: flex;
    height: 100vh;
    overflow: hidden;
    background-color: ${props => props.theme.background};
    color: ${props => props.theme.text};
    transition: all 0.3s ease;
  `;

  const Sidebar = styled.div<{isOpen: boolean}>`
    width: ${props => props.isOpen ? '250px' : '0px'};
    height: 100%;
    background: ${props => props.theme.sidebar.background};
    transition: all 0.3s ease;
    overflow-x: hidden;
    border-right: 1px solid ${props => props.theme.sidebar.border};
    display: flex;
    flex-direction: column;
    
    @media (max-width: 768px) {
      position: fixed;
      z-index: 1000;
      height: 100vh;
    }
  `;

  const SidebarLogo = styled.div`
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid ${props => props.theme.sidebar.border};

    h4 {
      margin: 0;
      font-size: 1.2rem;
      font-weight: 700;
      background: linear-gradient(90deg, #4776E6 0%, #8E54E9 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  `;

  const SidebarNav = styled.div`
    padding: 0.5rem;
    overflow-y: auto;
    flex: 1;

    hr {
      margin: 0.75rem 0;
      opacity: 0.2;
      border-color: ${props => props.theme.sidebar.border};
    }
  `;

  const NavList = styled.ul`
    list-style: none;
    padding: 0;
    margin: 0;
  `;

  const NavItem = styled.li`
    margin-bottom: 0.25rem;
  `;

  const NavLink = styled(Link)`
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    color: ${props => props.theme.sidebar.text};
    text-decoration: none;
    border-radius: 6px;
    transition: all 0.2s ease;
    gap: 0.75rem;
    
    &:hover {
      background: ${props => props.theme.sidebar.hoverBg};
      color: ${props => props.theme.sidebar.hoverText};
    }
  `;

  const NavText = styled.span`
    font-size: 0.95rem;
  `;

  const SidebarHeading = styled.h6`
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1rem 1rem 0.5rem;
    color: ${props => props.theme.sidebar.mutedText};
  `;

  const MainContent = styled.div`
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  `;

  const PageContent = styled.div`
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    background: ${props => props.theme.background};
  `;

  const Badge = styled.span`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: ${props => props.theme.badge.background};
    color: ${props => props.theme.badge.text};
    border-radius: 12px;
    padding: 0.15rem 0.5rem;
    font-size: 0.75rem;
    margin-left: 0.5rem;
  `;

  return (
    <AppContainer>
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen}>
        <SidebarLogo>
          <h4>SMART NOTES</h4>
        </SidebarLogo>
        <SidebarNav>
          <NavList>
            <NavItem>
              <NavLink to="/dashboard">
                <FaHome /> <NavText>Inicio</NavText>
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink to="/notes">
                <FaStickyNote /> <NavText>Mis Notas</NavText>
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink to="/graph">
                <FaProjectDiagram /> <NavText>Mapa Mental</NavText>
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink to="/upload">
                <FaCloudUploadAlt /> <NavText>Subir Imagen/PDF</NavText>
              </NavLink>
            </NavItem>
          </NavList>
          <hr />
          <SidebarHeading>Etiquetas</SidebarHeading>
          <NavList>
            {isLoading ? (
              <NavItem>
                <NavLink to="#" as="div">
                  <FaSpinner className="fa-spin" /> <NavText>Cargando...</NavText>
                </NavLink>
              </NavItem>
            ) : tags.length > 0 ? (
              tags.map((tag) => (
                <NavItem key={tag.id}>
                  <NavLink to={`/notes?tags=${tag.name}`}>
                    <FaTag /> 
                    <NavText>
                      {tag.name}
                      {tag.count && <Badge>{tag.count}</Badge>}
                    </NavText>
                  </NavLink>
                </NavItem>
              ))
            ) : (
              <NavItem>
                <NavLink to="#" as="div">
                  <FaInfoCircle /> <NavText>No hay etiquetas</NavText>
                </NavLink>
              </NavItem>
            )}
          </NavList>
        </SidebarNav>
      </Sidebar>

      {/* Contenido principal */}
      <MainContent>
        {/* Header */}
        <Header toggleSidebar={toggleSidebar} sidebarOpen={sidebarOpen} />

        {/* Contenido de la página (Outlet renderizará la ruta anidada) */}
        <PageContent>
          <Outlet />
        </PageContent>
      </MainContent>
    </AppContainer>
  );
};

export default AppLayout;
