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
    fecha = "2023-10-10"
    cantidad = 2
    edades = [25, 30]
    metodo_pago = 'tarjeta'
    email = "cliente@gmail.com"
    compra.comprar(fecha, cantidad, edades, metodo_pago, email)

    #ASSERT
    mock_mp.assert_called_once()
    mock_mail.assert_called_once()