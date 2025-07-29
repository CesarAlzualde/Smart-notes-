# 📦 **INSTALADOR PROFESIONAL - APUNTES 2.0**

## 🚀 **Cómo crear el instalador**

### **Método Automático (Recomendado)**
```bash
# Ejecuta este archivo para crear todo automáticamente:
📦 Crear Instalador.bat
```

### **Método Manual**
1. **Preparar Backend:**
   ```bash
   cd backend
   pyinstaller ApuntesBackend.spec
   ```

2. **Construir Frontend:**
   ```bash
   cd auth-frontend
   npm install
   npm run build
   npm run dist
   ```

## 📋 **Qué incluye el instalador**

### **✅ Funcionalidades Completas:**
- 🧠 **Backend Flask** empaquetado con PyInstaller
- ⚛️ **Frontend React** con Vite + Electron
- 🗄️ **Neo4j** para mapas conceptuales
- 👁️ **Google Vision API** para OCR premium
- 🤖 **Servicios de IA** completos (resumen, análisis, NER)
- 🔐 **Autenticación JWT** segura

### **📦 Archivos Incluidos:**
- `ApuntesBackend.exe` - Servidor Flask empaquetado
- `Apuntes 2.0.exe` - Aplicación Electron principal
- `config/` - Configuraciones y credenciales
- `.env` - Variables de entorno
- Todas las dependencias necesarias

### **🎯 Instalación Automática:**
- ✅ Crea accesos directos en escritorio
- ✅ Añade al menú inicio
- ✅ Configura directorios de datos
- ✅ Instala dependencias del sistema
- ✅ Configuración automática completa

## 🔧 **Requisitos del Sistema**

### **Para CREAR el instalador:**
- Windows 10/11
- Node.js 18+ instalado
- Python 3.8+ con PyInstaller
- Neo4j Desktop (opcional, para mapas)

### **Para USAR la aplicación (usuario final):**
- Windows 10/11
- **¡SOLO ESO!** - Todo viene incluido en el instalador

## 📁 **Estructura del Instalador**

```
📦 Apuntes 2.0 - Sistema de Notas con IA - Setup.exe
│
├── 🖥️ Aplicación Principal (Electron)
├── 🔧 Backend Flask (Puerto 5000)
├── 📊 Base de Datos SQLite
├── 🧠 Modelos de IA preentrenados
├── 👁️ OCR con Tesseract + Google Vision
├── 🗄️ Integración Neo4j (opcional)
└── ⚙️ Configuración automática
```

## 🔥 **Características del Instalador**

### **🎨 Interfaz Profesional:**
- Installer NSIS personalizado
- Mensajes informativos durante instalación
- Progreso detallado paso a paso
- Desinstalador completo incluido

### **🛡️ Seguridad:**
- Firma digital (opcional - requiere certificado)
- Verificación de integridad
- Instalación sin permisos de administrador
- Datos de usuario protegidos

### **📊 Estadísticas:**
- Tamaño aproximado: ~500MB
- Tiempo de instalación: 2-3 minutos
- Detección automática de dependencias
- Logs detallados de instalación

## 🚀 **Distribución**

### **Archivo Final:**
- **Nombre:** `Apuntes 2.0 - Sistema de Notas con IA - Setup.exe`
- **Ubicación:** `auth-frontend/dist-electron/`
- **Tamaño:** ~500MB (todo incluido)

### **Cómo Distribuir:**
1. ✅ Comparte el archivo `.exe` generado
2. ✅ Usuario ejecuta el instalador
3. ✅ ¡Todo funciona automáticamente!

## 🆘 **Solución de Problemas**

### **Error: "Backend no empaquetado"**
```bash
cd backend
pyinstaller ApuntesBackend.spec
```

### **Error: "Node.js no encontrado"**
- Instala Node.js desde: https://nodejs.org

### **Error: "Dependencias faltantes"**
```bash
cd auth-frontend
npm install --force
```

### **Error: "Icono no encontrado"**
- El script crea uno automáticamente
- O agrega manualmente `auth-frontend/assets/icon.ico`

## 🎯 **Personalización**

### **Cambiar Icono:**
1. Reemplaza `auth-frontend/assets/icon.ico`
2. Formato: 256x256 px, .ico

### **Modificar Instalador:**
- Edita `auth-frontend/installer.nsh`
- Personaliza mensajes y comportamiento

### **Cambiar Nombre:**
- Edita `productName` en `auth-frontend/package.json`

---

## 🎉 **¡Listo para Producción!**

Tu instalador profesional incluye:
- ✅ **Sistema completo** funcional offline
- ✅ **Todas las dependencias** incluidas  
- ✅ **Instalación automática** sin complicaciones
- ✅ **Interfaz profesional** lista para distribución

**¡Comparte tu instalador y que otros disfruten de Apuntes 2.0!** 🚀
