#!/usr/bin/env python3
"""
Script para generar hash de contraseña para el panel de administrador
Uso: python generate_password_hash.py
"""

from werkzeug.security import generate_password_hash
import getpass

def main():
    print("=" * 60)
    print("Generador de Hash de Contraseña - VerIP v3.5")
    print("=" * 60)
    print()
    
    # Solicitar contraseña
    while True:
        password = getpass.getpass("Ingresa la contraseña: ")
        confirm = getpass.getpass("Confirma la contraseña: ")
        
        if password != confirm:
            print("❌ Las contraseñas no coinciden. Intenta nuevamente.\n")
            continue
        
        if len(password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres.\n")
            continue
        
        break
    
    # Generar hash
    password_hash = generate_password_hash(password)
    
    print("\n" + "=" * 60)
    print("✅ Hash generado exitosamente!")
    print("=" * 60)
    print(f"\nHash de la contraseña:")
    print(f"{password_hash}")
    print("\nAgrega esta línea a tu archivo .env:")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print("\n" + "=" * 60)
    print("\n⚠️  IMPORTANTE: Guarda este hash de forma segura.")
    print("No podrás recuperar la contraseña original del hash.")
    print("=" * 60)

if __name__ == "__main__":
    main()
