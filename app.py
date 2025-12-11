# Imports estándar
import hashlib
import http.client
import json
import os
import random
import socket
import time
from datetime import datetime, timedelta
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

# Imports de terceros
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

# Cargar variables de entorno (.env solo se carga en desarrollo local, no en Vercel)
load_dotenv()

# Detectar entorno de producción (Vercel)
IS_PRODUCTION = os.getenv('VERCEL_ENV') in ['production', 'preview'] or os.getenv('VERCEL') == '1'

# Imports de seguridad
try:
    from security_fixes import (
        configure_security,
        setup_error_handlers,
        setup_secure_logging,
        validate_and_sanitize_ip,
        require_api_key_secure,
        create_csrf_endpoint,
        validate_json_request,
        sanitize_log_input
    )
    SECURITY_ENABLED = True
except ImportError:
    SECURITY_ENABLED = False
    import logging
    logging.basicConfig(level=logging.INFO)


# Constantes de configuración
APP_VERSION = '3.5'
DEFAULT_ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY', 'YOUR_API_KEY_HERE')
API_MONITOR_KEY = os.getenv('API_MONITOR_KEY', 'monitor-api-key-change-in-production')

# Configuración de base de datos
# En producción (Vercel): usa PostgreSQL de Neon desde DATABASE_URL
# En desarrollo: usa SQLite local o PostgreSQL si DATABASE_URL está definida
if IS_PRODUCTION:
    # En Vercel, DATABASE_URL debe estar configurada con PostgreSQL de Neon
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL no configurada en producción. Configure la variable de entorno en Vercel.")
else:
    # En desarrollo local: SQLite por defecto o PostgreSQL si se especifica
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///verip_stats.db')

# Constantes de categorías de AbuseIPDB
ABUSE_CATEGORIES = {
    3: "Fraud", 4: "DDoS Attack", 5: "FTP Brute-Force", 6: "Ping of Death",
    7: "Phishing", 8: "Fraud VoIP", 9: "Open Proxy", 10: "Web Spam",
    11: "Email Spam", 12: "Blog Spam", 13: "VPN IP", 14: "Port Scan",
    15: "Hacking", 16: "SQL Injection", 17: "Spoofing", 18: "Brute-Force",
    19: "Bad Web Bot", 20: "Exploited Host", 21: "Web App Attack",
    22: "SSH", 23: "IoT Targeted"
}

# Blacklists DNS principales
DNS_BLACKLISTS = {
    'zen.spamhaus.org': 'Spamhaus ZEN',
    'sbl.spamhaus.org': 'Spamhaus SBL',
    'cbl.spamhaus.org': 'Spamhaus CBL',
    'css.spamhaus.org': 'Spamhaus CSS',
    'pbl.spamhaus.org': 'Spamhaus PBL',
    'bl.spamcop.net': 'SpamCop',
    'multi.surbl.org': 'SURBL Multi',
    'multi.uribl.com': 'URIBL Multi',
    'dnsbl.sorbs.net': 'SORBS DNSBL',
    'spam.dnsbl.sorbs.net': 'SORBS Spam',
    'http.dnsbl.sorbs.net': 'SORBS HTTP',
    'b.barracudacentral.org': 'Barracuda',
    'cbl.abuseat.org': 'CBL Abuseat',
    'psbl.surriel.com': 'PSBL',
    'ips.backscatterer.org': 'Backscatterer',
    'dnsbl.njabl.org': 'NJABL',
    'rbl.efnetrbl.org': 'EFNet RBL',
    'blackholes.mail-abuse.org': 'Mail Abuse',
    'relays.mail-abuse.org': 'Mail Abuse Relays',
    'dynablock.njabl.org': 'NJABL Dynamic',
    'no-more-funn.moensted.dk': 'No More Funn'
}

# Inicializar Flask app
app = Flask(__name__)

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración adicional para PostgreSQL en Vercel
if IS_PRODUCTION and DATABASE_URL and DATABASE_URL.startswith('postgres'):
    # PostgreSQL requiere pool de conexiones más robusto en serverless
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verificar conexiones antes de usarlas
        'pool_recycle': 300,    # Reciclar conexiones cada 5 minutos
        'pool_size': 2,         # Reducir pool size para serverless
        'max_overflow': 0       # No permitir conexiones extra
    }

# Configurar SECRET_KEY (CRÍTICO para sesiones y CSRF)
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise RuntimeError("SECRET_KEY no configurada en producción. Configure la variable de entorno en Vercel.")
    else:
        # Solo en desarrollo: usar clave por defecto con advertencia
        SECRET_KEY = 'dev-secret-key-change-in-production'


app.config['SECRET_KEY'] = SECRET_KEY

# Configurar seguridad
if SECURITY_ENABLED:
    csrf, limiter = configure_security(app)
    setup_error_handlers(app)

else:
    csrf, limiter = None, None


# Inicializar extensiones de base de datos
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Modelos de base de datos
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get(user_id):
        """Obtener usuario por ID"""
        try:
            if isinstance(user_id, str):
                if not user_id.isdigit():
                    return None
                user_id = int(user_id)
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None

class QueryLog(db.Model):
    __tablename__ = 'query_logs'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    abuse_confidence = db.Column(db.Integer, default=0)
    total_reports = db.Column(db.Integer, default=0)
    is_whitelisted = db.Column(db.Boolean, default=False)
    country_code = db.Column(db.String(2))
    usage_type = db.Column(db.String(50))
    trust_score = db.Column(db.Integer)
    execution_time = db.Column(db.Float)
    api_used = db.Column(db.Boolean, default=False)

class SystemStatus(db.Model):
    __tablename__ = 'system_status'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='online')
    response_time = db.Column(db.Float)
    error_count = db.Column(db.Integer, default=0)

def init_db():
    """Inicializar base de datos y crear tablas si no existen"""
    try:
        db.create_all()
        return True
    except Exception as e:
        print(f"Error inicializando BD: {e}")
        return False

def init_admin_if_needed():
    """Inicializar usuario admin si no existe ninguno"""
    try:
        init_db()
        
        if User.query.filter_by(is_admin=True).first():
            return False
        
        admin_user = User(
            username=DEFAULT_ADMIN_USERNAME,
            password_hash=generate_password_hash(DEFAULT_ADMIN_PASSWORD),
            email=None,
            is_admin=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(admin_user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error inicializando admin: {e}")
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Middleware de validación JSON
if SECURITY_ENABLED:
    @app.before_request
    def check_json():
        return validate_json_request()
    
    # Crear endpoint CSRF
    create_csrf_endpoint(app)

# Decorador para API key (mantener compatibilidad)
def require_api_key(f):
    """Decorador de API key - usa versión segura si está disponible"""
    if SECURITY_ENABLED:
        return require_api_key_secure(f)
    else:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key or api_key != API_MONITOR_KEY:
                return jsonify({'error': 'API key inválida o ausente'}), 401
            return f(*args, **kwargs)
        return decorated_function

def generate_simulated_reputation_data(ip):
    """Generar datos simulados de reputación para demostración"""
    ip_hash = int(hashlib.md5(ip.encode()).hexdigest()[:8], 16)
    random.seed(ip_hash)
    
    abuse_confidence = random.choice([0, 0, 0, 0, 0, 5, 15, 25, 45, 75, 90])
    total_reports = random.choice([0, 0, 0, 1, 3, 8, 25, 50, 150, 500]) if abuse_confidence > 0 else 0
    is_whitelisted = abuse_confidence == 0 and random.random() < 0.1
    
    # Categorías según nivel de confianza
    if abuse_confidence > 50:
        categories = random.sample([4, 5, 15, 18, 20], k=random.randint(1, 3))
    elif abuse_confidence > 25:
        categories = random.sample([8, 9, 14, 22], k=random.randint(0, 2))
    elif abuse_confidence > 0:
        categories = random.sample([11, 13, 19], k=random.randint(0, 1))
    else:
        categories = []
    
    return {
        'success': True,
        'ip': ip,
        'abuse_confidence': abuse_confidence,
        'total_reports': total_reports,
        'is_whitelisted': is_whitelisted,
        'country_code': random.choice(['US', 'DE', 'FR', 'UK', 'CA', 'JP', 'AU']),
        'usage_type': random.choice(['isp', 'hosting', 'business', 'mobile']),
        'isp': random.choice(['Cloudflare', 'Amazon', 'Google', 'Microsoft', 'DigitalOcean']),
        'categories': categories,
        'last_reported': '2024-10-15T10:30:00Z' if total_reports > 0 else None,
        'api_used': False
    }

def check_ip_reputation_abuseipdb(ip):
    """Verificar reputación de IP usando AbuseIPDB API"""
    try:
        if not ABUSEIPDB_API_KEY or ABUSEIPDB_API_KEY == 'YOUR_API_KEY_HERE':
            return generate_simulated_reputation_data(ip)
        
        # Consulta real a AbuseIPDB API
        conn = http.client.HTTPSConnection("api.abuseipdb.com")
        headers = {'Key': ABUSEIPDB_API_KEY, 'Accept': 'application/json'}
        
        conn.request("GET", f"/api/v2/check?ipAddress={ip}&maxAgeInDays=90&verbose", headers=headers)
        response = conn.getresponse()
        data = response.read().decode()
        
        if response.status != 200:
            return {
                'success': False,
                'error': f'AbuseIPDB API error: {response.status}',
                'message': data
            }
        
        result = json.loads(data)
        if 'data' not in result:
            return {
                'success': False,
                'error': 'Respuesta API inválida',
                'message': 'La respuesta no contiene datos esperados'
            }
        
        api_data = result['data']
        return {
            'success': True,
            'ip': api_data.get('ipAddress', ip),
            'abuse_confidence': api_data.get('abuseConfidencePercentage', 0),
            'total_reports': api_data.get('totalReports', 0),
            'is_whitelisted': api_data.get('isWhitelisted', False),
            'country_code': api_data.get('countryCode', 'XX'),
            'usage_type': api_data.get('usageType', 'unknown'),
            'isp': api_data.get('isp', 'Unknown'),
            'categories': api_data.get('categories', []),
            'last_reported': api_data.get('lastReportedAt'),
            'api_used': True
        }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Error conectando con AbuseIPDB API'
        }

def check_dns_blacklist(ip, blacklist_host):
    """Verificar si una IP está en una blacklist DNS específica"""
    try:
        # Invertir la IP para la consulta DNS
        reversed_ip = '.'.join(ip.split('.')[::-1])
        query = f"{reversed_ip}.{blacklist_host}"
        
        # Intentar resolver la consulta DNS
        socket.gethostbyname(query)
        return True  # Si resuelve, la IP está listada
    except socket.gaierror:
        return False  # Si no resuelve, la IP no está listada
    except Exception:
        return False  # En caso de error, asumir no listada

def check_multiple_blacklists(ip):
    """Verificar IP contra múltiples blacklists DNS usando threading"""
    results = {}
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_blacklist = {
            executor.submit(check_dns_blacklist, ip, host): (host, name) 
            for host, name in DNS_BLACKLISTS.items()
        }
        
        for future in future_to_blacklist:
            host, name = future_to_blacklist[future]
            try:
                is_listed = future.result(timeout=3)
                results[host] = {'name': name, 'listed': is_listed, 'host': host}
            except Exception as e:
                results[host] = {'name': name, 'listed': False, 'host': host, 'error': str(e)}
    
    return results

def get_abuse_categories_description(categories):
    """Convertir códigos de categorías de AbuseIPDB a descripciones legibles"""
    return [ABUSE_CATEGORIES.get(cat, f"Category {cat}") for cat in categories]

def calculate_trust_metrics(abuse_confidence, total_reports, is_whitelisted):
    """Calcular métricas de confianza basadas en datos de AbuseIPDB"""
    if is_whitelisted:
        return 100, "Excelente", "high"
    
    if abuse_confidence == 0 and total_reports == 0:
        return 95, "Muy confiable", "high"
    
    trust_levels = [
        (10, 2, 80, "Confiable", "medium"),
        (25, 3, 60, "Moderadamente confiable", "medium"),
        (50, 4, 30, "Sospechosa", "low"),
        (float('inf'), 5, 0, "Peligrosa", "low")
    ]
    
    for threshold, multiplier, min_score, status, level in trust_levels:
        if abuse_confidence <= threshold:
            trust_score = max(min_score, 100 - abuse_confidence - (total_reports * multiplier))
            return int(trust_score), status, level

def get_geolocation(ip):
    """Obtener información de geolocalización de una IP"""
    try:
        conn = http.client.HTTPSConnection("ipwhois.app")
        conn.request("GET", f"/json/{ip}")
        response = conn.getresponse()
        geo_info = json.loads(response.read().decode())

        if not geo_info.get("success", False):
            return {'success': False}
        
        return {
            'success': True,
            'country': geo_info.get('country', 'N/A'),
            'region': geo_info.get('region', 'N/A'),
            'city': geo_info.get('city', 'N/A'),
            'isp': geo_info.get('isp', 'N/A'),
            'org': geo_info.get('org', 'N/A'),
            'latitude': geo_info.get('latitude', 'N/A'),
            'longitude': geo_info.get('longitude', 'N/A'),
            'timezone': geo_info.get('timezone', 'N/A')
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def calculate_simulated_categories(reputation):
    """Calcular categorías simuladas basadas en datos de AbuseIPDB"""
    abuse_conf = reputation['abuse_confidence']
    categories = reputation['categories']
    
    def calc_listed(condition, high_div, low_div, max_val):
        if condition:
            return min(max_val, max(1, int(abuse_conf / high_div)))
        elif abuse_conf > 25:
            return min(max_val // 2, max(1, int(abuse_conf / low_div)))
        return 0
    
    spam_listed = calc_listed(any(c in [10, 11, 12] for c in categories), 5, 15, 8)
    security_listed = calc_listed(any(c in [15, 16, 20, 21, 7] for c in categories), 4, 10, 12)
    proxy_listed = min(3, max(1, int(abuse_conf / 20))) if any(c in [9, 13] for c in categories) else 0
    sorbs_listed = calc_listed(any(c in [4, 14, 18] for c in categories), 6, 12, 10)
    
    policy_listed = 0
    usage_type = reputation['usage_type']
    if usage_type == 'hosting' and abuse_conf > 10:
        policy_listed = min(6, max(1, int(abuse_conf / 8)))
    elif usage_type == 'isp' and abuse_conf > 30:
        policy_listed = min(3, max(1, int(abuse_conf / 15)))
    
    return {
        'Spam Blacklists': {'listed': spam_listed, 'total': 29, 'blacklists': []},
        'Security/Malware Blacklists': {'listed': security_listed, 'total': 14, 'blacklists': []},
        'Tor/Proxy Blacklists': {'listed': proxy_listed, 'total': 3, 'blacklists': []},
        'SORBS Blacklists': {'listed': sorbs_listed, 'total': 14, 'blacklists': []},
        'Policy/Bogon Blacklists': {'listed': policy_listed, 'total': 14, 'blacklists': []}
    }

def verify_ip(ip):
    """Función principal de verificación - usa AbuseIPDB y blacklists DNS"""
    # Validar IP (ya validada en la ruta, esta es validación adicional)
    try:
        socket.inet_aton(ip)
    except socket.error:
        return {'error': f"'{ip}' no es una dirección IP válida."}

    start_time = time.time()
    
    # Obtener geolocalización (mantener funcionalidad existente)
    geo_info = get_geolocation(ip)
    
    # Verificar reputación con AbuseIPDB (reemplaza toda la lógica de blacklists DNS)
    reputation = check_ip_reputation_abuseipdb(ip)
    
    if not reputation['success']:
        return {
            'error': 'Error verificando reputación de IP',
            'details': reputation.get('message', 'Error desconocido')
        }
    
    # NUEVO: Verificar blacklists DNS reales en paralelo
    print(f"Verificando {ip} en blacklists DNS...")
    blacklist_results = check_multiple_blacklists(ip)
    
    # Contar cuántas blacklists tienen la IP listada
    blacklists_listed = sum(1 for bl in blacklist_results.values() if bl.get('listed', False))
    total_blacklists_checked = len(blacklist_results)
    
    print(f"Resultado: {blacklists_listed}/{total_blacklists_checked} blacklists reportan la IP")
    
    # Calcular métricas de confianza usando datos profesionales
    trust_score, trust_status, trust_level = calculate_trust_metrics(
        reputation['abuse_confidence'], 
        reputation['total_reports'], 
        reputation['is_whitelisted']
    )
    
    # Obtener descripciones de categorías de amenazas
    category_descriptions = get_abuse_categories_description(reputation['categories'])
    
    execution_time = time.time() - start_time
    
    # Registrar consulta en base de datos
    log_query_to_database(ip, reputation, trust_score, execution_time)
    
    simulated_categories = calculate_simulated_categories(reputation)
    total_listed = sum(cat['listed'] for cat in simulated_categories.values())
    
    return {
        'ip': ip,
        'geolocation': geo_info,
        'trust_score': trust_score,
        'trust_status': trust_status,
        'trust_level': trust_level,
        'listed_count': total_listed,
        'spam_count': len([cat for cat in reputation['categories'] if cat in [10, 11, 12]]),
        'policy_count': 1 if reputation['usage_type'] == 'isp' else 0,
        'total_blacklists': 74,  # Mantener para compatibilidad con frontend
        'categories': simulated_categories,
        'execution_time': execution_time,
        # Nuevos campos con datos profesionales de AbuseIPDB
        'abuseipdb': {
            'abuse_confidence': reputation['abuse_confidence'],
            'total_reports': reputation['total_reports'],
            'is_whitelisted': reputation['is_whitelisted'],
            'threat_categories': category_descriptions,
            'last_reported': reputation.get('last_reported'),
            'country_code': reputation.get('country_code'),
            'usage_type': reputation.get('usage_type'),
            'isp': reputation.get('isp'),
            'api_used': reputation.get('api_used', False)
        },
        # NUEVO: Resultados reales de blacklists DNS
        'dns_blacklists': blacklist_results,
        'blacklist_summary': {
            'listed_count': blacklists_listed,
            'total_checked': total_blacklists_checked,
            'percentage': round((blacklists_listed / total_blacklists_checked) * 100, 1) if total_blacklists_checked > 0 else 0
        }
    }

def log_query_to_database(ip, reputation, trust_score, execution_time):
    """Registrar consulta en la base de datos"""
    try:
        init_db()
        log_entry = QueryLog(
            ip_address=ip,
            abuse_confidence=reputation['abuse_confidence'],
            total_reports=reputation['total_reports'],
            is_whitelisted=reputation['is_whitelisted'],
            country_code=reputation.get('country_code'),
            usage_type=reputation.get('usage_type'),
            trust_score=trust_score,
            execution_time=execution_time,
            api_used=reputation.get('api_used', False)
        )
        db.session.add(log_entry)
        db.session.commit()
        print(f"✅ Consulta registrada: IP={ip}, Trust={trust_score}")
    except Exception as e:
        print(f"❌ Error registrando consulta: {e}")
        db.session.rollback()

# ============================================
# RUTAS PÚBLICAS
# ============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint para diagnosticar el estado de la aplicación"""
    try:
        init_admin_if_needed()
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'users': User.query.count(),
            'queries': QueryLog.query.count(),
            'environment': os.getenv('VERCEL_ENV', 'local'),
            'version': APP_VERSION
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'error': str(e),
            'environment': os.getenv('VERCEL_ENV', 'local')
        }), 500

@app.route('/verify', methods=['POST'])
def verify():
    # Aplicar rate limiting si está disponible
    if SECURITY_ENABLED and limiter:
        limiter.limit("10 per minute")(lambda: None)()
    
    data = request.get_json()
    ip_input = data.get('ip', '').strip()
    
    if not ip_input:
        return jsonify({'error': 'Por favor ingresa una dirección IP'}), 400
    
    # Validación segura de IP
    if SECURITY_ENABLED:
        ip, error = validate_and_sanitize_ip(ip_input)
        if error:
            return jsonify({'error': error}), 400
    else:
        ip = ip_input
    
    result = verify_ip(ip)
    return jsonify(result)

# ============================================
# RUTAS DE ADMINISTRADOR
# ============================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Rate limiting para prevenir brute force
    if SECURITY_ENABLED and limiter:
        limiter.limit("5 per minute")(lambda: None)()
    
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    init_admin_if_needed()
    
    if request.method != 'POST':
        return render_template('admin_login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        if SECURITY_ENABLED:
            time.sleep(1)  # Delay anti-brute-force
        flash('Usuario o contraseña incorrectos', 'error')
        return render_template('admin_login.html')
    
    # Regenerar sesión tras login exitoso
    if SECURITY_ENABLED:
        session.permanent = True
        session.modified = True

    
    user.last_login = datetime.utcnow()
    db.session.commit()
    login_user(user, remember=False)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

def get_dashboard_stats():
    """Obtener estadísticas para el dashboard de administrador"""
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    seven_days_ago = now - timedelta(days=7)
    
    # IPs más consultadas
    top_ips = db.session.query(
        QueryLog.ip_address,
        func.count(QueryLog.ip_address).label('count')
    ).group_by(QueryLog.ip_address).order_by(func.count(QueryLog.ip_address).desc()).limit(10).all()
    
    # Consultas por día (últimos 7 días)
    daily_queries = db.session.query(
        func.date(QueryLog.timestamp).label('date'),
        func.count(QueryLog.id).label('count')
    ).filter(QueryLog.timestamp >= seven_days_ago).group_by(func.date(QueryLog.timestamp)).all()
    
    # Consultas por país
    country_stats = db.session.query(
        QueryLog.country_code,
        func.count(QueryLog.country_code).label('count')
    ).filter(QueryLog.country_code.isnot(None)).group_by(
        QueryLog.country_code
    ).order_by(func.count(QueryLog.country_code).desc()).limit(10).all()
    
    return {
        'total_queries': QueryLog.query.count(),
        'today_queries': QueryLog.query.filter(QueryLog.timestamp >= now.date()).count(),
        'queries_24h': QueryLog.query.filter(QueryLog.timestamp >= last_24h).count(),
        'top_ips': [(ip, count) for ip, count in top_ips],
        'daily_queries': [(str(date), count) for date, count in daily_queries],
        'avg_trust_score': round(db.session.query(func.avg(QueryLog.trust_score)).scalar() or 0, 2),
        'high_risk_count': QueryLog.query.filter(QueryLog.abuse_confidence > 50).count(),
        'whitelisted_count': QueryLog.query.filter(QueryLog.is_whitelisted == True).count(),
        'country_stats': [(country, count) for country, count in country_stats],
        'api_queries': QueryLog.query.filter(QueryLog.api_used == True).count(),
        'simulated_queries': QueryLog.query.filter(QueryLog.api_used == False).count()
    }

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    stats = get_dashboard_stats()
    return render_template('admin_dashboard.html', stats=stats, api_key=API_MONITOR_KEY)

# ============================================
# API DE MONITOREO
# ============================================

@app.route('/api/status')
@require_api_key
def api_status():
    """Endpoint para verificar el estado del servicio"""
    # Rate limiting
    if SECURITY_ENABLED and limiter:
        limiter.limit("30 per minute")(lambda: None)()
    
    try:
        db.session.execute('SELECT 1')
        last_query = QueryLog.query.order_by(QueryLog.timestamp.desc()).first()
        
        return jsonify({
            'status': 'online',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'total_queries': QueryLog.query.count(),
            'last_query': last_query.timestamp.isoformat() if last_query else None,
            'avg_response_time': round(db.session.query(func.avg(QueryLog.execution_time)).scalar() or 0, 3),
            'version': APP_VERSION
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@app.route('/api/stats')
@require_api_key
def api_stats():
    """Endpoint para obtener estadísticas detalladas"""
    # Rate limiting
    if SECURITY_ENABLED and limiter:
        limiter.limit("30 per minute")(lambda: None)()
    
    period = request.args.get('period', '7d')
    
    period_map = {'24h': timedelta(hours=24), '30d': timedelta(days=30), '7d': timedelta(days=7)}
    since = datetime.utcnow() - period_map.get(period, timedelta(days=7))
    
    # Consultas en el período
    queries = QueryLog.query.filter(QueryLog.timestamp >= since).all()
    
    # Estadísticas
    total = len(queries)
    high_risk = len([q for q in queries if q.abuse_confidence > 50])
    medium_risk = len([q for q in queries if 25 < q.abuse_confidence <= 50])
    low_risk = len([q for q in queries if q.abuse_confidence <= 25])
    whitelisted = len([q for q in queries if q.is_whitelisted])
    
    # Agrupar por día
    daily_stats = {}
    for query in queries:
        date_key = query.timestamp.strftime('%Y-%m-%d')
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                'total': 0,
                'high_risk': 0,
                'api_used': 0
            }
        daily_stats[date_key]['total'] += 1
        if query.abuse_confidence > 50:
            daily_stats[date_key]['high_risk'] += 1
        if query.api_used:
            daily_stats[date_key]['api_used'] += 1
    
    # Top países
    country_counts = {}
    for query in queries:
        if query.country_code:
            country_counts[query.country_code] = country_counts.get(query.country_code, 0) + 1
    
    return jsonify({
        'period': period,
        'since': since.isoformat(),
        'summary': {
            'total_queries': total,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk,
            'whitelisted': whitelisted
        },
        'daily_stats': daily_stats,
        'top_countries': dict(sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    })

@app.route('/api/recent')
@require_api_key
def api_recent():
    """Endpoint para obtener consultas recientes"""
    # Rate limiting
    if SECURITY_ENABLED and limiter:
        limiter.limit("30 per minute")(lambda: None)()
    
    limit = int(request.args.get('limit', 50))
    
    queries = QueryLog.query.order_by(QueryLog.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'count': len(queries),
        'queries': [{
            'ip': q.ip_address,
            'timestamp': q.timestamp.isoformat(),
            'abuse_confidence': q.abuse_confidence,
            'trust_score': q.trust_score,
            'country': q.country_code,
            'is_whitelisted': q.is_whitelisted
        } for q in queries]
    })

if __name__ == '__main__':
    # Verificar modo debug
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    
    app.run(debug=debug_mode, port=5000, host='127.0.0.1' if debug_mode else '0.0.0.0')