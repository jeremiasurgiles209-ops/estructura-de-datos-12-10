"""Pruebas de comportamiento usando JSON temporales (no alteran data/)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models import Estudiante, Materia, Matricula, ModeloBase  # noqa: E402
from views import EstudianteController, MateriaController, MatriculaController  # noqa: E402


class PruebasSistemaAcademico(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        carpeta = Path(self.temporal.name)
        self.rutas = [carpeta / n for n in ("estudiantes.json", "materias.json", "matriculas.json")]
        self.e = EstudianteController(self.rutas[0])
        self.m = MateriaController(self.rutas[1])
        self.r = MatriculaController(self.e, self.m, self.rutas[2])
        self.e.vincular_matriculas(self.r)
        self.m.vincular_matriculas(self.r)

    def tearDown(self):
        self.temporal.cleanup()

    def alumno(self, carnet="EST1", email="ana@u.edu"):
        return self.e.crear({"nombre": "Ana", "apellido": "Pérez", "email": email,
                             "carnet": carnet, "carrera": "Software"})

    def materia(self, codigo="MAT101", cupos="2"):
        return self.m.crear({"nombre": "Cálculo I", "codigo": codigo,
                             "creditos": "4", "cupos": cupos})

    def test_modelos_herencia_y_conversion(self):
        self.assertTrue(issubclass(Estudiante, ModeloBase))
        alumno = Estudiante(2, "Ana", "Pérez", "a@u.edu", "EST1", "Software")
        reconstruido = Estudiante.desde_diccionario(alumno.a_diccionario())
        self.assertEqual(reconstruido.etiqueta(), alumno.etiqueta())
        materia = Materia.desde_diccionario(Materia(3, "Álgebra", "MAT2", 4, 30).a_diccionario())
        self.assertIn("Álgebra", str(materia))
        m = Matricula.desde_diccionario(Matricula(4, 2, 3, "2026-1", 14).a_diccionario())
        self.assertEqual(m.estado(), "Aprobado")
        self.assertEqual(len([c for c in ModeloBase.__dict__ if c == "desde_diccionario"]), 1)

    def test_estudiante_crud_unicidad_y_json(self):
        self.assertTrue(self.alumno()[0])
        self.assertFalse(self.alumno("EST1", "distinto@u.edu")[0])
        self.assertFalse(self.alumno("EST2", "ANA@U.EDU")[0])
        self.assertFalse(self.alumno("EST3", "invalido")[0])
        self.assertTrue(self.alumno("EST2", "luis@u.edu")[0])
        self.assertEqual(len(self.e.buscar("software")), 2)
        self.assertEqual(self.e.carreras(), ["Software"])
        self.assertTrue(self.e.actualizar(2, {"carnet": "EST4"})[0])
        self.assertEqual(self.e.obtener(2).carnet, "EST4")
        self.assertFalse(self.e.actualizar(2, {"email": "ana@u.edu"})[0])
        self.assertTrue(self.e.eliminar(2)[0])
        self.assertEqual(len(self.e.leer()), 1)
        guardados = json.loads(self.rutas[0].read_text(encoding="utf-8"))
        self.assertEqual(guardados[0]["carnet"], "EST1")

    def test_materia_crud_restricciones(self):
        self.assertTrue(self.materia()[0])
        self.assertFalse(self.materia("MAT101")[0])
        self.assertFalse(self.m.crear({"nombre": "Prueba", "codigo": "MAT5",
                                      "creditos": 11, "cupos": 20})[0])
        self.assertFalse(self.m.crear({"nombre": "Prueba", "codigo": "MAT5",
                                      "creditos": 3, "cupos": 31})[0])
        self.assertTrue(self.m.actualizar(1, {"creditos": "5"})[0])
        self.assertEqual(self.m.obtener(1).creditos, 5)
        self.assertEqual(len(self.m.buscar("mat101")), 1)
        self.assertTrue(self.m.eliminar(1)[0])

    def test_matricular_notas_certificado_retiro_persistencia(self):
        self.assertTrue(self.alumno()[0])
        self.assertTrue(self.materia()[0])
        datos = {"estudiante_id": 1, "materia_id": 1, "periodo": "2026-1"}
        self.assertTrue(self.r.crear(datos)[0])
        self.assertEqual(self.m.obtener(1).cupos, 1)
        self.assertFalse(self.r.crear(datos)[0])
        self.assertFalse(self.e.eliminar(1)[0])
        self.assertFalse(self.m.eliminar(1)[0])
        self.assertFalse(self.r.registrar_nota(1, 21)[0])
        self.assertTrue(self.r.registrar_nota(1, "16.5")[0])
        self.assertTrue(self.r.obtener(1).esta_aprobada())
        self.assertIn("Aprobado", self.r.certificado(1))
        self.assertIn("EST1", self.r.certificado(1))
        self.assertEqual(len(self.r.matriculas_por_estudiante()[1]), 1)
        self.assertEqual(self.r.promedio_de_estudiante(1), 16.5)
        self.assertEqual(self.r.aprobadas(), 1)
        documentos = json.loads(self.rutas[2].read_text(encoding="utf-8"))
        self.assertNotIn("estado", documentos[0])
        recargado = MatriculaController(self.e, self.m, self.rutas[2])
        self.assertEqual(recargado.obtener(1).nota, 16.5)
        self.assertTrue(self.r.retirar_matricula(1)[0])
        self.assertEqual(self.m.obtener(1).cupos, 2)
        self.assertEqual(self.r.leer(), [])
        self.assertTrue(self.e.eliminar(1)[0])
        self.assertTrue(self.m.eliminar(1)[0])

    def test_sin_cupos_y_promedios(self):
        self.alumno()
        self.materia(cupos="1")
        self.assertTrue(self.r.crear({"estudiante_id": 1, "materia_id": 1,
                                      "periodo": "2026-1"})[0])
        self.assertEqual(len(self.m.materias_sin_cupo()), 1)
        self.assertFalse(self.r.crear({"estudiante_id": 1, "materia_id": 1,
                                       "periodo": "2026-2"})[0])
        self.assertEqual(self.r.promedio_de_estudiante(1), 0)
        self.assertTrue(self.r.retirar_matricula(1)[0])
        self.assertEqual(len(self.m.materias_sin_cupo()), 0)
        self.assertIsNone(self.r.promedio_de_estudiante(1))

    def test_static_notas(self):
        self.assertTrue(Materia.es_nota_valida(0))
        self.assertTrue(Materia.es_nota_valida("20"))
        self.assertFalse(Materia.es_nota_valida(-0.1))
        self.assertFalse(Materia.es_nota_valida(20.1))
        self.assertFalse(Materia.es_nota_valida("hola"))
        self.assertFalse(Materia.es_nota_valida(float("nan")))


if __name__ == "__main__":
    unittest.main()
