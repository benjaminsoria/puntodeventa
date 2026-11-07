# -*- coding: utf-8 -*-
"""
Módulo de Configuración de la Tienda, Impresora, Cajón de Dinero y Copias de Seguridad.
Vital para computadoras sin internet en Windows XP:
- Permite configurar impresora térmica y cajón monedero.
- Pruebas directas de impresión y de apertura de cajón.
- Permite respaldar la base de datos a memoria USB con un clic.
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
import ticket

class FrameConfiguracion(tk.Frame):
    """Pantalla de datos de la tienda, impresora/cajón y copias de seguridad."""

    def __init__(self, parent, app_principal):
        super(FrameConfiguracion, self).__init__(parent, bg="#F7FAFC")
        self.app = app_principal

        self.crear_interfaz()
        self.cargar_configuracion()
        self.listar_respaldos_locales()

    def crear_interfaz(self):
        frame_cuerpo = tk.Frame(self, bg="#F7FAFC", padx=10, pady=10)
        frame_cuerpo.pack(fill=tk.BOTH, expand=True)

        # ----------------------------------------------------
        # Columna 1: Datos del Negocio
        # ----------------------------------------------------
        frame_izq = tk.LabelFrame(frame_cuerpo, text=" 1. Datos de la Tienda (En Ticket) ", font=("Arial", 10, "bold"), bg="#F7FAFC", fg="#2D3748", padx=12, pady=10)
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        tk.Label(frame_izq, text="Nombre del Negocio / Dulcería:", font=("Arial", 9, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(2, 2))
        self.var_nombre = tk.StringVar()
        entry_nom = tk.Entry(frame_izq, textvariable=self.var_nombre, font=("Arial", 10), width=28)
        entry_nom.pack(fill=tk.X, pady=(0, 8))

        tk.Label(frame_izq, text="Teléfono:", font=("Arial", 9, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(2, 2))
        self.var_telefono = tk.StringVar()
        entry_tel = tk.Entry(frame_izq, textvariable=self.var_telefono, font=("Arial", 10), width=28)
        entry_tel.pack(fill=tk.X, pady=(0, 8))

        tk.Label(frame_izq, text="Dirección:", font=("Arial", 9, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(2, 2))
        self.var_direccion = tk.StringVar()
        entry_dir = tk.Entry(frame_izq, textvariable=self.var_direccion, font=("Arial", 10), width=28)
        entry_dir.pack(fill=tk.X, pady=(0, 8))

        tk.Label(frame_izq, text="Mensaje al pie del ticket:", font=("Arial", 9, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(2, 2))
        self.var_mensaje = tk.StringVar()
        entry_msg = tk.Entry(frame_izq, textvariable=self.var_mensaje, font=("Arial", 10), width=28)
        entry_msg.pack(fill=tk.X, pady=(0, 15))

        btn_guardar_datos = tk.Button(frame_izq, text="Guardar Todos los Cambios", font=("Arial", 10, "bold"), bg="#38A169", fg="white", pady=8,
                                      command=self.guardar_datos)
        btn_guardar_datos.pack(fill=tk.X)

        # ----------------------------------------------------
        # Columna 2: Configuración de Impresora y Cajón de Dinero
        # ----------------------------------------------------
        frame_centro = tk.LabelFrame(frame_cuerpo, text=" 2. Impresora y Cajón de Dinero ", font=("Arial", 10, "bold"), bg="#F7FAFC", fg="#2D3748", padx=12, pady=10)
        frame_centro.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        tk.Label(frame_centro, text="Impresora de Tickets:", font=("Arial", 9, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(2, 2))
        self.var_impresora = tk.StringVar()
        self.cb_impresoras = ttk.Combobox(frame_centro, textvariable=self.var_impresora, font=("Arial", 10))
        self.cb_impresoras.pack(fill=tk.X, pady=(0, 4))
        self.refrescar_lista_impresoras()

        btn_buscar_imp = tk.Button(frame_centro, text="Buscar Impresoras Conectadas", font=("Arial", 8), bg="#E2E8F0",
                                   command=self.refrescar_lista_impresoras)
        btn_buscar_imp.pack(anchor="e", pady=(0, 8))

        # Botones de Prueba
        f_pruebas = tk.LabelFrame(frame_centro, text=" Probar Conexión de Hardware ", font=("Arial", 9, "bold"), bg="#F7FAFC", fg="#4A5568", padx=8, pady=8)
        f_pruebas.pack(fill=tk.X, pady=(0, 10))

        btn_test_imp = tk.Button(f_pruebas, text="Probar Impresión de Ticket", font=("Arial", 9, "bold"), bg="#3182CE", fg="white", pady=5,
                                 command=self.probar_impresora)
        btn_test_imp.pack(fill=tk.X, pady=2)

        btn_test_caj = tk.Button(f_pruebas, text="Probar Abrir Cajón", font=("Arial", 9, "bold"), bg="#DD6B20", fg="white", pady=5,
                                 command=self.probar_cajon)
        btn_test_caj.pack(fill=tk.X, pady=2)

        # Opciones automáticas al cobrar
        tk.Label(frame_centro, text="Al confirmar una venta:", font=("Arial", 9, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(4, 2))
        self.var_imp_auto = tk.BooleanVar(value=True)
        chk_imp_auto = tk.Checkbutton(frame_centro, text="Imprimir ticket automáticamente", variable=self.var_imp_auto, font=("Arial", 9), bg="#F7FAFC")
        chk_imp_auto.pack(anchor="w")

        self.var_cajon_auto = tk.BooleanVar(value=True)
        chk_caj_auto = tk.Checkbutton(frame_centro, text="Abrir cajón de dinero automáticamente", variable=self.var_cajon_auto, font=("Arial", 9), bg="#F7FAFC")
        chk_caj_auto.pack(anchor="w")

        self.var_corte_papel = tk.BooleanVar(value=True)
        chk_corte = tk.Checkbutton(frame_centro, text="Cortar papel automáticamente", variable=self.var_corte_papel, font=("Arial", 9), bg="#F7FAFC")
        chk_corte.pack(anchor="w", pady=(0, 8))

        # Ancho de papel
        tk.Label(frame_centro, text="Ancho de Papel:", font=("Arial", 9, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(2, 2))
        f_ancho = tk.Frame(frame_centro, bg="#F7FAFC")
        f_ancho.pack(anchor="w", pady=(0, 10))

        self.var_ancho = tk.StringVar(value="40")
        rb_58 = tk.Radiobutton(f_ancho, text="58 mm (32 car.)", variable=self.var_ancho, value="32", font=("Arial", 9), bg="#F7FAFC")
        rb_58.pack(side=tk.LEFT, padx=(0, 10))
        rb_80 = tk.Radiobutton(f_ancho, text="80 mm (40 car.)", variable=self.var_ancho, value="40", font=("Arial", 9), bg="#F7FAFC")
        rb_80.pack(side=tk.LEFT)

        btn_guardar_imp = tk.Button(frame_centro, text="Guardar Cambios de Impresora", font=("Arial", 10, "bold"), bg="#38A169", fg="white", pady=8,
                                    command=self.guardar_datos)
        btn_guardar_imp.pack(fill=tk.X)

        # ----------------------------------------------------
        # Columna 3: Respaldos a Memoria USB
        # ----------------------------------------------------
        frame_der = tk.LabelFrame(frame_cuerpo, text=" 3. Respaldos (Memoria USB) ", font=("Arial", 10, "bold"), bg="#F7FAFC", fg="#2D3748", padx=12, pady=10)
        frame_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        tk.Label(frame_der, text="¡Proteja sus ventas!\nCopie periódicamente los datos a una memoria USB (Pendrive).",
                 font=("Arial", 8), bg="#F7FAFC", fg="#4A5568", justify="left").pack(anchor="w", pady=(0, 8))

        btn_respaldo_usb = tk.Button(frame_der, text="COPIAR A MEMORIA USB", font=("Arial", 10, "bold"), bg="#3182CE", fg="white", pady=8,
                                     command=self.hacer_respaldo_usb)
        btn_respaldo_usb.pack(fill=tk.X, pady=(0, 6))

        btn_respaldo_local = tk.Button(frame_der, text="Guardar Respaldo Local Rápido", font=("Arial", 9), bg="#E2E8F0", pady=5,
                                       command=self.hacer_respaldo_local)
        btn_respaldo_local.pack(fill=tk.X, pady=(0, 10))

        # Lista de Respaldos
        tk.Label(frame_der, text="Respaldos en esta computadora:", font=("Arial", 9, "bold"), bg="#F7FAFC").pack(anchor="w", pady=(2, 2))

        cols = ("archivo", "tamano")
        self.tree_respaldos = ttk.Treeview(frame_der, columns=cols, show="headings", height=4)
        self.tree_respaldos.heading("archivo", text="Archivo")
        self.tree_respaldos.heading("tamano", text="Tamaño")
        self.tree_respaldos.column("archivo", width=140)
        self.tree_respaldos.column("tamano", width=65, anchor="e")
        self.tree_respaldos.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        btn_restaurar = tk.Button(frame_der, text="Restaurar Base de Datos", font=("Arial", 9, "bold"), bg="#FED7D7", fg="#9B2C2C", pady=5,
                                  command=self.restaurar_copia)
        btn_restaurar.pack(fill=tk.X)

    def refrescar_lista_impresoras(self):
        """Detecta las impresoras instaladas en Windows y llena el combobox."""
        impresoras = ticket.listar_impresoras_instaladas()
        opciones = ["(Predeterminada de Windows)"]
        for p in impresoras:
            if p not in opciones:
                opciones.append(p)
        for puerto in ["LPT1", "COM1", "COM2", "COM3", "Ninguna (Solo archivo)"]:
            if puerto not in opciones:
                opciones.append(puerto)
        self.cb_impresoras['values'] = opciones
        if not self.var_impresora.get():
            self.var_impresora.set("(Predeterminada de Windows)")

    def cargar_configuracion(self):
        cfg = database.obtener_configuracion()
        self.var_nombre.set(cfg.get('nombre_tienda', ''))
        self.var_telefono.set(cfg.get('telefono', ''))
        self.var_direccion.set(cfg.get('direccion', ''))
        self.var_mensaje.set(cfg.get('mensaje_ticket', ''))

        imp = cfg.get('impresora', '')
        if not imp:
            self.var_impresora.set("(Predeterminada de Windows)")
        else:
            self.var_impresora.set(imp)

        self.var_imp_auto.set(bool(int(cfg.get('imprimir_automatico', 1))))
        self.var_cajon_auto.set(bool(int(cfg.get('abrir_cajon_automatico', 1))))
        self.var_corte_papel.set(bool(int(cfg.get('cortar_papel', 1))))
        self.var_ancho.set(str(cfg.get('ancho_ticket', 40)))

    def guardar_datos(self):
        nom = self.var_nombre.get().strip()
        tel = self.var_telefono.get().strip()
        direccion = self.var_direccion.get().strip()
        msg = self.var_mensaje.get().strip()

        if not nom:
            messagebox.showwarning("Atención", "El nombre del negocio no puede estar vacío.", parent=self)
            return

        imp_sel = self.var_impresora.get().strip()
        if "(predeterminada" in imp_sel.lower():
            imp_sel = ""

        try:
            ancho = int(self.var_ancho.get())
        except ValueError:
            ancho = 40

        imp_auto = 1 if self.var_imp_auto.get() else 0
        cajon_auto = 1 if self.var_cajon_auto.get() else 0
        corte_auto = 1 if self.var_corte_papel.get() else 0

        database.guardar_configuracion(
            nom, tel, direccion, msg,
            ancho=ancho,
            impresora=imp_sel,
            imprimir_automatico=imp_auto,
            abrir_cajon_automatico=cajon_auto,
            cortar_papel=corte_auto
        )

        messagebox.showinfo("Guardado", "Los cambios han sido guardados correctamente.", parent=self)
        self.app.actualizar_titulo_tienda()

    def probar_impresora(self):
        imp_sel = self.var_impresora.get().strip()
        if "(predeterminada" in imp_sel.lower():
            imp_sel = ""

        try:
            ancho = int(self.var_ancho.get())
        except ValueError:
            ancho = 40

        exito, msg = ticket.probar_impresion(imp_sel, ancho)
        if exito:
            messagebox.showinfo(
                "Prueba de Impresión",
                "¡Comando de impresión enviado con éxito!\n\n"
                "Verifique que la impresora haya impreso el ticket de prueba.",
                parent=self
            )
        else:
            messagebox.showerror(
                "Error de Impresora",
                "No se pudo imprimir:\n\n{}\n\n"
                "Verifique que la impresora esté encendida, con cable USB conectado\n"
                "y con papel colocado correctamente.".format(msg),
                parent=self
            )

    def probar_cajon(self):
        imp_sel = self.var_impresora.get().strip()
        if "(predeterminada" in imp_sel.lower():
            imp_sel = ""

        exito, msg = ticket.probar_cajon(imp_sel)
        if exito:
            messagebox.showinfo(
                "Prueba de Cajón",
                "¡Pulso enviado al cajón de dinero con éxito!\n\n"
                "Si no abrió, asegúrese de que el cable RJ11 (tipo telefónico)\n"
                "esté conectado en la parte trasera de la impresora de tickets.",
                parent=self
            )
        else:
            messagebox.showerror(
                "Error de Cajón",
                "No se pudo enviar la orden de apertura:\n\n{}\n\n"
                "Verifique que la impresora esté encendida y conectada a la computadora.".format(msg),
                parent=self
            )

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
