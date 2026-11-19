# -*- coding: utf-8 -*-
"""
Módulo de Interfaz de Punto de Venta (Ventas y Cobro).
Diseñado para máxima facilidad de uso con letras grandes, atajos y calculadora de cambio.
Compatible con Python 3.4+ y Windows XP.
"""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    tk = None
    ttk = None
    messagebox = None

_FrameBase = tk.Frame if tk else object

import database
import ticket

def interpretar_cantidad(texto, valor_defecto=1.0):
    """
    Interpreta cantidades numéricas, decimales, fraccionarias o con unidades:
    '0.5', '.500', '0.500', '0,500', ',5' -> 0.5
    '500g', '250 gr', '100 gramos' -> 0.5, 0.25, 0.1
    '1/2', '1/4', '3/4' -> 0.5, 0.25, 0.75
    '2' -> 2.0
    """
    if texto is None:
        return valor_defecto
    s = str(texto).strip().lower().replace(',', '.')
    if not s:
        return valor_defecto

    # Fracciones comunes
    if s in ('1/2', '0.5'):
        return 0.5
    if s in ('1/4', '0.25'):
        return 0.25
    if s in ('3/4', '0.75'):
        return 0.75
    if '/' in s:
        partes = s.split('/')
        if len(partes) == 2:
            try:
                num = float(partes[0].strip())
                den = float(partes[1].strip())
                if den != 0:
                    return num / den
            except ValueError:
                pass

    # Sufijos de kilos y gramos (revisar 'kg' antes de 'g')
    if s.endswith('kilos'):
        try:
            return float(s[:-5].strip())
        except ValueError:
            pass
    elif s.endswith('kilo'):
        try:
            return float(s[:-4].strip())
        except ValueError:
            pass
    elif s.endswith('kg'):
        try:
            return float(s[:-2].strip())
        except ValueError:
            pass
    elif s.endswith('gramos'):
        try:
            return float(s[:-6].strip()) / 1000.0
        except ValueError:
            pass
    elif s.endswith('gr'):
        try:
            return float(s[:-2].strip()) / 1000.0
        except ValueError:
            pass
    elif s.endswith('g'):
        try:
            return float(s[:-1].strip()) / 1000.0
        except ValueError:
            pass
    elif s.endswith('k'):
        try:
            return float(s[:-1].strip())
        except ValueError:
            pass

    # Float directo (ej. .500, 0.5, 2, etc.)
    try:
        return float(s)
    except ValueError:
        return None

def formatear_cantidad(cant):
    """
    Formatea la cantidad de manera amigable.
    Si es entero: '1', '2'.
    Si es decimal: muestra decimales limpios (ej. '0.500', '0.250', '1.500').
    """
    try:
        c = float(cant)
        if c.is_integer():
            return "{:.0f}".format(c)
        return "{:.3f}".format(c)
    except (ValueError, TypeError):
        return str(cant)


class DialogoCobro(object):
    """Ventana modal grande para realizar el cobro, calcular cambio y confirmar la venta."""

    def __init__(self, parent, total, items_carrito, id_turno, callback_exito):
        self.parent = parent
        self.total = float(total)
        self.items_carrito = items_carrito
        self.id_turno = id_turno
        self.callback_exito = callback_exito
        self.ticket_generado = None

        self.top = tk.Toplevel(parent)
        self.top.title("Cobrar Venta")
        self.top.geometry("520x560")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        # Centrar ventana
        self.centrar_ventana(520, 560)

        self.crear_interfaz()

        # Atajos de teclado en el diálogo
        self.top.bind("<Return>", lambda event: self.confirmar_cobro())
        self.top.bind("<KP_Enter>", lambda event: self.confirmar_cobro())
        self.top.bind("<Escape>", lambda event: self.top.destroy())

    def centrar_ventana(self, ancho, alto):
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.top.winfo_screenheight() // 2) - (alto // 2)
        self.top.geometry("{}x{}+{}+{}".format(ancho, alto, max(0, x), max(0, y)))

    def crear_interfaz(self):
        frame_principal = tk.Frame(self.top, padx=20, pady=15, bg="#F0F4F8")
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Banner de Total a Pagar
        frame_total = tk.Frame(frame_principal, bg="#1B365D", padx=15, pady=12)
        frame_total.pack(fill=tk.X, pady=(0, 15))

        lbl_tit_total = tk.Label(frame_total, text="TOTAL A COBRAR", font=("Arial", 14, "bold"), fg="#E2E8F0", bg="#1B365D")
        lbl_tit_total.pack()

        lbl_monto_total = tk.Label(frame_total, text="${:.2f}".format(self.total), font=("Arial", 32, "bold"), fg="#38EF7D", bg="#1B365D")
        lbl_monto_total.pack()

        # Entrada de dinero recibido
        frame_input = tk.Frame(frame_principal, bg="#F0F4F8")
        frame_input.pack(fill=tk.X, pady=5)

        lbl_paga_con = tk.Label(frame_input, text="Paga con $: ", font=("Arial", 16, "bold"), bg="#F0F4F8", fg="#2D3748")
        lbl_paga_con.pack(side=tk.LEFT)

        self.var_pago = tk.StringVar(value="")
        self.entry_pago = tk.Entry(frame_input, textvariable=self.var_pago, font=("Arial", 22, "bold"), width=12, justify="center")
        self.entry_pago.pack(side=tk.LEFT, padx=10)
        self.entry_pago.focus_set()
        self.var_pago.trace("w", self.actualizar_cambio)

        # Botones rápidos de billetes comunes
        frame_billetes = tk.LabelFrame(frame_principal, text=" Billetes Rápidos (Clic para seleccionar) ", font=("Arial", 10, "bold"), bg="#F0F4F8", fg="#4A5568", padx=10, pady=8)
        frame_billetes.pack(fill=tk.X, pady=10)

        billetes = [20, 50, 100, 200, 500]
        sub_billetes = tk.Frame(frame_billetes, bg="#F0F4F8")
        sub_billetes.pack()

        for b in billetes:
            btn_b = tk.Button(sub_billetes, text="${}".format(b), font=("Arial", 12, "bold"), bg="#E2E8F0", width=5, pady=4,
                              command=lambda val=b: self.asignar_pago(val))
            btn_b.pack(side=tk.LEFT, padx=4)

        btn_exacto = tk.Button(sub_billetes, text="Exacto", font=("Arial", 11, "bold"), bg="#CBD5E0", width=7, pady=4,
                               command=lambda: self.asignar_pago(self.total))
        btn_exacto.pack(side=tk.LEFT, padx=4)

        # Banner de Cambio a Entregar
        self.frame_cambio = tk.Frame(frame_principal, bg="#EDF2F7", padx=15, pady=10, relief=tk.RIDGE, bd=2)
        self.frame_cambio.pack(fill=tk.X, pady=10)

        self.lbl_tit_cambio = tk.Label(self.frame_cambio, text="CAMBIO A ENTREGAR", font=("Arial", 13, "bold"), fg="#4A5568", bg="#EDF2F7")
        self.lbl_tit_cambio.pack()

        self.lbl_cambio = tk.Label(self.frame_cambio, text="$0.00", font=("Arial", 28, "bold"), fg="#2B6CB0", bg="#EDF2F7")
        self.lbl_cambio.pack()

        # Opciones de Impresión y Cajón
        cfg = database.obtener_configuracion()
        auto_imprimir = bool(cfg.get('imprimir_automatico', 1))
        auto_cajon = bool(cfg.get('abrir_cajon_automatico', 1))

        frame_opciones = tk.Frame(frame_principal, bg="#F0F4F8")
        frame_opciones.pack(pady=6)

        self.var_imprimir = tk.BooleanVar(value=auto_imprimir)
        chk_imp = tk.Checkbutton(frame_opciones, text="Imprimir Ticket", variable=self.var_imprimir,
                                 font=("Arial", 11, "bold"), bg="#F0F4F8", fg="#2D3748")
        chk_imp.pack(side=tk.LEFT, padx=10)

        self.var_cajon = tk.BooleanVar(value=auto_cajon)
        chk_caj = tk.Checkbutton(frame_opciones, text="Abrir Cajón", variable=self.var_cajon,
                                 font=("Arial", 11, "bold"), bg="#F0F4F8", fg="#2D3748")
        chk_caj.pack(side=tk.LEFT, padx=10)

        # Botones de Acción
        frame_acciones = tk.Frame(frame_principal, bg="#F0F4F8")
        frame_acciones.pack(fill=tk.X, pady=(10, 0))

        self.btn_confirmar = tk.Button(frame_acciones, text="CONFIRMAR COBRO (Enter)", font=("Arial", 14, "bold"), bg="#38A169", fg="white", pady=8,
                                       command=self.confirmar_cobro, state=tk.DISABLED)
        self.btn_confirmar.pack(fill=tk.X, pady=4)

        btn_cancelar = tk.Button(frame_acciones, text="Volver al Carrito (Esc)", font=("Arial", 11), bg="#E2E8F0", fg="#4A5568", pady=4,
                                 command=self.top.destroy)
        btn_cancelar.pack(fill=tk.X)

    def asignar_pago(self, monto):
        self.var_pago.set("{:.2f}".format(monto))
        self.entry_pago.focus_set()

    def actualizar_cambio(self, *args):
        texto = self.var_pago.get().strip()
        try:
            monto_pago = float(texto)
            cambio = monto_pago - self.total
            if cambio >= -0.001:
                self.lbl_tit_cambio.config(text="CAMBIO A ENTREGAR:", fg="#22543D")
                self.lbl_cambio.config(text="${:.2f}".format(cambio), fg="#276749")
                self.frame_cambio.config(bg="#C6F6D5")
                self.lbl_tit_cambio.config(bg="#C6F6D5")
                self.lbl_cambio.config(bg="#C6F6D5")
                self.btn_confirmar.config(state=tk.NORMAL)
            else:
                faltante = abs(cambio)
                self.lbl_tit_cambio.config(text="DINERO INSUFICIENTE (FALTAN):", fg="#9B2C2C")
                self.lbl_cambio.config(text="- ${:.2f}".format(faltante), fg="#C53030")
                self.frame_cambio.config(bg="#FED7D7")
                self.lbl_tit_cambio.config(bg="#FED7D7")
                self.lbl_cambio.config(bg="#FED7D7")
                self.btn_confirmar.config(state=tk.DISABLED)
        except ValueError:
            self.lbl_tit_cambio.config(text="CAMBIO A ENTREGAR:", fg="#4A5568")
            self.lbl_cambio.config(text="$0.00", fg="#2B6CB0")
            self.frame_cambio.config(bg="#EDF2F7")
            self.lbl_tit_cambio.config(bg="#EDF2F7")
            self.lbl_cambio.config(bg="#EDF2F7")
            self.btn_confirmar.config(state=tk.DISABLED)

    def confirmar_cobro(self):
        try:
            monto_pago = float(self.var_pago.get().strip())
        except ValueError:
            messagebox.showwarning("Atención", "Por favor ingrese una cantidad de dinero válida.", parent=self.top)
            return

        if monto_pago < self.total:
            messagebox.showwarning("Atención", "El dinero recibido es menor que el total de la venta.", parent=self.top)
            return

        cambio = round(monto_pago - self.total, 2)

        # Registrar la venta en la base de datos
        exito, msg, datos_ticket = database.registrar_venta(self.id_turno, self.items_carrito, monto_pago, "Efectivo")

        if not exito:
            messagebox.showerror("Error al guardar venta", msg, parent=self.top)
            return

        cfg = database.obtener_configuracion()

        # Siempre guardar copia de respaldo en archivo de texto
        ticket.guardar_ticket_en_archivo(datos_ticket, cfg)

        debe_imprimir = self.var_imprimir.get()
        debe_abrir_cajon = self.var_cajon.get()

        error_periferico = None
        if debe_imprimir:
            # Imprime ticket y abre cajón en el mismo flujo si ambos están activos
            ok_imp, msg_imp = ticket.imprimir_ticket(datos_ticket, cfg, abrir_cajon_tambien=debe_abrir_cajon)
            if not ok_imp:
                error_periferico = "Aviso de Impresora:\n" + msg_imp
        elif debe_abrir_cajon:
            # Si solo se solicitó abrir el cajón sin imprimir
            ok_caj, msg_caj = ticket.abrir_cajon(cfg.get('impresora', ''))
            if not ok_caj:
                error_periferico = "Aviso de Cajón:\n" + msg_caj

        self.top.destroy()

        if error_periferico:
            messagebox.showwarning(
                "Aviso de Hardware",
                "La venta se registró exitosamente, pero:\n\n"
                "{}\n\nVerifique que la impresora esté encendida o revise [F5] Ajustes.".format(error_periferico),
                parent=self.parent
            )

        # Mostrar mensaje de éxito con el cambio bien grande
        self.mostrar_exito(cambio, datos_ticket.get('folio', ''))

        if self.callback_exito:
            self.callback_exito()

    def mostrar_exito(self, cambio, folio):
        win_exito = tk.Toplevel(self.parent)
        win_exito.title("¡Venta Exitosa!")
        win_exito.geometry("450x280")
        win_exito.resizable(False, False)
        win_exito.transient(self.parent)
        win_exito.grab_set()

        # Centrar
        win_exito.update_idletasks()
        x = (win_exito.winfo_screenwidth() // 2) - (450 // 2)
        y = (win_exito.winfo_screenheight() // 2) - (280 // 2)
        win_exito.geometry("450x280+{}+{}".format(max(0, x), max(0, y)))

        f = tk.Frame(win_exito, bg="#F0FFF4", padx=20, pady=20)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="¡VENTA REGISTRADA CON ÉXITO!", font=("Arial", 16, "bold"), fg="#22543D", bg="#F0FFF4").pack(pady=5)
        tk.Label(f, text="Ticket Folio: {}".format(folio), font=("Arial", 12), fg="#4A5568", bg="#F0FFF4").pack()

        f_cambio = tk.Frame(f, bg="#C6F6D5", padx=15, pady=10, relief=tk.SOLID, bd=1)
        f_cambio.pack(fill=tk.X, pady=15)

        tk.Label(f_cambio, text="ENTREGAR CAMBIO AL CLIENTE:", font=("Arial", 13, "bold"), fg="#22543D", bg="#C6F6D5").pack()
        tk.Label(f_cambio, text="${:.2f}".format(cambio), font=("Arial", 32, "bold"), fg="#276749", bg="#C6F6D5").pack()

        btn_ok = tk.Button(f, text="Aceptar y Nueva Venta (Enter)", font=("Arial", 13, "bold"), bg="#38A169", fg="white", pady=6,
                           command=win_exito.destroy)
        btn_ok.pack(fill=tk.X, pady=5)
        btn_ok.focus_set()

        win_exito.bind("<Return>", lambda e: win_exito.destroy())
        win_exito.bind("<KP_Enter>", lambda e: win_exito.destroy())
        win_exito.bind("<space>", lambda e: win_exito.destroy())


class DialogoBuscarProducto(object):
    """Buscador rápido emergente cuando hay múltiples coincidencias por nombre."""

    def __init__(self, parent, criterio_inicial, callback_seleccion):
        self.parent = parent
        self.callback_seleccion = callback_seleccion

        self.top = tk.Toplevel(parent)
        self.top.title("Seleccionar Dulce")
        self.top.geometry("650x420")
        self.top.transient(parent)
        self.top.grab_set()

        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - 325
        y = (self.top.winfo_screenheight() // 2) - 210
        self.top.geometry("650x420+{}+{}".format(max(0, x), max(0, y)))

        # Barra de búsqueda
        f_top = tk.Frame(self.top, padx=10, pady=8, bg="#EDF2F7")
        f_top.pack(fill=tk.X)

        tk.Label(f_top, text="Buscar dulce:", font=("Arial", 11, "bold"), bg="#EDF2F7").pack(side=tk.LEFT, padx=5)
        self.var_buscar = tk.StringVar(value=criterio_inicial)
        self.entry_buscar = tk.Entry(f_top, textvariable=self.var_buscar, font=("Arial", 12), width=30)
        self.entry_buscar.pack(side=tk.LEFT, padx=5)
        self.entry_buscar.focus_set()
        self.var_buscar.trace("w", self.filtrar)

        # Tabla de resultados
        cols = ("codigo", "nombre", "categoria", "precio", "stock")
        self.tree = ttk.Treeview(self.top, columns=cols, show="headings", height=12)
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre del Dulce")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("stock", text="Stock")

        self.tree.column("codigo", width=80, anchor="center")
        self.tree.column("nombre", width=260)
        self.tree.column("categoria", width=120)
        self.tree.column("precio", width=80, anchor="e")
        self.tree.column("stock", width=70, anchor="center")

        scroll = ttk.Scrollbar(self.top, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scroll.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)

        # Botones inferiores
        f_bot = tk.Frame(self.top, padx=10, pady=8)
        f_bot.pack(side=tk.BOTTOM, fill=tk.X)

        btn_sel = tk.Button(f_bot, text="Seleccionar Dulce (Enter)", font=("Arial", 11, "bold"), bg="#3182CE", fg="white",
                            command=self.confirmar_seleccion)
        btn_sel.pack(side=tk.RIGHT, padx=5)

        btn_cancel = tk.Button(f_bot, text="Cerrar", font=("Arial", 10), command=self.top.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

        self.tree.bind("<Double-1>", lambda e: self.confirmar_seleccion())
        self.top.bind("<Return>", lambda e: self.confirmar_seleccion())
        self.top.bind("<KP_Enter>", lambda e: self.confirmar_seleccion())
        self.top.bind("<Escape>", lambda e: self.top.destroy())

        self.cargar_productos(criterio_inicial)

    def filtrar(self, *args):
        self.cargar_productos(self.var_buscar.get())

    def cargar_productos(self, texto):
        for item in self.tree.get_children():
            self.tree.delete(item)

        prods = database.obtener_todos_los_productos(solo_activos=True, filtro=texto)
        for p in prods:
            self.tree.insert("", "end", iid=p['id'], values=(
                p['codigo'],
                p['nombre'],
                p['categoria'],
                "${:.2f}".format(p['precio_venta']),
                "{:.0f}".format(p['stock']) if p['stock'].is_integer() else "{:.2f}".format(p['stock'])
            ))

        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.tree.focus(children[0])

    def confirmar_seleccion(self):
        sel = self.tree.selection()
        if not sel:
            return
        id_prod = int(sel[0])
        self.top.destroy()
        self.callback_seleccion(id_prod)


class DialogoArticuloNoCatalogado(object):
    """
    Ventana modal para registrar un artículo no catalogado para la venta actual
    (ej. dulces sueltos por kilo, bolsas a granel, mercancía sin código).
    Permite fijar precio por kilo/unidad y cantidad decimal (ej. .500 gramos, 1/4 kg, etc.).
    """

    def __init__(self, parent, callback_agregar, nombre_inicial="", cantidad_inicial="1"):
        self.parent = parent
        self.callback_agregar = callback_agregar
        self.nombre_inicial = nombre_inicial.strip() if nombre_inicial else "Dulces a Granel"
        self.cantidad_inicial = str(cantidad_inicial).strip() if cantidad_inicial else ".500"

        self.top = tk.Toplevel(parent)
        self.top.title("Artículo No Catalogado / Venta a Granel")
        self.top.geometry("540x630")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.centrar_ventana(540, 630)
        self.crear_interfaz()

        # Atajos de teclado
        self.top.bind("<Escape>", lambda event: self.top.destroy())

    def centrar_ventana(self, ancho, alto):
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.top.winfo_screenheight() // 2) - (alto // 2)
        self.top.geometry("{}x{}+{}+{}".format(ancho, alto, max(0, x), max(0, y)))

    def crear_interfaz(self):
        frame_principal = tk.Frame(self.top, padx=18, pady=12, bg="#F0F4F8")
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # Banner Superior
        frame_header = tk.Frame(frame_principal, bg="#4A5568", padx=12, pady=10)
        frame_header.pack(fill=tk.X, pady=(0, 10))

        tk.Label(frame_header, text="ARTÍCULO NO CATALOGADO / GRANEL", font=("Arial", 13, "bold"), fg="#FFFFFF", bg="#4A5568").pack()
        tk.Label(frame_header, text="Venta manual de dulces sueltos por kilo, piezas o varios", font=("Arial", 9), fg="#CBD5E0", bg="#4A5568").pack()

        # 1. Nombre / Descripción del Dulce
        f_nombre = tk.Frame(frame_principal, bg="#F0F4F8")
        f_nombre.pack(fill=tk.X, pady=4)

        tk.Label(f_nombre, text="Nombre del Dulce / Artículo:", font=("Arial", 11, "bold"), bg="#F0F4F8", fg="#2D3748").pack(anchor="w")
        self.var_nombre = tk.StringVar(value=self.nombre_inicial)
        self.entry_nombre = tk.Entry(f_nombre, textvariable=self.var_nombre, font=("Arial", 13), width=32)
        self.entry_nombre.pack(fill=tk.X, pady=2)
        self.entry_nombre.bind("<Return>", lambda e: self.entry_precio.focus_set())
        self.entry_nombre.bind("<KP_Enter>", lambda e: self.entry_precio.focus_set())

        # Botones de sugerencias de nombres comunes
        f_sugerencias = tk.Frame(frame_principal, bg="#F0F4F8")
        f_sugerencias.pack(fill=tk.X, pady=(0, 6))
        sug_nombres = ["Dulces a Granel", "Gomitas Sueltas", "Chocolates Sueltos", "Artículo Varios"]
        for sug in sug_nombres:
            btn_s = tk.Button(f_sugerencias, text=sug, font=("Arial", 8), bg="#E2E8F0", padx=4, pady=1,
                              command=lambda s=sug: self.asignar_nombre(s))
            btn_s.pack(side=tk.LEFT, padx=2)

        # 2. Precio Unitario ($ por Kilo o Pieza)
        f_precio = tk.Frame(frame_principal, bg="#F0F4F8")
        f_precio.pack(fill=tk.X, pady=4)

        tk.Label(f_precio, text="Precio por Kilo o Pieza ($):", font=("Arial", 11, "bold"), bg="#F0F4F8", fg="#2D3748").pack(anchor="w")
        self.var_precio = tk.StringVar(value="")
        self.entry_precio = tk.Entry(f_precio, textvariable=self.var_precio, font=("Arial", 16, "bold"), width=15, justify="center")
        self.entry_precio.pack(anchor="w", pady=2)
        self.entry_precio.bind("<Return>", lambda e: self.entry_cantidad.focus_set())
        self.entry_precio.bind("<KP_Enter>", lambda e: self.entry_cantidad.focus_set())
        self.var_precio.trace("w", self.recalcular_subtotal)

        # 3. Cantidad / Peso
        f_cant = tk.Frame(frame_principal, bg="#F0F4F8")
        f_cant.pack(fill=tk.X, pady=4)

        tk.Label(f_cant, text="Cantidad o Peso (ej. .500, 0.5, 1, 0.250):", font=("Arial", 11, "bold"), bg="#F0F4F8", fg="#2D3748").pack(anchor="w")
        val_cant_ini = self.cantidad_inicial if self.cantidad_inicial != "1" else ".500"
        self.var_cantidad = tk.StringVar(value=val_cant_ini)
        self.entry_cantidad = tk.Entry(f_cant, textvariable=self.var_cantidad, font=("Arial", 16, "bold"), width=15, justify="center")
        self.entry_cantidad.pack(anchor="w", pady=2)
        self.entry_cantidad.bind("<Return>", lambda e: self.confirmar())
        self.entry_cantidad.bind("<KP_Enter>", lambda e: self.confirmar())
        self.var_cantidad.trace("w", self.recalcular_subtotal)

        # Botones rápidos de peso común en dulcería
        f_pesos = tk.LabelFrame(frame_principal, text=" Porciones y Pesos Rápidos (Clic para seleccionar) ",
                                font=("Arial", 9, "bold"), bg="#F0F4F8", fg="#4A5568", padx=6, pady=4)
        f_pesos.pack(fill=tk.X, pady=4)

        pesos = [
            ("100g", ".100"),
            ("1/4 Kg", ".250"),
            ("1/2 Kg", ".500"),
            ("3/4 Kg", ".750"),
            ("1.0 Kg", "1"),
            ("1.5 Kg", "1.500"),
            ("2.0 Kg", "2")
        ]
        sub_p = tk.Frame(f_pesos, bg="#F0F4F8")
        sub_p.pack(fill=tk.X)
        for etiqueta, val in pesos:
            btn_p = tk.Button(sub_p, text=etiqueta, font=("Arial", 9, "bold"), bg="#EDF2F7", padx=4, pady=3,
                             command=lambda v=val: self.asignar_peso(v))
            btn_p.pack(side=tk.LEFT, padx=2)

        # 4. Calculadora por Importe en Dinero ($)
        f_dinero = tk.Frame(frame_principal, bg="#EBF8FF", padx=8, pady=6, relief=tk.GROOVE, bd=1)
        f_dinero.pack(fill=tk.X, pady=6)

        tk.Label(f_dinero, text="¿El cliente pide una cantidad fija de dinero? (ej. $50 de dulces):",
                 font=("Arial", 9, "bold"), bg="#EBF8FF", fg="#2B6CB0").pack(anchor="w")
        sub_d = tk.Frame(f_dinero, bg="#EBF8FF")
        sub_d.pack(fill=tk.X, pady=2)

        tk.Label(sub_d, text="Dinero solicitado $: ", font=("Arial", 10), bg="#EBF8FF", fg="#2D3748").pack(side=tk.LEFT)
        self.var_dinero = tk.StringVar(value="")
        self.entry_dinero = tk.Entry(sub_d, textvariable=self.var_dinero, font=("Arial", 11, "bold"), width=10, justify="center")
        self.entry_dinero.pack(side=tk.LEFT, padx=5)
        self.var_dinero.trace("w", self.al_cambiar_dinero)
        tk.Label(sub_d, text="(Calcula el peso automáticamente)", font=("Arial", 8, "italic"), bg="#EBF8FF", fg="#718096").pack(side=tk.LEFT, padx=4)

        # 5. Banner de Subtotal en Vivo
        self.frame_subtotal = tk.Frame(frame_principal, bg="#C6F6D5", padx=12, pady=8, relief=tk.RIDGE, bd=2)
        self.frame_subtotal.pack(fill=tk.X, pady=8)

        tk.Label(self.frame_subtotal, text="SUBTOTAL A COBRAR:", font=("Arial", 11, "bold"), fg="#22543D", bg="#C6F6D5").pack()
        self.lbl_subtotal = tk.Label(self.frame_subtotal, text="$0.00", font=("Arial", 24, "bold"), fg="#276749", bg="#C6F6D5")
        self.lbl_subtotal.pack()

        # 6. Botones de Acción
        f_acciones = tk.Frame(frame_principal, bg="#F0F4F8")
        f_acciones.pack(fill=tk.X, pady=(6, 0))

        self.btn_confirmar = tk.Button(f_acciones, text="✓ AGREGAR A LA VENTA (Enter)", font=("Arial", 13, "bold"),
                                       bg="#38A169", fg="white", pady=8, cursor="hand2", command=self.confirmar)
        self.btn_confirmar.pack(fill=tk.X, pady=3)

        btn_cancelar = tk.Button(f_acciones, text="Cancelar (Esc)", font=("Arial", 10), bg="#E2E8F0", fg="#4A5568", pady=4,
                                 command=self.top.destroy)
        btn_cancelar.pack(fill=tk.X)

        # Foco inicial inteligente
        if self.nombre_inicial and self.nombre_inicial != "Dulces a Granel":
            self.entry_precio.focus_set()
        else:
            self.entry_nombre.focus_set()

    def asignar_nombre(self, texto):
        self.var_nombre.set(texto)
        self.entry_precio.focus_set()

    def asignar_peso(self, peso_str):
        self.var_cantidad.set(peso_str)
        self.entry_cantidad.focus_set()

    def al_cambiar_dinero(self, *args):
        txt_dinero = self.var_dinero.get().strip()
        txt_precio = self.var_precio.get().strip()
        if not txt_dinero or not txt_precio:
            return
        try:
            monto = float(txt_dinero.replace(',', '.'))
            precio = float(txt_precio.replace(',', '.'))
            if precio > 0 and monto > 0:
                calc_cant = round(monto / precio, 3)
                self.var_cantidad.set("{:.3f}".format(calc_cant))
        except ValueError:
            pass

    def recalcular_subtotal(self, *args):
        txt_precio = self.var_precio.get().strip()
        txt_cant = self.var_cantidad.get().strip()
        cant = interpretar_cantidad(txt_cant, valor_defecto=None)
        try:
            prec = float(txt_precio.replace(',', '.'))
        except (ValueError, TypeError):
            prec = None

        if cant is not None and prec is not None and cant > 0 and prec >= 0:
            sub = round(cant * prec, 2)
            self.lbl_subtotal.config(text="${:.2f}".format(sub), fg="#276749")
            self.frame_subtotal.config(bg="#C6F6D5")
        else:
            self.lbl_subtotal.config(text="$0.00", fg="#718096")

    def confirmar(self):
        nombre = self.var_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta Nombre", "Por favor escriba el nombre o descripción del dulce.", parent=self.top)
            self.entry_nombre.focus_set()
            return

        txt_precio = self.var_precio.get().strip()
        try:
            precio = float(txt_precio.replace(',', '.'))
            if precio <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            messagebox.showwarning("Precio Inválido", "Por favor ingrese un precio válido mayor a cero.", parent=self.top)
            self.entry_precio.focus_set()
            return

        txt_cant = self.var_cantidad.get().strip()
        cant = interpretar_cantidad(txt_cant, valor_defecto=None)
        if cant is None or cant <= 0:
            messagebox.showwarning("Cantidad Inválida", "Por favor ingrese una cantidad o peso válido (ej. .500, 0.5, 1, 0.250).", parent=self.top)
            self.entry_cantidad.focus_set()
            return

        self.top.destroy()
        self.callback_agregar(nombre, precio, cant)


class DialogoModificarCantidad(object):
    """Ventana rápida para modificar la cantidad o peso de un producto seleccionado en el carrito."""

    def __init__(self, parent, item_carrito, callback_actualizar):
        self.parent = parent
        self.item = item_carrito
        self.callback_actualizar = callback_actualizar

        self.top = tk.Toplevel(parent)
        self.top.title("Modificar Cantidad / Peso")
        self.top.geometry("420x370")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.centrar_ventana(420, 370)
        self.crear_interfaz()

        self.top.bind("<Escape>", lambda e: self.top.destroy())

    def centrar_ventana(self, ancho, alto):
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.top.winfo_screenheight() // 2) - (alto // 2)
        self.top.geometry("{}x{}+{}+{}".format(ancho, alto, max(0, x), max(0, y)))

    def crear_interfaz(self):
        f = tk.Frame(self.top, padx=16, pady=12, bg="#F0F4F8")
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text=self.item['nombre'], font=("Arial", 12, "bold"), fg="#1A202C", bg="#F0F4F8", wraplength=380).pack(pady=(0, 4))
        tk.Label(f, text="Precio Unitario: ${:.2f}".format(self.item['precio']), font=("Arial", 10), fg="#4A5568", bg="#F0F4F8").pack(pady=(0, 10))

        tk.Label(f, text="Nueva Cantidad o Peso (ej. .500, 0.5, 1, 0.250):", font=("Arial", 11, "bold"), fg="#2D3748", bg="#F0F4F8").pack(anchor="w")

        cant_str = formatear_cantidad(self.item['cantidad'])
        self.var_cant = tk.StringVar(value=cant_str)
        self.entry_cant = tk.Entry(f, textvariable=self.var_cant, font=("Arial", 16, "bold"), width=12, justify="center")
        self.entry_cant.pack(pady=4)
        self.entry_cant.focus_set()
        self.entry_cant.select_range(0, tk.END)

        self.entry_cant.bind("<Return>", lambda e: self.confirmar())
        self.entry_cant.bind("<KP_Enter>", lambda e: self.confirmar())

        # Botones rápidos
        f_pesos = tk.Frame(f, bg="#F0F4F8")
        f_pesos.pack(fill=tk.X, pady=8)

        pesos = [("1/4 Kg", ".250"), ("1/2 Kg", ".500"), ("3/4 Kg", ".750"), ("1 Kg", "1"), ("+1", "+1"), ("-1", "-1")]
        for lbl, v in pesos:
            btn = tk.Button(f_pesos, text=lbl, font=("Arial", 9, "bold"), bg="#EDF2F7", padx=3, pady=2,
                            command=lambda val=v: self.ajustar_valor(val))
            btn.pack(side=tk.LEFT, padx=2)

        # Subtotal
        self.lbl_sub = tk.Label(f, text="", font=("Arial", 12, "bold"), fg="#276749", bg="#F0F4F8")
        self.lbl_sub.pack(pady=6)
        self.var_cant.trace("w", self.actualizar_sub)
        self.actualizar_sub()

        # Botones inferiores
        btn_ok = tk.Button(f, text="✓ Actualizar Cantidad (Enter)", font=("Arial", 12, "bold"), bg="#38A169", fg="white", pady=6,
                           command=self.confirmar)
        btn_ok.pack(fill=tk.X, pady=4)

        btn_cancel = tk.Button(f, text="Cancelar (Esc)", font=("Arial", 10), bg="#E2E8F0", fg="#4A5568", command=self.top.destroy)
        btn_cancel.pack(fill=tk.X)

    def ajustar_valor(self, val):
        if val == "+1":
            c = interpretar_cantidad(self.var_cant.get().strip(), 0.0) or 0.0
            self.var_cant.set(formatear_cantidad(c + 1))
        elif val == "-1":
            c = interpretar_cantidad(self.var_cant.get().strip(), 0.0) or 0.0
            if c > 1:
                self.var_cant.set(formatear_cantidad(c - 1))
        else:
            self.var_cant.set(val)
        self.entry_cant.focus_set()

    def actualizar_sub(self, *args):
        c = interpretar_cantidad(self.var_cant.get().strip(), None)
        if c is not None and c > 0:
            sub = round(c * self.item['precio'], 2)
            self.lbl_sub.config(text="Nuevo Subtotal: ${:.2f}".format(sub))
        else:
            self.lbl_sub.config(text="")

    def confirmar(self):
        c = interpretar_cantidad(self.var_cant.get().strip(), None)
        if c is None or c <= 0:
            messagebox.showwarning("Atención", "Por favor ingrese una cantidad válida mayor a cero.", parent=self.top)
            self.entry_cant.focus_set()
            return
        self.top.destroy()
        self.callback_actualizar(c)


class FrameVentas(_FrameBase):
    """Pantalla principal de ventas / punto de venta."""

    def __init__(self, parent, app_principal):
        super(FrameVentas, self).__init__(parent, bg="#F7FAFC")
        self.app = app_principal
        self.carrito = [] # Lista de items en la venta actual

        self.crear_interfaz()
        self.recargar_favoritos()

    def crear_interfaz(self):
        # Marco superior: Búsqueda rápida y Dulces Favoritos
        frame_superior = tk.Frame(self, bg="#EDF2F7", padx=12, pady=10, relief=tk.RIDGE, bd=1)
        frame_superior.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Fila de Búsqueda
        fila_busqueda = tk.Frame(frame_superior, bg="#EDF2F7")
        fila_busqueda.pack(fill=tk.X)

        lbl_scan = tk.Label(fila_busqueda, text="Escanear Código / Nombre del Dulce:", font=("Arial", 12, "bold"), bg="#EDF2F7", fg="#2D3748")
        lbl_scan.pack(side=tk.LEFT, padx=(0, 10))

        self.var_busqueda = tk.StringVar()
        self.entry_busqueda = tk.Entry(fila_busqueda, textvariable=self.var_busqueda, font=("Arial", 14), width=28)
        self.entry_busqueda.pack(side=tk.LEFT, padx=5)
        self.entry_busqueda.bind("<Return>", lambda e: self.procesar_busqueda())
        self.entry_busqueda.bind("<KP_Enter>", lambda e: self.procesar_busqueda())

        lbl_cant = tk.Label(fila_busqueda, text="Cant:", font=("Arial", 12, "bold"), bg="#EDF2F7", fg="#2D3748")
        lbl_cant.pack(side=tk.LEFT, padx=(15, 5))

        self.var_cantidad = tk.StringVar(value="1")
        self.entry_cantidad = tk.Entry(fila_busqueda, textvariable=self.var_cantidad, font=("Arial", 14), width=5, justify="center")
        self.entry_cantidad.pack(side=tk.LEFT, padx=5)
        self.entry_cantidad.bind("<Return>", lambda e: self.procesar_busqueda())
        self.entry_cantidad.bind("<KP_Enter>", lambda e: self.procesar_busqueda())

        btn_agregar = tk.Button(fila_busqueda, text="+ Agregar (Enter)", font=("Arial", 11, "bold"), bg="#3182CE", fg="white", padx=12, pady=2,
                                command=self.procesar_busqueda)
        btn_agregar.pack(side=tk.LEFT, padx=10)

        btn_buscar_catalogo = tk.Button(fila_busqueda, text="Buscar en Catálogo", font=("Arial", 10), bg="#E2E8F0", padx=8, pady=2,
                                        command=self.abrir_buscador)
        btn_buscar_catalogo.pack(side=tk.LEFT, padx=5)

        btn_no_catalogado = tk.Button(fila_busqueda, text="+ Art. No Catalogado (F7)", font=("Arial", 10, "bold"),
                                      bg="#6B46C1", fg="white", padx=10, pady=2, cursor="hand2",
                                      command=self.abrir_dialogo_no_catalogado)
        btn_no_catalogado.pack(side=tk.LEFT, padx=5)

        # Fila de Botones Rápidos (Dulces más vendidos)
        self.frame_favoritos = tk.LabelFrame(frame_superior, text=" Dulces Rápidos (Clic para agregar 1 pieza) ", font=("Arial", 10, "bold"), bg="#EDF2F7", fg="#4A5568", padx=5, pady=5)
        self.frame_favoritos.pack(fill=tk.X, pady=(8, 0))

        # Marco Central: Carrito a la izquierda y Resumen/Cobro a la derecha
        frame_cuerpo = tk.Frame(self, bg="#F7FAFC")
        frame_cuerpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Panel Izquierdo: Tabla del Carrito
        frame_tabla = tk.Frame(frame_cuerpo, bg="#F7FAFC")
        frame_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cols = ("num", "codigo", "nombre", "precio", "cant", "subtotal")
        self.tree_carrito = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=14)
        self.tree_carrito.heading("num", text="#")
        self.tree_carrito.heading("codigo", text="Código")
        self.tree_carrito.heading("nombre", text="Producto / Dulce")
        self.tree_carrito.heading("precio", text="P. Unit")
        self.tree_carrito.heading("cant", text="Cant.")
        self.tree_carrito.heading("subtotal", text="Subtotal")

        self.tree_carrito.column("num", width=35, anchor="center")
        self.tree_carrito.column("codigo", width=80, anchor="center")
        self.tree_carrito.column("nombre", width=250)
        self.tree_carrito.column("precio", width=85, anchor="e")
        self.tree_carrito.column("cant", width=70, anchor="center")
        self.tree_carrito.column("subtotal", width=95, anchor="e")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scroll_y.set)

        self.tree_carrito.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.LEFT, fill=tk.Y)
        self.tree_carrito.bind("<Double-1>", lambda e: self.modificar_cantidad_seleccionado())

        # Barra de botones del carrito (debajo de la tabla)
        frame_acciones_carrito = tk.Frame(self, bg="#F7FAFC", padx=10, pady=5)
        frame_acciones_carrito.pack(fill=tk.X)

        btn_modificar_cant = tk.Button(frame_acciones_carrito, text="[ Modificar Cantidad / Peso ]", font=("Arial", 10, "bold"),
                                       bg="#EBF8FF", fg="#2B6CB0", padx=8, pady=4,
                                       command=self.modificar_cantidad_seleccionado)
        btn_modificar_cant.pack(side=tk.LEFT, padx=4)

        btn_mas = tk.Button(frame_acciones_carrito, text="[ +1 Pieza ]", font=("Arial", 10, "bold"), bg="#EDF2F7", padx=8, pady=4,
                            command=self.sumar_uno_seleccionado)
        btn_mas.pack(side=tk.LEFT, padx=4)

        btn_menos = tk.Button(frame_acciones_carrito, text="[ -1 Pieza ]", font=("Arial", 10, "bold"), bg="#EDF2F7", padx=8, pady=4,
                              command=self.restar_uno_seleccionado)
        btn_menos.pack(side=tk.LEFT, padx=4)

        btn_quitar = tk.Button(frame_acciones_carrito, text="Quitar Renglón", font=("Arial", 10), bg="#FED7D7", fg="#9B2C2C", padx=8, pady=4,
                               command=self.quitar_renglon)
        btn_quitar.pack(side=tk.LEFT, padx=4)

        btn_vaciar = tk.Button(frame_acciones_carrito, text="Cancelar Venta / Limpiar Carrito", font=("Arial", 10), bg="#E2E8F0", fg="#4A5568", padx=8, pady=4,
                               command=self.limpiar_carrito)
        btn_vaciar.pack(side=tk.LEFT, padx=15)

        # Panel Derecho: Total y Botón de Cobro
        frame_derecho = tk.Frame(frame_cuerpo, bg="#EDF2F7", width=280, padx=15, pady=15, relief=tk.RIDGE, bd=2)
        frame_derecho.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        frame_derecho.pack_propagate(False)

        lbl_tit_resumen = tk.Label(frame_derecho, text="RESUMEN DE VENTA", font=("Arial", 13, "bold"), bg="#EDF2F7", fg="#2D3748")
        lbl_tit_resumen.pack(pady=(0, 10))

        # Tarjeta de Total
        card_total = tk.Frame(frame_derecho, bg="#1A202C", padx=12, pady=15)
        card_total.pack(fill=tk.X, pady=10)

        tk.Label(card_total, text="TOTAL A PAGAR", font=("Arial", 11, "bold"), fg="#A0AEC0", bg="#1A202C").pack()
        self.lbl_gran_total = tk.Label(card_total, text="$0.00", font=("Arial", 30, "bold"), fg="#48BB78", bg="#1A202C")
        self.lbl_gran_total.pack(pady=4)

        self.lbl_cant_articulos = tk.Label(card_total, text="0 artículos", font=("Arial", 11), fg="#CBD5E0", bg="#1A202C")
        self.lbl_cant_articulos.pack()

        # Botón Enorme de Cobro
        self.btn_cobrar = tk.Button(frame_derecho, text="COBRAR\n(Tecla F12)", font=("Arial", 16, "bold"), bg="#38A169", fg="white", pady=16,
                                    cursor="hand2", command=self.iniciar_cobro)
        self.btn_cobrar.pack(fill=tk.X, pady=(15, 6))

        # Botón Manual para Abrir Cajón
        self.btn_cajon = tk.Button(frame_derecho, text="Abrir Cajón (F8)", font=("Arial", 11, "bold"), bg="#4A5568", fg="white", pady=8,
                                   cursor="hand2", command=self.abrir_cajon_manual)
        self.btn_cajon.pack(fill=tk.X, pady=(0, 10))

        lbl_ayuda = tk.Label(frame_derecho, text="Atajos rápidos:\n- F7: Art. No Catalogado / Granel\n- F12: Cobrar venta actual\n- F8: Abrir cajón de dinero\n- Doble clic en carrito: Modificar peso\n- Enter: Agregar dulce escaneado\n- Esc: Regresar a búsqueda",
                             font=("Arial", 9), justify="left", bg="#EDF2F7", fg="#718096")
        lbl_ayuda.pack(side=tk.BOTTOM, pady=5)

    def recargar_favoritos(self):
        """Llena los botones de dulces rápidos."""
        for w in self.frame_favoritos.winfo_children():
            w.destroy()

        favoritos = database.obtener_productos_favoritos()
        if not favoritos:
            lbl = tk.Label(self.frame_favoritos, text="Puedes marcar dulces como favoritos en el Catálogo de Inventario para tener acceso rápido.",
                           font=("Arial", 9, "italic"), bg="#EDF2F7", fg="#718096")
            lbl.pack(pady=2)
            return

        contenedor = tk.Frame(self.frame_favoritos, bg="#EDF2F7")
        contenedor.pack(fill=tk.X)

        colores = ["#ED8936", "#DD6B20", "#319795", "#805AD5", "#D53F8C", "#3182CE", "#4299E1", "#38A169"]

        # Mostrar hasta los primeros 8 favoritos
        for idx, fav in enumerate(favoritos[:8]):
            color = colores[idx % len(colores)]
            texto_btn = "{}\n${:.2f}".format(fav['nombre'][:15], fav['precio_venta'])
            btn = tk.Button(contenedor, text=texto_btn, font=("Arial", 9, "bold"), bg=color, fg="white",
                            width=14, height=2, relief=tk.RAISED, cursor="hand2",
                            command=lambda p=fav: self.agregar_producto_directo(p, 1))
            btn.pack(side=tk.LEFT, padx=3, pady=2)

    def procesar_busqueda(self):
        texto = self.var_busqueda.get().strip()
        if not texto:
            self.entry_busqueda.focus_set()
            return

        cant = interpretar_cantidad(self.var_cantidad.get().strip(), 1.0)
        if cant is None or cant <= 0:
            cant = 1.0
            self.var_cantidad.set("1")

        # 1. Intentar buscar por código exacto
        prod = database.buscar_producto_por_codigo(texto)
        if prod:
            self.agregar_producto_directo(prod, cant)
            self.var_busqueda.set("")
            self.var_cantidad.set("1")
            self.entry_busqueda.focus_set()
            return

        # 2. Si no es código exacto, buscar por coincidencia en nombre o código
        coincidencias = database.obtener_todos_los_productos(solo_activos=True, filtro=texto)
        if len(coincidencias) == 1:
            self.agregar_producto_directo(coincidencias[0], cant)
            self.var_busqueda.set("")
            self.var_cantidad.set("1")
            self.entry_busqueda.focus_set()
        elif len(coincidencias) > 1:
            DialogoBuscarProducto(self, texto, lambda id_p: self.agregar_por_id(id_p, cant))
            self.var_busqueda.set("")
            self.var_cantidad.set("1")
        else:
            resp = messagebox.askyesno(
                "Dulce no catalogado",
                "No se encontró ningún dulce con el código o nombre '{}'.\n\n"
                "¿Desea agregarlo como artículo no catalogado para esta venta?".format(texto),
                parent=self
            )
            if resp:
                self.abrir_dialogo_no_catalogado(nombre_inicial=texto, cantidad_inicial=cant)
            else:
                self.entry_busqueda.focus_set()

    def abrir_dialogo_no_catalogado(self, nombre_inicial="", cantidad_inicial=None):
        if cantidad_inicial is None:
            cant_actual = self.var_cantidad.get().strip()
            cantidad_inicial = cant_actual if cant_actual else ".500"
        if not nombre_inicial:
            nombre_inicial = self.var_busqueda.get().strip()
        DialogoArticuloNoCatalogado(self, self.agregar_articulo_no_catalogado, nombre_inicial, cantidad_inicial)

    def agregar_articulo_no_catalogado(self, nombre, precio, cantidad, costo=0.0):
        cant = float(cantidad)
        prec = float(precio)
        sub = round(cant * prec, 2)

        # Si ya existe exactamente el mismo artículo no catalogado al mismo precio, acumular cantidad
        encontrado = False
        for item in self.carrito:
            if item.get('id') is None and item['nombre'].strip().lower() == nombre.strip().lower() and abs(item['precio'] - prec) < 0.001:
                item['cantidad'] += cant
                item['subtotal'] = round(item['cantidad'] * item['precio'], 2)
                encontrado = True
                break

        if not encontrado:
            self.carrito.append({
                'id': None,
                'codigo': 'MANUAL',
                'nombre': nombre.strip(),
                'precio': prec,
                'costo': float(costo),
                'cantidad': cant,
                'subtotal': sub
            })

        self.actualizar_vista_carrito()
        self.var_busqueda.set("")
        self.var_cantidad.set("1")
        self.entry_busqueda.focus_set()

    def modificar_cantidad_seleccionado(self):
        sel = self.tree_carrito.selection()
        if not sel:
            messagebox.showinfo("Seleccionar", "Por favor seleccione un dulce del carrito para modificar su cantidad o peso.", parent=self)
            return
        idx = int(sel[0])
        item = self.carrito[idx]

        def callback_actualizar(nueva_cant):
            self.carrito[idx]['cantidad'] = float(nueva_cant)
            self.carrito[idx]['subtotal'] = round(float(nueva_cant) * self.carrito[idx]['precio'], 2)
            self.actualizar_vista_carrito()
            self.tree_carrito.selection_set(str(idx))

        DialogoModificarCantidad(self, item, callback_actualizar)

    def abrir_buscador(self):
        DialogoBuscarProducto(self, "", lambda id_p: self.agregar_por_id(id_p, 1))

    def agregar_por_id(self, id_prod, cantidad=1):
        prods = database.obtener_todos_los_productos(solo_activos=True)
        for p in prods:
            if p['id'] == id_prod:
                self.agregar_producto_directo(p, cantidad)
                break
        self.entry_busqueda.focus_set()

    def agregar_producto_directo(self, prod, cantidad=1):
        # Verificar si el producto ya está en el carrito para solo sumar la cantidad
        encontrado = False
        for item in self.carrito:
            if item['id'] == prod['id']:
                item['cantidad'] += cantidad
                item['subtotal'] = round(item['cantidad'] * item['precio'], 2)
                encontrado = True
                break

        if not encontrado:
            sub = round(cantidad * prod['precio_venta'], 2)
            self.carrito.append({
                'id': prod['id'],
                'codigo': prod['codigo'],
                'nombre': prod['nombre'],
                'precio': prod['precio_venta'],
                'costo': prod['precio_costo'],
                'cantidad': cantidad,
                'subtotal': sub
            })

        self.actualizar_vista_carrito()

    def actualizar_vista_carrito(self):
        for row in self.tree_carrito.get_children():
            self.tree_carrito.delete(row)

        total_venta = 0.0
        total_piezas = 0.0

        for idx, item in enumerate(self.carrito, start=1):
            total_venta += item['subtotal']
            total_piezas += item['cantidad']

            str_cant = formatear_cantidad(item['cantidad'])
            self.tree_carrito.insert("", "end", iid=str(idx-1), values=(
                idx,
                item.get('codigo') or 'MANUAL',
                item['nombre'],
                "${:.2f}".format(item['precio']),
                str_cant,
                "${:.2f}".format(item['subtotal'])
            ))

        self.lbl_gran_total.config(text="${:.2f}".format(total_venta))
        str_art = formatear_cantidad(total_piezas)
        self.lbl_cant_articulos.config(text="{} artículo(s)".format(str_art))

    def sumar_uno_seleccionado(self):
        sel = self.tree_carrito.selection()
        if not sel:
            return
        idx = int(sel[0])
        self.carrito[idx]['cantidad'] += 1
        self.carrito[idx]['subtotal'] = round(self.carrito[idx]['cantidad'] * self.carrito[idx]['precio'], 2)
        self.actualizar_vista_carrito()
        self.tree_carrito.selection_set(str(idx))

    def restar_uno_seleccionado(self):
        sel = self.tree_carrito.selection()
        if not sel:
            return
        idx = int(sel[0])
        if self.carrito[idx]['cantidad'] > 1:
            self.carrito[idx]['cantidad'] -= 1
            self.carrito[idx]['subtotal'] = round(self.carrito[idx]['cantidad'] * self.carrito[idx]['precio'], 2)
        else:
            del self.carrito[idx]
        self.actualizar_vista_carrito()

    def quitar_renglon(self):
        sel = self.tree_carrito.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.carrito[idx]
        self.actualizar_vista_carrito()

    def limpiar_carrito(self):
        if not self.carrito:
            return
        if messagebox.askyesno("Confirmar", "¿Desea cancelar la venta actual y vaciar el carrito?", parent=self):
            self.carrito = []
            self.actualizar_vista_carrito()
            self.entry_busqueda.focus_set()

    def iniciar_cobro(self):
        if not self.carrito:
            messagebox.showinfo("Carrito Vacío", "No hay ningún dulce en el carrito para cobrar.", parent=self)
            self.entry_busqueda.focus_set()
            return

        # Verificar si hay un turno de caja abierto
        turno = database.obtener_turno_actual()
        if not turno:
            # Preguntar si desea abrir turno automáticamente con fondo inicial
            resp = messagebox.askyesno("Caja Cerrada", "No hay un turno de caja abierto.\n¿Desea abrir la caja ahora para comenzar a vender?", parent=self)
            if resp:
                self.app.abrir_pestana_caja()
            return

        total = sum(item['subtotal'] for item in self.carrito)

        DialogoCobro(self, total, self.carrito, turno['id'], self.al_terminar_venta)

    def al_terminar_venta(self):
        self.carrito = []
        self.actualizar_vista_carrito()
        self.var_busqueda.set("")
        self.var_cantidad.set("1")
        self.entry_busqueda.focus_set()
        # Notificar a la app principal para actualizar estados si es necesario
        self.app.actualizar_barra_estado()

    def abrir_cajon_manual(self):
        """Dispara manualmente la apertura del cajón monedero."""
        cfg = database.obtener_configuracion()
        exito, msg = ticket.abrir_cajon(cfg.get('impresora', ''))
        if not exito:
            messagebox.showwarning(
                "Aviso de Cajón",
                "No se pudo abrir el cajón de dinero:\n\n{}\n\n"
                "Verifique que la impresora esté encendida, con cable USB/serial conectado\n"
                "y el cable RJ11 del cajón conectado a la impresora.".format(msg),
                parent=self
            )
