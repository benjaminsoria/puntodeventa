# -*- coding: utf-8 -*-
"""
Módulo de Control de Caja, Entradas/Salidas y Corte Diario de Turno.
Permite a los encargados cuadrar el dinero en efectivo, registrar pagos a proveedores y calcular la ganancia.
Compatible con Python 3.4+ y Windows XP.
"""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    pass

import os
import database
import ticket

class DialogoMovimientoCaja(object):
    """Ventana para registrar una entrada o salida de dinero de la caja."""

    def __init__(self, parent, id_turno, tipo, callback_actualizar):
        self.parent = parent
        self.id_turno = id_turno
        self.tipo = tipo # 'ENTRADA' o 'SALIDA'
        self.callback_actualizar = callback_actualizar

        self.top = tk.Toplevel(parent)
        titulo = "Registrar Entrada de Dinero" if tipo == 'ENTRADA' else "Registrar Salida de Dinero (Gasto/Pago)"
        self.top.title(titulo)
        self.top.geometry("450x300")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - 225
        y = (self.top.winfo_screenheight() // 2) - 150
        self.top.geometry("450x300+{}+{}".format(max(0, x), max(0, y)))

        self.crear_interfaz()

    def crear_interfaz(self):
        f = tk.Frame(self.top, padx=20, pady=15, bg="#F7FAFC")
        f.pack(fill=tk.BOTH, expand=True)

        color_tipo = "#276749" if self.tipo == 'ENTRADA' else "#C53030"
        txt_tipo = "ENTRADA DE EFECTIVO (+)" if self.tipo == 'ENTRADA' else "SALIDA DE EFECTIVO (-)"
        tk.Label(f, text=txt_tipo, font=("Arial", 13, "bold"), fg=color_tipo, bg="#F7FAFC").pack(pady=(0, 10))

        # Monto
        f_monto = tk.Frame(f, bg="#F7FAFC")
        f_monto.pack(fill=tk.X, pady=8)

        tk.Label(f_monto, text="Monto $: ", font=("Arial", 12, "bold"), bg="#F7FAFC").pack(side=tk.LEFT)
        self.var_monto = tk.StringVar(value="")
        self.entry_monto = tk.Entry(f_monto, textvariable=self.var_monto, font=("Arial", 16, "bold"), width=12, justify="center")
        self.entry_monto.pack(side=tk.LEFT, padx=10)
        self.entry_monto.focus_set()

        # Motivo / Concepto
        f_motivo = tk.Frame(f, bg="#F7FAFC")
        f_motivo.pack(fill=tk.X, pady=8)

        tk.Label(f_motivo, text="Motivo / Concepto:", font=("Arial", 10, "bold"), bg="#F7FAFC").pack(anchor="w")
        self.var_motivo = tk.StringVar()
        sugerencias = ["Pago a repartidor", "Compra de bolsas", "Cambio / Morralla extra", "Retiro de efectivo", "Gasto de limpieza"]
        self.cb_motivo = ttk.Combobox(f_motivo, textvariable=self.var_motivo, values=sugerencias, font=("Arial", 11), width=35)
        self.cb_motivo.pack(fill=tk.X, pady=4)

        # Botones
        f_btn = tk.Frame(f, bg="#F7FAFC")
        f_btn.pack(fill=tk.X, pady=(15, 0))

        btn_guardar = tk.Button(f_btn, text="Registrar Movimiento (Enter)", font=("Arial", 11, "bold"),
                                bg=("#38A169" if self.tipo == 'ENTRADA' else "#E53E3E"), fg="white", pady=6,
                                command=self.guardar)
        btn_guardar.pack(fill=tk.X, pady=4)

        btn_cancel = tk.Button(f_btn, text="Cancelar (Esc)", font=("Arial", 10), bg="#E2E8F0", command=self.top.destroy)
        btn_cancel.pack(fill=tk.X)

        self.top.bind("<Return>", lambda e: self.guardar())
        self.top.bind("<KP_Enter>", lambda e: self.guardar())
        self.top.bind("<Escape>", lambda e: self.top.destroy())

    def guardar(self):
        try:
            monto = float(self.var_monto.get().strip())
            if monto <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Monto Inválido", "Por favor ingrese un monto mayor a $0.00.", parent=self.top)
            self.entry_monto.focus_set()
            return

        motivo = self.var_motivo.get().strip()
        if not motivo:
            motivo = "Entrada general" if self.tipo == 'ENTRADA' else "Salida general"

        database.registrar_movimiento_caja(self.id_turno, self.tipo, monto, motivo)
        self.top.destroy()
        if self.callback_actualizar:
            self.callback_actualizar()


class DialogoCorteCaja(object):
    """Ventana para confirmar y cerrar el corte de caja."""

    def __init__(self, parent, id_turno, resumen, callback_terminar):
        self.parent = parent
        self.id_turno = id_turno
        self.resumen = resumen
        self.callback_terminar = callback_terminar

        self.top = tk.Toplevel(parent)
        self.top.title("Corte de Caja Diario")
        self.top.geometry("540x580")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - 270
        y = (self.top.winfo_screenheight() // 2) - 290
        self.top.geometry("540x580+{}+{}".format(max(0, x), max(0, y)))

        self.crear_interfaz()

    def crear_interfaz(self):
        f = tk.Frame(self.top, padx=20, pady=15, bg="#F7FAFC")
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="CORTE Y CIERRE DE TURNO", font=("Arial", 14, "bold"), fg="#1A202C", bg="#F7FAFC").pack(pady=(0, 10))

        # Tarjeta con números clave
        f_resumen = tk.Frame(f, bg="#EDF2F7", padx=15, pady=10, relief=tk.RIDGE, bd=1)
        f_resumen.pack(fill=tk.X, pady=5)

        filas = [
            ("(+) Fondo Inicial de Caja:", "${:.2f}".format(self.resumen['monto_inicial'])),
            ("(+) Ventas Totales en Efectivo:", "${:.2f}".format(self.resumen['total_ventas'])),
            ("    Número de tickets cobrados:", "{} ventas".format(self.resumen['num_ventas'])),
            ("(+) Entradas extras de dinero:", "${:.2f}".format(self.resumen['total_entradas'])),
            ("(-) Salidas de dinero (gastos):", "${:.2f}".format(self.resumen['total_salidas'])),
            ("---------------------------------", "-------------"),
            ("TOTAL ESPERADO EN CAJÓN:", "${:.2f}".format(self.resumen['dinero_esperado'])),
            ("Ganancia Estimada de Ventas:", "${:.2f}".format(self.resumen['ganancia_estimada']))
        ]

        for idx, (etiqueta, valor) in enumerate(filas):
            es_negrita = "bold" if "ESPERADO" in etiqueta or "Ganancia" in etiqueta else "normal"
            tamano = 11 if "ESPERADO" in etiqueta else 10
            color = "#276749" if "ESPERADO" in etiqueta else ("#2B6CB0" if "Ganancia" in etiqueta else "#2D3748")

            r = tk.Frame(f_resumen, bg="#EDF2F7")
            r.pack(fill=tk.X, pady=2)
            tk.Label(r, text=etiqueta, font=("Arial", tamano, es_negrita), fg=color, bg="#EDF2F7").pack(side=tk.LEFT)
            tk.Label(r, text=valor, font=("Arial", tamano, es_negrita), fg=color, bg="#EDF2F7").pack(side=tk.RIGHT)

        # Entrada de dinero físico contado
        f_conteo = tk.LabelFrame(f, text=" Conteo de Dinero Físico en el Cajón ", font=("Arial", 10, "bold"), bg="#F7FAFC", fg="#2D3748", padx=10, pady=8)
        f_conteo.pack(fill=tk.X, pady=10)

        f_cont_row = tk.Frame(f_conteo, bg="#F7FAFC")
        f_cont_row.pack()

        tk.Label(f_cont_row, text="Dinero real contado $: ", font=("Arial", 12, "bold"), bg="#F7FAFC").pack(side=tk.LEFT)
        self.var_contado = tk.StringVar(value="{:.2f}".format(self.resumen['dinero_esperado']))
        self.entry_contado = tk.Entry(f_cont_row, textvariable=self.var_contado, font=("Arial", 14, "bold"), width=12, justify="center")
        self.entry_contado.pack(side=tk.LEFT, padx=8)
        self.var_contado.trace("w", self.actualizar_diferencia)

        self.lbl_diferencia = tk.Label(f_conteo, text="Diferencia: $0.00 (Caja Cuadrada)", font=("Arial", 11, "bold"), fg="#276749", bg="#F7FAFC")
        self.lbl_diferencia.pack(pady=4)

        # Observaciones
        tk.Label(f, text="Observaciones / Notas del turno:", font=("Arial", 9, "bold"), bg="#F7FAFC").pack(anchor="w")
        self.var_obs = tk.StringVar()
        entry_obs = tk.Entry(f, textvariable=self.var_obs, font=("Arial", 10), width=45)
        entry_obs.pack(fill=tk.X, pady=(2, 10))

        # Botones
        btn_cerrar = tk.Button(f, text="FINALIZAR CORTE Y CERRAR TURNO", font=("Arial", 12, "bold"), bg="#DD6B20", fg="white", pady=8,
                               command=self.confirmar_cierre)
        btn_cerrar.pack(fill=tk.X, pady=4)

        btn_cancel = tk.Button(f, text="Cancelar", font=("Arial", 10), bg="#E2E8F0", command=self.top.destroy)
        btn_cancel.pack(fill=tk.X)

    def actualizar_diferencia(self, *args):
        try:
            contado = float(self.var_contado.get().strip())
            dif = contado - self.resumen['dinero_esperado']
            if abs(dif) < 0.01:
                self.lbl_diferencia.config(text="Diferencia: $0.00 (¡Caja Perfectamente Cuadrada!)", fg="#276749")
            elif dif > 0:
                self.lbl_diferencia.config(text="Sobrante en caja: + ${:.2f}".format(dif), fg="#2B6CB0")
            else:
                self.lbl_diferencia.config(text="Faltante en caja: - ${:.2f}".format(abs(dif)), fg="#C53030")
        except ValueError:
            self.lbl_diferencia.config(text="Ingrese una cantidad numérica", fg="#718096")

    def confirmar_cierre(self):
        try:
            contado = float(self.var_contado.get().strip())
        except ValueError:
            messagebox.showwarning("Atención", "Por favor ingrese el total de dinero contado.", parent=self.top)
            return

        if not messagebox.askyesno("Confirmar Cierre", "¿Está seguro de cerrar el turno de caja actual?\nSe generará el archivo del corte diario.", parent=self.top):
            return

        obs = self.var_obs.get().strip()
        database.cerrar_turno(self.id_turno, contado, obs)

        # Generar archivo de corte
        cfg = database.obtener_configuracion()
        movs = database.obtener_movimientos_turno(self.id_turno)
        ruta_archivo = ticket.guardar_corte_en_archivo(self.resumen, movs, cfg)

        # Ofrecer impresión de corte en la impresora térmica si está disponible
        impresora = ticket.resolver_nombre_impresora(cfg.get('impresora', ''))
        if impresora:
            if messagebox.askyesno("Imprimir Corte", "¿Desea imprimir el comprobante del corte de caja en la impresora térmica?", parent=self.top):
                ok_imp, msg_imp = ticket.imprimir_corte(self.resumen, movs, cfg)
                if not ok_imp:
                    messagebox.showwarning("Aviso de Impresora", "No se pudo imprimir el comprobante del corte:\n\n{}".format(msg_imp), parent=self.parent)

        self.top.destroy()

        msg = "¡Turno cerrado exitosamente!\n\nEl reporte del corte se guardó en la carpeta 'cortes'."
        if ruta_archivo:
            msg += "\n\nArchivo:\n{}".format(os.path.basename(ruta_archivo))
        messagebox.showinfo("Corte Realizado", msg, parent=self.parent)

        if self.callback_terminar:
            self.callback_terminar()


class FrameCaja(tk.Frame):
    """Pantalla principal de corte de caja y control de turno."""

    def __init__(self, parent, app_principal):
        super(FrameCaja, self).__init__(parent, bg="#F7FAFC")
        self.app = app_principal
        self.crear_interfaz()
        self.recargar()

    def crear_interfaz(self):
        # Marco de Estado del Turno
        self.frame_estado = tk.Frame(self, bg="#EDF2F7", padx=15, pady=12, relief=tk.RIDGE, bd=1)
        self.frame_estado.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.lbl_estado_turno = tk.Label(self.frame_estado, text="ESTADO DE CAJA: CARGANDO...", font=("Arial", 13, "bold"), bg="#EDF2F7", fg="#2D3748")
        self.lbl_estado_turno.pack(side=tk.LEFT)

        self.lbl_info_apertura = tk.Label(self.frame_estado, text="", font=("Arial", 11), bg="#EDF2F7", fg="#4A5568")
        self.lbl_info_apertura.pack(side=tk.RIGHT)

        # Marco Central: Tarjetas de resumen a la izquierda, Movimientos a la derecha
        frame_cuerpo = tk.Frame(self, bg="#F7FAFC")
        frame_cuerpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Columna Izquierda: Tarjetas de Resumen
        frame_izq = tk.Frame(frame_cuerpo, bg="#F7FAFC", width=340)
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # Tarjeta Dinero Esperado
        self.card_dinero = tk.Frame(frame_izq, bg="#2D3748", padx=15, pady=15, relief=tk.RAISED, bd=2)
        self.card_dinero.pack(fill=tk.X, pady=(0, 10))

        tk.Label(self.card_dinero, text="EFECTIVO ESPERADO EN CAJA", font=("Arial", 11, "bold"), fg="#CBD5E0", bg="#2D3748").pack()
        self.lbl_monto_esperado = tk.Label(self.card_dinero, text="$0.00", font=("Arial", 28, "bold"), fg="#48BB78", bg="#2D3748")
        self.lbl_monto_esperado.pack(pady=4)

        # Desglose
        f_detalles = tk.Frame(frame_izq, bg="#EDF2F7", padx=12, pady=12, relief=tk.RIDGE, bd=1)
        f_detalles.pack(fill=tk.X, pady=(0, 10))

        self.lbl_desglose_fondo = self._crear_fila_resumen(f_detalles, "(+) Fondo Inicial:", "$0.00")
        self.lbl_desglose_ventas = self._crear_fila_resumen(f_detalles, "(+) Ventas del turno:", "$0.00")
        self.lbl_desglose_num_ventas = self._crear_fila_resumen(f_detalles, "    Tickets cobrados:", "0")
        self.lbl_desglose_entradas = self._crear_fila_resumen(f_detalles, "(+) Entradas de dinero:", "$0.00")
        self.lbl_desglose_salidas = self._crear_fila_resumen(f_detalles, "(-) Salidas / Pagos:", "$0.00")
        self.lbl_desglose_ganancia = self._crear_fila_resumen(f_detalles, "Ganancia Estimada:", "$0.00", color_val="#2B6CB0", negrita=True)

        # Botones de Acción de Caja
        self.btn_abrir_turno = tk.Button(frame_izq, text="ABRIR NUEVO TURNO DE CAJA", font=("Arial", 12, "bold"), bg="#38A169", fg="white", pady=10,
                                         command=self.abrir_turno_dialogo)

        self.btn_corte = tk.Button(frame_izq, text="REALIZAR CORTE Y CERRAR TURNO", font=("Arial", 12, "bold"), bg="#DD6B20", fg="white", pady=10,
                                   command=self.iniciar_corte)

        self.btn_entrada = tk.Button(frame_izq, text="(+) Entrada de Dinero", font=("Arial", 10, "bold"), bg="#E2E8F0", pady=6,
                                     command=lambda: self.registrar_movimiento('ENTRADA'))

        self.btn_salida = tk.Button(frame_izq, text="(-) Salida de Dinero (Gasto)", font=("Arial", 10, "bold"), bg="#FED7D7", fg="#9B2C2C", pady=6,
                                    command=lambda: self.registrar_movimiento('SALIDA'))

        self.btn_abrir_cajon = tk.Button(frame_izq, text="Abrir Cajón de Dinero (F8)", font=("Arial", 10, "bold"), bg="#4A5568", fg="white", pady=6,
                                         command=self.abrir_cajon_manual)

        # Columna Derecha: Tabla de Movimientos del Turno
        frame_der = tk.LabelFrame(frame_cuerpo, text=" Movimientos del Turno (Entradas y Salidas de Efectivo) ", font=("Arial", 10, "bold"), bg="#F7FAFC", fg="#2D3748", padx=10, pady=5)
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        cols = ("hora", "tipo", "motivo", "monto")
        self.tree_movs = ttk.Treeview(frame_der, columns=cols, show="headings", height=12)
        self.tree_movs.heading("hora", text="Hora")
        self.tree_movs.heading("tipo", text="Tipo")
        self.tree_movs.heading("motivo", text="Motivo / Concepto")
        self.tree_movs.heading("monto", text="Monto")

        self.tree_movs.column("hora", width=90, anchor="center")
        self.tree_movs.column("tipo", width=90, anchor="center")
        self.tree_movs.column("motivo", width=200)
        self.tree_movs.column("monto", width=90, anchor="e")

        scroll = ttk.Scrollbar(frame_der, orient="vertical", command=self.tree_movs.yview)
        self.tree_movs.configure(yscrollcommand=scroll.set)

        self.tree_movs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.LEFT, fill=tk.Y)

    def _crear_fila_resumen(self, parent, titulo, valor_inicial, color_val="#2D3748", negrita=False):
        f = tk.Frame(parent, bg="#EDF2F7")
        f.pack(fill=tk.X, pady=2)
        tk.Label(f, text=titulo, font=("Arial", 10, "bold" if negrita else "normal"), bg="#EDF2F7", fg="#4A5568").pack(side=tk.LEFT)
        lbl_val = tk.Label(f, text=valor_inicial, font=("Arial", 10, "bold" if negrita else "normal"), bg="#EDF2F7", fg=color_val)
        lbl_val.pack(side=tk.RIGHT)
        return lbl_val

    def recargar(self):
        turno = database.obtener_turno_actual()

        # Limpiar movimientos
        for row in self.tree_movs.get_children():
            self.tree_movs.delete(row)

        # Ocultar botones condicionales
        self.btn_abrir_turno.pack_forget()
        self.btn_corte.pack_forget()
        self.btn_entrada.pack_forget()
        self.btn_salida.pack_forget()
        self.btn_abrir_cajon.pack_forget()

        if turno:
            self.lbl_estado_turno.config(text="CAJA ABIERTA (Turno #{})".format(turno['id']), fg="#276749")
            self.lbl_info_apertura.config(text="Abierta desde: {}".format(turno['fecha_inicio']))

            resumen = database.calcular_resumen_caja(turno['id'])
            self.resumen_actual = resumen

            self.lbl_monto_esperado.config(text="${:.2f}".format(resumen['dinero_esperado']))
            self.lbl_desglose_fondo.config(text="${:.2f}".format(resumen['monto_inicial']))
            self.lbl_desglose_ventas.config(text="${:.2f}".format(resumen['total_ventas']))
            self.lbl_desglose_num_ventas.config(text="{} ventas".format(resumen['num_ventas']))
            self.lbl_desglose_entradas.config(text="${:.2f}".format(resumen['total_entradas']))
            self.lbl_desglose_salidas.config(text="${:.2f}".format(resumen['total_salidas']))
            self.lbl_desglose_ganancia.config(text="${:.2f}".format(resumen['ganancia_estimada']))

            # Cargar tabla de movimientos
            movs = database.obtener_movimientos_turno(turno['id'])
            for m in movs:
                hora = m['fecha_hora'].split(" ")[1] if " " in m['fecha_hora'] else m['fecha_hora']
                self.tree_movs.insert("", "end", values=(
                    hora,
                    m['tipo'],
                    m['motivo'],
                    "${:.2f}".format(m['monto'])
                ))

            # Mostrar botones de turno abierto
            self.btn_corte.pack(fill=tk.X, pady=(5, 4))
            self.btn_entrada.pack(fill=tk.X, pady=2)
            self.btn_salida.pack(fill=tk.X, pady=2)
            self.btn_abrir_cajon.pack(fill=tk.X, pady=(8, 2))

        else:
            self.lbl_estado_turno.config(text="CAJA CERRADA (No hay turno activo)", fg="#C53030")
            self.lbl_info_apertura.config(text="Abra un turno para registrar ventas y movimientos")
            self.lbl_monto_esperado.config(text="$0.00")
            self.lbl_desglose_fondo.config(text="$0.00")
            self.lbl_desglose_ventas.config(text="$0.00")
            self.lbl_desglose_num_ventas.config(text="0")
            self.lbl_desglose_entradas.config(text="$0.00")
            self.lbl_desglose_salidas.config(text="$0.00")
            self.lbl_desglose_ganancia.config(text="$0.00")

            self.btn_abrir_turno.pack(fill=tk.X, pady=10)

    def abrir_turno_dialogo(self):
        win_abrir = tk.Toplevel(self)
        win_abrir.title("Apertura de Caja")
        win_abrir.geometry("420x240")
        win_abrir.resizable(False, False)
        win_abrir.transient(self)
        win_abrir.grab_set()

        win_abrir.update_idletasks()
        x = (win_abrir.winfo_screenwidth() // 2) - 210
        y = (win_abrir.winfo_screenheight() // 2) - 120
        win_abrir.geometry("420x240+{}+{}".format(max(0, x), max(0, y)))

        f = tk.Frame(win_abrir, padx=20, pady=15, bg="#F7FAFC")
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="APERTURA DE TURNO DE CAJA", font=("Arial", 13, "bold"), fg="#276749", bg="#F7FAFC").pack()
        tk.Label(f, text="Ingrese el fondo de efectivo inicial (para dar cambio):", font=("Arial", 10), bg="#F7FAFC").pack(pady=5)

        f_in = tk.Frame(f, bg="#F7FAFC")
        f_in.pack(pady=10)

        tk.Label(f_in, text="$", font=("Arial", 16, "bold"), bg="#F7FAFC").pack(side=tk.LEFT)
        var_fondo = tk.StringVar(value="200.00")
        entry_fondo = tk.Entry(f_in, textvariable=var_fondo, font=("Arial", 16, "bold"), width=10, justify="center")
        entry_fondo.pack(side=tk.LEFT, padx=5)
        entry_fondo.focus_set()
        entry_fondo.select_range(0, tk.END)

        def confirmar_apertura():
            try:
                monto = float(var_fondo.get().strip())
                if monto < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showwarning("Atención", "Por favor ingrese una cantidad válida.", parent=win_abrir)
                return

            exito, id_nuevo = database.abrir_turno(monto, "Apertura de turno")
            if exito:
                win_abrir.destroy()
                self.recargar()
                self.app.actualizar_barra_estado()
                messagebox.showinfo("Caja Abierta", "Se abrió la caja correctamente con un fondo de ${:.2f}.".format(monto), parent=self)
            else:
                messagebox.showerror("Error", id_nuevo, parent=win_abrir)

        btn_ok = tk.Button(f, text="Abrir Caja Ahora (Enter)", font=("Arial", 11, "bold"), bg="#38A169", fg="white", pady=6,
                           command=confirmar_apertura)
        btn_ok.pack(fill=tk.X, pady=4)

        btn_cancel = tk.Button(f, text="Cancelar", font=("Arial", 10), command=win_abrir.destroy)
        btn_cancel.pack(fill=tk.X)

        win_abrir.bind("<Return>", lambda e: confirmar_apertura())
        win_abrir.bind("<KP_Enter>", lambda e: confirmar_apertura())
        win_abrir.bind("<Escape>", lambda e: win_abrir.destroy())

    def registrar_movimiento(self, tipo):
        turno = database.obtener_turno_actual()
        if not turno:
            messagebox.showinfo("Caja Cerrada", "Debe abrir un turno primero.", parent=self)
            return
        DialogoMovimientoCaja(self, turno['id'], tipo, self.recargar)

    def iniciar_corte(self):
        turno = database.obtener_turno_actual()
        if not turno:
            return
        resumen = database.calcular_resumen_caja(turno['id'])
        DialogoCorteCaja(self, turno['id'], resumen, self.al_terminar_corte)

    def al_terminar_corte(self):
        self.recargar()
        self.app.actualizar_barra_estado()

    def abrir_cajon_manual(self):
        """Abre el cajón de dinero manualmente."""
        cfg = database.obtener_configuracion()
        exito, msg = ticket.abrir_cajon(cfg.get('impresora', ''))
        if not exito:
            messagebox.showwarning(
                "Aviso de Cajón",
                "No se pudo abrir el cajón de dinero:\n\n{}\n\n"
                "Verifique que la impresora esté encendida y el cable RJ11 conectado.".format(msg),
                parent=self
            )
