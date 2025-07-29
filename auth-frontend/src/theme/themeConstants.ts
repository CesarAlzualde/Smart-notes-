// Definición de tipos para el tema
// Interfaces de componentes específicos
export interface HeaderTheme {
  background: string;
  text: string;
  icons: string;
  hoverBg: string;
}

export interface SidebarTheme {
  background: string;
  text: string;
  hoverBg: string;
  hoverText: string;
  activeBackground: string;
  activeText: string;
  border: string;
  mutedText: string;
}

export interface BadgeTheme {
  background: string;
  text: string;
}

export interface CardTheme {
  background: string;
  shadow: string;
  highlightShadow: string;
}

export interface ButtonTheme {
  primaryBg: string;
  primaryHoverBg: string;
  secondaryBg: string;
  secondaryHoverBg: string;
  disabledBg: string;
  primaryText: string;
  secondaryText: string;
  disabledText: string;
}

export interface InputTheme {
  border: string;
  focusBorder: string;
  background: string;
  placeholder: string;
}

export interface SpinnerTheme {
  primary: string;
  secondary: string;
}

// Interfaz completa del tema
export interface Theme {
  // Colores principales
  primary: string;
  primaryDark: string;
  primaryLight: string;
  secondary: string;
  secondaryDark: string;
  secondaryLight: string;
  
  // Colores de texto
  text: string;
  textLight: string;
  textMuted: string;
  
  // Colores de fondo
  background: string;
  backgroundLight: string;
  backgroundDark: string;
  paper: string;
  
  // Colores de estado
  success: string;
  successLight: string;
  warning: string;
  warningLight: string;
  error: string;
  errorLight: string;
  info: string;
  infoLight: string;
  
  // Colores de borde
  border: string;
  borderLight: string;
  
  // Componentes específicos
  header: HeaderTheme;
  sidebar: SidebarTheme;
  badge: BadgeTheme;
  card: CardTheme;
  button: ButtonTheme;
  input: InputTheme;
  spinner: SpinnerTheme;
  
  // Sombras
  shadows: {
    sm: string;
    md: string;
    lg: string;
  };
}

// Tema claro
export const lightTheme: Theme = {
  // Colores principales
  primary: '#4776E6',
  primaryDark: '#3D6AD9',
  primaryLight: '#5A8EFF',
  secondary: '#8E54E9',
  secondaryDark: '#7F4BD2',
  secondaryLight: '#9D63FF',
  
  // Colores de texto
  text: '#2D3748',
  textLight: '#4A5568',
  textMuted: '#718096',
  
  // Colores de fondo
  background: '#F7FAFC',
  backgroundLight: '#FFFFFF',
  backgroundDark: '#EDF2F7',
  paper: '#FFFFFF',
  
  // Colores de estado
  success: '#38B2AC',
  successLight: '#E6FFFA',
  warning: '#ED8936',
  warningLight: '#FEEBC8',
  error: '#E53E3E',
  errorLight: '#FED7D7',
  info: '#4299E1',
  infoLight: '#BEE3F8',
  
  // Colores de borde
  border: '#E2E8F0',
  borderLight: '#EDF2F7',
  
  // Componentes específicos
  header: {
    background: '#FFFFFF',
    text: '#303030',
    icons: '#5A73FC',
    hoverBg: 'rgba(90, 115, 252, 0.1)'
  },
  sidebar: {
    background: '#FFFFFF',
    text: '#303030',
    hoverBg: 'rgba(90, 115, 252, 0.1)',
    hoverText: '#4776E6',
    activeBackground: 'rgba(71, 118, 230, 0.1)',
    activeText: '#4776E6',
    border: '#E5E7EB',
    mutedText: '#6C757D'
  },
  badge: {
    background: 'rgba(71, 118, 230, 0.1)',
    text: '#4776E6'
  },
  card: {
    background: '#FFFFFF',
    shadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
    highlightShadow: '0 4px 12px rgba(71, 118, 230, 0.2)'
  },
  button: {
    primaryBg: '#4776E6',
    primaryText: '#FFFFFF',
    primaryHoverBg: '#3D6AD9',
    secondaryBg: '#8E54E9',
    secondaryText: '#FFFFFF',
    secondaryHoverBg: '#7F4BD2',
    disabledBg: '#CBD5E0',
    disabledText: '#718096',
  },
  input: {
    border: '#DFE2E6',
    focusBorder: '#4776E6',
    background: '#FFFFFF',
    placeholder: '#ADB5BD'
  },
  spinner: {
    primary: '#4776E6',
    secondary: '#8E54E9',
  },
  
  // Sombras
  shadows: {
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  },
};

// Tema oscuro
export const darkTheme: Theme = {
  // Colores principales
  primary: '#5A8EFF',
  primaryDark: '#4776E6',
  primaryLight: '#6B9CFF',
  secondary: '#9D63FF',
  secondaryDark: '#8E54E9',
  secondaryLight: '#B47EFF',
  
  // Colores de texto
  text: '#F7FAFC',
  textLight: '#E2E8F0',
  textMuted: '#A0AEC0',
  
  // Colores de fondo
  background: '#171923',
  backgroundLight: '#1A202C',
  backgroundDark: '#0B0E14',
  paper: '#1A202C',
  
  // Colores de estado
  success: '#38B2AC',
  successLight: '#1D4044',
  warning: '#ED8936',
  warningLight: '#513C06',
  error: '#E53E3E',
  errorLight: '#5F1D1D',
  info: '#4299E1',
  infoLight: '#1A365D',
  
  // Colores de borde
  border: '#2D3748',
  borderLight: '#4A5568',
  
  // Componentes específicos
  header: {
    background: '#1E1E1E',
    text: '#E5E5E5',
    icons: '#6B9FFF',
    hoverBg: 'rgba(106, 159, 255, 0.15)'
  },
  sidebar: {
    background: '#1E1E1E',
    text: '#E5E5E5',
    hoverBg: 'rgba(106, 159, 255, 0.15)',
    hoverText: '#6B9FFF',
    activeBackground: 'rgba(106, 159, 255, 0.2)',
    activeText: '#6B9FFF',
    border: '#333333',
    mutedText: '#A0A0A0'
  },
  badge: {
    background: 'rgba(106, 159, 255, 0.2)',
    text: '#6B9FFF'
  },
  card: {
    background: '#1E1E1E',
    shadow: '0 2px 10px rgba(0, 0, 0, 0.3)',
    highlightShadow: '0 4px 12px rgba(106, 159, 255, 0.3)'
  },
  button: {
    primaryBg: '#5A8EFF',
    primaryText: '#1A202C',
    primaryHoverBg: '#6B9CFF',
    secondaryBg: '#9D63FF',
    secondaryText: '#1A202C',
    secondaryHoverBg: '#B47EFF',
    disabledBg: '#4A5568',
    disabledText: '#CBD5E0',
  },
  input: {
    border: '#333333',
    focusBorder: '#5A8EFF',
    background: '#2D2D2D',
    placeholder: '#666666'
  },
  spinner: {
    primary: '#5A8EFF',
    secondary: '#9D63FF',
  },
  
  // Sombras
  shadows: {
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
  },
};
