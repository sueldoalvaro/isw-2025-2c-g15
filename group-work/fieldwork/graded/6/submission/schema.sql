-- ---------------------------------
-- Tabla de Usuarios
-- Guarda la información de quién compra
-- ---------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    email     TEXT    NOT NULL UNIQUE,
    nombre    TEXT
);

-- ---------------------------------
-- Tabla de Compras
-- Guarda la transacción (el "ticket" general)
-- ---------------------------------
CREATE TABLE IF NOT EXISTS compras (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Key: Vincula esta compra con un usuario
    id_usuario    INTEGER NOT NULL, 
    
    -- Tu idea de 'fecha' (cuándo van al parque)
    fecha_visita  TEXT NOT NULL,
    
    -- Tu idea de 'fechaHora' (cuándo se hizo la compra)
    -- Nota: SQLite datetime('now') devuelve UTC. Usamos 'localtime' para hora local por defecto en nuevas DBs.
    fecha_compra  TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    
    -- Tu idea de 'medio de pago'
    medio_pago    TEXT,
    
    -- Campo de resumen útil (del test original)
    cantidad      INTEGER NOT NULL,
    
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
);

-- ---------------------------------
-- Tabla de Entradas
-- Guarda cada entrada individual de una compra
-- ---------------------------------
CREATE TABLE IF NOT EXISTS entradas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Key: Vincula esta entrada con una compra
    id_compra     INTEGER NOT NULL,
    
    -- Tu idea de 'edad'
    edad          INTEGER NOT NULL,
    
    -- Tu idea de 'tipoEntrada'
    tipo_entrada  TEXT NOT NULL,
    
    FOREIGN KEY (id_compra) REFERENCES compras (id)
);