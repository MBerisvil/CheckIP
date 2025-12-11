"""
Punto de entrada para Vercel Serverless
"""
import os
from app import app

# Vercel busca una variable llamada 'app' o 'application'
application = app

# Para desarrollo local
if __name__ == "__main__":
    # Debug solo en desarrollo, nunca en producción
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)
