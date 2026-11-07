# -*- coding: utf-8 -*-
"""
Punto de Venta para Dulcería (POS Dulcería).
Diseñado específicamente para funcionar 100% desconectado a internet en Windows XP, 7, 10 y 11.
Construido únicamente con la biblioteca estándar de Python (Tkinter + SQLite3).
"""

import sys
import os
import datetime

# Importación segura de Tkinter
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Error: No se encontró la biblioteca gráfica Tkinter.")
    print("Asegúrese de instalar Python con la opción de 'Tcl/Tk' activada.")
    sys.exit(1)

import database
from ventas import FrameVentas
from inventario import FrameInventario
from caja import FrameCaja
from reportes import FrameReportes
from configuracion import FrameConfiguracion

class AppPuntoDeVenta(tk.Tk):
    """Ventana principal del sistema de Punto de Venta."""

    def __init__(self):
        super(AppPuntoDeVenta, self).__init__()

        # Inicializar base de datos
        database.inicializar_db()

        self.title("Punto de Venta - Dulcería")
        self.geometry("1024x720")
        self.minsize(980, 640)

        # Configurar estilos de la interfaz
        self.configurar_estilos()

        # Construir estructura visual
        self.crear_encabezado()
        self.crear_pestanas()
        self.crear_barra_inferior()

        # Vincular atajos de teclado globales
        self.configurar_atajos()

        # Iniciar reloj y estados
        self.actualizar_reloj()
        self.actualizar_barra_estado()

        # Al abrir, enfocar el campo de búsqueda de ventas
        self.after(300, lambda: self.pantalla_ventas.entry_busqueda.focus_set())

    def configurar_estilos(self):
        style = ttk.Style(self)
        try:
            # En Windows XP usa 'winnative' o 'xpnative', en Linux 'clam' o 'default'
            disponibles = style.theme_names()
            if "xpnative" in disponibles:
                style.theme_use("xpnative")
            elif "winnative" in disponibles:
                style.theme_use("winnative")
            elif "clam" in disponibles:
                style.theme_use("clam")
        except Exception:
            pass

        # Estilo para las pestañas grandes
        style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[16, 8])
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 10), rowheight=26)

    def crear_encabezado(self):
        self.frame_top = tk.Frame(self, bg="#1B365D", height=60, padx=15, pady=8)
        self.frame_top.pack(fill=tk.X)

        # Nombre de la dulcería
        cfg = database.obtener_configuracion()
        self.lbl_nombre_tienda = tk.Label(self.frame_top, text=cfg.get('nombre_tienda', 'DULCERÍA').upper(),
                                          font=("Arial", 16, "bold"), fg="#FFFFFF", bg="#1B365D")
        self.lbl_nombre_tienda.pack(side=tk.LEFT, pady=2)

        # Reloj en vivo a la derecha
        self.lbl_reloj = tk.Label(self.frame_top, text="", font=("Arial", 12, "bold"), fg="#90CDF4", bg="#1B365D")
        self.lbl_reloj.pack(side=tk.RIGHT, padx=10)

        # Indicador de estado de caja
        self.lbl_indicador_caja = tk.Label(self.frame_top, text="", font=("Arial", 11, "bold"), fg="#FFFFFF", bg="#1B365D")
        self.lbl_indicador_caja.pack(side=tk.RIGHT, padx=20)

    def crear_pestanas(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 1. Pantalla de Ventas (F1)
        self.pantalla_ventas = FrameVentas(self.notebook, self)
        self.notebook.add(self.pantalla_ventas, text=" VENTA (F1) ")

        # 2. Pantalla de Inventario (F2)
        self.pantalla_inventario = FrameInventario(self.notebook, self)
        self.notebook.add(self.pantalla_inventario, text=" INVENTARIO (F2) ")

        # 3. Pantalla de Corte de Caja (F3)
        self.pantalla_caja = FrameCaja(self.notebook, self)
        self.notebook.add(self.pantalla_caja, text=" CORTE DE CAJA (F3) ")

        # 4. Pantalla de Reportes e Historial (F4)
        self.pantalla_reportes = FrameReportes(self.notebook, self)
        self.notebook.add(self.pantalla_reportes, text=" HISTORIAL (F4) ")

        # 5. Pantalla de Ajustes y Respaldos (F5)
        self.pantalla_config = FrameConfiguracion(self.notebook, self)
        self.notebook.add(self.pantalla_config, text=" AJUSTES / USB (F5) ")

        # Evento al cambiar de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.al_cambiar_pestana)

    def crear_barra_inferior(self):
        self.frame_bottom = tk.Frame(self, bg="#2D3748", height=28, padx=10, pady=4)
        self.frame_bottom.pack(fill=tk.X, side=tk.BOTTOM)

        lbl_atajos = tk.Label(self.frame_bottom,
                              text="Atajos Rápidos:  [F1] Venta  |  [F2] Inventario  |  [F3] Caja  |  [F4] Historial  |  [F5] Ajustes  |  [F12] Cobrar",
                              font=("Arial", 9, "bold"), fg="#E2E8F0", bg="#2D3748")
        lbl_atajos.pack(side=tk.LEFT)

        lbl_version = tk.Label(self.frame_bottom, text="Sistema Offline | Windows XP Edition", font=("Arial", 9), fg="#A0AEC0", bg="#2D3748")
        lbl_version.pack(side=tk.RIGHT)

    def configurar_atajos(self):
        self.bind("<F1>", lambda e: self.notebook.select(0))
        self.bind("<F2>", lambda e: self.notebook.select(1))
        self.bind("<F3>", lambda e: self.notebook.select(2))
        self.bind("<F4>", lambda e: self.notebook.select(3))
        self.bind("<F5>", lambda e: self.notebook.select(4))
        self.bind("<F12>", lambda e: self.pantalla_ventas.iniciar_cobro())

    def al_cambiar_pestana(self, event):
        idx = self.notebook.index(self.notebook.select())
        if idx == 0:
            # Venta
            self.pantalla_ventas.entry_busqueda.focus_set()
        elif idx == 1:
            # Inventario
            self.pantalla_inventario.cargar_datos()
        elif idx == 2:
            # Caja
            self.pantalla_caja.recargar()
        elif idx == 3:
            # Reportes
            self.pantalla_reportes.cargar_ventas()
        elif idx == 4:
            # Ajustes
            self.pantalla_config.listar_respaldos_locales()

    def actualizar_titulo_tienda(self):
        cfg = database.obtener_configuracion()
        self.lbl_nombre_tienda.config(text=cfg.get('nombre_tienda', 'DULCERÍA').upper())

    def actualizar_reloj(self):
        ahora = datetime.datetime.now().strftime("%d/%m/%Y  %I:%M:%S %p")
        self.lbl_reloj.config(text=ahora)
        self.after(1000, self.actualizar_reloj)

    def actualizar_barra_estado(self):
        turno = database.obtener_turno_actual()
        if turno:
            self.lbl_indicador_caja.config(text="● Caja Abierta (Turno #{})".format(turno['id']), fg="#68D391")
        else:
            self.lbl_indicador_caja.config(text="○ Caja Cerrada", fg="#FEB2B2")

    def abrir_pestana_caja(self):
        self.notebook.select(2)
        self.pantalla_caja.abrir_turno_dialogo()

def main():
    app = AppPuntoDeVenta()
    app.mainloop()

if __name__ == "__main__":
    main()
