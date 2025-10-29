from src.servicio_mp import procesar_pago_mp, enviar_mail_confirmacion
from datetime import datetime, date

class Compra():
    def __init__(self, monto=None, fecha=None, metodo_pago=None):
        # Precios por tipo de pase
        self.precios = {
            'regular': 1000,
            'vip': 2000
        }

        # Si se pasan parámetros al constructor, validarlos inmediatamente
        if monto is not None:
            self._validar_monto(monto)
        if fecha is not None:
            self._validar_fecha(fecha)
        # método de pago solo se valida en comprar/_validar_inputs normalmente
        # pero aceptamos el parámetro para compatibilidad con tests que instancian así.
        if metodo_pago is not None and not metodo_pago:
            raise ValueError("Debe seleccionar un metodo de pago.")

    def comprar(self, fecha, cantidad, edades, metodo_pago, email, tipo_pase, datos_tarjeta=None):
        # 1. Validar todos los inputs primero 
        self._validar_inputs(fecha, cantidad, metodo_pago, tipo_pase)

        # 2. Procesar el pago
        pago_exitoso = self._procesar_pago(cantidad, metodo_pago, tipo_pase, datos_tarjeta)

        # 3. Enviar la confirmación si el pago fue exitoso
        if pago_exitoso:
            self._enviar_confirmacion(fecha, cantidad, edades, email, tipo_pase)

    def _validar_inputs(self, fecha, cantidad, metodo_pago, tipo_pase):
        """Método privado para agrupar todas las validaciones de entrada."""
        if tipo_pase not in self.precios:
            raise ValueError("Tipo de pase no valido.")
        if not metodo_pago:
            raise ValueError("Debe seleccionar un metodo de pago.")
        # validar cantidad y rango
        if not isinstance(cantidad, int):
            raise ValueError("La cantidad de entradas debe ser un entero.")
        if cantidad < 1 or cantidad > 10:
            raise ValueError("La cantidad de entradas debe estar entre 1 y 10.")

        # validar fecha (formato, pasado y días cerrados)
        self._validar_fecha(fecha)

    def _validar_fecha(self, fecha_str):
        """Valida formato YYYY-MM-DD, que no sea pasada y que no sea domingo."""
        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Formato de fecha inválido")

        if fecha_obj < date.today():
            raise ValueError("La fecha no puede ser anterior a hoy")
        if fecha_obj.weekday() == 6:  # Domingo
            raise ValueError("El parque se encuentra cerrado en la fecha seleccionada.")

    def _validar_monto(self, monto):
        """Valida que el monto calculado sea positivo."""
        if monto <= 0:
            raise ValueError("El monto debe ser positivo")

    def _procesar_pago(self, cantidad, metodo_pago, tipo_pase, datos_tarjeta):
        """Método privado que maneja la lógica de pago y devuelve un booleano o valor truthy."""
        precio_unitario = self.precios[tipo_pase]
        monto_total = precio_unitario * cantidad

        # validar monto calculado
        self._validar_monto(monto_total)

        if metodo_pago == 'tarjeta':
            if not datos_tarjeta:
                raise ValueError("Se requieren datos de la tarjeta para este metodo de pago.")
            # procesar_pago_mp puede devolver un id de transacción (truthy) o lanzar/retornar False
            return procesar_pago_mp(monto_total, datos_tarjeta)
        
        elif metodo_pago == 'efectivo':
            return True  # El pago en efectivo se considera exitoso para confirmar
        
        # Si llega otro método desconocido
        raise ValueError("Método de pago no válido.")

    def _enviar_confirmacion(self, fecha, cantidad, edades, email, tipo_pase):
        """Método privado para construir y enviar el email de confirmación."""
        precio_unitario = self.precios[tipo_pase]
        monto_total = precio_unitario * cantidad
        
        detalles_compra = {
            'fecha': fecha,
            'cantidad': cantidad,
            'edades': edades,
            'monto_total': monto_total,
            'tipo_pase': tipo_pase
        }
        enviar_mail_confirmacion(email, detalles_compra)

