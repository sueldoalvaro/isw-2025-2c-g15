# ...existing code...
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root
INSTANCE = ROOT / 'instance'
DB_PATH = INSTANCE / 'database.db'
SCHEMA = ROOT / 'schema.sql'

def init_db(db_path=DB_PATH, schema_path=SCHEMA, seed_user=True):
    INSTANCE.mkdir(parents=True, exist_ok=True)
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql no encontrado en {schema_path}")
    sql = schema_path.read_text(encoding='utf-8')
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(sql)
        conn.commit()
        print(f"Base de datos (schema) aplicada en: {db_path}")

        if seed_user:
            cur = conn.cursor()
            # Cambia estos datos si querés otro usuario seed
            seed_nombre = "Usuario"
            seed_apellido = "Demo"
            seed_email = "usuario.demo@example.com"
            # INSERT OR IGNORE depende de unique(email)
            cur.execute(
                "INSERT OR IGNORE INTO users (nombre, apellido, email) VALUES (?, ?, ?)",
                (seed_nombre, seed_apellido, seed_email)
            )
            conn.commit()
            print(f"Usuario seed asegurado: {seed_nombre} {seed_apellido} <{seed_email}>")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()