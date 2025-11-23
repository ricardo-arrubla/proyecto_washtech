<!-- README: Pasos para ejecutar WashTech -->

# WashTech - Instrucciones de ejecución

Resumen rápido

- Proyecto Flask que por defecto usa SQLite en desarrollo y permite configurar otra BD mediante la variable de entorno `DATABASE_URL`.

Requisitos

- Python 3.10+ (probado con 3.11)

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
- Cliente: `maria@email.com` / `cliente123`

Notas útiles

- Si no ves imágenes: revisa que las rutas en la BD apunten a `/static/images/...` y que los archivos existan en `views/static/images/`.
- Hay un archivo `controllers/__initi__.py` con un typo (se recomienda renombrarlo a `controllers/__init__.py`) para evitar confusiones con importaciones.
- Para desarrollo rápido puedes usar SQLite; para producción configura `DATABASE_URL` apuntando a PostgreSQL u otro motor y asegúrate de instalar el adaptador correspondiente.

Problemas comunes

- Puerto en uso: cambia el puerto en `run.py` o exporta `FLASK_RUN_PORT` y arranca con Flask.
- Errores de importación: verifica que `__init__.py` exista en paquetes necesarios.

Contacto

- Si quieres que renombre `controllers/__initi__.py` a `controllers/__init__.py` o haga un commit con este README, dímelo.

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
