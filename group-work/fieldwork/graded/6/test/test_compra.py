import pytest
from unittest.mock import patch
from datetime import date
from api.entrada import Entrada
from api.utils import TipoEntrada, MedioPago, LimiteEntradasError, ParqueCerradoError, FechaPasadaError, MockMP, MockEmailService, UsuarioNoRegistradoError, MedioPagoError

class TestCompra:

    def test_constructor_compra(self, compra_factory):
        compra_factory = compra_factory(medio_pago=MedioPago.EFECTIVO)
        # ASSERT
        assert compra_factory.medio_pago == MedioPago.EFECTIVO
        assert compra_factory.fecha == date(2025, 10, 25)
        assert compra_factory.fechaHora_compra is not None
        assert len(compra_factory.entradas) == 2
        assert [entrada.edad for entrada in compra_factory.entradas] == [30, 8]

    def test_contructor_compra_tarjeta(self, compra_factory):
        compra_factory = compra_factory(medio_pago=MedioPago.TARJETA)
        # ASSERT
        assert compra_factory.medio_pago == MedioPago.TARJETA
        assert compra_factory.fecha == date(2025, 10, 25)
        assert compra_factory.fechaHora_compra is not None
        assert len(compra_factory.entradas) == 2
        assert [entrada.edad for entrada in compra_factory.entradas] == [30, 8]

    def test_validar_compra_exitosa(self, compra_factory):
        # ASSERT
        assert compra_factory().validar_compra() is True

    def test_compra_fecha_pasada(self, compra_factory):

        # ACT & ASSERT
        with pytest.raises(FechaPasadaError, match='La fecha de la compra no puede ser en el pasado'):
            compra_factory(fecha=date(2020, 1, 1)).validar_compra()

    def test_compra_supera_limite_entradas(self, compra_factory):
        # ACT & ASSERT
        with pytest.raises(LimiteEntradasError, match='No se pueden comprar mas de 10 entradas'):
            compra_factory(entradas=[Entrada(edad=20, tipo_pase=TipoEntrada.REGULAR)] * 11).validar_compra()

    def test_compra_fecha_parque_cerrado(self, compra_factory):
        # ACT & ASSERT
        with pytest.raises(ParqueCerradoError, match='El parque está cerrado en esta fecha'):
            compra_factory(fecha=date(2025, 12, 25)).validar_compra()

    '''def test_compra_usuario_no_registrado(self, compra_factory):
        # ACT & ASSERT
        with pytest.raises(UsuarioNoRegistradoError, match='El usuario no está registrado'):
            compra_factory(usuario={'id': 2, 'registrado': False}).validar_compra()'''

    @pytest.mark.parametrize("edades, tipo_entrada, total_esperado", [
        ([30, 30, 30], TipoEntrada.REGULAR, 15000),
        ([30, 8],      TipoEntrada.REGULAR, 10000),
        ([30, 8],      TipoEntrada.VIP,     20000)
    ])
    def test_calcular_total(self, compra_factory, edades, tipo_entrada, total_esperado):
        """
        Verifica que el cálculo del total sea correcto.
        """
        lista_de_entradas = [Entrada(edad=edad, tipo_pase=tipo_entrada) for edad in edades]
        compra = compra_factory(entradas=lista_de_entradas)
        monto_calculado = compra.calcular_total()

        # ASSERT
        assert monto_calculado == total_esperado

    def test_conectar_mercado_pago_tarjeta(self, compra_factory):
        # ARRANGE
        mock_mp = MockMP()
        mock_email_service = MockEmailService()
        # ACT
        compra_factory(medio_pago=MedioPago.TARJETA).finalizar_compra(mock_mp, mock_email_service)

        # ASSERT
        assert mock_mp.redireccion is True

    def test_conectar_mercado_pago_efectivo(self, compra_factory):
        # ARRANGE
        compra = compra_factory()
        mock_mp = MockMP()
        mock_email_service = MockEmailService()
        # ACT
        compra.finalizar_compra(mock_mp, mock_email_service)

        # ASSERT
        assert mock_mp.redireccion is False
    
    def test_enviar_email_confirmacion(self, compra_factory):
        # ARRANGE
        mock_email_service = MockEmailService()
        mock_mp = MockMP()
        # ACT
        compra_factory().finalizar_compra(mock_mp, mock_email_service)
        assert mock_email_service.email_enviado is True

    def test_mostrar_cantidad_y_fecha(self, compra_factory):
        # ARRANGE
        compra = compra_factory()
        mock_mp = MockMP()
        mock_email_service = MockEmailService()

        # ACT
        # Capturamos el valor que devuelve el método.
        resultado = compra.finalizar_compra(mock_mp, mock_email_service)

        # ASSERT
        # Verificamos que el diccionario devuelto contenga los datos correctos.
        assert resultado["cantidad_comprada"] == 2
        assert resultado["fecha_visita"] == date(2025, 10, 25)
        