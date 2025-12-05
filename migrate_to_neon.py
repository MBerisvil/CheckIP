#!/usr/bin/env python3
"""
Script de migración de SQLite a PostgreSQL (Neon)
Migra los datos existentes de verip_stats.db a la base de datos Neon
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

def migrate_data():
    """Migrar datos de SQLite a PostgreSQL Neon"""
    
    # Verificar que exista DATABASE_URL en .env
    neon_url = os.getenv('DATABASE_URL')
    if not neon_url or 'postgresql' not in neon_url:
        print("❌ Error: No se encontró DATABASE_URL de PostgreSQL en el archivo .env")
        print("   Configura tu conexión a Neon en .env:")
        print("   DATABASE_URL=postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/verip?sslmode=require")
        return False
    
    # Verificar que exista la base de datos SQLite
    sqlite_path = 'instance/verip_stats.db'
    if not os.path.exists(sqlite_path):
        print("⚠️  No se encontró base de datos SQLite en instance/verip_stats.db")
        print("   No hay datos para migrar. Las tablas se crearán vacías en Neon.")
        return True
    
    print("🔄 Iniciando migración de datos a Neon PostgreSQL...")
    print(f"   Origen: {sqlite_path}")
    print(f"   Destino: {neon_url[:50]}...")
    
    try:
        # Conectar a SQLite
        sqlite_engine = create_engine(f'sqlite:///{sqlite_path}')
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        sqlite_session = SQLiteSession()
        
        # Conectar a PostgreSQL Neon
        neon_engine = create_engine(neon_url)
        NeonSession = sessionmaker(bind=neon_engine)
        neon_session = NeonSession()
        
        # Crear tablas en Neon (usando SQLAlchemy directamente)
        print("\n📋 Creando tablas en Neon...")
        
        # Importar modelos
        from app import QueryLog, SystemStatus
        
        # Crear tablas directamente con el engine de Neon
        QueryLog.metadata.create_all(neon_engine)
        SystemStatus.metadata.create_all(neon_engine)
        print("✅ Tablas creadas exitosamente")
        
        # Migrar query_logs
        print("\n📊 Migrando tabla query_logs...")
        query_logs = sqlite_session.execute(text("SELECT * FROM query_logs")).fetchall()
        
        if query_logs:
            columns = ['id', 'ip_address', 'timestamp', 'abuse_confidence', 'total_reports', 
                      'is_whitelisted', 'country_code', 'usage_type', 'trust_score', 
                      'execution_time', 'api_used']
            
            for row in query_logs:
                # Convertir valores a diccionario y ajustar tipos para PostgreSQL
                row_dict = {col: val for col, val in zip(columns, row)}
                
                # Convertir booleanos (SQLite guarda como 0/1, PostgreSQL necesita bool)
                row_dict['is_whitelisted'] = bool(row_dict['is_whitelisted'])
                row_dict['api_used'] = bool(row_dict['api_used'])
                
                neon_session.execute(
                    text("""
                        INSERT INTO query_logs 
                        (id, ip_address, timestamp, abuse_confidence, total_reports, 
                         is_whitelisted, country_code, usage_type, trust_score, 
                         execution_time, api_used)
                        VALUES 
                        (:id, :ip_address, :timestamp, :abuse_confidence, :total_reports,
                         :is_whitelisted, :country_code, :usage_type, :trust_score,
                         :execution_time, :api_used)
                    """),
                    row_dict
                )
            
            neon_session.commit()
            print(f"✅ Migrados {len(query_logs)} registros de query_logs")
        else:
            print("   No hay datos en query_logs")
        
        # Migrar system_status
        print("\n📊 Migrando tabla system_status...")
        system_status = sqlite_session.execute(text("SELECT * FROM system_status")).fetchall()
        
        if system_status:
            columns = ['id', 'timestamp', 'status', 'response_time', 'error_count']
            
            for row in system_status:
                neon_session.execute(
                    text("""
                        INSERT INTO system_status 
                        (id, timestamp, status, response_time, error_count)
                        VALUES 
                        (:id, :timestamp, :status, :response_time, :error_count)
                    """),
                    {col: val for col, val in zip(columns, row)}
                )
            
            neon_session.commit()
            print(f"✅ Migrados {len(system_status)} registros de system_status")
        else:
            print("   No hay datos en system_status")
        
        # Cerrar sesiones
        sqlite_session.close()
        neon_session.close()
        
        print("\n✨ Migración completada exitosamente!")
        print("\n📝 Próximos pasos:")
        print("   1. Verifica que DATABASE_URL esté configurado en tu .env")
        print("   2. Reinicia la aplicación: python app.py")
        print("   3. La app ahora usará la base de datos Neon")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("  🚀 Migración de SQLite a Neon PostgreSQL - VerIP v3.5")
    print("=" * 60)
    print()
    
    success = migrate_data()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
