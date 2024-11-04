import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Union
import pandas as pd
from tabulate import tabulate
import math

def crear_conexion() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect('inventario.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise

def crear_tablas():
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Productos (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_producto TEXT,
        precio REAL,
        stock_actual INTEGER DEFAULT 0,
        stock_seguridad INTEGER,
        punto_reorden INTEGER,
        proveedor_id INTEGER,
        clasificacion_abc TEXT,
        eoq INTEGER
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Proveedores (
        id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_proveedor TEXT,
        contacto TEXT,
        telefono TEXT,
        email TEXT,
        pais TEXT,
        tiempo_entrega INTEGER
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Pedidos (
        id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
        id_producto INTEGER,
        cantidad_pedida INTEGER,
        fecha_pedido DATE,
        fecha_entrega DATE,
        estado_pedido TEXT,
        FOREIGN KEY(id_producto) REFERENCES Productos(id_producto)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Historial_Inventario (
        id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
        id_producto INTEGER,
        cantidad INTEGER,
        tipo_movimiento TEXT,
        fecha_movimiento DATE,
        razon TEXT,
        FOREIGN KEY(id_producto) REFERENCES Productos(id_producto)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Demanda_Promedio (
        id_demanda INTEGER PRIMARY KEY AUTOINCREMENT,
        id_producto INTEGER,
        demanda_diaria INTEGER,
        demanda_mensual INTEGER,
        fecha_registro DATE,
        FOREIGN KEY(id_producto) REFERENCES Productos(id_producto)
    )''')

    conn.commit()
    conn.close()



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

    proveedor_id = seleccionar_proveedor()
    
    if proveedor_id is not None:
        conn = crear_conexion()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Proveedores WHERE id_proveedor = ?", (proveedor_id,))
        proveedor = cursor.fetchone()

        if proveedor:
            nombre_producto = obtener_input_valido("Ingrese el nombre del producto: ", str, "Por favor ingrese un nombre válido.")
            if nombre_producto is None: return
            
            demanda_diaria = obtener_input_valido("Ingrese la demanda diaria: ", int, "Por favor ingrese una demanda válida.")
            if demanda_diaria is None: return
            
            tiempo_entrega = proveedor[6]  # Suponiendo que el tiempo de entrega está en la séptima columna
            stock_seguridad = obtener_input_valido("Ingrese el stock de seguridad: ", int, "Por favor ingrese un stock válido.")
            if stock_seguridad is None: return
            
            precio = obtener_input_valido("Ingrese el precio del producto: ", float, "Por favor ingrese un precio válido.")
            if precio is None: return

            punto_reorden = (demanda_diaria * tiempo_entrega) + stock_seguridad
            cursor.execute('''INSERT INTO Productos (nombre_producto, stock_seguridad, punto_reorden, precio, proveedor_id)  
                            VALUES (?, ?, ?, ?, ?)''', (nombre_producto, stock_seguridad, punto_reorden, precio, proveedor_id))

            conn.commit()
            print("Producto agregado correctamente.")
        else:
            print("No se encontró información para este proveedor.")

        conn.close()
    else:
        print("No se pudo agregar el producto debido a un proveedor no válido.")


def insertar_pedido():
    print("\n--- Ingresar Pedido ---")
    
    conn = crear_conexion()
    cursor = conn.cursor()

    # Verificar proveedores
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
    if proveedor_id not in df_proveedores['ID Proveedor'].values:
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
    if producto_id not in df_productos_proveedor['ID Producto'].values:
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
    cursor.execute("SELECT * FROM Pedidos WHERE id_pedido = ? AND estado_pedido = 'Pendiente'", (id_pedido,))
    pedido = cursor.fetchone()

    if not pedido:
        print("Pedido no encontrado o ya fue actualizado.")
        conn.close()
        return

    # Obtener detalles del pedido
    id_producto, cantidad_pedida = pedido[1], pedido[2]

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
    
def verificar_reorden():
    print("\n--- Verificación de Punto de Reorden ---")
    
    conn = crear_conexion()
    cursor = conn.cursor()

    # Consulta para obtener productos con stock actual menor o igual al punto de reorden
    cursor.execute('''
        SELECT id_producto, nombre_producto, stock_actual, punto_reorden
        FROM Productos
        WHERE stock_actual <= punto_reorden
    ''')
    productos_para_reorden = cursor.fetchall()

    # Comprobar si hay productos en estado crítico de reorden
    if productos_para_reorden:
        print("\nProductos que necesitan reordenarse:")
        df_productos = pd.DataFrame(productos_para_reorden, columns=["ID Producto", "Nombre Producto", "Stock Actual", "Punto de Reorden"])
        print(tabulate(df_productos, headers='keys', tablefmt='fancy_grid', showindex=False))
    else:
        print("Todos los productos están por encima de su punto de reorden.")

    conn.close()

def clasificacion_abc():
    print("\n--- Clasificación ABC ---")
    
    conn = crear_conexion()
    cursor = conn.cursor()

    # Consulta para obtener los productos, su demanda mensual y su precio
    cursor.execute('''
        SELECT Pr.id_producto, Pr.nombre_producto, Pr.precio, Dm.demanda_mensual
        FROM Productos Pr
        JOIN Demanda_Promedio Dm ON Pr.id_producto = Dm.id_producto
    ''')
    productos = cursor.fetchall()

    if not productos:
        print("No hay productos ni demanda registrada para realizar la clasificación ABC.")
        conn.close()
        return

    # Calcular el valor anual por producto
    productos_abc = []
    for id_producto, nombre_producto, precio, demanda_mensual in productos:
        valor_anual = precio * demanda_mensual * 12  # Multiplicamos por 12 para tener el valor anual
        productos_abc.append((id_producto, nombre_producto, valor_anual))

    # Ordenar los productos por valor anual de mayor a menor
    productos_abc.sort(key=lambda x: x[2], reverse=True)

    # Calcular el valor total y determinar límites de cada categoría
    valor_total = sum([valor for _, _, valor in productos_abc])
    limite_a = valor_total * 0.8
    limite_b = valor_total * 0.95

    # Clasificar productos en A, B, C
    clasificacion = []
    valor_acumulado = 0
    for id_producto, nombre_producto, valor_anual in productos_abc:
        valor_acumulado += valor_anual
        if valor_acumulado <= limite_a:
            categoria = 'A'
        elif valor_acumulado <= limite_b:
            categoria = 'B'
        else:
            categoria = 'C'
        clasificacion.append((id_producto, nombre_producto, valor_anual, categoria))

    # Mostrar la clasificación
    df_clasificacion = pd.DataFrame(clasificacion, columns=["ID Producto", "Nombre Producto", "Valor Anual", "Categoría"])
    print(tabulate(df_clasificacion, headers='keys', tablefmt='fancy_grid', showindex=False))

    conn.close()
    
def seleccionar_producto():
    conn = crear_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT id_producto, nombre_producto, precio, stock_actual, stock_seguridad, punto_reorden, proveedor_id FROM Productos")
    productos = cursor.fetchall()

    if productos:
        df_productos = pd.DataFrame(productos, columns=["ID Producto", "Nombre Producto", "Precio", "Stock Actual", "Stock Seguridad", "Punto de Reorden", "ID Proveedor"])
        print("\nLista de Productos:")
        print(tabulate(df_productos, headers='keys', tablefmt='fancy_grid', showindex=False))
    else:
        print("No hay productos registrados.")
        return None

    seleccion = obtener_input_valido("Ingrese el ID del producto que desea seleccionar: ", int, "Por favor ingrese un ID válido.")
    if seleccion is not None:
        cursor.execute("SELECT * FROM Productos WHERE id_producto = ?", (seleccion,))
        producto = cursor.fetchone()
        if producto:
            return seleccion
        else:
            print("Producto no encontrado.")
            return None
    return None


def determinar_eoq():
    print("\n--- Determinar EOQ ---")
    
    producto_id = seleccionar_producto()
    if producto_id is None:
        print("No se pudo determinar el EOQ porque no se seleccionó un producto válido.")
        return
    
    # Obtener datos del producto seleccionado
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT stock_seguridad, demanda_mensual FROM Productos Pr JOIN Demanda_Promedio Dm ON Pr.id_producto = Dm.id_producto WHERE Pr.id_producto = ?", (producto_id,))
    datos_producto = cursor.fetchone()
    
    if datos_producto:
        stock_seguridad, demanda_mensual = datos_producto
        demanda_anual = demanda_mensual * 12  # Asumiendo 12 meses de demanda mensual
        costo_pedido = obtener_input_valido("Ingrese el costo de realizar un pedido: ", float, "Por favor ingrese un número válido.")
        costo_mantenimiento = obtener_input_valido("Ingrese el costo de mantener una unidad en inventario: ", float, "Por favor ingrese un número válido.")

        if costo_pedido is not None and costo_mantenimiento is not None:
            eoq = calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento)
            print(f"La cantidad óptima de pedido (EOQ) para el producto seleccionado es: {eoq:.2f} unidades.")
        else:
            print("No se pudieron obtener los valores necesarios para calcular el EOQ.")
    else:
        print("No se encontró información suficiente para el producto seleccionado.")
    conn.close()

def calcular_eoq(demanda_anual, costo_pedido, costo_mantenimiento):
    return math.sqrt((2 * demanda_anual * costo_pedido) / costo_mantenimiento)


def menu_principal():
    crear_tablas()
    while True:
        print("\nMenu Principal:")
        print("1. Agregar nuevo producto")
        print("2. Agregar nuevo pedido")
        print("3. Actualizar inventario")
        print("4. Mostrar historial de inventario")
        print("5. Verificar punto de reorden")
        print("6. Clasificación ABC")
        print("7. Determinar EOQ")
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
            verificar_reorden()
        elif opcion == 6:
            clasificacion_abc()
        elif opcion == 7:
            determinar_eoq()  # Llamar a la función que determina el EOQ
        elif opcion == 8:
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")


if __name__ == "__main__":
    crear_tablas()
    menu_principal()