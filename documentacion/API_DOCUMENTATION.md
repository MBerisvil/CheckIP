# 🚀 API de Monitoreo - VerIP v3.5

Esta documentación describe cómo usar la API REST de monitoreo de VerIP.

## 🔑 Autenticación

Todas las peticiones a la API requieren autenticación mediante API Key en el header:

```
X-API-Key: tu-api-key-aqui
```

### Configurar API Key

1. Edita el archivo `.env`:
```env
API_MONITOR_KEY=tu-clave-secreta-personalizada
```

2. Reinicia la aplicación para aplicar los cambios.

## 📡 Endpoints Disponibles

### 1. Estado del Servicio

**GET** `/api/status`

Verifica el estado general del servicio y la base de datos.

**Headers:**
```
X-API-Key: tu-api-key
```

**Respuesta Exitosa (200):**
```json
{
  "status": "online",
  "timestamp": "2024-12-05T10:30:00.123456",
  "database": "connected",
  "total_queries": 1523,
  "last_query": "2024-12-05T10:29:45.678901",
  "avg_response_time": 0.523,
  "version": "3.5"
}
```

**Ejemplo cURL:**
```bash
curl -H "X-API-Key: monitor-api-key-change-in-production" \
     http://localhost:5000/api/status
```

**Ejemplo Python:**
```python
import requests

headers = {'X-API-Key': 'monitor-api-key-change-in-production'}
response = requests.get('http://localhost:5000/api/status', headers=headers)
print(response.json())
```

---

### 2. Estadísticas Detalladas

**GET** `/api/stats?period=7d`

Obtiene estadísticas detalladas del servicio en un período específico.

**Parámetros de Query:**
- `period` (opcional): Período de tiempo a consultar
  - `24h`: Últimas 24 horas
  - `7d`: Últimos 7 días (por defecto)
  - `30d`: Últimos 30 días

**Headers:**
```
X-API-Key: tu-api-key
```

**Respuesta Exitosa (200):**
```json
{
  "period": "7d",
  "since": "2024-11-28T10:30:00.123456",
  "summary": {
    "total_queries": 450,
    "high_risk": 23,
    "medium_risk": 67,
    "low_risk": 360,
    "whitelisted": 15
  },
  "daily_stats": {
    "2024-11-28": {
      "total": 65,
      "high_risk": 3,
      "api_used": 45
    },
    "2024-11-29": {
      "total": 72,
      "high_risk": 5,
      "api_used": 50
    }
  },
  "top_countries": {
    "US": 120,
    "DE": 85,
    "FR": 67,
    "UK": 54,
    "CA": 42
  }
}
```

**Ejemplo cURL:**
```bash
curl -H "X-API-Key: monitor-api-key-change-in-production" \
     "http://localhost:5000/api/stats?period=24h"
```

**Ejemplo Python:**
```python
import requests

headers = {'X-API-Key': 'monitor-api-key-change-in-production'}
params = {'period': '24h'}
response = requests.get(
    'http://localhost:5000/api/stats',
    headers=headers,
    params=params
)
print(response.json())
```

---

### 3. Consultas Recientes

**GET** `/api/recent?limit=50`

Obtiene las consultas más recientes realizadas al sistema.

**Parámetros de Query:**
- `limit` (opcional): Número de resultados a retornar (por defecto: 50)

**Headers:**
```
X-API-Key: tu-api-key
```

**Respuesta Exitosa (200):**
```json
{
  "count": 50,
  "queries": [
    {
      "ip": "8.8.8.8",
      "timestamp": "2024-12-05T10:29:45.123456",
      "abuse_confidence": 0,
      "trust_score": 95,
      "country": "US",
      "is_whitelisted": false
    },
    {
      "ip": "192.168.1.1",
      "timestamp": "2024-12-05T10:25:30.654321",
      "abuse_confidence": 85,
      "trust_score": 15,
      "country": "XX",
      "is_whitelisted": false
    }
  ]
}
```

**Ejemplo cURL:**
```bash
curl -H "X-API-Key: monitor-api-key-change-in-production" \
     "http://localhost:5000/api/recent?limit=10"
```

**Ejemplo Python:**
```python
import requests

headers = {'X-API-Key': 'monitor-api-key-change-in-production'}
params = {'limit': 10}
response = requests.get(
    'http://localhost:5000/api/recent',
    headers=headers,
    params=params
)

data = response.json()
print(f"Total consultas: {data['count']}")
for query in data['queries']:
    print(f"IP: {query['ip']} - Score: {query['trust_score']}")
```

---

## ❌ Códigos de Error

### 401 Unauthorized
La API key no fue proporcionada o es inválida.

**Respuesta:**
```json
{
  "error": "API key inválida o ausente"
}
```

**Solución:** Verifica que estés enviando el header `X-API-Key` con el valor correcto.

### 500 Internal Server Error
Error interno del servidor.

**Respuesta:**
```json
{
  "status": "error",
  "timestamp": "2024-12-05T10:30:00.123456",
  "error": "Descripción del error"
}
```

---

## 🔧 Ejemplos de Integración

### Script de Monitoreo Continuo (Python)

```python
import requests
import time
from datetime import datetime

API_URL = "http://localhost:5000/api/status"
API_KEY = "monitor-api-key-change-in-production"
CHECK_INTERVAL = 60  # segundos

def check_service_status():
    headers = {'X-API-Key': API_KEY}
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[{datetime.now()}] ✅ Servicio OK - "
                  f"Total consultas: {data['total_queries']}, "
                  f"Tiempo respuesta: {data['avg_response_time']}s")
            return True
        else:
            print(f"[{datetime.now()}] ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error de conexión: {e}")
        return False

def main():
    print("Iniciando monitoreo continuo de VerIP...")
    
    while True:
        check_service_status()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
```

### Dashboard en Node.js (Express)

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
const API_URL = 'http://localhost:5000';
const API_KEY = 'monitor-api-key-change-in-production';

// Middleware para obtener estadísticas
app.get('/dashboard', async (req, res) => {
  try {
    const [status, stats] = await Promise.all([
      axios.get(`${API_URL}/api/status`, {
        headers: { 'X-API-Key': API_KEY }
      }),
      axios.get(`${API_URL}/api/stats?period=7d`, {
        headers: { 'X-API-Key': API_KEY }
      })
    ]);
    
    res.json({
      status: status.data,
      stats: stats.data
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Dashboard escuchando en puerto 3000');
});
```

### Script Bash para Monitoreo

```bash
#!/bin/bash

API_URL="http://localhost:5000/api/status"
API_KEY="monitor-api-key-change-in-production"

# Hacer petición
response=$(curl -s -w "\n%{http_code}" \
  -H "X-API-Key: $API_KEY" \
  "$API_URL")

# Separar body y status code
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    echo "✅ Servicio OK"
    echo "$body" | jq '.'
else
    echo "❌ Error: HTTP $http_code"
    echo "$body"
fi
```

---

## 📊 Integración con Herramientas de Monitoreo

### Prometheus

Puedes crear un exportador para Prometheus:

```python
from prometheus_client import Gauge, start_http_server
import requests
import time

# Métricas
total_queries = Gauge('verip_total_queries', 'Total de consultas')
avg_response_time = Gauge('verip_avg_response_time', 'Tiempo respuesta promedio')
high_risk_count = Gauge('verip_high_risk', 'IPs de alto riesgo')

def collect_metrics():
    headers = {'X-API-Key': 'monitor-api-key-change-in-production'}
    
    # Status
    status = requests.get('http://localhost:5000/api/status', headers=headers).json()
    total_queries.set(status['total_queries'])
    avg_response_time.set(status['avg_response_time'])
    
    # Stats
    stats = requests.get('http://localhost:5000/api/stats?period=24h', headers=headers).json()
    high_risk_count.set(stats['summary']['high_risk'])

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        collect_metrics()
        time.sleep(30)
```

### Grafana

Usa el datasource de Prometheus o crea queries directas a la API.

### Uptime Kuma

Configura un monitor HTTP con:
- URL: `http://tu-servidor:5000/api/status`
- Headers: `X-API-Key: tu-api-key`
- Intervalo: 60 segundos

---

## 🔒 Seguridad

### Buenas Prácticas

1. **API Key segura**: Usa una clave aleatoria y compleja
   ```bash
   # Generar API key segura
   openssl rand -hex 32
   ```

2. **Variables de entorno**: Nunca hardcodees la API key
   ```python
   import os
   API_KEY = os.getenv('VERIP_API_KEY')
   ```

3. **HTTPS**: En producción, usa siempre HTTPS
   ```python
   API_URL = "https://tu-dominio.com/api/status"
   ```

4. **Rate limiting**: Implementa límites de peticiones

5. **Rotación de keys**: Cambia la API key periódicamente

---

## 🧪 Testing

Usa el script incluido `test_monitor_api.py`:

```bash
python test_monitor_api.py
```

Este script prueba:
- ✅ Endpoint de estado
- ✅ Endpoint de estadísticas
- ✅ Endpoint de consultas recientes
- ✅ Seguridad (sin API key)

---

## 📞 Soporte

Para reportar problemas con la API:
1. Verifica que la API key sea correcta
2. Confirma que el servicio esté ejecutándose
3. Revisa los logs del servidor
4. Contacta al equipo de desarrollo

---

**VerIP v3.5** - API de Monitoreo Profesional
