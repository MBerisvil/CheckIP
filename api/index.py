"""
API handler para Vercel Serverless
"""
from app import app

# Vercel espera una variable llamada 'app' o un handler
# Flask app ya está configurado en app.py
handler = app

# Para compatibilidad con diferentes configuraciones de Vercel
if __name__ == "__main__":
    app.run()
