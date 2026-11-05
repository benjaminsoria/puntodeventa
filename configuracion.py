# -*- coding: utf-8 -*-
"""
Módulo de Configuración de la Tienda y Copias de Seguridad (Respaldos a USB).
Vital para computadoras sin internet: permite guardar la base de datos en una memoria USB con un clic.
Compatible con Python 3.4+ y Windows XP.
"""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    pass

import os
import datetime
import database

class FrameConfiguracion(tk.Frame):
    """Pantalla de datos de la tienda y copias de seguridad a USB."""

    def __init__(self, parent, app_principal):
        super(FrameConfiguracion, self).__init__(parent, bg="#F7FAFC")
        self.app = app_principal

        self.crear_interfaz()
        self.cargar_configuracion()
        self.listar_respaldos_locales()

    def crear_interfaz(self):
        frame_cuerpo = tk.Frame(self, bg="#F7FAFC", padx=15, pady=15)
        frame_cuerpo.pack(fill=tk.BOTH, expand=True)

        # Columna Izquierda: Datos del Negocio
        frame_izq = tk.LabelFrame(frame_cuerpo, text=" Datos de la Dulcería (Aparecen en el Ticket) ", font=("Arial", 11, "bold"), bg="#F7FAFC", fg="#2D3748", padx=15, pady=15)
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(frame_izq, text="Nombre de la Dulcería:", font=("Arial", 10, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(5, 2))
        self.var_nombre = tk.StringVar()
        entry_nom = tk.Entry(frame_izq, textvariable=self.var_nombre, font=("Arial", 11), width=35)
        entry_nom.pack(fill=tk.X, pady=(0, 10))

        tk.Label(frame_izq, text="Teléfono:", font=("Arial", 10, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(5, 2))
        self.var_telefono = tk.StringVar()
        entry_tel = tk.Entry(frame_izq, textvariable=self.var_telefono, font=("Arial", 11), width=35)
        entry_tel.pack(fill=tk.X, pady=(0, 10))

        tk.Label(frame_izq, text="Dirección:", font=("Arial", 10, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(5, 2))
        self.var_direccion = tk.StringVar()
        entry_dir = tk.Entry(frame_izq, textvariable=self.var_direccion, font=("Arial", 11), width=35)
        entry_dir.pack(fill=tk.X, pady=(0, 10))

        tk.Label(frame_izq, text="Mensaje al final del ticket:", font=("Arial", 10, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(5, 2))
        self.var_mensaje = tk.StringVar()
        entry_msg = tk.Entry(frame_izq, textvariable=self.var_mensaje, font=("Arial", 11), width=35)
        entry_msg.pack(fill=tk.X, pady=(0, 15))

        btn_guardar_datos = tk.Button(frame_izq, text="💾 Guardar Cambios de la Tienda", font=("Arial", 11, "bold"), bg="#38A169", fg="white", pady=8,
                                      command=self.guardar_datos)
        btn_guardar_datos.pack(fill=tk.X)

        # Columna Derecha: Respaldos a Memoria USB
        frame_der = tk.LabelFrame(frame_cuerpo, text=" Copias de Seguridad (Memoria USB) ", font=("Arial", 11, "bold"), bg="#F7FAFC", fg="#2D3748", padx=15, pady=15)
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(frame_der, text="¡Proteja la información de su negocio!\nAl no tener internet, es muy importante copiar periódicamente los datos a una memoria USB (Pendrive).",
                 font=("Arial", 9), bg="#F7FAFC", fg="#4A5568", justify="left").pack(anchor="w", pady=(0, 10))

        btn_respaldo_usb = tk.Button(frame_der, text="💾 COPIAR RESPALDO A MEMORIA USB", font=("Arial", 12, "bold"), bg="#3182CE", fg="white", pady=10,
                                     command=self.hacer_respaldo_usb)
        btn_respaldo_usb.pack(fill=tk.X, pady=(0, 10))

        btn_respaldo_local = tk.Button(frame_der, text="Guardar Respaldo Local Rápido", font=("Arial", 10), bg="#E2E8F0", pady=6,
                                       command=self.hacer_respaldo_local)
        btn_respaldo_local.pack(fill=tk.X, pady=(0, 15))

        # Lista de Respaldos Locales Recientes
        tk.Label(frame_der, text="Respaldos guardados en esta computadora:", font=("Arial", 10, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(5, 2))

        cols = ("archivo", "tamano")
        self.tree_respaldos = ttk.Treeview(frame_der, columns=cols, show="headings", height=5)
        self.tree_respaldos.heading("archivo", text="Archivo de Respaldo")
        self.tree_respaldos.heading("tamano", text="Tamaño")
        self.tree_respaldos.column("archivo", width=220)
        self.tree_respaldos.column("tamano", width=80, anchor="e")
        self.tree_respaldos.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        btn_restaurar = tk.Button(frame_der, text="🔄 Restaurar Sistema desde una Copia", font=("Arial", 10, "bold"), bg="#FED7D7", fg="#9B2C2C", pady=6,
                                  command=self.restaurar_copia)
        btn_restaurar.pack(fill=tk.X)

    def cargar_configuracion(self):
        cfg = database.obtener_configuracion()
        self.var_nombre.set(cfg.get('nombre_tienda', ''))
        self.var_telefono.set(cfg.get('telefono', ''))
        self.var_direccion.set(cfg.get('direccion', ''))
        self.var_mensaje.set(cfg.get('mensaje_ticket', ''))

    def guardar_datos(self):
        nom = self.var_nombre.get().strip()
        tel = self.var_telefono.get().strip()
        direccion = self.var_direccion.get().strip()
        msg = self.var_mensaje.get().strip()

        if not nom:
            messagebox.showwarning("Atención", "El nombre de la tienda no puede estar vacío.", parent=self)
            return

        database.guardar_configuracion(nom, tel, direccion, msg)
        messagebox.showinfo("Guardado", "Los datos de la tienda han sido actualizados.", parent=self)
        self.app.actualizar_titulo_tienda()

    def hacer_respaldo_usb(self):
        carpeta_seleccionada = filedialog.askdirectory(title="Seleccione su Memoria USB o Carpeta de Respaldo", parent=self)
        if not carpeta_seleccionada:
            return

        exito, resultado = database.crear_respaldo(directorio_destino=carpeta_seleccionada)
        if exito:
            nombre = os.path.basename(resultado)
            messagebox.showinfo("¡Respaldo Exitoso!",
                                "Se ha guardado una copia completa de la base de datos en su memoria USB:\n\n{}".format(nombre),
                                parent=self)
        else:
            messagebox.showerror("Error al Respaldar", resultado, parent=self)

    def hacer_respaldo_local(self):
        exito, resultado = database.crear_respaldo()
        if exito:
            messagebox.showinfo("Respaldo Guardado", "Se creó un respaldo local con éxito.", parent=self)
            self.listar_respaldos_locales()
        else:
            messagebox.showerror("Error", resultado, parent=self)

    def listar_respaldos_locales(self):
        for item in self.tree_respaldos.get_children():
            self.tree_respaldos.delete(item)

        directorio_base = os.path.dirname(os.path.abspath(__file__))
        carpeta_respaldos = os.path.join(directorio_base, "respaldos")

        if os.path.exists(carpeta_respaldos):
            archivos = [f for f in os.listdir(carpeta_respaldos) if f.endswith(".db")]
            archivos.sort(reverse=True)
            for arch in archivos[:8]:
                ruta_completa = os.path.join(carpeta_respaldos, arch)
                tamano_kb = os.path.getsize(ruta_completa) / 1024.0
                self.tree_respaldos.insert("", "end", values=(arch, "{:.1f} KB".format(tamano_kb)))

    def restaurar_copia(self):
        archivo_sel = filedialog.askopenfilename(
            title="Seleccionar archivo de respaldo (.db)",
            filetypes=[("Base de Datos SQLite", "*.db"), ("Todos los archivos", "*.*")],
            parent=self
        )
        if not archivo_sel:
            return

        if messagebox.askyesno("Confirmar Restauración",
                               "¿Está absolutamente seguro de restaurar este respaldo?\nSe reemplazará la información actual por la del archivo seleccionado.\n(Se guardará un respaldo previo de seguridad automáticamente)",
                               parent=self):
            exito, msg = database.restaurar_respaldo(archivo_sel)
            if exito:
                messagebox.showinfo("Restauración Completa", "La base de datos se ha restaurado correctamente.\nPor favor reinicie el sistema.", parent=self)
                # Recargar vistas
                if hasattr(self.app, 'pantalla_inventario'):
                    self.app.pantalla_inventario.cargar_datos()
                if hasattr(self.app, 'pantalla_caja'):
                    self.app.pantalla_caja.recargar()
                if hasattr(self.app, 'pantalla_reportes'):
                    self.app.pantalla_reportes.cargar_ventas()
            else:
                messagebox.showerror("Error al restaurar", msg, parent=self)
