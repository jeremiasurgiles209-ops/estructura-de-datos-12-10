from abc import ABC, abstractmethod

from models import Cliente, Producto, Venta, Devolucion
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
# Solo dice QUÉ métodos debe tener todo controlador.
# CÓMO se hace cada uno lo escribe cada controlador, de la forma más simple.
class CrudBase(ABC):

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


# =====================================================================
# CONTROLADOR DE CLIENTES
# =====================================================================
class ClienteController(CrudBase):

    def __init__(self, archivo="data/clientes.json"):
        self.gestor = GestorJSON(archivo)

        # Leemos el JSON y convertimos cada diccionario en un objeto Cliente
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Cliente.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for cliente in self.lista:
            datos.append(cliente.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Devuelve un mensaje de error, o None si todo está bien."""
        # Al crear hay que traer los tres obligatorios; al actualizar, solo lo que cambia
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO con los emails de los OTROS clientes
            usados = {c.email for c in self.lista if c.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        telefono = str(datos.get("telefono", "")).strip()
        if telefono != "" and not telefono.isdigit():
            return "El teléfono solo puede tener números"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_cliente):
        for cliente in self.lista:
            if cliente.id == id_cliente:
                return cliente
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for cliente in self.lista:
            if (texto in cliente.nombre.lower()
                    or texto in cliente.apellido.lower()
                    or texto in cliente.email
                    or texto in cliente.telefono
                    or texto in cliente.ciudad.lower()):
                encontrados.append(cliente)
        return encontrados

    def siguiente(self):
        mayor = 0
        for cliente in self.lista:
            if cliente.id > mayor:
                mayor = cliente.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        cliente = Cliente(self.siguiente(),
                          str(datos["nombre"]).strip().title(),
                          str(datos["apellido"]).strip().title(),
                          str(datos["email"]).strip().lower(),
                          str(datos.get("telefono", "")).strip(),
                          str(datos.get("ciudad", "")).strip().title())
        self.lista.append(cliente)
        self.guardar()
        return True, f"Cliente creado: {cliente.etiqueta()}"

    def actualizar(self, id_cliente, datos):
        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe un cliente con id {id_cliente}"
        if not datos:
            return False, "No se indicó ningún cambio"

        # DIFERENCIA de conjuntos: campos que no existen en un cliente
        permitidos = {"nombre", "apellido", "email", "telefono", "ciudad"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        # Se valida ANTES de tocar el objeto: si algo falla, no cambia nada
        error = self.validar(datos, id_cliente)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "ciudad"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            setattr(cliente, campo, valor)

        self.guardar()
        return True, f"Cliente {id_cliente} actualizado"

    def eliminar(self, id_cliente):
        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe un cliente con id {id_cliente}"

        self.lista.remove(cliente)
        self.guardar()
        return True, f"Cliente {id_cliente} eliminado"

    # --- propio de clientes ---
    def ciudades(self):
        """CONJUNTO de ciudades: sin repetidos. sorted() lo devuelve como lista."""
        return sorted({c.ciudad for c in self.lista if c.ciudad != ""})


# =====================================================================
# CONTROLADOR DE PRODUCTOS
# =====================================================================
class ProductoController(CrudBase):

    def __init__(self, archivo="data/productos.json"):
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Producto.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for producto in self.lista:
            datos.append(producto.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "precio"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        # es_precio_valido es el método ESTÁTICO de Producto
        if "precio" in datos and not Producto.es_precio_valido(datos["precio"]):
            return f"Precio inválido: '{datos['precio']}' (debe ser un número mayor a 0)"

        stock = str(datos.get("stock", "")).strip()
        if stock != "" and not stock.isdigit():
            return "El stock debe ser un número entero positivo"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otro in self.lista:
                if otro.nombre == nombre and otro.id != id_actual:
                    return f"Ya existe un producto llamado {nombre}"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_producto):
        for producto in self.lista:
            if producto.id == id_producto:
                return producto
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for producto in self.lista:
            if texto in producto.nombre.lower():
                encontrados.append(producto)
        return encontrados

    def siguiente(self):
        mayor = 0
        for producto in self.lista:
            if producto.id > mayor:
                mayor = producto.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        # Si no escribieron el stock, empieza en 0
        stock = str(datos.get("stock", "")).strip()
        producto = Producto(self.siguiente(),
                            str(datos["nombre"]).strip().title(),
                            float(datos["precio"]),
                            int(stock) if stock != "" else 0)
        self.lista.append(producto)
        self.guardar()
        return True, f"Producto creado: {producto.etiqueta()}"

    def actualizar(self, id_producto, datos):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe un producto con id {id_producto}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "precio", "stock"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_producto)
        if error:
            return False, error

        if "nombre" in datos:
            producto.nombre = str(datos["nombre"]).strip().title()
        if "precio" in datos:
            producto.precio = float(datos["precio"])
        if "stock" in datos:
            producto.stock = int(datos["stock"])

        self.guardar()
        return True, f"Producto {id_producto} actualizado"

    def eliminar(self, id_producto):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe un producto con id {id_producto}"

        self.lista.remove(producto)
        self.guardar()
        return True, f"Producto {id_producto} eliminado"

    # --- propio de productos ---
    def con_stock_bajo(self):
        bajos = []
        for producto in self.lista:
            if producto.stock_bajo():
                bajos.append(producto)
        return bajos


# =====================================================================
# CONTROLADOR DE VENTAS
# =====================================================================
class VentaController(CrudBase):

    def __init__(self, clientes, productos, archivo="data/ventas.json"):
        # La venta USA a los otros dos controladores.
        # Hay que pasarle los MISMOS que usa main.py.
        self.clientes = clientes
        self.productos = productos
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Venta.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for venta in self.lista:
            datos.append(venta.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            cliente_id = int(datos.get("cliente_id", 0))
            producto_id = int(datos.get("producto_id", 0))
            cantidad = int(datos.get("cantidad", 0))
        except (TypeError, ValueError):
            return "cliente_id, producto_id y cantidad deben ser números enteros"

        if cantidad <= 0:
            return "La cantidad debe ser mayor a 0"
        if self.clientes.obtener(cliente_id) is None:
            return f"No existe un cliente con id {cliente_id}"

        producto = self.productos.obtener(producto_id)
        if producto is None:
            return f"No existe un producto con id {producto_id}"
        if not producto.hay_stock(cantidad):
            return (f"Stock insuficiente de {producto.nombre}: "
                    f"hay {producto.stock}, piden {cantidad}")
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_venta):
        for venta in self.lista:
            if venta.id == id_venta:
                return venta
        return None

    def buscar(self, texto):
        # Las ventas se buscan por fecha, ej: "2026-09"
        texto = texto.strip()
        encontradas = []
        if texto == "":
            return encontradas

        for venta in self.lista:
            if texto in venta.fecha:
                encontradas.append(venta)
        return encontradas

    def siguiente(self):
        mayor = 0
        for venta in self.lista:
            if venta.id > mayor:
                mayor = venta.id
        return mayor + 1

    def crear(self, datos):
        # datos = {"cliente_id": 1, "producto_id": 2, "cantidad": 3}
        error = self.validar(datos)
        if error:
            return False, error

        producto = self.productos.obtener(int(datos["producto_id"]))
        venta = Venta(self.siguiente(),
                      int(datos["cliente_id"]),
                      producto.id,
                      int(datos["cantidad"]),
                      producto.precio)          # foto del precio del momento

        producto.descontar_stock(venta.cantidad)
        self.productos.guardar()                # guarda el stock nuevo en productos.json
        self.lista.append(venta)
        self.guardar()                          # guarda la venta en ventas.json
        return True, f"Venta {venta.id} registrada por ${venta.calcular_total():.2f}"

    def actualizar(self, id_venta, datos):
        # Una venta registrada no se modifica: se anula y se registra otra
        return False, "Las ventas no se pueden modificar: anúlela y registre otra"

    def eliminar(self, id_venta):
        """Anular una venta: se borra y el stock vuelve al producto."""
        venta = self.obtener(id_venta)
        if venta is None:
            return False, f"No existe la venta {id_venta}"

        producto = self.productos.obtener(venta.producto_id)
        if producto is not None:
            producto.devolver_stock(venta.cantidad)
            self.productos.guardar()

        self.lista.remove(venta)
        self.guardar()
        return True, f"Venta {id_venta} anulada y stock devuelto"

    # --- propio de ventas ---
    def comprobante(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return None

        cliente = self.clientes.obtener(venta.cliente_id)
        producto = self.productos.obtener(venta.producto_id)
        total = venta.calcular_total()

        texto = f"COMPROBANTE #{venta.id}   fecha: {venta.fecha}\n"
        texto += f"Cliente : {cliente.nombre_completo() if cliente else 'eliminado'}\n"
        texto += f"Producto: {producto.nombre if producto else 'eliminado'}\n"
        texto += f"Cantidad: {venta.cantidad} x ${venta.precio_unitario:.2f}\n"
        texto += "-" * 42 + "\n"
        texto += f"SUBTOTAL: ${total:.2f}\n"
        texto += f"TOTAL con IVA: ${Producto.con_iva(total):.2f}"
        return texto

    def ventas_por_cliente(self):
        """DICCIONARIO de LISTAS: {cliente_id: [ventas de ese cliente]}."""
        agrupadas = {}
        for venta in self.lista:
            if venta.cliente_id not in agrupadas:
                agrupadas[venta.cliente_id] = []
            agrupadas[venta.cliente_id].append(venta)
        return agrupadas

    def total_vendido(self):
        total = 0
        for venta in self.lista:
            total += venta.calcular_total()
        return round(total, 2)


# =====================================================================
# CONTROLADOR DE DEVOLUCIONES
# =====================================================================
class DevolucionController(CrudBase):
    """Devoluciones parciales de una venta.
    Recibe los MISMOS VentaController y ProductoController que usa main.py:
    el primero para buscar la venta, el segundo para regresar el stock."""

    def __init__(self, ventas, productos, archivo="data/devoluciones.json"):
        self.ventas = ventas
        self.productos = productos
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Devolucion.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for devolucion in self.lista:
            datos.append(devolucion.a_diccionario())
        self.gestor.guardar(datos)

    # ---------------- las 7 operaciones de CrudBase ----------------
    def leer(self):
        return self.lista

    def obtener(self, id_devolucion):
        for devolucion in self.lista:
            if devolucion.id == id_devolucion:
                return devolucion
        return None

    def buscar(self, texto):
        # Se busca por fecha ("2026-10") o por motivo ("defectuoso")
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas
        for devolucion in self.lista:
            if texto in devolucion.fecha or texto in devolucion.motivo:
                encontradas.append(devolucion)
        return encontradas

    def siguiente(self):
        mayor = 0
        for devolucion in self.lista:
            if devolucion.id > mayor:
                mayor = devolucion.id
        return mayor + 1

    def crear(self, datos):
        # datos = {"venta_id": 1, "cantidad": "2", "motivo": "arrepentido"}
        # Las validaciones van en el orden que pide la guía y ANTES de tocar nada.

        # 1) La venta existe
        try:
            venta_id = int(datos.get("venta_id", 0))
        except (TypeError, ValueError):
            return False, "El id de la venta debe ser un número entero"
        venta = self.ventas.obtener(venta_id)
        if venta is None:
            return False, f"No existe la venta {venta_id}"

        # 2) Está dentro del plazo
        if not Devolucion.dentro_del_plazo(venta.fecha):
            return False, (f"La venta {venta_id} está fuera del plazo de "
                           f"{Devolucion.DIAS_LIMITE} días para devolver")

        # 3) La cantidad es un entero > 0 y no mayor a lo disponible
        try:
            cantidad = int(datos.get("cantidad", 0))
        except (TypeError, ValueError):
            return False, "La cantidad debe ser un número entero"
        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0"
        disponible = self.cantidad_disponible(venta)
        if cantidad > disponible:
            return False, f"Solo se pueden devolver {disponible} unidad(es)"

        # 4) El motivo es válido
        motivo = str(datos.get("motivo", "")).strip().lower()
        if not Devolucion.es_motivo_valido(motivo):
            return False, (f"Motivo inválido: '{motivo}'. "
                           f"Use: {', '.join(Devolucion.MOTIVOS)}")

        # Todo bien: se crea la devolución con la foto del reembolso
        devolucion = Devolucion(self.siguiente(), venta.id, cantidad, motivo,
                                self.calcular_reembolso(venta, cantidad))

        # Solo si el producto sirve para volver a venderse, regresa al stock
        if devolucion.regresa_al_stock():
            producto = self.productos.obtener(venta.producto_id)
            if producto is not None:
                producto.devolver_stock(cantidad)
                self.productos.guardar()   # sin esto el stock se pierde al reiniciar

        self.lista.append(devolucion)
        self.guardar()
        return True, (f"Devolución {devolucion.id} registrada · "
                      f"reembolso ${devolucion.monto:.2f}")

    def actualizar(self, id_devolucion, datos):
        # Una devolución registrada es un hecho histórico: no se modifica
        return False, "Las devoluciones no se pueden modificar"

    def eliminar(self, id_devolucion):
        # Tampoco se borra: dejaría el stock y el dinero sin explicación
        return False, "Las devoluciones no se pueden eliminar"

    # ---------------- cálculos (NUNCA se guardan, se calculan) ----------------
    def devoluciones_de_venta(self, venta_id):
        encontradas = []
        for devolucion in self.lista:
            if devolucion.venta_id == venta_id:
                encontradas.append(devolucion)
        return encontradas

    def cantidad_devuelta(self, venta_id):
        total = 0
        for devolucion in self.devoluciones_de_venta(venta_id):
            total += devolucion.cantidad
        return total

    def cantidad_disponible(self, venta):
        # vendido - lo ya devuelto (siempre se resta lo anterior, no solo venta.cantidad)
        return venta.cantidad - self.cantidad_devuelta(venta.id)

    def calcular_reembolso(self, venta, cantidad):
        # Precio de la VENTA (no el actual del producto) + IVA, igual que el comprobante
        return Producto.con_iva(cantidad * venta.precio_unitario)

    def reembolsado_de_venta(self, venta_id):
        total = 0
        for devolucion in self.devoluciones_de_venta(venta_id):
            total += devolucion.monto
        return round(total, 2)

    # ---------------- reportes ----------------
    def nota_credito(self, id_devolucion):
        devolucion = self.obtener(id_devolucion)
        if devolucion is None:
            return None
        venta = self.ventas.obtener(devolucion.venta_id)
        cliente = self.ventas.clientes.obtener(venta.cliente_id) if venta else None
        producto = self.productos.obtener(venta.producto_id) if venta else None
        precio = venta.precio_unitario if venta else 0
        texto = f"NOTA DE CRÉDITO #{devolucion.id}   fecha: {devolucion.fecha}\n"
        texto += (f"Venta    : #{devolucion.venta_id}   "
                  f"({cliente.nombre_completo() if cliente else 'eliminado'})\n")
        texto += f"Producto : {producto.nombre if producto else 'eliminado'}\n"
        texto += f"Devuelto : {devolucion.cantidad} x ${precio:.2f}\n"
        texto += f"Motivo   : {devolucion.motivo}\n"
        texto += "-" * 42 + "\n"
        texto += f"REEMBOLSO con IVA: ${devolucion.monto:.2f}\n"
        if devolucion.regresa_al_stock():
            texto += "Stock    : regresa al inventario"
        else:
            texto += "Stock    : NO regresa (producto defectuoso)"
        return texto

    def devoluciones_por_motivo(self):
        """DICCIONARIO de LISTAS: {motivo: [devoluciones con ese motivo]}.
        Diccionario porque se consulta por etiqueta (el motivo); lista porque
        cada motivo puede tener muchas devoluciones."""
        agrupadas = {}
        for devolucion in self.lista:
            if devolucion.motivo not in agrupadas:
                agrupadas[devolucion.motivo] = []
            agrupadas[devolucion.motivo].append(devolucion)
        return agrupadas

    def total_reembolsado(self):
        total = 0
        for devolucion in self.lista:
            total += devolucion.monto
        return round(total, 2)

    def ventas_netas(self):
        """Total vendido CON IVA menos total reembolsado (que también lleva IVA),
        para comparar peras con peras."""
        vendido = 0
        for venta in self.ventas.leer():
            vendido += Producto.con_iva(venta.calcular_total())
        return round(vendido - self.total_reembolsado(), 2)

    # ---------------- reto extra ----------------
    def anular_venta(self, id_venta):
        """No se anula una venta que ya tiene devoluciones; si no, delega.
        Va aquí y no en VentaController porque VentaController no conoce a las
        devoluciones (la dependencia va de Devolucion hacia Venta, nunca al revés)."""
        if self.devoluciones_de_venta(id_venta):
            return False, "La venta tiene devoluciones; no se puede anular"
        return self.ventas.eliminar(id_venta)
