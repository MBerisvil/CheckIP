#!/usr/bin/env python3
"""
⚠️ OBSOLETO: Este script ya no es necesario

El sistema ahora usa una tabla de usuarios en la base de datos.
Para crear o actualizar usuarios admin, usa:
- init_admin_user.py (para desarrollo local)
- sync_admin_to_neon.py (para sincronizar con Neon DEV/PROD)

Las contraseñas se hashean automáticamente al crear el usuario.
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
