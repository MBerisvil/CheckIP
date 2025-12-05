# 🔐 Configuración de GitHub Secrets para VerIP

Esta guía te ayudará a configurar correctamente los secrets de GitHub para los ambientes de **Development** y **Production**.

## 📋 Lista de Secrets Necesarios

### 🔑 Secrets Compartidos (ambos ambientes)
| Secret Name | Descripción | Ejemplo |
|------------|-------------|---------|
| `VERCEL_TOKEN` | Token de autenticación de Vercel | `xxx...` |
| `VERCEL_ORG_ID` | ID de tu organización en Vercel | `team_xxx...` |
| `VERCEL_PROJECT_ID` | ID del proyecto en Vercel | `prj_xxx...` |
| `SECRET_KEY` | Clave secreta de Flask (genera una fuerte) | `tu-clave-super-secreta-123` |
| `ADMIN_USERNAME` | Usuario administrador | `Administrador` |
| `ADMIN_PASSWORD_HASH` | Hash de contraseña (usa `generate_password_hash.py`) | `pbkdf2:sha256:...` |
| `ABUSEIPDB_API_KEY` | API Key de AbuseIPDB | `076e1a0fe4d3a833...` |

### 🟢 Secrets para DEVELOPMENT
| Secret Name | Descripción | Valor |
|------------|-------------|-------|
| `DATABASE_URL_DEV` | Conexión a base de datos Neon Development | `postgresql://user:pass@ep-dev-xxx.neon.tech/verip_dev?sslmode=require` |
| `API_MONITOR_KEY_DEV` | API key de monitoreo para desarrollo | `dev-monitor-key-12345` |

### 🔴 Secrets para PRODUCTION
| Secret Name | Descripción | Valor |
|------------|-------------|-------|
| `DATABASE_URL_PROD` | Conexión a base de datos Neon Production | `postgresql://user:pass@ep-prod-yyy.neon.tech/verip_prod?sslmode=require` |
| `API_MONITOR_KEY_PROD` | API key de monitoreo para producción | `prod-monitor-key-67890` |

---

## 🚀 Paso a Paso: Configurar Secrets en GitHub

### 1️⃣ Ir a Settings del Repositorio

1. Ve a tu repositorio: https://github.com/MBerisvil/CheckIP
2. Click en **Settings** (última pestaña)
3. En el menú lateral, click en **Secrets and variables** → **Actions**

### 2️⃣ Agregar Secrets Compartidos

Haz click en **New repository secret** para cada uno:

```bash
# Secrets de Vercel (obtén estos valores de Vercel Dashboard)
VERCEL_TOKEN=xxx...
VERCEL_ORG_ID=team_xxx...
VERCEL_PROJECT_ID=prj_xxx...

# Flask y Admin
SECRET_KEY=cambia-esto-por-algo-muy-aleatorio-y-largo-123456789
ADMIN_USERNAME=Administrador
ADMIN_PASSWORD_HASH=pbkdf2:sha256:600000$lNQuJyMVbEgUliQw$021118a45c34f502425e1f8e7f31423a7fc5e2ab40001c24c7e8ecf205531776

# AbuseIPDB
ABUSEIPDB_API_KEY=076e1a0fe4d3a833506a3924c643bf1ee0fbb35a9d8870f71666bcc7c71a9ad10a371a7dcf8303e5
```

### 3️⃣ Agregar Secrets de Base de Datos

**Para Development:**
```bash
DATABASE_URL_DEV=postgresql://neondb_owner:npg_x72elpPfkcHM@ep-solitary-salad-a8pma39k-pooler.eastus2.azure.neon.tech/verip_dev?sslmode=require
API_MONITOR_KEY_DEV=dev-monitor-api-key-change-in-production
```

**Para Production:**
```bash
# Crea una segunda base de datos en Neon para producción
DATABASE_URL_PROD=postgresql://user:pass@ep-prod-xxxx.neon.tech/verip_prod?sslmode=require
API_MONITOR_KEY_PROD=prod-monitor-api-key-secure-random-string
```

---

## 🗄️ Configuración de Bases de Datos en Neon

### Opción 1: Dos Proyectos Separados (Recomendado)

1. **Proyecto Development:**
   - Nombre: `verip-development`
   - Database: `verip_dev`
   - Región: La más cercana a ti
   - Plan: Free (suficiente para desarrollo)

2. **Proyecto Production:**
   - Nombre: `verip-production`
   - Database: `verip_prod`
   - Región: La más cercana a tus usuarios
   - Plan: Free o Scale (según tráfico)

### Opción 2: Un Proyecto con Branches (Más elegante)

Neon permite crear "branches" de bases de datos como Git:

1. **Base principal (Production):**
   - Branch: `main`
   - Database: `verip_prod`

2. **Branch de desarrollo:**
   - Branch: `develop`
   - Database: Copia de producción para testing
   - Se actualiza automáticamente

**Comando para crear branch:**
```bash
neon branches create --name develop --parent main
```

---

## 🔧 Generar SECRET_KEY y Password Hash

### Generar SECRET_KEY fuerte:
```python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Generar ADMIN_PASSWORD_HASH:
```bash
python generate_password_hash.py
# Ingresa tu contraseña cuando te lo pida
# Copia el hash resultante
```

---

## ✅ Verificar Configuración

### 1. Verificar que tienes todos los secrets:
```bash
# Ve a: Settings → Secrets and variables → Actions
# Deberías ver 11 secrets en total
```

### 2. Probar deployment manual:
```bash
# Ve a: Actions → Deploy to Development → Run workflow
# Selecciona rama: develop
# Click: Run workflow
```

### 3. Revisar logs:
```bash
# Si falla, revisa los logs en la pestaña Actions
# Busca errores relacionados con secrets faltantes
```

---

## 🌍 Variables de Entorno en Vercel (Alternativa)

Si prefieres, también puedes configurar las variables directamente en Vercel:

1. Ve a tu proyecto en Vercel Dashboard
2. Settings → Environment Variables
3. Configura para cada environment:
   - **Production** (main branch)
   - **Preview** (develop branch)

**Ventaja:** Más fácil de gestionar
**Desventaja:** GitHub Actions no tendrá acceso directo

---

## 🔄 Flujo de Trabajo

### Para Desarrollo (rama develop):
1. Push a `develop` → Auto-deploy a Development
2. URL: `https://verip-dev.vercel.app`
3. Base de datos: `DATABASE_URL_DEV`

### Para Producción (rama main):
1. Merge de `develop` a `main` → Auto-deploy a Production
2. URL: `https://verificar-ip.vercel.app`
3. Base de datos: `DATABASE_URL_PROD`
4. Incluye modo mantenimiento

### Deploy Manual:
```bash
# Development
Actions → Deploy to Development → Run workflow

# Production  
Actions → Deploy to Production → Run workflow
```

---

## 🆘 Solución de Problemas

### Error: "Secret DATABASE_URL_DEV not found"
- Verifica que el secret exista en GitHub
- Revisa que el nombre sea exactamente `DATABASE_URL_DEV`
- Los nombres son case-sensitive

### Error: "connection refused" en Neon
- Verifica que la URL incluya `?sslmode=require`
- Confirma que la IP esté permitida en Neon (por defecto permite todas)
- Prueba la conexión localmente primero

### Workflows no se ejecutan
- Verifica que los archivos estén en `.github/workflows/`
- Nombres de archivo correctos: `deploy-develop.yml` y `deploy-production.yml`
- Los workflows deben estar en la rama correspondiente

---

## 📝 Checklist Final

- [ ] Todos los secrets configurados en GitHub
- [ ] Dos bases de datos creadas en Neon (dev y prod)
- [ ] Workflows en `.github/workflows/` committeados
- [ ] Test manual de deploy a development exitoso
- [ ] Verificar que la app funciona con ambas DBs
- [ ] Configurar alertas en Vercel (opcional)
- [ ] Documentar URLs de ambos ambientes

---

**¡Listo!** Ahora tienes un pipeline CI/CD profesional con ambientes separados. 🚀
