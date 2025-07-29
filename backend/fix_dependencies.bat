@echo off
echo Limpiando dependencias problemáticas...

:: Desinstalar paquetes que causan conflictos
pip uninstall -y tensorflow tensorflow-io-gcs-filesystem grpcio-status protobuf transformers google-cloud-vision

echo Instalando dependencias básicas necesarias...

:: Instalar solo las dependencias esenciales
pip install flask==3.1.1 flask-cors==5.0.1 werkzeug==3.1.3
pip install flask-jwt-extended==4.6.0 passlib==1.7.4
pip install psycopg2-binary==2.9.9 sqlalchemy==2.0.28 flask-sqlalchemy==3.1.1
pip install flask-migrate==4.0.5 alembic==1.13.1
pip install celery==5.3.6 redis==5.0.1

echo Instalando dependencias OCR...
pip install pytesseract==0.3.13 pillow==11.2.1 pdf2image==1.16.3
pip install opencv-python
pip install poppler-utils==0.1.0

echo Instalando ML básico...
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers==2.3.1
pip install scikit-learn==1.4.0

echo Instalando utilidades...
pip install numpy==1.26.4 tqdm==4.67.1 requests==2.32.3
pip install neo4j==5.14.0 gunicorn==23.0.0 python-dotenv==0.21.1

echo Instalando Google Vision con versión compatible...
pip install google-cloud-vision==3.4.5

echo ¡Dependencias instaladas correctamente!
echo Verificando conflictos...
pip check
