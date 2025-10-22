import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailService:
    """
    Servicio de envío de emails usando SMTP.
    Configurado para trabajar con Gmail por defecto.
    """
    
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587, 
                 sender_email=None, sender_password=None):
        """
        Inicializa el servicio de email.
        
        Args:
            smtp_server: Servidor SMTP (default: Gmail)
            smtp_port: Puerto SMTP (default: 587 para TLS)
            sender_email: Email del remitente
            sender_password: Contraseña o App Password del remitente
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def enviar_confirmacion(self, compra, destinatario_email: str) -> bool:
        """
        Envía un email de confirmación de compra.
        
        Args:
            compra: Objeto Compra con la información de la compra
            destinatario_email: Email del destinatario
            
        Returns:
            bool: True si se envió correctamente, False en caso contrario
            
        Raises:
            ValueError: Si faltan credenciales de email
            Exception: Si ocurre un error en el envío
        """
        if not self.sender_email or not self.sender_password:
            raise ValueError("Credenciales de email no configuradas")
        
        try:
            # Construir el mensaje
            mensaje = MIMEMultipart("alternative")
            mensaje["Subject"] = "Confirmación de Compra - Parque Temático"
            mensaje["From"] = self.sender_email
            mensaje["To"] = destinatario_email
            
            # Construir el cuerpo del email
            cuerpo_texto = self._construir_cuerpo_email(compra)
            cuerpo_html = self._construir_cuerpo_html(compra)
            
            # Agregar ambas versiones (texto plano y HTML)
            parte_texto = MIMEText(cuerpo_texto, "plain")
            parte_html = MIMEText(cuerpo_html, "html")
            
            mensaje.attach(parte_texto)
            mensaje.attach(parte_html)
            
            # Enviar el email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Iniciar conexión segura
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, destinatario_email, mensaje.as_string())
            
            return True
            
        except Exception as e:
            print(f"Error al enviar email: {str(e)}")
            raise
    
    def _construir_cuerpo_email(self, compra) -> str:
        """Construye el cuerpo del email en texto plano."""
        total = compra.calcular_total()
        fecha_compra = compra.fechaHora_compra.strftime("%d/%m/%Y %H:%M")
        fecha_visita = compra.fecha.strftime("%d/%m/%Y")
        
        cuerpo = f"""
¡Gracias por tu compra!

Confirmación de Compra - Parque Temático
========================================

Fecha de compra: {fecha_compra}
Fecha de visita: {fecha_visita}
Cantidad de entradas: {len(compra.entradas)}
Medio de pago: {compra.medio_pago.name}

Detalle de entradas:
"""
        
        for i, entrada in enumerate(compra.entradas, 1):
            precio = entrada.calcular_precio()
            cuerpo += f"\n  {i}. Edad: {entrada.edad} años - {entrada.tipo_pase.name} - ${precio:,.0f}"
        
        cuerpo += f"\n\nTOTAL: ${total:,.0f}\n"
        cuerpo += "\n¡Te esperamos en el parque!\n"
        cuerpo += "\nSaludos,\nEquipo Parque Temático"
        
        return cuerpo
    
    def _construir_cuerpo_html(self, compra) -> str:
        """Construye el cuerpo del email en HTML."""
        total = compra.calcular_total()
        fecha_compra = compra.fechaHora_compra.strftime("%d/%m/%Y %H:%M")
        fecha_visita = compra.fecha.strftime("%d/%m/%Y")
        
        # Construir filas de entradas
        filas_entradas = ""
        for i, entrada in enumerate(compra.entradas, 1):
            precio = entrada.calcular_precio()
            filas_entradas += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{i}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{entrada.edad} años</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{entrada.tipo_pase.name}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${precio:,.0f}</td>
                </tr>
            """
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4299e1; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background-color: #f7fafc; padding: 20px; }}
                    .info {{ margin: 15px 0; }}
                    .info-label {{ font-weight: bold; color: #2c5282; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                    th {{ background-color: #2c5282; color: white; padding: 10px; text-align: left; }}
                    .total {{ background-color: #38a169; color: white; padding: 15px; text-align: right; font-size: 1.2em; font-weight: bold; border-radius: 5px; margin-top: 15px; }}
                    .footer {{ text-align: center; padding: 20px; color: #718096; font-size: 0.9em; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎢 Confirmación de Compra</h1>
                        <p>Parque Temático</p>
                    </div>
                    <div class="content">
                        <p>¡Gracias por tu compra!</p>
                        
                        <div class="info">
                            <span class="info-label">📅 Fecha de compra:</span> {fecha_compra}
                        </div>
                        <div class="info">
                            <span class="info-label">🎫 Fecha de visita:</span> {fecha_visita}
                        </div>
                        <div class="info">
                            <span class="info-label">💳 Medio de pago:</span> {compra.medio_pago.name}
                        </div>
                        
                        <h3>Detalle de entradas:</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Edad</th>
                                    <th>Tipo</th>
                                    <th style="text-align: right;">Precio</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_entradas}
                            </tbody>
                        </table>
                        
                        <div class="total">
                            TOTAL: ${total:,.0f}
                        </div>
                        
                        <p style="margin-top: 20px;">¡Te esperamos en el parque! 🎉</p>
                    </div>
                    <div class="footer">
                        <p>Saludos,<br>Equipo Parque Temático</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html
