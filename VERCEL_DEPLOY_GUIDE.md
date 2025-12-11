# Guía de Despliegue en Vercel - VerIP v3.5

## 🚀 Solución al Error 500: FUNCTION_INVOCATION_FAILED

### Problemas Identificados y Solucionados

1. **Flask-Limiter incompatible con Vercel Serverless**
   - ✅ Detección automática de entorno Vercel
   - ✅ Desactivación de rate limiting en producción
   - ✅ Fallback a validación básica

2. **security_fixes.py causa errores en serverless**
   - ✅ Importación condicional basada en `VERCEL_ENV`
   - ✅ Modo compatibilidad para entorno serverless

3. **Variables de entorno faltantes**
   - ✅ Fallbacks seguros para SECRET_KEY y DATABASE_URL
   - ✅ Detección automática de entorno

## 📋 Pasos de Despliegue

### 1. Preparar el repositorio

```bash
# Asegurarte de que estás en develop
git status

# Añadir los nuevos archivos
git add vercel_app.py vercel.json .vercelignore requirements-vercel.txt

# Commit
git commit -m "fix: solucionar error 500 en Vercel - compatibilidad serverless"

# Push
git push origin develop
```

### 2. Configurar Variables de Entorno en Vercel

Ve a tu proyecto en Vercel Dashboard → Settings → Environment Variables y configura:

**Variables REQUERIDAS:**

```
ABUSEIPDB_API_KEY=076e1a0fe4d3a833506a3924c643bf1ee0fbb35a9d8870f71666bcc7c71a9ad10a371a7dcf8303e5
SECRET_KEY=dce6dd80f709473e6765f4a222044fc546b94b5c744a000eabc06fe96e6aa1eb
API_MONITOR_KEY=4AB3T9cvepd4IIvIqO-hjM72Qv6C1JsYXVvTEvCXtmFcfNG71v68YL_ZMkXvIATH
DATABASE_URL=postgresql://neondb_owner:npg_9djwtigQvFk1@ep-little-credit-a86yeguk-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require
ADMIN_USERNAME=Admin
ADMIN_PASSWORD=Admin94*!
```

**Variables OPCIONALES (auto-configuradas):**

```
VERCEL_ENV=1
DISABLE_RATE_LIMITING=1
```

### 3. Configurar Requirements para Vercel

**OPCIÓN A: Usar requirements-vercel.txt (Recomendado)**

En tu proyecto de Vercel, configura el build command:
```
cp requirements-vercel.txt requirements.txt
```

**OPCIÓN B: Renombrar manualmente**

```bash
# Backup del requirements actual
cp requirements.txt requirements-local.txt

# Usar requirements para Vercel
cp requirements-vercel.txt requirements.txt

# Commit
git add requirements.txt
git commit -m "chore: usar requirements para Vercel"
git push origin develop
```

### 4. Redesplegar en Vercel

**Desde el Dashboard:**
1. Ve a tu proyecto en Vercel
2. Pestaña "Deployments"
3. Click en "Redeploy" en el último deployment
4. Selecciona "Use existing Build Cache" → **NO** (deselecciona)
5. Click "Redeploy"

**Desde CLI:**
```bash
# Instalar Vercel CLI si no lo tienes
npm i -g vercel

# Login
vercel login

# Desplegar desde develop
vercel --prod
```

### 5. Verificar el Despliegue

Una vez desplegado, verifica:

1. **Endpoint de salud:**
   ```bash
   curl https://tu-app.vercel.app/health
   ```
   Debe retornar: `{"status": "ok"}`

2. **Página principal:**
   ```bash
   curl https://tu-app.vercel.app/
   ```
   Debe retornar HTML sin errores

3. **API de verificación:**
   ```bash
   curl -X POST https://tu-app.vercel.app/verify \
     -H "Content-Type: application/json" \
     -d '{"ip": "8.8.8.8"}'
   ```

### 6. Revisar Logs

Si aún hay errores:

1. Ve a Vercel Dashboard → Tu Proyecto → Deployments
2. Click en el deployment más reciente
3. Ve a "Functions" → Click en "vercel_app.py"
4. Revisa los logs para ver errores específicos

## 🔧 Diferencias entre Local y Vercel

### Características Desactivadas en Vercel:

- ❌ Flask-Limiter (rate limiting)
- ❌ Flask-Talisman (HTTPS enforcement - Vercel lo maneja)
- ❌ Flask-WTF CSRF (incompatible con serverless stateless)
- ❌ security_fixes.py (funciones avanzadas)
- ❌ Logging a archivo (sistema de archivos efímero)

### Características Activas en Vercel:

- ✅ Verificación de IPs (AbuseIPDB)
- ✅ Consulta de DNS Blacklists
- ✅ Dashboard de administración
- ✅ API endpoints
- ✅ Base de datos PostgreSQL (Neon)
- ✅ Autenticación de admin
- ✅ Validación básica de IPs

## 🐛 Troubleshooting

### Error: Module not found 'security_fixes'

**Solución:** Ya está manejado con try/except en app.py. Vercel ignora este módulo.

### Error: CSRF validation failed

**Solución:** CSRF está desactivado en Vercel (stateless). Usa API keys para proteger endpoints.

### Error: Database connection failed

**Solución:** Verifica que DATABASE_URL esté configurada en Vercel con la URL de Neon PROD.

### Error: Rate limit exceeded

**Solución:** Rate limiting está desactivado en Vercel. Considera usar Vercel Edge Config o Upstash Redis.

## 📊 Monitoreo

### Logs en Vercel

```bash
# Ver logs en tiempo real
vercel logs tu-app.vercel.app --follow

# Ver logs de una función específica
vercel logs tu-app.vercel.app --output=raw
```

### Metrics

Vercel automáticamente proporciona:
- Request rate
- Error rate
- Function duration
- Bandwidth usage

Accede en: Dashboard → Tu Proyecto → Analytics

## 🔐 Seguridad en Producción

Aunque algunas protecciones están desactivadas, Vercel proporciona:

- ✅ HTTPS automático
- ✅ DDoS protection
- ✅ Edge caching
- ✅ Automatic failover
- ✅ Security headers (configurable)

Para protección adicional:
1. Activa Vercel Firewall (plan Pro)
2. Usa Vercel Edge Config para rate limiting
3. Implementa API keys para endpoints sensibles
4. Monitorea con Vercel Analytics

## 🚦 Próximos Pasos

1. ✅ Verificar que el deployment funcione
2. ⏳ Configurar dominio personalizado
3. ⏳ Configurar alertas en Vercel
4. ⏳ Implementar rate limiting con Upstash Redis
5. ⏳ Agregar monitoreo con Sentry
6. ⏳ Configurar CI/CD con GitHub Actions

## 📞 Soporte

Si el error persiste:
1. Revisa los logs de Vercel
2. Verifica las variables de entorno
3. Prueba el deployment desde CLI con `vercel --debug`
4. Contacta soporte de Vercel con el deployment ID
