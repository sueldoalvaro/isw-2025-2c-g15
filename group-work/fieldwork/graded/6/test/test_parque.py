from api.parque import Parque
import pytest
import sqlite3
from unittest.mock import patch
from api.parque import Parque


def test_constructor_parque(parque):
    assert parque.db_path == 'database.db'
    assert isinstance(parque, Parque)

def test_realizar_compra_guarda_en_db(db_test):
    """
    Prueba que el método realizar_compra() guarda
    la compra y las entradas en la DB de forma relacional.
    """
    
    # --- ARRANGE ---
    parque = Parque(db_path=db_test)

    # 2. Prepara los datos: Inserta un usuario de prueba
    id_usuario_test = None
    # ¡ASEGÚRATE DE USAR 'with' AQUÍ!
    with sqlite3.connect(db_test) as conn_setup:
        cursor = conn_setup.cursor()
        cursor.execute("INSERT INTO usuarios (email, nombre) VALUES ('test@user.com', 'Test')")
        id_usuario_test = cursor.lastrowid
        # 'with' cierra y hace commit aquí

    # 3. Define los datos de la compra
    datos_formulario = {
        "fecha": "2025-12-20",
        "cantidad": "2",
        "edades": [30, 8],
        "tipoPase": "REGULAR",
        "medioPago": "TARJETA"
    }

    # --- ACT ---
    # (Este método ya usa 'with' internamente, así que está bien)
    id_compra_generada = parque.realizar_compra(
        id_usuario=id_usuario_test,
        datos_formulario=datos_formulario
    )

    # --- ASSERT ---
    assert id_compra_generada is not None

    # ¡ASEGÚRATE DE USAR 'with' AQUÍ TAMBIÉN!
    with sqlite3.connect(db_test) as conn_assert:
        conn_assert.row_factory = sqlite3.Row
        cursor = conn_assert.cursor()

        # 1. Verificar la tabla 'compras'
        cursor.execute("SELECT * FROM compras WHERE id = ?", (id_compra_generada,))
        compra_db = cursor.fetchone()
        assert compra_db is not None
        assert compra_db['id_usuario'] == id_usuario_test

        # 2. Verificar la tabla 'entradas'
        cursor.execute("SELECT * FROM entradas WHERE id_compra = ?", (id_compra_generada,))
        entradas_db = cursor.fetchall()
        assert len(entradas_db) == 2
    
    

def test_consultar_compras_devuelve_solo_las_del_usuario(db_test):
    """
    Prueba que el método consultar_compras_por_usuario()
    devuelve la lista correcta de compras para un usuario.
    """
    
    # --- ARRANGE ---
    parque = Parque(db_path=db_test)
    
    # 1. Insertamos dos usuarios y sus compras
    # ¡ASEGÚRATE DE USAR 'with' AQUÍ!
    with sqlite3.connect(db_test) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (email, nombre) VALUES ('user_A@test.com', 'Usuario A')")
        id_usuario_A = cur.lastrowid
        
        cur.execute("INSERT INTO usuarios (email, nombre) VALUES ('user_B@test.com', 'Usuario B')")
        id_usuario_B = cur.lastrowid
        
        # 2 compras para Usuario A
        cur.execute(
            "INSERT INTO compras (id_usuario, fecha_visita, cantidad, medio_pago) VALUES (?, ?, ?, ?)",
            (id_usuario_A, '2025-10-01', 2, 'TARJETA')
        )
        cur.execute(
            "INSERT INTO compras (id_usuario, fecha_visita, cantidad, medio_pago) VALUES (?, ?, ?, ?)",
            (id_usuario_A, '2025-10-15', 1, 'EFECTIVO')
        )
        
        # 1 compra para Usuario B
        cur.execute(
            "INSERT INTO compras (id_usuario, fecha_visita, cantidad, medio_pago) VALUES (?, ?, ?, ?)",
            (id_usuario_B, '2025-10-20', 4, 'TARJETA')
        )
        # 'with' cierra y hace commit aquí

    # --- ACT ---
    # (Estos métodos usan 'with' internamente, están bien)
    compras_usuario_A = parque.consultar_compras_por_usuario(id_usuario=id_usuario_A)
    compras_usuario_B = parque.consultar_compras_por_usuario(id_usuario=id_usuario_B)

    # --- ASSERT ---
    assert len(compras_usuario_A) == 2
    assert len(compras_usuario_B) == 1

def test_consultar_compras_usuario_sin_compras_devuelve_lista_vacia(db_test):
    """
    Prueba que el método devuelve una lista vacía
    para un usuario que existe pero no tiene compras.
    """
    
    # --- ARRANGE ---
    parque = Parque(db_path=db_test)
    
    # 1. Insertamos un usuario
    with sqlite3.connect(db_test) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (email, nombre) VALUES ('user_C@test.com', 'Usuario C')")
        id_usuario_C = cur.lastrowid
        
    # (No insertamos compras para este usuario)

    # --- ACT ---
    
    # Consultamos las compras del Usuario C
    compras_usuario_C = parque.consultar_compras_por_usuario(id_usuario=id_usuario_C)

    # --- ASSERT ---
    
    assert isinstance(compras_usuario_C, list)
    assert len(compras_usuario_C) == 0


def test_usuario_no_registrado_no_puede_comprar(db_test):
    """
    Prueba que realizar_compra() lanza UsuarioNoRegistradoError
    cuando se intenta comprar con un id_usuario que no existe en la BD.
    """
    from api.utils import UsuarioNoRegistradoError
    
    # --- ARRANGE ---
    parque = Parque(db_path=db_test)
    
    # NO insertamos ningún usuario en la BD
    # Usamos un id_usuario que claramente no existe
    id_usuario_inexistente = 9999
    
    datos_formulario = {
        "fecha": "2025-12-25",
        "cantidad": "1",
        "edades": [25],
        "tiposPase": ["VIP"],
        "medioPago": "EFECTIVO"
    }

    # --- ACT & ASSERT ---
    # Esperamos que se lance UsuarioNoRegistradoError
    with pytest.raises(UsuarioNoRegistradoError) as exc_info:
        parque.realizar_compra(
            id_usuario=id_usuario_inexistente,
            datos_formulario=datos_formulario
        )
    
    # Verificamos que el mensaje de error sea apropiado
    assert "no está registrado" in str(exc_info.value).lower()