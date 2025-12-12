"""
Punto de entrada para Vercel Serverless

Este archivo es el handler de WSGI para Vercel.
Vercel busca automáticamente una variable llamada 'app' o 'application'
y la usa como punto de entrada para las solicitudes HTTP.

IMPORTANTE: 
- No intenta escribir archivos (Vercel es read-only)
- Usa variables de entorno para configuración
- PostgreSQL debe estar configurado en DATABASE_URL
"""
import os
import sys

# Agregar directorio actual al path para imports
sys.path.insert(0, os.path.dirname(__file__))

# Importar la aplicación Flask
from app import app

# Vercel busca esta variable para el handler WSGI
application = app

# Para desarrollo local (no se ejecuta en Vercel)
if __name__ == "__main__":
    # Debug solo en desarrollo, nunca en producción
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
