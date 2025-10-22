from datetime import date
from api.compra import Compra
from api.utils import TipoEntrada, MedioPago
from api.parque import Parque
import pytest
import os
import sqlite3
from api.entrada import Entrada
import pytest

# (Asegúrate de importar tu Enum, ej: from api.enums import TipoPase)

@pytest.fixture
def entrada_factory():
    """
    Esta fixture es una FÁBRICA para crear objetos Entrada.
    Acepta kwargs para sobrescribir los inputs por defecto.
    """
    
    def _crear_entrada(**kwargs_de_input):
        
        # 1. Define los INPUTS por defecto (un adulto regular)
        inputs_por_defecto = {
            "edad": 30,
            "tipo_pase": TipoEntrada.REGULAR
        }
        
        # 2. Sobrescribe los defaults con lo que pidas
        inputs = {**inputs_por_defecto, **kwargs_de_input}

        # 3. Crea la instancia de Entrada
        # (El precio se calculará automáticamente en el constructor)
        return Entrada(
            edad=inputs['edad'],
            tipo_pase=inputs['tipo_pase']
        )

    # La fixture retorna la función interna
    return _crear_entrada

@pytest.fixture
def db_test(tmp_path):
    """
    Fixture unitaria: Crea una DB de prueba en blanco con el schema
    y la limpia después del test.
    """
    # Crea una DB única por test en un directorio temporal de pytest (evita locks en Windows)
    db_path = tmp_path / 'test_unit_parque.db'
    conn = sqlite3.connect(db_path)
    with open('schema.sql', mode='r') as f:
        conn.cursor().executescript(f.read())
    conn.commit()
    conn.close()
    # Entrega la ruta como str
    yield str(db_path)
    # No es necesario borrar manualmente: tmp_path se limpia al terminar el test

@pytest.fixture
def compra_factory():
    """
    Esta fixture es una FÁBRICA para crear Compras.
    Acepta kwargs para sobrescribir los valores por defecto.
    """
    
    def _crear_compra(**kwargs):
        # 1. Define todos los valores por defecto
        datos_por_defecto = {
            "fecha": date(2025, 10, 25),
            "entradas": [
                Entrada(edad=30, tipo_pase=TipoEntrada.REGULAR),
                Entrada(edad=8, tipo_pase=TipoEntrada.REGULAR)
            ],
            "medio_pago": MedioPago.EFECTIVO,  # Un default
        }
        
        # 2. Sobrescribe los defaults con lo que pidas
        datos_finales = {**datos_por_defecto, **kwargs}
        
        return Compra(**datos_finales)

    # 3. La fixture retorna la función interna
    return _crear_compra

@pytest.fixture
def parque():
    return Parque('database.db')