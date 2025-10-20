from datetime import date
from src.utils import TipoEntrada, MedioPago, LimiteEntradasError, ParqueCerradoError, FechaPasadaError, UsuarioNoRegistradoError, MedioPagoError

class Compra():
    def __init__(self, fecha, cantidad_entradas, edades, tipo_entrada, medio_pago, usuario):
        self.fecha = fecha
        self.cantidad_entradas = cantidad_entradas
        self.edades = edades
        self.tipo_entrada = tipo_entrada
        self.medio_pago = medio_pago
        self.usuario = usuario

    def validar_compra(self):
        if self.fecha < date.today():
            raise FechaPasadaError('La fecha de la compra no puede ser en el pasado')
        if self.cantidad_entradas > 10:
            raise LimiteEntradasError('No se pueden comprar mas de 10 entradas')
        if self.fecha in [date(2025, 10, 27), date(2025, 10, 28)]:
            raise ParqueCerradoError('El parque está cerrado en esta fecha')
        if not self.usuario.get('registrado'):
            raise UsuarioNoRegistradoError('El usuario no está registrado')
        if self.medio_pago not in [MedioPago.EFECTIVO, MedioPago.TARJETA]:
            raise MedioPagoError('Medio de pago no válido')
        return True
    
    def calcular_total(self):
        if self.tipo_entrada == TipoEntrada.REGULAR:
            precio_unitario = 10000
        else:
            precio_unitario = 20000
        return precio_unitario * self.cantidad_entradas

    def finalizar_compra(self, mock_mp, mock_email_service):
        if self.medio_pago == MedioPago.TARJETA:
            mock_mp.procesar_pago()
        mock_email_service.enviar_confirmacion(self)
        return {'cantidad_comprada': self.cantidad_entradas, 'fecha_visita': self.fecha}