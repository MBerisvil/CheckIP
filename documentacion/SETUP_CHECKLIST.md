# 📋 Checklist: Configuración de Ambientes VerIP

## ✅ COMPLETADO
- [x] Workflows separados creados (deploy-develop.yml y deploy-production.yml)
- [x] Script de migración a Neon (migrate_to_neon.py)
- [x] Documentación completa (GITHUB_SECRETS_SETUP.md y NEON_MIGRATION.md)
- [x] Soporte para DATABASE_URL en app.py
- [x] Base de datos Neon Development configurada y migrada

## 🔲 PENDIENTE - Debes hacer estos pasos

### 1. Crear Segunda Base de Datos en Neon (Production)

```bash
# Ve a https://console.neon.tech
# Crea un NUEVO proyecto llamado "verip-production"
# O crea un branch "production" del proyecto existente
```

**Resultado esperado:**
- URL Development: `postgresql://...@ep-dev-xxx.neon.tech/verip_dev?sslmode=require`
- URL Production: `postgresql://...@ep-prod-yyy.neon.tech/verip_prod?sslmode=require`

### 2. Configurar GitHub Secrets

Ve a: https://github.com/MBerisvil/CheckIP/settings/secrets/actions

**Agrega estos 11 secrets:**

#### Compartidos (ambos ambientes):
```
VERCEL_TOKEN=xxx...
VERCEL_ORG_ID=team_xxx...
VERCEL_PROJECT_ID=prj_xxx...
SECRET_KEY=genera-una-clave-aleatoria-fuerte
ADMIN_USERNAME=Administrador
ADMIN_PASSWORD_HASH=pbkdf2:sha256:600000$...
ABUSEIPDB_API_KEY=076e1a0fe4d3a833...
```

#### Development:
```
DATABASE_URL_DEV=postgresql://...@ep-dev-xxx.neon.tech/verip_dev?sslmode=require
API_MONITOR_KEY_DEV=dev-monitor-key-12345
```

#### Production:
```
DATABASE_URL_PROD=postgresql://...@ep-prod-yyy.neon.tech/verip_prod?sslmode=require
API_MONITOR_KEY_PROD=prod-monitor-key-secure-67890
```

### 3. Generar SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copia el resultado y úsalo en GitHub Secrets
```

### 4. Migrar Datos a Production DB

```bash
# Actualiza .env con la URL de producción temporalmente
DATABASE_URL=postgresql://...@ep-prod-yyy.neon.tech/verip_prod?sslmode=require

# Ejecuta migración
python migrate_to_neon.py

# Restaura .env a la URL de development
```

### 5. Probar Deployment Manual

```bash
# Ve a: https://github.com/MBerisvil/CheckIP/actions
# Selecciona: "Deploy to Development"
# Click: "Run workflow" en rama develop
# Verifica que se despliegue correctamente
```

### 6. Configurar Vercel (Opcional pero Recomendado)

1. Ve a tu proyecto en Vercel Dashboard
2. Settings → Environment Variables
3. Agrega las variables para cada ambiente:
   - **Production Branch:** main
   - **Preview Branch:** develop

## 🎯 URLs Finales

- **Development:** https://verip-dev.vercel.app (o tu dominio preview)
- **Production:** https://verificar-ip.vercel.app

## 🔄 Flujo de Trabajo

### Desarrollo:
```bash
git checkout develop
# Hacer cambios
git add .
git commit -m "feat: nueva funcionalidad"
git push origin develop
# → Auto-deploy a Development con DATABASE_URL_DEV
```

### Producción:
```bash
git checkout main
git merge develop
git push origin main
# → Auto-deploy a Production con DATABASE_URL_PROD
```

## ✅ Verificación Final

- [ ] Ambas bases de datos creadas en Neon
- [ ] 11 secrets configurados en GitHub
- [ ] Deploy manual de develop exitoso
- [ ] Dashboard funciona en ambos ambientes
- [ ] API de monitoreo responde correctamente
- [ ] No hay errores en logs de Vercel

## 📝 Notas Importantes

1. **NUNCA** uses la misma DB para dev y prod
2. **SIEMPRE** prueba en develop antes de mergear a main
3. Mantén los secrets sincronizados entre GitHub y Vercel
4. Revisa logs de deployment en Actions si algo falla
5. Los datos migrados a production son independientes de development

---

**Siguiente paso:** Ir a https://github.com/MBerisvil/CheckIP/settings/secrets/actions
