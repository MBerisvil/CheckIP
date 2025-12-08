#!/bin/bash

# 🚀 Script de Inicio Rápido - VerIP v3.5

echo "=========================================="
echo "🚀 Iniciando VerIP v3.5"
echo "=========================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo "❌ Error: Este script debe ejecutarse desde el directorio raíz de VerIP"
    exit 1
fi

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "❌ Error: No se encuentra el entorno virtual (.venv)"
    echo "Crea uno con: python3 -m venv .venv"
    exit 1
fi

# Verificar que las dependencias están instaladas
echo ""
echo "🔍 Verificando dependencias..."
python -c "import flask, flask_login, flask_sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependencias faltantes..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error instalando dependencias"
        exit 1
    fi
    echo "✅ Dependencias instaladas"
else
    echo "✅ Todas las dependencias están instaladas"
fi

# Verificar archivo .env
echo ""
echo "🔍 Verificando configuración..."
if [ ! -f ".env" ]; then
    echo "⚠️  No se encuentra archivo .env"
    echo "📝 Creando .env desde .env.example..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo ""
    echo "⚠️  IMPORTANTE: Edita .env con tus valores antes de usar en producción"
    echo "   - ABUSEIPDB_API_KEY (opcional para desarrollo)"
    echo "   - SECRET_KEY (cambiar en producción)"
    echo "   - ADMIN_PASSWORD_HASH (cambiar contraseña admin)"
    echo "   - API_MONITOR_KEY (cambiar en producción)"
    echo ""
else
    echo "✅ Archivo .env encontrado"
fi

# Crear base de datos si no existe
echo ""
echo "💾 Verificando base de datos..."
if [ ! -f "instance/verip_stats.db" ]; then
    echo "📝 Creando base de datos..."
    python -c "from app import app, db; app.app_context().push(); db.create_all()"
    if [ $? -eq 0 ]; then
        echo "✅ Base de datos creada exitosamente"
    else
        echo "❌ Error creando base de datos"
        exit 1
    fi
else
    echo "✅ Base de datos existente"
fi

# Mostrar información de inicio
echo ""
echo "=========================================="
echo "✅ Todo listo para iniciar VerIP"
echo "=========================================="
echo ""
echo "📝 URLs disponibles:"
echo "   🌐 Web principal:     http://localhost:5000"
echo "   🔐 Panel admin:       http://localhost:5000/admin/login"
echo "   📡 API de monitoreo:  http://localhost:5000/api/status"
echo ""
echo "🔑 Credenciales por defecto:"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo "   ⚠️  CAMBIAR EN PRODUCCIÓN"
echo ""
echo "📚 Documentación:"
echo "   - ADMIN_PANEL_GUIDE.md"
echo "   - API_DOCUMENTATION.md"
echo "   - README.md"
echo ""
echo "=========================================="
echo "🚀 Iniciando aplicación..."
echo "=========================================="
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Iniciar aplicación
python app.py
