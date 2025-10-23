import sqlite3
import os

def create_database():
    # Remover archivo existente si existe
    if os.path.exists('ventas.db'):
        os.remove('ventas.db')
    
    # Conectar a base de datos SQLite
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    
    # Crear tabla
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY,
        producto TEXT NOT NULL,
        categoria TEXT NOT NULL,
        precio REAL NOT NULL,
        pais TEXT NOT NULL,
        fecha_venta DATE NOT NULL
    )
    ''')
    
    # Insertar data
    ventas_data = [
        (1, 'iPhone 14', 'smartphones', 1300, 'Argentina', '2024-05-10'),
        (2, 'MacBook Air', 'notebooks', 1800, 'Chile', '2024-05-12')
    ]
    
    # Ejectar comando de insertar data
    cursor.executemany('''
    INSERT INTO ventas (id, producto, categoria, precio, pais, fecha_venta)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ventas_data)
    
    # Se realiza Commit a los cambnios
    conn.commit()
    
    # Confirmar que los datos fueron insertados
    cursor.execute('SELECT * FROM ventas')
    rows = cursor.fetchall()
    
    print("Database created successfully!")
    print("\nData in the database:")
    print("id | producto    | categoria   | precio | pais      | fecha_venta")
    print("-" * 60)
    for row in rows:
        print(f"{row[0]:2} | {row[1]:11} | {row[2]:11} | {row[3]:6} | {row[4]:9} | {row[5]}")
    
    # Se cierra la conexión
    conn.close()
    
if __name__ == "__main__":
    create_database()