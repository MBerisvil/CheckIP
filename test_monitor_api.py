#!/usr/bin/env python3
"""
Script de ejemplo para consumir la API de monitoreo de VerIP
Requiere: requests (pip install requests)
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
API_KEY = "monitor-api-key-change-in-production"  # Cambiar por tu API key

def test_api_status():
    """Prueba el endpoint de estado"""
    print("\n" + "="*60)
    print("🔍 Probando /api/status")
    print("="*60)
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(f"{BASE_URL}/api/status", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa:")
            print(f"   Estado: {data['status']}")
            print(f"   Versión: {data['version']}")
            print(f"   Total consultas: {data['total_queries']}")
            print(f"   Tiempo respuesta promedio: {data['avg_response_time']}s")
            print(f"   Base de datos: {data['database']}")
            print(f"   Última consulta: {data['last_query']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_api_stats(period="7d"):
    """Prueba el endpoint de estadísticas"""
    print("\n" + "="*60)
    print(f"📊 Probando /api/stats?period={period}")
    print("="*60)
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/stats",
            headers=headers,
            params={"period": period}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa:")
            print(f"   Período: {data['period']}")
            print(f"   Desde: {data['since']}")
            print("\n   Resumen:")
            print(f"   - Total consultas: {data['summary']['total_queries']}")
            print(f"   - Alto riesgo: {data['summary']['high_risk']}")
            print(f"   - Riesgo medio: {data['summary']['medium_risk']}")
            print(f"   - Bajo riesgo: {data['summary']['low_risk']}")
            print(f"   - Whitelisted: {data['summary']['whitelisted']}")
            
            if data['top_countries']:
                print("\n   Top 5 países:")
                for country, count in list(data['top_countries'].items())[:5]:
                    print(f"   - {country}: {count} consultas")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_api_recent(limit=10):
    """Prueba el endpoint de consultas recientes"""
    print("\n" + "="*60)
    print(f"📋 Probando /api/recent?limit={limit}")
    print("="*60)
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/recent",
            headers=headers,
            params={"limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa: {data['count']} consultas")
            
            for i, query in enumerate(data['queries'][:5], 1):
                print(f"\n   Consulta {i}:")
                print(f"   - IP: {query['ip']}")
                print(f"   - Timestamp: {query['timestamp']}")
                print(f"   - Confianza de abuso: {query['abuse_confidence']}%")
                print(f"   - Score de confianza: {query['trust_score']}")
                print(f"   - País: {query['country']}")
                print(f"   - Whitelisted: {'Sí' if query['is_whitelisted'] else 'No'}")
            
            if len(data['queries']) > 5:
                print(f"\n   ... y {len(data['queries']) - 5} consultas más")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_without_api_key():
    """Prueba sin API key para verificar seguridad"""
    print("\n" + "="*60)
    print("🔒 Probando seguridad (sin API key)")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        
        if response.status_code == 401:
            print("✅ Seguridad OK: Acceso denegado sin API key")
        else:
            print(f"⚠️  Advertencia: Código de respuesta inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def main():
    print("\n" + "="*60)
    print("🚀 Test de API de Monitoreo - VerIP v3.5")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    
    # Ejecutar todas las pruebas
    test_api_status()
    test_api_stats("7d")
    test_api_recent(10)
    test_without_api_key()
    
    print("\n" + "="*60)
    print("✅ Pruebas completadas")
    print("="*60)
    print("\nPara cambiar la configuración:")
    print("1. Edita las variables BASE_URL y API_KEY en este script")
    print("2. Asegúrate de que VerIP esté ejecutándose")
    print("3. Verifica que el API_KEY coincida con el del archivo .env")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Verificar que requests esté instalado
    try:
        import requests
    except ImportError:
        print("❌ Error: requests no está instalado")
        print("Instálalo con: pip install requests")
        exit(1)
    
    main()
