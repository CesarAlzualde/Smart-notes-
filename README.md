# 🧠 Smart Notes - Sistema de Notas con IA

Un sistema avanzado de gestión de notas con OCR, análisis de texto y visualización de grafos de conocimiento.

---

## 🚀 Características

- 🔐 **Autenticación Segura:** Con JWT (JSON Web Tokens).
- 📸 **OCR (Reconocimiento Óptico de Caracteres):** Extrae texto de imágenes y PDFs.
- ✍️ **Gestión de Notas Enriquecida:** Un editor completo con etiquetado y búsqueda avanzada.
- 🤖 **Análisis de Texto con IA:** Extrae automáticamente temas y conceptos clave de tus notas.
- 🕸️ **Visualización de Conocimiento:** Grafos interactivos para conectar ideas y descubrir nuevos insights.
- 🔌 **API REST Completa:** Para una fácil integración con otros sistemas.

---

## 🛠️ Arquitectura y Stack Tecnológico

Este proyecto utiliza un stack de tecnología moderno para ofrecer sus funcionalidades avanzadas.

### ⚙️ Backend (Flask)

- **Framework:** **Flask** es el núcleo de la API REST.
- **Base de Datos:** **PostgreSQL** para almacenar datos primarios como usuarios y notas.
- **Base de Datos de Grafos:** **Neo4j** se usa para almacenar y consultar los grafos de conocimiento, gestionado a través del driver oficial de Python.
- **Procesamiento de Grafos en Memoria:** **NetworkX** se utiliza para construir y manipular grafos en memoria antes de persistirlos.
- **IA y NLP (Procesamiento de Lenguaje Natural):**
  - **OCR (Reconocimiento Óptico de Caracteres):**
    - **Tesseract:** Motor de OCR de código abierto para el procesamiento local de imágenes y PDFs.
    - **Google Cloud Vision:** API avanzada para un reconocimiento de texto de alta precisión como opción secundaria.
  - **Análisis de Texto y Resúmenes:**
    - **Modelos de Resumen:** Utiliza modelos de vanguardia de Hugging Face para la generación de resúmenes abstractivos. El modelo principal es `facebook/bart-large-cnn`, conocido por su alta calidad en textos multilingües. Se configuran también modelos de respaldo como `josmunpen/mt5-small-spanish-summarization`.
    - **Análisis Semántico y Clasificación:** Para entender el significado y las relaciones en el texto, se utiliza el modelo `sentence-transformers/all-MiniLM-L6-v2`. Este convierte el texto en vectores numéricos (embeddings) que se usan para:
      - **Análisis de Similitud:** Encontrar notas y conceptos relacionados semánticamente.
      - **Clasificación Temática:** Agrupar notas por temas comunes utilizando los embeddings generados.
    - **Librerías de Soporte:**
      - **NLTK (Natural Language Toolkit):** Usado para tareas fundamentales de NLP como tokenización.
      - **PyTorch:** Sirve como el motor de *deep learning* para ejecutar los modelos de Transformers.

### 🎨 Frontend (React)

- **Framework:** **React** (con Vite) para una interfaz de usuario rápida e interactiva.
- **Componentes de UI:** **React Bootstrap** para un sistema de diseño consistente y adaptable.
- **Visualización de Grafos:** **React Force Graph** se utiliza para renderizar los grafos de conocimiento interactivos en 2D.
- **Gestión de Estado:** Zustand para una gestión de estado ligera y eficiente.

---

## ✅ Requisitos Previos

- **Python 3.8+**
- **Node.js 16+**
- **PostgreSQL 12+**
- **Base de datos Neo4j** (en ejecución y accesible)

---

## 🚀 Instalación y Desarrollo

Esta guía es para configurar un entorno de desarrollo local. Los instaladores de producción (`.exe`, `.asar`) **no están** en este repositorio y deben descargarse desde la página de **[Releases](https://github.com/CesarAlzualde/Smart-notes-/releases)** del proyecto.

### 1. Clonar el Repositorio

```bash
git clone https://github.com/CesarAlzualde/Smart-notes-.git
cd Smart-notes-
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (puedes copiar `.env.example`). Es crucial para las credenciales de la base de datos y las claves de API.

```dotenv
# Ejemplo de .env
DATABASE_URL=postgresql://user:password@localhost:5432/smartnotes_db
JWT_SECRET_KEY=tu-clave-super-secreta
UPLOAD_FOLDER=./uploads

# Credenciales de Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tu-password-de-neo4j
```

### 3. Configuración del Backend (Flask)

```bash
# Navega al directorio del backend
cd backend

# Crea y activa un entorno virtual
python -m venv venv
# En Windows: venv\Scripts\activate
# En macOS/Linux: source venv/bin/activate

# Instala las dependencias
pip install -r requirements.txt

# Inicializa y migra la base de datos
flask db upgrade

# Ejecuta el servidor de desarrollo
flask run --debug
```

### 4. Configuración del Frontend (React)

```bash
# Navega al directorio del frontend
cd auth-frontend

# Instala las dependencias
npm install

# Ejecuta el servidor de desarrollo
npm run dev
```

---

---

## 🧪 Pruebas

El proyecto utiliza `pytest` para las pruebas automatizadas. Para ejecutar las pruebas del backend, sigue estos pasos:

```bash
# Navega al directorio del backend
cd backend

# Asegúrate de que tu entorno virtual esté activado
# (venv\Scripts\activate en Windows o source venv/bin/activate en macOS/Linux)

# Instala las dependencias de desarrollo (si no lo has hecho)
pip install -r requirements.txt

# Ejecuta las pruebas
pytest
```

---

## 📂 Estructura del Proyecto

```plaintext
.
├── backend/          # Código fuente de la API de Flask
│   ├── app/          # Módulos principales de la aplicación
│   ├── migrations/   # Migraciones de la base de datos
│   └── tests/        # Pruebas automatizadas
├── auth-frontend/    # Código fuente de la aplicación React
│   └── src/          # Código principal del frontend
├── build_scripts/    # Scripts de compilación y empaquetado
├── tools/            # Scripts de utilidad y mantenimiento
├── uploads/          # (Local) Directorio para archivos subidos (ignorado por Git)
├── .gitignore        # Archivos y carpetas ignorados por Git
└── README.md         # Este archivo
```

---

## ❤️ Contribuciones

¡Las contribuciones son bienvenidas! Por favor, abre un *issue* para discutir tus ideas o envía un *pull request*.

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 📚 Referencias

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de React](https://reactjs.org/)
- [Documentación de Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Google Cloud Vision API](https://cloud.google.com/vision)
