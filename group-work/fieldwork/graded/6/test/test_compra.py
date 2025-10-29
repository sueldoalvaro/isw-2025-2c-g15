import pytest
from datetime import date, timedelta
from src.compra import Compra

# Helpers
def fecha_futura(dias=1):
    return (date.today() + timedelta(days=dias)).strftime('%Y-%m-%d')

def fecha_pasada(dias=1):
    return (date.today() - timedelta(days=dias)).strftime('%Y-%m-%d')

# --- Tests Happy Path ---

def test_compra_con_tarjeta_exitosa(mocker):
    mock_mp = mocker.patch('src.compra.procesar_pago_mp')
    mock_mp.return_value = "TRANSACCION_EXITOSA_123"
    mock_mail = mocker.patch('src.compra.enviar_mail_confirmacion')

    compra = Compra()
    datos_tarjeta = {'numero': '1234-5678-9012-3456', 'vencimiento': '12/25', 'cvv': '123'}
    compra.comprar(
        fecha=fecha_futura(),
        cantidad=2,
        edades=[25, 30],
        metodo_pago='tarjeta',
        email='cliente@gmail.com',
        tipo_pase='regular',
        datos_tarjeta=datos_tarjeta
    )

    mock_mp.assert_called_once_with(1000 * 2, datos_tarjeta)
    mock_mail.assert_called_once()

def test_compra_exitosa_en_efectivo(mocker):
    mock_mp = mocker.patch('src.compra.procesar_pago_mp')
    mock_mail = mocker.patch('src.compra.enviar_mail_confirmacion')

    compra = Compra()
    compra.comprar(
        fecha=fecha_futura(),
        cantidad=3,
        edades=[20, 21, 22],
        metodo_pago='efectivo',
        email='cliente2@gmail.com',
        tipo_pase='regular'
    )

    mock_mp.assert_not_called()
    mock_mail.assert_called_once()

# --- Tests Sad Path / Validaciones ---

def test_falla_al_comprar_en_dia_cerrado():
    # calcular próximo domingo (weekday()==6)
    hoy = date.today()
    dias_a_domingo = (6 - hoy.weekday()) % 7
    if dias_a_domingo == 0:
        dias_a_domingo = 7
    fecha_domingo = (hoy + timedelta(days=dias_a_domingo)).strftime('%Y-%m-%d')

    compra = Compra()
    with pytest.raises(ValueError, match="El parque se encuentra cerrado en la fecha seleccionada."):
        compra.comprar(
            fecha=fecha_domingo,
            cantidad=1,
            edades=[30],
            metodo_pago='efectivo',
            email='a@b.com',
            tipo_pase='regular'
        )

def test_falla_al_comprar_sin_metodo_de_pago():
    compra = Compra()
    with pytest.raises(ValueError, match="Debe seleccionar un metodo de pago."):
        compra.comprar(
            fecha=fecha_futura(),
            cantidad=1,
            edades=[30],
            metodo_pago='',
            email='a@b.com',
            tipo_pase='regular'
        )

def test_falla_al_comprar_mas_de_diez_entradas():
    compra = Compra()
    with pytest.raises(ValueError, match="La cantidad de entradas debe estar entre 1 y 10."):
        compra.comprar(
            fecha=fecha_futura(),
            cantidad=11,
            edades=list(range(11)),
            metodo_pago='efectivo',
            email='a@b.com',
            tipo_pase='regular'
        )

def test_monto_negativo():
    with pytest.raises(ValueError, match="El monto debe ser positivo"):
        Compra(-100, fecha_futura(), 'efectivo')

def test_monto_cero():
    with pytest.raises(ValueError, match="El monto debe ser positivo"):
        Compra(0, fecha_futura(), 'efectivo')

def test_fecha_pasada():
    with pytest.raises(ValueError, match="La fecha no puede ser anterior a hoy"):
        Compra(100, fecha_pasada(), 'efectivo')

def test_fecha_formato_invalido():
    with pytest.raises(ValueError, match="Formato de fecha inválido"):
        Compra(100, "29-10-2025", 'efectivo')

def test_tipo_pase_invalido():
    compra = Compra()
    with pytest.raises(ValueError, match="Tipo de pase no valido."):
        compra.comprar(
            fecha=fecha_futura(),
            cantidad=1,
            edades=[30],
            metodo_pago='efectivo',
            email='a@b.com',
            tipo_pase='premium'
        )

def test_metodo_pago_no_valido(mocker):
    mock_mail = mocker.patch('src.compra.enviar_mail_confirmacion')
    compra = Compra()
    with pytest.raises(ValueError, match="Método de pago no válido."):
        compra.comprar(
            fecha=fecha_futura(),
            cantidad=1,
            edades=[30],
            metodo_pago='transferencia',
            email='a@b.com',
            tipo_pase='regular'
        )
    mock_mail.assert_not_called()

def test_tarjeta_sin_datos_levanta_error():
    compra = Compra()
    with pytest.raises(ValueError, match="Se requieren datos de la tarjeta para este metodo de pago."):
        compra.comprar(
            fecha=fecha_futura(),
            cantidad=1,
            edades=[25],
            metodo_pago='tarjeta',
            email='a@b.com',
            tipo_pase='regular',
            datos_tarjeta=None
        )

def test_cantidad_no_entera():
    compra = Compra()
    with pytest.raises(ValueError, match="La cantidad de entradas debe ser un entero."):
        compra.comprar(
            fecha=fecha_futura(),
            cantidad='3',
            edades=[20,21,22],
            metodo_pago='efectivo',
            email='a@b.com',
            tipo_pase='regular'
        )

def test_cantidad_menor_1():
    compra = Compra()
    with pytest.raises(ValueError, match="La cantidad de entradas debe estar entre 1 y 10."):
        compra.comprar(
            fecha=fecha_futura(),
            cantidad=0,
            edades=[],
            metodo_pago='efectivo',
            email='a@b.com',
            tipo_pase='regular'
        )

def test_no_envia_mail_si_pago_falla(mocker):
    mock_mp = mocker.patch('src.compra.procesar_pago_mp')
    mock_mp.return_value = None
    mock_mail = mocker.patch('src.compra.enviar_mail_confirmacion')

    compra = Compra()
    compra.comprar(
        fecha=fecha_futura(),
        cantidad=2,
        edades=[25,26],
        metodo_pago='tarjeta',
        email='a@b.com',
        tipo_pase='regular',
        datos_tarjeta={'numero':'1','vencimiento':'01/26','cvv':'123'}
    )

    mock_mp.assert_called_once()
    mock_mail.assert_not_called()

def test_compra_vip_calcula_monto_correcto(mocker):
    mock_mp = mocker.patch('src.compra.procesar_pago_mp')
    mock_mp.return_value = "OK"
    mock_mail = mocker.patch('src.compra.enviar_mail_confirmacion')

    compra = Compra()
    cant = 2
    datos = {'numero':'1','vencimiento':'01/26','cvv':'123'}
    compra.comprar(
        fecha=fecha_futura(),
        cantidad=cant,
        edades=[30,31],
        metodo_pago='tarjeta',
        email='a@b.com',
        tipo_pase='vip',
        datos_tarjeta=datos
    )

    mock_mp.assert_called_once_with(2000 * cant, datos)
    mock_mail.assert_called_once()

def test_constructor_metodo_pago_vacio_levanta():
    with pytest.raises(ValueError, match="Debe seleccionar un metodo de pago."):
        Compra(100, fecha_futura(), "")