#!/usr/bin/env python3
"""
Script para inicializar el usuario administrador en la base de datos
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def init_admin():
    """Crear usuario administrador en la base de datos"""
    
    with app.app_context():
        # Crear todas las tablas si no existen
        db.create_all()
        
        # Verificar si ya existe un usuario admin
        admin_user = User.query.filter_by(username='Administrador').first()
        
        if admin_user:
            print("⚠️  El usuario 'Administrador' ya existe en la base de datos")
            respuesta = input("¿Deseas actualizar la contraseña? (s/n): ")
            
            if respuesta.lower() != 's':
                print("❌ Operación cancelada")
                return
            
            # Actualizar contraseña
            print("\n🔐 Actualización de contraseña del administrador")
            password = input("Nueva contraseña: ")
            confirm_password = input("Confirma la contraseña: ")
            
            if password != confirm_password:
                print("❌ Las contraseñas no coinciden")
                return
            
            admin_user.password_hash = generate_password_hash(password)
            db.session.commit()
            
            print("\n✅ Contraseña actualizada exitosamente!")
            
        else:
            # Crear nuevo usuario administrador
            print("=" * 60)
            print("  🚀 Inicialización de Usuario Administrador")
            print("=" * 60)
            print("\nCreando usuario administrador en la base de datos...")
            print("Ingresa los datos del administrador:\n")
            
            username = input("Nombre de usuario [Administrador]: ").strip() or "Administrador"
            email = input("Email (opcional): ").strip() or None
            
            password = input("Contraseña: ")
            confirm_password = input("Confirma la contraseña: ")
            
            if password != confirm_password:
                print("\n❌ Las contraseñas no coinciden. Intenta nuevamente.")
                return
            
            # Crear usuario
            admin_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                is_admin=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ Usuario administrador creado exitosamente!")
            print("=" * 60)
            print(f"\n👤 Usuario: {username}")
            print(f"📧 Email: {email or 'No especificado'}")
            print(f"🔐 Contraseña: {'*' * len(password)}")
            print(f"⚡ Permisos: Administrador")
            print(f"📅 Creado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print("\n" + "=" * 60)
            print("\n⚠️  IMPORTANTE: Guarda esta contraseña de forma segura.")
            print("No podrás recuperarla si la olvidas.\n")

if __name__ == '__main__':
    init_admin()
