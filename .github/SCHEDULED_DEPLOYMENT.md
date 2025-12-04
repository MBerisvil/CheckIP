# 🕐 Configuración de Despliegue Programado

## Configuración Actual

**Horario configurado:** Lunes a las 02:00 AM UTC  
**Equivalente en Argentina (UTC-3):** Domingo 11:00 PM  
**Rama desplegada:** `main` (producción)

## Cómo Cambiar el Horario

El despliegue programado se configura en `.github/workflows/ci-cd.yml` línea ~8:

```yaml
schedule:
  - cron: '0 2 * * 1'  # Formato: minuto hora día_mes mes día_semana
```

### Formato Cron

```
┌───────────── minuto (0 - 59)
│ ┌───────────── hora (0 - 23) en UTC
│ │ ┌───────────── día del mes (1 - 31)
│ │ │ ┌───────────── mes (1 - 12)
│ │ │ │ ┌───────────── día de la semana (0 - 6) (Domingo=0)
│ │ │ │ │
* * * * *
```

**⚠️ IMPORTANTE:** GitHub Actions usa **hora UTC**. Argentina está en UTC-3.

## Ejemplos de Configuración

### Despliegue Semanal

```yaml
# Todos los viernes a las 6:00 PM (hora Argentina)
- cron: '0 21 * * 5'  # Viernes 9:00 PM UTC

# Todos los lunes a las 3:00 AM (hora Argentina)
- cron: '0 6 * * 1'   # Lunes 6:00 AM UTC

# Todos los domingos a medianoche (hora Argentina)
- cron: '0 3 * * 0'   # Domingo 3:00 AM UTC
```

### Despliegue Diario

```yaml
# Todos los días a las 2:00 AM (hora Argentina)
- cron: '0 5 * * *'   # 5:00 AM UTC

# Todos los días a las 10:00 PM (hora Argentina)
- cron: '0 1 * * *'   # 1:00 AM UTC (día siguiente)
```

### Despliegue Mensual

```yaml
# Primer día de cada mes a las 12:00 AM (hora Argentina)
- cron: '0 3 1 * *'   # Día 1, 3:00 AM UTC

# Último viernes del mes a las 5:00 PM (hora Argentina)
# Nota: Cron no soporta "último viernes", usar día específico
- cron: '0 20 25-31 * 5'  # Viernes entre día 25-31, 8:00 PM UTC
```

### Múltiples Horarios

```yaml
schedule:
  # Lunes a las 2:00 AM
  - cron: '0 5 * * 1'
  # Viernes a las 6:00 PM
  - cron: '0 21 * * 5'
```

## Tabla de Conversión Horaria

Argentina (UTC-3) → UTC

| Hora Argentina | Hora UTC | Cron (hora) |
|---------------|----------|-------------|
| 12:00 AM      | 3:00 AM  | `0 3`       |
| 2:00 AM       | 5:00 AM  | `0 5`       |
| 6:00 AM       | 9:00 AM  | `0 9`       |
| 12:00 PM      | 3:00 PM  | `0 15`      |
| 6:00 PM       | 9:00 PM  | `0 21`      |
| 10:00 PM      | 1:00 AM* | `0 1`       |

*Día siguiente en UTC

## Días de la Semana

| Día       | Número | Ejemplo Cron        |
|-----------|--------|---------------------|
| Domingo   | 0      | `0 5 * * 0`        |
| Lunes     | 1      | `0 5 * * 1`        |
| Martes    | 2      | `0 5 * * 2`        |
| Miércoles | 3      | `0 5 * * 3`        |
| Jueves    | 4      | `0 5 * * 4`        |
| Viernes   | 5      | `0 5 * * 5`        |
| Sábado    | 6      | `0 5 * * 6`        |

## Herramientas Útiles

- **Generador Cron:** https://crontab.guru/
- **Convertidor de Zonas Horarias:** https://www.timeanddate.com/worldclock/converter.html

## Cómo Cambiar el Horario

### 1. Editar el Archivo

```bash
# Abre el archivo de workflow
nano .github/workflows/ci-cd.yml

# O con VS Code
code .github/workflows/ci-cd.yml
```

### 2. Modificar la Línea del Cron

Busca la sección `schedule:` (línea ~8) y cambia el valor:

```yaml
schedule:
  - cron: '0 21 * * 5'  # Cambia esto a tu horario deseado
```

### 3. Guardar y Subir los Cambios

```bash
git add .github/workflows/ci-cd.yml
git commit -m "chore: actualizar horario de despliegue programado"
git push origin develop

# Luego crear PR a main
```

## Deshabilitar Despliegue Programado

### Opción 1: Comentar el Schedule

```yaml
# schedule:
#   - cron: '0 2 * * 1'
```

### Opción 2: Deshabilitar el Workflow

1. Ve a: https://github.com/MBerisvil/CheckIP/actions
2. Selecciona "CI/CD Pipeline"
3. Click en "..." (menú)
4. Click en "Disable workflow"

## Verificar Próximo Despliegue

1. Ve a: https://github.com/MBerisvil/CheckIP/actions
2. Selecciona "CI/CD Pipeline"
3. En la parte superior derás un mensaje: "This workflow has a `schedule` trigger"
4. GitHub te mostrará cuándo se ejecutará el próximo despliegue

## Notas Importantes

- ⏰ **Hora UTC:** Recuerda siempre convertir a UTC
- 🕐 **Precisión:** GitHub Actions puede tener un retraso de 3-10 minutos
- 🌿 **Rama:** Siempre despliega desde `main`
- ✅ **Tests:** Se ejecutan antes del despliegue
- 🔒 **Protección:** El despliegue requiere que los tests pasen
- 📧 **Notificaciones:** GitHub te enviará un email si el despliegue falla

## Ejemplo Práctico

**Quiero desplegar todos los viernes a las 8:00 PM (hora Argentina):**

1. Hora Argentina: 8:00 PM (20:00)
2. Convertir a UTC: 20:00 + 3 horas = 23:00 UTC (11:00 PM)
3. Día: Viernes = 5
4. Cron: `0 23 * * 5`

```yaml
schedule:
  - cron: '0 23 * * 5'  # Viernes 11:00 PM UTC (8:00 PM Argentina)
```

## Logs y Monitoreo

Para ver el historial de despliegues programados:

1. Ve a: https://github.com/MBerisvil/CheckIP/actions
2. Filtra por "schedule" en el tipo de evento
3. Click en cualquier ejecución para ver los logs detallados

---

**Última actualización:** Diciembre 2025  
**Configuración actual:** Lunes 2:00 AM UTC (Domingo 11:00 PM Argentina)
