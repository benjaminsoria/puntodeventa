# -*- coding: utf-8 -*-
"""
Módulo para generación y exportación de etiquetas de precios en formato .doc (RTF).
Diseñado para etiquetas de 1.5 cm de alto por 5.0 cm de ancho (4 columnas x 17 filas = 68 por página).
Totalmente compatible con Windows XP SP3, Word 2003/2007/2010/2016/365, WordPad, LibreOffice y Python 3.4+.
Construido únicamente con la biblioteca estándar de Python (100% offline, sin dependencias pip).
"""

import os
import sys
import datetime

# Constantes de medidas (1 cm = 566.929 twips)
TWIPS_POR_CM = 567
ANCHO_ETIQUETA_TWIPS = 2835  # 5.0 cm exactos
ALTO_ETIQUETA_TWIPS = 850    # 1.5 cm exactos

COLUMNAS_POR_HOJA = 4
FILAS_POR_HOJA = 17
ETIQUETAS_POR_HOJA = COLUMNAS_POR_HOJA * FILAS_POR_HOJA  # 68 etiquetas por página

# Márgenes para hoja Carta / Letter (12240 x 15840 twips)
# 4 columnas * 2835 = 11340 twips (20.0 cm).
# Margen horizontal: (12240 - 11340) / 2 = 450 twips (~0.79 cm por lado).
MARGEN_IZQ_TWIPS = 450
MARGEN_DER_TWIPS = 450

# 17 filas * 850 = 14450 twips (25.49 cm).
# Altura hoja Carta = 15840 twips. Margen restante = 1390 twips.
# Con 550 twips (~0.97 cm) arriba y abajo aseguramos que 17 filas quepan
# holgadamente tanto en papel Carta como en papel A4 sin desbordar.
MARGEN_ARR_TWIPS = 550
MARGEN_ABA_TWIPS = 550

ANCHO_PAGINA_TWIPS = 12240  # Carta: 8.5 pulgadas
ALTO_PAGINA_TWIPS = 15840   # Carta: 11.0 pulgadas


def escapar_rtf(texto):
    """
    Escapa caracteres especiales para el formato RTF garantizando compatibilidad
    con Windows-1252 y Unicode en cualquier versión de Word o WordPad.
    Retorna una cadena 100% en rango ASCII seguro.
    """
    if texto is None:
        return ""
    texto = str(texto)
    res = []
    for ch in texto:
        if ch == '\\':
            res.append(r'\\')
        elif ch == '{':
            res.append(r'\{')
        elif ch == '}':
            res.append(r'\}')
        else:
            cp = ord(ch)
            if cp < 128:
                res.append(ch)
            elif cp <= 255:
                res.append(r"\'%02x" % cp)
            else:
                signed_cp = cp if cp < 32768 else cp - 65536
                res.append(r"\u%d?" % signed_cp)
    return "".join(res)


def formatear_precio(precio):
    """Formatea el precio a formato legible con signo de pesos ($X.XX)."""
    try:
        val = float(precio)
        return "${:.2f}".format(val)
    except (ValueError, TypeError):
        return "${}".format(precio)


def obtener_ruta_escritorio():
    """
    Obtiene la ruta absoluta a la carpeta del Escritorio del usuario.
    Funciona de manera precisa en:
      - Windows XP en Español: C:\\Documents and Settings\\<usuario>\\Escritorio
      - Windows XP en Inglés: C:\\Documents and Settings\\<usuario>\\Desktop
      - Windows 7, 8, 10, 11 (incluidas carpetas redirigidas)
      - Linux y macOS
    """
    # 1. En sistemas Windows, consultar el Registro del Sistema
    if os.name == 'nt':
        try:
            import winreg
            clave = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            )
            ruta_reg, _ = winreg.QueryValueEx(clave, "Desktop")
            winreg.CloseKey(clave)
            ruta_exp = os.path.expandvars(ruta_reg)
            if os.path.exists(ruta_exp):
                return os.path.abspath(ruta_exp)
        except Exception:
            pass

        # Fallback de Windows mediante USERPROFILE
        userprofile = os.environ.get('USERPROFILE')
        if userprofile:
            for carpeta in ["Escritorio", "Desktop"]:
                p = os.path.join(userprofile, carpeta)
                if os.path.exists(p):
                    return os.path.abspath(p)

    # 2. Linux / macOS / Fallback general
    home = os.path.expanduser("~")
    for carpeta in ["Escritorio", "Desktop"]:
        p = os.path.join(home, carpeta)
        if os.path.exists(p):
            return os.path.abspath(p)

    return os.path.abspath(home)


def generar_rtf_etiquetas(lista_productos, copias_por_producto=1):
    """
    Genera el contenido de un documento RTF (.doc) con las etiquetas de dulces.
    
    Parámetros:
      lista_productos: lista de diccionarios, cada uno con al menos:
                       'nombre' (nombre del dulce)
                       'precio_venta' o 'precio' (precio al público)
      copias_por_producto: número de etiquetas a generar por cada producto (default: 1).
      
    Retorna:
      Cadena con el documento RTF formateado.
    """
    # Expandir según el número de copias
    items = []
    copias = max(1, int(copias_por_producto))
    for prod in lista_productos:
        nombre = prod.get('nombre', '')
        precio = prod.get('precio_venta', prod.get('precio', 0.0))
        for _ in range(copias):
            items.append((nombre, precio))

    if not items:
        return None

    cols = COLUMNAS_POR_HOJA
    filas_por_hoja = FILAS_POR_HOJA
    num_filas = (len(items) + cols - 1) // cols

    rtf = []
    # Encabezado RTF estándar
    rtf.append(r'{\rtf1\ansi\ansicpg1252\deff0')
    rtf.append(r'{\fonttbl{\f0\fswiss\fcharset0 Arial;}}')
    # Paleta de colores: 1: Negro, 2: Gris medio para líneas de corte
    rtf.append(r'{\colortbl ;\red0\green0\blue0;\red120\green120\blue120;}')
    
    # Configuración de página: Papel Carta con márgenes optimizados
    rtf.append(r'\paperw{}\paperh{}\margl{}\margr{}\margt{}\margb{}'.format(
        ANCHO_PAGINA_TWIPS, ALTO_PAGINA_TWIPS,
        MARGEN_IZQ_TWIPS, MARGEN_DER_TWIPS,
        MARGEN_ARR_TWIPS, MARGEN_ABA_TWIPS
    ))

    for r in range(num_filas):
        # Salto de página exacto cada 17 filas (excepto al inicio)
        if r > 0 and r % filas_por_hoja == 0:
            rtf.append(r'\page')

        # Definición de fila: fija a 1.5 cm (-850 twips exactos), sin partirse entre páginas
        rtf.append(r'\trowd\trkeep\trgaph40\trleft0\trrh-{}'.format(ALTO_ETIQUETA_TWIPS))

        # Definir las 4 celdas de la fila (5.0 cm cada una, bordes punteados de corte)
        for c in range(cols):
            x = (c + 1) * ANCHO_ETIQUETA_TWIPS
            rtf.append(
                r'\clvertalc'
                r'\clbrdrt\brdrdash\brdrw10\brdrcf2'
                r'\clbrdrb\brdrdash\brdrw10\brdrcf2'
                r'\clbrdrl\brdrdash\brdrw10\brdrcf2'
                r'\clbrdrr\brdrdash\brdrw10\brdrcf2'
                r'\cellx{}'.format(x)
            )

        # Contenido de cada celda
        for c in range(cols):
            idx = r * cols + c
            if idx < len(items):
                nom_raw, pre_raw = items[idx]
                nom_str = str(nom_raw).strip()
                pre_str = formatear_precio(pre_raw)

                # Ajustar longitud del nombre para que no desborde la celda de 1.5 cm
                if len(nom_str) > 38:
                    nom_display = nom_str[:35] + "..."
                else:
                    nom_display = nom_str

                # Tamaño de fuente: si el nombre es largo, 6.5pt (fs13) o 7pt (fs14); si no, 7.5pt (fs15)
                fs_nom = 13 if len(nom_display) > 22 else 14
                fs_pre = 20  # 10 pt para el precio

                nom_esc = escapar_rtf(nom_display)
                pre_esc = escapar_rtf(pre_str)

                # Celda con centrado horizontal y vertical
                rtf.append(
                    r'{\qc\sl-130\slmult0\fs' + str(fs_nom) + r'\b ' + nom_esc +
                    r'\b0\par\sl-160\slmult0\fs' + str(fs_pre) + r'\b ' + pre_esc +
                    r'\b0\cell}'
                )
            else:
                # Celda vacía que conserva los bordes de la cuadrícula
                rtf.append(r'{\cell}')

        rtf.append(r'\row')

    rtf.append(r'}')
    return '\n'.join(rtf)


def exportar_etiquetas_escritorio(lista_productos, copias_por_producto=1, nombre_base="etiquetas"):
    """
    Genera el archivo .doc con las etiquetas y lo guarda directamente
    en el Escritorio de la máquina con el formato:
      etiquetas_YYYY-MM-DD.doc
      
    Retorna una tupla: (exito, mensaje, ruta_archivo)
    """
    if not lista_productos:
        return False, "No hay productos seleccionados para exportar etiquetas.", None

    contenido = generar_rtf_etiquetas(lista_productos, copias_por_producto)
    if not contenido:
        return False, "Error al formatear las etiquetas de los productos.", None

    escritorio = obtener_ruta_escritorio()
    if not os.path.exists(escritorio):
        try:
            os.makedirs(escritorio)
        except Exception:
            escritorio = os.path.abspath(".")

    hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = "{}_{}.doc".format(nombre_base, hoy)
    ruta_completa = os.path.join(escritorio, nombre_archivo)

    # Si el archivo ya existe y está bloqueado por Word, intentar con timestamp
    try:
        with open(ruta_completa, "w", encoding="latin-1") as f:
            f.write(contenido)
    except (IOError, PermissionError):
        ahora = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        nombre_archivo = "{}_{}.doc".format(nombre_base, ahora)
        ruta_completa = os.path.join(escritorio, nombre_archivo)
        try:
            with open(ruta_completa, "w", encoding="latin-1") as f:
                f.write(contenido)
        except Exception as e:
            return False, "No se pudo guardar el archivo en el escritorio: {}".format(e), None

    total_etiquetas = len(lista_productos) * max(1, int(copias_por_producto))
    msg = (
        "Se exportaron exitosamente {} etiquetas en formato .doc.\n"
        "Archivo guardado en el Escritorio:\n{}"
    ).format(total_etiquetas, ruta_completa)

    return True, msg, ruta_completa


def abrir_documento(ruta_archivo):
    """
    Abre el documento en la aplicación predeterminada del sistema (Microsoft Word,
    WordPad, LibreOffice, etc.).
    """
    if not ruta_archivo or not os.path.exists(ruta_archivo):
        return False

    try:
        if os.name == 'nt':
            os.startfile(ruta_archivo)
        elif sys.platform.startswith('darwin'):
            import subprocess
            subprocess.Popen(['open', ruta_archivo])
        else:
            import subprocess
            subprocess.Popen(['xdg-open', ruta_archivo])
        return True
    except Exception:
        return False
