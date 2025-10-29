import pytest
from src.compra import Compra
from datetime import date, timedelta

# --- Tests de Casos Exitosos (Happy Path) ---

def test_compra_con_tarjeta_exitosa(mocker):
    """
    Test para verificar que el metodo comprar con tarjeta funciona correctamente.
    """
    # ARRANGE
    mock_mp = mocker.patch('src.compra.procesar_pago_mp')
    mock_mp.return_value = "TRANSACCION_EXITOSA_123" # Simulamos una respuesta exitosa del pago
    
    mock_mail = mocker.patch('src.compra.enviar_mail_confirmacion')
    compra = Compra()

    # Los datos de la tarjeta ahora se definen y se pasan desde el test
    datos_tarjeta_prueba = {
        'numero': '1234-5678-9012-3456',
        'vencimiento': '12/25',
        'cvv': '123'
    }

    # ACT
    fecha = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d') # Siempre una fecha futura válida
    cantidad = 2
    edades = [25, 30]
    email = "cliente@gmail.com"
    tipo_pase = "regular"

    compra.comprar(
        fecha=fecha,
        cantidad=cantidad,
        edades=edades,
        metodo_pago='tarjeta',
        email=email,
        tipo_pase=tipo_pase,
        datos_tarjeta=datos_tarjeta_prueba # Pasamos los datos de tarjeta
    )

    # ASSERT
    monto_esperado = 1000 * cantidad
    mock_mp.assert_called_once_with(monto_esperado, datos_tarjeta_prueba) # Verificamos con los datos del test
    mock_mail.assert_called_once() # Verificamos que se intentó enviar el mail

def test_compra_exitosa_en_efectivo(mocker):
    """
    Verifica que la compra en efectivo no llama a Mercado Pago pero sí envía el mail.
    """
    # ARRANGE
    mock_mp = mocker.patch('src.compra.procesar_pago_mp')
    mock_mail = mocker.patch('src.compra.enviar_mail_confirmacion')
    compra = Compra()

    # ACT
    compra.comprar(
        fecha=(date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
        cantidad=3,
        edades=[20, 21, 22],
        metodo_pago='efectivo',
        email="cliente_efectivo@test.com",
        tipo_pase='regular'
    )

    # ASSERT
    mock_mp.assert_not_called()
    mock_mail.assert_called_once()

# --- Tests de Casos de Error (Sad Path) ---

def test_falla_al_comprar_en_dia_cerrado(mocker):
    """
    Verifica que no se puede comprar si el parque está cerrado en la fecha seleccionada.
    """
    # ARRANGE
    compra = Compra()
    hoy = date.today()
    dias_para_domingo = (6 - hoy.weekday() + 7) % 7
    fecha_domingo = (hoy + timedelta(days=dias_para_domingo)).strftime('%Y-%m-%d')

    # ACT & ASSERT
    with pytest.raises(ValueError, match="El parque se encuentra cerrado en la fecha seleccionada."):
        compra.comprar(
            fecha=fecha_domingo,
            cantidad=2,
            edades=[25, 30],
            metodo_pago='efectivo', # Usamos efectivo para no necesitar datos de tarjeta
            email="cliente@gmail.com",
            tipo_pase="regular"
        )

def test_falla_al_comprar_sin_metodo_de_pago(mocker):
    """
    Verifica que el sistema falla si no se especifica un método de pago.
    """
    # ARRANGE
    compra = Compra()

    # ACT & ASSERT
    with pytest.raises(ValueError, match="Debe seleccionar un metodo de pago."):
        compra.comprar(
            fecha=(date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            cantidad=1,
            edades=[25],
            metodo_pago=None, # Condición a probar
            email="cliente@gmail.com",
            tipo_pase="regular"
        )

def test_falla_al_comprar_mas_de_diez_entradas(mocker):
    """
    Verifica que no se pueden comprar más de 10 entradas a la vez.
    """
    # ARRANGE
    compra = Compra()

    # ACT & ASSERT
    with pytest.raises(ValueError, match="La cantidad de entradas debe estar entre 1 y 10."):
        compra.comprar(
            fecha=(date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            cantidad=11, # Condición a probar
            edades=[25] * 11,
            metodo_pago='efectivo',
            email="cliente@gmail.com",
            tipo_pase="regular"
        )

def test_monto_negativo():
    """
    La compra no debe permitir montos negativos
    """

    with pytest.raises(ValueError) as error:
        compra = Compra(-100, "2025-12-25", "efectivo")
    assert str(error.value) == "El monto debe ser positivo"

def test_monto_cero():
    """
    La compra no debe permitir monto cero
    """
    with pytest.raises(ValueError) as error:
        compra = Compra(0, "2025-12-25", "efectivo")
    assert str(error.value) == "El monto debe ser positivo"

def test_fecha_pasada():
    """
    No se pueden comprar entradas para fechas pasadas
    """
    with pytest.raises(ValueError) as error:
        compra = Compra(100, "2024-10-29", "efectivo")
    assert str(error.value) == "La fecha no puede ser anterior a hoy"

def test_fecha_formato_invalido():
    """
    La fecha debe tener formato válido YYYY-MM-DD
    """
    with pytest.raises(ValueError) as error:
        compra = Compra(100, "29-10-2025", "efectivo")
    assert str(error.value) == "Formato de fecha inválido"