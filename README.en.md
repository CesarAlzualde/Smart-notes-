# 🧠 Smart Notes - AI-Powered Note-Taking System

An advanced note management system featuring OCR, text analysis, and knowledge graph visualization.

---

## 🚀 Features

- 🔐 **Secure Authentication:** JWT (JSON Web Tokens) for user authentication.
- 📸 **OCR (Optical Character Recognition):** Extract text from images and PDFs.
- ✍️ **Rich Note Management:** A full-featured editor with tagging and advanced search.
- 🤖 **AI-Powered Text Analysis:** Automatically extract key topics and concepts from your notes.
- 🕸️ **Knowledge Visualization:** Interactive relationship graphs to connect ideas and discover insights.
- 🔌 **Complete REST API:** For easy integration with other systems.

---

## 🛠️ Architecture and Tech Stack

This project uses a modern technology stack to deliver its advanced features.

### ⚙️ Backend (Flask)

- **Framework:** **Flask** serves as the core of the REST API.
- **Database:** **PostgreSQL** for storing primary data like users and notes.
- **Graph Database:** **Neo4j** is used to store and query the knowledge graphs, managed via the official Python driver.
- **In-Memory Graph Processing:** **NetworkX** is used to build and manipulate graphs in memory before they are persisted.
- **AI & NLP:**
  - **OCR (Optical Character Recognition):**
    - **Tesseract:** Open-source OCR engine for local processing of images and PDFs.
    - **Google Cloud Vision:** Advanced API for high-accuracy text recognition as a secondary option.
  - **Text Analysis & Summarization:**
    - **Summarization Models:** Utilizes state-of-the-art models from Hugging Face for abstractive summarization. The primary model is `facebook/bart-large-cnn`, known for its high-quality performance on multilingual texts. Backup models like `josmunpen/mt5-small-spanish-summarization` are also configured.
    - **Semantic Analysis and Classification:** To understand meaning and relationships in the text, the project uses the `sentence-transformers/all-MiniLM-L6-v2` model. This converts text into numerical vectors (embeddings) used for:
      - **Similarity Analysis:** Finding semantically related notes and concepts.
      - **Thematic Classification:** Grouping notes by common themes using the generated embeddings.
    - **Supporting Libraries:**
      - **NLTK (Natural Language Toolkit):** Used for fundamental NLP tasks like tokenization.
      - **PyTorch:** Serves as the deep learning backend for running the Transformers models.

### 🎨 Frontend (React)

- **Framework:** **React** (with Vite) for a fast and interactive user interface.
- **UI Components:** **React Bootstrap** for a consistent and responsive design system.
- **Graph Visualization:** **React Force Graph** is used to render the interactive 2D knowledge graphs.
- **State Management:** Zustand for lightweight and efficient state management.

---

## ✅ Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **PostgreSQL 12+**
- **Neo4j Database** (running and accessible)

---

## 🚀 Installation and Development

This guide is for setting up a local development environment. Production installers (`.exe`, `.asar`) are **not** in this repository and should be downloaded from the project's **[Releases](https://github.com/CesarAlzualde/Smart-notes-/releases)** page.

### 1. Clone the Repository

```bash
git clone https://github.com/CesarAlzualde/Smart-notes-.git
cd Smart-notes-
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (you can copy `.env.example`). This is crucial for database credentials and API keys.

```dotenv
# .env example
DATABASE_URL=postgresql://user:password@localhost:5432/smartnotes_db
JWT_SECRET_KEY=your-super-secret-key
UPLOAD_FOLDER=./uploads

# Neo4j Credentials
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```

### 3. Backend Setup (Flask)

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize and migrate the database
flask db upgrade

# Run the development server
flask run --debug
```

### 4. Frontend Setup (React)

```bash
# Navigate to the frontend directory
cd auth-frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

---

---

## 🧪 Testing

The project uses `pytest` for automated testing. To run the backend tests, follow these steps:

```bash
# Navigate to the backend directory
cd backend

# Make sure your virtual environment is activated
# (venv\Scripts\activate on Windows or source venv/bin/activate on macOS/Linux)

# Install development dependencies (if you haven't already)
pip install -r requirements.txt

# Run the tests
pytest
```

---

## 📂 Project Structure

```plaintext
.
├── backend/          # Flask API source code
│   ├── app/          # Core application modules
│   ├── migrations/   # Database migrations
│   └── tests/        # Automated tests
├── auth-frontend/    # React application source code
│   └── src/          # Main frontend code
├── build_scripts/    # Build and packaging scripts
├── tools/            # Utility and maintenance scripts
├── uploads/          # (Local) Directory for user uploads (ignored by Git)
├── .gitignore        # Files and folders ignored by Git
└── README.md         # This file
```

---

## ❤️ Contributions

Contributions are welcome! Please open an issue to discuss your ideas or submit a pull request.

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 📚 References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/)
- [Neo4j Python Driver Documentation](https://neo4j.com/docs/python-manual/current/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Google Cloud Vision API](https://cloud.google.com/vision)
