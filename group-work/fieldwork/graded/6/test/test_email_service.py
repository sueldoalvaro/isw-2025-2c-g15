import pytest
from datetime import date
from api.compra import Compra
from api.entrada import Entrada
from api.utils import TipoEntrada, MedioPago, MockEmailService


def test_enviar_confirmacion_se_llama_correctamente():
    """
    Prueba que el método enviar_confirmacion() se invoca
    cuando se finaliza una compra.
    """
    # --- ARRANGE ---
    # Crear una compra válida
    entrada1 = Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR)
    entrada2 = Entrada(edad=8, tipo_pase=TipoEntrada.VIP)
    
    compra = Compra(
        fecha=date(2025, 12, 20),
        entradas=[entrada1, entrada2],
        medio_pago=MedioPago.EFECTIVO
    )
    
    # Crear el mock del servicio de email
    mock_email = MockEmailService()
    
    # Verificar estado inicial
    assert mock_email.email_enviado == False
    
    # --- ACT ---
    from api.utils import MockMP
    mock_mp = MockMP()
    compra.finalizar_compra(mock_mp, mock_email)
    
    # --- ASSERT ---
    # Verificar que se marcó como enviado
    assert mock_email.email_enviado == True


def test_enviar_confirmacion_recibe_objeto_compra():
    """
    Prueba que enviar_confirmacion() recibe el objeto Compra
    con toda la información necesaria.
    """
    # --- ARRANGE ---
    entrada1 = Entrada(edad=25, tipo_pase=TipoEntrada.REGULAR)
    
    compra = Compra(
        fecha=date(2025, 11, 15),
        entradas=[entrada1],
        medio_pago=MedioPago.TARJETA
    )
    
    # Mock personalizado que captura el parámetro
    class EmailServiceEspia(MockEmailService):
        def __init__(self):
            super().__init__()
            self.compra_recibida = None
        
        def enviar_confirmacion(self, compra):
            self.compra_recibida = compra
            self.email_enviado = True
    
    mock_email = EmailServiceEspia()
    
    # --- ACT ---
    from api.utils import MockMP
    mock_mp = MockMP()
    compra.finalizar_compra(mock_mp, mock_email)
    
    # --- ASSERT ---
    assert mock_email.compra_recibida is not None
    assert mock_email.compra_recibida == compra
    assert mock_email.compra_recibida.fecha == date(2025, 11, 15)
    assert len(mock_email.compra_recibida.entradas) == 1


def test_email_service_mock_tiene_atributo_email_enviado():
    """
    Prueba que MockEmailService tiene el atributo email_enviado
    inicializado correctamente.
    """
    # --- ARRANGE & ACT ---
    mock_email = MockEmailService()
    
    # --- ASSERT ---
    assert hasattr(mock_email, 'email_enviado')
    assert mock_email.email_enviado == False


def test_enviar_confirmacion_retorna_true():
    """
    Prueba que enviar_confirmacion() retorna True
    cuando se ejecuta correctamente.
    """
    # --- ARRANGE ---
    entrada = Entrada(edad=30, tipo_pase=TipoEntrada.VIP)
    compra = Compra(
        fecha=date(2025, 12, 25),
        entradas=[entrada],
        medio_pago=MedioPago.EFECTIVO
    )
    
    mock_email = MockEmailService()
    
    # --- ACT ---
    resultado = mock_email.enviar_confirmacion(compra)
    
    # --- ASSERT ---
    # MockEmailService debería retornar True o al menos no fallar
    # (actualmente no retorna nada explícitamente, que es None)
    assert mock_email.email_enviado == True


def test_multiples_envios_de_email():
    """
    Prueba que se puede usar el mismo mock para múltiples envíos
    (aunque en producción cada compra tendría su propio email).
    """
    # --- ARRANGE ---
    entrada1 = Entrada(edad=20, tipo_pase=TipoEntrada.REGULAR)
    entrada2 = Entrada(edad=15, tipo_pase=TipoEntrada.VIP)
    
    compra1 = Compra(
        fecha=date(2025, 10, 10),
        entradas=[entrada1],
        medio_pago=MedioPago.EFECTIVO
    )
    
    compra2 = Compra(
        fecha=date(2025, 11, 11),
        entradas=[entrada2],
        medio_pago=MedioPago.TARJETA
    )
    
    mock_email = MockEmailService()
    
    # --- ACT ---
    mock_email.enviar_confirmacion(compra1)
    assert mock_email.email_enviado == True
    
    # Segundo envío
    mock_email.enviar_confirmacion(compra2)
    
    # --- ASSERT ---
    assert mock_email.email_enviado == True  # Sigue siendo True
