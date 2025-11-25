#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnóstico rápido para verificar la configuración de email
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 70)
print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN DE EMAIL")
print("=" * 70)
print()

# Verificar archivo .env
env_exists = os.path.exists('.env')
print(f"📁 Archivo .env existe: {'✅ SÍ' if env_exists else '❌ NO'}")
print()

# Verificar variables
smtp_email = os.getenv('SMTP_EMAIL')
smtp_password = os.getenv('SMTP_PASSWORD')
smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = os.getenv('SMTP_PORT', '587')

print("📋 Variables de Entorno:")
print(f"   SMTP_SERVER: {smtp_server}")
print(f"   SMTP_PORT: {smtp_port}")
print(f"   SMTP_EMAIL: {smtp_email if smtp_email else '❌ NO CONFIGURADO'}")
print(f"   SMTP_PASSWORD: {'✅ Configurado' if smtp_password else '❌ NO CONFIGURADO'}")
print()

# Diagnóstico
problemas = []

if not env_exists:
    problemas.append("❌ No existe el archivo .env en la raíz del proyecto")
    print("💡 SOLUCIÓN: Crea un archivo .env con las siguientes variables:")
    print()
    print("   SMTP_EMAIL=tu_email@gmail.com")
    print("   SMTP_PASSWORD=tu_contraseña_de_aplicacion")
    print("   SMTP_SERVER=smtp.gmail.com")
    print("   SMTP_PORT=587")
    print()

if not smtp_email:
    problemas.append("❌ SMTP_EMAIL no está configurado")
    
if not smtp_password:
    problemas.append("❌ SMTP_PASSWORD no está configurado")

if problemas:
    print("=" * 70)
    print("⚠️ PROBLEMAS ENCONTRADOS:")
    print("=" * 70)
    for problema in problemas:
        print(f"   {problema}")
    print()
    print("=" * 70)
    print("📝 GUÍA RÁPIDA DE CONFIGURACIÓN:")
    print("=" * 70)
    print()
    print("1. Crea un archivo .env en la raíz del proyecto")
    print()
    print("2. Para Gmail, necesitas una 'Contraseña de Aplicación':")
    print("   a) Ve a: https://myaccount.google.com/")
    print("   b) Seguridad → Verificación en dos pasos (actívala si no está)")
    print("   c) Seguridad → Contraseñas de aplicaciones")
    print("   d) Genera una contraseña para 'Correo'")
    print()
    print("3. Agrega al archivo .env:")
    print("   SMTP_EMAIL=tu_email@gmail.com")
    print("   SMTP_PASSWORD=la_contraseña_de_16_caracteres")
    print("   SMTP_SERVER=smtp.gmail.com")
    print("   SMTP_PORT=587")
    print()
    print("4. Reinicia el servidor Flask")
    print()
else:
    print("=" * 70)
    print("✅ CONFIGURACIÓN CORRECTA")
    print("=" * 70)
    print()
    print("Las credenciales están configuradas. Si aún no recibes emails:")
    print()
    print("1. Verifica que la contraseña sea una 'Contraseña de Aplicación'")
    print("   (no tu contraseña normal de Gmail)")
    print()
    print("2. Revisa la carpeta de spam")
    print()
    print("3. Ejecuta el script de prueba:")
    print("   python test_email.py")
    print()
    print("4. Revisa los logs del servidor para ver errores específicos")
    print()

print("=" * 70)

