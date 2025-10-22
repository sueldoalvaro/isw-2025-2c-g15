import sqlite3
from datetime import datetime

class Parque:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def realizar_compra(self, *, id_usuario: int, datos_formulario: dict) -> int:
        """
        Persiste una compra y sus entradas.


        """
        # Validación y extracción de datos del formulario
        try:
            fecha_visita = datos_formulario["fecha"]
            cantidad = int(datos_formulario["cantidad"])
            edades = datos_formulario["edades"]
            medio_pago = datos_formulario["medioPago"]
            
            # Aceptar lista de tipos O un solo tipo
            if "tiposPase" in datos_formulario:
                tipos_pase = datos_formulario["tiposPase"]
            elif "tipoPase" in datos_formulario:
                # Compatibilidad: si viene un solo tipo, repetirlo para todas
                tipos_pase = [datos_formulario["tipoPase"]] * cantidad
            else:
                raise KeyError("tiposPase o tipoPase")
                
        except KeyError as e:
            raise ValueError(f"Faltan datos en la compra: {e}")

        if cantidad != len(edades):
            raise ValueError("La cantidad de entradas no coincide con el número de edades.")
        
        if cantidad != len(tipos_pase):
            raise ValueError("La cantidad de entradas no coincide con el número de tipos de pase.")

        # Inserciones en DB según schema.sql
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            # Validar que el usuario existe
            from api.utils import UsuarioNoRegistradoError
            cur.execute("SELECT id FROM usuarios WHERE id = ?", (id_usuario,))
            if cur.fetchone() is None:
                raise UsuarioNoRegistradoError(f"El usuario con id {id_usuario} no está registrado en el sistema")

            # A) Insertar compra (forzando fecha_compra en horario local del sistema para evitar desfase UTC)
            # Usamos astimezone() que devuelve la hora local sin requerir base IANA (funciona en Windows)
            try:
                ahora_local = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                # Fallback simple si algo falla
                ahora_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cur.execute(
                """
                INSERT INTO compras (id_usuario, fecha_visita, fecha_compra, cantidad, medio_pago)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id_usuario, fecha_visita, ahora_local, cantidad, medio_pago),
            )
            id_compra = cur.lastrowid

            # B) Insertar entradas (con tipo individual por entrada)
            cur.executemany(
                """
                INSERT INTO entradas (id_compra, edad, tipo_entrada)
                VALUES (?, ?, ?)
                """,
                [(id_compra, int(edad), tipo_pase) for edad, tipo_pase in zip(edades, tipos_pase)],
            )
            return id_compra

    def consultar_compras_por_usuario(self, *, id_usuario: int):
        """Devuelve todas las compras del usuario dado (lista)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM compras WHERE id_usuario = ? ORDER BY id ASC",
                (id_usuario,),
            )
            filas = cur.fetchall()
        # Retornamos lista de dicts para conveniencia (tests solo usan len)
        return [dict(f) for f in filas]