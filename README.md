<!-- README: Pasos para ejecutar WashTech -->

# WashTech - Instrucciones de ejecución

Resumen rápido

- **Desarrollo**: Proyecto Flask que usa SQLite por defecto
- **Producción (Render)**: PostgreSQL con variable de entorno `DATABASE_URL` (configurada automáticamente por Render)
- Incluye `Procfile` y `gunicorn` para despliegue en Render

Requisitos

- Python 3.10+ (probado con 3.11)
- Para Render: Cuenta en [render.com](https://render.com)

1. Crear y activar entorno virtual

```bash
python -m venv .venv
# En bash (Git Bash / WSL / bash.exe)
source .venv/Scripts/activate

# En PowerShell:
.\.venv\Scripts\Activate.ps1

# En cmd.exe:
.venv\Scripts\activate
```

2. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requerimientos.txt
```

3. Crear las tablas de la base de datos

La aplicación crea automáticamente las tablas cuando se ejecuta por primera vez.

**Con `run.py` (recomendado - única forma de ejecutar):**

```bash
python run.py
```

Este comando:

- ✅ Crea las tablas automáticamente si no existen
- ✅ Inicia el servidor de desarrollo
- ✅ Es el único punto de entrada necesario

**Si prefieres crear tablas manualmente sin ejecutar el servidor:**

```bash
python << 'EOF'
from app import create_app
from database.connection import db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tablas creadas')
EOF
```

4. Poblar datos de prueba (seed)

```bash
python seed_data.py
```

El script imprimirá credenciales de prueba (SuperAdmin, Admin, Cliente).

5. Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en `http://127.0.0.1:5000`

### Arquitectura de la aplicación

- **`app.py`**: Define la factory `create_app()` (importado por `run.py`)
- **`run.py`**: Punto de entrada único (ejecuta la app y crea tablas automáticamente)
- **`seed_data.py`**: Script para poblar datos de prueba

6. Verificar qué base de datos está usando la app

```bash
python - <<'PY'
from app import create_app
app = create_app()
print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])
PY
```

- Si la salida es `sqlite:///washtech.db`, usa SQLite (archivo `washtech.db` en la raíz).
- Si quieres usar PostgreSQL u otra BD, exporta `DATABASE_URL` antes de crear tablas o arrancar la app:

```bash
export DATABASE_URL='postgresql://usuario:pass@host:5432/dbname'
# (Windows PowerShell: $env:DATABASE_URL = '...')
```

Credenciales de prueba (seed_data.py)

- SuperAdmin: `super@washtech.com` / `super123`
- Admin: `admin@washtech.com` / `admin123`
- Operador: `operador@washtech.com` / `operador123`
- Cliente: `maria@email.com` / `cliente123`

## 📁 Estructura de ejecución

### Antes (confuso)

```
app.py       → Punto de entrada + configuración + crea tablas
run.py       → Punto de entrada sin crear tablas
```

### Ahora (limpio)

```
app.py       → Solo define create_app() (factory pattern)
run.py       → Punto de entrada ÚNICO (crea tablas + inicia servidor)
seed_data.py → Script para poblar datos de prueba
```

**Flujo de ejecución:**

```
python run.py
    ↓
Importa create_app() de app.py
    ↓
Crea tablas automáticamente (db.create_all())
    ↓
Inicia servidor en http://127.0.0.1:5000
```

---

## 🚀 Despliegue en Render

### Requisitos previos

1. Cuenta en [render.com](https://render.com)
2. Repositorio en GitHub con los cambios
3. Variables de entorno configuradas (Render las crea automáticamente)

### Pasos para desplegar

#### 1. Conectar repositorio a Render

```
1. Inicia sesión en Render.com
2. Haz clic en "New +"
3. Selecciona "Web Service"
4. Conecta tu repositorio de GitHub
5. Selecciona el repositorio "proyecto_washtech"
6. Asegúrate de seleccionar la rama correcta (main o ricardo)
```

#### 2. Configurar el Web Service

En el formulario de Render:

- **Name**: washtech (o el nombre que prefieras)
- **Environment**: Python 3
- **Build Command**: `pip install -r requerimientos.txt`
- **Start Command**: `gunicorn app:app`
- **Region**: Selecciona la más cercana a ti

#### 3. Render detectará automáticamente:

- **`Procfile`**: Leerá `web: gunicorn app:app`
- **`requerimientos.txt`**: Instalará todas las dependencias

#### 4. Agregar base de datos PostgreSQL

En el dashboard de Render:

```
1. En tu Web Service: "Connected Services" → "Create New"
2. Selecciona "PostgreSQL"
3. Configura:
   - Name: washtech-db (o el nombre que prefieras)
   - PostgreSQL Version: 15 (o la versión disponible)
4. Render creará automáticamente la variable DATABASE_URL
```

#### 5. Vincular variables de entorno

En tu Web Service → Environment:

```
DATABASE_URL=valor_creado_automáticamente_por_render
SECRET_KEY=tu_clave_secreta_segura_aqui
```

#### 6. Render desplegará automáticamente

- Los cambios se desplegarán cuando hagas push a tu rama principal
- Puedes ver el progreso en Render Dashboard → Deployments

### Crear tablas en Render (primera vez)

**Opción A: Usar Render Shell**

```bash
# En Render Dashboard → Web Service → Shell
python << 'EOF'
from app import create_app
from database.connection import db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tablas creadas en PostgreSQL')
EOF
```

**Opción B: Poblar datos de prueba**

```bash
# En Render Shell
python seed_data.py
```

### Monitoreo y logs

```
Render Dashboard → Web Service → Logs
- Ver logs en tiempo real
- Detectar errores de conexión a BD
- Verificar que gunicorn esté corriendo
```

### Problemas comunes

| Problema                     | Solución                                                              |
| ---------------------------- | --------------------------------------------------------------------- |
| `DATABASE_URL` no encontrada | Render la crea cuando agregas PostgreSQL. Verifica en Variables       |
| Build failure                | Ejecuta `pip install -r requerimientos.txt` localmente para verificar |
| Tablas no existen            | Ejecuta `db.create_all()` en Render Shell (ver arriba)                |
| Errores de conexión BD       | Verifica que PostgreSQL esté activo en Render Dashboard               |
| Port binding error           | Render asigna el puerto automáticamente via la variable `PORT`        |

### URLs útiles

- Dashboard Render: https://dashboard.render.com
- Documentación: https://render.com/docs
- PostgreSQL en Render: https://render.com/docs/databases

---

## 📝 Notas sobre configuración

### Bases de datos

**Desarrollo (SQLite)**:

- Archivo: `instance/washtech.db`
- Configuración automática, sin configuración necesaria
- Ideal para desarrollo local rápido

**Producción (PostgreSQL)**:

- Configuración en `config.py`: Prioriza `DATABASE_URL` del entorno
- Fallback local: `postgresql://postgres:pupiales8@localhost:5432/washtech_local`
- En Render: `DATABASE_URL` se crea automáticamente
- Requiere: `psycopg2-binary` (ya incluido en `requerimientos.txt`)

### Archivos importantes para despliegue

- `Procfile`: Indica a Render cómo ejecutar la app con gunicorn
- `requerimientos.txt`: Incluye gunicorn y todas las dependencias
- `config.py`: Maneja la configuración de BD según el entorno
- `seed_data.py`: Para crear datos de prueba en la BD

### Otras notas

- Si no ves imágenes: revisa que las rutas en la BD apunten a `/static/images/...` y que los archivos existan en `views/static/images/`.
- Hay un archivo `controllers/__initi__.py` con un typo (se recomienda renombrarlo a `controllers/__init__.py`) para evitar confusiones con importaciones.

### Problemas comunes en desarrollo

- Puerto en uso: cambia el puerto en `run.py` o exporta `FLASK_RUN_PORT` y arranca con Flask.
- Errores de importación: verifica que `__init__.py` exista en paquetes necesarios.

---

Exportar CSV de reservas

- Endpoint: `GET /reportes/reservas.csv`
- Parámetros opcionales (query string):
  - `start_date` (YYYY-MM-DD)
  - `end_date` (YYYY-MM-DD)
  - `status` (pendiente, confirmada, cancelada, completada)
  - `user_id` (id numérico)

Ejemplos de uso con `curl` (asumiendo servidor en `http://127.0.0.1:5000`):

Descargar todas las reservas:

```bash
curl -L "http://127.0.0.1:5000/reportes/reservas.csv" -o reservas_todas.csv
```

Descargar reservas entre fechas:

```bash
curl -L "http://127.0.0.1:5000/reportes/reservas.csv?start_date=2025-01-01&end_date=2025-12-31" -o reservas_2025.csv
```

Descargar reservas de un usuario y estado:

```bash
curl -L "http://127.0.0.1:5000/reportes/reservas.csv?user_id=10&status=confirmada" -o reservas_usuario10_confirmadas.csv
```

Importante: El endpoint requiere autenticación (login). Si usas `curl` contra el dev server y tu app usa sesión por cookies, primero inicia sesión y reutiliza las cookies, o implementa temporalmente un token si lo prefieres.
