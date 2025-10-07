import sqlite3

# Nombre del archivo de base de datos
DB_NAME = "schoolcoin.db"

def crear_tablas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Crear tabla estudiantes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        coins REAL DEFAULT 0
    );
    """)

    # Crear tabla entregas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entregas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_estudiante INTEGER,
        trabajo TEXT,
        coins_asignados REAL DEFAULT 0,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(id_estudiante) REFERENCES estudiantes(id)
    );
    """)

    # Crear tabla examenes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS examenes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_estudiante INTEGER,
        examen TEXT,
        nota REAL DEFAULT 0,
        FOREIGN KEY(id_estudiante) REFERENCES estudiantes(id)
    );
    """)

    conn.commit()
    conn.close()
    print(f"✅ Base de datos '{DB_NAME}' creada con éxito.")

if __name__ == "__main__":
    crear_tablas()
