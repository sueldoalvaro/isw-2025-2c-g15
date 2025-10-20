from enum import Enum


class ErrorCompra(Exception):
    pass


class LimiteEntradasError(ErrorCompra):
    pass


class ParqueCerradoError(ErrorCompra):
    pass


class FechaPasadaError(ErrorCompra):
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
        # Lógica simulada para procesar el pago
        return True