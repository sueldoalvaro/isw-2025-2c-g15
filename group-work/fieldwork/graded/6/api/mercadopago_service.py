"""
Simulador de Mercado Pago para procesamiento de pagos con tarjeta.
Incluye validación Luhn, generación de IDs y simulación de estados.
"""
import time
import uuid
from datetime import datetime
from typing import Dict, Literal


class MercadoPagoService:
    """
    Servicio que simula el comportamiento de Mercado Pago.
    
    Funcionalidades:
    - Validación de números de tarjeta (algoritmo de Luhn)
    - Generación de IDs de transacción únicos
    - Simulación de estados: approved, rejected, pending
    - Simulación de tiempo de procesamiento
    """
    
    # Tarjetas de prueba (simulan las de MP sandbox)
    TARJETAS_APROBADAS = [
        "4509953566233704",  # Visa
        "5031433215406351",  # Mastercard
        "3711803032594270",  # Amex
    ]
    
    TARJETAS_RECHAZADAS = [
        "4111111111111111",  # Fondos insuficientes
        "5555555555554444",  # Tarjeta expirada
    ]
    
    TARJETAS_PENDIENTES = [
        "4000000000000002",  # Requiere autorización
    ]
    
    def __init__(self):
        """Inicializa el servicio de Mercado Pago."""
        self.transacciones = []
        self.redireccion = False
        self.url_checkout = None
        self.preference_id = None
    
    def crear_preferencia(self, datos_compra: Dict) -> Dict:
        """
        Crea una preferencia de pago (simula MP preference API).
        
        Args:
            datos_compra: Diccionario con:
                - total: Monto total
                - descripcion: Descripción de la compra
                - compra_id: ID interno de la compra
        
        Returns:
            Dict con preference_id y init_point (URL de checkout)
        """
        preference_id = f"PREF-{uuid.uuid4().hex[:16].upper()}"
        compra_id = datos_compra.get('compra_id', 'unknown')
        
        # URL del checkout simulado
        init_point = f"/pago-mercadopago?preference_id={preference_id}&compra_id={compra_id}"
        
        self.preference_id = preference_id
        self.url_checkout = init_point
        self.redireccion = True
        
        return {
            "preference_id": preference_id,
            "init_point": init_point,
            "status": "created"
        }
    
    def procesar_pago(self, datos_tarjeta: Dict) -> Dict:
        """
        Procesa un pago con tarjeta (simula MP payment API).
        
        Args:
            datos_tarjeta: Diccionario con:
                - numero_tarjeta: String de 13-19 dígitos
                - cvv: String de 3-4 dígitos
                - vencimiento_mes: String "01"-"12"
                - vencimiento_anio: String "25"-"35"
                - titular: Nombre del titular
                - monto: Monto a cobrar
        
        Returns:
            Dict con:
                - transaction_id: ID único de transacción
                - status: "approved", "rejected", "pending"
                - status_detail: Descripción del estado
                - payment_method: "credit_card"
                - monto: Monto procesado
                - fecha: Timestamp del proceso
        """
        # Simular tiempo de procesamiento
        time.sleep(0.5)
        
        numero_tarjeta = datos_tarjeta.get('numero_tarjeta', '').replace(' ', '')
        cvv = datos_tarjeta.get('cvv', '')
        monto = datos_tarjeta.get('monto', 0)
        
        # Validaciones
        if not self._validar_tarjeta(numero_tarjeta):
            return self._crear_respuesta_rechazada(
                "Número de tarjeta inválido",
                monto
            )
        
        if not self._validar_cvv(cvv):
            return self._crear_respuesta_rechazada(
                "CVV inválido",
                monto
            )
        
        if not self._validar_vencimiento(
            datos_tarjeta.get('vencimiento_mes'),
            datos_tarjeta.get('vencimiento_anio')
        ):
            return self._crear_respuesta_rechazada(
                "Tarjeta vencida",
                monto
            )
        
        # Determinar estado según tarjeta
        status = self._determinar_estado(numero_tarjeta)
        
        if status == "approved":
            return self._crear_respuesta_aprobada(monto)
        elif status == "pending":
            return self._crear_respuesta_pendiente(monto)
        else:
            return self._crear_respuesta_rechazada(
                "Fondos insuficientes",
                monto
            )
    
    def _validar_tarjeta(self, numero: str) -> bool:
        """
        Valida número de tarjeta usando algoritmo de Luhn.
        
        Args:
            numero: String con el número de tarjeta
        
        Returns:
            True si es válido, False si no
        """
        if not numero.isdigit():
            return False
        
        if len(numero) < 13 or len(numero) > 19:
            return False
        
        # Algoritmo de Luhn
        def luhn_checksum(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            
            return checksum % 10
        
        return luhn_checksum(numero) == 0
    
    def _validar_cvv(self, cvv: str) -> bool:
        """Valida CVV (3-4 dígitos)."""
        return cvv.isdigit() and len(cvv) in [3, 4]
    
    def _validar_vencimiento(self, mes: str, anio: str) -> bool:
        """Valida fecha de vencimiento."""
        try:
            mes_int = int(mes)
            anio_int = int(anio)
            
            if mes_int < 1 or mes_int > 12:
                return False
            
            # Asumir año de 2 dígitos (25 = 2025)
            if anio_int < 100:
                anio_int += 2000
            
            # Comparar con fecha actual
            now = datetime.now()
            if anio_int < now.year:
                return False
            if anio_int == now.year and mes_int < now.month:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def _determinar_estado(self, numero_tarjeta: str) -> Literal["approved", "rejected", "pending"]:
        """
        Determina el estado del pago según el número de tarjeta.
        
        Args:
            numero_tarjeta: Número de tarjeta sin espacios
        
        Returns:
            Estado: "approved", "rejected", o "pending"
        """
        if numero_tarjeta in self.TARJETAS_APROBADAS:
            return "approved"
        elif numero_tarjeta in self.TARJETAS_RECHAZADAS:
            return "rejected"
        elif numero_tarjeta in self.TARJETAS_PENDIENTES:
            return "pending"
        else:
            # Por defecto, aprobar tarjetas válidas no listadas
            return "approved"
    
    def _crear_respuesta_aprobada(self, monto: float) -> Dict:
        """Crea respuesta de pago aprobado."""
        transaction_id = f"TXN-{uuid.uuid4().hex[:16].upper()}"
        
        respuesta = {
            "transaction_id": transaction_id,
            "status": "approved",
            "status_detail": "accredited",
            "payment_method": "credit_card",
            "monto": monto,
            "fecha": datetime.now().isoformat(),
            "message": "Pago aprobado exitosamente"
        }
        
        self.transacciones.append(respuesta)
        return respuesta
    
    def _crear_respuesta_rechazada(self, razon: str, monto: float) -> Dict:
        """Crea respuesta de pago rechazado."""
        transaction_id = f"TXN-{uuid.uuid4().hex[:16].upper()}"
        
        respuesta = {
            "transaction_id": transaction_id,
            "status": "rejected",
            "status_detail": razon.lower().replace(' ', '_'),
            "payment_method": "credit_card",
            "monto": monto,
            "fecha": datetime.now().isoformat(),
            "message": f"Pago rechazado: {razon}"
        }
        
        self.transacciones.append(respuesta)
        return respuesta
    
    def _crear_respuesta_pendiente(self, monto: float) -> Dict:
        """Crea respuesta de pago pendiente."""
        transaction_id = f"TXN-{uuid.uuid4().hex[:16].upper()}"
        
        respuesta = {
            "transaction_id": transaction_id,
            "status": "pending",
            "status_detail": "pending_authorization",
            "payment_method": "credit_card",
            "monto": monto,
            "fecha": datetime.now().isoformat(),
            "message": "Pago pendiente de autorización"
        }
        
        self.transacciones.append(respuesta)
        return respuesta
    
    def obtener_transaccion(self, transaction_id: str) -> Dict:
        """
        Obtiene una transacción por su ID.
        
        Args:
            transaction_id: ID de la transacción
        
        Returns:
            Dict con datos de la transacción o None si no existe
        """
        for transaccion in self.transacciones:
            if transaccion['transaction_id'] == transaction_id:
                return transaccion
        return None
