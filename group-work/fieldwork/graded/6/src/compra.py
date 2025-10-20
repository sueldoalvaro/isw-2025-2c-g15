from enum import Enum
class Compra():
    pass


class TipoEntrada(Enum):
    REGULAR = 1
    VIP = 2


class MedioPago(Enum):
    EFECTIVO = 1
    TARJETA = 2


class ErrorCompra(Exception):
    pass


class LimiteEntradasError(ErrorCompra):
    pass


class ParqueCerradoError(ErrorCompra):
    pass


class FechaPasadaError(ErrorCompra):
    pass