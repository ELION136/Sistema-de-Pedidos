# Sistema de Gestión de Pedidos - Ropa Deportiva

Sistema web completo para la gestión de pedidos de una PYME que fabrica ropa deportiva para colegios. Desarrollado con Django y PostgreSQL.

## 🎯 Características Principales

- ✅ **Gestión de Clientes** (Colegios e Instituciones)
- ✅ **Gestión de Pedidos** con código automático
- ✅ **Registro de Prendas** individuales o por conjuntos
- ✅ **Importación desde Excel** con vista previa y validación
- ✅ **Clasificación Automática** por tipo, género y talla
- ✅ **Módulo de Producción** con órdenes y planificación
- ✅ **Gestión de Materia Prima** requerida
- ✅ **Reportes** listos para imprimir

## 🚀 Instalación Rápida

### Requisitos
- Python 3.10+
- PostgreSQL 14+

### Pasos

```bash
# 1. Clonar y entrar al directorio
cd gestion_pedidos

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno (Windows)
venv\Scripts\activate
# O Linux/Mac:
# source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus datos

# 6. Crear base de datos PostgreSQL
createdb gestion_pedidos

# 7. Migrar base de datos
python manage.py migrate

# 8. Crear usuario administrador
python manage.py createsuperuser

# 9. Iniciar servidor
python manage.py runserver
```

Acceder a: http://127.0.0.1:8000/

## 📋 Configuración (.env)

```
DB_NAME=gestion_pedidos
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

DEBUG=True
SECRET_KEY=tu_clave_secreta_aqui
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🏗️ Estructura del Sistema

```
apps/
├── core/           # Dashboard y autenticación
├── clientes/       # Gestión de colegios
├── pedidos/        # Pedidos y items
└── produccion/     # Órdenes de producción
```

## 📖 Documentación Completa

Ver [DOCUMENTACION.md](DOCUMENTACION.md) para:
- Arquitectura detallada
- Modelos de datos
- Flujos de trabajo
- Buenas prácticas
- Sugerencias de mejora

## 🎨 Capturas de Pantalla

### Dashboard Principal
- Estadísticas en tiempo real
- Pedidos urgentes
- Acciones rápidas

### Gestión de Pedidos
- Listado con filtros
- Detalle completo
- Importación Excel

### Módulo de Producción
- Órdenes de producción
- Clasificación automática
- Materia prima

## 🔒 Seguridad

- Autenticación requerida para todas las vistas
- Protección CSRF en formularios
- SQL Injection prevention (ORM Django)
- XSS Protection

## 🛠️ Tecnologías

- **Backend:** Django 4.2+
- **Base de Datos:** PostgreSQL
- **Frontend:** Bootstrap 5, HTML5, CSS3
- **Formularios:** Django Crispy Forms
- **Excel:** pandas, openpyxl

## 📞 Soporte

Para soporte técnico o consultas, contactar al equipo de desarrollo.

---

**Versión:** 1.0.0  
**Licencia:** Propietaria