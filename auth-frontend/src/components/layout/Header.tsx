import React from 'react';
import styled from '@emotion/styled';
import { FaMoon, FaSun, FaUserCircle } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import { useTheme } from '../../theme/themeHooks';
import { useAuthStore } from '../../store/authStore';
import logoIcon from '../../assets/Gemini_Generated_Image_zft9nlzft9nlzft9.png';

interface HeaderProps {
  toggleSidebar: () => void;
  sidebarOpen: boolean;
}

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  background: #1E293B; /* Color oscuro que mantiene la paleta */
  color: #FFFFFF;
  transition: all 0.3s ease;
  width: 100%;
`;

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
`;

const LogoImage = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(71, 118, 230, 0.5);
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  
  &:hover {
    transform: scale(1.05);
  }
`;

const BrandLogo = styled.div`
  flex: 1;
  display: flex;
  justify-content: flex-start; /* Cambio de posición: alineado a la izquierda */
  align-items: center;
  margin-left: 1rem;
  
  img {
    height: 36px;
    object-fit: contain;
  }
`;

const SidebarToggle = styled.button`
  background: none;
  border: none;
  color: #64B5F6; /* Azul más claro para mejor contraste */
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.25rem;
  margin-right: 0.5rem;
  
  &:hover {
    background-color: rgba(100, 181, 246, 0.2);
  }
  
  &:focus {
    outline: none;
  }
`;

const ThemeToggle = styled.button`
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #64B5F6;
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  
  &:hover {
    background-color: rgba(100, 181, 246, 0.2);
  }
  
  &:focus {
    outline: none;
  }
`;

const UserMenu = styled.div`
  position: relative;
`;

const UserButton = styled.button`
  background: none;
  border: none;
  color: #64B5F6;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(100, 181, 246, 0.2);
  }
  
  span {
    margin-left: 0.5rem;
    color: #FFFFFF;
  }
  
  &:focus {
    outline: none;
  }
`;

const Dropdown = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 200px;
  background-color: #FFFFFF;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border-radius: 4px;
  z-index: 1000;
  overflow: hidden;
`;

const DropdownItem = styled(Link)`
  display: block;
  padding: 0.75rem 1rem;
  color: #4A5568;
  text-decoration: none;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: #EDF2F7;
  }
`;

const DropdownButton = styled.button`
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: #E53E3E;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: #EDF2F7;
  }
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const Header: React.FC<HeaderProps> = ({ toggleSidebar, sidebarOpen }) => {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuthStore();
  const [menuOpen, setMenuOpen] = React.useState(false);
  
  const toggleMenu = () => setMenuOpen(!menuOpen);
  
  // Importamos la función de logout del store de autenticación
  const { logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      console.log('Iniciando cierre de sesión...');
      await logout();
      console.log('Sesión cerrada exitosamente');
      // La redirección debe ocurrir automáticamente por el router después del logout
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    }
  };

  return (
    <HeaderContainer>
      <LogoContainer>
        <SidebarToggle onClick={toggleSidebar}>
          {sidebarOpen ? '✕' : '☰'}
        </SidebarToggle>
        <LogoImage>
          <img src={logoIcon} alt="Smart Notes" />
        </LogoImage>
      </LogoContainer>
      
      <BrandLogo>
        <span style={{
          fontSize: '1.2rem', 
          fontWeight: 'bold',
          background: 'linear-gradient(90deg, #4776E6 0%, #8E54E9 100%)',
          WebkitBackgroundClip: 'text',
          backgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          color: 'transparent',
          display: 'inline-block'
        }}>SMART NOTES</span>
      </BrandLogo>
      
      <UserSection>
        <ThemeToggle onClick={toggleTheme} title="Cambiar tema">
          {theme === 'dark' ? <FaSun /> : <FaMoon />}
        </ThemeToggle>
        
        {user ? (
          <UserMenu>
            <UserButton onClick={toggleMenu}>
              <FaUserCircle />
              <span>{user.name}</span>
            </UserButton>
            
            {menuOpen && (
              <Dropdown>
                <DropdownItem to="/profile">Mi Perfil</DropdownItem>
                <DropdownItem to="/settings">Configuración</DropdownItem>
                <DropdownButton onClick={handleLogout}>Cerrar Sesión</DropdownButton>
              </Dropdown>
            )}
          </UserMenu>
        ) : (
          <Link to="/login" style={{ textDecoration: 'none', color: 'inherit' }}>
            <UserButton>
              <FaUserCircle />
              <span>Iniciar Sesión</span>
            </UserButton>
          </Link>
        )}
      </UserSection>
    </HeaderContainer>
  );
};

export default Header;
