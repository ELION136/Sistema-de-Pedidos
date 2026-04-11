#!/bin/bash
# Script de configuración inicial del Sistema de Gestión de Pedidos

echo "=========================================="
echo "  Sistema de Gestión de Pedidos - Setup"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 encontrado${NC}"

# Verificar pip
if ! command -v pip &> /dev/null; then
    echo -e "${RED}Error: pip no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ pip encontrado${NC}"

# Crear entorno virtual
echo ""
echo "Creando entorno virtual..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ El directorio venv ya existe${NC}"
    read -p "¿Desea eliminarlo y crear uno nuevo? (s/n): " respuesta
    if [ "$respuesta" = "s" ]; then
        rm -rf venv
        python3 -m venv venv
    fi
else
    python3 -m venv venv
fi

echo -e "${GREEN}✓ Entorno virtual creado${NC}"

# Activar entorno virtual
echo ""
echo "Activando entorno virtual..."
source venv/bin/activate

echo -e "${GREEN}✓ Entorno virtual activado${NC}"

# Instalar dependencias
echo ""
echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# Crear archivo .env si no existe
echo ""
if [ ! -f ".env" ]; then
    echo "Creando archivo .env..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Archivo .env creado. Por favor, edítelo con sus configuraciones.${NC}"
else
    echo -e "${YELLOW}⚠ El archivo .env ya existe${NC}"
fi

# Crear directorios necesarios
echo ""
echo "Creando directorios..."
mkdir -p logs
mkdir -p media/importaciones
mkdir -p static
mkdir -p staticfiles

echo -e "${GREEN}✓ Directorios creados${NC}"

# Mensaje final
echo ""
echo "=========================================="
echo -e "${GREEN}  Configuración completada!${NC}"
echo "=========================================="
echo ""
echo "Pasos siguientes:"
echo ""
echo "1. Configurar la base de datos PostgreSQL:"
echo "   createdb gestion_pedidos"
echo ""
echo "2. Editar el archivo .env con tus configuraciones"
echo ""
echo "3. Ejecutar migraciones:"
echo "   python manage.py migrate"
echo ""
echo "4. Crear superusuario:"
echo "   python manage.py createsuperuser"
echo ""
echo "5. Iniciar servidor:"
echo "   python manage.py runserver"
echo ""
echo "=========================================="