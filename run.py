"""
Punto de entrada principal para WashTech en desarrollo local.
Ejecutar con: python run.py

Nota: Para Gunicorn en producción (Render), se usa directamente:
      gunicorn app:app
"""
from app import app

if __name__ == '__main__':
    # Ejecutar servidor de desarrollo
    # - debug=True: recarga automática al cambiar código
    # - host='0.0.0.0': accesible desde cualquier interfaz de red
    # - port=5000: puerto por defecto de Flask
    print('🚀 Iniciando WashTech en http://127.0.0.1:5000')
    print('   (La aplicación ya está completamente inicializada)')
    app.run(debug=True, host='0.0.0.0', port=5000)