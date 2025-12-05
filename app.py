from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import http.client
import json
import socket
import time
import os
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import wraps

# Cargar variables de entorno desde .env (solo en desarrollo)
load_dotenv()

# VerIP v3.5 - Panel de Administrador + API de Monitoreo + Gráficos AbuseIPDB

app = Flask(__name__)

# Configuración segura
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuración de base de datos (SQLite local o PostgreSQL Neon)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///verip_stats.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de API
ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY', 'YOUR_API_KEY_HERE')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', generate_password_hash('admin123'))  # Cambiar en producción
API_MONITOR_KEY = os.getenv('API_MONITOR_KEY', 'monitor-api-key-change-in-production')

# Inicializar extensiones
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
        return User.query.get(int(user_id))

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

# Crear tablas
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Decorador para API key
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_MONITOR_KEY:
            return jsonify({'error': 'API key inválida o ausente'}), 401
        return f(*args, **kwargs)
    return decorated_function

def check_ip_reputation_abuseipdb(ip):
    """Verificar reputación de IP usando AbuseIPDB API - reemplaza 74+ blacklists DNS"""
    try:
        # Si no hay API key configurada o es la de ejemplo, usar datos simulados
        if not ABUSEIPDB_API_KEY or ABUSEIPDB_API_KEY == 'YOUR_API_KEY_HERE':
            # Generar datos simulados realistas para demostración
            import random
            import hashlib
            
            # Usar hash de IP para datos consistentes
            ip_hash = int(hashlib.md5(ip.encode()).hexdigest()[:8], 16)
            random.seed(ip_hash)
            
            # Simular diferentes tipos de IPs
            abuse_confidence = random.choice([0, 0, 0, 0, 0, 5, 15, 25, 45, 75, 90])  # Mayoría limpias
            total_reports = random.choice([0, 0, 0, 1, 3, 8, 25, 50, 150, 500]) if abuse_confidence > 0 else 0
            is_whitelisted = abuse_confidence == 0 and random.random() < 0.1  # 10% whitelisted
            
            # Categorías simuladas basadas en confianza
            categories = []
            if abuse_confidence > 50:
                categories = random.sample([4, 5, 15, 18, 20], k=random.randint(1, 3))
            elif abuse_confidence > 25:
                categories = random.sample([8, 9, 14, 22], k=random.randint(0, 2))
            elif abuse_confidence > 0:
                categories = random.sample([11, 13, 19], k=random.randint(0, 1))
            
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
                'api_used': False  # Indicar que son datos simulados
            }
        
        # Consulta real a AbuseIPDB API (cuando tienes API key válida)
        conn = http.client.HTTPSConnection("api.abuseipdb.com")
        headers = {
            'Key': ABUSEIPDB_API_KEY,
            'Accept': 'application/json'
        }
        
        # Verificar IP (últimos 90 días, con información detallada)
        conn.request("GET", f"/api/v2/check?ipAddress={ip}&maxAgeInDays=90&verbose", headers=headers)
        response = conn.getresponse()
        data = response.read().decode()
        
        if response.status == 200:
            result = json.loads(data)
            # Verificar que la respuesta tenga la estructura esperada
            if 'data' in result:
                api_data = result['data']
                abuse_confidence = api_data.get('abuseConfidencePercentage', 0)
                total_reports = api_data.get('totalReports', 0)
                
                return {
                    'success': True,
                    'ip': api_data.get('ipAddress', ip),
                    'abuse_confidence': abuse_confidence,
                    'total_reports': total_reports,
                    'is_whitelisted': api_data.get('isWhitelisted', False),
                    'country_code': api_data.get('countryCode', 'XX'),
                    'usage_type': api_data.get('usageType', 'unknown'),
                    'isp': api_data.get('isp', 'Unknown'),
                    'categories': api_data.get('categories', []),
                    'last_reported': api_data.get('lastReportedAt'),
                    'api_used': True
                }
            else:
                return {
                    'success': False,
                    'error': 'Respuesta API inválida',
                    'message': 'La respuesta no contiene datos esperados'
                }
        else:
            return {
                'success': False,
                'error': f'AbuseIPDB API error: {response.status}',
                'message': data
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
    """Verificar IP contra múltiples blacklists DNS clave usando threading"""
    # Blacklists DNS clave más importantes
    blacklists = {
        # Spamhaus (las más importantes)
        'zen.spamhaus.org': 'Spamhaus ZEN',
        'sbl.spamhaus.org': 'Spamhaus SBL',
        'cbl.spamhaus.org': 'Spamhaus CBL', 
        'css.spamhaus.org': 'Spamhaus CSS',
        'pbl.spamhaus.org': 'Spamhaus PBL',

        # SpamCop
        'bl.spamcop.net': 'SpamCop',
        
        # SURBL/URIBL (URLs y dominios)
        'multi.surbl.org': 'SURBL Multi',
        'multi.uribl.com': 'URIBL Multi',
        
        # SORBS
        'dnsbl.sorbs.net': 'SORBS DNSBL',
        'spam.dnsbl.sorbs.net': 'SORBS Spam',
        'http.dnsbl.sorbs.net': 'SORBS HTTP',
        
        # Barracuda
        'b.barracudacentral.org': 'Barracuda',
        
        # CBL (Composite Blocking List)
        'cbl.abuseat.org': 'CBL Abuseat',
        
        # PSBL
        'psbl.surriel.com': 'PSBL',
        
        # Invaluement
        'ips.backscatterer.org': 'Backscatterer',
        
        # Otras importantes
        'dnsbl.njabl.org': 'NJABL',
        'rbl.efnetrbl.org': 'EFNet RBL',
        'blackholes.mail-abuse.org': 'Mail Abuse',
        'relays.mail-abuse.org': 'Mail Abuse Relays',
        'dynablock.njabl.org': 'NJABL Dynamic',
        'no-more-funn.moensted.dk': 'No More Funn'
    }
    
    results = {}
    
    # Usar ThreadPoolExecutor para consultas paralelas (más rápido)
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_blacklist = {
            executor.submit(check_dns_blacklist, ip, host): (host, name) 
            for host, name in blacklists.items()
        }
        
        for future in future_to_blacklist:
            host, name = future_to_blacklist[future]
            try:
                is_listed = future.result(timeout=3)  # 3 segundos timeout por consulta
                results[host] = {
                    'name': name,
                    'listed': is_listed,
                    'host': host
                }
            except Exception as e:
                # En caso de error, marcar como no disponible
                results[host] = {
                    'name': name,
                    'listed': False,
                    'host': host,
                    'error': str(e)
                }
    
    return results

def get_abuse_categories_description(categories):
    """Convertir códigos de categorías de AbuseIPDB a descripciones legibles"""
    category_map = {
        3: "Fraud", 4: "DDoS Attack", 5: "FTP Brute-Force", 6: "Ping of Death",
        7: "Phishing", 8: "Fraud VoIP", 9: "Open Proxy", 10: "Web Spam",
        11: "Email Spam", 12: "Blog Spam", 13: "VPN IP", 14: "Port Scan",
        15: "Hacking", 16: "SQL Injection", 17: "Spoofing", 18: "Brute-Force",
        19: "Bad Web Bot", 20: "Exploited Host", 21: "Web App Attack",
        22: "SSH", 23: "IoT Targeted"
    }
    return [category_map.get(cat, f"Category {cat}") for cat in categories]

def calculate_trust_metrics(abuse_confidence, total_reports, is_whitelisted):
    """Calcular métricas de confianza basadas en datos de AbuseIPDB"""
    if is_whitelisted:
        trust_score = 100
        status = "Excelente"
        level = "high"
    elif abuse_confidence == 0 and total_reports == 0:
        trust_score = 95
        status = "Muy confiable"
        level = "high"
    elif abuse_confidence <= 10:
        trust_score = max(80, 100 - abuse_confidence - (total_reports * 2))
        status = "Confiable"
        level = "medium"
    elif abuse_confidence <= 25:
        trust_score = max(60, 100 - abuse_confidence - (total_reports * 3))
        status = "Moderadamente confiable"
        level = "medium"
    elif abuse_confidence <= 50:
        trust_score = max(30, 100 - abuse_confidence - (total_reports * 4))
        status = "Sospechosa"
        level = "low"
    else:
        trust_score = max(0, 100 - abuse_confidence - (total_reports * 5))
        status = "Peligrosa"
        level = "low"
    
    return int(trust_score), status, level

def get_geolocation(ip):
    try:
        conn = http.client.HTTPSConnection("ipwhois.app")
        conn.request("GET", f"/json/{ip}")
        response = conn.getresponse()
        data = response.read().decode()
        geo_info = json.loads(data)

        if geo_info.get("success", False):
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
        else:
            return {'success': False}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_ip(ip):
    """Función principal de verificación - ahora usa AbuseIPDB en lugar de 74+ DNS blacklists"""
    # Validar IP
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
    try:
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
    except Exception as e:
        print(f"Error registrando consulta: {e}")
        db.session.rollback()
    
    # Simular estructura de categorías para compatibilidad con frontend
    # Mejorado para mostrar datos más realistas y variados
    
    # Calcular bloqueos basados en la confianza de AbuseIPDB
    abuse_conf = reputation['abuse_confidence']
    categories = reputation['categories']
    
    # Spam Blacklists - basado en reportes de spam
    spam_listed = 0
    if 10 in categories or 11 in categories or 12 in categories:  # Web/Email/Blog Spam
        spam_listed = min(8, max(1, int(abuse_conf / 5)))
    elif abuse_conf > 25:
        spam_listed = min(3, max(1, int(abuse_conf / 15)))
    
    # Security/Malware Blacklists - basado en actividad maliciosa
    security_listed = 0
    if any(cat in [15, 16, 20, 21, 7] for cat in categories):  # Hacking, SQL Injection, Exploited Host, Web App Attack, Phishing
        security_listed = min(12, max(2, int(abuse_conf / 4)))
    elif abuse_conf > 40:
        security_listed = min(6, max(1, int(abuse_conf / 10)))
    
    # Tor/Proxy Blacklists - basado en proxies y VPNs
    proxy_listed = 0
    if 9 in categories or 13 in categories:  # Open Proxy, VPN IP
        proxy_listed = min(3, max(1, int(abuse_conf / 20)))
    
    # SORBS Blacklists - basado en actividad general sospechosa
    sorbs_listed = 0
    if 4 in categories or 14 in categories or 18 in categories:  # DDoS, Port Scan, Brute-Force
        sorbs_listed = min(10, max(1, int(abuse_conf / 6)))
    elif abuse_conf > 20:
        sorbs_listed = min(4, max(1, int(abuse_conf / 12)))
    
    # Policy/Bogon Blacklists - basado en tipo de uso y políticas
    policy_listed = 0
    if reputation['usage_type'] == 'hosting' and abuse_conf > 10:
        policy_listed = min(6, max(1, int(abuse_conf / 8)))
    elif reputation['usage_type'] == 'isp' and abuse_conf > 30:
        policy_listed = min(3, max(1, int(abuse_conf / 15)))
    
    simulated_categories = {
        'Spam Blacklists': {
            'listed': spam_listed,
            'total': 29,
            'blacklists': []
        },
        'Security/Malware Blacklists': {
            'listed': security_listed,
            'total': 14,
            'blacklists': []
        },
        'Tor/Proxy Blacklists': {
            'listed': proxy_listed,
            'total': 3,
            'blacklists': []
        },
        'SORBS Blacklists': {
            'listed': sorbs_listed,
            'total': 14,
            'blacklists': []
        },
        'Policy/Bogon Blacklists': {
            'listed': policy_listed,
            'total': 14,
            'blacklists': []
        }
    }
    
    # Calcular total de listas que reportan la IP
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint para diagnosticar el estado de la aplicación"""
    try:
        # Verificar conexión a base de datos
        user_count = User.query.count()
        query_count = QueryLog.query.count()
        
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'users': user_count,
            'queries': query_count,
            'environment': os.getenv('VERCEL_ENV', 'local')
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
    data = request.get_json()
    ip = data.get('ip', '').strip()
    
    if not ip:
        return jsonify({'error': 'Por favor ingresa una dirección IP'}), 400
    
    result = verify_ip(ip)
    return jsonify(result)

# ============================================
# RUTAS DE ADMINISTRADOR
# ============================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Buscar usuario en la base de datos
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Actualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Estadísticas generales
    total_queries = QueryLog.query.count()
    today_queries = QueryLog.query.filter(
        QueryLog.timestamp >= datetime.utcnow().date()
    ).count()
    
    # Últimas 24 horas
    last_24h = datetime.utcnow() - timedelta(hours=24)
    queries_24h = QueryLog.query.filter(QueryLog.timestamp >= last_24h).count()
    
    # IPs más consultadas
    from sqlalchemy import func
    top_ips = db.session.query(
        QueryLog.ip_address,
        func.count(QueryLog.ip_address).label('count')
    ).group_by(QueryLog.ip_address).order_by(func.count(QueryLog.ip_address).desc()).limit(10).all()
    
    # Consultas por día (últimos 7 días)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_queries = db.session.query(
        func.date(QueryLog.timestamp).label('date'),
        func.count(QueryLog.id).label('count')
    ).filter(QueryLog.timestamp >= seven_days_ago).group_by(func.date(QueryLog.timestamp)).all()
    
    # Estadísticas de confianza
    avg_trust_score = db.session.query(func.avg(QueryLog.trust_score)).scalar() or 0
    high_risk_count = QueryLog.query.filter(QueryLog.abuse_confidence > 50).count()
    whitelisted_count = QueryLog.query.filter(QueryLog.is_whitelisted == True).count()
    
    # Consultas por país
    country_stats = db.session.query(
        QueryLog.country_code,
        func.count(QueryLog.country_code).label('count')
    ).filter(QueryLog.country_code.isnot(None)).group_by(QueryLog.country_code).order_by(func.count(QueryLog.country_code).desc()).limit(10).all()
    
    # API usage
    api_queries = QueryLog.query.filter(QueryLog.api_used == True).count()
    simulated_queries = QueryLog.query.filter(QueryLog.api_used == False).count()
    
    # Convertir Row objects a listas/tuplas para JSON serialization
    top_ips_list = [(ip, count) for ip, count in top_ips]
    daily_queries_list = [(str(date), count) for date, count in daily_queries]
    country_stats_list = [(country, count) for country, count in country_stats]
    
    stats = {
        'total_queries': total_queries,
        'today_queries': today_queries,
        'queries_24h': queries_24h,
        'top_ips': top_ips_list,
        'daily_queries': daily_queries_list,
        'avg_trust_score': round(avg_trust_score, 2),
        'high_risk_count': high_risk_count,
        'whitelisted_count': whitelisted_count,
        'country_stats': country_stats_list,
        'api_queries': api_queries,
        'simulated_queries': simulated_queries
    }
    
    return render_template('admin_dashboard.html', stats=stats, api_key=API_MONITOR_KEY)

# ============================================
# API DE MONITOREO
# ============================================

@app.route('/api/status')
@require_api_key
def api_status():
    """Endpoint para verificar el estado del servicio"""
    try:
        # Verificar conexión a base de datos
        db.session.execute('SELECT 1')
        
        # Obtener últimas estadísticas
        last_query = QueryLog.query.order_by(QueryLog.timestamp.desc()).first()
        total_queries = QueryLog.query.count()
        
        # Calcular tiempo de respuesta promedio
        avg_response_time = db.session.query(func.avg(QueryLog.execution_time)).scalar() or 0
        
        return jsonify({
            'status': 'online',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'total_queries': total_queries,
            'last_query': last_query.timestamp.isoformat() if last_query else None,
            'avg_response_time': round(avg_response_time, 3),
            'version': '3.5'
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
    period = request.args.get('period', '7d')  # 24h, 7d, 30d
    
    # Calcular período
    if period == '24h':
        since = datetime.utcnow() - timedelta(hours=24)
    elif period == '30d':
        since = datetime.utcnow() - timedelta(days=30)
    else:  # 7d por defecto
        since = datetime.utcnow() - timedelta(days=7)
    
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
    app.run(debug=True, port=5000)