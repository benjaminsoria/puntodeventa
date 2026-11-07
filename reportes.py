# -*- coding: utf-8 -*-
"""
Módulo de Historial de Ventas, Reportes y Cancelaciones.
Permite consultar ventas pasadas, ver qué dulces se vendieron y cancelar ventas por equivocación reponiendo el stock.
Compatible con Python 3.4+ y Windows XP.
"""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    pass

import datetime
import database
import ticket

class FrameReportes(tk.Frame):
    """Pantalla de historial de ventas y reportes."""

    def __init__(self, parent, app_principal):
        super(FrameReportes, self).__init__(parent, bg="#F7FAFC")
        self.app = app_principal

        self.crear_interfaz()
        self.cargar_ventas()

    def crear_interfaz(self):
        # Barra Superior de Filtros
        frame_filtros = tk.Frame(self, bg="#EDF2F7", padx=12, pady=10, relief=tk.RIDGE, bd=1)
        frame_filtros.pack(fill=tk.X, padx=10, pady=(10, 5))

        tk.Label(frame_filtros, text="Filtrar por Fecha:", font=("Arial", 11, "bold"), bg="#EDF2F7", fg="#2D3748").pack(side=tk.LEFT, padx=(0, 5))

        hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        self.var_fecha = tk.StringVar(value=hoy)
        self.entry_fecha = tk.Entry(frame_filtros, textvariable=self.var_fecha, font=("Arial", 11), width=12, justify="center")
        self.entry_fecha.pack(side=tk.LEFT, padx=5)

        btn_hoy = tk.Button(frame_filtros, text="Hoy", font=("Arial", 9), bg="#E2E8F0", command=self.filtrar_hoy)
        btn_hoy.pack(side=tk.LEFT, padx=3)

        btn_todas = tk.Button(frame_filtros, text="Ver Todas", font=("Arial", 9), bg="#E2E8F0", command=self.filtrar_todas)
        btn_todas.pack(side=tk.LEFT, padx=3)

        btn_buscar = tk.Button(frame_filtros, text="Aplicar Filtro", font=("Arial", 10, "bold"), bg="#3182CE", fg="white",
                               command=self.cargar_ventas)
        btn_buscar.pack(side=tk.LEFT, padx=8)

        # Totales del filtro
        self.lbl_resumen_filtro = tk.Label(frame_filtros, text="Ventas: 0 | Total: $0.00", font=("Arial", 11, "bold"), fg="#276749", bg="#EDF2F7")
        self.lbl_resumen_filtro.pack(side=tk.RIGHT, padx=10)

        # Marco Central: Tabla de Ventas (izquierda) y Detalle de la Venta (derecha)
        frame_cuerpo = tk.Frame(self, bg="#F7FAFC")
        frame_cuerpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Panel Izquierdo: Lista de Ventas
        frame_ventas = tk.LabelFrame(frame_cuerpo, text=" Ventas Realizadas (Seleccione una para ver su detalle) ", font=("Arial", 10, "bold"), bg="#F7FAFC", fg="#2D3748", padx=5, pady=5)
        frame_ventas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        cols = ("folio", "fecha", "total", "pago", "cambio", "estado")
        self.tree_ventas = ttk.Treeview(frame_ventas, columns=cols, show="headings", height=14)
        self.tree_ventas.heading("folio", text="Folio")
        self.tree_ventas.heading("fecha", text="Fecha y Hora")
        self.tree_ventas.heading("total", text="Total")
        self.tree_ventas.heading("pago", text="Pago Con")
        self.tree_ventas.heading("cambio", text="Cambio")
        self.tree_ventas.heading("estado", text="Estado")

        self.tree_ventas.column("folio", width=80, anchor="center")
        self.tree_ventas.column("fecha", width=140, anchor="center")
        self.tree_ventas.column("total", width=80, anchor="e")
        self.tree_ventas.column("pago", width=75, anchor="e")
        self.tree_ventas.column("cambio", width=75, anchor="e")
        self.tree_ventas.column("estado", width=100, anchor="center")

        scroll_v = ttk.Scrollbar(frame_ventas, orient="vertical", command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=scroll_v.set)

        self.tree_ventas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_v.pack(side=tk.LEFT, fill=tk.Y)

        self.tree_ventas.tag_configure("cancelada", background="#FED7D7", foreground="#9B2C2C")
        self.tree_ventas.bind("<<TreeviewSelect>>", self.al_seleccionar_venta)

        # Panel Derecho: Detalle de Artículos Vendidos
        frame_detalle = tk.LabelFrame(frame_cuerpo, text=" Dulces Comprados en este Ticket ", font=("Arial", 10, "bold"), bg="#F7FAFC", fg="#2D3748", padx=5, pady=5, width=320)
        frame_detalle.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        frame_detalle.pack_propagate(False)

        cols_det = ("cant", "nombre", "precio", "subtotal")
        self.tree_detalle = ttk.Treeview(frame_detalle, columns=cols_det, show="headings", height=10)
        self.tree_detalle.heading("cant", text="Cant")
        self.tree_detalle.heading("nombre", text="Dulce")
        self.tree_detalle.heading("precio", text="P.U.")
        self.tree_detalle.heading("subtotal", text="Subtotal")

        self.tree_detalle.column("cant", width=45, anchor="center")
        self.tree_detalle.column("nombre", width=140)
        self.tree_detalle.column("precio", width=55, anchor="e")
        self.tree_detalle.column("subtotal", width=65, anchor="e")

        scroll_d = ttk.Scrollbar(frame_detalle, orient="vertical", command=self.tree_detalle.yview)
        self.tree_detalle.configure(yscrollcommand=scroll_d.set)

        self.tree_detalle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_d.pack(side=tk.LEFT, fill=tk.Y)

        # Barra Inferior de Acciones
        frame_acciones = tk.Frame(self, bg="#EDF2F7", padx=10, pady=8, relief=tk.RIDGE, bd=1)
        frame_acciones.pack(fill=tk.X, padx=10, pady=(5, 10))

        btn_reimprimir = tk.Button(frame_acciones, text="Reimprimir Ticket",
                                   font=("Arial", 10, "bold"), bg="#3182CE", fg="white", padx=12, pady=4,
                                   command=self.reimprimir_ticket_seleccionado)
        btn_reimprimir.pack(side=tk.LEFT, padx=5)

        btn_cancelar_venta = tk.Button(frame_acciones, text="Cancelar Venta Seleccionada",
                                       font=("Arial", 10, "bold"), bg="#FED7D7", fg="#9B2C2C", padx=10, pady=4,
                                       command=self.cancelar_venta_seleccionada)
        btn_cancelar_venta.pack(side=tk.LEFT, padx=5)

        btn_refrescar = tk.Button(frame_acciones, text="Actualizar", font=("Arial", 10), bg="#E2E8F0", padx=10, pady=4,
                                  command=self.cargar_ventas)
        btn_refrescar.pack(side=tk.RIGHT, padx=5)

    def filtrar_hoy(self):
        hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        self.var_fecha.set(hoy)
        self.cargar_ventas()

    def filtrar_todas(self):
        self.var_fecha.set("")
        self.cargar_ventas()

    def cargar_ventas(self):
        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)

        for item in self.tree_detalle.get_children():
            self.tree_detalle.delete(item)

        fecha = self.var_fecha.get().strip() or None
        ventas = database.obtener_historial_ventas(fecha_filtro=fecha)

        suma_total = 0.0
        conteo_activas = 0

        for v in ventas:
            etiqueta = "cancelada" if v['estado'] == 'CANCELADA' else ""
            if v['estado'] == 'COMPLETADA':
                suma_total += v['total']
                conteo_activas += 1

            self.tree_ventas.insert("", "end", iid=str(v['id']), tags=(etiqueta,), values=(
                v['folio'],
                v['fecha_hora'],
                "${:.2f}".format(v['total']),
                "${:.2f}".format(v['pago_con']),
                "${:.2f}".format(v['cambio']),
                v['estado']
            ))

        self.lbl_resumen_filtro.config(text="Ventas Activas: {} | Total: ${:.2f}".format(conteo_activas, suma_total))

    def al_seleccionar_venta(self, event):
        sel = self.tree_ventas.selection()
        if not sel:
            return
        id_venta = int(sel[0])

        for item in self.tree_detalle.get_children():
            self.tree_detalle.delete(item)

        detalles = database.obtener_detalle_venta(id_venta)
        for d in detalles:
            str_cant = "{:.0f}".format(d['cantidad']) if float(d['cantidad']).is_integer() else "{:.2f}".format(d['cantidad'])
            self.tree_detalle.insert("", "end", values=(
                str_cant,
                d['nombre_producto'],
                "${:.2f}".format(d['precio_unitario']),
                "${:.2f}".format(d['subtotal'])
            ))

    def cancelar_venta_seleccionada(self):
        sel = self.tree_ventas.selection()
        if not sel:
            messagebox.showinfo("Seleccionar", "Por favor seleccione una venta de la lista para cancelarla.", parent=self)
            return

        id_venta = int(sel[0])

        # Verificar si ya está cancelada
        valores = self.tree_ventas.item(sel[0], "values")
        if valores and valores[5] == 'CANCELADA':
            messagebox.showinfo("Atención", "Esta venta ya se encuentra cancelada.", parent=self)
            return

        if messagebox.askyesno("Confirmar Cancelación",
                               "¿Está seguro de cancelar el ticket {} por ${}?\n\nLos dulces de esta venta serán devueltos automáticamente al inventario.".format(valores[0], valores[2]),
                               parent=self):
            exito, msg = database.cancelar_venta(id_venta, "Cancelación por usuario")
            if exito:
                messagebox.showinfo("Venta Cancelada", "La venta ha sido cancelada y los productos regresaron al stock.", parent=self)
                self.cargar_ventas()
                # Actualizar inventario y caja
                if hasattr(self.app, 'pantalla_inventario'):
                    self.app.pantalla_inventario.cargar_datos()
                if hasattr(self.app, 'pantalla_caja'):
                    self.app.pantalla_caja.recargar()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def reimprimir_ticket_seleccionado(self):
        sel = self.tree_ventas.selection()
        if not sel:
            messagebox.showinfo("Seleccionar", "Por favor seleccione una venta de la lista para reimprimir su ticket.", parent=self)
            return

        id_venta = int(sel[0])
        datos_ticket = database.preparar_datos_ticket_desde_venta(id_venta)
        if not datos_ticket:
            messagebox.showerror("Error", "No se pudieron obtener los datos de la venta seleccionada.", parent=self)
            return

        cfg = database.obtener_configuracion()
        exito, msg = ticket.imprimir_ticket(datos_ticket, cfg, abrir_cajon_tambien=False)
        if exito:
            messagebox.showinfo("Ticket Reimpreso", "El ticket del folio {} fue enviado a la impresora con éxito.".format(datos_ticket.get('folio', '')), parent=self)
        else:
            messagebox.showerror("Error de Impresora", "No se pudo imprimir el ticket:\n\n{}\n\nVerifique que la impresora esté encendida.".format(msg), parent=self)
