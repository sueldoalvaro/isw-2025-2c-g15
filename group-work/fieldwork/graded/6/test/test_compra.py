import pytest
from datetime import date
from src.compra import Compra, TipoEntrada, MedioPago, LimiteEntradasError, ParqueCerradoError, FechaPasadaError

class TestCompra:
    def test_constructor_compra(self):
        # ARRANGE
        fecha_visita = date(2025, 10, 25)
        cantidad_entradas = 2
        edades_visitantes = [30, 8]
        medio_pago = MedioPago.EFECTIVO
        tipo_entrada = TipoEntrada.VIP

        # ACT
        compra = Compra(
            fecha=fecha_visita,
            cantidad=cantidad_entradas,
            edades=edades_visitantes,
            tipo_entrada=tipo_entrada,
            medio_pago=medio_pago
        )

        # ASSERT
        assert compra.tipo_entrada == tipo_entrada
        assert compra.medio_pago == medio_pago
        assert compra.fecha == fecha_visita
        assert compra.cantidad == cantidad_entradas
        assert compra.edades == edades_visitantes

    def test_validar_compra_exitosa(self):
        # ARRANGE
        fecha_visita = date(2025, 10, 25)
        cantidad_entradas = 2
        edades_visitantes = [30, 8]
        medio_pago = MedioPago.EFECTIVO
        tipo_entrada = TipoEntrada.VIP

        # ACT
        compra = Compra(
            fecha=fecha_visita,
            cantidad=cantidad_entradas,
            edades=edades_visitantes,
            tipo_entrada=tipo_entrada,
            medio_pago=medio_pago
        )

        # ASSERT
        assert compra.validar_compra() is True

    def test_validar_falla_fecha_pasada(self):
        # ARRANGE
        compra = Compra(
            fecha=date(2020, 1, 1), 
            cantidad=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.REGULAR,
            medio_pago=MedioPago.EFECTIVO
        )

        # ACT & ASSERT
        with pytest.raises(FechaPasadaError, match='La fecha de la compra no puede ser en el pasado'):
            compra.validar_compra()

    def test_validar_falla_limite_entradas(self):
        # ARRANGE
        compra = Compra(
            fecha=date(2025, 10, 25),
            cantidad=11,
            edades=[20] * 11,
            tipo_entrada=TipoEntrada.REGULAR,
            medio_pago=MedioPago.TARJETA
        )

        # ACT & ASSERT
        with pytest.raises(LimiteEntradasError, match='No se pueden comprar mas de 10 entradas'):
            compra.validar_compra()
    
    def test_validar_falla_parque_cerrado(self):
        # ARRANGE
        compra = Compra(
            fecha=date(2025, 10, 27), 
            cantidad=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.VIP,
            medio_pago=MedioPago.EFECTIVO
        )

        # ACT & ASSERT
        with pytest.raises(ParqueCerradoError, match='El parque está cerrado en esta fecha'):
            compra.validar_compra()

'''
    def test_compra_11_entradas(self):
        with pytest.raises(LimiteEntradasError, match='No se pueden comprar mas de 10 entradas'):
            Compra(date(2025, 10, 25), 11, [20] * 11, TipoEntrada.REGULAR, MedioPago.TARJETA)


    def test_compra_fecha_parque_cerrado(self):
        compra = Compra(date(2025, 10, 25), 2, [30, 8], TipoEntrada.VIP, MedioPago.EFECTIVO)
        with pytest.raises(ParqueCerradoError, match='El parque está cerrado en esta fecha'):
            compra.comprar()
'''
    