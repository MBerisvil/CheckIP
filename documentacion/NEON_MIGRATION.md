# 🚀 Guía de Migración a Neon PostgreSQL

Esta guía te ayudará a migrar tu base de datos de SQLite local a Neon PostgreSQL para producción.

## 📋 Requisitos Previos

1. Una cuenta en [Neon](https://neon.tech)
2. Python 3.8 o superior
3. Dependencias instaladas: `pip install -r requirements.txt`

## 🔧 Paso 1: Crear Base de Datos en Neon

1. Ve a [console.neon.tech](https://console.neon.tech)
2. Crea un nuevo proyecto llamado `verip` o similar
3. Copia la **Connection String** que se ve así:
   ```
   postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/verip?sslmode=require
   ```

## 📝 Paso 2: Configurar Variables de Entorno

Agrega la URL de conexión a tu archivo `.env`:

```bash
# Base de datos Neon PostgreSQL
DATABASE_URL=postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/verip?sslmode=require
```

**Importante:** 
- Reemplaza `user`, `password` y `ep-xxxxx` con tus credenciales de Neon
- La URL debe incluir `?sslmode=require` al final
- Neon proporciona esta URL completa en el dashboard

## 🔄 Paso 3: Ejecutar Script de Migración

El script `migrate_to_neon.py` hará automáticamente:
- ✅ Crear las tablas en Neon
- ✅ Migrar todos los datos de SQLite a PostgreSQL
- ✅ Mantener los IDs y timestamps originales

Ejecuta:

```bash
python migrate_to_neon.py
```

**Salida esperada:**
```
============================================================
  🚀 Migración de SQLite a Neon PostgreSQL - VerIP v3.5
============================================================

🔄 Iniciando migración de datos a Neon PostgreSQL...
   Origen: instance/verip_stats.db
   Destino: postgresql://user:***@ep-xxxxx...

📋 Creando tablas en Neon...
✅ Tablas creadas exitosamente

📊 Migrando tabla query_logs...
✅ Migrados 150 registros de query_logs

📊 Migrando tabla system_status...
✅ Migrados 5 registros de system_status

✨ Migración completada exitosamente!
```

## ✅ Paso 4: Verificar la Migración

1. **Inicia la aplicación:**
   ```bash
   python app.py
   ```

2. **Accede al dashboard de administración:**
   - Ve a `http://localhost:5000/admin/login`
   - Inicia sesión con tus credenciales
   - Verifica que las estadísticas muestren los datos migrados

3. **Verifica la conexión en Neon:**
   - Ve al dashboard de Neon
   - Revisa la sección "Tables" para ver `query_logs` y `system_status`
   - Puedes ejecutar queries SQL directamente en el SQL Editor

## 🔍 Solución de Problemas

### Error: "could not connect to server"
- Verifica que tu IP esté permitida en Neon (por defecto, Neon permite todas las IPs)
- Revisa que la URL de conexión sea correcta
- Asegúrate de que incluya `?sslmode=require`

### Error: "relation already exists"
- Las tablas ya existen en Neon
- Puedes eliminarlas manualmente desde el SQL Editor de Neon:
  ```sql
  DROP TABLE IF EXISTS query_logs CASCADE;
  DROP TABLE IF EXISTS system_status CASCADE;
  ```
- Vuelve a ejecutar el script de migración

### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

## 🌐 Despliegue en Producción

Una vez migrado a Neon, tu aplicación está lista para producción:

### Vercel
```bash
vercel --prod
```

Asegúrate de configurar las variables de entorno en Vercel:
- `DATABASE_URL` - Tu connection string de Neon
- `SECRET_KEY` - Clave secreta de Flask
- `ADMIN_PASSWORD_HASH` - Hash de tu contraseña
- `API_MONITOR_KEY` - Clave de API de monitoreo
- `ABUSEIPDB_API_KEY` - Tu API key de AbuseIPDB

### Otras plataformas (Railway, Render, Fly.io)
Todas soportan PostgreSQL y variables de entorno. Configura `DATABASE_URL` y las demás variables.

## 💾 Backup de SQLite

Antes de migrar, puedes hacer backup de tu base de datos local:

```bash
cp instance/verip_stats.db instance/verip_stats_backup_$(date +%Y%m%d).db
```

## 🔄 Rollback (Volver a SQLite)

Si necesitas volver a SQLite temporalmente:

1. Comenta o elimina `DATABASE_URL` de tu `.env`
2. Reinicia la aplicación
3. La app volverá a usar `sqlite:///verip_stats.db` por defecto

## 📊 Ventajas de Neon

- ✅ **Escalabilidad automática**: Se adapta a tu tráfico
- ✅ **Backups automáticos**: Point-in-time recovery
- ✅ **Branches**: Crea copias de tu DB para testing
- ✅ **Gratis para empezar**: Plan generoso sin tarjeta de crédito
- ✅ **Compatible con PostgreSQL**: Puedes usar todas las features de Postgres

## 🆘 Soporte

Si encuentras problemas durante la migración:

1. Revisa los logs del script de migración
2. Verifica la conexión a Neon en su dashboard
3. Consulta la documentación de [Neon](https://neon.tech/docs)

---

**¡Listo!** Tu aplicación VerIP ahora está usando una base de datos PostgreSQL profesional en la nube. 🎉
