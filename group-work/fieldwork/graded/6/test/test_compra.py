import pytest
from datetime import date
from src.compra import Compra
from src.utils import TipoEntrada, MedioPago, LimiteEntradasError, ParqueCerradoError, FechaPasadaError, MockMP

class TestCompra:
    @pytest.fixture
    def compra_valida_fixture_efectivo(self) -> Compra:
        """
        Este fixture crea y devuelve una instancia de Compra con datos válidos.
        """
        
        return Compra(
            fecha=date(2025, 10, 25),
            cantidad_entradas=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.VIP,
            medio_pago=MedioPago.EFECTIVO
        )
    @pytest.fixture
    def compra_valida_fixture_tarjeta(self) -> Compra:
        """
        Este fixture crea y devuelve una instancia de Compra con datos válidos.
        """
        
        return Compra(
            fecha=date(2025, 10, 25),
            cantidad_entradas=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.VIP,
            medio_pago=MedioPago.TARJETA
        )

    def test_constructor_compra(self, compra_valida_fixture_efectivo):

        # ASSERT
        assert compra_valida_fixture_efectivo.tipo_entrada == TipoEntrada.VIP
        assert compra_valida_fixture_efectivo.medio_pago == MedioPago.EFECTIVO
        assert compra_valida_fixture_efectivo.fecha == date(2025, 10, 25)
        assert compra_valida_fixture_efectivo.cantidad_entradas == 2
        assert compra_valida_fixture_efectivo.edades == [30, 8]

    def test_contructor_compra_tarjeta(self, compra_valida_fixture_tarjeta):

        # ASSERT
        assert compra_valida_fixture_tarjeta.tipo_entrada == TipoEntrada.VIP
        assert compra_valida_fixture_tarjeta.medio_pago == MedioPago.TARJETA
        assert compra_valida_fixture_tarjeta.fecha == date(2025, 10, 25)
        assert compra_valida_fixture_tarjeta.cantidad_entradas == 2
        assert compra_valida_fixture_tarjeta.edades == [30, 8]

    def test_validar_compra_exitosa(self, compra_valida_fixture_efectivo):
        # ASSERT
        assert compra_valida_fixture_efectivo.validar_compra() is True

    def test_validar_falla_fecha_pasada(self):
        # ARRANGE
        compra = Compra(
            fecha=date(2020, 1, 1), 
            cantidad_entradas=2,
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
            cantidad_entradas=11,
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
            cantidad_entradas=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.VIP,
            medio_pago=MedioPago.EFECTIVO
        )

        # ACT & ASSERT
        with pytest.raises(ParqueCerradoError, match='El parque está cerrado en esta fecha'):
            compra.validar_compra()

    @pytest.mark.parametrize("tipo_entrada, cantidad, total_esperado", [
        (TipoEntrada.REGULAR, 3, 30000),    # Escenario 1: 3 entradas regulares
        (TipoEntrada.VIP,     2, 40000),    # Escenario 2: 2 entradas VIP
        (TipoEntrada.REGULAR, 1, 10000),    # Escenario 3: 1 entrada regular
        (TipoEntrada.VIP,     10, 200000)  # Escenario 4: 10 entradas VIP
    ])
    def test_calcular_total(self, tipo_entrada, cantidad, total_esperado):
        """
        Verifica que el cálculo del total sea correcto para diferentes
        cantidades y tipos de pase.
        """
        # ARRANGE: Preparamos el objeto. El total esperado ya está definido.
        compra = Compra(
            fecha=date(2025, 10, 25),
            cantidad_entradas=cantidad,
            edades=[30] * cantidad,
            tipo_entrada=tipo_entrada,
            medio_pago=MedioPago.TARJETA
        )

        # ACT: Llamamos EXCLUSIVAMENTE al método bajo prueba.
        monto_calculado = compra.calcular_total()

        # ASSERT: Comparamos el resultado con nuestro valor esperado y fiable.
        assert monto_calculado == total_esperado

    def test_finalizar_compra_tarjeta(self, compra_valida_fixture_tarjeta):
        # ARRANGE
        compra = compra_valida_fixture_tarjeta
        mock_mp = MockMP()
        # ACT
        compra.finalizar_compra(mock_mp)

        # ASSERT
        assert mock_mp.redireccion is True
    
    def test_finalizar_compra_efectivo(self, compra_valida_fixture_efectivo):
        # ARRANGE
        compra = compra_valida_fixture_efectivo
        mock_mp = MockMP()
        # ACT
        compra.finalizar_compra(mock_mp)

        # ASSERT
        assert mock_mp.redireccion is False
        