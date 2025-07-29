# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para Tesseract y Poppler
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn && \
    rm -rf /root/.cache/pip

# Crear directorio para uploads
RUN mkdir -p uploads

# Copiar el resto de la aplicación
COPY . .

# Verificar que Tesseract está instalado correctamente
RUN tesseract --version

# Puerto expuesto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]