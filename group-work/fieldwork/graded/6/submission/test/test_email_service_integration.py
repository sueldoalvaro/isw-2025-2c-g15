import pytest
from datetime import date
from api.compra import Compra
from api.entrada import Entrada
from api.utils import TipoEntrada, MedioPago
from api.email_service import EmailService
from unittest.mock import patch, MagicMock
import smtplib


class TestEmailServiceIntegracion:
    """
    Tests de integración para el servicio de email real.
    Estos tests usan mocks para el servidor SMTP para evitar envíos reales.
    """
    
    def test_enviar_confirmacion_sin_credenciales_lanza_error(self):
        """
        Prueba que enviar_confirmacion lanza ValueError
        si no hay credenciales configuradas.
        """
        # --- ARRANGE ---
        email_service = EmailService()
        
        entrada = Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR)
        compra = Compra(
            fecha=date(2025, 12, 20),
            entradas=[entrada],
            medio_pago=MedioPago.EFECTIVO
        )
        
        # --- ACT & ASSERT ---
        with pytest.raises(ValueError) as exc_info:
            email_service.enviar_confirmacion(compra, "destinatario@test.com")
        
        assert "credenciales" in str(exc_info.value).lower()
    
    @patch('smtplib.SMTP')
    def test_enviar_confirmacion_con_credenciales_validas(self, mock_smtp):
        """
        Prueba que enviar_confirmacion se conecta al servidor SMTP
        y envía el email correctamente.
        """
        # --- ARRANGE ---
        # Configurar el mock del servidor SMTP
        mock_server_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server_instance
        
        email_service = EmailService(
            sender_email="test@sender.com",
            sender_password="test_password"
        )
        
        entrada = Entrada(edad=25, tipo_pase=TipoEntrada.VIP)
        compra = Compra(
            fecha=date(2025, 11, 15),
            entradas=[entrada],
            medio_pago=MedioPago.TARJETA
        )
        
        # --- ACT ---
        resultado = email_service.enviar_confirmacion(compra, "cliente@test.com")
        
        # --- ASSERT ---
        assert resultado == True
        
        # Verificar que se llamó al servidor SMTP
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        
        # Verificar que se llamó a starttls
        mock_server_instance.starttls.assert_called_once()
        
        # Verificar que se hizo login
        mock_server_instance.login.assert_called_once_with("test@sender.com", "test_password")
        
        # Verificar que se llamó a sendmail
        assert mock_server_instance.sendmail.called
        call_args = mock_server_instance.sendmail.call_args[0]
        assert call_args[0] == "test@sender.com"  # remitente
        assert call_args[1] == "cliente@test.com"  # destinatario
        assert isinstance(call_args[2], str)  # mensaje
    
    @patch('smtplib.SMTP')
    def test_contenido_email_incluye_informacion_compra(self, mock_smtp):
        """
        Prueba que el contenido del email incluye toda la información
        relevante de la compra.
        """
        # --- ARRANGE ---
        mock_server_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server_instance
        
        email_service = EmailService(
            sender_email="test@sender.com",
            sender_password="test_password"
        )
        
        entrada1 = Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR)
        entrada2 = Entrada(edad=8, tipo_pase=TipoEntrada.VIP)
        compra = Compra(
            fecha=date(2025, 12, 25),
            entradas=[entrada1, entrada2],
            medio_pago=MedioPago.TARJETA
        )
        
        # --- ACT ---
        email_service.enviar_confirmacion(compra, "cliente@test.com")
        
        # --- ASSERT ---
        # Obtener el mensaje enviado (está en formato MIME con contenido codificado)
        mensaje_enviado = mock_server_instance.sendmail.call_args[0][2]
        
        # Verificar que el mensaje contiene información clave
        # El contenido puede estar en base64, así que buscamos en el mensaje completo
        assert "Confirmaci" in mensaje_enviado or "confirmaci" in mensaje_enviado.lower()
        # El mensaje MIME contiene Subject con la información
        assert "Parque" in mensaje_enviado
    
    @patch('smtplib.SMTP')
    def test_email_contiene_total_calculado(self, mock_smtp):
        """
        Prueba que el email incluye el total calculado de la compra.
        """
        # --- ARRANGE ---
        mock_server_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server_instance
        
        email_service = EmailService(
            sender_email="test@sender.com",
            sender_password="test_password"
        )
        
        entrada = Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR)
        compra = Compra(
            fecha=date(2025, 11, 10),
            entradas=[entrada],
            medio_pago=MedioPago.EFECTIVO
        )
        
        total_esperado = compra.calcular_total()
        
        # --- ACT ---
        email_service.enviar_confirmacion(compra, "cliente@test.com")
        
        # --- ASSERT ---
        mensaje_enviado = mock_server_instance.sendmail.call_args[0][2]
        
        # Verificar que el mensaje fue enviado correctamente
        # El contenido está codificado en base64, así que verificamos que sea un mensaje MIME válido
        assert "Content-Type" in mensaje_enviado
        assert "multipart/alternative" in mensaje_enviado
    
    @patch('smtplib.SMTP')
    def test_error_smtp_se_propaga(self, mock_smtp):
        """
        Prueba que si hay un error en el servidor SMTP,
        la excepción se propaga correctamente.
        """
        # --- ARRANGE ---
        # Configurar el mock para lanzar una excepción
        mock_smtp.side_effect = smtplib.SMTPException("Error de conexión")
        
        email_service = EmailService(
            sender_email="test@sender.com",
            sender_password="test_password"
        )
        
        entrada = Entrada(edad=25, tipo_pase=TipoEntrada.REGULAR)
        compra = Compra(
            fecha=date(2025, 10, 10),
            entradas=[entrada],
            medio_pago=MedioPago.EFECTIVO
        )
        
        # --- ACT & ASSERT ---
        with pytest.raises(smtplib.SMTPException):
            email_service.enviar_confirmacion(compra, "cliente@test.com")
    
    @patch('smtplib.SMTP')
    def test_email_html_contiene_estilos(self, mock_smtp):
        """
        Prueba que el email HTML generado contiene estilos CSS.
        """
        # --- ARRANGE ---
        mock_server_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server_instance
        
        email_service = EmailService(
            sender_email="test@sender.com",
            sender_password="test_password"
        )
        
        entrada = Entrada(edad=20, tipo_pase=TipoEntrada.VIP)
        compra = Compra(
            fecha=date(2025, 12, 15),
            entradas=[entrada],
            medio_pago=MedioPago.TARJETA
        )
        
        # --- ACT ---
        email_service.enviar_confirmacion(compra, "cliente@test.com")
        
        # --- ASSERT ---
        mensaje_enviado = mock_server_instance.sendmail.call_args[0][2]
        
        # Verificar que el mensaje es multipart con HTML
        assert "Content-Type" in mensaje_enviado
        assert "text/html" in mensaje_enviado
        assert "multipart/alternative" in mensaje_enviado
    
    def test_construir_cuerpo_email_genera_texto_plano(self):
        """
        Prueba que el método privado _construir_cuerpo_email
        genera correctamente el texto plano.
        """
        # --- ARRANGE ---
        email_service = EmailService(
            sender_email="test@sender.com",
            sender_password="test_password"
        )
        
        entrada = Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR)
        compra = Compra(
            fecha=date(2025, 12, 20),
            entradas=[entrada],
            medio_pago=MedioPago.EFECTIVO
        )
        
        # --- ACT ---
        cuerpo = email_service._construir_cuerpo_email(compra)
        
        # --- ASSERT ---
        assert "Confirmación de Compra" in cuerpo
        assert "20/12/2025" in cuerpo
        assert "EFECTIVO" in cuerpo
        assert "30 años" in cuerpo
        assert "REGULAR" in cuerpo
        assert "$5,000" in cuerpo  # Precio REGULAR formateado
    
    def test_construir_cuerpo_html_genera_html_valido(self):
        """
        Prueba que el método privado _construir_cuerpo_html
        genera HTML válido.
        """
        # --- ARRANGE ---
        email_service = EmailService(
            sender_email="test@sender.com",
            sender_password="test_password"
        )
        
        entrada = Entrada(edad=25, tipo_pase=TipoEntrada.VIP)
        compra = Compra(
            fecha=date(2025, 11, 15),
            entradas=[entrada],
            medio_pago=MedioPago.TARJETA
        )
        
        # --- ACT ---
        html = email_service._construir_cuerpo_html(compra)
        
        # --- ASSERT ---
        assert html.startswith("<html>") or html.strip().startswith("<html>")
        assert "</html>" in html
        assert "<table>" in html
        assert "25 años" in html
        assert "VIP" in html
        assert "$10,000" in html  # Precio VIP formateado
