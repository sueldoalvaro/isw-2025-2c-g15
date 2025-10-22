# app.py

import traceback
import sqlite3
import os
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
from api.entrada import Entrada
from api.compra import Compra
from api.parque import Parque
from api.utils import TipoEntrada, MedioPago, MockMP, MockEmailService, ErrorCompra, UsuarioNoRegistradoError, MedioPagoError
from api.email_service import EmailService
from api.mercadopago_service import MercadoPagoService

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
DB_PATH = Path(app.instance_path) / 'development.db'
DB_PATH.parent.mkdir(exist_ok=True)

# Inicializar DB si no existe o está vacía
def init_db():
    if not DB_PATH.exists() or Path(DB_PATH).stat().st_size == 0:
        schema_path = Path(__file__).parent / 'schema.sql'
        with sqlite3.connect(DB_PATH) as conn:
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
        print(f"✅ Base de datos inicializada: {DB_PATH}")

init_db()
parque = Parque(str(DB_PATH))

# Configurar servicio de email
# Si hay credenciales en .env, usar servicio real; si no, usar mock
gmail_user = os.getenv("GMAIL_USER")
gmail_password = os.getenv("GMAIL_APP_PASSWORD")

if gmail_user and gmail_password:
    print(f"✅ Servicio de email configurado: {gmail_user}")
    email_service = EmailService(sender_email=gmail_user, sender_password=gmail_password)
    USE_REAL_EMAIL = True
else:
    print("⚠️  Usando MockEmailService (no se enviarán emails reales)")
    email_service = MockEmailService()
    USE_REAL_EMAIL = False

# Reusable mock instances
mock_mp = MockMP()

# Instancia del simulador de Mercado Pago
mp_service = MercadoPagoService()

@app.route("/")
def index():
    """Ruta raíz que sirve el frontend"""
    frontend_path = Path(__file__).parent / 'frontend' / 'index.html'
    return frontend_path.read_text(encoding='utf-8')

@app.route("/src/<path:filename>")
def serve_src(filename):
    """Sirve archivos JS y CSS desde frontend/src"""
    frontend_src = Path(__file__).parent / 'frontend' / 'src'
    return send_from_directory(frontend_src, filename)

@app.route("/public/<path:filename>")
def serve_public(filename):
    """Sirve archivos desde frontend/public"""
    frontend_public = Path(__file__).parent / 'frontend' / 'public'
    return send_from_directory(frontend_public, filename)

@app.route("/pago-mercadopago")
def pago_mercadopago():
    """Sirve la página de checkout simulado de Mercado Pago"""
    frontend_path = Path(__file__).parent / 'frontend' / 'pago.html'
    return frontend_path.read_text(encoding='utf-8')

@app.route("/usuario-actual")
def usuario_actual():
    """Retorna el usuario actual utilizado para las compras (demo).

    Para simplificar, el proyecto usa un usuario por defecto. Esta ruta asegura
    que exista en la base de datos y expone sus datos para mostrarlos en el frontend.
    """
    try:
        usuario_email = 'alvarosueldoc@gmail.com'
        usuario_nombre = 'Alvaro Sueldo'

        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, email, nombre FROM usuarios WHERE email = ?", (usuario_email,))
            row = cur.fetchone()
            if row:
                id_usuario, email, nombre = row
            else:
                cur.execute("INSERT INTO usuarios (email, nombre) VALUES (?, ?)", (usuario_email, usuario_nombre))
                id_usuario = cur.lastrowid
                email = usuario_email
                nombre = usuario_nombre

        return jsonify({
            "id": id_usuario,
            "email": email,
            "nombre": nombre
        }), 200
    except Exception as e:
        print(f"⚠️  Error en /usuario-actual: {e}")
        return jsonify({"error": "No se pudo obtener el usuario actual"}), 500

@app.route("/procesar-pago", methods=["POST"])
def procesar_pago():
    """
    Procesa un pago con tarjeta usando el simulador de Mercado Pago.
    Recibe datos de tarjeta y retorna el resultado del pago.
    """
    try:
        datos = request.json
        
        # Validar datos requeridos
        campos_requeridos = ['numero_tarjeta', 'cvv', 'vencimiento_mes', 
                            'vencimiento_anio', 'titular', 'monto']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({
                    "status": "rejected",
                    "message": f"Falta el campo: {campo}"
                }), 400
        
        # Procesar pago con el servicio de Mercado Pago
        resultado = mp_service.procesar_pago(datos)
        
        # Si el pago fue aprobado, enviar email de confirmación
        if resultado['status'] == 'approved' and 'compra_id' in datos:
            try:
                # Obtener datos de la compra desde la DB
                with sqlite3.connect(DB_PATH) as conn:
                    cur = conn.cursor()
                    
                    # Obtener compra y entradas
                    cur.execute("""
                        SELECT c.id, c.fecha_visita, c.cantidad, c.medio_pago, u.email
                        FROM compras c
                        JOIN usuarios u ON c.id_usuario = u.id
                        WHERE c.id = ?
                    """, (datos['compra_id'],))
                    
                    compra_row = cur.fetchone()
                    
                    if compra_row:
                        compra_id, fecha_visita, cantidad, medio_pago_str, usuario_email = compra_row
                        
                        # Obtener entradas de la compra
                        cur.execute("""
                            SELECT edad, tipo_entrada
                            FROM entradas
                            WHERE id_compra = ?
                        """, (compra_id,))
                        
                        entradas_rows = cur.fetchall()
                        
                        # Reconstruir objetos Entrada y Compra para el email
                        entradas = []
                        for edad, tipo_entrada_str in entradas_rows:
                            entrada = Entrada(
                                edad=edad,
                                tipo_pase=TipoEntrada[tipo_entrada_str]
                            )
                            entradas.append(entrada)
                        
                        compra = Compra(
                            fecha=datetime.strptime(fecha_visita, '%Y-%m-%d').date(),
                            entradas=entradas,
                            medio_pago=MedioPago[medio_pago_str]
                        )
                        
                        # Enviar email de confirmación
                        if USE_REAL_EMAIL:
                            try:
                                print(f"📧 Enviando email de confirmación a {usuario_email}...")
                                email_service.enviar_confirmacion(compra, usuario_email)
                                print(f"✅ Email enviado correctamente")
                                resultado['email_enviado'] = True
                            except Exception as email_error:
                                print(f"⚠️  Error al enviar email: {email_error}")
                                resultado['email_enviado'] = False
                        else:
                            email_service.enviar_confirmacion(compra)
                            resultado['email_enviado'] = False
                    
            except Exception as db_error:
                print(f"⚠️  Error al procesar email: {db_error}")
                import traceback
                traceback.print_exc()
        
        return jsonify(resultado), 200
        
    except Exception as e:
        print("--- ERROR EN PROCESAR PAGO ---")
        traceback.print_exc()
        print("-----------------------------")
        return jsonify({
            "status": "error",
            "message": "Error al procesar el pago"
        }), 500

@app.route("/pago-exitoso")
def pago_exitoso():
    """Página de confirmación de pago exitoso"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pago Exitoso</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 50px;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 500px;
            }
            .icon {
                font-size: 80px;
                margin-bottom: 20px;
                animation: bounce 0.5s ease;
            }
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-20px); }
            }
            h1 {
                color: #00A650;
                margin-bottom: 15px;
                font-size: 32px;
            }
            p {
                color: #666;
                margin-bottom: 10px;
                font-size: 16px;
                line-height: 1.6;
            }
            .transaction-id {
                background: #F5F5F5;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                font-family: monospace;
                color: #333;
            }
            .btn {
                display: inline-block;
                padding: 15px 40px;
                background: #009EE3;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                margin-top: 30px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .btn:hover {
                background: #0077B3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">✅</div>
            <h1>¡Pago Exitoso!</h1>
            <p>Tu pago ha sido procesado correctamente.</p>
            <p>Recibirás un email de confirmación con los detalles de tu compra.</p>
            <div class="transaction-id" id="transaction-info">
                Cargando información...
            </div>
            <a href="/" class="btn">Volver al inicio</a>
        </div>
        <script>
            const urlParams = new URLSearchParams(window.location.search);
            const transactionId = urlParams.get('transaction_id');
            if (transactionId) {
                document.getElementById('transaction-info').textContent = 
                    'ID de transacción: ' + transactionId;
            }
        </script>
    </body>
    </html>
    """

@app.route("/pago-pendiente")
def pago_pendiente():
    """Página para pagos pendientes de autorización"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pago Pendiente</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 50px;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 500px;
            }
            .icon {
                font-size: 80px;
                margin-bottom: 20px;
            }
            h1 {
                color: #FF9800;
                margin-bottom: 15px;
                font-size: 32px;
            }
            p {
                color: #666;
                margin-bottom: 10px;
                font-size: 16px;
                line-height: 1.6;
            }
            .btn {
                display: inline-block;
                padding: 15px 40px;
                background: #FF9800;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                margin-top: 30px;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">⏳</div>
            <h1>Pago Pendiente</h1>
            <p>Tu pago está pendiente de autorización.</p>
            <p>Te notificaremos por email cuando se complete.</p>
            <a href="/" class="btn">Volver al inicio</a>
        </div>
    </body>
    </html>
    """

@app.route("/comprar", methods=["POST"])
def comprar():
    datos = request.json

    try:
        # Validar y crear objetos Entrada para validación de negocio
        entradas = []
        edades = []
        for e in datos['entradas']:
            edad = int(e['edad'])
            edades.append(edad)  # Agregar edad a la lista
            tipo_entrada = TipoEntrada[e['tipoEntrada']]
            entrada = Entrada(edad=edad, tipo_pase=tipo_entrada)
            entradas.append(entrada)
        
        try:
            medio_pago = MedioPago[datos['medioPago']]
        except KeyError:
            return jsonify({"status": "error", "mensaje": "El medio de pago especificado no es válido o falta."}), 400
        except Exception as e:
            return jsonify({"status": "error", "mensaje": f"Error al procesar el medio de pago: {str(e)}"}), 400

        # Crear objeto Compra para validar reglas de negocio
        compra = Compra(
            fecha=datetime.strptime(datos['fecha'], '%Y-%m-%d').date(),
            entradas=entradas,
            medio_pago=medio_pago,
        )
        compra.validar_compra()
        total_compra = compra.calcular_total()
        
        # Persistir en DB usando Parque
        # Primero asegurar que existe un usuario (para demo, creamos/obtenemos uno genérico)
        usuario_email = 'alvarosueldoc@gmail.com'  # Email donde llegarán las confirmaciones
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, email FROM usuarios WHERE email = ?", (usuario_email,))
            row = cur.fetchone()
            if row:
                id_usuario = row[0]
                usuario_email = row[1]
            else:
                cur.execute("INSERT INTO usuarios (email, nombre) VALUES (?, ?)", (usuario_email, 'Alvaro Sueldo'))
                id_usuario = cur.lastrowid
        
        # Preparar datos para Parque
        tipos_pase = [e['tipoEntrada'] for e in datos['entradas']]
        datos_formulario = {
            'fecha': datos['fecha'],
            'cantidad': str(len(entradas)),
            'edades': edades,
            'tiposPase': tipos_pase,  # Lista de tipos, uno por entrada
            'medioPago': datos['medioPago']
        }
        
        # Guardar en DB
        id_compra = parque.realizar_compra(id_usuario=id_usuario, datos_formulario=datos_formulario)
        
        # Si el medio de pago es TARJETA, crear preferencia de MP y redirigir
        if medio_pago == MedioPago.TARJETA:
            # Crear preferencia de pago en Mercado Pago
            preferencia = mp_service.crear_preferencia({
                'total': total_compra,
                'descripcion': f'Entradas Parque Temático - {len(entradas)} entrada(s)',
                'compra_id': id_compra
            })
            
            # Retornar URL de checkout para redirección
            return jsonify({
                "status": "redireccion",
                "mensaje": "Redirigiendo a Mercado Pago...",
                "checkout_url": preferencia['init_point'],
                "preference_id": preferencia['preference_id'],
                "id_compra": id_compra,
                "total": total_compra,
                "cantidad": len(entradas)
            }), 200
        
        # Si es EFECTIVO, procesar directamente
        mock_mp.procesar_pago()
        
        # Enviar email de confirmación
        if USE_REAL_EMAIL:
            try:
                print(f"📧 Enviando email de confirmación a {usuario_email}...")
                email_service.enviar_confirmacion(compra, usuario_email)
                print(f"✅ Email enviado correctamente")
            except Exception as email_error:
                print(f"⚠️  Error al enviar email: {email_error}")
                # No fallamos la compra si el email falla
        else:
            # Usar mock para testing
            email_service.enviar_confirmacion(compra)

        return jsonify({
            "status": "exito",
            "mensaje": f"¡Compra exitosa! Se compraron {len(entradas)} entradas para el {compra.fecha.strftime('%d/%m/%Y')}.",
            "total": total_compra,
            "id_compra": id_compra,
            "email_enviado": USE_REAL_EMAIL
        }), 200
    
    except ErrorCompra as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 400
    except Exception as e:
        print("--- ERROR INESPERADO ---")
        traceback.print_exc()
        print("------------------------")
        return jsonify({"status": "error", "mensaje": "Ocurrió un error inesperado."}), 500


if __name__ == '__main__':
    app.run(debug=True)