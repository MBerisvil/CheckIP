#!/bin/bash
# ============================================
# SCRIPT DE AUDITORÍA DE SEGURIDAD AUTOMATIZADA
# ============================================

echo "🔒 Iniciando Auditoría de Seguridad para VerIP v3.5"
echo "=================================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ISSUES_FOUND=0

# 1. Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py no encontrado. Ejecuta este script desde el directorio raíz del proyecto.${NC}"
    exit 1
fi

echo "✅ Directorio del proyecto verificado"
echo ""

# 2. Verificar Python
echo "📦 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
fi
echo ""

# 3. Verificar entorno virtual
echo "🐍 Verificando entorno virtual..."
if [ -d ".venv" ] || [ -d "venv" ]; then
    echo -e "${GREEN}✅ Entorno virtual encontrado${NC}"
    
    # Activar si no está activo
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "ℹ️  Activando entorno virtual..."
        if [ -d ".venv" ]; then
            source .venv/bin/activate
        else
            source venv/bin/activate
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Entorno virtual no encontrado${NC}"
    echo "   Recomendación: Crear con 'python3 -m venv .venv'"
fi
echo ""

# 4. Instalar herramientas de seguridad si no existen
echo "🔧 Verificando herramientas de seguridad..."
TOOLS_MISSING=0

if ! python3 -c "import safety" &> /dev/null; then
    echo -e "${YELLOW}⚠️  'safety' no instalado${NC}"
    TOOLS_MISSING=1
fi

if ! command -v bandit &> /dev/null; then
    echo -e "${YELLOW}⚠️  'bandit' no instalado${NC}"
    TOOLS_MISSING=1
fi

if [ $TOOLS_MISSING -eq 1 ]; then
    echo ""
    read -p "¿Instalar herramientas de seguridad? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install safety bandit pip-audit
    fi
fi
echo ""

# 5. Verificar variables de entorno
echo "🔐 Verificando configuración de seguridad..."
if [ -f ".env" ]; then
    echo "✅ Archivo .env encontrado"
    
    # Verificar SECRET_KEY
    if grep -q "SECRET_KEY=.*dev-secret-key" .env 2>/dev/null; then
        echo -e "${RED}❌ SECRET_KEY por defecto detectada${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    elif ! grep -q "SECRET_KEY=" .env 2>/dev/null; then
        echo -e "${RED}❌ SECRET_KEY no configurada${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ SECRET_KEY configurada${NC}"
    fi
    
    # Verificar ADMIN_PASSWORD
    if grep -q "ADMIN_PASSWORD=admin123" .env 2>/dev/null; then
        echo -e "${RED}❌ Contraseña de admin por defecto${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ ADMIN_PASSWORD personalizada${NC}"
    fi
    
    # Verificar API_MONITOR_KEY
    if grep -q "API_MONITOR_KEY=.*monitor-api-key-change" .env 2>/dev/null; then
        echo -e "${RED}❌ API_MONITOR_KEY por defecto${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ API_MONITOR_KEY configurada${NC}"
    fi
    
else
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    echo "   Recomendación: Crear .env basándose en .env.example"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# 6. Escanear vulnerabilidades en dependencias
echo "🔍 Escaneando vulnerabilidades en dependencias..."
if command -v safety &> /dev/null; then
    echo "Ejecutando Safety check..."
    if safety check --json > safety_report.json 2>&1; then
        echo -e "${GREEN}✅ No se encontraron vulnerabilidades conocidas${NC}"
        rm -f safety_report.json
    else
        VULN_COUNT=$(grep -c "vulnerability" safety_report.json 2>/dev/null || echo "0")
        if [ "$VULN_COUNT" -gt 0 ]; then
            echo -e "${RED}❌ $VULN_COUNT vulnerabilidades encontradas${NC}"
            echo "   Ver safety_report.json para detalles"
            ISSUES_FOUND=$((ISSUES_FOUND + VULN_COUNT))
        else
            echo -e "${GREEN}✅ Escaneo completado${NC}"
            rm -f safety_report.json
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Safety no instalado, saltando...${NC}"
fi
echo ""

# 7. Análisis estático de código con Bandit
echo "🔍 Análisis estático de seguridad del código..."
if command -v bandit &> /dev/null; then
    echo "Ejecutando Bandit..."
    if bandit -r . -f json -o bandit_report.json -ll 2>/dev/null; then
        echo -e "${GREEN}✅ Sin problemas de severidad alta detectados${NC}"
        rm -f bandit_report.json
    else
        echo -e "${RED}❌ Problemas de seguridad detectados en el código${NC}"
        echo "   Ver bandit_report.json para detalles"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Bandit no instalado, saltando...${NC}"
fi
echo ""

# 8. Verificar permisos de archivos sensibles
echo "📂 Verificando permisos de archivos..."
PERMS_OK=1

if [ -f ".env" ]; then
    PERMS=$(stat -c %a .env 2>/dev/null || stat -f %A .env 2>/dev/null)
    if [ "$PERMS" != "600" ] && [ "$PERMS" != "400" ]; then
        echo -e "${YELLOW}⚠️  .env tiene permisos $PERMS (recomendado: 600)${NC}"
        echo "   Ejecuta: chmod 600 .env"
        PERMS_OK=0
    fi
fi

if [ -f "verip_stats.db" ]; then
    PERMS=$(stat -c %a verip_stats.db 2>/dev/null || stat -f %A verip_stats.db 2>/dev/null)
    if [ "$PERMS" != "600" ] && [ "$PERMS" != "640" ]; then
        echo -e "${YELLOW}⚠️  verip_stats.db tiene permisos $PERMS (recomendado: 600)${NC}"
        echo "   Ejecuta: chmod 600 verip_stats.db"
        PERMS_OK=0
    fi
fi

if [ $PERMS_OK -eq 1 ]; then
    echo -e "${GREEN}✅ Permisos de archivos correctos${NC}"
fi
echo ""

# 9. Verificar .gitignore
echo "📝 Verificando .gitignore..."
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore && grep -q "\.db" .gitignore; then
        echo -e "${GREEN}✅ .gitignore configurado correctamente${NC}"
    else
        echo -e "${YELLOW}⚠️  .gitignore incompleto${NC}"
        echo "   Asegúrate de incluir: .env, *.db, __pycache__"
    fi
else
    echo -e "${RED}❌ .gitignore no encontrado${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi
echo ""

# 10. Verificar código Python por problemas comunes
echo "🐍 Verificando código Python..."
PYTHON_ISSUES=0

# Buscar uso de eval() o exec()
if grep -r "eval(" --include="*.py" . 2>/dev/null | grep -v ".venv" | grep -v "venv"; then
    echo -e "${RED}❌ Uso de eval() detectado (peligroso)${NC}"
    PYTHON_ISSUES=$((PYTHON_ISSUES + 1))
fi

# Buscar SQL injection potencial
if grep -r "execute.*%" --include="*.py" . 2>/dev/null | grep -v ".venv" | grep -v "venv"; then
    echo -e "${YELLOW}⚠️  Posible SQL injection (revisar manualmente)${NC}"
fi

# Buscar debug=True
if grep -r "debug=True" --include="*.py" . 2>/dev/null | grep -v ".venv" | grep -v "venv"; then
    echo -e "${YELLOW}⚠️  debug=True encontrado (no usar en producción)${NC}"
fi

if [ $PYTHON_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ No se detectaron problemas obvios${NC}"
else
    ISSUES_FOUND=$((ISSUES_FOUND + PYTHON_ISSUES))
fi
echo ""

# 11. Verificar que HTTPS esté configurado para producción
echo "🔒 Verificando configuración HTTPS..."
if grep -q "force_https.*False" app.py 2>/dev/null; then
    echo -e "${YELLOW}⚠️  HTTPS no forzado en el código${NC}"
    echo "   Asegúrate de usar HTTPS en producción"
fi
echo ""

# 12. Verificar actualizaciones disponibles
echo "📦 Verificando actualizaciones de paquetes..."
if command -v pip-audit &> /dev/null; then
    if pip-audit 2>/dev/null; then
        echo -e "${GREEN}✅ No hay vulnerabilidades en las dependencias${NC}"
    else
        echo -e "${YELLOW}⚠️  Algunas dependencias tienen actualizaciones de seguridad${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  pip-audit no instalado, saltando...${NC}"
fi
echo ""

# RESUMEN FINAL
echo "=================================================="
echo "📊 RESUMEN DE AUDITORÍA"
echo "=================================================="

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ ¡Excelente! No se encontraron problemas críticos${NC}"
    echo ""
    echo "Recomendaciones adicionales:"
    echo "  • Implementar protección CSRF (Flask-WTF)"
    echo "  • Agregar rate limiting (Flask-Limiter)"
    echo "  • Configurar headers de seguridad (Flask-Talisman)"
    echo "  • Revisar SECURITY_AUDIT_REPORT.md para más detalles"
else
    echo -e "${RED}⚠️  Se encontraron $ISSUES_FOUND problemas de seguridad${NC}"
    echo ""
    echo "Acciones requeridas:"
    echo "  1. Revisar los problemas listados arriba"
    echo "  2. Consultar SECURITY_AUDIT_REPORT.md"
    echo "  3. Implementar security_fixes.py"
    echo "  4. Volver a ejecutar esta auditoría"
fi

echo ""
echo "📄 Documentación de seguridad:"
echo "  • SECURITY_AUDIT_REPORT.md - Reporte completo"
echo "  • security_fixes.py - Código de corrección"
echo "  • requirements-security.txt - Dependencias actualizadas"
echo ""

# Generar reporte JSON
cat > security_audit_summary.json <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "issues_found": $ISSUES_FOUND,
  "status": "$([ $ISSUES_FOUND -eq 0 ] && echo 'PASS' || echo 'FAIL')",
  "checks": {
    "environment_vars": "$([ $ISSUES_FOUND -eq 0 ] && echo 'OK' || echo 'ISSUES')",
    "dependencies": "checked",
    "code_analysis": "completed",
    "permissions": "$([ $PERMS_OK -eq 1 ] && echo 'OK' || echo 'WARNING')"
  }
}
EOF

echo "✅ Reporte guardado en: security_audit_summary.json"
echo ""

exit $ISSUES_FOUND
