import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Union
import pandas as pd
from tabulate import tabulate
import math
from math import sqrt

def crear_conexion() -> sqlite3.Connection:
    return sqlite3.connect('inventario.db')

def obtener_input_valido(mensaje: str, tipo_dato: type, mensaje_error: str) -> Optional[Union[str, int, float]]:
    while True:
        entrada = input(mensaje).strip()
        if entrada == '0':
            print("Operación cancelada.")
            return None
        if tipo_dato == str:
            return entrada
        elif tipo_dato == int:
            try:
                return int(entrada)
            except ValueError:
                print(mensaje_error)
        elif tipo_dato == float:
            try:
                return float(entrada)
            except ValueError:
                print(mensaje_error)

def agregar_proveedor(cursor):
    nombre_proveedor = obtener_input_valido("Ingrese el nombre del proveedor: ", str, "Por favor ingrese un nombre válido.")
    if nombre_proveedor is None: return None
    contacto = obtener_input_valido("Ingrese el contacto del proveedor: ", str, "Por favor ingrese un contacto válido.")
    if contacto is None: return None
    telefono = obtener_input_valido("Ingrese el teléfono del proveedor: ", str, "Por favor ingrese un teléfono válido.")
    if telefono is None: return None
    email = obtener_input_valido("Ingrese el email del proveedor: ", str, "Por favor ingrese un email válido.")
    if email is None: return None
    pais = obtener_input_valido("Ingrese el país del proveedor: ", str, "Por favor ingrese un país válido.")
    if pais is None: return None
    tiempo_entrega = obtener_input_valido("Ingrese el tiempo de entrega (días): ", int, "Por favor ingrese un tiempo válido.")
    if tiempo_entrega is None: return None

    cursor.execute('''INSERT INTO Proveedores (nombre, contacto, telefono, email, pais, tiempo_entrega)  
                    VALUES (?, ?, ?, ?, ?, ?)''', (nombre_proveedor, contacto, telefono, email, pais, tiempo_entrega))
    return cursor.lastrowid

def seleccionar_proveedor() -> Optional[int]:
    conn = crear_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM Proveedores")
        proveedores = cursor.fetchall()

        if proveedores:
            df_proveedores = pd.DataFrame(proveedores, columns=["ID Proveedor", "Nombre", "Contacto", "Teléfono", "Email", "País", "Tiempo de Entrega (días)"])
            print("\nLista de Proveedores:")
            print(tabulate(df_proveedores, headers='keys', tablefmt='fancy_grid', showindex=False))
        else:
            print("No hay proveedores registrados.")
            return None

        seleccion = input("\nIngrese el ID del proveedor que desea seleccionar o escriba '//' para agregar uno nuevo: ").strip()

        if seleccion == '//':
            proveedor_id = agregar_proveedor(cursor)
            conn.commit()
            if proveedor_id:
                print("Proveedor agregado correctamente.")
                return proveedor_id
            return None
        else:
            try:
                id_proveedor = int(seleccion)
                cursor.execute("SELECT * FROM Proveedores WHERE id_proveedor = ?", (id_proveedor,))
                proveedor = cursor.fetchone()
                if proveedor:
                    return id_proveedor
                else:
                    print("Proveedor no encontrado.")
                    return None
            except ValueError:
                print("Selección no válida. No se seleccionará ningún proveedor.")
                return None
    finally:
        conn.close()

def insertar_producto():
    print("\n--- Ingresar Producto ---")

    conn = crear_conexion()
    cursor = conn.cursor()
    
    # Verificar si hay proveedores registrados
    cursor.execute("SELECT COUNT(*) FROM Proveedores")
    cantidad_proveedores = cursor.fetchone()[0]
    
    if cantidad_proveedores == 0:
        print("No hay proveedores registrados. Debe agregar un proveedor antes de ingresar un producto.")
        proveedor_id = agregar_proveedor(cursor)
        conn.commit()
        if proveedor_id:
            print("Proveedor agregado correctamente.")
        else:
            print("No se pudo agregar un proveedor. No se ingresará el producto.")
            conn.close()
            return
    
    conn.close()  # Cerrar la conexión temporal
    proveedor_id = seleccionar_proveedor()  # Selección de proveedor
    
    if proveedor_id is not None:
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT tiempo_entrega FROM Proveedores WHERE id_proveedor = ?", (proveedor_id,))
        tiempo_entrega = cursor.fetchone()[0]

        # Obtener datos del producto
        nombre_producto = obtener_input_valido("Ingrese el nombre del producto: ", str, "Por favor ingrese un nombre válido.")
        if nombre_producto is None: return
        
        demanda_diaria = obtener_input_valido("Ingrese la demanda diaria: ", int, "Por favor ingrese una demanda válida.")
        if demanda_diaria is None: return
        
        precio = obtener_input_valido("Ingrese el precio del producto: ", float, "Por favor ingrese un precio válido.")
        if precio is None: return

        costo_pedido = obtener_input_valido("Ingrese el costo de pedido: ", float, "Por favor ingrese un costo de pedido válido.")
        if costo_pedido is None: return
        
        costo_mantenimiento = obtener_input_valido("Ingrese el costo de mantenimiento: ", float, "Por favor ingrese un costo de mantenimiento válido.")
        if costo_mantenimiento is None: return

        # Calcular los valores derivados
        stock_seguridad = int(demanda_diaria * 0.2)
        punto_reorden = (demanda_diaria * tiempo_entrega) + stock_seguridad
        demanda_anual = demanda_diaria * 365

        # Calcular el EOQ
        eoq = calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento)
        if eoq is None:
            print("Los valores ingresados para el cálculo de EOQ son inválidos.")
            conn.close()
            return

        # Clasificación ABC
        clasificacion_abc = 'A' if precio * demanda_anual > 50000 else ('B' if precio * demanda_anual > 10000 else 'C')

        # Inserción en la tabla Productos
        cursor.execute('''INSERT INTO Productos (nombre_producto, stock_seguridad, punto_reorden, precio, proveedor_id, 
                            stock_actual, clasificacion_abc, eoq, costo_pedido, costo_mantenimiento)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                    (nombre_producto, stock_seguridad, punto_reorden, precio, proveedor_id, 0, clasificacion_abc, eoq, costo_pedido, costo_mantenimiento))
        conn.commit()

        # Obtener el ID del producto recién insertado
        id_producto = cursor.lastrowid

        # Insertar la demanda mensual en la tabla Demanda_Promedio
        cursor.execute('''INSERT INTO Demanda_Promedio (id_producto, demanda_diaria, demanda_mensual, fecha_registro)
                        VALUES (?, ?, ?, ?)''', 
                    (id_producto, demanda_diaria, demanda_diaria * 30, datetime.now().strftime('%Y-%m-%d')))
        
        # Insertar los costos en la tabla Costos
        cursor.execute('''INSERT INTO Costos (id_producto, costo_pedido, costo_mantenimiento)
                        VALUES (?, ?, ?)''', 
                    (id_producto, costo_pedido, costo_mantenimiento))
        
        conn.commit()
        
        print("Producto agregado correctamente.")
        conn.close()

    else:
        print("No se pudo agregar el producto debido a un proveedor no válido.")

def verificar_existencia(cursor, tabla, campo_id, valor_id):
    cursor.execute(f"SELECT 1 FROM {tabla} WHERE {campo_id} = ?", (valor_id,))
    return cursor.fetchone() is not None

def insertar_pedido():
    print("\n--- Ingresar Pedido ---")
    
    conn = crear_conexion()
    cursor = conn.cursor()

    # Verificar si existen proveedores
    cursor.execute("SELECT * FROM Proveedores")
    proveedores = cursor.fetchall()

    if not proveedores:
        print("No hay proveedores registrados.")
        conn.close()
        return

    # Mostrar proveedores
    df_proveedores = pd.DataFrame(proveedores, columns=["ID Proveedor", "Nombre", "Contacto", "Teléfono", "Email", "País", "Tiempo de Entrega (días)"])
    print("\nProveedores disponibles:")
    print(tabulate(df_proveedores, headers='keys', tablefmt='fancy_grid', showindex=False))

    # Seleccionar el proveedor
    proveedor_id = obtener_input_valido("Ingrese el ID del proveedor al que desea pedir: ", int, "Por favor ingrese un ID válido.")
    if not verificar_existencia(cursor, "Proveedores", "id_proveedor", proveedor_id):
        print("Proveedor no encontrado. Operación cancelada.")
        conn.close()
        return

    # Obtener productos del proveedor seleccionado
    cursor.execute('''
        SELECT Pr.id_producto, Pr.nombre_producto 
        FROM Productos Pr
        WHERE Pr.proveedor_id = ?
    ''', (proveedor_id,))
    productos_proveedor = cursor.fetchall()

    if not productos_proveedor:
        print("No hay productos asociados a este proveedor.")
        conn.close()
        return

    # Mostrar productos del proveedor
    df_productos_proveedor = pd.DataFrame(productos_proveedor, columns=["ID Producto", "Nombre Producto"])
    print("\nProductos disponibles del proveedor seleccionado:")
    print(tabulate(df_productos_proveedor, headers='keys', tablefmt='fancy_grid', showindex=False))

    # Seleccionar el producto
    producto_id = obtener_input_valido("Ingrese el ID del producto que desea seleccionar: ", int, "Por favor ingrese un ID válido.")
    if not verificar_existencia(cursor, "Productos", "id_producto", producto_id):
        print("Producto no encontrado. Operación cancelada.")
        conn.close()
        return

    # Capturar cantidad y fecha del pedido
    cantidad_pedida = obtener_input_valido("Ingrese la cantidad que desea pedir: ", int, "Por favor ingrese una cantidad válida.")
    fecha_pedido = datetime.now()
    
    # Calcular fecha de entrega
    fecha_entrega = fecha_pedido + timedelta(days=5)

    # Convertir fechas a formato de cadena
    fecha_pedido_str = fecha_pedido.strftime('%Y-%m-%d')
    fecha_entrega_str = fecha_entrega.strftime('%Y-%m-%d')

    cursor.execute('''INSERT INTO Pedidos (id_producto, cantidad_pedida, fecha_pedido, fecha_entrega, estado_pedido)  
                    VALUES (?, ?, ?, ?, ?)''', (producto_id, cantidad_pedida, fecha_pedido_str, fecha_entrega_str, 'Pendiente'))

    conn.commit()
    conn.close()
    print("Pedido agregado correctamente.")

def actualizar_inventario():
    print("\n--- Actualizar Inventario en Base a Pedidos ---")
    
    conn = crear_conexion()
    cursor = conn.cursor()

    # Obtener pedidos pendientes
    cursor.execute('''
        SELECT Pe.id_pedido, Pe.id_producto, Pr.nombre_producto, Pe.cantidad_pedida, Pe.fecha_pedido, Pe.fecha_entrega, Pe.estado_pedido 
        FROM Pedidos Pe
        JOIN Productos Pr ON Pe.id_producto = Pr.id_producto
        WHERE Pe.estado_pedido = 'Pendiente'
    ''')
    pedidos = cursor.fetchall()

    if not pedidos:
        print("No hay pedidos pendientes para actualizar el inventario.")
        conn.close()
        return

    # Mostrar los pedidos pendientes
    df_pedidos = pd.DataFrame(pedidos, columns=["ID Pedido", "ID Producto", "Nombre Producto", "Cantidad Pedida", "Fecha Pedido", "Fecha Entrega", "Estado"])
    print("\nPedidos Pendientes:")
    print(tabulate(df_pedidos, headers='keys', tablefmt='fancy_grid', showindex=False))

    # Seleccionar un pedido para actualizar inventario
    id_pedido = obtener_input_valido("Ingrese el ID del pedido que desea confirmar: ", int, "Por favor ingrese un ID válido.")

    # Verificar si el pedido existe y está pendiente
    if not verificar_existencia(cursor, "Pedidos", "id_pedido", id_pedido):
        print("Pedido no encontrado o ya fue actualizado.")
        conn.close()
        return

    # Obtener detalles del pedido
    cursor.execute("SELECT id_producto, cantidad_pedida FROM Pedidos WHERE id_pedido = ? AND estado_pedido = 'Pendiente'", (id_pedido,))
    pedido = cursor.fetchone()
    id_producto, cantidad_pedida = pedido[0], pedido[1]

    # Actualizar el inventario del producto con la cantidad pedida
    cursor.execute("UPDATE Productos SET stock_actual = stock_actual + ? WHERE id_producto = ?", (cantidad_pedida, id_producto))

    # Marcar el pedido como completado
    cursor.execute("UPDATE Pedidos SET estado_pedido = 'Completado' WHERE id_pedido = ?", (id_pedido,))

    # Insertar movimiento en el historial
    fecha_movimiento = datetime.now().date()
    cursor.execute('''INSERT INTO Historial_Inventario (id_producto, cantidad, tipo_movimiento, fecha_movimiento, razon)
                    VALUES (?, ?, ?, ?, ?)''', (id_producto, cantidad_pedida, "Entrada", fecha_movimiento, "Pedido recibido"))

    conn.commit()
    conn.close()
    print("Inventario actualizado correctamente con el pedido seleccionado.")

def mostrar_historial_inventario():
    conn = crear_conexion()
    cursor = conn.cursor()

    # Obtener todos los productos y sus proveedores
    cursor.execute('''
        SELECT P.id_producto, P.nombre_producto, Pr.nombre_proveedor 
        FROM Productos P
        JOIN Proveedores Pr ON P.proveedor_id = Pr.id_proveedor
    ''')
    productos = cursor.fetchall()

    if productos:
        df_productos = pd.DataFrame(productos, columns=["ID Producto", "Nombre Producto", "Proveedor"])
        print("\nLista de Productos y Proveedores:")
        print(tabulate(df_productos, headers='keys', tablefmt='fancy_grid', showindex=False))
    else:
        print("No hay productos registrados.")
        conn.close()
        return

    # Solicitar ID del producto
    id_producto = obtener_input_valido("Ingrese el ID del producto para mostrar el historial: ", int, "Por favor ingrese un ID válido.")

    # Consultar el historial de movimientos del producto
    cursor.execute('''SELECT * FROM Historial_Inventario WHERE id_producto = ? ORDER BY fecha_movimiento DESC''', (id_producto,))
    historial = cursor.fetchall()

    if historial:
        df_historial = pd.DataFrame(historial, columns=["ID Historial", "ID Producto", "Cantidad", "Tipo Movimiento", "Fecha Movimiento", "Razón"])
        print("\nHistorial de Movimientos:")
        print(tabulate(df_historial, headers='keys', tablefmt='fancy_grid', showindex=False))
    else:
        print("No hay movimientos registrados para este producto.")

    conn.close()
    
def calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento):
    """Calcular el EOQ (Economic Order Quantity) con la fórmula básica"""
    if demanda_anual > 0 and costo_pedido > 0 and costo_mantenimiento > 0:
        return math.sqrt((2 * demanda_anual * costo_pedido) / costo_mantenimiento)
    else:
        return None  # Si algún parámetro es 0 o negativo, no calculamos el EOQ

def verificar_y_clasificar_productos():
    print("\n--- Verificación de Punto de Reorden, EOQ y Clasificación ABC ---")

    conn = crear_conexion()
    cursor = conn.cursor()

    # Obtener productos con stock, demanda mensual, y costos asociados
    cursor.execute(''' 
        SELECT Pr.id_producto, Pr.nombre_producto, Pr.precio, Pr.stock_actual, Pr.punto_reorden, 
            Dm.demanda_mensual, Pr.stock_seguridad, C.costo_pedido, C.costo_mantenimiento
        FROM Productos Pr
        LEFT JOIN Demanda_Promedio Dm ON Pr.id_producto = Dm.id_producto
        LEFT JOIN Costos C ON Pr.id_producto = C.id_producto
    ''')
    productos = cursor.fetchall()
    
    if not productos:
        print("No hay productos o demanda registrada para realizar la verificación y clasificación.")
        conn.close()
        return

    # Procesar cada producto y calcular valores adicionales
    productos_data = []
    for id_producto, nombre, precio, stock_actual, punto_reorden, demanda_mensual, stock_seguridad, costo_pedido, costo_mantenimiento in productos:
        # Asegurarse de que los costos no sean NULL
        costo_pedido = costo_pedido if costo_pedido is not None else 100  # Valor por defecto
        costo_mantenimiento = costo_mantenimiento if costo_mantenimiento is not None else 10  # Valor por defecto
        
        # Cálculo de demanda anual (si la demanda es válida)
        demanda_anual = (demanda_mensual * 12) if demanda_mensual else 0
        
        # Calcular valor anual
        valor_anual = round(precio * demanda_anual, 2)  # Redondear el valor anual a dos decimales
        
        # Verificación de reorden
        necesita_reorden = "Sí" if stock_actual is not None and punto_reorden is not None and stock_actual <= punto_reorden else "No"

        # Calcular EOQ si hay demanda anual válida
        eoq = None
        if demanda_anual > 0:  # Solo calcular si la demanda anual es válida
            eoq = calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento)

        productos_data.append((id_producto, nombre, precio, stock_actual, valor_anual, stock_seguridad, punto_reorden, necesita_reorden, eoq))

    # Clasificar productos por valor anual para el análisis ABC
    productos_data.sort(key=lambda x: x[4], reverse=True)  # Ordenar por valor_anual
    valor_total = sum([producto[4] for producto in productos_data])
    limite_a, limite_b = valor_total * 0.8, valor_total * 0.95

    # Clasificación ABC
    valor_acumulado = 0
    clasificacion = []
    for producto in productos_data:
        id_producto, nombre, precio, stock_actual, valor_anual, stock_seguridad, punto_reorden, necesita_reorden, eoq = producto
        valor_acumulado += valor_anual
        if valor_acumulado <= limite_a:
            categoria = 'A'
        elif valor_acumulado <= limite_b:
            categoria = 'B'
        else:
            categoria = 'C'

        clasificacion.append((id_producto, nombre, precio, stock_actual, valor_anual, categoria, eoq, punto_reorden, necesita_reorden))

    # Crear DataFrame con las columnas en el orden adecuado
    columnas = ["ID Producto", "Nombre Producto", "Precio", "Stock Actual", "Valor Anual", "Categoría ABC", "EOQ", "Punto de Reorden", "Reorden Necesario"]
    df_productos = pd.DataFrame(clasificacion, columns=columnas)

    # Mostrar la tabla con formato adecuado
    print(tabulate(df_productos, headers='keys', tablefmt='fancy_grid', showindex=False))
    conn.close()



def mostrar_clasificacion_abc():
    print("\n--- Clasificación ABC de Productos ---")

    conn = crear_conexion()
    cursor = conn.cursor()

    # Obtener productos con stock y demanda mensual
    cursor.execute('''
        SELECT Pr.id_producto, Pr.nombre_producto, Pr.precio, Pr.stock_actual, 
            Dm.demanda_mensual
        FROM Productos Pr
        LEFT JOIN Demanda_Promedio Dm ON Pr.id_producto = Dm.id_producto
    ''')
    productos = cursor.fetchall()

    if not productos:
        print("No hay productos o demanda registrada para realizar la clasificación ABC.")
        conn.close()
        return

    # Procesar datos básicos
    productos_data = []
    for id_producto, nombre, precio, stock_actual, demanda_mensual in productos:
        valor_anual = (precio * demanda_mensual * 12) if demanda_mensual else 0
        productos_data.append((id_producto, nombre, precio, stock_actual, valor_anual))

    # Ordenar productos por valor anual para clasificación ABC
    productos_data.sort(key=lambda x: x[4], reverse=True)  # Índice 4 corresponde a valor_anual
    valor_total = sum([producto[4] for producto in productos_data])
    limite_a, limite_b = valor_total * 0.8, valor_total * 0.95

    # Clasificar productos
    clasificacion = []
    valor_acumulado = 0
    for producto in productos_data:
        id_producto, nombre, precio, stock_actual, valor_anual = producto
        valor_acumulado += valor_anual
        if valor_acumulado <= limite_a:
            categoria = 'A'
        elif valor_acumulado <= limite_b:
            categoria = 'B'
        else:
            categoria = 'C'
        clasificacion.append((id_producto, nombre, precio, stock_actual, valor_anual, categoria))

    # Crear DataFrame y mostrar la tabla de clasificación
    columnas = ["ID Producto", "Nombre Producto", "Precio", "Stock Actual", "Valor Anual", "Categoría ABC"]
    df_clasificacion = pd.DataFrame(clasificacion, columns=columnas)
    print(tabulate(df_clasificacion, headers='keys', tablefmt='fancy_grid', showindex=False))
    conn.close()
    

def calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento):
    # Fórmula EOQ: sqrt((2 * demanda * costo_pedido) / costo_mantenimiento)
    return round(sqrt((2 * demanda_anual * costo_pedido) / costo_mantenimiento), 0)

# Función para mostrar los datos de EOQ
def mostrar_datos_eoq():
    print("\n--- Datos para Cálculo de EOQ ---")

    conn = crear_conexion()
    cursor = conn.cursor()

    # Obtener productos y costos asociados (con un LEFT JOIN para no perder productos sin demanda o costos)
    cursor.execute('''
        SELECT Pr.id_producto, Pr.nombre_producto, Pr.precio, Dm.demanda_mensual, C.costo_pedido, C.costo_mantenimiento
        FROM Productos Pr
        LEFT JOIN Demanda_Promedio Dm ON Pr.id_producto = Dm.id_producto
        LEFT JOIN Costos C ON Pr.id_producto = C.id_producto
    ''')
    productos = cursor.fetchall()

    if not productos:
        print("No hay productos o costos registrados para realizar el cálculo de EOQ.")
        conn.close()
        return

    # Procesar los productos y calcular el EOQ
    datos_eoq = []
    for id_producto, nombre, precio, demanda_mensual, costo_pedido, costo_mantenimiento in productos:
        # Verificar si la demanda mensual y los costos no son nulos
        if demanda_mensual is not None and costo_pedido is not None and costo_mantenimiento is not None:
            demanda_anual = demanda_mensual * 12  # Convertir la demanda mensual a anual
            eoq = calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento)
            datos_eoq.append((id_producto, nombre, precio, demanda_mensual, eoq))
        else:
            print(f"Faltan datos para el producto '{nombre}' (ID: {id_producto}). No se puede calcular EOQ.")

    # Crear DataFrame con los datos procesados
    columnas = ["ID Producto", "Nombre Producto", "Precio", "Demanda Mensual", "EOQ"]
    df_datos_eoq = pd.DataFrame(datos_eoq, columns=columnas)

    # Mostrar la tabla de datos para EOQ
    if not df_datos_eoq.empty:
        print(tabulate(df_datos_eoq, headers='keys', tablefmt='fancy_grid', showindex=False))
    else:
        print("No hay productos con datos completos para calcular EOQ.")

    conn.close()

# Agrega estas opciones al menú principal
def menu_principal():
    while True:
        print("\nMenu Principal:")
        print("1. Agregar nuevo producto")
        print("2. Agregar nuevo pedido")
        print("3. Actualizar inventario")
        print("4. Mostrar historial de inventario")
        print("5. Verificar y clasificar productos")
        print("6. Mostrar clasificación ABC")
        print("7. Mostrar datos para EOQ")
        print("8. Salir")

        opcion = obtener_input_valido("Seleccione una opción: ", int, "Por favor ingrese una opción válida.")

        if opcion == 1:
            insertar_producto()
        elif opcion == 2:
            insertar_pedido()
        elif opcion == 3:
            actualizar_inventario()
        elif opcion == 4:
            mostrar_historial_inventario()
        elif opcion == 5:
            verificar_y_clasificar_productos()
        elif opcion == 6:
            mostrar_clasificacion_abc()
        elif opcion == 7:
            mostrar_datos_eoq()
        elif opcion == 8:
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    
    menu_principal()

#Script adicional que se puede usar en otro archivo en la misma carpeta para hacer pruebas en el codigo
"""
import sqlite3
import random
from datetime import datetime, timedelta

# Función para crear la conexión con la base de datos
def crear_conexion() -> sqlite3.Connection:
    return sqlite3.connect('inventario.db')

# Crear las tablas necesarias en la base de datos
def crear_tablas():
    conn = crear_conexion()
    cursor = conn.cursor()
    
    # Crear tabla Proveedores
    cursor.execute('''CREATE TABLE IF NOT EXISTS Proveedores (
                        id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_proveedor TEXT,
                        contacto TEXT,
                        telefono TEXT,
                        email TEXT,
                        pais TEXT,
                        tiempo_entrega INTEGER
                    )''')

    # Crear tabla Productos
    cursor.execute('''CREATE TABLE IF NOT EXISTS Productos (
                        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_producto TEXT,
                        precio REAL,
                        stock_actual INTEGER,
                        stock_seguridad INTEGER,
                        punto_reorden INTEGER,
                        proveedor_id INTEGER,
                        clasificacion_abc TEXT,
                        eoq INTEGER,
                        costo_pedido REAL,
                        costo_mantenimiento REAL,
                        FOREIGN KEY(proveedor_id) REFERENCES Proveedores(id_proveedor)
                    )''')

    # Crear tabla Pedidos
    cursor.execute('''CREATE TABLE IF NOT EXISTS Pedidos (
                        id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_producto INTEGER,
                        cantidad_pedida INTEGER,
                        fecha_pedido DATE,
                        fecha_entrega DATE,
                        estado_pedido TEXT,
                        FOREIGN KEY(id_producto) REFERENCES Productos(id_producto)
                    )''')

    # Crear tabla Historial_Inventario
    cursor.execute('''CREATE TABLE IF NOT EXISTS Historial_Inventario (
                        id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_producto INTEGER,
                        cantidad INTEGER,
                        tipo_movimiento TEXT,
                        fecha_movimiento DATE,
                        razon TEXT,
                        FOREIGN KEY(id_producto) REFERENCES Productos(id_producto)
                    )''')

    # Crear tabla Demanda_Promedio
    cursor.execute('''CREATE TABLE IF NOT EXISTS Demanda_Promedio (
                        id_demanda INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_producto INTEGER,
                        demanda_diaria INTEGER,
                        demanda_mensual INTEGER,
                        fecha_registro DATE,
                        FOREIGN KEY(id_producto) REFERENCES Productos(id_producto)
                    )''')

    # Crear tabla Costos
    cursor.execute('''CREATE TABLE IF NOT EXISTS Costos (
                        id_producto INTEGER PRIMARY KEY,
                        costo_pedido REAL NOT NULL,
                        costo_mantenimiento REAL NOT NULL,
                        FOREIGN KEY(id_producto) REFERENCES Productos(id_producto)
                    )''')

    conn.commit()
    conn.close()

# Calcular EOQ (Cantidad Económica de Pedido)
def calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento):
    if demanda_anual > 0 and costo_pedido > 0 and costo_mantenimiento > 0:
        return int(((2 * demanda_anual * costo_pedido) / costo_mantenimiento) ** 0.5)
    return None

# Función para insertar datos de prueba
def insertar_datos_prueba():
    crear_tablas()  # Asegurarse de que las tablas existan

    conn = crear_conexion()
    cursor = conn.cursor()

    # Insertar proveedores de prueba
    proveedores = [
        ('Proveedor A', 'Juan Perez', '555-1234', 'juan@proveedora.com', 'México', 3),
        ('Proveedor B', 'Maria Lopez', '555-5678', 'maria@proveedorb.com', 'Estados Unidos', 5)
    ]
    cursor.executemany('''INSERT INTO Proveedores (nombre_proveedor, contacto, telefono, email, pais, tiempo_entrega)  
                        VALUES (?, ?, ?, ?, ?, ?)''', proveedores)

    # Insertar productos de prueba
    productos = [
        ('Hamburguesa Clásica', 50.0, 10, 5, 15, 1, 'A', 20),
        ('Hamburguesa Doble', 75.0, 5, 3, 10, 1, 'A', 30),
        ('Hamburguesa Vegana', 65.0, 20, 5, 15, 2, 'B', 25)
    ]
    
    # Insertar productos, pero primero calcular el EOQ dinámicamente para cada producto
    for nombre_producto, precio, stock_actual, stock_seguridad, punto_reorden, proveedor_id, clasificacion_abc, eoq in productos:
        # Calcular la demanda anual como 365 veces la demanda diaria (ficticia para los datos de prueba)
        demanda_diaria = stock_seguridad  # Solo un valor de ejemplo
        demanda_anual = demanda_diaria * 365  # Calculamos la demanda anual
        costo_pedido = 50  # Valor ficticio de ejemplo
        costo_mantenimiento = 5  # Valor ficticio de ejemplo
        
        # Calcular el EOQ para cada producto
        eoq_calculado = calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento)

        # Insertar producto en la base de datos
        cursor.execute('''INSERT INTO Productos (nombre_producto, precio, stock_actual, stock_seguridad, punto_reorden, proveedor_id, 
                            clasificacion_abc, eoq, costo_pedido, costo_mantenimiento)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (nombre_producto, precio, stock_actual, stock_seguridad, punto_reorden, proveedor_id, 
                        clasificacion_abc, eoq_calculado, costo_pedido, costo_mantenimiento))

    # Insertar pedidos de prueba
    for _ in range(3):
        id_producto = random.randint(1, 3)
        cantidad_pedida = random.randint(1, 10)
        fecha_pedido = datetime.now().date()
        fecha_entrega = fecha_pedido + timedelta(days=random.randint(1, 7))
        estado_pedido = 'Pendiente'

        cursor.execute('''INSERT INTO Pedidos (id_producto, cantidad_pedida, fecha_pedido, fecha_entrega, estado_pedido)  
                VALUES (?, ?, ?, ?, ?)''', (id_producto, cantidad_pedida, fecha_pedido, fecha_entrega, estado_pedido))

    # Insertar demanda promedio de prueba
    demandas = [
        (1, 3, 90, '2024-01-01'),
        (2, 2, 60, '2024-01-01'),
        (3, 5, 150, '2024-01-01')
    ]
    cursor.executemany('''INSERT INTO Demanda_Promedio (id_producto, demanda_diaria, demanda_mensual, fecha_registro)  
                        VALUES (?, ?, ?, ?)''', demandas)

    # Insertar costos de prueba
    costos = [
        (1, 50, 5),
        (2, 45, 6),
        (3, 40, 4)
    ]
    cursor.executemany('''INSERT INTO Costos (id_producto, costo_pedido, costo_mantenimiento)  
                        VALUES (?, ?, ?)''', costos)

    conn.commit()
    conn.close()
    print("Datos de prueba insertados correctamente.")

# Ejecutar la función para insertar los datos de prueba
if __name__ == "__main__":
    insertar_datos_prueba()

"""
