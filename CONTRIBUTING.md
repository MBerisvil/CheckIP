# Guía de Contribución y Flujo de Trabajo Git

## 📋 Índice
- [Estructura de Ramas](#estructura-de-ramas)
- [Flujo de Trabajo](#flujo-de-trabajo)
- [Comandos Útiles](#comandos-útiles)
- [Reglas de Protección](#reglas-de-protección)
- [Despliegue](#despliegue)
- [Versionado](#versionado)

## 🌿 Estructura de Ramas

### `main` (Producción)
- Rama protegida que representa el código en producción
- **NUNCA** trabajes directamente en esta rama
- Solo se actualiza mediante Pull Requests aprobados
- Cada commit debe estar etiquetado con una versión

### `develop` (Desarrollo)
- Rama de integración para desarrollo activo
- Base para crear nuevas ramas de features
- Se fusiona a `main` cuando está lista para producción

### `feature/*` (Funcionalidades)
- Para nuevas características: `feature/nombre-funcionalidad`
- Se crean desde `develop`
- Se fusionan de vuelta a `develop`

### `hotfix/*` (Correcciones Urgentes)
- Para correcciones críticas en producción
- Se crean desde `main`
- Se fusionan tanto a `main` como a `develop`

### `bugfix/*` (Correcciones)
- Para correcciones de bugs no críticos
- Se crean desde `develop`
- Se fusionan de vuelta a `develop`

## 🔄 Flujo de Trabajo

### 1. Iniciar una nueva funcionalidad

```bash
# Asegúrate de estar en develop y actualizado
git checkout develop
git pull origin develop

# Crea una nueva rama
git checkout -b feature/nombre-funcionalidad

# Trabaja en tu código...
git add .
git commit -m "feat: descripción de la funcionalidad"

# Sube tu rama al repositorio
git push -u origin feature/nombre-funcionalidad
```

### 2. Crear un Pull Request

1. Ve a GitHub: https://github.com/MBerisvil/CheckIP/pulls
2. Click en "New Pull Request"
3. Selecciona:
   - Base: `develop`
   - Compare: `feature/nombre-funcionalidad`
4. Completa la descripción del PR
5. Espera las pruebas automáticas (CI)
6. Solicita revisión si es necesario
7. Fusiona cuando esté aprobado

### 3. Preparar release a producción

```bash
# Cuando develop esté listo para producción
git checkout main
git pull origin main

# Crea un PR desde develop hacia main
# O fusiona localmente (no recomendado)
git merge develop
git push origin main

# Etiqueta la versión
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 4. Hotfix urgente

```bash
# Crea rama desde main
git checkout main
git pull origin main
git checkout -b hotfix/descripcion-problema

# Aplica la corrección
git add .
git commit -m "fix: corrección urgente"
git push -u origin hotfix/descripcion-problema

# Crea PR hacia main
# Después del merge, también fusionar a develop
git checkout develop
git merge main
git push origin develop
```

## 🛠️ Comandos Útiles

### Ver estado de ramas
```bash
git branch -a                    # Listar todas las ramas
git status                       # Ver estado actual
git log --oneline --graph --all  # Ver historial visual
```

### Actualizar tu rama con cambios recientes
```bash
git checkout develop
git pull origin develop
git checkout tu-rama-feature
git merge develop
# O usa rebase para un historial más limpio
git rebase develop
```

### Limpiar ramas locales obsoletas
```bash
git fetch --prune
git branch -d nombre-rama-local  # Solo si ya está fusionada
git branch -D nombre-rama-local  # Forzar eliminación
```

### Deshacer cambios
```bash
git restore archivo.py           # Descartar cambios no confirmados
git reset HEAD~1                 # Deshacer último commit (mantener cambios)
git reset --hard HEAD~1          # Deshacer último commit (eliminar cambios)
```

## 🔒 Reglas de Protección

Para configurar en GitHub:

1. Ve a: **Settings** → **Branches** → **Add rule**
2. Aplica a: `main`
3. Activa:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (mínimo 1 si trabajas en equipo)
   - ✅ Require status checks to pass (CI/CD)
   - ✅ Require conversation resolution before merging
   - ✅ Do not allow bypassing the above settings

4. También protege `develop` con reglas similares

## 🚀 Despliegue

### Despliegue Manual a Producción

El despliegue a producción se hace **manualmente** desde GitHub Actions:

1. Ve a: **Actions** → **CI/CD Pipeline**
2. Click en "Run workflow"
3. Selecciona:
   - Branch: `main`
   - Environment: `production`
4. Click "Run workflow"

### Despliegue a Staging (opcional)

Para probar antes de producción:

1. Ve a: **Actions** → **CI/CD Pipeline**
2. Click en "Run workflow"
3. Selecciona:
   - Branch: `develop`
   - Environment: `staging`

### Configurar Secrets en GitHub

Para que funcione el despliegue automático a Vercel:

1. Ve a: **Settings** → **Secrets and variables** → **Actions**
2. Agrega los siguientes secrets:
   - `VERCEL_TOKEN`: Tu token de Vercel
   - `VERCEL_ORG_ID`: ID de tu organización en Vercel
   - `VERCEL_PROJECT_ID`: ID del proyecto en Vercel

Para obtener estos valores:
```bash
# Instala Vercel CLI
npm i -g vercel

# Login y obtén los valores
vercel login
vercel link
# Los valores están en .vercel/project.json
```

## 🏷️ Versionado

Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR** (v1.0.0 → v2.0.0): Cambios incompatibles
- **MINOR** (v1.0.0 → v1.1.0): Nueva funcionalidad compatible
- **PATCH** (v1.0.0 → v1.0.1): Corrección de bugs

### Crear una nueva versión

```bash
# Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# Crea y sube el tag
git tag -a v1.2.0 -m "Release v1.2.0: Descripción de cambios"
git push origin v1.2.0

# También puedes crear releases en GitHub con notas de cambios
```

## 📝 Convención de Commits

Usa prefijos descriptivos:

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Documentación
- `style:` Formato, punto y coma faltantes, etc.
- `refactor:` Refactorización de código
- `test:` Agregar tests
- `chore:` Tareas de mantenimiento

Ejemplos:
```bash
git commit -m "feat: agregar validación de email"
git commit -m "fix: corregir error en verificación de IP"
git commit -m "docs: actualizar README con nuevas instrucciones"
```

## ⚠️ Importante

- ❌ **NUNCA** hagas `git push --force` en `main` o `develop`
- ❌ **NUNCA** trabajes directamente en `main`
- ✅ Siempre crea una rama para tus cambios
- ✅ Mantén los commits pequeños y descriptivos
- ✅ Prueba tu código antes de hacer push
- ✅ Actualiza tu rama con cambios recientes antes de crear PR

## 🆘 Ayuda

Si tienes problemas:

1. Verifica el estado: `git status`
2. Ver el log: `git log --oneline`
3. Si algo salió mal: `git reflog` (para recuperar commits)
4. Pide ayuda al equipo antes de forzar cambios

---

**Última actualización:** Diciembre 2025
