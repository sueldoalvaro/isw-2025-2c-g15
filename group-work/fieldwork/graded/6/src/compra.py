from src.servicio_mp import procesar_pago_mp, enviar_mail_confirmacion
from datetime import datetime, date

class Compra():
    def __init__(self):
        self.precios = {
            'regular': 1000,
            'vip': 2000
        }

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
        if not (1 <= cantidad <= 10):
            raise ValueError("La cantidad de entradas debe estar entre 1 y 10.")
        if not metodo_pago:
            raise ValueError("Debe seleccionar un metodo de pago.")
        
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        if fecha_obj < date.today():
            raise ValueError("La fecha de visita no puede ser en el pasado.")
        if fecha_obj.weekday() == 6: # Domingos
            raise ValueError("El parque se encuentra cerrado en la fecha seleccionada.")

    def _procesar_pago(self, cantidad, metodo_pago, tipo_pase, datos_tarjeta):
        """Método privado que maneja la lógica de pago y devuelve un booleano."""
        precio_unitario = self.precios[tipo_pase]
        monto_total = precio_unitario * cantidad

        if metodo_pago == 'tarjeta':
            if not datos_tarjeta:
                raise ValueError("Se requieren datos de la tarjeta para este metodo de pago.")
            return procesar_pago_mp(monto_total, datos_tarjeta)
        
        elif metodo_pago == 'efectivo':
            return True # El pago en efectivo siempre es exitoso para la confirmación
        
        return False

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