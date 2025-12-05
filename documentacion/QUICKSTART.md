# 🎯 Quick Start - VerIP v3.5

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ Instalar y Ejecutar

```bash
# Clonar (si aún no lo tienes)
git clone https://github.com/MBerisvil/CheckIP.git
cd CheckIP

# Ejecutar script de inicio automático
./start.sh
```

El script `start.sh` hará todo automáticamente:
- ✅ Activar entorno virtual
- ✅ Instalar dependencias
- ✅ Crear archivo .env
- ✅ Crear base de datos
- ✅ Iniciar aplicación

### 2️⃣ Acceder

**Web Principal:**
```
http://localhost:5000
```

**Panel de Administrador:**
```
http://localhost:5000/admin/login
Usuario: admin
Contraseña: admin123
```

**API de Monitoreo:**
```bash
curl -H "X-API-Key: monitor-api-key-change-in-production" \
     http://localhost:5000/api/status
```

---

## 📦 ¿Qué hay de nuevo en v3.5?

### 🔐 Panel de Administrador
- Dashboard con estadísticas en tiempo real
- Gráficos interactivos (Chart.js)
- IPs más consultadas
- Métricas de seguridad

### 📡 API de Monitoreo
- 3 endpoints REST
- Autenticación con API Key
- Estado del servicio
- Estadísticas detalladas

### 💾 Base de Datos
- SQLite integrado
- Registro de todas las consultas
- Historial completo
- Análisis de tendencias

---

## 🔧 Configuración Rápida

### Cambiar Contraseña de Admin

```bash
# Generar nuevo hash
python generate_password_hash.py

# Copiar el hash generado al archivo .env
# ADMIN_PASSWORD_HASH=pbkdf2:sha256:...
```

### Configurar API de AbuseIPDB (Opcional)

```bash
# Editar .env
ABUSEIPDB_API_KEY=tu-api-key-aqui
```

Sin API key, VerIP usa datos simulados realistas.

### Cambiar API Key de Monitoreo

```bash
# Editar .env
API_MONITOR_KEY=tu-nueva-api-key-segura
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [README.md](README.md) | Información general y características |
| [ADMIN_PANEL_GUIDE.md](ADMIN_PANEL_GUIDE.md) | Guía completa del panel de administrador |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Documentación detallada de la API |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Resumen técnico de implementación |

---

## 🧪 Probar la API

```bash
# Script de pruebas incluido
python test_monitor_api.py
```

Prueba automáticamente:
- ✅ Endpoint de estado
- ✅ Endpoint de estadísticas  
- ✅ Endpoint de consultas recientes
- ✅ Seguridad sin API key

---

## 🚀 Comandos Útiles

### Iniciar aplicación
```bash
./start.sh
# O manualmente:
source .venv/bin/activate
python app.py
```

### Generar contraseña
```bash
python generate_password_hash.py
```

### Probar API
```bash
python test_monitor_api.py
```

### Crear base de datos manualmente
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

---

## 🔑 Credenciales por Defecto

⚠️ **IMPORTANTE: Cambiar en producción**

| Servicio | Usuario | Contraseña/Key |
|----------|---------|----------------|
| Panel Admin | `admin` | `admin123` |
| API Monitoreo | - | `monitor-api-key-change-in-production` |

---

## 📊 Estructura de Archivos Principales

```
CheckIP/
├── app.py                      # Aplicación principal
├── requirements.txt            # Dependencias
├── start.sh                    # Script de inicio rápido ⭐
├── .env                        # Configuración (crear desde .env.example)
├── templates/
│   ├── index.html             # Página principal
│   ├── admin_login.html       # Login de admin
│   └── admin_dashboard.html   # Dashboard
├── instance/
│   └── verip_stats.db         # Base de datos SQLite
└── docs/
    ├── ADMIN_PANEL_GUIDE.md   # Guía del panel
    └── API_DOCUMENTATION.md   # Docs de API
```

---

## 🆘 Solución de Problemas

### Error: ModuleNotFoundError

```bash
# Instalar dependencias
source .venv/bin/activate
pip install -r requirements.txt
```

### Error: No se puede acceder al panel admin

- Verifica que uses las credenciales correctas: `admin` / `admin123`
- Revisa el archivo `.env` si cambiaste las credenciales

### Error: API retorna 401

- Verifica el header: `X-API-Key: monitor-api-key-change-in-production`
- Revisa el valor en `.env` si lo cambiaste

### La base de datos no se crea

```bash
# Crear manualmente
source .venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

---

## 🎓 Primeros Pasos Recomendados

1. **Inicia la aplicación** con `./start.sh`
2. **Verifica algunas IPs** en http://localhost:5000
3. **Accede al panel admin** en http://localhost:5000/admin/login
4. **Explora los gráficos** y estadísticas
5. **Prueba la API** con `python test_monitor_api.py`
6. **Lee la documentación** completa

---

## 🔐 Checklist de Seguridad

Antes de usar en producción:

- [ ] Cambiar contraseña de admin
- [ ] Cambiar SECRET_KEY de Flask
- [ ] Cambiar API_MONITOR_KEY
- [ ] Obtener API key de AbuseIPDB
- [ ] Configurar HTTPS
- [ ] Hacer backup de la base de datos
- [ ] Revisar logs regularmente

---

## 📞 Soporte

- 📖 Consulta la [documentación completa](README.md)
- 🐛 Reporta bugs en GitHub Issues
- 💬 Únete a las discusiones del proyecto

---

## 🎉 ¡Listo para Usar!

```bash
./start.sh
```

Abre tu navegador en **http://localhost:5000** y comienza a verificar IPs.

---

**VerIP v3.5** - Sistema Profesional de Verificación de IPs
Con Panel de Administrador y API de Monitoreo 🚀
