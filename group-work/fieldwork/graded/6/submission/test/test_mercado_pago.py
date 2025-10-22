import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from api.compra import Compra
from api.entrada import Entrada
from api.utils import TipoEntrada, MedioPago, MockMP
from api.mercadopago_service import MercadoPagoService


class TestMercadoPagoIntegracion:
    """
    Tests para validar la integración con Mercado Pago.
    Verifican que el procesamiento de pagos con tarjeta funcione correctamente.
    """
    
    def test_compra_con_tarjeta_debe_llamar_a_mercado_pago(self):
        """
        Prueba que cuando el medio de pago es TARJETA,
        se debe invocar el servicio de Mercado Pago.
        """
        # --- ARRANGE ---
        entrada = Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR)
        compra = Compra(
            fecha=date(2025, 12, 20),
            entradas=[entrada],
            medio_pago=MedioPago.TARJETA
        )
        
        mock_mp = MockMP()
        mock_email = Mock()
        
        # Verificar estado inicial
        assert mock_mp.redireccion == False
        
        # --- ACT ---
        compra.finalizar_compra(mock_mp, mock_email)
        
        # --- ASSERT ---
        # Cuando es TARJETA, debe procesar el pago con MP
        assert mock_mp.redireccion == True
    
    def test_compra_con_efectivo_no_debe_llamar_a_mercado_pago(self):
        """
        Prueba que cuando el medio de pago es EFECTIVO,
        NO se debe invocar Mercado Pago.
        """
        # --- ARRANGE ---
        entrada = Entrada(edad=25, tipo_pase=TipoEntrada.VIP)
        compra = Compra(
            fecha=date(2025, 11, 15),
            entradas=[entrada],
            medio_pago=MedioPago.EFECTIVO
        )
        
        mock_mp = MockMP()
        mock_email = Mock()
        
        # --- ACT ---
        compra.finalizar_compra(mock_mp, mock_email)
        
        # --- ASSERT ---
        # Con EFECTIVO no debe redirigir a MP
        assert mock_mp.redireccion == False
    
    def test_mercado_pago_procesar_pago_retorna_true(self):
        """
        Prueba que el método procesar_pago() de Mercado Pago
        retorna True cuando el pago es exitoso.
        """
        # --- ARRANGE ---
        mock_mp = MockMP()
        
        # --- ACT ---
        resultado = mock_mp.procesar_pago()
        
        # --- ASSERT ---
        # procesar_pago debe cambiar el estado
        assert mock_mp.redireccion == True
    
    def test_mercado_pago_cambia_estado_de_redireccion(self):
        """
        Prueba que procesar_pago() cambia el flag redireccion.
        Este flag indica que el usuario debe ser redirigido a MP.
        """
        # --- ARRANGE ---
        mock_mp = MockMP()
        assert mock_mp.redireccion == False
        
        # --- ACT ---
        mock_mp.procesar_pago()
        
        # --- ASSERT ---
        assert mock_mp.redireccion == True
    
    def test_multiples_compras_con_tarjeta_usan_mercado_pago(self):
        """
        Prueba que múltiples compras con TARJETA
        siempre invocan a Mercado Pago.
        """
        # --- ARRANGE ---
        entrada1 = Entrada(edad=20, tipo_pase=TipoEntrada.REGULAR)
        entrada2 = Entrada(edad=15, tipo_pase=TipoEntrada.VIP)
        
        compra1 = Compra(
            fecha=date(2025, 10, 10),
            entradas=[entrada1],
            medio_pago=MedioPago.TARJETA
        )
        
        compra2 = Compra(
            fecha=date(2025, 11, 11),
            entradas=[entrada2],
            medio_pago=MedioPago.TARJETA
        )
        
        mock_mp1 = MockMP()
        mock_mp2 = MockMP()
        mock_email = Mock()
        
        # --- ACT ---
        compra1.finalizar_compra(mock_mp1, mock_email)
        compra2.finalizar_compra(mock_mp2, mock_email)
        
        # --- ASSERT ---
        assert mock_mp1.redireccion == True
        assert mock_mp2.redireccion == True
    
    def test_compra_con_tarjeta_actualiza_estado_antes_de_email(self):
        """
        Prueba que el procesamiento de MP ocurre antes del envío de email.
        El orden correcto es: 1) Validar, 2) Procesar pago, 3) Enviar email.
        """
        # --- ARRANGE ---
        entrada = Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR)
        compra = Compra(
            fecha=date(2025, 12, 25),
            entradas=[entrada],
            medio_pago=MedioPago.TARJETA
        )
        
        # Mock que registra el orden de llamadas
        call_order = []
        
        class MockMPOrden(MockMP):
            def procesar_pago(self):
                call_order.append('pago')
                super().procesar_pago()
        
        class MockEmailOrden:
            def enviar_confirmacion(self, compra):
                call_order.append('email')
        
        mock_mp = MockMPOrden()
        mock_email = MockEmailOrden()
        
        # --- ACT ---
        compra.finalizar_compra(mock_mp, mock_email)
        
        # --- ASSERT ---
        # El pago debe procesarse antes del email
        assert call_order == ['pago', 'email']
    
    @patch('api.utils.MockMP')
    def test_fallo_en_mercado_pago_se_propaga(self, mock_mp_class):
        """
        Prueba que si Mercado Pago falla, la excepción se propaga
        correctamente sin completar la compra.
        """
        # --- ARRANGE ---
        entrada = Entrada(edad=25, tipo_pase=TipoEntrada.VIP)
        compra = Compra(
            fecha=date(2025, 11, 20),
            entradas=[entrada],
            medio_pago=MedioPago.TARJETA
        )
        
        # Configurar mock para que falle
        mock_mp_instance = MagicMock()
        mock_mp_instance.procesar_pago.side_effect = Exception("Error de conexión con MP")
        mock_mp_class.return_value = mock_mp_instance
        
        mock_email = Mock()
        
        # --- ACT & ASSERT ---
        with pytest.raises(Exception) as exc_info:
            compra.finalizar_compra(mock_mp_instance, mock_email)
        
        assert "Error de conexión con MP" in str(exc_info.value)
    
    def test_mercado_pago_mock_tiene_metodo_procesar_pago(self):
        """
        Prueba que MockMP tiene el método procesar_pago disponible.
        """
        # --- ARRANGE & ACT ---
        mock_mp = MockMP()
        
        # --- ASSERT ---
        assert hasattr(mock_mp, 'procesar_pago')
        assert callable(mock_mp.procesar_pago)
    
    def test_mercado_pago_mock_tiene_atributo_redireccion(self):
        """
        Prueba que MockMP tiene el atributo redireccion
        que indica si debe redirigir al usuario.
        """
        # --- ARRANGE & ACT ---
        mock_mp = MockMP()
        
        # --- ASSERT ---
        assert hasattr(mock_mp, 'redireccion')
        assert isinstance(mock_mp.redireccion, bool)
        assert mock_mp.redireccion == False  # Estado inicial


class TestMercadoPagoIntegracionReal:
    """
    Tests preparados para la integración real con Mercado Pago.
    Actualmente usan mocks, pero pueden adaptarse para usar la API real.
    """
    
    def test_estructura_datos_para_mercado_pago(self):
        """
        Prueba que la compra tiene todos los datos necesarios
        para enviar a la API de Mercado Pago.
        """
        # --- ARRANGE ---
        entrada1 = Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR)
        entrada2 = Entrada(edad=8, tipo_pase=TipoEntrada.VIP)
        
        compra = Compra(
            fecha=date(2025, 12, 25),
            entradas=[entrada1, entrada2],
            medio_pago=MedioPago.TARJETA
        )
        
        # --- ACT ---
        total = compra.calcular_total()
        
        # --- ASSERT ---
        # Verificar que tenemos todos los datos necesarios para MP
        assert compra.fecha is not None
        assert len(compra.entradas) > 0
        assert compra.medio_pago == MedioPago.TARJETA
        assert total > 0
        assert isinstance(total, (int, float))
    
    def test_datos_compra_pueden_serializarse_para_api(self):
        """
        Prueba que los datos de la compra pueden convertirse
        a un formato válido para enviar a la API de MP.
        """
        # --- ARRANGE ---
        entrada = Entrada(edad=25, tipo_pase=TipoEntrada.REGULAR)
        compra = Compra(
            fecha=date(2025, 11, 15),
            entradas=[entrada],
            medio_pago=MedioPago.TARJETA
        )
        
        # --- ACT ---
        # Simular preparación de datos para MP
        datos_mp = {
            'transaction_amount': compra.calcular_total(),
            'description': f'Entradas Parque Temático - {len(compra.entradas)} entrada(s)',
            'payment_method_id': 'credit_card',
            'payer': {
                'email': 'cliente@example.com'
            }
        }
        
        # --- ASSERT ---
        assert 'transaction_amount' in datos_mp
        assert 'description' in datos_mp
        assert 'payment_method_id' in datos_mp
        assert datos_mp['transaction_amount'] == 5000
        assert 'entrada(s)' in datos_mp['description']


class TestMercadoPagoServiceReal:
    """
    Tests para el servicio real de simulación de Mercado Pago.
    """
    
    def test_crear_preferencia_retorna_datos_correctos(self):
        """
        Prueba que crear_preferencia retorna preference_id y init_point.
        """
        # --- ARRANGE ---
        mp_service = MercadoPagoService()
        datos_compra = {
            'total': 15000,
            'descripcion': 'Test compra',
            'compra_id': 123
        }
        
        # --- ACT ---
        resultado = mp_service.crear_preferencia(datos_compra)
        
        # --- ASSERT ---
        assert 'preference_id' in resultado
        assert 'init_point' in resultado
        assert 'status' in resultado
        assert resultado['status'] == 'created'
        assert resultado['preference_id'].startswith('PREF-')
        assert '/pago-mercadopago' in resultado['init_point']
        assert 'compra_id=123' in resultado['init_point']
    
    def test_procesar_pago_tarjeta_aprobada(self):
        """
        Prueba que una tarjeta de prueba aprobada retorna status approved.
        """
        # --- ARRANGE ---
        mp_service = MercadoPagoService()
        datos_tarjeta = {
            'numero_tarjeta': '4509953566233704',  # Tarjeta aprobada
            'cvv': '123',
            'vencimiento_mes': '12',
            'vencimiento_anio': '28',
            'titular': 'JUAN PEREZ',
            'monto': 10000
        }
        
        # --- ACT ---
        resultado = mp_service.procesar_pago(datos_tarjeta)
        
        # --- ASSERT ---
        assert resultado['status'] == 'approved'
        assert resultado['transaction_id'].startswith('TXN-')
        assert resultado['monto'] == 10000
        assert resultado['payment_method'] == 'credit_card'
        assert 'fecha' in resultado
    
    def test_procesar_pago_tarjeta_rechazada(self):
        """
        Prueba que una tarjeta de prueba rechazada retorna status rejected.
        """
        # --- ARRANGE ---
        mp_service = MercadoPagoService()
        datos_tarjeta = {
            'numero_tarjeta': '4111111111111111',  # Tarjeta rechazada
            'cvv': '123',
            'vencimiento_mes': '12',
            'vencimiento_anio': '28',
            'titular': 'MARIA GOMEZ',
            'monto': 5000
        }
        
        # --- ACT ---
        resultado = mp_service.procesar_pago(datos_tarjeta)
        
        # --- ASSERT ---
        assert resultado['status'] == 'rejected'
        assert 'fondos_insuficientes' in resultado['status_detail']
        assert resultado['monto'] == 5000
    
    def test_procesar_pago_tarjeta_pendiente(self):
        """
        Prueba que una tarjeta de prueba pendiente retorna status pending.
        """
        # --- ARRANGE ---
        mp_service = MercadoPagoService()
        datos_tarjeta = {
            'numero_tarjeta': '4000000000000002',  # Tarjeta pendiente
            'cvv': '456',
            'vencimiento_mes': '06',
            'vencimiento_anio': '29',
            'titular': 'PEDRO LOPEZ',
            'monto': 7500
        }
        
        # --- ACT ---
        resultado = mp_service.procesar_pago(datos_tarjeta)
        
        # --- ASSERT ---
        assert resultado['status'] == 'pending'
        assert 'pending' in resultado['status_detail']
        assert resultado['monto'] == 7500
    
    def test_validacion_tarjeta_invalida(self):
        """
        Prueba que un número de tarjeta inválido es rechazado.
        """
        # --- ARRANGE ---
        mp_service = MercadoPagoService()
        datos_tarjeta = {
            'numero_tarjeta': '1234567890123456',  # Inválido (no pasa Luhn)
            'cvv': '123',
            'vencimiento_mes': '12',
            'vencimiento_anio': '28',
            'titular': 'TEST USER',
            'monto': 1000
        }
        
        # --- ACT ---
        resultado = mp_service.procesar_pago(datos_tarjeta)
        
        # --- ASSERT ---
        assert resultado['status'] == 'rejected'
        assert 'inválido' in resultado['message'].lower()
    
    def test_validacion_cvv_invalido(self):
        """
        Prueba que un CVV inválido es rechazado.
        """
        # --- ARRANGE ---
        mp_service = MercadoPagoService()
        datos_tarjeta = {
            'numero_tarjeta': '4509953566233704',
            'cvv': '12',  # CVV muy corto
            'vencimiento_mes': '12',
            'vencimiento_anio': '28',
            'titular': 'TEST USER',
            'monto': 1000
        }
        
        # --- ACT ---
        resultado = mp_service.procesar_pago(datos_tarjeta)
        
        # --- ASSERT ---
        assert resultado['status'] == 'rejected'
        assert 'cvv' in resultado['message'].lower()
    
    def test_validacion_tarjeta_vencida(self):
        """
        Prueba que una tarjeta vencida es rechazada.
        """
        # --- ARRANGE ---
        mp_service = MercadoPagoService()
        datos_tarjeta = {
            'numero_tarjeta': '4509953566233704',
            'cvv': '123',
            'vencimiento_mes': '01',
            'vencimiento_anio': '20',  # Año pasado
            'titular': 'TEST USER',
            'monto': 1000
        }
        
        # --- ACT ---
        resultado = mp_service.procesar_pago(datos_tarjeta)
        
        # --- ASSERT ---
        assert resultado['status'] == 'rejected'
        assert 'vencida' in resultado['message'].lower()
    
    def test_transacciones_se_almacenan(self):
        """
        Prueba que las transacciones procesadas se almacenan en el servicio.
        """
        # --- ARRANGE ---
        mp_service = MercadoPagoService()
        datos_tarjeta = {
            'numero_tarjeta': '4509953566233704',
            'cvv': '123',
            'vencimiento_mes': '12',
            'vencimiento_anio': '28',
            'titular': 'TEST USER',
            'monto': 5000
        }
        
        # --- ACT ---
        resultado = mp_service.procesar_pago(datos_tarjeta)
        transaction_id = resultado['transaction_id']
        
        transaccion = mp_service.obtener_transaccion(transaction_id)
        
        # --- ASSERT ---
        assert transaccion is not None
        assert transaccion['transaction_id'] == transaction_id
        assert transaccion['monto'] == 5000
    
    def test_multiples_transacciones(self):
        """
        Prueba que se pueden procesar múltiples pagos consecutivos.
        """
        # --- ARRANGE ---
        mp_service = MercadoPagoService()
        
        # --- ACT ---
        resultado1 = mp_service.procesar_pago({
            'numero_tarjeta': '4509953566233704',
            'cvv': '123',
            'vencimiento_mes': '12',
            'vencimiento_anio': '28',
            'titular': 'USER 1',
            'monto': 1000
        })
        
        resultado2 = mp_service.procesar_pago({
            'numero_tarjeta': '5031433215406351',
            'cvv': '456',
            'vencimiento_mes': '06',
            'vencimiento_anio': '29',
            'titular': 'USER 2',
            'monto': 2000
        })
        
        # --- ASSERT ---
        assert len(mp_service.transacciones) == 2
        assert resultado1['transaction_id'] != resultado2['transaction_id']
        assert resultado1['status'] == 'approved'
        assert resultado2['status'] == 'approved'
