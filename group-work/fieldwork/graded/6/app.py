# app.py

import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from src.compra import Compra
from src.utils import TipoEntrada, MedioPago, MockMP, MockEmailService, ErrorCompra,UsuarioNoRegistradoError, MedioPagoError

app = Flask(__name__)
CORS(app)  # 🔓 Habilita CORS para todas las rutas

@app.route("/comprar", methods=["POST"])
def comprar():
    # tu lógica acá
    datos = request.json

    try:
        # Convertimos los datos del frontend a los tipos correctos
        compra = Compra(
            fecha=datetime.strptime(datos['fecha'], '%Y-%m-%d').date(),
            cantidad_entradas=int(datos['cantidad']),
            edades=[int(e) for e in datos['edades']],
            tipo_entrada=TipoEntrada[datos['tipoPase']],
            medio_pago=MedioPago[datos['medioPago']],
            usuario={"registrado": True} # Asumimos usuario logueado
        )

        # Ejecutamos la lógica que ya probaste
        compra.validar_compra()
        
        resultado = compra.finalizar_compra(MockMP(), MockEmailService()) # Usamos los mocks por ahora
        total_compra = compra.calcular_total()

        # 2. Añadí el 'total' al diccionario de la respuesta
        return jsonify({
            "status": "exito",
            "mensaje": f"¡Compra exitosa! Se compraron {resultado['cantidad_comprada']} entradas.",
            "total": total_compra
        }), 200
    
    except ErrorCompra as e:
        # Si la validación falla, devolvemos un error
        return jsonify({"status": "error", "mensaje": str(e)}), 400
    except Exception as e:
        # 2. Imprimimos el traceback completo en la terminal
        print("--- ERROR INESPERADO ---")
        traceback.print_exc()
        print("------------------------")
        
        # 3. Devolvemos la respuesta genérica como antes
        return jsonify({"status": "error", "mensaje": "Ocurrió un error inesperado."}), 500


class MockMP:
    def __init__(self):
        self.redireccion = False

    def procesar_pago(self) -> bool:
        self.redireccion = True


class MockEmailService:
    def __init__(self):
        self.email_enviado = False

    def enviar_confirmacion(self, compra):
        self.email_enviado = True


if __name__ == '__main__':
    app.run(debug=True)