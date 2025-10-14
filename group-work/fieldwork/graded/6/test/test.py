import pytest
from src.compra import Compra

def test_compra_2_entradas_efectivo_para_dia_siguiente():
    #ACT
    compra = Compra()
    compra.comprar(fecha="2025-10-10", cantidad=2, edades=[30, 8], metodo_pago="efectivo")
    #ASSERT
    assert 20000 == 2 * compra.precio
    assert compra.metodo_pago == "efectivo"

def test_compra_11_entradas():
    compra = Compra()
    codigo = compra.comprar(fecha="2025-10-10", cantidad=11, edades=[10, 10, 10, 10, 10, 10, 20, 20, 20, 20, 20],
                            metodo_pago="efectivo")
    #ASSERT
    assert codigo is None

def test_compra_con_tarjeta():
    compra = Compra()
    codigo = compra.comprar(fecha="2025-10-10", cantidad=2, edades=[30, 8], metodo_pago="tarjeta")
    #ASSERT
    assert codigo is not None
    assert 20000 == 2 * compra.precio
    assert compra.metodo_pago == "tarjeta" 

def test_compra_sin_metodo_pago():
    compra = Compra()
    codigo = compra.comprar(fecha="2025-10-10", cantidad=2, edades=[30, 8], metodo_pago=None)
    #ASSERT
    assert codigo is None

def test_compra_fecha_parque_cerrado():
    compra = Compra()
    codigo = compra.comprar(fecha="2025-10-12", cantidad=2, edades=[30, 8], metodo_pago="efectivo")
    #ASSERT
    assert codigo is None
    
