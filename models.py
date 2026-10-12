"""MODELOS (M de MVC): clases, herencia y polimorfismo.

Los modelos no usan print, input ni abren archivos JSON.
"""
from datetime import date


class ModeloBase:
    """Clase padre: comparte id, conversiones y representacion."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    # UNICO metodo de clase del proyecto: todos los modelos lo heredan.
    @classmethod
    def desde_diccionario(cls, datos):
        copia = dict(datos)
        id_registro = copia.pop("id")
        return cls(id_registro, **copia)

    def a_diccionario(self):
        return {"id": self.id}

    def etiqueta(self):
        return f"registro {self.id}"

    def __str__(self):
        # Polimorfismo: cada clase hija tiene su propia etiqueta().
        return f"[{self.id}] {self.etiqueta()}"


class Persona(ModeloBase):
    """Clase padre de Estudiante. Se reutiliza del ejemplo de ventas."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona, y agrega carnet y carrera."""

    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.carnet} · {self.carrera or 'sin carrera'}"


class Materia(ModeloBase):
    """Equivale a Producto: los cupos se comportan como el stock."""

    CUPOS_MAXIMOS = 30  # atributo de clase compartido
    NOTA_APROBACION = 14  # atributo de clase compartido

    def __init__(self, id_registro, nombre, codigo, creditos=0, cupos=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor):
        """Regla independiente de cualquier instancia de Materia."""
        try:
            numero = float(valor)
            return 0 <= numero <= 20  # tambien rechaza NaN
        except (TypeError, ValueError, OverflowError):
            return False

    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if not self.hay_cupo():
            return False
        self.cupos -= 1
        return True

    def liberar_cupo(self):
        if self.cupos >= Materia.CUPOS_MAXIMOS:
            return False
        self.cupos += 1
        return True

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self):
        aviso = " · SIN CUPOS" if not self.hay_cupo() else ""
        return (f"{self.nombre} · {self.codigo} · {self.creditos} créditos "
                f"· {self.cupos} cupos{aviso}")


class Matricula(ModeloBase):
    """Relaciona un estudiante y una materia mediante sus ID."""

    def __init__(self, id_registro, estudiante_id, materia_id, periodo,
                 nota=0.0, fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = str(periodo)
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self):
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        # No se guarda en el JSON: se calcula siempre.
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        return (f"{self.periodo} · estudiante {self.estudiante_id} "
                f"· materia {self.materia_id} · nota {self.nota:g} "
                f"· {self.estado()}")
