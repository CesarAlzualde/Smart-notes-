@echo off
echo Limpiando dependencias problemáticas...

:: Desinstalar solo TensorFlow y sus dependencias problemáticas (mantenemos transformers)
pip uninstall -y tensorflow tensorflow-io-gcs-filesystem grpcio-status

echo Instalando dependencias básicas necesarias...

:: Instalar Flask y autenticación
pip install flask==3.1.1 flask-cors==5.0.1 werkzeug==3.1.3
pip install flask-jwt-extended==4.6.0 passlib==1.7.4 gunicorn==23.0.0 python-dotenv==0.21.1

:: Instalar base de datos
pip install psycopg2-binary==2.9.9 sqlalchemy==2.0.28 flask-sqlalchemy==3.1.1
pip install flask-migrate==4.0.5 alembic==1.13.1

:: Instalar task queue
pip install celery==5.3.6 redis==5.0.1

echo Instalando dependencias OCR...
pip install pytesseract==0.3.13 pillow==11.2.1 pdf2image==1.16.3
pip install opencv-python poppler-utils==0.1.0

echo Instalando ML con PyTorch (sin TensorFlow)...
:: Instalar PyTorch CPU first para evitar dependencias CUDA innecesarias
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

:: Instalar transformers con versiones específicas para evitar conflictos
pip install transformers==4.35.2 tokenizers==0.14.1
pip install sentence-transformers==2.3.1
pip install scikit-learn==1.4.0

echo Instalando utilidades...
pip install numpy==1.26.4 tqdm==4.67.1 requests==2.32.3
pip install neo4j==5.14.0

echo Instalando Google Vision con protobuf compatible...
:: Instalar protobuf específico compatible con google-cloud-vision
pip install "protobuf>=4.21.6,<5.0.0"
pip install google-cloud-vision==3.4.5

echo Instalando NLTK para fallbacks...
pip install nltk==3.8.1

echo ¡Dependencias instaladas correctamente!
echo Verificando conflictos...
pip check

echo Descargando datos NLTK necesarios...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

echo ¡Setup completo!
