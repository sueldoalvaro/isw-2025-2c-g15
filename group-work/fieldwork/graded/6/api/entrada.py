from api.utils import TipoEntrada


class Entrada:
    def __init__(self, edad, tipo_pase):
        self.edad = edad
        self.tipo_pase = tipo_pase

    def calcular_precio(self):
        if self.tipo_pase == TipoEntrada.REGULAR:
            return 5000
        elif self.tipo_pase == TipoEntrada.VIP:
            return 10000