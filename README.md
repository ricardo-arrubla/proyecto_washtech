<!-- README: Pasos para ejecutar WashTech -->

# WashTech - Instrucciones de ejecución

Resumen rápido

- **Desarrollo**: Proyecto Flask que usa SQLite por defecto
- **Producción (Railway)**: PostgreSQL con variable de entorno `DATABASE_URL` (configurada automáticamente por Railway)
- Incluye `Procfile` y `gunicorn` para despliegue en Railway

Requisitos

- Python 3.10+ (probado con 3.11)
- Para Railway: Cuenta en [railway.app](https://railway.app)

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

Opción A (crear tablas manualmente):

```bash
python - <<'PY'
from app import create_app
from database.connection import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Tablas creadas')
PY
```

Opción B (el script `app.py` también crea tablas si se ejecuta directamente):

```bash
python app.py
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

Abre `http://127.0.0.1:5000` en el navegador.

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

---

## 🚀 Despliegue en Railway

### Requisitos previos

1. Cuenta en [railway.app](https://railway.app)
2. Repositorio en GitHub con los cambios
3. Variables de entorno configuradas (Railway las crea automáticamente)

### Pasos para desplegar

#### 1. Conectar repositorio a Railway

```
1. Inicia sesión en Railway.app
2. Haz clic en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Autoriza el acceso a tu repositorio de GitHub
5. Selecciona el repositorio "proyecto_washtech"
```

#### 2. Railway configurará automáticamente:

- **`Procfile`**: Indicará cómo ejecutar la aplicación con gunicorn
- **Variables de entorno**: Railway detectará `DATABASE_URL` automáticamente

#### 3. Agregar base de datos PostgreSQL

```
1. En tu proyecto de Railway: "+ Add Service"
2. Selecciona "Database"
3. Elige "PostgreSQL"
4. Railway creará automáticamente la variable DATABASE_URL
```

#### 4. Configurar variables de entorno (opcional pero recomendado)

En Railway Dashboard → Variables:

```
SECRET_KEY=tu_clave_secreta_segura
```

#### 5. Railway desplegará automáticamente

- Los cambios se desplegarán cuando hagas push a tu rama principal
- Las tablas se crearán automáticamente (si lo configuras en el startup)

### Crear tablas en Railway (primera vez)

**Opción A: Ejecutar comando en Railway SSH**

```bash
# En Railway Dashboard → Deployments → Shell
python - <<'PY'
from app import create_app
from database.connection import db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tablas creadas en PostgreSQL')
PY
```

**Opción B: Poblar datos de prueba**

```bash
# En Railway SSH
python seed_data.py
```

### Monitoreo y logs

```
Railway Dashboard → Deployments → Logs
- Ver logs en tiempo real
- Detectar errores de conexión a BD
- Verificar que gunicorn esté corriendo
```

### Problemas comunes

| Problema                     | Solución                                                         |
| ---------------------------- | ---------------------------------------------------------------- |
| `DATABASE_URL` no encontrada | Railway la crea cuando agregas PostgreSQL. Verifica en Variables |
| Tablas no existen            | Ejecuta `db.create_all()` en Railway SSH (ver arriba)            |
| Puerto en uso                | Railway asigna automáticamente el puerto en variable `PORT`      |
| Errores de conexión          | Verifica que PostgreSQL esté activo en el dashboard de Railway   |

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
- En Railway: `DATABASE_URL` se crea automáticamente
- Requiere: `psycopg2-binary` (ya incluido en `requerimientos.txt`)

### Archivos importantes para despliegue

- `Procfile`: Indica a Railway cómo ejecutar la app con gunicorn
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
