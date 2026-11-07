# -*- coding: utf-8 -*-
"""
Módulo de Gestión de Inventario y Catálogo de Productos.
Diseñado para control simple de existencias, alertas de productos por agotarse y entrada rápida de mercancía.
Compatible con Python 3.4+ y Windows XP.
"""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    pass

import database

class DialogoProducto(object):
    """Ventana para agregar o editar un producto de la dulcería."""

    def __init__(self, parent, id_producto=None, callback_actualizar=None):
        self.parent = parent
        self.id_producto = id_producto
        self.callback_actualizar = callback_actualizar

        self.top = tk.Toplevel(parent)
        self.top.title("Editar Dulce" if id_producto else "Nuevo Dulce / Producto")
        self.top.geometry("500x520")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        # Centrar
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - 250
        y = (self.top.winfo_screenheight() // 2) - 260
        self.top.geometry("500x520+{}+{}".format(max(0, x), max(0, y)))

        self.crear_formulario()

        if self.id_producto:
            self.cargar_datos()

    def crear_formulario(self):
        f = tk.Frame(self.top, padx=20, pady=15, bg="#F7FAFC")
        f.pack(fill=tk.BOTH, expand=True)

        titulo = "EDITAR PRODUCTO" if self.id_producto else "REGISTRAR NUEVO PRODUCTO"
        tk.Label(f, text=titulo, font=("Arial", 14, "bold"), bg="#F7FAFC", fg="#2D3748").pack(pady=(0, 15))

        # Campos
        grid_frame = tk.Frame(f, bg="#F7FAFC")
        grid_frame.pack(fill=tk.X)

        # Código de barras / clave
        tk.Label(grid_frame, text="Código / Cód. Barras:", font=("Arial", 10, "bold"), bg="#F7FAFC").grid(row=0, column=0, sticky="w", pady=6)
        self.var_codigo = tk.StringVar()
        self.entry_codigo = tk.Entry(grid_frame, textvariable=self.var_codigo, font=("Arial", 11), width=24)
        self.entry_codigo.grid(row=0, column=1, sticky="w", pady=6)

        # Nombre del dulce
        tk.Label(grid_frame, text="Nombre del Dulce:", font=("Arial", 10, "bold"), bg="#F7FAFC").grid(row=1, column=0, sticky="w", pady=6)
        self.var_nombre = tk.StringVar()
        self.entry_nombre = tk.Entry(grid_frame, textvariable=self.var_nombre, font=("Arial", 11), width=24)
        self.entry_nombre.grid(row=1, column=1, sticky="w", pady=6)

        # Categoría
        tk.Label(grid_frame, text="Categoría:", font=("Arial", 10, "bold"), bg="#F7FAFC").grid(row=2, column=0, sticky="w", pady=6)
        self.var_categoria = tk.StringVar(value="Dulces y Paletas")
        categorias = database.obtener_categorias()
        self.cb_categoria = ttk.Combobox(grid_frame, textvariable=self.var_categoria, values=categorias, font=("Arial", 10), width=22)
        self.cb_categoria.grid(row=2, column=1, sticky="w", pady=6)

        # Precio de Costo (Mayoreo)
        tk.Label(grid_frame, text="Precio Costo (Compra):", font=("Arial", 10, "bold"), bg="#F7FAFC").grid(row=3, column=0, sticky="w", pady=6)
        self.var_costo = tk.StringVar(value="0.00")
        self.entry_costo = tk.Entry(grid_frame, textvariable=self.var_costo, font=("Arial", 11), width=12)
        self.entry_costo.grid(row=3, column=1, sticky="w", pady=6)

        # Precio de Venta (Público)
        tk.Label(grid_frame, text="Precio Venta (Público):", font=("Arial", 10, "bold"), bg="#F7FAFC", fg="#276749").grid(row=4, column=0, sticky="w", pady=6)
        self.var_venta = tk.StringVar(value="0.00")
        self.entry_venta = tk.Entry(grid_frame, textvariable=self.var_venta, font=("Arial", 12, "bold"), width=12)
        self.entry_venta.grid(row=4, column=1, sticky="w", pady=6)

        # Stock actual
        tk.Label(grid_frame, text="Stock Actual (Piezas):", font=("Arial", 10, "bold"), bg="#F7FAFC").grid(row=5, column=0, sticky="w", pady=6)
        self.var_stock = tk.StringVar(value="10")
        self.entry_stock = tk.Entry(grid_frame, textvariable=self.var_stock, font=("Arial", 11), width=12)
        self.entry_stock.grid(row=5, column=1, sticky="w", pady=6)

        # Stock mínimo
        tk.Label(grid_frame, text="Stock Mínimo (Alerta):", font=("Arial", 10, "bold"), bg="#F7FAFC").grid(row=6, column=0, sticky="w", pady=6)
        self.var_stock_min = tk.StringVar(value="5")
        self.entry_stock_min = tk.Entry(grid_frame, textvariable=self.var_stock_min, font=("Arial", 11), width=12)
        self.entry_stock_min.grid(row=6, column=1, sticky="w", pady=6)

        # Unidad de Medida
        tk.Label(grid_frame, text="Unidad de Venta:", font=("Arial", 10, "bold"), bg="#F7FAFC").grid(row=7, column=0, sticky="w", pady=6)
        self.var_unidad = tk.StringVar(value="Pza")
        cb_unidad = ttk.Combobox(grid_frame, textvariable=self.var_unidad, values=["Pza", "Kg", "Paq"], width=10, state="readonly")
        cb_unidad.grid(row=7, column=1, sticky="w", pady=6)

        # Favorito en botonera rápida
        self.var_favorito = tk.IntVar(value=0)
        chk_fav = tk.Checkbutton(f, text="Marcar como Dulce Favorito (Acceso rápido en pantalla de venta)",
                                 variable=self.var_favorito, font=("Arial", 10), bg="#F7FAFC", fg="#2D3748")
        chk_fav.pack(pady=12, anchor="w")

        # Botones
        f_btn = tk.Frame(f, bg="#F7FAFC")
        f_btn.pack(fill=tk.X, pady=(10, 0))

        btn_guardar = tk.Button(f_btn, text="Guardar Producto (Enter)", font=("Arial", 11, "bold"), bg="#38A169", fg="white", pady=6,
                                command=self.guardar)
        btn_guardar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn_cancel = tk.Button(f_btn, text="Cancelar (Esc)", font=("Arial", 11), bg="#E2E8F0", pady=6,
                               command=self.top.destroy)
        btn_cancel.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        self.top.bind("<Return>", lambda e: self.guardar())
        self.top.bind("<KP_Enter>", lambda e: self.guardar())
        self.top.bind("<Escape>", lambda e: self.top.destroy())

        self.entry_codigo.focus_set()

    def cargar_datos(self):
        prods = database.obtener_todos_los_productos(solo_activos=False)
        for p in prods:
            if p['id'] == self.id_producto:
                self.var_codigo.set(p['codigo'])
                self.var_nombre.set(p['nombre'])
                self.var_categoria.set(p['categoria'])
                self.var_costo.set("{:.2f}".format(p['precio_costo']))
                self.var_venta.set("{:.2f}".format(p['precio_venta']))
                self.var_stock.set("{:.0f}".format(p['stock']) if p['stock'].is_integer() else "{:.2f}".format(p['stock']))
                self.var_stock_min.set("{:.0f}".format(p['stock_minimo']) if p['stock_minimo'].is_integer() else "{:.2f}".format(p['stock_minimo']))
                self.var_unidad.set(p['unidad'])
                self.var_favorito.set(p['es_favorito'])
                break

    def guardar(self):
        cod = self.var_codigo.get().strip()
        nom = self.var_nombre.get().strip()
        cat = self.var_categoria.get().strip() or "General"
        uni = self.var_unidad.get().strip() or "Pza"
        fav = self.var_favorito.get()

        if not cod:
            messagebox.showwarning("Falta Código", "Por favor ingrese un código o escanee el código de barras.", parent=self.top)
            self.entry_codigo.focus_set()
            return

        if not nom:
            messagebox.showwarning("Falta Nombre", "Por favor ingrese el nombre del dulce.", parent=self.top)
            self.entry_nombre.focus_set()
            return

        try:
            costo = float(self.var_costo.get().strip())
            venta = float(self.var_venta.get().strip())
            stock = float(self.var_stock.get().strip())
            stock_min = float(self.var_stock_min.get().strip())
        except ValueError:
            messagebox.showerror("Valores Numéricos", "Los precios y existencias deben ser números válidos.", parent=self.top)
            return

        if venta <= 0:
            messagebox.showwarning("Precio de Venta", "El precio de venta debe ser mayor a $0.00.", parent=self.top)
            self.entry_venta.focus_set()
            return

        # Guardar en base de datos
        database.agregar_categoria(cat)

        if self.id_producto:
            exito, msg = database.actualizar_producto(self.id_producto, cod, nom, cat, costo, venta, stock, stock_min, uni, fav)
        else:
            exito, msg = database.agregar_producto(cod, nom, cat, costo, venta, stock, stock_min, uni, fav)

        if exito:
            self.top.destroy()
            if self.callback_actualizar:
                self.callback_actualizar()
        else:
            messagebox.showerror("Error al guardar", str(msg), parent=self.top)


class DialogoEntradaStock(object):
    """Ventana para agregar rápidamente existencias a un producto."""

    def __init__(self, parent, id_producto, nombre_producto, stock_actual, callback_actualizar):
        self.parent = parent
        self.id_producto = id_producto
        self.callback_actualizar = callback_actualizar

        self.top = tk.Toplevel(parent)
        self.top.title("Recepción de Mercancía")
        self.top.geometry("400x260")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - 200
        y = (self.top.winfo_screenheight() // 2) - 130
        self.top.geometry("400x260+{}+{}".format(max(0, x), max(0, y)))

        f = tk.Frame(self.top, padx=20, pady=15, bg="#F7FAFC")
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="ENTRADA RÁPIDA DE DULCES", font=("Arial", 12, "bold"), fg="#2B6CB0", bg="#F7FAFC").pack()
        tk.Label(f, text=nombre_producto, font=("Arial", 11, "bold"), fg="#2D3748", bg="#F7FAFC", wraplength=350).pack(pady=4)

        str_actual = "{:.0f}".format(stock_actual) if stock_actual.is_integer() else "{:.2f}".format(stock_actual)
        tk.Label(f, text="Existencia actual: {} piezas".format(str_actual), font=("Arial", 10), fg="#718096", bg="#F7FAFC").pack(pady=2)

        f_cant = tk.Frame(f, bg="#F7FAFC")
        f_cant.pack(pady=15)

        tk.Label(f_cant, text="¿Cuántas piezas llegaron?:", font=("Arial", 11, "bold"), bg="#F7FAFC").pack(side=tk.LEFT, padx=5)
        self.var_cantidad = tk.StringVar(value="24")
        self.entry_cant = tk.Entry(f_cant, textvariable=self.var_cantidad, font=("Arial", 14, "bold"), width=8, justify="center")
        self.entry_cant.pack(side=tk.LEFT, padx=5)
        self.entry_cant.focus_set()
        self.entry_cant.select_range(0, tk.END)

        btn_ok = tk.Button(f, text="Sumar al Inventario (Enter)", font=("Arial", 12, "bold"), bg="#38A169", fg="white", pady=6,
                           command=self.confirmar)
        btn_ok.pack(fill=tk.X, pady=4)

        btn_cancel = tk.Button(f, text="Cancelar (Esc)", font=("Arial", 10), bg="#E2E8F0", command=self.top.destroy)
        btn_cancel.pack(fill=tk.X)

        self.top.bind("<Return>", lambda e: self.confirmar())
        self.top.bind("<KP_Enter>", lambda e: self.confirmar())
        self.top.bind("<Escape>", lambda e: self.top.destroy())

    def confirmar(self):
        try:
            cant = float(self.var_cantidad.get().strip())
            if cant <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Atención", "Por favor ingrese una cantidad válida mayor a 0.", parent=self.top)
            self.entry_cant.focus_set()
            return

        exito, msg = database.agregar_stock_rapido(self.id_producto, cant)
        if exito:
            self.top.destroy()
            if self.callback_actualizar:
                self.callback_actualizar()
        else:
            messagebox.showerror("Error", msg, parent=self.top)


class FrameInventario(tk.Frame):
    """Pantalla principal de administración del inventario y catálogo."""

    def __init__(self, parent, app_principal):
        super(FrameInventario, self).__init__(parent, bg="#F7FAFC")
        self.app = app_principal

        self.crear_interfaz()
        self.cargar_datos()

    def crear_interfaz(self):
        # Barra superior de filtros
        frame_filtros = tk.Frame(self, bg="#EDF2F7", padx=12, pady=10, relief=tk.RIDGE, bd=1)
        frame_filtros.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(frame_filtros, text="Buscar dulce:", font=("Arial", 11, "bold"), bg="#EDF2F7", fg="#2D3748").pack(side=tk.LEFT, padx=(0, 5))

        self.var_filtro_texto = tk.StringVar()
        entry_filtro = tk.Entry(frame_filtros, textvariable=self.var_filtro_texto, font=("Arial", 11), width=20)
        entry_filtro.pack(side=tk.LEFT, padx=5)
        self.var_filtro_texto.trace("w", lambda *args: self.cargar_datos())

        tk.Label(frame_filtros, text="Categoría:", font=("Arial", 11, "bold"), bg="#EDF2F7", fg="#2D3748").pack(side=tk.LEFT, padx=(15, 5))

        self.var_filtro_cat = tk.StringVar(value="Todas")
        cats = ["Todas"] + database.obtener_categorias()
        self.cb_filtro_cat = ttk.Combobox(frame_filtros, textvariable=self.var_filtro_cat, values=cats, font=("Arial", 10), state="readonly", width=18)
        self.cb_filtro_cat.pack(side=tk.LEFT, padx=5)
        self.cb_filtro_cat.bind("<<ComboboxSelected>>", lambda e: self.cargar_datos())

        self.var_solo_bajos = tk.BooleanVar(value=False)
        chk_bajos = tk.Checkbutton(frame_filtros, text="Ver solo dulces por agotarse", variable=self.var_solo_bajos,
                                   font=("Arial", 10, "bold"), bg="#EDF2F7", fg="#C53030", command=self.cargar_datos)
        chk_bajos.pack(side=tk.LEFT, padx=15)

        btn_limpiar_filtros = tk.Button(frame_filtros, text="Mostrar Todos", font=("Arial", 9), bg="#E2E8F0",
                                        command=self.limpiar_filtros)
        btn_limpiar_filtros.pack(side=tk.LEFT, padx=5)

        # Tabla de Productos
        frame_tabla = tk.Frame(self, bg="#F7FAFC")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("codigo", "nombre", "categoria", "costo", "venta", "ganancia", "stock", "minimo", "favorito")
        self.tree = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=15)

        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre del Dulce")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("costo", text="Costo")
        self.tree.heading("venta", text="P. Venta")
        self.tree.heading("ganancia", text="Ganancia")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("minimo", text="Mínimo")
        self.tree.heading("favorito", text="Favorito")

        self.tree.column("codigo", width=80, anchor="center")
        self.tree.column("nombre", width=240)
        self.tree.column("categoria", width=120)
        self.tree.column("costo", width=75, anchor="e")
        self.tree.column("venta", width=75, anchor="e")
        self.tree.column("ganancia", width=75, anchor="e")
        self.tree.column("stock", width=70, anchor="center")
        self.tree.column("minimo", width=65, anchor="center")
        self.tree.column("favorito", width=65, anchor="center")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.LEFT, fill=tk.Y)

        # Configurar colores para stock bajo
        self.tree.tag_configure("stock_bajo", background="#FED7D7", foreground="#742A2A")
        self.tree.tag_configure("stock_agotado", background="#FEB2B2", foreground="#9B2C2C")

        # Barra de Botones de Acción
        frame_acciones = tk.Frame(self, bg="#EDF2F7", padx=10, pady=8, relief=tk.RIDGE, bd=1)
        frame_acciones.pack(fill=tk.X, padx=10, pady=(5, 10))

        btn_nuevo = tk.Button(frame_acciones, text="+ Nuevo Dulce", font=("Arial", 11, "bold"), bg="#38A169", fg="white", padx=12, pady=4,
                              command=self.nuevo_producto)
        btn_nuevo.pack(side=tk.LEFT, padx=4)

        btn_editar = tk.Button(frame_acciones, text="Modificar Seleccionado", font=("Arial", 10, "bold"), bg="#3182CE", fg="white", padx=10, pady=4,
                               command=self.editar_producto)
        btn_editar.pack(side=tk.LEFT, padx=4)

        btn_entrada = tk.Button(frame_acciones, text="+ Agregar Mercancía (Stock)", font=("Arial", 10, "bold"), bg="#DD6B20", fg="white", padx=10, pady=4,
                                command=self.entrada_mercancia)
        btn_entrada.pack(side=tk.LEFT, padx=8)

        btn_fav = tk.Button(frame_acciones, text="Alternar Favorito", font=("Arial", 10), bg="#E2E8F0", padx=8, pady=4,
                            command=self.alternar_favorito)
        btn_fav.pack(side=tk.LEFT, padx=4)

        btn_eliminar = tk.Button(frame_acciones, text="Eliminar / Desactivar", font=("Arial", 10), bg="#FED7D7", fg="#9B2C2C", padx=8, pady=4,
                                 command=self.eliminar_producto)
        btn_eliminar.pack(side=tk.RIGHT, padx=4)

        self.tree.bind("<Double-1>", lambda e: self.editar_producto())

    def limpiar_filtros(self):
        self.var_filtro_texto.set("")
        self.var_filtro_cat.set("Todas")
        self.var_solo_bajos.set(False)
        self.cargar_datos()

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        texto = self.var_filtro_texto.get().strip()
        cat = self.var_filtro_cat.get()
        bajos = self.var_solo_bajos.get()

        prods = database.obtener_todos_los_productos(solo_activos=True, filtro=texto, categoria=cat, solo_bajos=bajos)

        for p in prods:
            costo = p['precio_costo']
            venta = p['precio_venta']
            ganancia = venta - costo
            stock = p['stock']
            stock_min = p['stock_minimo']

            str_stock = "{:.0f}".format(stock) if stock.is_integer() else "{:.2f}".format(stock)
            str_min = "{:.0f}".format(stock_min) if stock_min.is_integer() else "{:.2f}".format(stock_min)
            str_fav = "Sí" if p['es_favorito'] == 1 else "No"

            etiqueta = ""
            if stock <= 0:
                etiqueta = "stock_agotado"
            elif stock <= stock_min:
                etiqueta = "stock_bajo"

            self.tree.insert("", "end", iid=str(p['id']), tags=(etiqueta,), values=(
                p['codigo'],
                p['nombre'],
                p['categoria'],
                "${:.2f}".format(costo),
                "${:.2f}".format(venta),
                "${:.2f}".format(ganancia),
                str_stock,
                str_min,
                str_fav
            ))

    def nuevo_producto(self):
        DialogoProducto(self, None, self.al_guardar_producto)

    def editar_producto(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Seleccionar", "Por favor seleccione un dulce de la lista para modificarlo.", parent=self)
            return
        id_prod = int(sel[0])
        DialogoProducto(self, id_prod, self.al_guardar_producto)

    def entrada_mercancia(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Seleccionar", "Por favor seleccione un dulce para agregarle existencias.", parent=self)
            return
        id_prod = int(sel[0])
        prods = database.obtener_todos_los_productos(solo_activos=True)
        for p in prods:
            if p['id'] == id_prod:
                DialogoEntradaStock(self, id_prod, p['nombre'], p['stock'], self.al_guardar_producto)
                break

    def alternar_favorito(self):
        sel = self.tree.selection()
        if not sel:
            return
        id_prod = int(sel[0])
        prods = database.obtener_todos_los_productos(solo_activos=True)
        for p in prods:
            if p['id'] == id_prod:
                nuevo_fav = 0 if p['es_favorito'] == 1 else 1
                database.actualizar_producto(id_prod, p['codigo'], p['nombre'], p['categoria'],
                                            p['precio_costo'], p['precio_venta'], p['stock'],
                                            p['stock_minimo'], p['unidad'], nuevo_fav)
                self.al_guardar_producto()
                break

    def eliminar_producto(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Seleccionar", "Por favor seleccione un dulce para eliminarlo.", parent=self)
            return
        id_prod = int(sel[0])
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de eliminar este producto del catálogo?\n(Las ventas pasadas se conservarán en el historial)", parent=self):
            database.eliminar_o_desactivar_producto(id_prod)
            self.al_guardar_producto()

    def al_guardar_producto(self):
        self.cargar_datos()
        # Actualizar favoritos en la pantalla de ventas
        if hasattr(self.app, 'pantalla_ventas'):
            self.app.pantalla_ventas.recargar_favoritos()
