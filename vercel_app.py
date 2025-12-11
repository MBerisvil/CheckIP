"""
Punto de entrada para Vercel Serverless
IMPORTANTE: Desactiva funciones incompatibles con serverless
"""
import os
import sys

# Desactivar seguridad avanzada en Vercel (incompatible con serverless)
os.environ['VERCEL_ENV'] = '1'
os.environ['DISABLE_RATE_LIMITING'] = '1'

# Asegurar que las variables de entorno críticas existan
if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'vercel-production-key-use-env-vars'

if not os.getenv('DATABASE_URL'):
    # Usar SQLite como fallback (Vercel efímero, solo para desarrollo)
    os.environ['DATABASE_URL'] = 'sqlite:////tmp/verip_stats.db'

try:
    from app import app
    
    # Desactivar modo debug en producción
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Vercel busca una variable llamada 'app' o 'application'
    application = app
    
    print("✅ Vercel app iniciada correctamente", file=sys.stderr)
    
except Exception as e:
    print(f"❌ Error al iniciar app: {str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    raise

# Para desarrollo local
if __name__ == "__main__":
    app.run(debug=True)
