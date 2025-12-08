"""
Punto de entrada para Vercel Serverless
"""
from app import app

# Vercel busca una variable llamada 'app' o 'application'
application = app

# Para desarrollo local
if __name__ == "__main__":
    app.run(debug=True)
