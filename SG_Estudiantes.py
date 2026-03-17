def registrar_estudiante():
    nombre = input("Ingrese el nombre del estudiante: ")
    edad = int(input("Ingrese la edad del estudiante: "))
    if edad > 18:
     n1 = float(input("Ingrese la nota 1 del estudiante: "))
     n2 = float(input("Ingrese la nota 2 del estudiante: "))
     n3 = float(input("Ingrese la nota 3 del estudiante: "))
     if n1 < 0 or n1 > 5 or n2 < 0 or n2 > 5 or n3 < 0 or n3 > 5:
        print("Las notas deben estar entre 0 y 5. Por favor, ingrese las notas nuevamente.")
        return None
    else:
        print("El estudiante no cumple con la edad requerida para el registro.")
        return None

    estudiante = {
        "nombre": nombre,
        "edad": edad,
        "nota1": n1,
        "nota2": n2,
        "nota3": n3
    }

    return estudiante

def calcular_promedio(estudiante):
    n1 = float(estudiante["nota1"])
    n2 = float(estudiante["nota2"])
    n3 = float(estudiante["nota3"])
    promedio = (n1 + n2 + n3) / 3
    return promedio

def evaluar_estado(promedio):
    if promedio >= 4.0:
        return "Aprobado"
    elif promedio >= 3.0 and promedio < 4.0:
        return "En recuperacion"
    else:
        return "Reprobado"
    
def menu():
    print("========Bienvenido al sistema de gestión de estudiantes========")
    print("1. Registrar estudiante")
    print("2. Salir")    
    opcion = input("Seleccione una opción: ")
    return opcion

opcion = 0
contador = 0
PROMEDIO_GENERAL = 0
while opcion != "2":
    opcion = menu()
    if opcion == "1":
        estudiante = registrar_estudiante()
        if estudiante is None:
            continue
        promedio = calcular_promedio(estudiante)
        estado = evaluar_estado(promedio)
        print(f"Estudiante {estudiante['nombre']}\n Promedio del estudiante {promedio:.2f}\n Estado academico: {estado}")
        contador += 1
        PROMEDIO_GENERAL += promedio
    elif opcion == "2":
        print("Saliendo del sistema. ¡Hasta luego!")
        print(f"Total de estudiantes registrados: {contador}")
        if contador > 0:
            print(f"Promedio general de los estudiantes: {PROMEDIO_GENERAL / contador:.2f}")
    else:
        print("Opción no válida. Por favor, seleccione una opción válida.")