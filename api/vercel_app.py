"""
Punto de entrada para Vercel Serverless

Este archivo es el handler de WSGI para Vercel.
"""
import os
import sys

# Agregar el directorio padre para poder importar app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar la aplicación Flask
from app import app

# Vercel busca esta variable para el handler WSGI
application = app

# Para desarrollo local
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
