# -*- coding: utf-8 -*-
"""
Módulo de Formateo e Impresión de Tickets y Cortes de Caja.
Compatible con impresoras térmicas (58mm / 80mm), bloc de notas de Windows y consolas.
Compatible con Python 3.4+ y Windows XP.
"""

import os
import datetime

def centrar_texto(texto, ancho):
    """Centra una línea de texto según el ancho especificado."""
    return texto.center(ancho)

def linea_separadora(caracter="=", ancho=40):
    """Genera una línea divisoria."""
    return caracter * ancho

def generar_texto_ticket(datos_venta, config):
    """
    Genera el formato en texto plano para un ticket de compra.
    datos_venta: dict con 'folio', 'fecha_hora', 'articulos', 'total', 'pago_con', 'cambio', 'metodo_pago'
    config: dict con 'nombre_tienda', 'direccion', 'telefono', 'mensaje_ticket', 'ancho_ticket'
    """
    ancho = int(config.get('ancho_ticket', 40))
    lineas = []

    # Encabezado
    lineas.append(centrar_texto(config.get('nombre_tienda', 'DULCERÍA').upper(), ancho))
    if config.get('direccion'):
        lineas.append(centrar_texto(config.get('direccion'), ancho))
    if config.get('telefono'):
        lineas.append(centrar_texto("Tel: " + config.get('telefono'), ancho))

    lineas.append(linea_separadora("=", ancho))
    lineas.append("FOLIO: {:<15} CAJA: 1".format(datos_venta.get('folio', 'T-00000')))
    lineas.append("FECHA: {}".format(datos_venta.get('fecha_hora', '')))
    lineas.append(linea_separadora("-", ancho))

    # Columnas de artículos: Cant | Descripcion | Precio | Subtotal
    # Formato para 40 caracteres: "CANT  PRODUCTO           PRECIO  IMPORTE"
    lineas.append("{:<5} {:<17} {:>7} {:>8}".format("CANT", "PRODUCTO", "P.UNIT", "TOTAL"))
    lineas.append(linea_separadora("-", ancho))

    total_piezas = 0
    for art in datos_venta.get('articulos', []):
        cant = art.get('cantidad', 1)
        total_piezas += cant
        nombre = art.get('nombre', 'Producto')
        # Si el nombre es largo, recortarlo para que encaje
        if len(nombre) > 17:
            nombre = nombre[:15] + ".."
        precio = float(art.get('precio', 0.0))
        subtotal = float(art.get('subtotal', cant * precio))

        # Formato de cantidad (entero si no tiene decimales)
        str_cant = "{:.0f}".format(cant) if cant.is_integer() else "{:.2f}".format(cant)

        lineas.append("{:<5} {:<17} {:>7.2f} {:>8.2f}".format(str_cant, nombre, precio, subtotal))

    lineas.append(linea_separadora("=", ancho))
    lineas.append("{:>25} {:>14}".format("TOTAL DE ARTICULOS:", "{:.0f}".format(total_piezas)))
    lineas.append("{:>25} ${:>13.2f}".format("TOTAL A PAGAR:", float(datos_venta.get('total', 0.0))))
    lineas.append("{:>25} ${:>13.2f}".format("PAGO CON:", float(datos_venta.get('pago_con', 0.0))))
    lineas.append("{:>25} ${:>13.2f}".format("SU CAMBIO:", float(datos_venta.get('cambio', 0.0))))
    lineas.append(linea_separadora("=", ancho))

    # Pie de ticket
    mensaje = config.get('mensaje_ticket', '¡Gracias por su preferencia!')
    for parte in mensaje.split("\n"):
        lineas.append(centrar_texto(parte.strip(), ancho))

    lineas.append("\n\n") # Espacio para corte de papel
    return "\n".join(lineas)

def guardar_ticket_en_archivo(datos_venta, config):
    """Guarda una copia del ticket en la carpeta tickets/."""
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
        # Fallback a latin-1 para compatibilidad extrema con Windows XP
        try:
            with open(ruta_archivo, "w", encoding="latin-1", errors="replace") as f:
                f.write(texto)
            return ruta_archivo
        except Exception:
            return None

def generar_texto_corte(resumen_caja, movimientos, config):
    """
    Genera el formato en texto del Corte de Caja diario.
    """
    ancho = int(config.get('ancho_ticket', 40))
    lineas = []

    lineas.append(centrar_texto(config.get('nombre_tienda', 'DULCERÍA').upper(), ancho))
    lineas.append(centrar_texto("CORTE DE CAJA / CIERRE DE TURNO", ancho))
    lineas.append(linea_separadora("=", ancho))

    lineas.append("TURNO ID: #{}".format(resumen_caja.get('id_turno', 1)))
    lineas.append("APERTURA: {}".format(resumen_caja.get('fecha_inicio', '')))
    lineas.append("CIERRE:   {}".format(resumen_caja.get('fecha_fin') or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    lineas.append(linea_separadora("-", ancho))

    lineas.append("{:<25} ${:>12.2f}".format("(+) Fondo Inicial de Caja:", float(resumen_caja.get('monto_inicial', 0.0))))
    lineas.append("{:<25} ${:>12.2f}".format("(+) Ventas en Efectivo:", float(resumen_caja.get('total_ventas', 0.0))))
    lineas.append("{:<25}   {:>12}".format("    Número de ventas:", resumen_caja.get('num_ventas', 0)))
    lineas.append("{:<25} ${:>12.2f}".format("(+) Entradas de Dinero:", float(resumen_caja.get('total_entradas', 0.0))))
    lineas.append("{:<25} ${:>12.2f}".format("(-) Salidas de Dinero:", float(resumen_caja.get('total_salidas', 0.0))))
    lineas.append(linea_separadora("=", ancho))

    lineas.append("{:<25} ${:>12.2f}".format("TOTAL ESPERADO EN CAJA:", float(resumen_caja.get('dinero_esperado', 0.0))))
    lineas.append(linea_separadora("=", ancho))

    lineas.append("{:<25} ${:>12.2f}".format("Costo de Mercancía:", float(resumen_caja.get('total_costo', 0.0))))
    lineas.append("{:<25} ${:>12.2f}".format("GANANCIA ESTIMADA:", float(resumen_caja.get('ganancia_estimada', 0.0))))
    lineas.append(linea_separadora("-", ancho))

    if movimientos:
        lineas.append(centrar_texto("DETALLE DE MOVIMIENTOS", ancho))
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

    lineas.append("\n\nFirma del Responsable: __________________\n\n")
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
