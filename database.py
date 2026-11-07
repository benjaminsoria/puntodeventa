# -*- coding: utf-8 -*-
"""
Módulo de Base de Datos para el Punto de Venta de Dulcería.
Compatible con Python 3.4+ y Windows XP (sin dependencias externas).
"""

import os
import sqlite3
import datetime
import shutil

DB_FILENAME = "dulceria.db"

def obtener_ruta_db():
    """Retorna la ruta absoluta del archivo de base de datos en el directorio actual."""
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directorio_base, DB_FILENAME)

def conectar_db():
    """Crea una conexión con SQLite y habilita claves foráneas."""
    ruta = obtener_ruta_db()
    conn = sqlite3.connect(ruta)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def inicializar_db():
    """Crea las tablas necesarias si no existen y precarga datos iniciales."""
    conn = conectar_db()
    cursor = conn.cursor()

    # Tabla de Configuración de la Tienda
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracion (
        id INTEGER PRIMARY KEY,
        nombre_tienda TEXT NOT NULL,
        telefono TEXT,
        direccion TEXT,
        mensaje_ticket TEXT,
        ancho_ticket INTEGER DEFAULT 40,
        impresora TEXT DEFAULT '',
        imprimir_automatico INTEGER DEFAULT 1,
        abrir_cajon_automatico INTEGER DEFAULT 1,
        cortar_papel INTEGER DEFAULT 1
    )
    """)

    # Migración de columnas de impresora y cajón para bases de datos existentes
    cursor.execute("PRAGMA table_info(configuracion)")
    cols_existentes = [row[1] for row in cursor.fetchall()]
    if 'impresora' not in cols_existentes:
        cursor.execute("ALTER TABLE configuracion ADD COLUMN impresora TEXT DEFAULT ''")
    if 'imprimir_automatico' not in cols_existentes:
        cursor.execute("ALTER TABLE configuracion ADD COLUMN imprimir_automatico INTEGER DEFAULT 1")
    if 'abrir_cajon_automatico' not in cols_existentes:
        cursor.execute("ALTER TABLE configuracion ADD COLUMN abrir_cajon_automatico INTEGER DEFAULT 1")
    if 'cortar_papel' not in cols_existentes:
        cursor.execute("ALTER TABLE configuracion ADD COLUMN cortar_papel INTEGER DEFAULT 1")

    # Tabla de Categorías
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL
    )
    """)

    # Tabla de Productos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        categoria TEXT DEFAULT 'Dulces',
        precio_costo REAL DEFAULT 0.0,
        precio_venta REAL NOT NULL,
        stock REAL DEFAULT 0.0,
        stock_minimo REAL DEFAULT 5.0,
        unidad TEXT DEFAULT 'Pza',
        es_favorito INTEGER DEFAULT 0,
        activo INTEGER DEFAULT 1
    )
    """)

    # Tabla de Turnos / Caja
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS turnos_caja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT,
        monto_inicial REAL DEFAULT 0.0,
        monto_final REAL DEFAULT 0.0,
        estado TEXT DEFAULT 'ABIERTA',
        observaciones TEXT
    )
    """)

    # Tabla de Movimientos de Caja (Entradas y Salidas)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos_caja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_turno INTEGER,
        fecha_hora TEXT NOT NULL,
        tipo TEXT NOT NULL, -- 'ENTRADA' o 'SALIDA'
        monto REAL NOT NULL,
        motivo TEXT NOT NULL,
        FOREIGN KEY (id_turno) REFERENCES turnos_caja (id)
    )
    """)

    # Tabla de Ventas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT UNIQUE NOT NULL,
        id_turno INTEGER,
        fecha_hora TEXT NOT NULL,
        total REAL NOT NULL,
        costo_total REAL DEFAULT 0.0,
        pago_con REAL NOT NULL,
        cambio REAL NOT NULL,
        metodo_pago TEXT DEFAULT 'Efectivo',
        estado TEXT DEFAULT 'COMPLETADA', -- 'COMPLETADA' o 'CANCELADA'
        motivo_cancelacion TEXT,
        FOREIGN KEY (id_turno) REFERENCES turnos_caja (id)
    )
    """)

    # Tabla de Detalle de Ventas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_venta INTEGER NOT NULL,
        id_producto INTEGER,
        codigo TEXT,
        nombre_producto TEXT NOT NULL,
        cantidad REAL NOT NULL,
        precio_unitario REAL NOT NULL,
        costo_unitario REAL DEFAULT 0.0,
        subtotal REAL NOT NULL,
        FOREIGN KEY (id_venta) REFERENCES ventas (id) ON DELETE CASCADE,
        FOREIGN KEY (id_producto) REFERENCES productos (id)
    )
    """)

    # Insertar configuración inicial por defecto si está vacía
    cursor.execute("SELECT COUNT(*) FROM configuracion")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO configuracion (id, nombre_tienda, telefono, direccion, mensaje_ticket, ancho_ticket, impresora, imprimir_automatico, abrir_cajon_automatico, cortar_papel)
        VALUES (1, 'Dulcería La Bendición', '55-1234-5678', 'Av. Principal #123, Col. Centro', '¡Gracias por su compra! Vuelva pronto.', 40, '', 1, 1, 1)
        """)

    # Categorías iniciales
    categorias_base = ['Dulces y Paletas', 'Chocolates', 'Gomitas', 'Botanas y Frituras', 'Bebidas', 'Granel / Varios']
    for cat in categorias_base:
        cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (cat,))

    # Insertar productos de ejemplo si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos_ejemplo = [
            # codigo, nombre, categoria, costo, venta, stock, stock_min, unidad, es_favorito
            ('101', 'Mazapán de la Rosa 28g', 'Dulces y Paletas', 4.50, 7.00, 50, 10, 'Pza', 1),
            ('102', 'Paleta Payaso Ricolino 45g', 'Chocolates', 12.00, 18.00, 30, 6, 'Pza', 1),
            ('103', 'Pelón Pelo Rico 30g', 'Dulces y Paletas', 7.50, 12.00, 40, 8, 'Pza', 1),
            ('104', 'Pulparindo De la Rosa 14g', 'Dulces y Paletas', 3.50, 6.00, 60, 15, 'Pza', 1),
            ('105', 'Duvalín Avellana Fresa', 'Chocolates', 3.00, 5.00, 48, 12, 'Pza', 1),
            ('106', 'Bubbaloo Fresa', 'Dulces y Paletas', 1.20, 2.00, 100, 25, 'Pza', 1),
            ('107', 'Bubbaloo Menta', 'Dulces y Paletas', 1.20, 2.00, 80, 20, 'Pza', 1),
            ('108', 'Picafresa Vero', 'Dulces y Paletas', 0.80, 1.50, 120, 30, 'Pza', 1),
            ('109', 'Paleta Vero Mango con Chile', 'Dulces y Paletas', 4.00, 6.50, 35, 10, 'Pza', 1),
            ('110', 'Paleta Vero Elote', 'Dulces y Paletas', 4.00, 6.50, 35, 10, 'Pza', 1),
            ('111', 'Rockaleta Paleta', 'Dulces y Paletas', 5.00, 8.00, 25, 8, 'Pza', 1),
            ('112', 'Panditas Ricolino 65g', 'Gomitas', 11.00, 16.00, 24, 6, 'Pza', 1),
            ('113', 'Kranky Ricolino 40g', 'Chocolates', 10.50, 16.00, 20, 5, 'Pza', 1),
            ('114', 'Chocolate Carlos V 18g', 'Chocolates', 7.00, 11.00, 30, 8, 'Pza', 1),
            ('115', 'Skwinkles Salsagheti Sandía', 'Dulces y Paletas', 8.50, 14.00, 20, 5, 'Pza', 1),
            ('116', 'Lucas Muecas Chamoy', 'Dulces y Paletas', 9.00, 15.00, 18, 5, 'Pza', 1),
            ('117', 'Chupa Chups Surtida', 'Dulces y Paletas', 4.20, 7.00, 45, 10, 'Pza', 1),
            ('118', 'Cacahuates Japoneses 100g', 'Botanas y Frituras', 6.00, 10.00, 25, 6, 'Pza', 0),
            ('119', 'Gomitas Panditas a Granel', 'Gomitas', 65.00, 110.00, 5.0, 1.0, 'Kg', 0),
            ('120', 'Refresco Coca Cola 600ml', 'Bebidas', 14.50, 19.00, 24, 8, 'Pza', 0),
        ]
        cursor.executemany("""
        INSERT INTO productos (codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, unidad, es_favorito)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, productos_ejemplo)

    conn.commit()
    conn.close()

# ==========================================================
# GESTIÓN DE CONFIGURACIÓN
# ==========================================================

def obtener_configuracion():
    """Obtiene los datos de configuración del negocio y de impresión."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM configuracion WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        cfg = dict(row)
        cfg.setdefault('ancho_ticket', 40)
        cfg.setdefault('impresora', '')
        cfg.setdefault('imprimir_automatico', 1)
        cfg.setdefault('abrir_cajon_automatico', 1)
        cfg.setdefault('cortar_papel', 1)
        return cfg
    return {
        'nombre_tienda': 'Mi Dulcería',
        'telefono': '',
        'direccion': '',
        'mensaje_ticket': '¡Gracias por su compra!',
        'ancho_ticket': 40,
        'impresora': '',
        'imprimir_automatico': 1,
        'abrir_cajon_automatico': 1,
        'cortar_papel': 1
    }

def guardar_configuracion(nombre, telefono, direccion, mensaje, ancho=40,
                          impresora=None, imprimir_automatico=None,
                          abrir_cajon_automatico=None, cortar_papel=None):
    """Actualiza los datos de configuración de la tienda y periféricos."""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM configuracion WHERE id = 1")
    actual = dict(cursor.fetchone() or {})

    imp_final = impresora.strip() if impresora is not None else actual.get('impresora', '')
    imp_auto = int(imprimir_automatico) if imprimir_automatico is not None else actual.get('imprimir_automatico', 1)
    cajon_auto = int(abrir_cajon_automatico) if abrir_cajon_automatico is not None else actual.get('abrir_cajon_automatico', 1)
    corte_auto = int(cortar_papel) if cortar_papel is not None else actual.get('cortar_papel', 1)

    cursor.execute("""
    UPDATE configuracion
    SET nombre_tienda = ?, telefono = ?, direccion = ?, mensaje_ticket = ?, ancho_ticket = ?,
        impresora = ?, imprimir_automatico = ?, abrir_cajon_automatico = ?, cortar_papel = ?
    WHERE id = 1
    """, (nombre.strip(), telefono.strip(), direccion.strip(), mensaje.strip(), int(ancho),
          imp_final, imp_auto, cajon_auto, corte_auto))
    conn.commit()
    conn.close()

# ==========================================================
# GESTIÓN DE PRODUCTOS E INVENTARIO
# ==========================================================

def obtener_todos_los_productos(solo_activos=True, filtro="", categoria=None, solo_bajos=False):
    """Busca productos según filtros opcionales."""
    conn = conectar_db()
    cursor = conn.cursor()

    query = "SELECT * FROM productos WHERE 1=1"
    params = []

    if solo_activos:
        query += " AND activo = 1"

    if categoria and categoria != "Todas":
        query += " AND categoria = ?"
        params.append(categoria)

    if filtro:
        query += " AND (codigo LIKE ? OR nombre LIKE ?)"
        patron = "%" + filtro.strip() + "%"
        params.extend([patron, patron])

    if solo_bajos:
        query += " AND stock <= stock_minimo"

    query += " ORDER BY nombre ASC"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def obtener_productos_favoritos():
    """Retorna los productos marcados como favoritos para la botonera rápida."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE activo = 1 AND es_favorito = 1 ORDER BY nombre ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def buscar_producto_por_codigo(codigo):
    """Busca un producto exacto por su código de barras o clave interna."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE codigo = ? AND activo = 1", (codigo.strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def agregar_producto(codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, unidad='Pza', es_favorito=0):
    """Inserta un nuevo producto al catálogo."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO productos (codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, unidad, es_favorito, activo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (codigo.strip(), nombre.strip(), categoria.strip(), float(precio_costo), float(precio_venta), float(stock), float(stock_minimo), unidad, int(es_favorito)))
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()
        return True, nuevo_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Ya existe un producto con el código '{}'.".format(codigo)
    except Exception as e:
        conn.close()
        return False, str(e)

def actualizar_producto(id_prod, codigo, nombre, categoria, precio_costo, precio_venta, stock, stock_minimo, unidad='Pza', es_favorito=0):
    """Actualiza los datos de un producto existente."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        UPDATE productos
        SET codigo = ?, nombre = ?, categoria = ?, precio_costo = ?, precio_venta = ?,
            stock = ?, stock_minimo = ?, unidad = ?, es_favorito = ?
        WHERE id = ?
        """, (codigo.strip(), nombre.strip(), categoria.strip(), float(precio_costo), float(precio_venta), float(stock), float(stock_minimo), unidad, int(es_favorito), id_prod))
        conn.commit()
        conn.close()
        return True, "Producto actualizado correctamente."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Ya existe otro producto con el código '{}'.".format(codigo)
    except Exception as e:
        conn.close()
        return False, str(e)

def agregar_stock_rapido(id_prod, cantidad_a_sumar):
    """Suma cantidad al stock existente de un producto (para recepción rápida de pedidos)."""
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (float(cantidad_a_sumar), id_prod))
        conn.commit()
        conn.close()
        return True, "Stock actualizado exitosamente."
    except Exception as e:
        conn.close()
        return False, str(e)

def eliminar_o_desactivar_producto(id_prod):
    """Desactiva un producto para mantener consistencia con ventas pasadas."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET activo = 0 WHERE id = ?", (id_prod,))
    conn.commit()
    conn.close()
    return True

def obtener_categorias():
    """Retorna la lista de todas las categorías registradas."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM categorias ORDER BY nombre ASC")
    filas = [r['nombre'] for r in cursor.fetchall()]
    conn.close()
    return filas

def agregar_categoria(nombre):
    """Agrega una categoría si no existe."""
    if not nombre or not nombre.strip():
        return False
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (nombre.strip(),))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

# ==========================================================
# GESTIÓN DE TURNOS Y CORTE DE CAJA
# ==========================================================

def obtener_turno_actual():
    """Retorna el turno abierto actualmente o None si no hay turno abierto."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM turnos_caja WHERE estado = 'ABIERTA' ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def abrir_turno(monto_inicial, observaciones=""):
    """Abre un nuevo turno de caja con el fondo inicial para dar cambio."""
    turno_actual = obtener_turno_actual()
    if turno_actual:
        return False, "Ya hay un turno abierto actualmente (Turno #{}).".format(turno_actual['id'])

    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO turnos_caja (fecha_inicio, monto_inicial, estado, observaciones)
    VALUES (?, ?, 'ABIERTA', ?)
    """, (ahora, float(monto_inicial), observaciones))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return True, nuevo_id

def cerrar_turno(id_turno, monto_final, observaciones=""):
    """Cierra el turno de caja registrando el conteo final de dinero."""
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE turnos_caja
    SET fecha_fin = ?, monto_final = ?, estado = 'CERRADA', observaciones = ?
    WHERE id = ? AND estado = 'ABIERTA'
    """, (ahora, float(monto_final), observaciones, id_turno))
    conn.commit()
    conn.close()
    return True

def registrar_movimiento_caja(id_turno, tipo, monto, motivo):
    """Registra una entrada o salida de efectivo (ej. pago a repartidor o fondo extra)."""
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO movimientos_caja (id_turno, fecha_hora, tipo, monto, motivo)
    VALUES (?, ?, ?, ?, ?)
    """, (id_turno, ahora, tipo.upper(), float(monto), motivo.strip()))
    conn.commit()
    conn.close()
    return True

def obtener_movimientos_turno(id_turno):
    """Obtiene todas las entradas y salidas de un turno específico."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movimientos_caja WHERE id_turno = ? ORDER BY id ASC", (id_turno,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def calcular_resumen_caja(id_turno):
    """Calcula las ventas, ganancias, entradas, salidas y dinero esperado en caja para un turno."""
    conn = conectar_db()
    cursor = conn.cursor()

    # Obtener turno
    cursor.execute("SELECT * FROM turnos_caja WHERE id = ?", (id_turno,))
    turno = cursor.fetchone()
    if not turno:
        conn.close()
        return None

    monto_inicial = float(turno['monto_inicial'])

    # Ventas en el turno
    cursor.execute("""
    SELECT COUNT(*) as num_ventas,
           COALESCE(SUM(total), 0.0) as total_ventas,
           COALESCE(SUM(costo_total), 0.0) as total_costo
    FROM ventas
    WHERE id_turno = ? AND estado = 'COMPLETADA'
    """, (id_turno,))
    datos_ventas = cursor.fetchone()
    num_ventas = datos_ventas['num_ventas']
    total_ventas = float(datos_ventas['total_ventas'])
    total_costo = float(datos_ventas['total_costo'])
    ganancia_estimada = total_ventas - total_costo

    # Entradas de dinero
    cursor.execute("""
    SELECT COALESCE(SUM(monto), 0.0) as total_entradas
    FROM movimientos_caja
    WHERE id_turno = ? AND tipo = 'ENTRADA'
    """, (id_turno,))
    total_entradas = float(cursor.fetchone()['total_entradas'])

    # Salidas de dinero (retiros, pagos)
    cursor.execute("""
    SELECT COALESCE(SUM(monto), 0.0) as total_salidas
    FROM movimientos_caja
    WHERE id_turno = ? AND tipo = 'SALIDA'
    """, (id_turno,))
    total_salidas = float(cursor.fetchone()['total_salidas'])

    # Dinero que debe haber físicamente en caja
    dinero_esperado = monto_inicial + total_ventas + total_entradas - total_salidas

    conn.close()

    return {
        'id_turno': id_turno,
        'fecha_inicio': turno['fecha_inicio'],
        'fecha_fin': turno['fecha_fin'],
        'estado': turno['estado'],
        'monto_inicial': monto_inicial,
        'num_ventas': num_ventas,
        'total_ventas': round(total_ventas, 2),
        'total_costo': round(total_costo, 2),
        'ganancia_estimada': round(ganancia_estimada, 2),
        'total_entradas': round(total_entradas, 2),
        'total_salidas': round(total_salidas, 2),
        'dinero_esperado': round(dinero_esperado, 2)
    }

# ==========================================================
# GESTIÓN DE VENTAS
# ==========================================================

def generar_siguiente_folio():
    """Genera un folio secuencial amigable para el ticket, ej: T-00001."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM ventas")
    max_id = cursor.fetchone()[0]
    conn.close()
    siguiente = 1 if max_id is None else (max_id + 1)
    return "T-{:05d}".format(siguiente)

def registrar_venta(id_turno, lista_carrito, pago_con, metodo_pago="Efectivo"):
    """
    Registra una venta de forma atómica:
    - Valida turno
    - Calcula totales y costos
    - Descuenta existencias del inventario
    - Guarda venta y detalle de venta
    lista_carrito: lista de diccionarios:
      [{'id': prod_id, 'codigo': cod, 'nombre': nom, 'precio': float, 'costo': float, 'cantidad': float}]
    """
    if not lista_carrito:
        return False, "El carrito de compras está vacío.", None

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        total_venta = 0.0
        total_costo = 0.0

        for item in lista_carrito:
            cant = float(item['cantidad'])
            prec = float(item['precio'])
            cost = float(item.get('costo', 0.0))
            sub = round(cant * prec, 2)
            item['subtotal'] = sub
            total_venta += sub
            total_costo += round(cant * cost, 2)

        total_venta = round(total_venta, 2)
        total_costo = round(total_costo, 2)
        pago_con = float(pago_con)

        if pago_con < total_venta:
            conn.close()
            return False, "El pago recibido (${:.2f}) es menor al total (${:.2f}).".format(pago_con, total_venta), None

        cambio = round(pago_con - total_venta, 2)
        folio = generar_siguiente_folio()
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Iniciar transacción
        cursor.execute("BEGIN TRANSACTION")

        cursor.execute("""
        INSERT INTO ventas (folio, id_turno, fecha_hora, total, costo_total, pago_con, cambio, metodo_pago, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETADA')
        """, (folio, id_turno, ahora, total_venta, total_costo, pago_con, cambio, metodo_pago))
        id_venta = cursor.lastrowid

        for item in lista_carrito:
            cursor.execute("""
            INSERT INTO detalle_ventas (id_venta, id_producto, codigo, nombre_producto, cantidad, precio_unitario, costo_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_venta, item.get('id'), item.get('codigo', ''), item['nombre'], item['cantidad'], item['precio'], item.get('costo', 0.0), item['subtotal']))

            # Descontar stock
            if item.get('id'):
                cursor.execute("""
                UPDATE productos
                SET stock = stock - ?
                WHERE id = ?
                """, (item['cantidad'], item['id']))

        conn.commit()
        conn.close()

        datos_ticket = {
            'id_venta': id_venta,
            'folio': folio,
            'fecha_hora': ahora,
            'total': total_venta,
            'pago_con': pago_con,
            'cambio': cambio,
            'metodo_pago': metodo_pago,
            'articulos': lista_carrito
        }
        return True, "Venta registrada con éxito.", datos_ticket

    except Exception as e:
        conn.rollback()
        conn.close()
        return False, "Error al registrar venta: {}".format(str(e)), None

def cancelar_venta(id_venta, motivo="Cancelación manual"):
    """
    Cancela una venta y reincorpora los productos al inventario automáticamente.
    """
    conn = conectar_db()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("SELECT estado FROM ventas WHERE id = ?", (id_venta,))
        venta = cursor.fetchone()
        if not venta:
            conn.close()
            return False, "La venta no existe."
        if venta['estado'] == 'CANCELADA':
            conn.close()
            return False, "La venta ya está cancelada."

        # Reintegrar stock de cada producto
        cursor.execute("SELECT id_producto, cantidad FROM detalle_ventas WHERE id_venta = ?", (id_venta,))
        detalles = cursor.fetchall()
        for det in detalles:
            if det['id_producto']:
                cursor.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (det['cantidad'], det['id_producto']))

        # Marcar venta como cancelada
        cursor.execute("UPDATE ventas SET estado = 'CANCELADA', motivo_cancelacion = ? WHERE id = ?", (motivo, id_venta))

        conn.commit()
        conn.close()
        return True, "Venta cancelada e inventario restablecido exitosamente."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, "Error al cancelar venta: {}".format(str(e))

def obtener_historial_ventas(fecha_filtro=None, solo_completadas=False):
    """Retorna lista de ventas ordenadas por fecha reciente."""
    conn = conectar_db()
    cursor = conn.cursor()

    query = "SELECT * FROM ventas WHERE 1=1"
    params = []

    if fecha_filtro:
        query += " AND fecha_hora LIKE ?"
        params.append(fecha_filtro + "%")

    if solo_completadas:
        query += " AND estado = 'COMPLETADA'"

    query += " ORDER BY id DESC LIMIT 200"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def obtener_detalle_venta(id_venta):
    """Obtiene los productos vendidos en una venta específica."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detalle_ventas WHERE id_venta = ? ORDER BY id ASC", (id_venta,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def obtener_venta_por_id(id_venta):
    """Obtiene los datos generales de una venta por su ID."""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas WHERE id = ?", (id_venta,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def preparar_datos_ticket_desde_venta(id_venta):
    """Reconstruye el formato de ticket para reimpresión a partir de un ID de venta."""
    venta = obtener_venta_por_id(id_venta)
    if not venta:
        return None
    detalles = obtener_detalle_venta(id_venta)
    articulos = []
    for d in detalles:
        articulos.append({
            'nombre': d['nombre_producto'],
            'cantidad': d['cantidad'],
            'precio': d['precio_unitario'],
            'subtotal': d['subtotal']
        })
    return {
        'id_venta': venta['id'],
        'folio': venta['folio'],
        'fecha_hora': venta['fecha_hora'],
        'total': venta['total'],
        'pago_con': venta['pago_con'],
        'cambio': venta['cambio'],
        'metodo_pago': venta.get('metodo_pago', 'Efectivo'),
        'articulos': articulos
    }

# ==========================================================
# RESPALDO Y RESTAURACIÓN (ESENCIAL PARA MÁQUINAS SIN INTERNET)
# ==========================================================

def crear_respaldo(directorio_destino=None):
    """
    Copia el archivo SQLite a una memoria USB o carpeta de respaldo con fecha y hora.
    """
    ruta_origen = obtener_ruta_db()
    if not os.path.exists(ruta_origen):
        return False, "No se encontró el archivo de base de datos para respaldar."

    if not directorio_destino:
        directorio_base = os.path.dirname(os.path.abspath(__file__))
        directorio_destino = os.path.join(directorio_base, "respaldos")

    if not os.path.exists(directorio_destino):
        try:
            os.makedirs(directorio_destino)
        except Exception as e:
            return False, "No se pudo crear la carpeta de respaldos: {}".format(str(e))

    nombre_archivo = "respaldo_dulceria_{}.db".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    ruta_destino = os.path.join(directorio_destino, nombre_archivo)

    try:
        shutil.copy2(ruta_origen, ruta_destino)
        return True, ruta_destino
    except Exception as e:
        return False, "Error al copiar archivo de respaldo: {}".format(str(e))

def restaurar_respaldo(ruta_archivo_respaldo):
    """Restaura la base de datos a partir de un archivo de respaldo seleccionado."""
    if not os.path.exists(ruta_archivo_respaldo):
        return False, "El archivo de respaldo no existe."

    ruta_actual = obtener_ruta_db()
    try:
        # Hacemos una copia de seguridad preventiva antes de sobreescribir
        if os.path.exists(ruta_actual):
            shutil.copy2(ruta_actual, ruta_actual + ".previo_a_restaurar")
        shutil.copy2(ruta_archivo_respaldo, ruta_actual)
        return True, "Base de datos restaurada correctamente."
    except Exception as e:
        return False, "Error al restaurar base de datos: {}".format(str(e))
