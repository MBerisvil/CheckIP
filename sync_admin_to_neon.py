#!/usr/bin/env python3
"""
Script para sincronizar usuario admin en bases de datos DEV y PROD
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash
from datetime import datetime

load_dotenv()

def sync_admin_user():
    """Sincronizar usuario admin en ambas bases de datos"""
    
    dev_url = os.getenv('DATABASE_URL_DEV')
    prod_url = os.getenv('DATABASE_URL_PROD')
    
    if not dev_url or not prod_url:
        print("❌ Error: DATABASE_URL_DEV y DATABASE_URL_PROD deben estar en .env")
        return
    
    print("=" * 60)
    print("  🔄 Sincronización de Usuario Administrador")
    print("=" * 60)
    print("\nIngresa los datos del usuario a sincronizar:\n")
    
    username = input("Nombre de usuario: ").strip()
    email = input("Email (opcional): ").strip() or None
    password = input("Contraseña: ")
    confirm_password = input("Confirma la contraseña: ")
    
    if password != confirm_password:
        print("\n❌ Las contraseñas no coinciden")
        return
    
    password_hash = generate_password_hash(password)
    created_at = datetime.utcnow()
    
    # Sincronizar en DEV
    print("\n🔄 Sincronizando con base de datos DEV...")
    try:
        engine_dev = create_engine(dev_url)
        with engine_dev.connect() as conn:
            # Verificar si existe la tabla users
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                );
            """))
            table_exists = result.fetchone()[0]
            
            if not table_exists:
                # Crear tabla users
                conn.execute(text("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        email VARCHAR(120),
                        is_admin BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    );
                """))
                conn.commit()
                print("  ✅ Tabla 'users' creada")
            
            # Insertar o actualizar usuario
            result = conn.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": username}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                conn.execute(
                    text("""
                        UPDATE users 
                        SET password_hash = :password_hash, email = :email
                        WHERE username = :username
                    """),
                    {
                        "password_hash": password_hash,
                        "email": email,
                        "username": username
                    }
                )
                print(f"  ✅ Usuario '{username}' actualizado en DEV")
            else:
                conn.execute(
                    text("""
                        INSERT INTO users (username, password_hash, email, is_admin, created_at)
                        VALUES (:username, :password_hash, :email, TRUE, :created_at)
                    """),
                    {
                        "username": username,
                        "password_hash": password_hash,
                        "email": email,
                        "created_at": created_at
                    }
                )
                print(f"  ✅ Usuario '{username}' creado en DEV")
            
            conn.commit()
    except Exception as e:
        print(f"  ❌ Error en DEV: {str(e)}")
        return
    
    # Sincronizar en PROD
    print("\n🔄 Sincronizando con base de datos PROD...")
    try:
        engine_prod = create_engine(prod_url)
        with engine_prod.connect() as conn:
            # Verificar si existe la tabla users
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                );
            """))
            table_exists = result.fetchone()[0]
            
            if not table_exists:
                # Crear tabla users
                conn.execute(text("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        email VARCHAR(120),
                        is_admin BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    );
                """))
                conn.commit()
                print("  ✅ Tabla 'users' creada")
            
            # Insertar o actualizar usuario
            result = conn.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": username}
            )
            existing_user = result.fetchone()
            
            if existing_user:
                conn.execute(
                    text("""
                        UPDATE users 
                        SET password_hash = :password_hash, email = :email
                        WHERE username = :username
                    """),
                    {
                        "password_hash": password_hash,
                        "email": email,
                        "username": username
                    }
                )
                print(f"  ✅ Usuario '{username}' actualizado en PROD")
            else:
                conn.execute(
                    text("""
                        INSERT INTO users (username, password_hash, email, is_admin, created_at)
                        VALUES (:username, :password_hash, :email, TRUE, :created_at)
                    """),
                    {
                        "username": username,
                        "password_hash": password_hash,
                        "email": email,
                        "created_at": created_at
                    }
                )
                print(f"  ✅ Usuario '{username}' creado en PROD")
            
            conn.commit()
    except Exception as e:
        print(f"  ❌ Error en PROD: {str(e)}")
        return
    
    print("\n" + "=" * 60)
    print("✅ Sincronización completada exitosamente!")
    print("=" * 60)
    print(f"\n👤 Usuario: {username}")
    print(f"📧 Email: {email or 'No especificado'}")
    print(f"🔐 Contraseña: {'*' * len(password)}")
    print(f"✅ Sincronizado en: DEV y PROD")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    sync_admin_user()
