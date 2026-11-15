# -*- coding: utf-8 -*-
"""
Módulo de Formateo e Impresión de Tickets y Apertura de Cajón de Dinero.
Compatible con impresoras térmicas (58mm / 70mm / 80mm), puertos USB, LPT, COM y Spooler de Windows.
Diseñado específicamente para Windows XP SP3, 7, 8, 10 y 11 usando únicamente la librería estándar de Python.
"""

import os
import sys
import datetime
import textwrap

# Importación segura de ctypes y winreg para Windows XP+
try:
    import ctypes
    from ctypes import wintypes
except ImportError:
    ctypes = None
    wintypes = None

try:
    import winreg
except ImportError:
    winreg = None

# Constantes ESC/POS para Ticketera y Cajón de Dinero
CMD_INIT = b"\x1b\x40"                             # Inicializar impresora (ESC @)
CMD_SELECCIONAR_CP850 = b"\x1b\x74\x02"            # Tabla de caracteres CP850 (Multilingual)
CMD_CORTE_PAPEL = b"\x1d\x56\x00"                  # Corte total de papel (GS V 0)
CMD_CORTE_PARCIAL = b"\x1d\x56\x01"                # Corte parcial de papel (GS V 1)
CMD_AVANCE_LINEAS = b"\n\n\n\n\n"                  # Espacio para que el ticket salga del cortador

# Secuencia universal para apertura de cajón monedero por puerto RJ11 (DK):
# Pulso de 50ms al Pin 2 y al Pin 5, más secuencia DLE DC4 para impresoras Epson/chinas
CMD_ABRIR_CAJON = (
    b"\x1b\x70\x00\x19\xfa"                        # ESC p 0 25 250 (Pin 2)
    b"\x1b\x70\x01\x19\xfa"                        # ESC p 1 25 250 (Pin 5)
    b"\x10\x14\x01\x00\x05"                        # DLE DC4 1 0 5
)

# Estructura DOC_INFO_1W de Windows Spooler
if ctypes and wintypes:
    class DOC_INFO_1W(ctypes.Structure):
        _fields_ = [
            ("pDocName", wintypes.LPWSTR),
            ("pOutputFile", wintypes.LPWSTR),
            ("pDatatype", wintypes.LPWSTR),
        ]
else:
    DOC_INFO_1W = None


# ==========================================================
# CONFIGURACIÓN Y CONSTANTES DE ANCHO DE IMPRESORA TÉRMICA
# ==========================================================
ANCHO_58MM = 32   # Columnas estándar para impresora térmica compacta de 58 mm
ANCHO_70MM = 36   # Columnas estándar para impresora térmica mediana de 70 mm
ANCHO_80MM = 40   # Columnas estándar para impresora térmica grande de 80 mm (compatible 40 a 48)

OPCIONES_ANCHO = (
    (ANCHO_58MM, "58 mm (32 car.)"),
    (ANCHO_70MM, "70 mm (36 car.)"),
    (ANCHO_80MM, "80 mm (40 car.)"),
)

def obtener_opciones_ancho():
    """Retorna una lista de tuplas (columnas, etiqueta) con los anchos térmicos soportados."""
    return list(OPCIONES_ANCHO)

def resolver_ancho_ticket(ancho_configurado):
    """
    Normaliza el ancho del ticket al número de columnas correspondiente.
    Soporta la especificación en milímetros (58, 70, 80) o en columnas (32, 36, 40, etc.).
    """
    if ancho_configurado is None:
        return ANCHO_80MM
    try:
        if isinstance(ancho_configurado, str):
            val_limpio = "".join([c for c in ancho_configurado if c.isdigit()])
            val = int(val_limpio) if val_limpio else ANCHO_80MM
        else:
            val = int(ancho_configurado)
    except (ValueError, TypeError):
        return ANCHO_80MM

    # Si se especificó en milímetros:
    if val in (58, 57):
        return ANCHO_58MM
    elif val in (70, 69, 72):
        return ANCHO_70MM
    elif val in (80, 76):
        return ANCHO_80MM

    # Si ya se especificó en número de columnas:
    if val <= 33:
        return ANCHO_58MM
    elif val <= 37:
        return ANCHO_70MM
    else:
        return val


# ==========================================================
# UTILIDADES DE TEXTO Y FORMATEO
# ==========================================================

def centrar_texto(texto, ancho):
    """Centra una línea de texto según el ancho especificado."""
    return texto.center(ancho)

def linea_separadora(caracter="=", ancho=ANCHO_80MM):
    """Genera una línea divisoria."""
    return caracter * ancho

def codificar_para_impresora(texto):
    """
    Codifica el texto en bytes compatibles con la impresora térmica (CP850 / CP437 / Latin-1).
    Evita caracteres extraños en impresoras térmicas de Windows XP.
    """
    try:
        return texto.encode('cp850', errors='replace')
    except Exception:
        try:
            return texto.encode('cp437', errors='replace')
        except Exception:
            try:
                return texto.encode('latin-1', errors='replace')
            except Exception:
                return texto.encode('ascii', errors='replace')

def generar_texto_ticket(datos_venta, config=None):
    """
    Genera el formato en texto plano para un ticket de compra adaptado a:
    - 58mm (32 columnas)
    - 70mm (36 columnas)
    - 80mm (40 a 48 columnas)
    datos_venta: dict con 'folio', 'fecha_hora', 'articulos', 'total', 'pago_con', 'cambio', 'metodo_pago'
    config: dict con 'nombre_tienda', 'direccion', 'telefono', 'mensaje_ticket', 'ancho_ticket'
    """
    if config is None:
        config = {}

    ancho = resolver_ancho_ticket(config.get('ancho_ticket', ANCHO_80MM))
    lineas = []

    # Encabezado
    nombre_tienda = config.get('nombre_tienda', 'DULCERIA') if config else 'DULCERIA'
    for nom_linea in textwrap.wrap(nombre_tienda.upper(), width=ancho) or [nombre_tienda.upper()]:
        lineas.append(centrar_texto(nom_linea, ancho))
    if config and config.get('direccion'):
        for dir_linea in textwrap.wrap(config.get('direccion'), width=ancho):
            lineas.append(centrar_texto(dir_linea, ancho))
    if config and config.get('telefono'):
        lineas.append(centrar_texto("Tel: " + config.get('telefono'), ancho))

    lineas.append(linea_separadora("=", ancho))
    folio = datos_venta.get('folio', 'T-00000')
    fecha = datos_venta.get('fecha_hora', '')
    lineas.append("FOLIO: {:<12} CAJA: 1".format(folio))
    lineas.append("FECHA: {}".format(fecha))
    lineas.append(linea_separadora("-", ancho))

    total_piezas = 0

    if ancho <= 32:
        # Formato compacto para impresoras de 58mm (32 columnas exactas)
        # CAN(3) DESC(13) P.U(6) TOTAL(7) -> 3+1+13+1+6+1+7 = 32
        lineas.append("{:<3} {:<13} {:>6} {:>7}".format("CAN", "PRODUCTO", "P.U.", "TOTAL"))
        lineas.append(linea_separadora("-", ancho))

        for art in datos_venta.get('articulos', []):
            cant = art.get('cantidad', 1)
            total_piezas += cant
            nombre = art.get('nombre', 'Producto')
            if len(nombre) > 13:
                nombre = nombre[:11] + ".."
            precio = float(art.get('precio', 0.0))
            subtotal = float(art.get('subtotal', cant * precio))
            str_cant = "{:.0f}".format(cant) if float(cant).is_integer() else "{:.1f}".format(cant)
            lineas.append("{:<3} {:<13} {:>6.2f} {:>7.2f}".format(str_cant, nombre, precio, subtotal))

        lineas.append(linea_separadora("=", ancho))
        lineas.append("{:<18} {:>13}".format("TOTAL ARTICULOS:", "{:.0f}".format(total_piezas)))
        lineas.append("{:<18} ${:>12.2f}".format("TOTAL A PAGAR:", float(datos_venta.get('total', 0.0))))
        lineas.append("{:<18} ${:>12.2f}".format("PAGO CON:", float(datos_venta.get('pago_con', 0.0))))
        lineas.append("{:<18} ${:>12.2f}".format("SU CAMBIO:", float(datos_venta.get('cambio', 0.0))))
        lineas.append(linea_separadora("=", ancho))
    elif ancho <= 37:
        # Formato intermedio para impresoras de 70mm (36 columnas exactas)
        # CANT(4) PRODUCTO(16) P.UNIT(6) TOTAL(7) -> 4+1+16+1+6+1+7 = 36
        lineas.append("{:<4} {:<16} {:>6} {:>7}".format("CANT", "PRODUCTO", "P.UNIT", "TOTAL"))
        lineas.append(linea_separadora("-", ancho))

        for art in datos_venta.get('articulos', []):
            cant = art.get('cantidad', 1)
            total_piezas += cant
            nombre = art.get('nombre', 'Producto')
            if len(nombre) > 16:
                nombre = nombre[:14] + ".."
            precio = float(art.get('precio', 0.0))
            subtotal = float(art.get('subtotal', cant * precio))
            str_cant = "{:.0f}".format(cant) if float(cant).is_integer() else "{:.1f}".format(cant)
            lineas.append("{:<4} {:<16} {:>6.2f} {:>7.2f}".format(str_cant, nombre, precio, subtotal))

        lineas.append(linea_separadora("=", ancho))
        lineas.append("{:<20} {:>15}".format("TOTAL ARTICULOS:", "{:.0f}".format(total_piezas)))
        lineas.append("{:<20} ${:>14.2f}".format("TOTAL A PAGAR:", float(datos_venta.get('total', 0.0))))
        lineas.append("{:<20} ${:>14.2f}".format("PAGO CON:", float(datos_venta.get('pago_con', 0.0))))
        lineas.append("{:<20} ${:>14.2f}".format("SU CAMBIO:", float(datos_venta.get('cambio', 0.0))))
        lineas.append(linea_separadora("=", ancho))
    else:
        # Formato estándar para impresoras de 80mm (40 a 48 columnas)
        w_prod = max(15, ancho - 23)
        header = "{:<5} {:<" + str(w_prod) + "} {:>7} {:>8}"
        lineas.append(header.format("CANT", "PRODUCTO", "P.UNIT", "TOTAL"))
        lineas.append(linea_separadora("-", ancho))

        for art in datos_venta.get('articulos', []):
            cant = art.get('cantidad', 1)
            total_piezas += cant
            nombre = art.get('nombre', 'Producto')
            if len(nombre) > w_prod:
                nombre = nombre[:w_prod - 2] + ".."
            precio = float(art.get('precio', 0.0))
            subtotal = float(art.get('subtotal', cant * precio))
            str_cant = "{:.0f}".format(cant) if float(cant).is_integer() else "{:.2f}".format(cant)
            row_fmt = "{:<5} {:<" + str(w_prod) + "} {:>7.2f} {:>8.2f}"
            lineas.append(row_fmt.format(str_cant, nombre, precio, subtotal))

        lineas.append(linea_separadora("=", ancho))
        w_tit = ancho - 15
        fmt_art = "{:>" + str(w_tit) + "} {:>14}"
        fmt_tot = "{:>" + str(w_tit) + "} ${:>13.2f}"
        lineas.append(fmt_art.format("TOTAL DE ARTICULOS:", "{:.0f}".format(total_piezas)))
        lineas.append(fmt_tot.format("TOTAL A PAGAR:", float(datos_venta.get('total', 0.0))))
        lineas.append(fmt_tot.format("PAGO CON:", float(datos_venta.get('pago_con', 0.0))))
        lineas.append(fmt_tot.format("SU CAMBIO:", float(datos_venta.get('cambio', 0.0))))
        lineas.append(linea_separadora("=", ancho))

    # Pie de ticket
    mensaje = config.get('mensaje_ticket', '¡Gracias por su preferencia!') if config else '¡Gracias por su preferencia!'
    for parte in mensaje.split("\n"):
        parte = parte.strip()
        if not parte:
            continue
        for sublinea in textwrap.wrap(parte, width=ancho) or [parte]:
            lineas.append(centrar_texto(sublinea, ancho))

    lineas.append("")
    return "\n".join(lineas)

def guardar_ticket_en_archivo(datos_venta, config):
    """Guarda una copia del ticket en la carpeta tickets/ como respaldo."""
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    carpeta_tickets = os.path.join(directorio_base, "tickets")
    if not os.path.exists(carpeta_tickets):
        try:
            os.makedirs(carpeta_tickets)
        except Exception:
            pass

    nombre_archivo = "ticket_{}.txt".format(datos_venta.get('folio', 'sin_folio'))
    ruta_archivo = os.path.join(carpeta_tickets, nombre_archivo)

    texto = generar_texto_ticket(datos_venta, config)
    try:
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(texto)
        return ruta_archivo
    except Exception:
        try:
            with open(ruta_archivo, "w", encoding="latin-1", errors="replace") as f:
                f.write(texto)
            return ruta_archivo
        except Exception:
            return None

def generar_texto_corte(resumen_caja, movimientos, config=None):
    """
    Genera el formato en texto del Corte de Caja diario adaptado a 58mm, 70mm u 80mm.
    """
    if config is None:
        config = {}

    ancho = resolver_ancho_ticket(config.get('ancho_ticket', ANCHO_80MM))
    lineas = []

    nombre_tienda = config.get('nombre_tienda', 'DULCERIA') if config else 'DULCERIA'
    for nom_linea in textwrap.wrap(nombre_tienda.upper(), width=ancho) or [nombre_tienda.upper()]:
        lineas.append(centrar_texto(nom_linea, ancho))
    lineas.append(centrar_texto("CORTE DE CAJA / CIERRE DE TURNO", ancho))
    lineas.append(linea_separadora("=", ancho))

    lineas.append("TURNO ID: #{}".format(resumen_caja.get('id_turno', 1)))
    lineas.append("APERTURA: {}".format(resumen_caja.get('fecha_inicio', '')))
    lineas.append("CIERRE:   {}".format(resumen_caja.get('fecha_fin') or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    lineas.append(linea_separadora("-", ancho))

    if ancho <= 32:
        w_etiq = 18
        w_val = 12
        fmt_fila = "{:<" + str(w_etiq) + "} ${:>" + str(w_val) + ".2f}"
        fmt_fila_txt = "{:<" + str(w_etiq) + "}   {:>" + str(w_val) + "}"
    elif ancho <= 37:
        w_etiq = 20
        w_val = 14
        fmt_fila = "{:<" + str(w_etiq) + "} ${:>" + str(w_val) + ".2f}"
        fmt_fila_txt = "{:<" + str(w_etiq) + "}   {:>" + str(w_val - 1) + "}"
    else:
        w_etiq = 25
        w_val = 12
        fmt_fila = "{:<" + str(w_etiq) + "} ${:>" + str(w_val) + ".2f}"
        fmt_fila_txt = "{:<" + str(w_etiq) + "}   {:>" + str(w_val) + "}"

    lineas.append(fmt_fila.format("(+) Fondo Inicial:", float(resumen_caja.get('monto_inicial', 0.0))))
    lineas.append(fmt_fila.format("(+) Ventas Efectivo:", float(resumen_caja.get('total_ventas', 0.0))))
    lineas.append(fmt_fila_txt.format("    Num. Ventas:", resumen_caja.get('num_ventas', 0)))
    lineas.append(fmt_fila.format("(+) Entradas:", float(resumen_caja.get('total_entradas', 0.0))))
    lineas.append(fmt_fila.format("(-) Salidas/Gastos:", float(resumen_caja.get('total_salidas', 0.0))))
    lineas.append(linea_separadora("=", ancho))
    if ancho <= 37:
        lineas.append("TOTAL ESPERADO EN CAJA:")
        lineas.append("{:>{w}}".format("${:.2f}".format(float(resumen_caja.get('dinero_esperado', 0.0))), w=ancho))
    else:
        lineas.append(fmt_fila.format("TOTAL ESPERADO EN CAJA:", float(resumen_caja.get('dinero_esperado', 0.0))))
    lineas.append(linea_separadora("=", ancho))

    lineas.append(fmt_fila.format("Costo Mercancia:", float(resumen_caja.get('total_costo', 0.0))))
    lineas.append(fmt_fila.format("GANANCIA ESTIMADA:", float(resumen_caja.get('ganancia_estimada', 0.0))))
    lineas.append(linea_separadora("-", ancho))

    if movimientos:
        lineas.append(centrar_texto("DETALLE DE MOVIMIENTOS", ancho))
        if ancho <= 32:
            lineas.append("{:<4} {:<16} {:>9}".format("TIPO", "MOTIVO", "MONTO"))
            lineas.append(linea_separadora("-", ancho))
            for mov in movimientos:
                tipo = mov.get('tipo', 'MOV')[:3]
                motivo = mov.get('motivo', '')
                if len(motivo) > 16:
                    motivo = motivo[:14] + ".."
                monto = float(mov.get('monto', 0.0))
                lineas.append("{:<4} {:<16} ${:>8.2f}".format(tipo, motivo, monto))
        elif ancho <= 37:
            lineas.append("{:<5} {:<19} {:>10}".format("TIPO", "MOTIVO", "MONTO"))
            lineas.append(linea_separadora("-", ancho))
            for mov in movimientos:
                tipo = mov.get('tipo', 'MOV')[:5]
                motivo = mov.get('motivo', '')
                if len(motivo) > 19:
                    motivo = motivo[:17] + ".."
                monto = float(mov.get('monto', 0.0))
                lineas.append("{:<5} {:<19} ${:>9.2f}".format(tipo, motivo, monto))
        else:
            lineas.append("{:<8} {:<20} {:>10}".format("TIPO", "MOTIVO", "MONTO"))
            lineas.append(linea_separadora("-", ancho))
            for mov in movimientos:
                tipo = mov.get('tipo', 'MOV')
                motivo = mov.get('motivo', '')
                if len(motivo) > 18:
                    motivo = motivo[:16] + ".."
                monto = float(mov.get('monto', 0.0))
                lineas.append("{:<8} {:<20} ${:>9.2f}".format(tipo, motivo, monto))
        lineas.append(linea_separadora("-", ancho))

    lineas.append("")
    if ancho <= 32:
        lineas.append("Firma: " + ("_" * max(8, ancho - 7)))
    else:
        lineas.append("Firma Responsable: " + ("_" * max(8, ancho - 19)))
    lineas.append("")
    return "\n".join(lineas)

def guardar_corte_en_archivo(resumen_caja, movimientos, config):
    """Guarda el reporte del corte de caja en la carpeta cortes/."""
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    carpeta_cortes = os.path.join(directorio_base, "cortes")
    if not os.path.exists(carpeta_cortes):
        try:
            os.makedirs(carpeta_cortes)
        except Exception:
            pass

    fecha_hoy = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = "corte_turno_{}_{}.txt".format(resumen_caja.get('id_turno', 1), fecha_hoy)
    ruta_archivo = os.path.join(carpeta_cortes, nombre_archivo)

    texto = generar_texto_corte(resumen_caja, movimientos, config)
    try:
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(texto)
        return ruta_archivo
    except Exception:
        try:
            with open(ruta_archivo, "w", encoding="latin-1", errors="replace") as f:
                f.write(texto)
            return ruta_archivo
        except Exception:
            return None


# ==========================================================
# GESTIÓN Y DETECCIÓN DE IMPRESORAS EN WINDOWS XP+
# ==========================================================

def obtener_impresora_predeterminada():
    """
    Obtiene el nombre de la impresora predeterminada de Windows.
    Utiliza GetDefaultPrinterW de winspool.drv o el registro de Windows.
    """
    if os.name != 'nt' or not ctypes:
        return None

    # Método 1: winspool.drv GetDefaultPrinterW
    try:
        winspool = ctypes.WinDLL("winspool.drv")
        tam = wintypes.DWORD(0)
        winspool.GetDefaultPrinterW(None, ctypes.byref(tam))
        if tam.value > 0:
            buf = ctypes.create_unicode_buffer(tam.value)
            if winspool.GetDefaultPrinterW(buf, ctypes.byref(tam)):
                if buf.value:
                    return buf.value.strip()
    except Exception:
        pass

    # Método 2: Registro de Windows (100% compatible con Windows XP)
    if winreg:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Windows")
            val, _ = winreg.QueryValueEx(key, "Device")
            winreg.CloseKey(key)
            if val:
                nombre = val.split(',')[0].strip()
                if nombre:
                    return nombre
        except Exception:
            pass

    return None

def listar_impresoras_instaladas():
    """
    Retorna la lista de impresoras instaladas en el sistema operativo.
    En Windows lee del registro de Windows (compatible con XP, 7, 10, 11).
    """
    impresoras = []
    if os.name != 'nt':
        return ["Impresora de Prueba (Simulador Linux)"]

    if winreg:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Devices")
            idx = 0
            while True:
                try:
                    nombre, _, _ = winreg.EnumValue(key, idx)
                    if nombre and nombre not in impresoras:
                        impresoras.append(nombre)
                    idx += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass

    return impresoras

def resolver_nombre_impresora(nombre_configurado):
    """
    Determina la impresora final a usar. Si no se especificó o es 'predeterminada',
    busca la impresora por defecto de Windows.
    """
    if not nombre_configurado or not nombre_configurado.strip():
        return obtener_impresora_predeterminada()

    nom = nombre_configurado.strip()
    nom_lower = nom.lower()

    if "predeterminad" in nom_lower or nom_lower == "default":
        pred = obtener_impresora_predeterminada()
        return pred if pred else nom

    if "ninguna" in nom_lower or "desactivada" in nom_lower:
        return None

    return nom


# ==========================================================
# COMUNICACIÓN DIRECTA CON HARDWARE (SPOOLER, PUERTOS Y ESC/POS)
# ==========================================================

def enviar_raw_a_impresora(nombre_impresora, datos_bytes, doc_name="Ticket POS"):
    """
    Envía bytes binarios en crudo (RAW ESC/POS) a la impresora.
    Soporta:
    1. Spooler de Windows (winspool.drv) para impresoras USB/Térmicas sin requerir pywin32.
    2. Puertos directos de hardware (LPT1, LPT2, COM1, COM2, COM3, COM4, PRN).
    3. Rutas de red compartidas (\\\\localhost\\Ticketera).
    4. Simulación en entornos de prueba / no-Windows.
    """
    if not datos_bytes:
        return False, "No hay datos para enviar a la impresora."

    if not nombre_impresora or not nombre_impresora.strip():
        return False, "No se ha configurado ninguna impresora."

    nombre_destino = nombre_impresora.strip()
    nombre_upper = nombre_destino.upper()

    # Caso 1: Puertos directos de Windows (LPT1, COM1, PRN...)
    if nombre_upper.startswith(("LPT", "COM", "PRN")):
        rutas_probar = [
            r"\\.\{}".format(nombre_upper),
            nombre_upper
        ]
        ultimo_error = ""
        for r in rutas_probar:
            try:
                with open(r, "wb", buffering=0) as f:
                    f.write(datos_bytes)
                return True, "Enviado exitosamente al puerto {}".format(nombre_upper)
            except Exception as e:
                ultimo_error = str(e)
        return False, "Error al escribir en puerto {}: {}".format(nombre_upper, ultimo_error)

    # Caso 2: Impresora de red compartida UNC (\\127.0.0.1\Impresora o \\Equipo\POS)
    if nombre_destino.startswith(r"\\"):
        try:
            with open(nombre_destino, "wb", buffering=0) as f:
                f.write(datos_bytes)
            return True, "Enviado exitosamente a la impresora compartida {}".format(nombre_destino)
        except Exception as e:
            return False, "Error al enviar a impresora compartida {}: {}".format(nombre_destino, str(e))

    # Caso 3: En entornos no-Windows (desarrollo/pruebas)
    if os.name != 'nt' or not ctypes:
        print("[POS-DEBUG] Modo no-Windows. Enviando {} bytes a '{}'".format(len(datos_bytes), nombre_destino))
        return True, "Impresión simulada exitosamente (Entorno no-Windows)"

    # Caso 4: Spooler de Windows mediante winspool.drv (Windows XP SP3 a Windows 11)
    try:
        winspool = ctypes.WinDLL("winspool.drv")

        # Configurar firmas de funciones Win32
        winspool.OpenPrinterW.argtypes = [wintypes.LPWSTR, ctypes.POINTER(wintypes.HANDLE), ctypes.c_void_p]
        winspool.OpenPrinterW.restype = wintypes.BOOL

        winspool.StartDocPrinterW.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p]
        winspool.StartDocPrinterW.restype = wintypes.DWORD

        winspool.StartPagePrinter.argtypes = [wintypes.HANDLE]
        winspool.StartPagePrinter.restype = wintypes.BOOL

        winspool.WritePrinter.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
        winspool.WritePrinter.restype = wintypes.BOOL

        winspool.EndPagePrinter.argtypes = [wintypes.HANDLE]
        winspool.EndPagePrinter.restype = wintypes.BOOL

        winspool.EndDocPrinter.argtypes = [wintypes.HANDLE]
        winspool.EndDocPrinter.restype = wintypes.BOOL

        winspool.ClosePrinter.argtypes = [wintypes.HANDLE]
        winspool.ClosePrinter.restype = wintypes.BOOL

        hPrinter = wintypes.HANDLE()
        if not winspool.OpenPrinterW(nombre_destino, ctypes.byref(hPrinter), None):
            cod_err = ctypes.GetLastError() if hasattr(ctypes, 'GetLastError') else 0
            return False, "No se pudo abrir la impresora '{}'. Verifique que esté instalada y encendida. (Error {})".format(nombre_destino, cod_err)

        try:
            doc_info = DOC_INFO_1W()
            doc_info.pDocName = doc_name
            doc_info.pOutputFile = None
            doc_info.pDatatype = "RAW"

            job_id = winspool.StartDocPrinterW(hPrinter, 1, ctypes.byref(doc_info))
            if job_id == 0:
                cod_err = ctypes.GetLastError() if hasattr(ctypes, 'GetLastError') else 0
                return False, "No se pudo iniciar el trabajo de impresión en '{}'. (Error {})".format(nombre_destino, cod_err)

            try:
                if not winspool.StartPagePrinter(hPrinter):
                    cod_err = ctypes.GetLastError() if hasattr(ctypes, 'GetLastError') else 0
                    return False, "Error al iniciar página de impresión. (Error {})".format(cod_err)

                try:
                    bytes_escritos = wintypes.DWORD(0)
                    buffer = ctypes.create_string_buffer(datos_bytes, len(datos_bytes))
                    tamano = wintypes.DWORD(len(datos_bytes))
                    exito = winspool.WritePrinter(hPrinter, buffer, tamano, ctypes.byref(bytes_escritos))
                    if not exito:
                        cod_err = ctypes.GetLastError() if hasattr(ctypes, 'GetLastError') else 0
                        return False, "Error al enviar los datos a la impresora. (Error {})".format(cod_err)
                finally:
                    winspool.EndPagePrinter(hPrinter)
            finally:
                winspool.EndDocPrinter(hPrinter)
        finally:
            winspool.ClosePrinter(hPrinter)

        return True, "Impresión enviada correctamente."
    except Exception as e:
        return False, "Ocurrió una excepción al imprimir: {}".format(str(e))

def abrir_cajon(nombre_impresora=None):
    """
    Envía los pulsos eléctricos ESC/POS para abrir el cajón monedero
    conectado a la impresora térmica (puerto RJ11 / DK).
    """
    impresora = resolver_nombre_impresora(nombre_impresora)
    if not impresora:
        return False, "No hay impresora configurada ni predeterminada en Windows."

    # Comando de inicialización + pulsos para disparar el solenoide del cajón
    datos_cajon = CMD_INIT + CMD_ABRIR_CAJON
    return enviar_raw_a_impresora(impresora, datos_cajon, doc_name="Abrir Cajon")

def generar_bytes_ticket(datos_venta, config, abrir_cajon=False, cortar=True):
    """
    Construye el flujo binario completo en ESC/POS con inicialización,
    apertura de cajón si aplica, texto formateado y corte de papel.
    """
    partes = []

    # 1. Inicializar la impresora
    partes.append(CMD_INIT)

    # 2. Abrir cajón de dinero al iniciar el ticket (para dar cambio rápido)
    if abrir_cajon:
        partes.append(CMD_ABRIR_CAJON)

    # 3. Seleccionar tabla de caracteres en español (CP850)
    partes.append(CMD_SELECCIONAR_CP850)

    # 4. Texto del ticket
    texto_ticket = generar_texto_ticket(datos_venta, config)
    partes.append(codificar_para_impresora(texto_ticket))

    # 5. Avance de papel para que el texto rebase la cuchilla
    partes.append(CMD_AVANCE_LINEAS)

    # 6. Comando de corte de papel
    if cortar:
        partes.append(CMD_CORTE_PAPEL)

    return b"".join(partes)

def imprimir_ticket(datos_venta, config=None, abrir_cajon_tambien=False):
    """
    Imprime un ticket de venta en la impresora configurada o predeterminada.
    Si abrir_cajon_tambien es True, dispara el solenoide del cajón en el mismo trabajo.
    """
    if config is None:
        import database
        config = database.obtener_configuracion()

    impresora = resolver_nombre_impresora(config.get('impresora', ''))
    if not impresora:
        return False, "No hay impresora seleccionada ni predeterminada en Windows."

    cortar = bool(int(config.get('cortar_papel', 1)))
    datos_bytes = generar_bytes_ticket(datos_venta, config, abrir_cajon=abrir_cajon_tambien, cortar=cortar)
    folio = datos_venta.get('folio', 'T-00000')

    return enviar_raw_a_impresora(impresora, datos_bytes, doc_name="Ticket {}".format(folio))

def imprimir_corte(resumen_caja, movimientos, config=None):
    """
    Imprime el corte de caja diario en la impresora térmica.
    """
    if config is None:
        import database
        config = database.obtener_configuracion()

    impresora = resolver_nombre_impresora(config.get('impresora', ''))
    if not impresora:
        return False, "No hay impresora seleccionada ni predeterminada en Windows."

    cortar = bool(int(config.get('cortar_papel', 1)))

    partes = []
    partes.append(CMD_INIT)
    partes.append(CMD_SELECCIONAR_CP850)

    texto_corte = generar_texto_corte(resumen_caja, movimientos, config)
    partes.append(codificar_para_impresora(texto_corte))
    partes.append(CMD_AVANCE_LINEAS)

    if cortar:
        partes.append(CMD_CORTE_PAPEL)

    datos_bytes = b"".join(partes)
    turno_id = resumen_caja.get('id_turno', 1)
    return enviar_raw_a_impresora(impresora, datos_bytes, doc_name="Corte Turno #{}".format(turno_id))

def probar_impresion(nombre_impresora=None, ancho=ANCHO_80MM):
    """
    Imprime un ticket de prueba pequeño para verificar el funcionamiento de la impresora.
    Soporta anchos de 58mm (32 cols), 70mm (36 cols) y 80mm (40 cols).
    """
    impresora = resolver_nombre_impresora(nombre_impresora)
    if not impresora:
        return False, "No se ha seleccionado una impresora para probar."

    ancho = resolver_ancho_ticket(ancho)
    lineas = []
    lineas.append(centrar_texto("PRUEBA DE IMPRESORA POS", ancho))
    lineas.append(linea_separadora("=", ancho))
    lineas.append("Impresora: {}".format(impresora[:max(10, ancho - 12)]))
    lineas.append("Fecha/Hora: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    etiqueta_papel = "80mm"
    if ancho <= 32:
        etiqueta_papel = "58mm"
    elif ancho <= 37:
        etiqueta_papel = "70mm"

    lineas.append("Ancho: {} columnas ({})".format(ancho, etiqueta_papel))
    lineas.append(linea_separadora("-", ancho))
    if ancho <= 32:
        lineas.append(centrar_texto("¡La comunicacion con", ancho))
        lineas.append(centrar_texto("la impresora funciona", ancho))
        lineas.append(centrar_texto("correctamente!", ancho))
    else:
        lineas.append(centrar_texto("¡La comunicacion con la", ancho))
        lineas.append(centrar_texto("impresora funciona correctamente!", ancho))
    lineas.append(linea_separadora("=", ancho))
    lineas.append("\n")

    partes = [
        CMD_INIT,
        CMD_SELECCIONAR_CP850,
        codificar_para_impresora("\n".join(lineas)),
        CMD_AVANCE_LINEAS,
        CMD_CORTE_PAPEL
    ]
    return enviar_raw_a_impresora(impresora, b"".join(partes), doc_name="Prueba Impresora")

def probar_cajon(nombre_impresora=None):
    """
    Envía únicamente la señal de apertura de cajón para verificar la conexión RJ11.
    """
    return abrir_cajon(nombre_impresora)
