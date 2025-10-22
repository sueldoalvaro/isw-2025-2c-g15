from datetime import date, datetime
from api.utils import MedioPago, SinEntradasError, LimiteEntradasError, ParqueCerradoError, FechaPasadaError, UsuarioNoRegistradoError, MedioPagoError, esta_abierto
from api.entrada import Entrada

class Compra():
    def __init__(self, fecha, entradas, medio_pago):
        self.fecha = fecha
        self.entradas = entradas
        self.medio_pago = medio_pago
        self.fechaHora_compra = datetime.now()

    def validar_compra(self):
        if self.fecha < date.today():
            raise FechaPasadaError('La fecha de la compra no puede ser en el pasado')
        if len(self.entradas) > 10:
            raise LimiteEntradasError('No se pueden comprar mas de 10 entradas')
        if len(self.entradas) == 0:
            raise SinEntradasError('No se han agregado entradas a la compra')
        if not esta_abierto(self.fecha):
            raise ParqueCerradoError('El parque está cerrado en esta fecha')
        #if not self.usuario.get('registrado'):
            #raise UsuarioNoRegistradoError('El usuario no está registrado')
        if self.medio_pago not in [MedioPago.EFECTIVO, MedioPago.TARJETA]:
            raise MedioPagoError('Medio de pago no válido')
        return True
    
    def calcular_total(self):
        return sum(entrada.calcular_precio() for entrada in self.entradas)

    def finalizar_compra(self, mock_mp, mock_email_service):
        if self.medio_pago == MedioPago.TARJETA:
            mock_mp.procesar_pago()
        mock_email_service.enviar_confirmacion(self)
        return {'cantidad_comprada': len(self.entradas), 'fecha_visita': self.fecha}