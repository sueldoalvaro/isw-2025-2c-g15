"""
Script de prueba para enviar un email real usando el servicio EmailService.

ANTES DE EJECUTAR:
1. Lee INSTRUCCIONES_GMAIL.md para configurar tu App Password
2. Configura las variables en el archivo .env

Uso (desde la raíz de graded/6):
  - Git Bash:   python tools/manual-tests/enviar_email_real.py
  - PowerShell: python .\tools\manual-tests\enviar_email_real.py
"""

import os
from datetime import date
from dotenv import load_dotenv
from api.compra import Compra
from api.entrada import Entrada
from api.utils import TipoEntrada, MedioPago
from api.email_service import EmailService

# Cargar variables de entorno desde .env
load_dotenv()


def main():
    print("=" * 70)
    print("📧 PRUEBA DE ENVÍO DE EMAIL REAL")
    print("=" * 70)

    # Configuración del email
    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or not sender_password:
        print("\n⚠️  Variables de entorno no encontradas.")
        print("Puedes configurarlas temporalmente aquí para la prueba:")
        print()
        # sender_email = "tu_email@gmail.com"
        # sender_password = "tu_app_password_16_chars"
        if not sender_email or not sender_password:
            print("❌ ERROR: Debes configurar las credenciales.")
            print()
            print("Opciones:")
            print("1. Configura variables de entorno:")
            print('   $env:GMAIL_USER = "tu_email@gmail.com"')
            print('   $env:GMAIL_APP_PASSWORD = "tu_app_password"')
            print()
            print("2. O edita este archivo y descomenta las líneas de configuración")
            print()
            return

    # Email de destino
    destinatario = input("\n📬 Ingresa el email de destino (o Enter para usar el mismo): ").strip()
    if not destinatario:
        destinatario = sender_email

    print(f"\n✅ Configuración:")
    print(f"   Remitente: {sender_email}")
    print(f"   Destinatario: {destinatario}")
    print()

    # Crear una compra de prueba
    print("🎫 Creando compra de prueba...")
    entrada1 = Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR)
    entrada2 = Entrada(edad=8, tipo_pase=TipoEntrada.VIP)

    compra = Compra(
        fecha=date(2025, 12, 25),
        entradas=[entrada1, entrada2],
        medio_pago=MedioPago.TARJETA,
    )

    total = compra.calcular_total()
    print(f"   📊 Total de la compra: ${total:,.0f}")
    print(f"   📅 Fecha de visita: {compra.fecha.strftime('%d/%m/%Y')}")
    print(f"   🎟️  Entradas: {len(compra.entradas)}")
    print()

    # Enviar el email
    print("📧 Inicializando servicio de email...")
    email_service = EmailService(sender_email=sender_email, sender_password=sender_password)

    print("📤 Enviando email... (esto puede tardar unos segundos)")
    try:
        resultado = email_service.enviar_confirmacion(compra, destinatario)
        if resultado:
            print()
            print("=" * 70)
            print("✅ ¡EMAIL ENVIADO EXITOSAMENTE!")
            print("=" * 70)
            print()
            print(f"📬 Revisa tu bandeja de entrada: {destinatario}")
            print("   También revisa la carpeta de SPAM por si acaso")
        else:
            print("\n❌ ERROR: El envío no retornó True")
    except ValueError as e:
        print(f"\n❌ ERROR DE CONFIGURACIÓN: {e}")
        print("   Verifica que las credenciales sean correctas")
    except Exception as e:
        print(f"\n❌ ERROR AL ENVIAR EMAIL: {type(e).__name__}")
        print(f"   Detalles: {str(e)}")
        print()
        print("Posibles causas:")
        print("  • App Password incorrecta")
        print("  • Verificación en 2 pasos no activada")
        print("  • Sin conexión a Internet")
        print("  • Firewall bloqueando el puerto 587")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
