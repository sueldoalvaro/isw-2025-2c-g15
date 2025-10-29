-- ...existing code...

-- Tabla de usuarios (seedable)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

-- Tabla de compras básicas para el TP6
CREATE TABLE IF NOT EXISTS compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,               -- YYYY-MM-DD
    cantidad INTEGER NOT NULL,
    tipo_pase TEXT NOT NULL,           -- 'regular'|'vip'
    metodo_pago TEXT NOT NULL,         -- 'efectivo'|'tarjeta'
    monto_total INTEGER NOT NULL,
    email TEXT,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    created_at TEXT DEFAULT (datetime('now'))
);

-- Tabla de tickets (detalles por persona)
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    compra_id INTEGER NOT NULL,
    nombre TEXT,
    edad INTEGER,
    FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE
);