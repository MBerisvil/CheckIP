

**Ver-IP v3.5** es una aplicación web profesional que permite verificar la reputación de direcciones IP usando AbuseIPDB API, mostrando información técnica detallada sobre conexiones, geolocalización, y estadísticas de seguridad.

## 🌐 Sitio en producción

[https://ver-ip.vercel.app](https://ver-ip.vercel.app)

---

## ✨ Nuevas Funcionalidades v3.5

### 🔐 Panel de Administrador
- Sistema de autenticación seguro con Flask-Login
- Dashboard completo con estadísticas en tiempo real
- Visualización de consultas y métricas
- Gráficos interactivos con Chart.js

### 📡 API de Monitoreo
- 3 endpoints REST para monitoreo externo
- Autenticación con API Key
- Consulta de estado del servicio
- Estadísticas detalladas por período
- Historial de consultas recientes

### 📊 Sistema de Registro
- Base de datos SQLite para almacenar consultas
- Tracking de todas las verificaciones de IP
- Estadísticas de uso de AbuseIPDB API
- Análisis de tendencias y patrones

### 📈 Gráficos y Visualización
- Consultas por día (últimos 7 días)
- Distribución por países
- Métricas de AbuseIPDB API
- IPs más consultadas

---

## 📋 Funcionalidades principales

- ✅ Verificación de reputación de IPs con AbuseIPDB
- ✅ Visualización de dirección IP pública
- ✅ Información del proveedor de servicios
- ✅ Ubicación geográfica aproximada
- ✅ Datos del navegador y sistema operativo
- ✅ Panel de administrador con estadísticas
- ✅ API REST para monitoreo externo
- ✅ Gráficos interactivos de consultas
- ✅ Base de datos de historial

---

## 🚀 Documentación Completa

- 📖 [Guía del Panel de Administrador](ADMIN_PANEL_GUIDE.md)
- 📡 [Documentación de la API de Monitoreo](API_DOCUMENTATION.md)
- 🤝 [Guía de Contribución](CONTRIBUTING.md)

---

## 🔧 Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/MBerisvil/CheckIP.git
cd CheckIP
```

### 2. Crear entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Edita .env con tus valores
```

### 5. Ejecutar la aplicación
```bash
python app.py
```

La aplicación estará disponible en:
- **Web principal**: http://localhost:5000
- **Panel admin**: http://localhost:5000/admin/login

---

## 🔑 Configuración

### Variables de Entorno (.env)

```env
# API de AbuseIPDB (opcional)
ABUSEIPDB_API_KEY=tu-api-key-aqui

# Seguridad de Flask
SECRET_KEY=clave-secreta-aleatoria

# Usuario administrador
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=hash-generado-con-werkzeug

# API de monitoreo
API_MONITOR_KEY=clave-para-api-externa
```

### Generar Hash de Contraseña

```bash
python generate_password_hash.py
```

---

## 📡 API de Monitoreo

### Endpoints Disponibles

```bash
# Estado del servicio
GET /api/status

# Estadísticas detalladas
GET /api/stats?period=7d

# Consultas recientes
GET /api/recent?limit=50
```

Todos los endpoints requieren el header:
```
X-API-Key: tu-api-key
```

### Ejemplo de Uso

```python
import requests

headers = {'X-API-Key': 'tu-api-key'}
response = requests.get('http://localhost:5000/api/status', headers=headers)
print(response.json())
```

Ver [API_DOCUMENTATION.md](API_DOCUMENTATION.md) para más detalles.

---

## 🛠️ Cómo contribuir

Por favor lee nuestra [Guía de Contribución](CONTRIBUTING.md) para conocer el flujo de trabajo completo.

**Flujo rápido:**

1. Fork del repositorio
2. Clona tu fork: `git clone https://github.com/TU-USUARIO/CheckIP.git`
3. Crea una rama desde `develop`: `git checkout -b feature/nueva-funcionalidad`
4. Realiza tus cambios y commits: `git commit -m 'feat: descripción'`
5. Push a tu fork: `git push origin feature/nueva-funcionalidad`
6. Abre un Pull Request hacia `develop`

**⚠️ Importante:** Nunca trabajes directamente en `main`. Todas las contribuciones deben ir a través de Pull Requests.

---
