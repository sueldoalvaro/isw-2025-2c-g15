import pytest
from datetime import date
from src.compra import Compra
from src.utils import TipoEntrada, MedioPago, LimiteEntradasError, ParqueCerradoError, FechaPasadaError, MockMP, MockEmailService, UsuarioNoRegistradoError, MedioPagoError

class TestCompra:
    @pytest.fixture
    def usuario_registrado(self):
        """
        Este fixture simula un usuario registrado.
        """
        return {'id': 1, 'registrado': True}
    
    @pytest.fixture
    def compra_valida_fixture_efectivo(self, usuario_registrado) -> Compra:
        """
        Este fixture crea y devuelve una instancia de Compra con datos válidos.
        """
        
        return Compra(
            fecha=date(2025, 10, 25),
            cantidad_entradas=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.VIP,
            medio_pago=MedioPago.EFECTIVO,
            usuario=usuario_registrado
        )
    @pytest.fixture
    def compra_valida_fixture_tarjeta(self, usuario_registrado) -> Compra:
        """
        Este fixture crea y devuelve una instancia de Compra con datos válidos.
        """
        
        return Compra(
            fecha=date(2025, 10, 25),
            cantidad_entradas=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.VIP,
            medio_pago=MedioPago.TARJETA,
            usuario=usuario_registrado
        )

    def test_constructor_compra(self, compra_valida_fixture_efectivo):

        # ASSERT
        assert compra_valida_fixture_efectivo.tipo_entrada == TipoEntrada.VIP
        assert compra_valida_fixture_efectivo.medio_pago == MedioPago.EFECTIVO
        assert compra_valida_fixture_efectivo.fecha == date(2025, 10, 25)
        assert compra_valida_fixture_efectivo.cantidad_entradas == 2
        assert compra_valida_fixture_efectivo.edades == [30, 8]
        assert compra_valida_fixture_efectivo.usuario == {'id': 1, 'registrado': True}

    def test_contructor_compra_tarjeta(self, compra_valida_fixture_tarjeta):

        # ASSERT
        assert compra_valida_fixture_tarjeta.tipo_entrada == TipoEntrada.VIP
        assert compra_valida_fixture_tarjeta.medio_pago == MedioPago.TARJETA
        assert compra_valida_fixture_tarjeta.fecha == date(2025, 10, 25)
        assert compra_valida_fixture_tarjeta.cantidad_entradas == 2
        assert compra_valida_fixture_tarjeta.edades == [30, 8]
        assert compra_valida_fixture_tarjeta.usuario == {'id': 1, 'registrado': True}

    def test_validar_compra_exitosa(self, compra_valida_fixture_efectivo):
        # ASSERT
        assert compra_valida_fixture_efectivo.validar_compra() is True

    def test_compra_sin_medio_pago(self, usuario_registrado):
        # ARRANGE
        compra = Compra(
            fecha=date(2025, 10, 25),
            cantidad_entradas=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.VIP,
            medio_pago=None,
            usuario=usuario_registrado
        )

        # ACT & ASSERT
        with pytest.raises(MedioPagoError):
            compra.validar_compra()

    def test_compra_fecha_pasada(self, usuario_registrado):
        # ARRANGE
        compra = Compra(
            fecha=date(2020, 1, 1), 
            cantidad_entradas=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.REGULAR,
            medio_pago=MedioPago.EFECTIVO,
            usuario=usuario_registrado
        )

        # ACT & ASSERT
        with pytest.raises(FechaPasadaError, match='La fecha de la compra no puede ser en el pasado'):
            compra.validar_compra()

    def test_compra_supera_limite_entradas(self, usuario_registrado):
        # ARRANGE
        compra = Compra(
            fecha=date(2025, 10, 25),
            cantidad_entradas=11,
            edades=[20] * 11,
            tipo_entrada=TipoEntrada.REGULAR,
            medio_pago=MedioPago.TARJETA,
            usuario=usuario_registrado
        )

        # ACT & ASSERT
        with pytest.raises(LimiteEntradasError, match='No se pueden comprar mas de 10 entradas'):
            compra.validar_compra()

    def test_compra_fecha_parque_cerrado(self, usuario_registrado):
        # ARRANGE
        compra = Compra(
            fecha=date(2025, 10, 27), 
            cantidad_entradas=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.VIP,
            medio_pago=MedioPago.EFECTIVO,
            usuario=usuario_registrado
        )

        # ACT & ASSERT
        with pytest.raises(ParqueCerradoError, match='El parque está cerrado en esta fecha'):
            compra.validar_compra()

    def test_compra_usuario_no_registrado(self):
        # ARRANGE
        usuario_no_registrado = {'id': 2, 'registrado': False}
        compra = Compra(
            fecha=date(2025, 10, 25),
            cantidad_entradas=2,
            edades=[30, 8],
            tipo_entrada=TipoEntrada.VIP,
            medio_pago=MedioPago.EFECTIVO,
            usuario=usuario_no_registrado
        )

        # ACT & ASSERT
        with pytest.raises(UsuarioNoRegistradoError, match='El usuario no está registrado'):
            compra.validar_compra()

    @pytest.mark.parametrize("tipo_entrada, cantidad, total_esperado", [
        (TipoEntrada.REGULAR, 3, 30000),    # Escenario 1: 3 entradas regulares
        (TipoEntrada.VIP,     2, 40000),    # Escenario 2: 2 entradas VIP
        (TipoEntrada.REGULAR, 1, 10000),    # Escenario 3: 1 entrada regular
        (TipoEntrada.VIP,     10, 200000)  # Escenario 4: 10 entradas VIP
    ])
    def test_calcular_total(self, tipo_entrada, cantidad, total_esperado, usuario_registrado):
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
            medio_pago=MedioPago.TARJETA,
            usuario=usuario_registrado
        )

        # ACT: Llamamos EXCLUSIVAMENTE al método bajo prueba.
        monto_calculado = compra.calcular_total()

        # ASSERT: Comparamos el resultado con nuestro valor esperado y fiable.
        assert monto_calculado == total_esperado

    def test_conectar_mercado_pago(self, compra_valida_fixture_tarjeta):
        # ARRANGE
        compra = compra_valida_fixture_tarjeta
        mock_mp = MockMP()
        mock_email_service = MockEmailService()
        # ACT
        compra.finalizar_compra(mock_mp, mock_email_service)

        # ASSERT
        assert mock_mp.redireccion is True

    def test_conectar_mercado_pago_efectivo(self, compra_valida_fixture_efectivo):
        # ARRANGE
        compra = compra_valida_fixture_efectivo
        mock_mp = MockMP()
        mock_email_service = MockEmailService()
        # ACT
        compra.finalizar_compra(mock_mp, mock_email_service)

        # ASSERT
        assert mock_mp.redireccion is False
    
    @pytest.mark.parametrize('compra_fixture', [
        'compra_valida_fixture_efectivo',
        'compra_valida_fixture_tarjeta'
    ])
    def test_enviar_email_confirmacion(self, compra_fixture, request):
        # ARRANGE
        mock_email_service = MockEmailService()
        mock_mp = MockMP()
        # ACT
        request.getfixturevalue(compra_fixture).finalizar_compra(mock_mp, mock_email_service)
        assert mock_email_service.email_enviado is True

    @pytest.mark.parametrize('compra', [
        'compra_valida_fixture_efectivo',
        'compra_valida_fixture_tarjeta'
    ])
    def test_mostrar_cantidad_y_fecha(self, compra, request):
        # ARRANGE
        compra = request.getfixturevalue(compra)
        mock_mp = MockMP()
        mock_email_service = MockEmailService()

        # ACT
        # Capturamos el valor que devuelve el método.
        resultado = compra.finalizar_compra(mock_mp, mock_email_service)

        # ASSERT
        # Verificamos que el diccionario devuelto contenga los datos correctos.
        assert resultado["cantidad_comprada"] == 2
        assert resultado["fecha_visita"] == date(2025, 10, 25)
        