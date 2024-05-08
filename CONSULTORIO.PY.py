from sqlite3 import Error
from tabulate import tabulate
import datetime
import sqlite3
import pandas as pd
import sys


try:

    with sqlite3.connect('Base_de_datos_clinica', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as conn:
        cursor = conn.cursor()

        cursor.execute('''
CREATE TABLE IF NOT EXISTS pacientes (
    clave_paciente INTEGER PRIMARY KEY,
    primer_apellido TEXT NOT NULL,
    segundo_apellido TEXT,
    nombre TEXT NOT NULL,
    fecha_nacimiento timestamp NOT NULL,
    edad_paciente INTEGER NOT NULL,
    sexo TEXT NOT NULL
)''')

        cursor.execute('''
CREATE TABLE IF NOT EXISTS citas (
    folio_cita INTEGER PRIMARY KEY AUTOINCREMENT,
    clave_paciente INTEGER,
    fecha_cita timestamp NOT NULL,
    turno TEXT NOT NULL,
    estado TEXT NOT NULL,
    FOREIGN KEY(clave_paciente) REFERENCES pacientes(clave_paciente)
)''')
        cursor.execute('''
CREATE TABLE IF NOT EXISTS citas_realizadas (
    folio_cita INTEGER PRIMARY KEY,
    clave_paciente INTEGER,
    hora_de_llegada timestamp NOT NULL,
    peso FLOAT,
    estatura FLOAT,
    presion_sistolica INTEGER,
    presion_diastolica INTEGER,
    diagnostico TEXT,
    FOREIGN KEY(folio_cita) REFERENCES citas(folio_cita),
    FOREIGN KEY(clave_paciente) REFERENCES pacientes(clave_paciente)
)''')


except Error as e:
    print(f"Error al trabajar con la base de datos: {e}")

except Exception as e:
    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
finally:
    conn.close()


def menu_principal():
    while True:
        print("\nMENÚ PRINCIPAL")
        print("1. Registro de paciente")
        print("2. Citas")
        print("3. Consultas y reportes")
        print("4. Salir")
        try:
            opcion = int(input("Seleccione una opción (1/2/3/4): "))
            if opcion not in [1, 2, 3, 4]:
                raise ValueError("Opción no válida")
            if opcion == 1:
                registrar_paciente()
            elif opcion == 2:
                menu_citas()
            elif opcion == 3:
                menu_consultas_y_reportes()
                pass
            elif opcion == 4:
                confirmar_salida()
                break
        except ValueError as e:
            print(f"{e}. Por favor, ingrese un número válido (1/2/3/4).")

def confirmar_salida():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = conn.cursor()

        while True:
            try:
                confirmacion = input("¿Está seguro de que desea salir? (S/N) o escriba 0 para cancelar la operación: ").strip().upper()

                if confirmacion in ['S', 'N']:
                    if confirmacion == 'S':
                        print("Guardando datos y saliendo del sistema...")
                        conn.close()  
                        exit()
                    else:
                        print("Salida cancelada. Volviendo al menú principal.")
                        return menu_principal()
                elif confirmacion == '0':
                    print("Operación cancelada. Volviendo al menú principal.")
                    return menu_principal()
                else:
                    raise ValueError("Entrada inválida")
            except ValueError as e:
                print(f"{e}. Por favor, ingrese 'S' para salir, 'N' para continuar o '0' para cancelar la operación.")

    except Error as e:
        print(f"Error al trabajar con la base de datos: {e}")

def registrar_paciente():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = conn.cursor()

        while True:
            try:
                primer_apellido = input("Ingrese el primer apellido del paciente o escriba 0 para cancelar: ").strip().capitalize()
                if primer_apellido == "0":
                    print("Saliendo del área de registrar pacientes...")
                    return menu_principal()

                if not primer_apellido.isalpha():
                    raise ValueError("El primer apellido solo puede contener letras. O escribe 0 para cancelar.")
                break
            except ValueError as e:
                print(f"Error: {e}. Intente de nuevo o escriba 0 para cancelar.")

        while True:
            try:
                segundo_apellido = input("Ingrese el segundo apellido del paciente (opcional) o escriba 0 para cancelar: ").strip().capitalize()
                if segundo_apellido == "0":
                    print("Saliendo del área de registrar pacientes...")
                    return menu_principal()

                if segundo_apellido and not segundo_apellido.isalpha():
                    raise ValueError("El segundo apellido solo puede contener letras o puede dejarse en blanco. O escribe 0 para cancelar.")
                break
            except ValueError as e:
                print(f"Error: {e}. Intente de nuevo o escriba 0 para cancelar.")

        while True:
            try:
                nombre = input("Ingrese el nombre del paciente o escriba 0 para cancelar: ").strip().capitalize()
                if nombre == "0":
                    print("Saliendo del área de registrar pacientes...")
                    return menu_principal()

                if not nombre.isalpha():
                    raise ValueError("El nombre solo puede contener letras. O escribe 0 para cancelar.")
                break
            except ValueError as e:
                print(f"Error: {e}. Intente de nuevo o escriba 0 para cancelar.")

        while True:
            try:
                fecha_nacimiento_str = input("Ingrese la fecha de nacimiento (MM/DD/YYYY) o escriba 0 para cancelar: ").strip()
                if fecha_nacimiento_str == "0":
                    print("Saliendo del área de registrar pacientes...")
                    return

                fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento_str, "%m/%d/%Y").date()
                if fecha_nacimiento >= datetime.date.today():
                    raise ValueError("La fecha de nacimiento debe ser anterior a la fecha actual. O escribe 0 para cancelar.")
                edad = (datetime.date.today() - fecha_nacimiento).days // 365
                break
            except ValueError as e:
                print(f"Error: {e}. Intente de nuevo o escriba 0 para cancelar.")

        while True:
            try:
                sexo = input("Ingrese el sexo del paciente (H/M/N) o escriba 0 para cancelar: ").strip().upper()
                if sexo == "0":
                    print("Saliendo del área de registrar pacientes...")
                    return menu_principal()
                if sexo not in ["H", "M", "N"]:
                    raise ValueError("Sexo inválido. Debe ser H, M, o N. O escribe 0 para cancelar.")
                sexo_desc = {'H': 'Hombre', 'M': 'Mujer', 'N': 'No contestó'}[sexo]
                break
            except ValueError as e:
                print(f"Error: {e}. Intente de nuevo o escriba 0 para cancelar.")

        valores = (primer_apellido, segundo_apellido, nombre, fecha_nacimiento, edad, sexo_desc)
        cursor.execute('''
            INSERT INTO pacientes (primer_apellido, segundo_apellido, nombre, fecha_nacimiento, edad_paciente, sexo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', valores)
        conn.commit() 

    except Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        if conn:
            conn.close()


def menu_citas():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(clave_paciente) FROM pacientes")
            count = cursor.fetchone()[0]

            if count == 0:
                print("No hay pacientes registrados. Por favor, registre pacientes antes de programar citas.")
                conn.close()
                return

        except Error as e:
            print(f"Error al verificar pacientes: {e}")
            conn.close()
            return

        while True:
            print("\nMENÚ DE CITAS")
            print("1. Programar cita")
            print("2. Realización de citas programadas")
            print("3. Cancelar cita")
            print("4. Volver al menú principal")

            try:
                opcion = int(input("Seleccione una opción (1/2/3/4): "))
                if opcion not in [1, 2, 3, 4]:
                    raise ValueError("Opción no válida")

                if opcion == 1:
                    programar_cita()
                elif opcion == 2:
                    realizar_cita()
                elif opcion == 3:
                    menu_cancelacion_citas()
                elif opcion == 4:
                    return menu_principal()

            except ValueError:
                print(f"Opción no válida. Intente de nuevo.")

    except Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        conn.close()

def programar_cita():
    while True:
        try:
            with sqlite3.connect('Base_de_datos_clinica', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM pacientes")
                if cursor.fetchone()[0] == 0:
                    print("No hay pacientes registrados. Por favor, registre pacientes antes de programar citas.")
                    return menu_citas()

                while True:
                    try:
                        cursor.execute("SELECT clave_paciente, nombre || ' ' || primer_apellido || ' ' || COALESCE(segundo_apellido, '') AS nombre_completo FROM pacientes")
                        pacientes = cursor.fetchall()

                        if not pacientes:
                            print("No hay pacientes registrados.")
                            return menu_citas()

                        headers_pacientes = ["Clave del Paciente", "Nombre Completo"]
                        print("Pacientes registrados:")
                        print(tabulate(pacientes, headers=headers_pacientes, tablefmt="fancy_grid"))

                        clave_paciente_id = int(input("Ingrese la clave del paciente o escriba 0 para cancelar: "))
                        if clave_paciente_id == 0:
                            print("Saliendo del área de programar citas...")
                            return menu_citas()

                        cursor.execute("SELECT COUNT(*) FROM pacientes WHERE clave_paciente = ?", (clave_paciente_id,))
                        paciente_existe = cursor.fetchone()[0]

                        if paciente_existe == 0:
                            raise ValueError("La clave del paciente no existe. Por favor, registre al paciente primero. O escribe 0 para cancelar.")
                        break
                    except ValueError as e:
                        print(f"Error: {e}. Intente de nuevo o escriba 0 para cancelar.")

                while True:
                    fecha_cita_str = input("Ingrese la fecha de la cita (MM/DD/YYYY) o escriba 0 para cancelar: ")
                    if fecha_cita_str == "0":
                        print("Saliendo del área de programar citas...")
                        return menu_citas()

                    try:
                        fecha_cita = datetime.datetime.strptime(fecha_cita_str, "%m/%d/%Y").date()

                        hoy = datetime.datetime.today().date()

                        if fecha_cita <= hoy:
                            print("La fecha de la cita debe ser posterior a la fecha actual. O escribe 0 para cancelar.")
                            continue

                        if hoy.weekday() == 5 and fecha_cita == hoy + datetime.timedelta(days=1):
                            print("No se puede programar una cita para el domingo si hoy es sábado.")
                            proximo_lunes = hoy + datetime.timedelta(days=2)
                            print(f"Por favor, seleccione una fecha a partir del siguiente lunes: {proximo_lunes.strftime('%m/%d/%Y')}")
                            continue

                        if fecha_cita.weekday() == 6:  
                            print("No se pueden programar citas para los domingos.")
                            reprogramar = input("¿Desea programar la cita para el sábado siguiente? (S/N) o escriba 0 para cancelar: ").strip().upper()
                            while reprogramar not in ['S', 'N', '0']:
                                print("Valor no válido. Por favor, ingrese 'S' para sí, 'N' para no o '0' para cancelar.")
                                reprogramar = input("¿Desea programar la cita para el sábado siguiente? (S/N) o escriba 0 para cancelar: ").strip().upper()
                            if reprogramar == "S":
                                fecha_cita = fecha_cita - datetime.timedelta(days=1)
                            elif reprogramar == "0":
                                print("Operación cancelada.")
                                return menu_citas()
                            else:
                                continue

                        elif fecha_cita > hoy + datetime.timedelta(days=60):
                            print("La cita no puede programarse para más de 60 días en el futuro.")
                            continue

                        print(f"Fecha programada correctamente para el {fecha_cita.strftime('%m/%d/%Y')}")

                        break
                    except ValueError:
                        print("Fecha de cita inválida. Intente de nuevo o escriba 0 para cancelar.")

                turnos = {1: "mañana", 2: "mediodía", 3: "tarde"}
                while True:
                    try:
                        turno = int(input("Ingrese el turno de la cita (1: mañana / 2: mediodía / 3: tarde) o escriba 0 para cancelar: "))
                        if turno == 0:
                            print("Saliendo del área de programar citas...")
                            return menu_citas()
                        if turno not in turnos or turno <= 0:
                            print("Turno inválido. Intente de nuevo o escriba 0 para cancelar.")
                            continue

                        turno_desc = turnos[turno]
                        break
                    except ValueError:
                        print("El turno debe ser un número entero positivo (1, 2, o 3). Intente de nuevo o escriba 0 para cancelar.")

                try:
                    valores = (clave_paciente_id, fecha_cita, turno_desc, "pendiente")
                    cursor.execute('''
                        INSERT INTO citas (clave_paciente, fecha_cita, turno, estado)
                        VALUES (?, ?, ?, ?)
                    ''', valores)
                    conn.commit()

                    folio_cita_id = cursor.lastrowid 
                    print(f"Cita programada con éxito. Folio de la cita: {folio_cita_id}")
                    return menu_citas()

                except Error as e:
                    print(f"Error al trabajar con la base de datos: {e}")

        except Exception as e:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def realizar_cita():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM citas WHERE estado = 'pendiente'")
        if cursor.fetchone()[0] == 0:
            print("No hay citas pendientes por realizar.")
            return menu_citas()

        while True:
            try:
                cursor.execute("""
                    SELECT p.clave_paciente, p.nombre || ' ' || p.primer_apellido || ' ' || COALESCE(p.segundo_apellido, '') AS nombre_completo
                    FROM pacientes p
                    JOIN citas c ON p.clave_paciente = c.clave_paciente
                    WHERE c.estado = 'pendiente'
                """)
                pacientes = cursor.fetchall()

                if not pacientes:
                    print("No hay pacientes con citas pendientes por realizar.")
                    return menu_citas()

                headers_pacientes = ["Clave del Paciente", "Nombre Completo"]
                print("Pacientes con citas pendientes por realizar:")
                print(tabulate(pacientes, headers=headers_pacientes, tablefmt="fancy_grid"))

                clave_paciente = int(input("Ingrese la clave del paciente o escriba 0 para cancelar: "))
                if clave_paciente == 0:
                    print("Saliendo del área de realizar citas...")
                    return menu_citas()

                cursor.execute("SELECT COUNT(*) FROM pacientes WHERE clave_paciente = ?", (clave_paciente,))
                paciente_existe = cursor.fetchone()[0]
                if paciente_existe == 0:
                    print(f"No se encontró un paciente con la clave {clave_paciente}. O escribe 0 para cancelar.")
                    continue
                break
            except ValueError:
                print("Clave inválida. Intente de nuevo o escribe 0 para cancelar.")

        cursor.execute("""
            SELECT folio_cita, fecha_cita, turno 
            FROM citas 
            WHERE clave_paciente = ? AND estado = 'pendiente'
        """, (clave_paciente,))
        citas = cursor.fetchall()

        if not citas:
            print(f"No hay citas pendientes para el paciente {clave_paciente}.")
            return

        print("Citas pendientes del paciente:")
        print(tabulate(citas, headers=["Folio de Cita", "Fecha de Cita", "Turno"], tablefmt="fancy_grid"))

        while True:
            try:
                folio_cita_id = int(input("Ingrese el folio de la cita o escriba 0 para cancelar: "))
                if folio_cita_id == 0:
                    print("Saliendo del área de realizar citas...")
                    return menu_citas()

                cursor.execute("SELECT * FROM citas WHERE folio_cita = ? AND estado = 'pendiente'", (folio_cita_id,))
                cita = cursor.fetchone()

                if not cita:
                    print(f"No se encontró una cita pendiente con el folio {folio_cita_id}. O escribe 0 para cancelar.")
                    continue
                break
            except ValueError:
                print("Folio inválido. Intente de nuevo o escribe 0 para cancelar.")

        folio_cita_id, clave_paciente_id, fecha_cita, turno, estado = cita
        hora_llegada = datetime.datetime.now().strftime('%H:%M:%S')

        print(f"Detalles de la cita:\nFolio: {folio_cita_id}\nPaciente ID: {clave_paciente_id}\nFecha: {fecha_cita}\nHora de llegada: {hora_llegada}\nTurno: {turno}")

        while True:
            try:
                peso = float(input("Ingrese el peso del paciente: "))
                if peso <= 0:
                    raise ValueError("El peso debe ser positivo. O escribe 0 para cancelar.")
                break
            except ValueError as e:
                print(f"Error: {e}. Intente de nuevo o escribe 0 para cancelar.")

        while True:
            try:
                estatura = float(input("Ingrese la estatura del paciente: "))
                if estatura <= 0:
                    raise ValueError("La estatura debe ser positiva. O escribe 0 para cancelar.")
                break
            except ValueError as e:
                print(f"Error: {e}. Intente de nuevo o escribe 0 para cancelar.")

        while True:
            try:
                presion_sistolica = int(input("Ingrese la presión sistólica: "))
                if presion_sistolica <= 0:
                    raise ValueError("La presión sistólica debe ser positiva. O escribe 0 para cancelar.")
                break
            except ValueError as e:
                print(f"Error: {e}. Intente de nuevo o escribe 0 para cancelar.")

        while True:
            try:
                presion_diastolica = int(input("Ingrese la presión diastólica: "))
                if presion_diastolica <= 0:
                    raise ValueError("La presión diastólica debe ser positiva. O escribe 0 para cancelar.")
                break
            except ValueError as e:
                print(f"Error: {e}. Intente de nuevo o escribe 0 para cancelar.")

        while True:
            diagnostico = input("Ingrese el diagnóstico (máximo 200 caracteres) o escriba 0 para cancelar: ")
            if diagnostico == "0":
                print("Saliendo del área de realizar citas...")
                return menu_citas()
            if len(diagnostico) > 200:
                print("Diagnóstico excede 200 caracteres. Intente de nuevo o escribe 0 para cancelar.")
                continue
            break

        valores_cita = (folio_cita_id, clave_paciente_id, hora_llegada, peso, estatura, presion_sistolica, presion_diastolica, diagnostico)

        cursor.execute('''
            INSERT INTO citas_realizadas (folio_cita, clave_paciente, hora_de_llegada, peso, estatura, presion_sistolica, presion_diastolica, diagnostico)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', valores_cita)

        cursor.execute("UPDATE citas SET estado = 'realizada' WHERE folio_cita = ?", (folio_cita_id,))
        conn.commit()

        print(f"Cita realizada con éxito. Folio de la cita: {folio_cita_id}")

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def menu_cancelacion_citas():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM citas WHERE estado = 'pendiente'")
        citas_pendientes = cursor.fetchall()

        if not citas_pendientes:
            print("No hay citas programadas para cancelar.")
            return menu_citas()

        while True:
            print("\nMENÚ CANCELACIÓN DE CITAS")
            print("1. Cancelar citas por fecha")
            print("2. Cancelar citas por paciente")
            print("3. Volver al menú de citas")

            try:
                opcion = input("Seleccione una opción (1/2/3): ")
                if opcion not in [1, 2, 3]:
                    raise ValueError("Opción no válida")
                if opcion == '1':
                    cancelar_citas_por_fecha()
                elif opcion == '2':
                    cancelar_citas_por_paciente()
                elif opcion == '3':
                    return menu_citas()
                else:
                    print("Opción no válida. Intente de nuevo.")
            except ValueError:
                print("Opción no válida. Intente de nuevo.")
    finally:
            conn.close()

def cancelar_citas_por_fecha():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT strftime('%m/%d/%Y', fecha_cita) AS fecha_cita 
            FROM citas 
            WHERE estado = 'pendiente'
            ORDER BY fecha_cita
        """)
        fechas = cursor.fetchall()

        if not fechas:
            print("No hay citas pendientes.")
            return menu_cancelacion_citas()

        print("Fechas con citas pendientes por realizar:")
        print(tabulate(fechas, headers=["Fecha de la Cita"], tablefmt="fancy_grid"))

        while True:
            while True:
                fecha_str = input("Ingrese la fecha de las citas a cancelar (MM/DD/YYYY) o escriba 0 para cancelar: ").strip()
                if fecha_str == "0":
                    print("Operación cancelada.")
                    return menu_cancelacion_citas()

                try:
                    fecha = datetime.datetime.strptime(fecha_str, "%m/%d/%Y").date()
                    break
                except ValueError:
                    print("Fecha inválida. Intente de nuevo.")

            cursor.execute("""
                SELECT folio_cita, strftime('%m/%d/%Y', fecha_cita) AS fecha_cita, turno 
                FROM citas 
                WHERE strftime('%m/%d/%Y', fecha_cita) = ? AND estado = 'pendiente'
            """, (fecha_str,))
            citas = cursor.fetchall()

            if not citas:
                print(f"No hay citas pendientes para la fecha {fecha_str}.")
                continue

            print("Citas de la fecha seleccionada:")
            print(tabulate(citas, headers=["Folio de Cita", "Fecha de Cita", "Turno"], tablefmt="fancy_grid"))

            while True:
                while True:
                    folio_cita_str = input("Ingrese el folio de la cita que desea cancelar o escriba 0 para cancelar la operación: ").strip()
                    if folio_cita_str == "0":
                        print("Operación cancelada.")
                        return menu_cancelacion_citas()

                    try:
                        folio_cita = int(folio_cita_str)
                        break
                    except ValueError:
                        print("Folio inválido. Intente de nuevo.")

                cursor.execute("DELETE FROM citas WHERE folio_cita = ? AND estado = 'pendiente'", (folio_cita,))
                affected = cursor.rowcount
                if affected == 0:
                    print(f"No se encontró una cita pendiente con el folio {folio_cita}, o ya fue cancelada.")
                    continue
                conn.commit()
                print(f"Cita {folio_cita} cancelada exitosamente.")

                cursor.execute("SELECT COUNT(*) FROM citas WHERE estado = 'pendiente'")
                if cursor.fetchone()[0] >=1:
                    return menu_cancelacion_citas()
                else:
                    print("No hay más citas pendientes.")
                    return menu_citas()
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    finally:
        conn.close()


def cancelar_citas_por_paciente():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT p.clave_paciente, 
            p.nombre || ' ' || p.primer_apellido || ' ' || COALESCE(p.segundo_apellido, '') AS nombre_completo
            FROM pacientes p
            JOIN citas c ON p.clave_paciente = c.clave_paciente
            WHERE c.estado = 'pendiente'
        """)
        pacientes = cursor.fetchall()

        if not pacientes:
            print("No hay pacientes con citas pendientes.")
            return menu_citas()

        headers_pacientes = ["Clave del Paciente", "Nombre Completo"]
        print("Pacientes con citas pendientes por realizar:")
        print(tabulate(pacientes, headers=headers_pacientes, tablefmt="fancy_grid"))

        while True:
            while True:
                clave_paciente = input("Ingrese la clave del paciente para cancelar sus citas o escriba 0 para cancelar la operación: ").strip()

                if clave_paciente == "0":
                    print("Operación cancelada.")
                    return menu_cancelacion_citas()

                try:
                    clave_paciente = int(clave_paciente)
                    if clave_paciente < 0:
                        raise ValueError("Clave inválida. Debe ser un número positivo.")
                    break
                except ValueError as e:
                    print(f"Error: {e}. Intente de nuevo.")

            cursor.execute("""
                SELECT folio_cita, strftime('%m/%d/%Y', fecha_cita) AS fecha_cita, turno
                FROM citas
                WHERE clave_paciente = ? AND estado = 'pendiente'
            """, (clave_paciente,))
            citas = cursor.fetchall()

            if not citas:
                print(f"No hay citas pendientes para el paciente {clave_paciente}.")
                continue

            headers_citas = ["Folio de Cita", "Fecha de Cita", "Turno"]
            print("Citas pendientes del paciente seleccionado:")
            print(tabulate(citas, headers=headers_citas, tablefmt="fancy_grid"))

            while True:
                while True:
                    folio_cita = input("Ingrese el folio de la cita que desea cancelar o escriba 0 para cancelar la operación: ").strip()

                    if folio_cita == "0":
                        print("Operación cancelada.")
                        return menu_cancelacion_citas()

                    try:
                        folio_cita = int(folio_cita)
                        if folio_cita < 0:
                            raise ValueError("Folio inválido. Debe ser un número positivo.")
                        break
                    except ValueError as e:
                        print(f"Error: {e}. Intente de nuevo.")

                cursor.execute("SELECT COUNT(*) FROM citas WHERE folio_cita = ? AND estado = 'pendiente'", (folio_cita,))
                if cursor.fetchone()[0] == 0:
                    print(f"No hay citas pendientes con el folio {folio_cita}.")
                    continue

                try:
                    cursor.execute("DELETE FROM citas WHERE folio_cita = ?", (folio_cita,))
                    conn.commit()
                    print(f"Cita {folio_cita} cancelada exitosamente.")
                    break
                except sqlite3.Error as e:
                    print(f"Error al cancelar la cita: {e}")

            cursor.execute("SELECT COUNT(*) FROM citas WHERE clave_paciente = ? AND estado = 'pendiente'", (clave_paciente,))
            if cursor.fetchone()[0] == 0:
                print("No hay citas programadas para cancelar.")
                return menu_citas()
    finally:
        conn.close()

def menu_consultas_y_reportes():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM pacientes")
        if cursor.fetchone()[0] == 0:
            print("No hay pacientes registrados. Por favor, registre pacientes antes de acceder a consultas y reportes.")
            return

        while True:
            print("\nCONSULTAS Y REPORTES")
            print("1. Reportes de citas")
            print("2. Reportes de pacientes")
            print("3. Estadísticos demográficos")
            print("4. Regresar al menú principal")
            try:
                opcion = int(input("Seleccione una opción (1/2/3/4): "))
                if opcion not in [1, 2, 3, 4]:
                    raise ValueError("Opción no válida")

                if opcion == 1:
                    reportes_de_citas()
                elif opcion == 2:
                    reportes_de_pacientes()
                elif opcion == 3:
                    estadisticos_demograficos()
                elif opcion == 4:
                    return menu_principal() 
            except ValueError as e:
                print(f"{e}. Por favor, ingrese un número válido (1/2/3/4).")

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        conn.close()

def reportes_de_citas():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM citas")
        if cursor.fetchone()[0] == 0:
            print("No hay citas registradas. Por favor, registre alguna cita antes de acceder a los reportes de citas.")
            return  

        while True:
            print("\nREPORTES DE CITAS")
            print("1. Citas por periodo")
            print("2. Citas por paciente")
            print("3. Volver al menú de consultas y reportes")
            opcion = input("Seleccione una opción (1/2/3): ")
            if opcion not in [1, 2, 3]:
                    raise ValueError("Opción no válida")
            if opcion == "1":
                reporte_citas_por_periodo()
            elif opcion == "2":
                reporte_citas_por_paciente()
            elif opcion == "3":
                return menu_consultas_y_reportes()
            else:
                print("Opción no válida. Intente de nuevo.")

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        conn.close()

def reporte_citas_por_periodo():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT strftime('%m/%d/%Y', fecha_cita) FROM citas ORDER BY date(fecha_cita)")
        fechas = cursor.fetchall()
        if not fechas:
            print("No hay citas programadas.")
            return

        print("Fechas disponibles de citas:")
        print(tabulate(fechas, headers=["Fechas Disponibles"], tablefmt="fancy_grid"))

        while True:
            inicio = input("Ingrese la fecha de inicio del periodo (MM/DD/YYYY) o escriba 0 para cancelar: ")
            if inicio == '0':
                print("Operación cancelada.")
                return
            fin = input("Ingrese la fecha de fin del periodo (MM/DD/YYYY) o escriba 0 para cancelar: ")
            if fin == '0':
                print("Operación cancelada.")
                return

            try:
                inicio_fecha = datetime.datetime.strptime(inicio, "%m/%d/%Y").date()
                fin_fecha = datetime.datetime.strptime(fin, "%m/%d/%Y").date()
                if fin_fecha < inicio_fecha:
                    print("La fecha de fin no puede ser anterior a la fecha de inicio.")
                    continue
                elif fin_fecha == inicio_fecha:
                    print("La fecha de fin no puede ser igual a la fecha de inicio.")
                    continue

                cursor.execute("""
                    SELECT c.folio_cita, p.clave_paciente, p.primer_apellido || ' ' || p.segundo_apellido || ' ' || p.nombre AS nombre_completo,
                    strftime('%m/%d/%Y', c.fecha_cita) AS formatted_date
                    FROM citas c
                    JOIN pacientes p ON c.clave_paciente = p.clave_paciente
                    WHERE date(fecha_cita) BETWEEN ? AND ?
                    ORDER BY date(fecha_cita)
                """, (inicio_fecha, fin_fecha))
                citas = cursor.fetchall()

                if not citas:
                    print("No hay citas en ese periodo de tiempo. Intenta de nuevo o escribe 0 para cancelar.")
                    continue

                print("Citas en el periodo especificado:")
                print(tabulate(citas, headers=["Folio Cita", "ID Paciente", "Nombre Completo", "Fecha de la Cita"], tablefmt="fancy_grid"))
                break

            except ValueError:
                print("Formato de fecha incorrecto. Por favor, use el formato MM/DD/YYYY.")
        
        while True:
            folio = input("Ingrese el folio de la cita para ver más detalles, escriba 0 para cancelar: ")
            if folio == '0':
                print("Operación cancelada.")
                return

            try:
                folio = int(folio)
                if folio < 0:
                    raise ValueError("El folio no puede ser un número negativo.")

                cursor.execute("""
                    SELECT p.clave_paciente, p.primer_apellido || ' ' || p.segundo_apellido || ' ' || p.nombre AS nombre_completo, 
                           strftime('%m/%d/%Y', p.fecha_nacimiento) AS fecha_nac, p.sexo, c.estado, 
                           (strftime('%Y', 'now') - strftime('%Y', p.fecha_nacimiento)) AS edad, cr.hora_de_llegada,
                           cr.peso, cr.estatura, printf('%03d/%03d', cr.presion_sistolica, cr.presion_diastolica) AS presion, cr.diagnostico
                    FROM pacientes p
                    JOIN citas c ON p.clave_paciente = c.clave_paciente
                    LEFT JOIN citas_realizadas cr ON c.folio_cita = cr.folio_cita
                    WHERE c.folio_cita = ?
                """, (folio,))
                detalle = cursor.fetchone()
                if not detalle:
                    print("No se encontraron detalles para el folio proporcionado. Intenta con otro folio o escribe 0 para cancelar.")
                    continue

                headers = ["ID Paciente", "Nombre Completo", "Fecha Nac", "Sexo", "Estado Cita", "Edad", "Hora de Llegada",
                           "Peso", "Estatura", "Presión Sistólica/Diastólica", "Diagnóstico"]
                print("Detalles del paciente y la cita:")
                print(tabulate([detalle], headers=headers, tablefmt="fancy_grid"))

                exportar = input("¿Desea exportar los datos a CSV o Excel? (S/N) o escriba 0 para cancelar: ").strip().upper()
                if exportar == 'S':
                    exportar_citas_por_periodo(detalle)
                elif exportar == 'N':
                    return reportes_de_citas()
                elif exportar == 0:
                    return reportes_de_citas()
                else:
                    print("Opción no válida. Por favor, ingrese 'S' para sí o 'N' para no o escriba 0 para cancelar la operacion.")

            except ValueError:
                print("Dato ingresado no es válido. Intenta de nuevo o escribe 0 para cancelar.")

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        conn.close()

def exportar_citas_por_periodo(detalle):
    df = pd.DataFrame([detalle], columns=["ID Paciente", "Nombre Completo", "Fecha Nac", "Sexo", "Estado Cita", "Edad", "Hora de Llegada", "Peso", "Estatura", "Presión Sistólica/Diastólica", "Diagnóstico"])

    while True:
        formato = input("Escriba '1' para exportar a CSV, '2' para exportar a Excel o '0' para cancelar la operación: ").strip()
        if formato == '1':
            df.to_csv('detalle_cita.csv', index=False)
            print("Datos exportados correctamente a 'detalle_cita.csv'.")
            return reportes_de_citas()
        elif formato == '2':
            df.to_excel('detalle_cita.xlsx', index=False)
            print("Datos exportados correctamente a 'detalle_cita.xlsx'.")
            return reportes_de_citas()
        elif formato == '0':
            print("Operación cancelada.")
            return reportes_de_citas()
        else:
            print("Entrada inválida. Por favor, intente de nuevo.")



def reporte_citas_por_paciente():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        cursor.execute("SELECT clave_paciente, primer_apellido || ' ' || segundo_apellido || ' ' || nombre AS nombre_completo FROM pacientes")
        pacientes = cursor.fetchall()
        if not pacientes:
            print("No hay pacientes registrados.")
            return

        print("Pacientes registrados:")
        print(tabulate(pacientes, headers=["Clave Paciente", "Nombre Completo"], tablefmt="fancy_grid"))

        while True:
            clave_paciente = input("Ingrese la clave del paciente para ver sus citas o escriba 0 para cancelar: ")
            if clave_paciente == '0':
                return
            
            try:
                clave_paciente = int(clave_paciente)
                if clave_paciente < 0:
                    raise ValueError("La clave del paciente no puede ser un número negativo.")
            except ValueError:
                print("Dato ingresado no es válido. Por favor, ingrese un número entero positivo o escriba 0 para cancelar.")
                continue
            
            cursor.execute("SELECT COUNT(*) FROM pacientes WHERE clave_paciente = ?", (clave_paciente,))
            if cursor.fetchone()[0] == 0:
                print("No se encontró un paciente con esa clave. Intente de nuevo o escriba 0 para cancelar.")
                continue
            break

        cursor.execute("""
            SELECT folio_cita, strftime('%m/%d/%Y', fecha_cita) AS formatted_date
            FROM citas
            WHERE clave_paciente = ?
            ORDER BY date(fecha_cita)
        """, (clave_paciente,))
        citas = cursor.fetchall()

        if not citas:
            print("Este paciente no tiene citas registradas.")
            return

        print("Citas del paciente seleccionado:")
        print(tabulate(citas, headers=["Folio Cita", "Fecha de la Cita"], tablefmt="fancy_grid"))

        while True:
            folio_cita = input("Ingrese el folio de la cita para ver más detalles, escriba 0 para cancelar: ")
            if folio_cita == '0':
                return

            try:
                folio_cita = int(folio_cita)
                if folio_cita < 0:
                    raise ValueError("El folio no puede ser un número negativo.")

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM citas
                    WHERE folio_cita = ? AND clave_paciente = ?
                """, (folio_cita, clave_paciente))
                if cursor.fetchone()[0] == 0:
                    print("No se encontró una cita con ese folio para el paciente seleccionado. Intente de nuevo o escriba 0 para cancelar.")
                    continue

                cursor.execute("""
                    SELECT p.clave_paciente, p.primer_apellido || ' ' || p.segundo_apellido || ' ' || p.nombre AS nombre_completo, 
                           strftime('%m/%d/%Y', p.fecha_nacimiento) AS fecha_nac, p.sexo, c.estado, cr.hora_de_llegada,
                           (strftime('%Y', 'now') - strftime('%Y', p.fecha_nacimiento)) AS edad, 
                           cr.peso, cr.estatura, printf('%03d/%03d', cr.presion_sistolica, cr.presion_diastolica) AS presion, cr.diagnostico
                    FROM pacientes p
                    JOIN citas c ON p.clave_paciente = c.clave_paciente
                    LEFT JOIN citas_realizadas cr ON c.folio_cita = cr.folio_cita
                    WHERE c.folio_cita = ?
                """, (folio_cita,))
                detalle = cursor.fetchone()
                headers = ["ID Paciente", "Nombre Completo", "Fecha Nac", "Sexo", "Estado Cita", "Hora de Llegada", "Edad",
                           "Peso", "Estatura", "Presión Sistólica/Diastólica", "Diagnóstico"]
                print("Detalles del paciente y la cita:")
                print(tabulate([detalle], headers=headers, tablefmt="fancy_grid"))
                exportar_citas_por_paciente(detalle)
            except ValueError:
                print("Dato ingresado no es válido. Intenta de nuevo o escribe 0 para cancelar.")

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        conn.close()

def exportar_citas_por_paciente(detalle):
    df = pd.DataFrame([detalle], columns=["ID Paciente", "Nombre Completo", "Fecha Nac", "Sexo", "Estado Cita", "Hora de Llegada", "Edad", "Peso", "Estatura", "Presión Sistólica/Diastólica", "Diagnóstico"])

    while True:
        respuesta = input("¿Desea exportar los datos de la cita y el paciente a CSV o Excel? (S/N): ").strip().upper()
        if respuesta == 'S':
            while True:
                formato = input("Escriba '1' para exportar a CSV, '2' para exportar a Excel o '0' para cancelar la operación: ").strip()
                if formato == '1':
                    df.to_csv('detalle_cita_por_paciente.csv', index=False)
                    print("Datos exportados correctamente a 'detalle_cita_por_paciente.csv'.")
                    return reportes_de_citas()
                elif formato == '2':
                    df.to_excel('detalle_cita_por_paciente.xlsx', index=False)
                    print("Datos exportados correctamente a 'detalle_cita_por_paciente.xlsx'.")
                    return reportes_de_citas()
                elif formato == '0':
                    print("Operación cancelada.")
                    return reportes_de_citas()
                else:
                    print("Entrada inválida. Por favor, intente de nuevo.")
        elif respuesta == 'N':
            return reportes_de_citas()
        elif respuesta == 0:
            return reportes_de_citas()
        else:
            print("Respuesta no válida. Por favor, ingrese 'S' para sí, 'N' para no.")

def reportes_de_pacientes():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM pacientes")
        if cursor.fetchone()[0] == 0:
            print("No hay pacientes registrados. No se puede acceder a los reportes por pacientes.")
            return

        while True:
            print("\nMENU DE REPORTES POR PACIENTES")
            print("1. Listado completo de pacientes")
            print("2. Búsqueda por clave de paciente")
            print("3. Búsqueda por apellidos y nombres")
            print("4. Volver al menu de consultas y reportes")
            opcion = input("Seleccione una opción (1/2/3/4): ")

            try:
                opcion = int(opcion)
                if opcion == 1:
                    listar_pacientes()
                elif opcion == 2:
                    buscar_por_clave_paciente()
                elif opcion == 3:
                    buscar_por_apellido_nombre()
                elif opcion == 4:
                    print("Volviendo al menú de consutas y reportes..")
                    return menu_consultas_y_reportes()
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida (1, 2, 3, 4).")

            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número entero (1, 2, 3, 4 ).")

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        conn.close()

def listar_pacientes():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()
        cursor.execute("SELECT clave_paciente, primer_apellido, segundo_apellido, nombre, strftime('%m/%d/%Y', fecha_nacimiento) AS fecha_nac, sexo FROM pacientes")
        pacientes = cursor.fetchall()

        if pacientes:
            print(tabulate(pacientes, headers=["ID", "Primer Apellido", "Segundo Apellido", "Nombre", "Fecha Nac", "Sexo"], tablefmt="fancy_grid"))
            respuesta = input("¿Desea exportar el listado completo de pacientes? (S/N): ").strip().upper()
            while respuesta not in ('S', 'N', '0'):
                print("Dato ingresado no es válido. Por favor, ingrese S para sí, N para no, o 0 para cancelar.")
                respuesta = input("¿Desea exportar el listado completo de pacientes? (S/N): ").strip().upper()

            if respuesta == 'S':
                exportar_datos_listado_pacientes()
            elif respuesta == 'N':
                return reportes_de_pacientes()
            elif respuesta == '0':
                return
        else:
            print("No hay pacientes registrados.")
    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        conn.close()

def exportar_datos_listado_pacientes():
    conn = sqlite3.connect('Base_de_datos_clinica')
    cursor = conn.cursor()
    cursor.execute("SELECT clave_paciente, primer_apellido, segundo_apellido, nombre, strftime('%m/%d/%Y', fecha_nacimiento) AS fecha_nac, sexo FROM pacientes")
    pacientes = cursor.fetchall()
    df = pd.DataFrame(pacientes, columns=["ID", "Primer Apellido", "Segundo Apellido", "Nombre", "Fecha Nac", "Sexo"])
    conn.close()

    if not pacientes:
        print("No hay pacientes registrados para exportar.")
        return

    while True:
        formato = input("Escriba '1' para exportar a CSV, '2' para exportar a Excel o '0' para cancelar la operación: ").strip()
        if formato == '1':
            df.to_csv('listado_completo_pacientes.csv', index=False)
            print("Datos exportados a 'listado_completo_pacientes.csv'.")
            break
        elif formato == '2':
            df.to_excel('listado_completo_pacientes.xlsx', index=False)
            print("Datos exportados a 'listado_completo_pacientes.xlsx'.")
            break
        elif formato == '0':
            print("Operación cancelada.")
            return
        else:
            print("Entrada inválida. Por favor, intente de nuevo o escriba '0' para cancelar la operación.")

    reportes_de_pacientes()



def buscar_por_clave_paciente():
    conn = sqlite3.connect('Base_de_datos_clinica')
    cursor = conn.cursor()

    try:
        while True:
            clave = input("Ingrese la clave del paciente o escriba 0 para cancelar: ")
            if clave == '0':
                return

            try:
                clave = int(clave)
                if clave <= 0:
                    print("Por favor, ingrese un número entero positivo para la clave del paciente.")
                    continue
            except ValueError:
                print("Por favor, ingrese un número válido para la clave del paciente.")
                continue

            cursor.execute("""
                SELECT clave_paciente, primer_apellido, segundo_apellido, nombre, 
                       strftime('%m/%d/%Y', fecha_nacimiento) AS fecha_nac, edad_paciente, sexo
                FROM pacientes WHERE clave_paciente = ?
            """, (clave,))
            paciente = cursor.fetchone()

            if not paciente:
                print("No se encontró un paciente con esa clave.")
                continue

            print(tabulate([paciente], headers=["ID", "Primer Apellido", "Segundo Apellido", "Nombre", "Fecha Nac", "Edad", "Sexo"], tablefmt="fancy_grid"))

            while True:
                opcion = input("¿Desea consultar el expediente clínico? (S/N) o escriba 0 para cancelar: ").strip().upper()
                if opcion == '0':
                    return
                elif opcion == 'S':
                    cursor.execute("""
                        SELECT c.folio_cita, strftime('%m/%d/%Y', c.fecha_cita) AS fecha_cita, strftime('%H:%M:%S', cr.hora_de_llegada) AS hora_llegada,
                               c.turno, c.estado, cr.peso, cr.estatura, printf('%03d/%03d', cr.presion_sistolica, cr.presion_diastolica) AS presion, cr.diagnostico
                        FROM citas c
                        JOIN citas_realizadas cr ON c.folio_cita = cr.folio_cita
                        WHERE c.clave_paciente = ?
                        ORDER BY c.fecha_cita
                    """, (clave,))
                    expedientes = cursor.fetchall()

                    if not expedientes:
                        print("No se encontraron detalles clínicos para el paciente.")
                    else:
                        headers = ["Folio Cita", "Fecha de Cita", "Hora de Llegada", "Turno", "Estado", "Peso", "Estatura", "Presión (Sis/Dias)", "Diagnóstico"]
                        print("Expediente clínico del paciente:")
                        print(tabulate(expedientes, headers=headers, tablefmt="fancy_grid"))

                    while True:
                        exportar = input("¿Desea exportar los datos del paciente y el expediente a CSV o Excel? (S/N) o escriba 0 para cancelar: ").strip().upper()
                        if exportar == '0':
                            return
                        elif exportar == 'S':
                            exportar_datos_paciente_por_clave(paciente, expedientes)
                            break
                        elif exportar == 'N':
                            break
                        else:
                            print("Opción no válida. Por favor, ingrese S para sí, N para no, o 0 para cancelar.")
                            continue

                    break
                elif opcion == 'N':
                    return
                else:
                    print("Opción no válida. Por favor, ingrese S para sí, N para no, o 0 para cancelar.")

    finally:
        conn.close()

def exportar_datos_paciente_por_clave(paciente, expedientes):
    import pandas as pd

    df_paciente = pd.DataFrame([paciente], columns=["ID", "Primer Apellido", "Segundo Apellido", "Nombre", "Fecha Nac", "Edad", "Sexo"])
    
    df_expedientes = pd.DataFrame(expedientes, columns=["Folio Cita", "Fecha de Cita", "Hora de Llegada", "Turno", "Estado", "Peso", "Estatura", "Presión Sistólica/Diastólica", "Diagnóstico"])

    df_paciente = df_paciente.loc[df_paciente.index.repeat(len(df_expedientes))].reset_index(drop=True)
    df_final = pd.concat([df_paciente, df_expedientes], axis=1)

    while True:
        formato = input("Escriba '1' para exportar a CSV, '2' para exportar a Excel o '0' para cancelar la operación: ").strip()
        if formato == '1':
            df_final.to_csv('expediente_clinico_completo.csv', index=False)
            print("Datos del paciente y su expediente clínico exportados a 'expediente_clinico_completo.csv'.")
            return reportes_de_pacientes()
        elif formato == '2':
            df_final.to_excel('expediente_clinico_completo.xlsx', index=False)
            print("Datos del paciente y su expediente clínico exportados a 'expediente_clinico_completo.xlsx'.")
            return reportes_de_pacientes()
        elif formato == '0':
            print("Operación cancelada.")
            return
        else:
            print("Entrada inválida. Por favor, intente de nuevo o escriba '0' para cancelar.")

def buscar_por_apellido_nombre():
    conn = sqlite3.connect('Base_de_datos_clinica')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT clave_paciente, primer_apellido, COALESCE(segundo_apellido, '') as segundo_apellido, nombre
            FROM pacientes 
            ORDER BY primer_apellido, segundo_apellido, nombre
        """)
        pacientes = cursor.fetchall()
        if not pacientes:
            print("No hay pacientes registrados.")
            return reportes_de_pacientes
        else:
            print("Pacientes registrados:")
            print(tabulate(pacientes, headers=["ID", "Primer Apellido", "Segundo Apellido", "Nombre"], tablefmt="fancy_grid"))

        while True:
            primer_apellido = input("Ingrese el primer apellido del paciente o escriba 0 para cancelar: ")
            if primer_apellido == '0':
                break

            if not primer_apellido.isalpha():
                print("El apellido debe contener solo letras. Intente de nuevo o escriba 0 para cancelar.")
                continue

            nombre = input("Ingrese el nombre del paciente o escriba 0 para cancelar: ")
            if nombre == '0':
                break

            if not nombre.isalpha():
                print("El nombre debe contener solo letras. Intente de nuevo o escriba 0 para cancelar.")
                continue

            cursor.execute("""
                SELECT clave_paciente, primer_apellido, segundo_apellido, nombre, 
                       strftime('%m/%d/%Y', fecha_nacimiento) AS fecha_nac, edad_paciente, sexo
                FROM pacientes 
                WHERE UPPER(primer_apellido) LIKE UPPER(?) AND UPPER(nombre) LIKE UPPER(?)
            """, ('%'+primer_apellido+'%', '%'+nombre+'%'))
            resultados = cursor.fetchall()
            if not resultados:
                print("No se encontraron pacientes con esos datos. Intente de nuevo o escriba 0 para cancelar.")
            else:
                print("Resultados de búsqueda:")
                print(tabulate(resultados, headers=["ID", "Primer Apellido", "Segundo Apellido", "Nombre", "Fecha Nac", "Edad", "Sexo"], tablefmt="fancy_grid"))
                while True:
                    respuesta = input("¿Desea consultar el expediente clínico de algún paciente listado? (S/N): ").strip().upper()
                    if respuesta == 'S':
                        clave_paciente = resultados[0][0]  
                        mostrar_expediente_clinico_apellido_nombre(clave_paciente)
                        break
                    elif respuesta == 'N':
                        return reportes_de_pacientes()
                    elif respuesta == '0':
                        return reportes_de_pacientes()
                    else:
                        print("Respuesta no válida. Intente de nuevo o escriba 0 para cancelar.")
                        continue

    finally:
        conn.close()

def mostrar_expediente_clinico_apellido_nombre(clave_paciente):
    conn = sqlite3.connect('Base_de_datos_clinica')
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT p.clave_paciente, p.primer_apellido, COALESCE(p.segundo_apellido, '') as segundo_apellido, p.nombre, 
                   strftime('%m/%d/%Y', p.fecha_nacimiento) AS fecha_nac, p.edad_paciente, p.sexo,
                   c.folio_cita, strftime('%m/%d/%Y', c.fecha_cita) AS fecha_cita, c.turno, c.estado,
                   strftime('%H:%M:%S', cr.hora_de_llegada) AS hora_llegada, cr.peso, cr.estatura,
                   printf('%03d/%03d', cr.presion_sistolica, cr.presion_diastolica) AS presion, cr.diagnostico
            FROM pacientes p
            JOIN citas c ON p.clave_paciente = c.clave_paciente
            JOIN citas_realizadas cr ON c.folio_cita = cr.folio_cita
            WHERE p.clave_paciente = ?
            ORDER BY c.fecha_cita
        """, (clave_paciente,))
        expedientes = cursor.fetchall()

        if not expedientes:
            print("No se encontraron detalles clínicos para el paciente.")
        else:
            headers = ["Clave Paciente", "Primer Apellido", "Segundo Apellido", "Nombre", "Fecha Nac", "Edad", "Sexo",
                       "Folio Cita", "Fecha de Cita", "Turno", "Estado", "Hora de Llegada", "Peso", "Estatura", "Presión Sistolica/Diastolica", "Diagnóstico"]
            print("Expediente clínico del paciente:")
            print(tabulate(expedientes, headers=headers, tablefmt="fancy_grid"))

            while True:
                respuesta = input("¿Desea exportar el expediente a CSV o Excel? (S/N): ").strip().upper()
                if respuesta == 'S':
                    exportar_expediente_clinico_apellido_nombre(expedientes)
                    return reportes_de_pacientes()
                elif respuesta == 'N':
                    return reportes_de_pacientes()
                elif respuesta == '0':
                    break
                else:
                    print("Respuesta no válida. Por favor, ingrese 'S', 'N' o '0' para cancelar.")
    finally:
        conn.close()

def exportar_expediente_clinico_apellido_nombre(expedientes):
    df = pd.DataFrame(expedientes, columns=["Clave Paciente", "Primer Apellido", "Segundo Apellido", "Nombre", "Fecha Nac", "Edad", "Sexo", "Folio Cita", "Fecha de Cita", "Turno", "Estado", "Hora de Llegada", "Peso", "Estatura", "Presión Sistolica/Diastolica", "Diagnóstico"])

    while True:
        formato = input("Escriba '1' para exportar a CSV, '2' para exportar a Excel o '0' para cancelar la operación: ").strip()
        if formato == '1':
            df.to_csv('expediente_clinico_apellido_nombre.csv', index=False)
            print("Datos exportados correctamente a 'expediente_clinico_apellido_nombre.csv'.")
            return reportes_de_pacientes()
        elif formato == '2':
            df.to_excel('expediente_clinico_apellido_nombre.xlsx', index=False)
            print("Datos exportados correctamente a 'expediente_clinico_apellido_nombre.xlsx'.")
            return reportes_de_pacientes()
        elif formato == '0':
            print("Operación cancelada.")
            return reportes_de_pacientes()
        else:
            print("Entrada inválida. Por favor, intente de nuevo.")

def estadisticos_demograficos():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM pacientes")
        if cursor.fetchone()[0] == 0:
            print("No hay pacientes registrados. Por favor, registre algún paciente antes de acceder a los reportes de citas.")
            return menu_consultas_y_reportes()

        while True:
            print("\nESTADÍSTICOS DEMOGRÁFICOS")
            print("1. Por edad")
            print("2. Por sexo")
            print("3. Por edad y sexo")
            print("4. Volver al menú de consultas y reportes")
            opcion = input("Seleccione una opción (1/2/3/4): ")

            if opcion not in ['1', '2', '3', '4']:
                print("Opción no válida. Intente de nuevo o escriba 0 para cancelar.")
                continue

            if opcion == "1":
                # Llamar a la función para obtener estadísticas por edad
                estadisticos_por_edad()
            elif opcion == "2":
                # Llamar a la función para obtener estadísticas por sexo
                estadisticos_por_sexo()
            elif opcion == "3":
                # Llamar a la función para obtener estadísticas por edad y sexo
                estadisticos_por_edad_y_sexo()
            elif opcion == "4":
                return menu_consultas_y_reportes()

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        conn.close()

import sqlite3
import pandas as pd
from tabulate import tabulate

def estadisticos_por_edad():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        # Verificar si hay al menos dos pacientes con citas realizadas
        cursor.execute("SELECT COUNT(DISTINCT clave_paciente) FROM citas_realizadas")
        if cursor.fetchone()[0] < 2:
            print("No hay suficientes pacientes con citas realizadas para realizar el análisis.")
            return

        # Mostrar todos los pacientes registrados con sus edades
        cursor.execute("SELECT nombre, edad_paciente FROM pacientes")
        pacientes = cursor.fetchall()
        print("\nPacientes registrados con sus edades:")
        print(tabulate(pacientes, headers=["Nombre", "Edad"], tablefmt="fancy_grid"))

        while True:
            try:
                input_str = input("Ingrese la edad mínima a analizar (1-100) o escriba '0' para cancelar: ").strip()
                if input_str == '0':
                    print("Operación cancelada.")
                    return
                edad_minima = int(input_str)
                
                if edad_minima < 1 or edad_minima > 100:
                    print("Ingrese una edad mínima válida entre 1 y 100.")
                    continue
                
                input_str = input("Ingrese la edad máxima a analizar (1-100) o escriba '0' para cancelar: ").strip()
                if input_str == '0':
                    print("Operación cancelada.")
                    return
                edad_maxima = int(input_str)
                
                if edad_maxima < 1 or edad_maxima > 100 or edad_maxima < edad_minima:
                    print("Ingrese una edad máxima válida entre 1 y 100, que sea mayor o igual a la edad mínima.")
                    continue
                
                # Verificar si hay datos en el rango de edad seleccionado
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM pacientes p
                    WHERE p.edad_paciente BETWEEN ? AND ?
                """, (edad_minima, edad_maxima))
                if cursor.fetchone()[0] == 0:
                    print("No hay pacientes en el rango de edad especificado. Intente de nuevo.")
                    continue

                break
            except ValueError:
                print("Por favor, ingrese valores numéricos válidos.")

        # Recuperar datos de las citas realizadas para los pacientes en el rango de edad
        cursor.execute("""
            SELECT p.nombre, p.edad_paciente, cr.peso, cr.estatura, cr.presion_sistolica, cr.presion_diastolica
            FROM pacientes p
            JOIN citas_realizadas cr ON p.clave_paciente = cr.clave_paciente
            WHERE p.edad_paciente BETWEEN ? AND ?
        """, (edad_minima, edad_maxima))
        datos = cursor.fetchall()

        # Convertir los datos a DataFrame para realizar cálculos estadísticos
        df = pd.DataFrame(datos, columns=["Nombre", "Edad", "Peso", "Estatura", "Presión Sistólica", "Presión Diastólica"])

        # Calcular estadísticas descriptivas
        estadisticos = df.describe()
        print("\nEstadísticas descriptivas de los datos de las citas realizadas:")
        print(tabulate(estadisticos, headers="keys", tablefmt="fancy_grid"))

        # Opción para exportar los datos
        while True:
            respuesta = input("¿Desea exportar los datos a CSV o Excel? (S/N) o escriba '0' para cancelar la operación: ").strip().upper()
            if respuesta == '0':
                print("Operación cancelada.")
                return
            elif respuesta == 'S':
                while True:
                    formato = input("Escriba '1' para exportar a CSV, '2' para exportar a Excel o '0' para cancelar la operación: ").strip()
                    if formato == '0':
                        print("Operación cancelada.")
                        return
                    elif formato == '1':
                        df.to_csv('estadisticos_por_edad.csv', index=False)
                        print("Datos exportados correctamente a 'estadisticos_por_edad.csv'.")
                        return
                    elif formato == '2':
                        df.to_excel('estadisticos_por_edad.xlsx', index=False)
                        print("Datos exportados correctamente a 'estadisticos_por_edad.xlsx'.")
                        return
                    else:
                        print("Entrada inválida. Por favor, intente de nuevo.")
            elif respuesta == 'N':
                return
            else:
                print("Respuesta no válida. Por favor, ingrese 'S' para sí, 'N' para no, o '0' para cancelar.")

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        if conn:
            conn.close()


def estadisticos_por_sexo():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        # Solicitar al usuario el sexo de los pacientes de los que desea ver los datos
        sexo_map = {'H': 'Hombre', 'M': 'Mujer', 'N': 'No contestó'}
        while True:
            sexo = input("Ingrese el sexo de los pacientes a analizar ('H' para hombres, 'M' para mujeres, 'N' para no contestaron) o escriba '0' para cancelar: ").strip().upper()
            if sexo == '0':
                print("Operación cancelada.")
                return
            elif sexo in sexo_map:
                sexo_desc = sexo_map[sexo]
                break
            else:
                print("Por favor, ingrese un valor válido ('H', 'M', 'N') o '0' para cancelar.")

        # Verificar si hay datos para el sexo seleccionado
        cursor.execute("SELECT COUNT(*) FROM pacientes WHERE sexo = ?", (sexo_desc,))
        if cursor.fetchone()[0] == 0:
            print(f"No hay pacientes registrados del sexo {sexo_desc}.")
            return

        # Recuperar datos de las citas realizadas para los pacientes del sexo seleccionado
        cursor.execute("""
            SELECT p.nombre, cr.peso, cr.estatura, cr.presion_sistolica, cr.presion_diastolica
            FROM pacientes p
            JOIN citas_realizadas cr ON p.clave_paciente = cr.clave_paciente
            WHERE p.sexo = ?
        """, (sexo_desc,))
        datos = cursor.fetchall()

        if not datos:
            print(f"No hay datos de citas realizadas para pacientes del sexo {sexo_desc}.")
            return

        # Convertir los datos a DataFrame para realizar cálculos estadísticos
        df = pd.DataFrame(datos, columns=["Nombre", "Peso", "Estatura", "Presión Sistólica", "Presión Diastólica"])

        # Calcular estadísticas descriptivas
        estadisticos = df.describe()
        print(f"\nEstadísticas descriptivas de los datos de las citas realizadas para pacientes del sexo {sexo_desc}:")
        print(tabulate(estadisticos, headers="keys", tablefmt="fancy_grid"))

        # Opción para exportar los datos
        while True:
            respuesta = input("¿Desea exportar los datos a CSV o Excel? (S/N) o escriba '0' para cancelar la operación: ").strip().upper()
            if respuesta == '0':
                print("Operación cancelada.")
                return
            elif respuesta == 'S':
                while True:
                    formato = input("Escriba '1' para exportar a CSV, '2' para exportar a Excel o '0' para cancelar la operación: ").strip()
                    if formato == '0':
                        print("Operación cancelada.")
                        return
                    elif formato == '1':
                        df.to_csv(f'estadisticos_por_sexo_{sexo}.csv', index=False)
                        print(f"Datos exportados correctamente a 'estadisticos_por_sexo_{sexo}.csv'.")
                        return
                    elif formato == '2':
                        df.to_excel(f'estadisticos_por_sexo_{sexo}.xlsx', index=False)
                        print(f"Datos exportados correctamente a 'estadisticos_por_sexo_{sexo}.xlsx'.")
                        return
                    else:
                        print("Entrada inválida. Por favor, intente de nuevo.")
            elif respuesta == 'N':
                return
            else:
                print("Respuesta no válida. Por favor, ingrese 'S' para sí, 'N' para no, o '0' para cancelar.")

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def estadisticos_por_edad_y_sexo():
    try:
        conn = sqlite3.connect('Base_de_datos_clinica')
        cursor = conn.cursor()

        # Mapeo de entradas de sexo a descripciones
        sexo_map = {'H': 'Hombre', 'M': 'Mujer', 'N': 'No contestó'}
        while True:
            sexo_input = input("Ingrese el sexo de los pacientes a analizar ('H' para hombres, 'M' para mujeres, 'N' para no contestaron) o escriba '0' para cancelar: ").strip().upper()
            if sexo_input == '0':
                print("Operación cancelada.")
                return
            elif sexo_input in sexo_map:
                sexo = sexo_map[sexo_input]
                break
            else:
                print("Entrada inválida. Por favor, ingrese 'H', 'M', 'N' o '0' para cancelar.")
        
        # Mostrar los pacientes del sexo seleccionado con sus edades
        cursor.execute("SELECT nombre, edad_paciente FROM pacientes WHERE sexo = ?", (sexo,))
        pacientes = cursor.fetchall()
        if not pacientes:
            print(f"No hay pacientes registrados del sexo {sexo}.")
            return
        print(f"\nPacientes del sexo {sexo} registrados con sus edades:")
        print(tabulate(pacientes, headers=["Nombre", "Edad"], tablefmt="fancy_grid"))

        while True:
            try:
                min_edad = input("Ingrese la edad mínima a analizar o escriba '0' para cancelar: ").strip()
                if min_edad == '0':
                    print("Operación cancelada.")
                    return
                min_edad = int(min_edad)

                max_edad = input("Ingrese la edad máxima a analizar o escriba '0' para cancelar: ").strip()
                if max_edad == '0':
                    print("Operación cancelada.")
                    return
                max_edad = int(max_edad)

                if min_edad < 0 or max_edad > 100 or max_edad < min_edad:
                    print("Por favor, asegúrese de que la edad mínima sea mayor o igual a 0, la máxima no más de 100, y la mínima menor o igual a la máxima.")
                    continue

                # Verificar si hay pacientes en el rango de edad
                cursor.execute("SELECT COUNT(*) FROM pacientes WHERE edad_paciente BETWEEN ? AND ? AND sexo = ?", (min_edad, max_edad, sexo))
                if cursor.fetchone()[0] == 0:
                    print("No se encontraron pacientes en ese rango de edades. Intente de nuevo.")
                    continue

                break
            except ValueError:
                print("Por favor, ingrese números válidos para las edades.")

        # Recuperar y analizar datos
        cursor.execute("""
            SELECT nombre, edad_paciente, peso, estatura, presion_sistolica, presion_diastolica
            FROM pacientes p
            JOIN citas_realizadas cr ON p.clave_paciente = cr.clave_paciente
            WHERE p.edad_paciente BETWEEN ? AND ? AND p.sexo = ?
        """, (min_edad, max_edad, sexo))
        datos = cursor.fetchall()
        df = pd.DataFrame(datos, columns=["Nombre", "Edad", "Peso", "Estatura", "Presión Sistólica", "Presión Diastólica"])

        if df.empty:
            print("No se encontraron datos de citas para los pacientes en el rango de edades especificado.")
            return

        estadisticos = df.describe()
        print("\nEstadísticas descriptivas de los datos de las citas realizadas:")
        print(tabulate(estadisticos, headers="keys", tablefmt="fancy_grid"))

        # Opción para exportar los datos
        while True:
            respuesta = input("¿Desea exportar los datos a CSV o Excel? (S/N) o escriba '0' para cancelar la operación: ").strip().upper()
            if respuesta == '0':
                print("Operación cancelada.")
                return
            elif respuesta == 'S':
                while True:
                    formato = input("Escriba '1' para exportar a CSV, '2' para exportar a Excel o '0' para cancelar la operación: ").strip()
                    if formato == '0':
                        print("Operación cancelada.")
                        return
                    elif formato == '1':
                        df.to_csv(f'estadisticos_por_edad_y_sexo_{sexo}.csv', index=False)
                        print(f"Datos exportados correctamente a 'estadisticos_por_edad_y_sexo_{sexo}.csv'.")
                        return
                    elif formato == '2':
                        df.to_excel(f'estadisticos_por_edad_y_sexo_{sexo}.xlsx', index=False)
                        print(f"Datos exportados correctamente a 'estadisticos_por_edad_y_sexo_{sexo}.xlsx'.")
                        return
                    else:
                        print("Entrada inválida. Por favor, intente de nuevo.")
            elif respuesta == 'N':
                return
            else:
                print("Respuesta no válida. Por favor, ingrese 'S' para sí, 'N' para no, o '0' para cancelar.")

    except sqlite3.Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    finally:
        if conn:
            conn.close()

menu_principal()