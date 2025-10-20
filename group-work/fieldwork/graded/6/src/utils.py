from enum import Enum


class ErrorCompra(Exception):
    pass


class LimiteEntradasError(ErrorCompra):
    pass


class ParqueCerradoError(ErrorCompra):
    pass


class FechaPasadaError(ErrorCompra):
    pass


class UsuarioNoRegistradoError(ErrorCompra):    
    pass


class MedioPagoError(ErrorCompra):
    pass


class TipoEntrada(Enum):
    REGULAR = 1
    VIP = 2


class MedioPago(Enum):
    EFECTIVO = 1
    TARJETA = 2


class MockMP():
    def __init__(self):
        self.redireccion = False

    def procesar_pago(self) -> bool:
        self.redireccion = True
        
    

class MockEmailService():
    def __init__(self):
        self.email_enviado = False

    def enviar_confirmacion(self) -> bool:
        self.email_enviado = True
        