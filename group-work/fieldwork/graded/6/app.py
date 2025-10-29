from flask import Flask, send_from_directory, request, jsonify
from src.compra import Compra
from pathlib import Path
import sqlite3
from typing import Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

APP_ROOT = Path(__file__).resolve().parent
DB_PATH = APP_ROOT / 'instance' / 'database.db'
FRONTEND_DIR = APP_ROOT / 'frontend'

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='')


@app.route('/')
def index():
    logger.debug("Serving index.html")
    return send_from_directory(str(FRONTEND_DIR), 'index.html')


@app.route('/<path:filename>')
def frontend_files(filename):
    logger.debug(f"Serving static file: {filename}")
    return send_from_directory(str(FRONTEND_DIR), filename)


def _ensure_db_dir():
    """Asegura que exista el directorio de la base de datos"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensuring DB directory exists: {DB_PATH.parent}")


def _get_user_fullname_by_email(conn: sqlite3.Connection, email: Optional[str] = None) -> str:
    """
    Obtiene el nombre completo del usuario por email.
    Si no se encuentra o no se provee email, devuelve el primer usuario (asumiendo usuario demo).
    """
    cur = conn.cursor()
    if email:
        cur.execute("SELECT nombre, apellido FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if row:
            return f"{row[0]} {row[1]}"
    
    # Si no hay email o no se encontró, usar el primer usuario (demo)
    cur.execute("SELECT nombre, apellido FROM users ORDER BY id LIMIT 1")
    row = cur.fetchone()
    if not row:
        raise ValueError("No hay usuarios en la base de datos. Ejecute init_db.py primero.")
    return f"{row[0]} {row[1]}"


def _save_compra_to_db(fecha: str, cantidad: int, tipo_pase: str,
                       metodo_pago: str, monto_total: int,
                       email: Optional[str], edades: Optional[List[int]]) -> int:
    """
    Inserta una compra y sus tickets asociados.
    Asigna el nombre del comprador a cada ticket.
    """
    logger.info(f"Saving purchase: fecha={fecha}, cantidad={cantidad}, tipo={tipo_pase}")
    _ensure_db_dir()
    
    if not DB_PATH.exists():
        logger.error(f"Database file not found: {DB_PATH}")
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()
        
        # Insertar compra
        logger.debug("Inserting into compras table")
        cur.execute(
            "INSERT INTO compras (fecha, cantidad, tipo_pase, metodo_pago, monto_total, email, estado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (fecha, cantidad, tipo_pase, metodo_pago, monto_total, email or None, 'confirmada')
        )
        compra_id = cur.lastrowid
        logger.debug(f"Purchase inserted with ID: {compra_id}")

        # Obtener nombre del comprador
        buyer_name = _get_user_fullname_by_email(conn, email)
        
        # Insertar tickets con el nombre del comprador
        if edades:
            logger.debug(f"Inserting {len(edades)} tickets for {buyer_name}")
            for edad in edades:
                cur.execute(
                    "INSERT INTO tickets (compra_id, nombre, edad) VALUES (?, ?, ?)",
                    (compra_id, buyer_name, edad)
                )

        conn.commit()
        logger.info(f"Purchase saved successfully with ID: {compra_id}")
        return compra_id
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()


@app.route('/api/compra', methods=['POST'])
def api_compra():
    """
    Endpoint para procesar una compra:
    - Valida datos
    - Procesa pago
    - Persiste compra y tickets con nombre del comprador
    """
    logger.info("Received purchase request")
    data = request.get_json(silent=True) or {}
    logger.debug(f"Request data: {data}")

    required = ['fecha', 'cantidad', 'metodo_pago', 'tipo_pase']
    for key in required:
        if key not in data:
            logger.warning(f"Missing required field: {key}")
            return jsonify({'ok': False, 'error': f'Falta campo {key}'}), 400

    try:
        fecha = data['fecha']
        cantidad = int(data['cantidad'])
        metodo_pago = data['metodo_pago']
        tipo_pase = data['tipo_pase']
        edades = data.get('edades', [])
        email = data.get('email', '')  # email opcional, usará usuario demo si no se provee
        datos_tarjeta = data.get('datos_tarjeta')

        logger.debug(f"Processing purchase: fecha={fecha}, cantidad={cantidad}, tipo={tipo_pase}")

        # Validar compra
        compra = Compra()
        compra.comprar(
            fecha=fecha,
            cantidad=cantidad,
            edades=edades,
            metodo_pago=metodo_pago,
            email=email,
            tipo_pase=tipo_pase,
            datos_tarjeta=datos_tarjeta
        )

        # Calcular monto
        precio_unitario = Compra.PRICES.get(tipo_pase, 0)
        monto_total = precio_unitario * cantidad
        
        # Persistir compra y tickets
        logger.info(f"Purchase validated, saving to DB. Amount: {monto_total}")
        compra_id = _save_compra_to_db(fecha, cantidad, tipo_pase, metodo_pago, monto_total, email, edades)

        logger.info(f"Purchase completed successfully. ID: {compra_id}")
        return jsonify({
            'ok': True, 
            'message': 'Compra confirmada',
            'compra_id': compra_id
        })

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Internal error: {str(e)}", exc_info=True)
        return jsonify({'ok': False, 'error': 'Error interno'}), 500


if __name__ == '__main__':
    logger.info("Starting Flask server on http://localhost:5001")
    app.run(host='localhost', port=5001, debug=True)