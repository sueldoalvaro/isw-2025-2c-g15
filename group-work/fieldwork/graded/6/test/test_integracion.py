from api.entrada import Entrada

def test_asociacion_entrada_compra(compra_factory, entrada_factory):
    compra = compra_factory(entradas=[entrada_factory(edad=25), entrada_factory(edad=10)])
    assert isinstance(compra.entradas[0], Entrada)
    assert isinstance(compra.entradas[1], Entrada)
    assert compra.entradas[0].edad == 25
    assert compra.entradas[1].edad == 10
    