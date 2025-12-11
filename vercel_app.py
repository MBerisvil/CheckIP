"""
Punto de entrada para Vercel Serverless
"""
import os
import sys

# Asegurarse de que las variables de entorno estén disponibles
print("Inicializando Vercel App...")
print(f"DATABASE_URL configurado: {'Sí' if os.getenv('DATABASE_URL') else 'No'}")
print(f"SECRET_KEY configurado: {'Sí' if os.getenv('SECRET_KEY') else 'No'}")

try:
    from app import app
    
    # Vercel busca una variable llamada 'app' o 'application'
    application = app
    
    print("✅ Aplicación inicializada correctamente")
except Exception as e:
    print(f"❌ Error al inicializar aplicación: {e}")
    import traceback
    traceback.print_exc()
    
    # Crear una app de fallback que muestre el error
    from flask import Flask, jsonify
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return jsonify({
            'error': 'Error al inicializar la aplicación',
            'details': str(e),
            'message': 'Verifica las variables de entorno en Vercel'
        }), 500
    
    @application.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            'error': 'Error al inicializar la aplicación',
            'details': str(e)
        }), 500

# Para desarrollo local
if __name__ == "__main__":
    application.run(debug=True)
