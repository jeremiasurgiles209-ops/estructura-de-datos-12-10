from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from models import Devolucion
from views import (
    ClienteController, ProductoController, VentaController, DevolucionController
)

# Se crea UN solo controlador de cada tipo.
# A ventas se le pasan los MISMOS clientes y productos.
clientes = ClienteController()
productos = ProductoController()
ventas = VentaController(clientes, productos)
# Devoluciones usa los MISMOS controladores de ventas y productos
devoluciones = DevolucionController(ventas, productos)


# =====================================================================
# AYUDAS DE PANTALLA
# =====================================================================

def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    """Devuelve un entero o None si el usuario escribió otra cosa."""
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    # Los controladores devuelven la TUPLA (exito, mensaje)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    """Sirve para clientes, productos y ventas: cada modelo sabe mostrarse."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    # Recorre el DICCIONARIO del objeto: clave y valor a la vez
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# =====================================================================
# MENÚ DE CLIENTES
# =====================================================================

def crear_cliente():
    imprimir_titulo("CREAR CLIENTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "telefono": input("Teléfono: "),
        "ciudad": input("Ciudad: "),
    }
    mostrar_resultado(*clientes.crear(datos))
    pausa()


def listar_clientes():
    imprimir_titulo("CLIENTES")
    mostrar_lista(clientes.leer(), "Todavía no hay clientes.")
    pausa()


def buscar_cliente():
    imprimir_titulo("BUSCAR CLIENTE")
    termino = input("Nombre, email, teléfono o ciudad: ")
    encontrados = clientes.buscar(termino)
    mostrar_lista(encontrados, f"Ningún cliente coincide con '{termino}'.")
    pausa()


def ver_cliente():
    imprimir_titulo("VER CLIENTE POR ID")
    cliente = clientes.obtener(pedir_entero("Id: "))
    if cliente is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(cliente)
    pausa()


def actualizar_cliente():
    imprimir_titulo("ACTUALIZAR CLIENTE")
    id_cliente = pedir_entero("Id: ")
    cliente = clientes.obtener(id_cliente)
    if cliente is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {cliente.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "telefono", "ciudad"):
        actual = getattr(cliente, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*clientes.actualizar(id_cliente, cambios))
    pausa()


def eliminar_cliente():
    imprimir_titulo("ELIMINAR CLIENTE")
    id_cliente = pedir_entero("Id: ")
    cliente = clientes.obtener(id_cliente)
    if cliente is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminará: {cliente.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*clientes.eliminar(id_cliente))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DE PRODUCTOS
# =====================================================================

def crear_producto():
    imprimir_titulo("CREAR PRODUCTO")
    datos = {
        "nombre": input("Nombre: "),
        "precio": input("Precio: "),
        "stock": input("Stock: "),
    }
    mostrar_resultado(*productos.crear(datos))
    pausa()


def listar_productos():
    imprimir_titulo("PRODUCTOS")
    mostrar_lista(productos.leer(), "Todavía no hay productos.")
    pausa()


def buscar_producto():
    imprimir_titulo("BUSCAR PRODUCTO")
    termino = input("Nombre: ")
    mostrar_lista(productos.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_producto():
    imprimir_titulo("VER PRODUCTO POR ID")
    producto = productos.obtener(pedir_entero("Id: "))
    if producto is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(producto)
        imprimir_info(f"Precio con IVA: ${producto.con_iva(producto.precio):.2f}")
    pausa()


def actualizar_producto():
    imprimir_titulo("ACTUALIZAR PRODUCTO")
    id_producto = pedir_entero("Id: ")
    producto = productos.obtener(id_producto)
    if producto is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {producto.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "precio", "stock"):
        actual = getattr(producto, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*productos.actualizar(id_producto, cambios))
    pausa()


def eliminar_producto():
    imprimir_titulo("ELIMINAR PRODUCTO")
    id_producto = pedir_entero("Id: ")
    producto = productos.obtener(id_producto)
    if producto is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminará: {producto.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*productos.eliminar(id_producto))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DE VENTAS
# =====================================================================

def registrar_venta():
    imprimir_titulo("REGISTRAR VENTA")
    imprimir_info("Clientes:")
    mostrar_lista(clientes.leer())
    imprimir_info("Productos:")
    mostrar_lista(productos.leer())

    datos = {
        "cliente_id": pedir_entero("\nId del cliente: "),
        "producto_id": pedir_entero("Id del producto: "),
        "cantidad": pedir_entero("Cantidad: "),
    }
    if None in datos.values():
        imprimir_error("Todos los datos deben ser números enteros")
        return pausa()

    mostrar_resultado(*ventas.crear(datos))
    pausa()


def listar_ventas():
    imprimir_titulo("VENTAS")
    mostrar_lista(ventas.leer(), "Todavía no hay ventas.")
    pausa()


def ver_comprobante():
    imprimir_titulo("COMPROBANTE")
    texto = ventas.comprobante(pedir_entero("Id de la venta: "))
    if texto is None:
        imprimir_error("No existe esa venta")
    else:
        print(texto)
    pausa()


def anular_venta():
    imprimir_titulo("ANULAR VENTA")
    id_venta = pedir_entero("Id de la venta: ")
    if id_venta and confirmar("Se devolverá el stock. ¿Confirma?"):
        mostrar_resultado(*devoluciones.anular_venta(id_venta))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DE DEVOLUCIONES
# =====================================================================
def mostrar_estado_venta(venta):
    """Muestra cuánto se vendió, cuánto se devolvió y cuánto queda por devolver.
    Los números los calcula el Controlador; aquí solo se imprimen."""
    devuelta = devoluciones.cantidad_devuelta(venta.id)
    disponible = devoluciones.cantidad_disponible(venta)
    imprimir_info(f"Vendidas: {venta.cantidad} · Ya devueltas: {devuelta} · "
                  f"Disponibles para devolver: {disponible}")
    return disponible


def registrar_devolucion():
    imprimir_titulo("REGISTRAR DEVOLUCIÓN")
    id_venta = pedir_entero("Id de la venta / factura: ")
    if id_venta is None:
        imprimir_error("El id debe ser un número entero")
        return pausa()
    # Si el comprobante es None, la venta no existe
    texto = ventas.comprobante(id_venta)
    if texto is None:
        imprimir_error("No existe esa venta")
        return pausa()
    print(texto)
    disponible = mostrar_estado_venta(ventas.obtener(id_venta))
    if disponible <= 0:
        imprimir_error("Esta venta ya no tiene unidades disponibles para devolver")
        return pausa()
    cantidad = pedir_entero("Cantidad a devolver: ")
    if cantidad is None:
        imprimir_error("La cantidad debe ser un número entero")
        return pausa()
    # Los motivos se recorren desde la TUPLA del modelo: no se escriben a mano
    print("Motivos:")
    for numero, motivo in enumerate(Devolucion.MOTIVOS, start=1):
        print(f"  {numero}. {motivo}")
    eleccion = pedir_entero("Motivo: ")
    if eleccion is None or not 1 <= eleccion <= len(Devolucion.MOTIVOS):
        imprimir_error("Motivo no válido: no se registró nada")
        return pausa()
    datos = {
        "venta_id": id_venta,
        "cantidad": cantidad,
        "motivo": Devolucion.MOTIVOS[eleccion - 1],
    }
    mostrar_resultado(*devoluciones.crear(datos))
    pausa()


def consultar_devoluciones():
    imprimir_titulo("DEVOLUCIONES DE UNA VENTA")
    id_venta = pedir_entero("Id de la venta: ")
    texto = ventas.comprobante(id_venta) if id_venta is not None else None
    if texto is None:
        imprimir_error("No existe esa venta")
        return pausa()
    print(texto)
    print()
    mostrar_lista(devoluciones.devoluciones_de_venta(id_venta),
                  "Esta venta no tiene devoluciones.")
    imprimir_info(f"Total reembolsado de esta venta: "
                  f"${devoluciones.reembolsado_de_venta(id_venta):.2f}")
    mostrar_estado_venta(ventas.obtener(id_venta))
    pausa()


def listar_devoluciones():
    imprimir_titulo("TODAS LAS DEVOLUCIONES")
    mostrar_lista(devoluciones.leer(), "Todavía no hay devoluciones.")
    if devoluciones.leer():
        imprimir_info(f"Total reembolsado: ${devoluciones.total_reembolsado():.2f}")
    pausa()


def ver_nota_credito():
    imprimir_titulo("NOTA DE CRÉDITO")
    texto = devoluciones.nota_credito(pedir_entero("Id de la devolución: "))
    if texto is None:
        imprimir_error("No existe esa devolución")
    else:
        print(texto)
    pausa()


def resumen():
    imprimir_titulo("RESUMEN")
    print(f"  Clientes  : {len(clientes.leer())}")
    print(f"  Ciudades  : {', '.join(clientes.ciudades()) or '-'}")
    print(f"  Productos : {len(productos.leer())}")
    bajos = productos.con_stock_bajo()
    print(f"  Stock bajo: {', '.join(p.nombre for p in bajos) or 'ninguno'}")
    print(f"  Ventas    : {len(ventas.leer())}")
    print(f"  Vendido   : ${ventas.total_vendido():.2f}  (sin IVA)")
    print(f"  Devoluciones : {len(devoluciones.leer())}")
    print(f"  Reembolsado  : ${devoluciones.total_reembolsado():.2f}  (con IVA)")
    print(f"  Ventas netas : ${devoluciones.ventas_netas():.2f}  (vendido con IVA - reembolsado)")
    pausa()


# =====================================================================
# MENÚS: DICCIONARIOS tecla -> (texto, función)
# =====================================================================

MENU_CLIENTES = {
    "1": ("Crear cliente", crear_cliente),
    "2": ("Ver todos", listar_clientes),
    "3": ("Buscar", buscar_cliente),
    "4": ("Ver por id", ver_cliente),
    "5": ("Actualizar", actualizar_cliente),
    "6": ("Eliminar", eliminar_cliente),
    "0": ("Volver", None),
}

MENU_PRODUCTOS = {
    "1": ("Crear producto", crear_producto),
    "2": ("Ver todos", listar_productos),
    "3": ("Buscar", buscar_producto),
    "4": ("Ver por id", ver_producto),
    "5": ("Actualizar", actualizar_producto),
    "6": ("Eliminar", eliminar_producto),
    "0": ("Volver", None),
}

MENU_VENTAS = {
    "1": ("Registrar venta", registrar_venta),
    "2": ("Ver todas", listar_ventas),
    "3": ("Ver comprobante", ver_comprobante),
    "4": ("Anular venta", anular_venta),
    "0": ("Volver", None),
}


# DICCIONARIO tecla -> (texto, función): igual que los otros menús, así
# ejecutar_menu() lo recorre sin cambiar ni una línea.
MENU_DEVOLUCIONES = {
    "1": ("Registrar devolución", registrar_devolucion),
    "2": ("Consultar devoluciones de una venta", consultar_devoluciones),
    "3": ("Ver todas", listar_devoluciones),
    "4": ("Ver nota de crédito", ver_nota_credito),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    """Un solo bucle para los tres submenús."""
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opción: ").strip()
        if tecla not in opciones:               # búsqueda por clave: instantánea
            imprimir_error("Opción no válida")
            pausa()
            continue

        _texto, funcion = opciones[tecla]
        if funcion is None:                      # la opción "Volver"
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA DE VENTAS")
        print("  1. Clientes")
        print("  2. Productos")
        print("  3. Ventas")
        print("  4. Devoluciones")
        print("  5. Resumen")
        print("  0. Salir\n")

        tecla = input("Opción: ").strip()
        if tecla == "1":
            ejecutar_menu("CLIENTES", MENU_CLIENTES)
        elif tecla == "2":
            ejecutar_menu("PRODUCTOS", MENU_PRODUCTOS)
        elif tecla == "3":
            ejecutar_menu("VENTAS", MENU_VENTAS)
        elif tecla == "4":
            ejecutar_menu("DEVOLUCIONES", MENU_DEVOLUCIONES)
        elif tecla == "5":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
