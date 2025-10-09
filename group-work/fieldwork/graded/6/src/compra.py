from src.servicio_mp import procesar_pago_mp, enviar_mail_confirmacion

class Compra():
    def __init__(self):
        self.precio_unitario = 1000  


    def comprar(self, fecha, cantidad, edades, metodo_pago, email):
        if metodo_pago == 'tarjeta':
            monto_total = self.precio_unitario * cantidad
            datos_tarjeta = {
                'numero': '1234-5678-9012-3456',
                'vencimiento': '12/25',
                'cvv': '123'
            }
            codigo_transaccion = procesar_pago_mp(monto_total, datos_tarjeta)

            if codigo_transaccion:
                detalles_compra = {
                    'fecha': fecha,
                    'cantidad': cantidad,
                    'edades': edades,
                    'monto_total': monto_total
                }
                enviar_mail_confirmacion(email, detalles_compra)
        