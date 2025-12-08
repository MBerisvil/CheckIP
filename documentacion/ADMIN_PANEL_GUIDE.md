# VerIP v3.5 - Nuevas Funcionalidades

## 🎉 Novedades Implementadas

### 1. 🔐 Panel de Administrador

Se ha implementado un sistema completo de administración con:

- **Login seguro**: Autenticación con usuario y contraseña usando Flask-Login
- **Protección de contraseñas**: Hash seguro con Werkzeug
- **Dashboard completo**: Visualización de todas las estadísticas

#### Acceso al Panel
- **URL**: `http://localhost:5000/admin/login`
- **Usuario por defecto**: `admin`
- **Contraseña por defecto**: `admin123` (⚠️ CAMBIAR EN PRODUCCIÓN)

### 2. 📊 Dashboard Administrativo

El panel incluye:

- **Estadísticas en tiempo real**:
  - Total de consultas realizadas
  - Consultas de hoy
  - Consultas últimas 24h
  - Score de confianza promedio
  - IPs de alto riesgo detectadas
  - IPs en whitelist
  - Uso de API real vs datos simulados

- **Gráficos interactivos** (Chart.js):
  - Consultas por día (últimos 7 días)
  - Consultas por país (Top 10)
  - Estadísticas de AbuseIPDB API

- **Tablas de datos**:
  - IPs más consultadas
  - Información de configuración del sistema

### 3. 🔌 API de Monitoreo

Se han creado 3 endpoints REST para monitoreo externo:

#### **GET /api/status**
Verifica el estado del servicio

**Headers requeridos**:
```
X-API-Key: tu-api-key-aqui
```

**Respuesta**:
```json
{
  "status": "online",
  "timestamp": "2024-12-05T10:30:00Z",
  "database": "connected",
  "total_queries": 1523,
  "last_query": "2024-12-05T10:29:45Z",
  "avg_response_time": 0.523,
  "version": "3.5"
}
```

#### **GET /api/stats?period=7d**
Obtiene estadísticas detalladas

**Parámetros**:
- `period`: `24h`, `7d` (default), `30d`

**Headers requeridos**:
```
X-API-Key: tu-api-key-aqui
```

**Respuesta**:
```json
{
  "period": "7d",
  "since": "2024-11-28T10:30:00Z",
  "summary": {
    "total_queries": 450,
    "high_risk": 23,
    "medium_risk": 67,
    "low_risk": 360,
    "whitelisted": 15
  },
  "daily_stats": {...},
  "top_countries": {...}
}
```

#### **GET /api/recent?limit=50**
Obtiene las consultas más recientes

**Parámetros**:
- `limit`: cantidad de resultados (default: 50)

**Headers requeridos**:
```
X-API-Key: tu-api-key-aqui
```

**Respuesta**:
```json
{
  "count": 50,
  "queries": [
    {
      "ip": "8.8.8.8",
      "timestamp": "2024-12-05T10:29:45Z",
      "abuse_confidence": 0,
      "trust_score": 95,
      "country": "US",
      "is_whitelisted": false
    }
  ]
}
```

### 4. 📈 Sistema de Registro de Consultas

Todas las consultas se registran automáticamente en SQLite:

**Base de datos**: `verip_stats.db`

**Tablas**:
- `query_logs`: Historial de todas las consultas
- `system_status`: Estado del sistema

**Campos registrados**:
- IP consultada
- Timestamp
- Nivel de confianza de abuso
- Total de reportes
- País de origen
- Tipo de uso
- Score de confianza
- Tiempo de ejecución
- Si se usó API real o datos simulados

### 5. 📊 Gráficos AbuseIPDB

Visualizaciones implementadas con Chart.js:

1. **Gráfico de línea**: Consultas por día (últimos 7 días)
2. **Gráfico de barras**: Distribución por países
3. **Gráfico de dona**: 
   - Consultas usando API real
   - Consultas con datos simulados
   - IPs de alto riesgo
   - IPs en whitelist

## 🚀 Instalación de Dependencias

```bash
pip install -r requirements.txt
```

**Nuevas dependencias agregadas**:
- Flask-Login==0.6.3
- Werkzeug==2.3.7
- Flask-SQLAlchemy==3.0.5

## ⚙️ Configuración

### 1. Variables de Entorno

Copia `.env.example` a `.env` y configura:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
ABUSEIPDB_API_KEY=tu-api-key-de-abuseipdb
SECRET_KEY=clave-secreta-aleatoria-para-flask
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=hash-de-tu-contraseña
API_MONITOR_KEY=clave-para-api-de-monitoreo
```

### 2. Generar Hash de Contraseña

Para generar un hash seguro de tu contraseña:

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('tu-contraseña-aqui'))
```

### 3. Iniciar la Aplicación

```bash
python app.py
```

La base de datos se creará automáticamente en el primer inicio.

## 📱 Uso

### Acceso Web Principal
- URL: `http://localhost:5000`
- Función: Verificación de IPs (pública)

### Panel de Administrador
- URL: `http://localhost:5000/admin/login`
- Usuario: `admin` (configurable)
- Contraseña: `admin123` (⚠️ cambiar)

### API de Monitoreo
Todas las peticiones requieren el header:
```
X-API-Key: tu-api-key
```

**Ejemplo con curl**:
```bash
curl -H "X-API-Key: monitor-api-key-change-in-production" \
     http://localhost:5000/api/status
```

**Ejemplo con Python**:
```python
import requests

headers = {'X-API-Key': 'monitor-api-key-change-in-production'}
response = requests.get('http://localhost:5000/api/status', headers=headers)
print(response.json())
```

## 🔒 Seguridad

### Recomendaciones para Producción:

1. **Cambiar credenciales por defecto**:
   - Usuario administrador
   - Contraseña administrador
   - Secret key de Flask
   - API key de monitoreo

2. **Variables de entorno**:
   - Nunca commitear el archivo `.env`
   - Usar variables de entorno del servidor en producción

3. **Base de datos**:
   - Considerar migrar a PostgreSQL para producción
   - Implementar backups regulares

4. **HTTPS**:
   - Usar HTTPS en producción
   - Configurar certificados SSL/TLS

5. **Rate limiting**:
   - Considerar implementar Flask-Limiter para proteger endpoints

## 📊 Estructura de Archivos Nuevos

```
Verificar-IP/
├── app.py                          # Actualizado con nuevas funcionalidades
├── requirements.txt                # Dependencias actualizadas
├── .env.example                    # Ejemplo de configuración
├── verip_stats.db                  # Base de datos SQLite (auto-generada)
└── templates/
    ├── admin_login.html            # NUEVO: Login de administrador
    └── admin_dashboard.html        # NUEVO: Dashboard con gráficos
```

## 🎯 Características Técnicas

### Backend
- Flask 2.3.3
- Flask-Login para autenticación
- Flask-SQLAlchemy para ORM
- SQLite para almacenamiento
- Werkzeug para seguridad de contraseñas

### Frontend
- Chart.js 4.4.0 para gráficos
- CSS moderno con gradientes
- Diseño responsive
- Tablas interactivas

### API
- RESTful endpoints
- Autenticación por API key
- Respuestas JSON estructuradas
- Manejo de errores

## 🐛 Troubleshooting

### Error de importación de módulos
```bash
pip install -r requirements.txt --upgrade
```

### Base de datos no se crea
La base de datos se crea automáticamente. Si hay problemas:
```python
from app import app, db
with app.app_context():
    db.create_all()
```

### No puedo acceder al panel de administrador
Verifica que estés usando las credenciales correctas:
- Usuario: `admin`
- Contraseña: `admin123` (por defecto)

### API retorna 401 Unauthorized
Verifica que estés enviando el header correcto:
```
X-API-Key: monitor-api-key-change-in-production
```

## 📝 Notas de Versión

**v3.5** - 5 de diciembre de 2024
- ✅ Panel de administrador completo
- ✅ API de monitoreo con 3 endpoints
- ✅ Sistema de registro de consultas en SQLite
- ✅ Gráficos interactivos con Chart.js
- ✅ Estadísticas en tiempo real
- ✅ Autenticación segura con Flask-Login
- ✅ Documentación completa

## 🤝 Soporte

Para reportar problemas o sugerir mejoras, contacta al equipo de desarrollo.

---

**VerIP v3.5** - Sistema Profesional de Verificación de Reputación de IPs
