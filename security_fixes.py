"""
🔒 CORRECCIONES DE SEGURIDAD PARA VerIP v3.5
Este archivo contiene todo el código necesario para remediar las vulnerabilidades encontradas.

INSTALACIÓN REQUERIDA:
pip install Flask-WTF Flask-Limiter Flask-Talisman safety pip-audit

INSTRUCCIONES:
1. Revisar cada función
2. Integrar en app.py
3. Actualizar requirements.txt
4. Probar en desarrollo
5. Desplegar en producción
"""

import os
import re
import hmac
import time
import secrets
import logging
import ipaddress
import traceback
from datetime import timedelta
from functools import wraps
from urllib.parse import urlparse

from flask import request, jsonify, session
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# ============================================
# 1. CONFIGURACIÓN SEGURA DE LA APLICACIÓN
# ============================================

def get_secret_key():
    """Obtener o generar SECRET_KEY segura"""
    secret = os.getenv('SECRET_KEY')
    if not secret:
        if os.getenv('FLASK_ENV') == 'production':
            raise RuntimeError("❌ SECRET_KEY must be set in production!")
        # En desarrollo, generar una temporal
        return secrets.token_hex(32)
    return secret

def configure_security(app):
    """
    Configurar todas las medidas de seguridad de la aplicación.
    Llamar DESPUÉS de crear la app Flask.
    
    Usage:
        app = Flask(__name__)
        csrf, limiter = configure_security(app)
    """
    
    # Validar SECRET_KEY
    app.config['SECRET_KEY'] = get_secret_key()
    
    # CSRF Protection
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Rate Limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.getenv('REDIS_URL', 'memory://'),
        headers_enabled=True
    )
    
    # HTTPS/TLS en producción
    if os.getenv('FLASK_ENV') == 'production':
        Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            session_cookie_secure=True,
            content_security_policy={
                'default-src': "'self'",
                'script-src': ["'self'", "'unsafe-inline'", "https://unpkg.com"],
                'style-src': ["'self'", "'unsafe-inline'", "https://unpkg.com"],
                'img-src': ["'self'", "data:", "https:"],
                'connect-src': ["'self'", "https://api.abuseipdb.com", "https://ipwhois.app"]
            }
        )
    
    # Configuración de sesiones seguras
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
        SESSION_COOKIE_NAME='__Secure-session',
        MAX_CONTENT_LENGTH=16 * 1024  # 16KB max request size
    )
    
    # Headers de seguridad
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response
    
    return csrf, limiter

# ============================================
# 2. VALIDACIÓN Y SANITIZACIÓN DE ENTRADA
# ============================================

def validate_and_sanitize_ip(ip_string):
    """
    Validar y sanitizar dirección IP de forma segura.
    
    Returns:
        tuple: (ip_valida: str | None, error: str | None)
    
    Example:
        ip, error = validate_and_sanitize_ip(user_input)
        if error:
            return jsonify({'error': error}), 400
    """
    # Sanitizar entrada
    if not ip_string or not isinstance(ip_string, str):
        return None, "IP requerida"
    
    ip_string = ip_string.strip()
    
    # Validar longitud
    if len(ip_string) > 45:  # Max IPv6 length
        return None, "IP demasiado larga"
    
    if len(ip_string) < 7:  # Min IPv4 (x.x.x.x)
        return None, "IP demasiado corta"
    
    # Validar caracteres permitidos
    if not re.match(r'^[0-9a-fA-F:\.]+$', ip_string):
        return None, "Caracteres inválidos en IP"
    
    try:
        ip_obj = ipaddress.ip_address(ip_string)
        
        # Rechazar IPs no públicas
        if ip_obj.is_private:
            return None, "No se permiten IPs privadas (RFC 1918)"
        if ip_obj.is_loopback:
            return None, "No se permiten IPs loopback (127.0.0.0/8)"
        if ip_obj.is_multicast:
            return None, "No se permiten IPs multicast"
        if ip_obj.is_reserved:
            return None, "IP reservada no permitida"
        if ip_obj.is_link_local:
            return None, "No se permiten IPs link-local"
        
        # Rechazar IPs especiales
        special_ips = ['0.0.0.0', '255.255.255.255', '::1', '::']
        if str(ip_obj) in special_ips:
            return None, "IP especial no permitida"
        
        return str(ip_obj), None
        
    except ValueError as e:
        return None, f"Formato de IP inválido: {str(e)}"

def sanitize_log_input(text):
    """
    Sanitizar entrada para prevenir log injection.
    
    Args:
        text: Texto a sanitizar
        
    Returns:
        str: Texto sanitizado
    """
    if not text:
        return ""
    
    # Convertir a string
    text = str(text)
    
    # Remover caracteres de control excepto tabs, newlines, returns
    sanitized = ''.join(
        char for char in text 
        if ord(char) >= 32 or char in '\n\r\t'
    )
    
    # Limitar longitud
    if len(sanitized) > 500:
        sanitized = sanitized[:500] + "..."
    
    return sanitized

# ============================================
# 3. AUTENTICACIÓN Y AUTORIZACIÓN
# ============================================

def validate_password_strength(password):
    """
    Validar fuerza de contraseña según mejores prácticas.
    
    Returns:
        tuple: (is_valid: bool, errors: list[str])
    """
    errors = []
    
    if not password:
        return False, ["Contraseña requerida"]
    
    if len(password) < 12:
        errors.append("Mínimo 12 caracteres")
    if len(password) > 128:
        errors.append("Máximo 128 caracteres")
    if not re.search(r'[A-Z]', password):
        errors.append("Requiere al menos una mayúscula")
    if not re.search(r'[a-z]', password):
        errors.append("Requiere al menos una minúscula")
    if not re.search(r'\d', password):
        errors.append("Requiere al menos un número")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]', password):
        errors.append("Requiere al menos un carácter especial")
    
    # Lista de contraseñas comunes (agregar más)
    common_passwords = [
        'admin123', 'password', 'password123', '12345678', 
        'qwerty', 'abc123', 'admin', 'letmein', 'welcome',
        'monkey', '1234567890', 'password1'
    ]
    
    if password.lower() in common_passwords:
        errors.append("Contraseña demasiado común")
    
    # Verificar patrones simples
    if re.match(r'^(.)\1+$', password):  # Todos caracteres iguales
        errors.append("No usar el mismo carácter repetido")
    
    return len(errors) == 0, errors

def require_api_key_secure(f):
    """
    Decorador seguro para validar API key (resistente a timing attacks).
    
    Usage:
        @app.route('/api/endpoint')
        @require_api_key_secure
        def api_endpoint():
            return jsonify({'data': 'secure'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.getenv('API_MONITOR_KEY')
        
        if not expected_key:
            return jsonify({'error': 'API key no configurada'}), 500
        
        if not api_key:
            return jsonify({'error': 'API key ausente'}), 401
        
        # Comparación segura contra timing attacks
        if not hmac.compare_digest(api_key, expected_key):
            # Delay para prevenir brute force
            time.sleep(1)
            return jsonify({'error': 'API key inválida'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# 5. MANEJO DE ERRORES SEGURO
# ============================================

def setup_error_handlers(app):
    """
    Configurar manejadores de errores seguros.
    
    Usage:
        setup_error_handlers(app)
    """
    DEBUG_MODE = os.getenv('FLASK_ENV') != 'production'
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Solicitud inválida'}), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': 'No autorizado'}), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': 'Acceso denegado'}), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Recurso no encontrado'}), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Demasiadas solicitudes',
            'message': 'Por favor, espera antes de intentar nuevamente'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(e):
        if DEBUG_MODE:
            return jsonify({
                'error': 'Error interno del servidor',
                'details': str(e),
                'traceback': traceback.format_exc()
            }), 500
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        if DEBUG_MODE:
            return jsonify({
                'error': str(e),
                'type': type(e).__name__
            }), 500
        return jsonify({'error': 'Error interno del servidor'}), 500

# ============================================
# 6. VALIDACIONES ESPECÍFICAS
# ============================================

def validate_json_request():
    """
    Middleware para validar requests JSON.
    
    Usage:
        @app.before_request
        def check_json():
            return validate_json_request()
    """
    if request.method == 'POST' and request.is_json:
        try:
            data = request.get_json()
            if not isinstance(data, dict):
                return jsonify({'error': 'JSON debe ser un objeto'}), 400
        except Exception as e:
            return jsonify({'error': 'JSON inválido'}), 400
    return None

def get_safe_db_url(db_url):
    """
    Sanitizar URL de base de datos para logs.
    
    Args:
        db_url: URL completa de la base de datos
        
    Returns:
        str: URL sanitizada sin credenciales
    """
    try:
        parsed = urlparse(db_url)
        # Remover usuario y contraseña
        safe_url = f"{parsed.scheme}://{parsed.hostname}"
        if parsed.port:
            safe_url += f":{parsed.port}"
        safe_url += parsed.path
        return safe_url
    except Exception:
        return "database://****"

# ============================================
# 7. MEJORAS DE CHECK DNS BLACKLIST
# ============================================

def check_dns_blacklist_secure(ip, blacklist_host, allowed_hosts):
    """
    Verificar blacklist DNS con validación estricta.
    
    Args:
        ip: IP a verificar (ya validada)
        blacklist_host: Host de la blacklist
        allowed_hosts: Lista de hosts permitidos
        
    Returns:
        bool: True si está listada, False si no
    """
    # Validar que blacklist_host está en whitelist
    if blacklist_host not in allowed_hosts:
        raise ValueError("Blacklist host no autorizado")
    
    # Validar IP
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return False
    
    # Solo IPv4 para blacklists DNS tradicionales
    if isinstance(ip_obj, ipaddress.IPv6Address):
        return False
    
    # Construir query de forma segura
    parts = str(ip_obj).split('.')
    if len(parts) != 4:
        return False
    
    try:
        octets = [int(p) for p in parts]
        if not all(0 <= o <= 255 for o in octets):
            return False
    except ValueError:
        return False
    
    reversed_ip = '.'.join(reversed(parts))
    query = f"{reversed_ip}.{blacklist_host}"
    
    try:
        import socket
        socket.gethostbyname(query)
        return True
    except socket.gaierror:
        return False
    except Exception as e:
        return False

# ============================================
# 8. CSRF TOKEN ENDPOINT
# ============================================

def create_csrf_endpoint(app):
    """
    Crear endpoint para obtener CSRF token.
    
    Usage:
        create_csrf_endpoint(app)
        
    Frontend:
        fetch('/csrf-token')
          .then(r => r.json())
          .then(data => csrfToken = data.csrf_token)
    """
    @app.route('/csrf-token', methods=['GET'])
    def get_csrf_token():
        token = generate_csrf()
        return jsonify({'csrf_token': token})

# ============================================
# 9. EJEMPLO DE USO COMPLETO
# ============================================

"""
# En app.py, reemplazar la configuración actual con:

from security_fixes import (
    configure_security,
    setup_error_handlers,
    setup_secure_logging,
    validate_and_sanitize_ip,
    require_api_key_secure,
    validate_password_strength,
    check_dns_blacklist_secure,
    create_csrf_endpoint,
    validate_json_request,
    get_safe_db_url
)

# Configurar logging

# Crear app
app = Flask(__name__)

# Configurar seguridad
csrf, limiter = configure_security(app)

# Configurar manejadores de errores
setup_error_handlers(app)

# Crear endpoint CSRF
create_csrf_endpoint(app)

# Middleware de validación JSON
@app.before_request
def check_json():
    return validate_json_request()

# Ejemplo de ruta con validación
@app.route('/verify', methods=['POST'])
@limiter.limit("10 per minute")
def verify():
    data = request.get_json()
    ip_input = data.get('ip', '').strip()
    
    # Validar IP
    ip, error = validate_and_sanitize_ip(ip_input)
    if error:
        return jsonify({'error': error}), 400
    
    # Procesar IP validada
    result = verify_ip(ip)
    return jsonify(result)

# Ejemplo de API protegida
@app.route('/api/status')
@require_api_key_secure
@limiter.limit("30 per minute")
def api_status():
    # ... código ...
    pass
"""

# ============================================
# 10. SCRIPT DE VERIFICACIÓN DE SEGURIDAD
# ============================================

def run_security_checks():
    """
    Ejecutar verificaciones de seguridad básicas.
    Llamar al iniciar la aplicación.
    """
    issues = []
    
    # Verificar SECRET_KEY
    if not os.getenv('SECRET_KEY'):
        issues.append("⚠️  SECRET_KEY no configurada")
    
    # Verificar contraseñas por defecto
    if os.getenv('ADMIN_PASSWORD') == 'admin123':
        issues.append("⚠️  Contraseña de admin por defecto detectada")
    
    # Verificar API keys
    if os.getenv('API_MONITOR_KEY') == 'monitor-api-key-change-in-production':
        issues.append("⚠️  API_MONITOR_KEY por defecto detectada")
    
    if os.getenv('ABUSEIPDB_API_KEY') == 'YOUR_API_KEY_HERE':
        issues.append("ℹ️  AbuseIPDB API key no configurada (modo demo)")
    
    # Verificar modo debug en producción
    if os.getenv('FLASK_ENV') == 'production' and os.getenv('FLASK_DEBUG') == '1':
        issues.append("🔴 DEBUG MODE ACTIVADO EN PRODUCCIÓN!")
    
    # Verificar HTTPS
    if os.getenv('FLASK_ENV') == 'production' and not os.getenv('FORCE_HTTPS'):
        issues.append("⚠️  HTTPS no forzado en producción")
    
    
    return len(issues) == 0

# Ejecutar verificaciones al importar el módulo
if __name__ != '__main__':
    run_security_checks()
