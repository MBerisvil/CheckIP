# VerIP v3.5

🔍 Sistema profesional de verificación de reputación de direcciones IP con panel de administración y API de monitoreo.

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📚 Documentación

Toda la documentación del proyecto se encuentra en la carpeta [`documentacion/`](./documentacion/):

- **[README.md](./documentacion/README.md)** - Documentación completa del proyecto
- **[QUICKSTART.md](./documentacion/QUICKSTART.md)** - Guía de inicio rápido
- **[ADMIN_PANEL_GUIDE.md](./documentacion/ADMIN_PANEL_GUIDE.md)** - Guía del panel de administrador
- **[API_DOCUMENTATION.md](./documentacion/API_DOCUMENTATION.md)** - Documentación de la API de monitoreo
- **[CONTRIBUTING.md](./documentacion/CONTRIBUTING.md)** - Guía de contribución
- **[SETUP_SUMMARY.md](./documentacion/SETUP_SUMMARY.md)** - Resumen de configuración

## ✨ Características Principales

- ✅ Verificación de IPs con AbuseIPDB API
- ✅ Verificación en 21+ blacklists DNS
- ✅ Panel de administrador con estadísticas
- ✅ API REST para monitoreo externo
- ✅ Gráficos interactivos con Chart.js
- ✅ Base de datos SQLite con registro de consultas
- ✅ Diseño responsive y moderno

## 🔑 Acceso al Panel de Administrador

1. Navega a la página principal
2. Haz clic en el icono de configuración (⚙️) en el footer
3. Usa las credenciales configuradas en `.env`

## 🛠️ Configuración

Copia `.env.example` a `.env` y configura:

```bash
ABUSEIPDB_API_KEY=tu-api-key-aqui
ADMIN_USERNAME=tu-usuario
ADMIN_PASSWORD=tu-contraseña-segura
API_MONITOR_KEY=tu-clave-api-monitoreo
```

## 📊 API de Monitoreo

Endpoints disponibles con autenticación por API key:

- `GET /api/status` - Estado del sistema
- `GET /api/stats` - Estadísticas detalladas
- `GET /api/recent` - Consultas recientes

Ver [API_DOCUMENTATION.md](./documentacion/API_DOCUMENTATION.md) para más detalles.

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.

## 👨‍💻 Autor

**MBerisvil** - [GitHub](https://github.com/MBerisvil)

---

Para más información detallada, consulta la [documentación completa](./documentacion/).
