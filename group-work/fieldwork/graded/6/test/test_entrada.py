import pytest
from api.utils import TipoEntrada

def test_constructor_entrada(entrada_factory):
    entrada = entrada_factory(edad=25, tipo_pase=TipoEntrada.VIP)
    assert entrada.edad == 25
    assert entrada.tipo_pase == TipoEntrada.VIP

def test_calcular_precio_entrada_regular(entrada_factory):
    entrada = entrada_factory()
    assert entrada.calcular_precio() == 5000

def test_calcular_precio_entrada_vip(entrada_factory):
    entrada = entrada_factory( tipo_pase=TipoEntrada.VIP)
    assert entrada.calcular_precio() == 10000
