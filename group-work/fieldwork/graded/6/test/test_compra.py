import pytest
from src.compra import Compra

def test_compra_con_tarjeta(mocker):
    """
    Test para verificar que el metodo comprar con tarjeta funciona correctamente.
    
    """
    #ARRANGE
    mock_mp = mocker.patch('src.compra.procesar_pago_mp')
    mock_mail = mocker.patch('src.compra.enviar_mail_confirmacion')
    compra = Compra()

    #ACT 
    fecha = "2025-10-10"
    cantidad = 2
    edades = [25, 30]
    metodo_pago = 'tarjeta'
    email = "cliente@gmail.com"
    compra.comprar(fecha, cantidad, edades, metodo_pago, email)

    #ASSERT
    monto_esperado = 1000 * 2
    mock_mp.assert_called_once_with(
        monto_esperado,
        {
            'numero': '1234-5678-9012-3456',
            'vencimiento': '12/25',
            'cvv': '123'
        }
    ) 
    mock_mail.assert_called_once_with(
        email,
        {
            'fecha': fecha,
            'cantidad': cantidad,
            'edades': edades,
            'monto_total': monto_esperado
        }
    )

def test_comprar_dia_no_disponible(mocker):
    """
    Test para verificar que el metodo comprar no permite compras en dias no disponibles.
    """
    # ARRANGE
    fecha_cerrado = "2025-10-06"

    compra = Compra()
    fecha = fecha_cerrado
    cantidad = 2
    edades = [25, 30]
    metodo_pago = 'tarjeta'
    email = "cliente@gmail.com"

    # ACT & ASSERT
    with pytest.raises(ValueError, match="El parque se encuentra cerrado en la fecha seleccionada."):
        compra.comprar(
            fecha,
            cantidad,
            edades,
            metodo_pago,
            email)
        
def test_comprar_sin_metodo_de_pago(mocker):
    """
    Test para verificar que el metodo comprar no permite compras sin metodo de pago.
    """

    # ARRANGE
    compra = Compra()
    fecha = "2025-10-10"
    cantidad = 1
    edades = [25]
    metodo_pago = None
    email = "cliente@gmail.com"

    # ACT & ASSERT
    with pytest.raises(ValueError, match="Debe seleccionar un metodo de pago."):
        compra.comprar(
            fecha,
            cantidad,
            edades,
            metodo_pago,
            email)