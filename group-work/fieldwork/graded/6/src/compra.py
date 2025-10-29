from src.servicio_mp import procesar_pago_mp, enviar_mail_confirmacion
from datetime import datetime, date
from typing import Optional, Dict, Any, List


class Compra:
    PRICES = {
        'regular': 1000,
        'vip': 2000
    }
    CLOSED_WEEKDAY = 6  # domingo

    def __init__(self, monto: Optional[float] = None, fecha: Optional[str] = None, metodo_pago: Optional[str] = None):
        """
        Constructor admite validaciones inmediatas si se pasan parámetros
        (compatibilidad con tests que instancian con valores).
        """
        if monto is not None:
            self._validar_monto(monto)
        if fecha is not None:
            self._validar_fecha(fecha)
        if metodo_pago is not None and not metodo_pago:
            raise ValueError("Debe seleccionar un metodo de pago.")

    def comprar(self, fecha: str, cantidad: int, edades: List[int], metodo_pago: str,
                email: str, tipo_pase: str, datos_tarjeta: Optional[Dict[str, Any]] = None) -> None:
        """
        Orquesta la compra: valida datos, procesa pago y envía confirmación si procede.
        """
        self._validar_inputs(fecha, cantidad, metodo_pago, tipo_pase)
        pago_exitoso = self._procesar_pago(cantidad, metodo_pago, tipo_pase, datos_tarjeta)
        if pago_exitoso:
            self._enviar_confirmacion(fecha, cantidad, edades, email, tipo_pase)

    # --- Validaciones agrupadas ---
    def _validar_inputs(self, fecha: str, cantidad: int, metodo_pago: Optional[str], tipo_pase: str) -> None:
        self._validar_tipo_pase(tipo_pase)
        self._validar_metodo_pago(metodo_pago)
        self._validar_cantidad(cantidad)
        self._validar_fecha(fecha)

    def _validar_tipo_pase(self, tipo_pase: str) -> None:
        if tipo_pase not in self.PRICES:
            raise ValueError("Tipo de pase no valido.")

    def _validar_metodo_pago(self, metodo_pago: Optional[str]) -> None:
        if not metodo_pago:
            raise ValueError("Debe seleccionar un metodo de pago.")

    def _validar_cantidad(self, cantidad: Any) -> None:
        if not isinstance(cantidad, int):
            raise ValueError("La cantidad de entradas debe ser un entero.")
        if cantidad < 1 or cantidad > 10:
            raise ValueError("La cantidad de entradas debe estar entre 1 y 10.")

    def _validar_fecha(self, fecha_str: str) -> None:
        """
        Valida:
         - formato YYYY-MM-DD -> "Formato de fecha inválido"
         - no anterior a hoy -> "La fecha no puede ser anterior a hoy"
         - no día cerrado (domingo) -> "El parque se encuentra cerrado en la fecha seleccionada."
        """
        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("Formato de fecha inválido")

        if fecha_obj < date.today():
            raise ValueError("La fecha no puede ser anterior a hoy")
        if fecha_obj.weekday() == self.CLOSED_WEEKDAY:
            raise ValueError("El parque se encuentra cerrado en la fecha seleccionada.")

    def _validar_monto(self, monto: float) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo")

    # --- Cálculo y procesamiento de pago ---
    def _calcular_monto(self, cantidad: int, tipo_pase: str) -> float:
        precio_unitario = self.PRICES[tipo_pase]
        return precio_unitario * cantidad

    def _procesar_pago(self, cantidad: int, metodo_pago: str, tipo_pase: str,
                       datos_tarjeta: Optional[Dict[str, Any]]) -> bool:
        monto_total = self._calcular_monto(cantidad, tipo_pase)
        self._validar_monto(monto_total)

        if metodo_pago == 'tarjeta':
            if not datos_tarjeta:
                raise ValueError("Se requieren datos de la tarjeta para este metodo de pago.")
            resultado = procesar_pago_mp(monto_total, datos_tarjeta)
            return bool(resultado)
        elif metodo_pago == 'efectivo':
            return True
        else:
            raise ValueError("Método de pago no válido.")

    # --- Envío de confirmación ---
    def _enviar_confirmacion(self, fecha: str, cantidad: int, edades: List[int], email: str, tipo_pase: str) -> None:
        monto_total = self._calcular_monto(cantidad, tipo_pase)
        detalles_compra = {
            'fecha': fecha,
            'cantidad': cantidad,
            'edades': edades,
            'monto_total': monto_total,
            'tipo_pase': tipo_pase
        }
        enviar_mail_confirmacion(email, detalles_compra)

