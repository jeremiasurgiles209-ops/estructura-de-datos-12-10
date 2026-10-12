"""El almacenamiento JSON: unico modulo que lee y escribe archivos de datos."""
import json
import os


class GestorJSON:
    """Lee y guarda listas de diccionarios; adaptado de la guia de ventas."""

    def __init__(self, ruta):
        self.ruta = str(ruta)
        carpeta = os.path.dirname(self.ruta)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta)

    def leer(self):
        if not os.path.exists(self.ruta):
            return []
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def guardar(self, datos):
        try:
            # 'w' escribe la lista completa actualizada; 'a' dañaría este JSON.
            with open(self.ruta, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            return True
        except (TypeError, OSError):
            return False
