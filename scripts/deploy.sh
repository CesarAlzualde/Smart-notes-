#!/bin/bash

# ===================================================
# Script de despliegue para Proyecto Apuntes
# Plataforma: EC2 Ubuntu 22.04
# Componentes: Nginx, Gunicorn, PostgreSQL y Neo4j en Docker
# ===================================================

set -e  # Detener ejecución si ocurre un error

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

# Función para imprimir mensajes con formato
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Variables de configuración (pueden ser modificadas)
APP_NAME="proyecto-apuntes"
APP_DIR="/opt/$APP_NAME"
GIT_REPO="https://github.com/usuario/$APP_NAME.git"  # Reemplazar con URL real
VENV_DIR="$APP_DIR/.venv"
NGINX_CONF="/etc/nginx/sites-available/$APP_NAME"
DB_NAME="apuntes_db"
DB_USER="apuntes_user"
DB_PASSWORD="${NEO4J_PASSWORD:-password123}"  # Usar variable de entorno o valor por defecto
NEO4J_PASSWORD="${NEO4J_PASSWORD:-password123}"
DB_URL="postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"

# ===================================================
# 1. Actualizar sistema e instalar dependencias básicas
# ===================================================
log "Actualizando sistema e instalando dependencias básicas..."
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv git nginx poppler-utils tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng postgresql postgresql-contrib docker.io docker-compose curl

# Habilitar y arrancar servicios
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl enable postgresql
sudo systemctl start postgresql

# ===================================================
# 2. Configurar PostgreSQL
# ===================================================
log "Configurando PostgreSQL..."
# Crear usuario y base de datos
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# ===================================================
# 3. Configurar Neo4j con Docker
# ===================================================
log "Configurando Neo4j con Docker..."
# Crear directorio para datos persistentes
sudo mkdir -p /var/lib/neo4j/data
sudo mkdir -p /var/lib/neo4j/logs
sudo mkdir -p /var/lib/neo4j/import

# Crear docker-compose.yml para Neo4j
cat > /tmp/docker-compose.yml << EOF
version: '3'
services:
  neo4j:
    image: neo4j:5.14.0
    container_name: neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/$NEO4J_PASSWORD
    volumes:
      - /var/lib/neo4j/data:/data
      - /var/lib/neo4j/logs:/logs
      - /var/lib/neo4j/import:/import
    restart: always
EOF

# Mover el archivo a la ubicación correcta
sudo mv /tmp/docker-compose.yml /opt/docker-compose.yml

# Iniciar Neo4j
cd /opt && sudo docker-compose up -d

# ===================================================
# 4. Clonar repositorio y configurar entorno
# ===================================================
log "Clonando repositorio y configurando entorno..."
# Crear directorio de la aplicación
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clonar repositorio
git clone $GIT_REPO $APP_DIR || error "No se pudo clonar el repositorio"

# Crear entorno virtual e instalar dependencias
cd $APP_DIR
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# ===================================================
# 5. Configurar variables de entorno
# ===================================================
log "Configurando variables de entorno..."
# Crear archivo .env
cat > $APP_DIR/.env << EOF
DB_URL=$DB_URL
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=$NEO4J_PASSWORD
FLASK_APP=app.py
FLASK_ENV=production
PORT=8000
EOF

# Crear script para cargar variables de entorno
cat > $APP_DIR/load_env.sh << EOF
#!/bin/bash
export DB_URL="$DB_URL"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="$NEO4J_PASSWORD"
export FLASK_APP="app.py"
export FLASK_ENV="production"
export PORT="8000"
EOF

chmod +x $APP_DIR/load_env.sh

# ===================================================
# 6. Configurar Gunicorn como servicio
# ===================================================
log "Configurando Gunicorn como servicio..."
# Crear archivo de servicio systemd
cat > /tmp/gunicorn.service << EOF
[Unit]
Description=Gunicorn para $APP_NAME
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# ===================================================
# 7. Configurar Nginx como proxy inverso
# ===================================================
log "Configurando Nginx como proxy inverso..."
# Crear configuración de Nginx
cat > /tmp/nginx.conf << EOF
server {
    listen 80;
    server_name _;  # Cambiar por dominio real si está disponible

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
    }

    location /uploads {
        alias $APP_DIR/uploads;
    }

    client_max_body_size 16M;
}
EOF

sudo mv /tmp/nginx.conf $NGINX_CONF
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
sudo nginx -t || error "Configuración de Nginx inválida"
sudo systemctl restart nginx

# ===================================================
# 8. Configurar directorio de uploads
# ===================================================
log "Configurando directorio de uploads..."
sudo mkdir -p $APP_DIR/uploads
sudo chown -R $USER:www-data $APP_DIR/uploads
sudo chmod -R 775 $APP_DIR/uploads

# ===================================================
# 9. Verificar instalación
# ===================================================
log "Verificando instalación..."
# Comprobar que todos los servicios estén funcionando
GUNICORN_STATUS=$(systemctl is-active gunicorn)
NGINX_STATUS=$(systemctl is-active nginx)
POSTGRESQL_STATUS=$(systemctl is-active postgresql)
NEO4J_STATUS=$(docker ps | grep neo4j | wc -l)

if [ "$GUNICORN_STATUS" = "active" ] && [ "$NGINX_STATUS" = "active" ] && [ "$POSTGRESQL_STATUS" = "active" ] && [ "$NEO4J_STATUS" -gt 0 ]; then
    log "Todos los servicios están funcionando correctamente"
    log "La aplicación debería estar disponible en: http://$(curl -s ifconfig.me)"
else
    warn "Algunos servicios no están funcionando correctamente:"
    [ "$GUNICORN_STATUS" != "active" ] && warn "- Gunicorn: $GUNICORN_STATUS"
    [ "$NGINX_STATUS" != "active" ] && warn "- Nginx: $NGINX_STATUS"
    [ "$POSTGRESQL_STATUS" != "active" ] && warn "- PostgreSQL: $POSTGRESQL_STATUS"
    [ "$NEO4J_STATUS" -eq 0 ] && warn "- Neo4j: No está ejecutándose"
    warn "Revisa los logs para más información:"
    warn "  - Gunicorn: sudo journalctl -u gunicorn"
    warn "  - Nginx: sudo tail -n 50 /var/log/nginx/error.log"
    warn "  - Neo4j: sudo docker logs neo4j"
fi

log "Despliegue completado. Recuerda actualizar las variables de entorno según sea necesario."
