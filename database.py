import sqlite3

DB_PATH = 'control_minutos.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        club TEXT NOT NULL,
        categoria TEXT NOT NULL,
        letra TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS jugadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS partidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo_id INTEGER NOT NULL,
        rival TEXT NOT NULL,
        fecha TEXT NOT NULL,
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS minutos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partido_id INTEGER NOT NULL,
        jugador_id INTEGER NOT NULL,
        minutos INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (partido_id) REFERENCES partidos(id),
        FOREIGN KEY (jugador_id) REFERENCES jugadores(id)
    )''')

    conn.commit()
    conn.close()