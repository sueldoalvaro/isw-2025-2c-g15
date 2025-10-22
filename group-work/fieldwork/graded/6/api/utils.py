from enum import Enum
from datetime import datetime


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


class SinEntradasError(ErrorCompra):
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

    def enviar_confirmacion(self, compra) -> bool:
        self.email_enviado = True


def esta_abierto(fecha_actual):
    """
    Verifica si el parque está abierto según la fecha dada.
    
    Reglas:
    - Cierra Lunes.
    - Cierra 25 de Diciembre y 1 de Enero.
    - Abre de 9:00 a 19:00 hs.
    """
    
    feriados = [
        (12, 25), 
        (1, 1)    
    ]
    
    if fecha_actual.weekday() == 0:
        return False
        
    dia_actual = (fecha_actual.month, fecha_actual.day)
    if dia_actual in feriados:
        return False
    
    return True
    


if __name__ == "__main__":
    
    print("--- Probando lógica de horarios ---")
    
    # Un martes a las 10:00 (Debería estar ABIERTO)
    fecha_abierta = datetime(year=2025, month=10, day=21, hour=10, minute=0)
    print(f"¿Abierto el {fecha_abierta}? {esta_abierto(fecha_abierta)}")
    
    # Un lunes a las 11:00 (Debería estar CERRADO por ser lunes)
    fecha_lunes = datetime(year=2025, month=10, day=27, hour=11, minute=0)
    print(f"¿Abierto el {fecha_lunes}? {esta_abierto(fecha_lunes)}")

    # Un martes a las 20:00 (Debería estar CERRADO por horario)
    fecha_tarde = datetime(year=2025, month=10, day=21, hour=20, minute=0)
    print(f"¿Abierto el {fecha_tarde}? {esta_abierto(fecha_tarde)}")
    
    # Navidad (Debería estar CERRADO por feriado)
    fecha_navidad = datetime(year=2025, month=12, day=25, hour=14, minute=0)
    print(f"¿Abierto el {fecha_navidad}? {esta_abierto(fecha_navidad)}")