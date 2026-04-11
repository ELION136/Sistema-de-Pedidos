# Sistema de Gestión de Pedidos - Ropa Deportiva para Colegios

## 📋 Índice

1. [Descripción del Sistema](#descripción-del-sistema)
2. [Arquitectura](#arquitectura)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Modelos de Datos](#modelos-de-datos)
5. [Módulos del Sistema](#módulos-del-sistema)
6. [Flujo de Funcionamiento](#flujo-de-funcionamiento)
7. [Instalación y Configuración](#instalación-y-configuración)
8. [Buenas Prácticas Implementadas](#buenas-prácticas-implementadas)
9. [Sugerencias de Mejora](#sugerencias-de-mejora)

---

## Descripción del Sistema

El Sistema de Gestión de Pedidos es una aplicación web desarrollada en Django y PostgreSQL diseñada para resolver el problema de recepción desordenada de pedidos en una PYME que fabrica ropa deportiva para colegios.

### Objetivos Principales

- **Digitalización**: Reemplazar el manejo de pedidos en Excel, papel y Word
- **Automatización**: Clasificación automática de tallas, género y tipo de prenda
- **Eficiencia**: Reducir el tiempo de procesamiento de pedidos
- **Trazabilidad**: Mantener historial completo de pedidos y producción

---

## Arquitectura

### Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Backend | Django 4.2+ |
| Base de Datos | PostgreSQL 14+ |
| Frontend | Bootstrap 5, HTML5, CSS3 |
| Formularios | Django Crispy Forms |
| Procesamiento Excel | pandas, openpyxl |
| Entorno | Python 3.10+ |

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        Navegador Web                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Core App  │  │ Clientes App│  │    Pedidos App      │  │
│  │  (Auth/Dash)│  │  (CRUD)     │  │ (Gestión Pedidos)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Producción App (Planificación)             │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│  ┌────────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐   │
│  │  Clientes  │ │  Pedidos   │ │  Ítems   │ │Conjuntos │   │
│  └────────────┘ └────────────┘ └──────────┘ └──────────┘   │
│  ┌────────────┐ ┌────────────┐ ┌──────────┐                 │
│  │  Órdenes   │ │  Resumen   │ │ Materia  │                 │
│  │Producción  │ │Producción  │ │  Prima   │                 │
│  └────────────┘ └────────────┘ └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Estructura del Proyecto

```
gestion_pedidos/
├── config/                     # Configuración principal de Django
│   ├── __init__.py
│   ├── settings.py            # Configuración del proyecto
│   ├── urls.py                # URLs principales
│   ├── wsgi.py                # Configuración WSGI
│   └── asgi.py                # Configuración ASGI
│
├── apps/                       # Aplicaciones Django
│   ├── core/                   # App base (dashboard, auth)
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   │
│   ├── clientes/               # Gestión de clientes (colegios)
│   │   ├── models.py          # Modelo Cliente
│   │   ├── views.py           # Vistas CRUD
│   │   ├── forms.py           # Formularios
│   │   ├── urls.py            # URLs
│   │   ├── admin.py           # Configuración admin
│   │   └── templates/
│   │
│   ├── pedidos/                # Gestión de pedidos
│   │   ├── models.py          # Pedido, ItemPedido, ConjuntoPedido
│   │   ├── views.py           # Vistas de pedidos
│   │   ├── forms.py           # Formularios
│   │   ├── urls.py            # URLs
│   │   ├── admin.py           # Configuración admin
│   │   └── templates/
│   │
│   └── produccion/             # Módulo de producción
│       ├── models.py          # OrdenProduccion, ResumenProduccion
│       ├── views.py           # Vistas de producción
│       ├── forms.py           # Formularios
│       ├── urls.py            # URLs
│       ├── admin.py           # Configuración admin
│       └── templates/
│
├── templates/                  # Templates base
│   └── base/
│       └── base.html          # Template base del sistema
│
├── static/                     # Archivos estáticos (CSS, JS, imágenes)
│
├── media/                      # Archivos subidos por usuarios
│   └── importaciones/         # Archivos Excel importados
│
├── logs/                       # Archivos de log
│
├── requirements.txt            # Dependencias del proyecto
├── .env.example               # Ejemplo de variables de entorno
├── manage.py                  # Script de gestión de Django
└── DOCUMENTACION.md           # Este archivo
```

---

## Modelos de Datos

### Diagrama Entidad-Relación

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    CLIENTE      │     │     PEDIDO      │     │   ITEM_PEDIDO   │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ PK id           │◄────┤ PK id           │◄────┤ PK id           │
│ nombre          │     │ FK cliente_id   │     │ FK pedido_id    │
│ tipo            │     │ codigo          │     │ tipo_prenda     │
│ contacto_nombre │     │ gestion         │     │ genero          │
│ telefono        │     │ tipo_pedido     │     │ talla           │
│ email           │     │ estado          │     │ cantidad        │
│ direccion       │     │ fecha_entrega   │     │ es_parte_de_    │
│ ciudad          │     │ notas           │     │   conjunto      │
│ nit             │     │ creado_en       │     │ conjunto_padre_ │
│ activo          │     │ modificado_en   │     │   id            │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       ▲
         │                       │
         │              ┌─────────────────┐
         │              │ CONJUNTO_PEDIDO │
         │              ├─────────────────┤
         │              │ PK id           │
         │              │ FK pedido_id    │
         │              │ genero          │
         │              │ talla           │
         │              │ cantidad        │
         │              │ notas           │
         │              └─────────────────┘
         │
         │              ┌─────────────────┐     ┌─────────────────┐
         │              │ ORDEN_PRODUCCION│     │RESUMEN_PRODUCCION
         │              ├─────────────────┤     ├─────────────────┤
         └─────────────►│ PK id           │◄────┤ PK id           │
                        │ codigo          │     │ FK orden_id     │
                        │ gestion         │     │ tipo_prenda     │
                        │ estado          │     │ genero          │
                        │ fecha_inicio    │     │ talla           │
                        │ fecha_fin_est.  │     │ cantidad_total  │
                        │ notas           │     └─────────────────┘
                        └─────────────────┘
                                 ▲
                                 │
                        ┌─────────────────┐
                        │MATERIA_PRIMA_   │
                        │REQUERIDA        │
                        ├─────────────────┤
                        │ PK id           │
                        │ FK orden_id     │
                        │ tipo_material   │
                        │ descripcion     │
                        │ cantidad_req.   │
                        │ unidad_medida   │
                        │ cantidad_comp.  │
                        └─────────────────┘
```

### Descripción de Modelos

#### Cliente
Representa a los colegios o instituciones clientes.
- Campos principales: nombre, tipo, contacto, teléfono, email, dirección
- Métodos útiles: `get_pedidos_count()`, `get_pedidos_activos_count()`

#### Pedido
Representa un pedido completo de un cliente.
- Campos principales: código único, cliente, gestión, tipo, estado
- Tipos: `completo` (conjunto), `parcial` (prendas individuales)
- Estados: `pendiente`, `en_proceso`, `completado`, `entregado`, `cancelado`
- Métodos útiles: `get_total_prendas()`, `get_resumen_por_prenda()`

#### ItemPedido
Representa una prenda individual dentro de un pedido.
- Campos: tipo_prenda, genero, talla, cantidad
- Campos de control: `es_parte_de_conjunto`, `conjunto_padre_id`

#### ConjuntoPedido
Representa un conjunto completo de prendas.
- Al guardar, automáticamente genera 4 ítems individuales
- Al eliminar, elimina los ítems generados

#### OrdenProduccion
Representa una orden de producción que agrupa múltiples pedidos.
- Estados: `pendiente`, `en_corte`, `en_confeccion`, `en_acabados`, `completada`
- Método útil: `generar_resumen_produccion()`

#### ResumenProduccion
Almacena el resumen agregado de prendas por tipo, género y talla.
- Se genera automáticamente al crear/actualizar una orden

---

## Módulos del Sistema

### 1. Módulo de Clientes

**Funcionalidades:**
- CRUD completo de clientes (colegios)
- Búsqueda y filtrado
- Vista de detalle con historial de pedidos
- Estadísticas por cliente

**Vistas principales:**
- `lista_clientes`: Listado con filtros
- `detalle_cliente`: Información detallada
- `crear_cliente` / `editar_cliente`: Formularios

### 2. Módulo de Pedidos

**Funcionalidades:**
- Creación de pedidos con código automático
- Agregación de ítems individuales
- Agregación de conjuntos (auto-genera prendas)
- Importación desde Excel con vista previa
- Resumen para producción

**Vistas principales:**
- `lista_pedidos`: Listado con filtros avanzados
- `detalle_pedido`: Información completa del pedido
- `agregar_items`: Interfaz para agregar prendas/conjuntos
- `importar_excel`: Importación con validación
- `resumen_pedido_produccion`: Tabla lista para producción

**Lógica de Conjuntos:**
```python
# Al guardar un conjunto:
ConjuntoPedido(cantidad=10, talla='M', genero='varon')
# Genera automáticamente:
# - 10 Chamarras talla M varón
# - 10 Busos talla M varón
# - 10 Poleras talla M varón
# - 10 Shorts talla M varón
```

### 3. Módulo de Producción

**Funcionalidades:**
- Dashboard con estadísticas
- Creación de órdenes de producción
- Clasificación automática por tipo/género/talla
- Gestión de materia prima requerida
- Reportes de producción

**Vistas principales:**
- `dashboard_produccion`: Panel principal
- `lista_ordenes`: Órdenes de producción
- `detalle_orden`: Información completa
- `resumen_clasificacion`: Tabla de producción
- `reporte_materia_prima`: Materiales necesarios

---

## Flujo de Funcionamiento

### Flujo 1: Crear un Pedido Nuevo

```
1. Dashboard → "Nuevo Pedido"
   ↓
2. Formulario: Seleccionar cliente, gestión, tipo, fecha entrega
   ↓
3. Guardar → Genera código automático (PED-2024-00001)
   ↓
4. Redirige a "Agregar Ítems"
   ↓
5. Opciones:
   a) Agregar prendas individuales (tipo, género, talla, cantidad)
   b) Agregar conjuntos (género, talla, cantidad → auto-genera 4 prendas)
   ↓
6. Pedido listo → Ver detalle / Resumen producción
```

### Flujo 2: Importar desde Excel

```
1. Pedido → "Importar Excel"
   ↓
2. Seleccionar archivo (.xlsx o .xls)
   ↓
3. Validación de formato y datos
   ↓
4. Vista previa con datos válidos
   ↓
5. Mostrar errores si existen
   ↓
6. Confirmar importación
   ↓
7. Crear ítems automáticamente
```

### Flujo 3: Crear Orden de Producción

```
1. Producción → "Nueva Orden"
   ↓
2. Seleccionar pedidos a incluir
   ↓
3. Definir fechas de inicio y fin
   ↓
4. Guardar → Genera código (OP-2024-00001)
   ↓
5. Sistema genera automáticamente:
   - ResumenProduccion: agrupado por tipo/género/talla
   ↓
6. Ver resumen de clasificación (tabla para producción)
   ↓
7. Agregar materia prima requerida
```

---

## Instalación y Configuración

### Requisitos Previos

- Python 3.10+
- PostgreSQL 14+
- pip (gestor de paquetes Python)

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone <repositorio>
cd gestion_pedidos

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 6. Crear base de datos en PostgreSQL
createdb gestion_pedidos

# 7. Ejecutar migraciones
python manage.py migrate

# 8. Crear superusuario
python manage.py createsuperuser

# 9. Cargar datos iniciales (opcional)
python manage.py loaddata fixtures/initial_data.json

# 10. Iniciar servidor de desarrollo
python manage.py runserver
```

### Configuración de Variables de Entorno (.env)

```
# Base de Datos
DB_NAME=gestion_pedidos
DB_USER=postgres
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost
DB_PORT=5432

# Django
DEBUG=True
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Buenas Prácticas Implementadas

### 1. Arquitectura y Organización

- ✅ **Estructura modular**: Apps separadas por dominio (clientes, pedidos, produccion)
- ✅ **DRY (Don't Repeat Yourself)**: Modelo base TimeStampedModel reutilizable
- ✅ **Separación de responsabilidades**: Models, Views, Forms en archivos separados
- ✅ **URLs namespaced**: Evita colisiones de nombres de URL

### 2. Seguridad

- ✅ **CSRF Protection**: Todos los formularios POST protegidos
- ✅ **Login required**: Vistas protegidas con @login_required
- ✅ **SQL Injection prevention**: Uso exclusivo del ORM de Django
- ✅ **XSS Protection**: Templates escapan automáticamente el contenido
- ✅ **Variables sensibles en .env**: Nunca en el código

### 3. Base de Datos

- ✅ **Índices optimizados**: Campos de búsqueda frecuente indexados
- ✅ **Relaciones apropiadas**: ForeignKey, ManyToMany donde corresponde
- ✅ **Integridad referencial**: on_delete=PROTECT para datos importantes
- ✅ **Migraciones versionadas**: Control de cambios en esquema

### 4. UI/UX

- ✅ **Diseño responsive**: Bootstrap 5, funciona en móviles
- ✅ **Feedback al usuario**: Mensajes de éxito/error con django.contrib.messages
- ✅ **Formularios con crispy**: Formularios consistentes y validados
- ✅ **Navegación intuitiva**: Sidebar, breadcrumbs, botones de acción claros

### 5. Código

- ✅ **Docstrings**: Documentación de clases y métodos importantes
- ✅ **Type hints implícitos**: Uso de nombres descriptivos
- ✅ **Manejo de errores**: Try-except en operaciones críticas
- ✅ **Logging**: Configurado para registrar eventos importantes

---

## Sugerencias de Mejora

### Corto Plazo (Fase 2)

1. **API REST**
   - Implementar Django REST Framework
   - Permitir integración con aplicaciones móviles

2. **Reportes Avanzados**
   - Exportar a PDF (ReportLab o WeasyPrint)
   - Gráficos estadísticos (Chart.js)
   - Reportes comparativos por gestión

3. **Notificaciones**
   - Email de confirmación de pedidos
   - Alertas de pedidos próximos a vencer
   - Notificaciones de cambio de estado

4. **Mejoras en Excel**
   - Plantilla descargable
   - Soporte para múltiples hojas
   - Validación más flexible de columnas

### Mediano Plazo (Fase 3)

1. **Integración WhatsApp**
   - Notificaciones automáticas a clientes
   - Confirmación de pedidos vía WhatsApp
   - Bot para consultas básicas

2. **Gestión de Inventario**
   - Control de stock de materia prima
   - Alertas de stock bajo
   - Historial de movimientos

3. **Módulo de Facturación**
   - Generación de facturas
   - Control de pagos
   - Estados de cuenta por cliente

4. **Multi-usuario y Permisos**
   - Roles: Administrador, Vendedor, Producción
   - Permisos granulares por módulo
   - Auditoría de cambios

### Largo Plazo (Fase 4)

1. **Inteligencia Artificial**
   - OCR para lectura de pedidos escaneados
   - Predicción de demanda por temporada
   - Sugerencias de compra de materia prima

2. **Análisis Predictivo**
   - Forecast de pedidos por colegio
   - Identificación de patrones estacionales
   - Alertas de clientes inactivos

3. **Portal de Clientes**
   - Acceso para colegios a sus pedidos
   - Seguimiento en tiempo real
   - Descarga de reportes

4. **Escalabilidad**
   - Dockerización
   - Configuración para AWS/GCP
   - Caché con Redis
   - Celery para tareas asíncronas

---

## Mantenimiento y Soporte

### Comandos Útiles

```bash
# Backup de base de datos
pg_dump -U postgres gestion_pedidos > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -U postgres gestion_pedidos < backup_20240101.sql

# Crear superusuario
python manage.py createsuperuser

# Shell de Django
python manage.py shell

# Check del sistema
python manage.py check

# Coleccionar archivos estáticos (producción)
python manage.py collectstatic
```

### Contacto y Soporte

Para reportar bugs o solicitar nuevas funcionalidades, contactar al equipo de desarrollo.

---

**Documentación generada el:** 2024
**Versión del Sistema:** 1.0.0
**Autor:** Equipo de Desarrollo