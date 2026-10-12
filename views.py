"""CONTROLADORES (C de MVC): validan reglas, hacen CRUD y usan GestorJSON.

No se usa input() ni print() aqui: de eso se encarga main.py.
Se conserva el estilo de clases Controller del proyecto de ventas original.
"""
from abc import ABC, abstractmethod
from pathlib import Path

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

DATOS = Path(__file__).resolve().parent / "data"


class CrudBase(ABC):
    """Todos los controladores concretos implementan el mismo contrato CRUD."""

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


class EstudianteController(CrudBase):
    """CRUD de estudiantes y comprobacion de carnet/email unicos."""

    def __init__(self, archivo=None):
        self.gestor = GestorJSON(archivo or DATOS / "estudiantes.json")
        self.lista = [Estudiante.desde_diccionario(d) for d in self.gestor.leer()]
        self.matriculas = None

    def vincular_matriculas(self, controlador):
        self.matriculas = controlador

    def guardar(self):
        datos = [alumno.a_diccionario() for alumno in self.lista]
        return self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        # TUPLA: conjunto fijo de campos obligatorios.
        for campo in ("nombre", "apellido", "email", "carnet"):
            if campo in datos or id_actual is None:
                if not str(datos.get(campo, "")).strip():
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return "El email no tiene un formato válido"
            # SET: evita buscar repetidos recorriendo cada vez la lista.
            usados = {e.email.lower() for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ya existe un estudiante con ese email"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            # SET: los carnets deben ser únicos.
            usados = {e.carnet.upper() for e in self.lista if e.id != id_actual}
            if carnet in usados:
                return "Ya existe un estudiante con ese carnet"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_registro):
        for alumno in self.lista:
            if alumno.id == id_registro:
                return alumno
        return None

    def buscar(self, texto):
        texto = str(texto).strip().lower()
        if not texto:
            return []
        # TUPLA: los campos por los que buscamos se mantienen fijos.
        campos = ("nombre", "apellido", "email", "carnet", "carrera")
        return [e for e in self.lista
                if any(texto in str(getattr(e, campo)).lower() for campo in campos)]

    def siguiente(self):
        return max((e.id for e in self.lista), default=0) + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error  # TUPLA: (exito, mensaje)
        alumno = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos["carnet"]).strip().upper(),
            str(datos.get("carrera", "")).strip().title(),
        )
        self.lista.append(alumno)  # LISTA: crece cada vez que hay un registro.
        if not self.guardar():
            self.lista.remove(alumno)
            return False, "No fue posible guardar el estudiante en JSON"
        return True, f"Estudiante creado: {alumno.etiqueta()}"

    def actualizar(self, id_registro, cambios):
        alumno = self.obtener(id_registro)
        if alumno is None:
            return False, "Estudiante no encontrado"
        if not cambios:
            return False, "No se indicó ningún cambio"
        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        if set(cambios) - permitidos:
            return False, "Se enviaron campos no permitidos"
        error = self.validar(cambios, id_registro)
        if error:
            return False, error
        anteriores = {campo: getattr(alumno, campo) for campo in cambios}
        for campo, valor in cambios.items():
            valor = str(valor).strip()
            if campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            else:
                valor = valor.title()
            setattr(alumno, campo, valor)
        if not self.guardar():
            for campo, valor in anteriores.items():
                setattr(alumno, campo, valor)
            return False, "No fue posible actualizar el archivo JSON"
        return True, f"Estudiante {id_registro} actualizado"

    def eliminar(self, id_registro):
        alumno = self.obtener(id_registro)
        if alumno is None:
            return False, "Estudiante no encontrado"
        if self.matriculas and any(m.estudiante_id == id_registro
                                  for m in self.matriculas.leer()):
            return False, "Primero retire las matrículas del estudiante"
        posicion = self.lista.index(alumno)
        self.lista.pop(posicion)
        if not self.guardar():
            self.lista.insert(posicion, alumno)
            return False, "No fue posible guardar la eliminación"
        return True, f"Estudiante {id_registro} eliminado"

    def carreras(self):
        # SET: una carrera se muestra una sola vez; sorted permite ordenarlas.
        return sorted({e.carrera for e in self.lista if e.carrera})


class MateriaController(CrudBase):
    """CRUD de materias; valida código, créditos y cupos."""

    def __init__(self, archivo=None):
        self.gestor = GestorJSON(archivo or DATOS / "materias.json")
        self.lista = [Materia.desde_diccionario(d) for d in self.gestor.leer()]
        self.matriculas = None

    def vincular_matriculas(self, controlador):
        self.matriculas = controlador

    def guardar(self):
        return self.gestor.guardar([m.a_diccionario() for m in self.lista])

    def validar(self, datos, id_actual=None):
        for campo in ("nombre", "codigo", "creditos"):
            if campo in datos or id_actual is None:
                if not str(datos.get(campo, "")).strip():
                    return f"El campo {campo} es obligatorio"
        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            # SET: los códigos de materia deben ser únicos.
            usados = {m.codigo.upper() for m in self.lista if m.id != id_actual}
            if codigo in usados:
                return "El código de materia ya existe"
        if "creditos" in datos:
            try:
                creditos = int(str(datos["creditos"]).strip())
                if not 1 <= creditos <= 10:
                    return "Los créditos deben estar entre 1 y 10"
            except (ValueError, TypeError):
                return "Los créditos deben ser un número entero entre 1 y 10"
        if "cupos" in datos:
            try:
                cupos = int(str(datos["cupos"]).strip())
                if not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
                    return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"
            except (ValueError, TypeError):
                return "Los cupos deben ser un número entero"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_registro):
        for materia in self.lista:
            if materia.id == id_registro:
                return materia
        return None

    def buscar(self, texto):
        texto = str(texto).strip().lower()
        if not texto:
            return []
        return [m for m in self.lista
                if texto in m.nombre.lower() or texto in m.codigo.lower()]

    def siguiente(self):
        return max((m.id for m in self.lista), default=0) + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error
        materia = Materia(
            self.siguiente(), str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            int(datos["creditos"]), int(datos.get("cupos", Materia.CUPOS_MAXIMOS)),
        )
        self.lista.append(materia)
        if not self.guardar():
            self.lista.remove(materia)
            return False, "No se pudo guardar la materia"
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_registro, cambios):
        materia = self.obtener(id_registro)
        if materia is None:
            return False, "Materia no encontrada"
        if not cambios:
            return False, "No se indicó ningún cambio"
        permitidos = {"nombre", "codigo", "creditos", "cupos"}
        if set(cambios) - permitidos:
            return False, "Se enviaron campos no permitidos"
        error = self.validar(cambios, id_registro)
        if error:
            return False, error
        if "cupos" in cambios and self.matriculas:
            # Cupos disponibles + matrículas activas no deben pasar de 30.
            matriculados = sum(1 for m in self.matriculas.leer()
                               if m.materia_id == id_registro)
            if int(cambios["cupos"]) + matriculados > Materia.CUPOS_MAXIMOS:
                return False, "Los cupos disponibles más los ocupados superarían 30"
        anteriores = {campo: getattr(materia, campo) for campo in cambios}
        for campo, valor in cambios.items():
            if campo in ("cupos", "creditos"):
                valor = int(valor)
            elif campo == "codigo":
                valor = str(valor).strip().upper()
            else:
                valor = str(valor).strip().title()
            setattr(materia, campo, valor)
        if not self.guardar():
            for campo, valor in anteriores.items():
                setattr(materia, campo, valor)
            return False, "No se pudo guardar la actualización"
        return True, f"Materia {id_registro} actualizada"

    def eliminar(self, id_registro):
        materia = self.obtener(id_registro)
        if materia is None:
            return False, "Materia no encontrada"
        if self.matriculas and any(m.materia_id == id_registro
                                  for m in self.matriculas.leer()):
            return False, "Primero retire las matrículas de esta materia"
        posicion = self.lista.index(materia)
        self.lista.pop(posicion)
        if not self.guardar():
            self.lista.insert(posicion, materia)
            return False, "No se pudo guardar la eliminación"
        return True, f"Materia {id_registro} eliminada"

    def materias_sin_cupo(self):
        return [m for m in self.lista if not m.hay_cupo()]


class MatriculaController(CrudBase):
    """Relaciona estudiantes con materias, controla cupos y registra notas."""

    def __init__(self, estudiantes, materias, archivo=None):
        # Reutiliza EXACTAMENTE los controladores de main.py.
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo or DATOS / "matriculas.json")
        self.lista = [Matricula.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        return self.gestor.guardar([m.a_diccionario() for m in self.lista])

    def validar(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id"))
            materia_id = int(datos.get("materia_id"))
        except (ValueError, TypeError):
            return "Los ID de estudiante y materia deben ser números enteros"
        periodo = str(datos.get("periodo", "")).strip()
        if not periodo:
            return "El período es obligatorio (ejemplo: 2026-1)"
        if self.estudiantes.obtener(estudiante_id) is None:
            return "El estudiante no existe"
        materia = self.materias.obtener(materia_id)
        if materia is None:
            return "La materia no existe"
        if not materia.hay_cupo():
            return "La materia no tiene cupos disponibles"
        # Validación conjunta: estudiante + materia + periodo.
        for m in self.lista:
            if (m.estudiante_id == estudiante_id and
                    m.materia_id == materia_id and m.periodo == periodo):
                return "Ese estudiante ya está matriculado en esa materia y período"
        if not Materia.es_nota_valida(datos.get("nota", 0)):
            return "La nota debe ser numérica y estar entre 0 y 20"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_registro):
        for matricula in self.lista:
            if matricula.id == id_registro:
                return matricula
        return None

    def buscar(self, texto):
        texto = str(texto).strip()
        return [m for m in self.lista if texto and texto in m.periodo]

    def siguiente(self):
        return max((m.id for m in self.lista), default=0) + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error
        materia = self.materias.obtener(int(datos["materia_id"]))
        matricula = Matricula(
            self.siguiente(), int(datos["estudiante_id"]), materia.id,
            str(datos["periodo"]).strip(), float(datos.get("nota", 0)),
        )
        if not materia.ocupar_cupo():
            return False, "Ya no hay cupos disponibles"
        if not self.materias.guardar():
            materia.liberar_cupo()
            return False, "No se pudo guardar el cupo de la materia"
        self.lista.append(matricula)
        if not self.guardar():
            self.lista.remove(matricula)
            materia.liberar_cupo()
            self.materias.guardar()
            return False, "No se pudo guardar la matrícula"
        return True, f"Matrícula {matricula.id} creada y un cupo ocupado"

    def actualizar(self, id_registro, datos):
        if set(datos) != {"nota"}:
            return False, "Las matrículas se actualizan con registrar_nota()"
        return self.registrar_nota(id_registro, datos["nota"])

    def eliminar(self, id_registro):
        return self.retirar_matricula(id_registro)

    def registrar_nota(self, id_registro, nota):
        matricula = self.obtener(id_registro)
        if matricula is None:
            return False, "Matrícula no encontrada"
        if not Materia.es_nota_valida(nota):
            return False, "La nota debe estar entre 0 y 20"
        anterior = matricula.nota
        matricula.nota = float(nota)
        if not self.guardar():
            matricula.nota = anterior
            return False, "No se pudo guardar la nota"
        return True, f"Nota registrada: {matricula.nota:g} ({matricula.estado()})"

    def retirar_matricula(self, id_registro):
        matricula = self.obtener(id_registro)
        if matricula is None:
            return False, "Matrícula no encontrada"
        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            if not materia.liberar_cupo():
                return False, "El cupo de esa materia ya está en el máximo"
            if not self.materias.guardar():
                materia.ocupar_cupo()
                return False, "No se pudo devolver el cupo"
        posicion = self.lista.index(matricula)
        self.lista.pop(posicion)
        if not self.guardar():
            self.lista.insert(posicion, matricula)
            if materia is not None:
                materia.ocupar_cupo()
                self.materias.guardar()
            return False, "No se pudo retirar la matrícula"
        return True, f"Matrícula {id_registro} retirada; cupo liberado"

    def certificado(self, id_registro):
        matricula = self.obtener(id_registro)
        if matricula is None:
            return None
        # DICCIONARIO ÍNDICE {id: objeto}: une las tres entidades por id.
        indice_estudiantes = {e.id: e for e in self.estudiantes.leer()}
        indice_materias = {m.id: m for m in self.materias.leer()}
        alumno = indice_estudiantes.get(matricula.estudiante_id)
        materia = indice_materias.get(matricula.materia_id)
        alumno_nombre = alumno.nombre_completo() if alumno else "No encontrado"
        carnet = alumno.carnet if alumno else "-"
        materia_nombre = materia.nombre if materia else "No encontrada"
        codigo = materia.codigo if materia else "-"
        creditos = materia.creditos if materia else "-"
        return (
            f"CERTIFICADO #{matricula.id}   período: {matricula.periodo}\n"
            f"Estudiante: {alumno_nombre} ({carnet})\n"
            f"Materia   : {materia_nombre} ({codigo}) · {creditos} créditos\n"
            + "-" * 44 + "\n"
            + f"Nota      : {matricula.nota:g}\n"
            + f"Estado    : {matricula.estado()}\n"
            + f"Fecha     : {matricula.fecha}"
        )

    def matriculas_por_estudiante(self):
        # DICCIONARIO DE LISTAS: cada estudiante tiene una lista de matrículas.
        agrupadas = {}
        for matricula in self.lista:
            agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
        return agrupadas

    def promedio_de_estudiante(self, estudiante_id):
        # LISTA: notas del estudiante seleccionado (incluye 0 si aún no registra nota).
        notas = [m.nota for m in self.lista if m.estudiante_id == estudiante_id]
        return sum(notas) / len(notas) if notas else None

    def aprobadas(self):
        return sum(1 for m in self.lista if m.esta_aprobada())
