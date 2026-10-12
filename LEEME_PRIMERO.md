# Sistema académico en Python — MVC + JSON

Proyecto basado en el ejemplo de **ventas** de la guía del ingeniero. Usa `main.py` (vista), `views.py` (controladores), `models.py` (modelos) y `shared/json_manager.py` (persistencia). No necesita instalar librerías externas.

## Pasos EXACTOS en Windows y Visual Studio Code

1. **Descarga el archivo ZIP** que recibiste en ChatGPT. Guárdalo, por ejemplo, en **Descargas**.
2. **Clic derecho** sobre `sistema_academico_mvc.zip` → **Extraer todo...**. Elige, por ejemplo, tu **Escritorio**. **No ejecutes los archivos dentro del ZIP**; primero extráelos.
3. Verás una carpeta llamada `sistema_academico_mvc`. **Esa es tu carpeta de proyecto**; no necesitas crear los archivos uno por uno, ya están incluidos.
4. Abre **Visual Studio Code** → **Archivo** → **Abrir carpeta** → selecciona `sistema_academico_mvc` (la que tiene `main.py` dentro) → **Seleccionar carpeta**.
5. Mira a la izquierda en **Explorador**: deben aparecer `main.py`, `models.py`, `views.py`, `shared` y `data`.
6. Abre **Terminal** → **Nuevo terminal** (o Ctrl + ñ). Revisa que la ruta termina en `sistema_academico_mvc`.
7. En el terminal escribe `python --version`. Si no funciona, prueba `py --version`.
8. Inicia el proyecto escribiendo **`python main.py`**. Si tu PC usa `py`, entonces **`py main.py`**.
9. Selecciona el menú con un número y presiona Enter. Para volver al menú principal usa `0`.
10. Revisa `data/estudiantes.json`, `data/materias.json` y `data/matriculas.json`: los registros aparecerán ahí automáticamente. Para confirmar persistencia, sal con `0`, vuelve a ejecutar y lista los registros.

**Nota:** Si al abrir la carpeta solo aparece otra carpeta con el mismo nombre, abre esa subcarpeta: necesitas ver `main.py` directamente en el Explorador de VS Code.

## ¿Y si quiero crear los archivos manualmente?

Haz clic derecho sobre el Escritorio → **Nuevo > Carpeta** → ponle `sistema_academico_mvc` → abre esa carpeta en VS Code. En el Explorador de VS Code, usa **Nuevo archivo** para crear `main.py`, `models.py`, `views.py`; usa **Nueva carpeta** para crear `shared` y `data`. Dentro de `shared`, crea `__init__.py`, `json_manager.py`, `herramientas.py`; dentro de `data`, crea `estudiantes.json`, `materias.json`, `matriculas.json` y escribe `[]` en cada uno. Copia el código de cada archivo en el archivo del mismo nombre. **Como ya recibes el ZIP terminado, este método manual es opcional.**

## Primera prueba (con ejemplos ficticios)

1. Menú `1 > 1`: crea estudiante `Ana`, `Pérez`, email `ana@ejemplo.com`, carnet `EST2026001`, carrera `Software`.
2. Menú `2 > 1`: crea materia `Cálculo I`, código `MAT101`, `4` créditos, `30` cupos.
3. Menú `3 > 1`: matricula al estudiante ID `1` en materia ID `1`, período `2026-1`. Se guarda una matrícula con nota inicial **0** y los cupos bajan de **30 a 29**.
4. Menú `3 > 3`: registra `16.5` a la matrícula ID `1`.
5. Menú `3 > 4`: muestra el **certificado** de la matrícula ID `1` con estado **Aprobado**.
6. Menú `3 > 5`: retira la matrícula ID `1`; los cupos vuelven a **30**.
7. Cierra con `0`, vuelve a ejecutar y comprueba que los JSON conservan los datos.

Una matrícula nueva tiene nota `0` hasta que uses **Registrar nota**. La guía del ingeniero define `Aprobado` para nota ≥ 14 y `Reprobado` para una nota menor, por eso antes de registrar la nota puede aparecer `Reprobado`. El promedio incluye esas notas iniciales de cero, por simplicidad del ejercicio.

## Función de cada archivo

| Archivo | Qué hace |
| --- | --- |
| `main.py` | **Vista**: menú, pide datos por `input()` y muestra información con `print()`. |
| `models.py` | **Modelo**: `ModeloBase`, `Persona`, `Estudiante`, `Materia`, `Matricula`. Define atributos y métodos. |
| `views.py` | **Controlador**: CRUD, validaciones, relaciones, notas, cupos y certificados. Conserva la estructura de clases `Controller` del ejemplo que compartiste. |
| `shared/json_manager.py` | `GestorJSON`: único que abre los JSON con `open()` y realiza `json.load()` y `json.dump()`. |
| `shared/herramientas.py` | Colores de terminal, confirmaciones y validación sencilla de email. |
| `data/*.json` | Almacenamiento persistente: listas de diccionarios de estudiantes, materias y matrículas. |
| `tests/test_sistema.py` | Pruebas automáticas del funcionamiento, en un directorio temporal; NO modifica tus datos reales. |

## Conceptos para explicar al ingeniero

- **Herencia:** `Estudiante(Persona)` usa `super()` en el constructor y en `a_diccionario()`. `Persona` hereda de `ModeloBase`; `Materia` y `Matricula` también heredan de `ModeloBase`.
- **Método de clase:** `ModeloBase.desde_diccionario()` tiene `@classmethod`: convierte un registro leído del JSON en objeto, a través de `cls(...)`. Ninguna hija lo vuelve a implementar.
- **Método estático:** `Materia.es_nota_valida(valor)` tiene `@staticmethod`, porque para saber si una nota está entre 0 y 20 no necesita los datos de una materia particular.
- **Atributos de clase:** `Materia.CUPOS_MAXIMOS = 30` y `Materia.NOTA_APROBACION = 14` aplican igual a todas las materias.
- **Polimorfismo:** `__str__()` llama a `etiqueta()`. Cada modelo tiene su propia `etiqueta()`; por eso `mostrar_lista()` en `main.py` funciona con estudiantes, materias y matrículas sin condicionales de tipo.
- **Listas:** almacenan registros en memoria (`self.lista`).
- **Conjuntos `set`:** detectan carnets, emails y códigos repetidos; `carreras()` los usa para no repetir carreras.
- **Tuplas:** contienen nombres fijos de campos y retornos `(exito, mensaje)`.
- **Diccionarios:** cada registro JSON es un diccionario; `certificado()` usa un índice `{id: objeto}` y `matriculas_por_estudiante()` usa un diccionario de listas con `setdefault()`.
- **CRUD:** crear, leer, buscar, actualizar y eliminar estudiantes y materias; matrículas permiten registrar, consultar, registrar nota y retirar.
- **Relaciones:** `matriculas.json` guarda `estudiante_id` y `materia_id`, no vuelve a copiar todos los nombres; el certificado busca por esos IDs.
- **Persistencia:** `gestor.leer()` usa modo `r`; `gestor.guardar()` usa modo `w` para **reescribir toda la lista JSON válida**, no agrega cadenas con modo `a` (que podrían dañarla).

## Pruebas automáticas opcionales

Abre la terminal en la carpeta del proyecto y escribe:

```powershell
python -m unittest discover -s tests -v
```

Si la computadora usa el lanzador de Python de Windows, reemplaza `python` por `py`.

## Advertencias importantes

- Los archivos `data/*.json` tienen `[]` al principio: significa **lista vacía**, no es un error. El programa los llena cuando creas registros.
- No pegues comentarios `//` dentro de JSON: JSON no admite comentarios.
- No agregues la misma matrícula del mismo alumno, materia y período dos veces.
- No elimines estudiantes o materias que aún tienen matrículas: primero retíralas.
- Si modificas manualmente los JSON con datos inconsistentes, el programa no puede garantizar la integridad.
- La guía del ingeniero muestra en parte funciones sueltas como controladores; aquí usamos **clases Controller** porque son las que aparecían en el código de ventas que proporcionaste. La funcionalidad y las capas MVC son equivalentes, pero conviene confirmar con el docente si exige literalmente los nombres de sus funciones.
