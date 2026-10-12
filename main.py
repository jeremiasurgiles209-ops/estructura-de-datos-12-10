"""VISTA (V de MVC): menus, input() y print().

Ejecutar desde VS Code: python main.py
La logica de datos NO se escribe aqui, sino en views.py.
"""
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import EstudianteController, MateriaController, MatriculaController

# Se comparten los MISMOS controladores entre la vista y las matrículas.
estudiantes = EstudianteController()
materias = MateriaController()
matriculas = MatriculaController(estudiantes, materias)
estudiantes.vincular_matriculas(matriculas)
materias.vincular_matriculas(matriculas)


def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(mensaje):
    try:
        return int(input(mensaje).strip())
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    # TUPLA: los controladores devuelven (True/False, mensaje).
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        # Polimorfismo: el MISMO print funciona con los tres modelos.
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    # DICT: datos del objeto en forma de clave -> valor.
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {clave.replace('_', ' ').capitalize():<18}: {valor}")


# ---------------------------------------------------------------------
# ESTUDIANTES
# ---------------------------------------------------------------------
def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet (único): "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(estudiantes.leer(), "Todavía no hay estudiantes")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    mostrar_lista(estudiantes.buscar(termino), "No se encontraron coincidencias")
    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    alumno = estudiantes.obtener(pedir_entero("ID: "))
    if alumno is None:
        imprimir_error("Estudiante no encontrado")
    else:
        mostrar_detalle(alumno)
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_registro = pedir_entero("ID: ")
    alumno = estudiantes.obtener(id_registro)
    if alumno is None:
        imprimir_error("Estudiante no encontrado")
        return pausa()
    imprimir_info(f"Editando: {alumno.etiqueta()}")
    print("Deja vacío cada dato que no deseas modificar.\n")
    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(alumno, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    mostrar_resultado(*estudiantes.actualizar(id_registro, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_registro = pedir_entero("ID: ")
    alumno = estudiantes.obtener(id_registro)
    if alumno is None:
        imprimir_error("Estudiante no encontrado")
    elif confirmar(f"¿Eliminar a {alumno.nombre_completo()}?"):
        mostrar_resultado(*estudiantes.eliminar(id_registro))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# ---------------------------------------------------------------------
# MATERIAS
# ---------------------------------------------------------------------
def crear_materia():
    imprimir_titulo("CREAR MATERIA")
    print("Créditos entre 1 y 10; cupos entre 0 y 30.\n")
    nombre = input("Nombre de la materia: ")
    codigo = input("Código único (ej.: MAT101): ")
    creditos = input("Créditos: ")
    cupos = input("Cupos (Enter para 30): ").strip()
    datos = {
        "nombre": nombre,
        "codigo": codigo,
        "creditos": creditos,
        "cupos": cupos if cupos else "30",
    }
    mostrar_resultado(*materias.crear(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(materias.leer(), "Todavía no hay materias")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o código: ")
    mostrar_lista(materias.buscar(termino), "No se encontraron coincidencias")
    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = materias.obtener(pedir_entero("ID: "))
    if materia is None:
        imprimir_error("Materia no encontrada")
    else:
        mostrar_detalle(materia)
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_registro = pedir_entero("ID: ")
    materia = materias.obtener(id_registro)
    if materia is None:
        imprimir_error("Materia no encontrada")
        return pausa()
    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deja vacío cada dato que no deseas modificar.\n")
    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    mostrar_resultado(*materias.actualizar(id_registro, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_registro = pedir_entero("ID: ")
    materia = materias.obtener(id_registro)
    if materia is None:
        imprimir_error("Materia no encontrada")
    elif confirmar(f"¿Eliminar {materia.nombre}?"):
        mostrar_resultado(*materias.eliminar(id_registro))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# ---------------------------------------------------------------------
# MATRÍCULAS
# ---------------------------------------------------------------------
def crear_matricula():
    imprimir_titulo("MATRICULAR ESTUDIANTE")
    imprimir_info("Estudiantes registrados:")
    mostrar_lista(estudiantes.leer())
    imprimir_info("Materias disponibles:")
    mostrar_lista(materias.leer())
    datos = {
        "estudiante_id": pedir_entero("\nID del estudiante: "),
        "materia_id": pedir_entero("ID de la materia: "),
        "periodo": input("Período (ej.: 2026-1): ").strip(),
        "nota": 0,  # se registra/corrige desde la opción Registrar nota
    }
    mostrar_resultado(*matriculas.crear(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRÍCULAS")
    mostrar_lista(matriculas.leer(), "Todavía no hay matrículas")
    pausa()


def registrar_nota():
    imprimir_titulo("REGISTRAR NOTA")
    id_registro = pedir_entero("ID de matrícula: ")
    nota = input("Nota entre 0 y 20: ").strip()
    mostrar_resultado(*matriculas.registrar_nota(id_registro, nota))
    pausa()


def ver_certificado():
    imprimir_titulo("CERTIFICADO")
    texto = matriculas.certificado(pedir_entero("ID de matrícula: "))
    if texto is None:
        imprimir_error("Matrícula no encontrada")
    else:
        print(texto)
    pausa()


def retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")
    id_registro = pedir_entero("ID de matrícula: ")
    if matriculas.obtener(id_registro) is None:
        imprimir_error("Matrícula no encontrada")
    elif confirmar("¿Retirar y devolver el cupo?"):
        mostrar_resultado(*matriculas.retirar_matricula(id_registro))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def ver_matriculas_estudiante():
    imprimir_titulo("MATRÍCULAS DE UN ESTUDIANTE")
    id_registro = pedir_entero("ID del estudiante: ")
    grupos = matriculas.matriculas_por_estudiante()
    mostrar_lista(grupos.get(id_registro, []), "Sin matrículas para ese estudiante")
    pausa()


def ver_promedio_estudiante():
    imprimir_titulo("PROMEDIO DE ESTUDIANTE")
    id_registro = pedir_entero("ID del estudiante: ")
    if estudiantes.obtener(id_registro) is None:
        imprimir_error("Ese estudiante no existe")
    else:
        promedio = matriculas.promedio_de_estudiante(id_registro)
        if promedio is None:
            imprimir_info("El estudiante no tiene matrículas")
        else:
            imprimir_info(f"Promedio de notas registradas: {promedio:.2f}")
    pausa()


def resumen():
    imprimir_titulo("RESUMEN ACADÉMICO")
    print(f"  Estudiantes       : {len(estudiantes.leer())}")
    print(f"  Carreras distintas: {', '.join(estudiantes.carreras()) or '-'}")
    print(f"  Materias          : {len(materias.leer())}")
    sin_cupo = materias.materias_sin_cupo()
    print(f"  Materias sin cupo : {', '.join(m.nombre for m in sin_cupo) or 'ninguna'}")
    print(f"  Matrículas        : {len(matriculas.leer())}")
    print(f"  Aprobadas         : {matriculas.aprobadas()}")
    pausa()


# DICCIONARIOS: tecla -> TUPLA (etiqueta, funcion).
MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por ID", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por ID", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Matricular", crear_matricula),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Registrar nota", registrar_nota),
    "4": ("Ver certificado", ver_certificado),
    "5": ("Retirar matrícula", retirar_matricula),
    "6": ("Matrículas por estudiante", ver_matriculas_estudiante),
    "7": ("Promedio de estudiante", ver_promedio_estudiante),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()
        tecla = input("Opción: ").strip()
        if tecla not in opciones:
            imprimir_error("Opción no válida")
            pausa()
            continue
        _texto, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO · MVC + JSON")
        print("  1. Estudiantes")
        print("  2. Materias")
        print("  3. Matrículas")
        print("  4. Resumen")
        print("  0. Salir\n")
        tecla = input("Opción: ").strip()
        if tecla == "1":
            ejecutar_menu("ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("MATERIAS", MENU_MATERIAS)
        elif tecla == "3":
            ejecutar_menu("MATRÍCULAS", MENU_MATRICULAS)
        elif tecla == "4":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego!")
            break
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
