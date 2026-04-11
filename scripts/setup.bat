@echo off
chcp 65001 >nul
REM Script de configuración inicial para Windows

echo ==========================================
echo   Sistema de Gestión de Pedidos - Setup
echo ==========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH
    exit /b 1
)
echo [OK] Python encontrado

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip no está instalado
    exit /b 1
)
echo [OK] pip encontrado

REM Crear entorno virtual
echo.
echo Creando entorno virtual...
if exist venv (
    echo [ADVERTENCIA] El directorio venv ya existe
    set /p respuesta="¿Desea eliminarlo y crear uno nuevo? (s/n): "
    if /i "%respuesta%"=="s" (
        rmdir /s /q venv
        python -m venv venv
    )
) else (
    python -m venv venv
)
echo [OK] Entorno virtual creado

REM Activar entorno virtual
echo.
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado

REM Instalar dependencias
echo.
echo Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Dependencias instaladas

REM Crear archivo .env si no existe
echo.
if not exist .env (
    echo Creando archivo .env...
    copy .env.example .env
    echo [ADVERTENCIA] Archivo .env creado. Por favor, edítelo con sus configuraciones.
) else (
    echo [ADVERTENCIA] El archivo .env ya existe
)

REM Crear directorios necesarios
echo.
echo Creando directorios...
if not exist logs mkdir logs
if not exist media\importaciones mkdir media\importaciones
if not exist static mkdir static
if not exist staticfiles mkdir staticfiles
echo [OK] Directorios creados

REM Mensaje final
echo.
echo ==========================================
echo   Configuración completada!
echo ==========================================
echo.
echo Pasos siguientes:
echo.
echo 1. Configurar la base de datos PostgreSQL:
echo    createdb gestion_pedidos
echo.
echo 2. Editar el archivo .env con tus configuraciones
echo.
echo 3. Ejecutar migraciones:
echo    python manage.py migrate
echo.
echo 4. Crear superusuario:
echo    python manage.py createsuperuser
echo.
echo 5. Iniciar servidor:
echo    python manage.py runserver
echo.
echo ==========================================

pause