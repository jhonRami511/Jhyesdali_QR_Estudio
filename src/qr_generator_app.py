import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from tkinter import ttk
import os
from PIL import Image, ImageTk
import pandas as pd
import qrcode

try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE_FILTER = Image.LANCZOS

class QRGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.minsize(700, 400)  # Ajusta el ancho y alto mínimo según te guste
        self.root.title("Jhyesdali_Qr Estudio")
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.role_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.link_var = tk.StringVar()
        self.format_var = tk.StringVar(value="Completo")
        self.preview_size_var = tk.IntVar(value=230)
        self.error_corr_var = tk.StringVar(value="Q")
        self.box_size_var = tk.IntVar(value=10)
        self.border_var = tk.IntVar(value=4)
        self.qr_color = "#000000"
        self.bg_color = "#FFFFFF"
        self.logo_path = None
        self.tk_image = None
        self.qr_image = None
        self.tema_claro = True
        self.historial = []
        self.idioma = "ES"
        self.qr_auto_mobile = tk.BooleanVar(value=True)
        self.textos = {
            "ES": {
                "title": "Jhyesdali_Qr Estudio - Fácil, rápido y seguro",
                "datos_entrada": "📋 Datos de entrada",
                "id": "ID:",
                "nombre": "Nombre:",
                "cargo": "Cargo:",
                "fecha": "Fecha (opcional):",
                "enlace": "Enlace (opcional):",
                "personalizado": "Contenido personalizado:",
                "formato_qr": "📝 Formato de QR",
                "tipo_qr": "Tipo de QR:",
                "ayuda_completo": "Puedes ingresar todos los datos.",
                "ayuda_basica": "Solo ingreses ID y Nombre.",
                "ayuda_enlace": "Solo el campo 'Enlace' será usado.",
                "ayuda_pers": "Solo el campo 'Contenido personalizado' será incluido.",
                "opciones_qr": "🎨 Opciones QR",
                "errorcorr": "Error corr:",
                "boxsize": "Box size:",
                "border": "Border:",
                "colorqr": "Color QR",
                "colorfondo": "Color Fondo",
                "logo": "Seleccionar logo (opc.)",
                "tam_preview": "Tamaño vista previa (px):",
                "vista_previa": "🔲 Vista previa",
                "copiar": "Copiar datos al portapapeles",
                "acciones": "⚙️ Acciones",
                "vista_prev": "Generar vista previa",
                "guardar_qr": "Guardar QR",
                "csv": "Generar desde CSV/Excel (batch)",
                "imprimir": "Crear hoja para imprimir",
                "tema": "Cambiar tema",
                "historial": "Ver historial",
                "idioma": "Idioma",
                "success": "Éxito",
                "saved": "QR guardado en",
                "error": "Error",
                "csv_success": "QRs generados desde archivo.",
                "copiado": "¡Datos copiados al portapapeles!"
            },
            "EN": {
                "title": "Jhyesdali_Qr Estudio - Easy, fast, and safe",
                "datos_entrada": "📋 Input Data",
                "id": "ID:",
                "nombre": "Name:",
                "cargo": "Role:",
                "fecha": "Date (optional):",
                "enlace": "Link (optional):",
                "personalizado": "Custom content:",
                "formato_qr": "📝 QR Format",
                "tipo_qr": "QR Type:",
                "ayuda_completo": "You can fill all the fields.",
                "ayuda_basica": "Only ID and Name are used.",
                "ayuda_enlace": "Only the 'Link' field will be used.",
                "ayuda_pers": "Only the 'Custom content' field will be used.",
                "opciones_qr": "🎨 QR Options",
                "errorcorr": "Error corr:",
                "boxsize": "Box size:",
                "border": "Border:",
                "colorqr": "QR Color",
                "colorfondo": "Background Color",
                "logo": "Select logo (opt.)",
                "tam_preview": "Preview size (px):",
                "vista_previa": "🔲 Preview",
                "copiar": "Copy data to clipboard",
                "acciones": "⚙️ Actions",
                "vista_prev": "Preview",
                "guardar_qr": "Save QR",
                "csv": "Batch from CSV/Excel",
                "imprimir": "Create print sheet",
                "tema": "Change theme",
                "historial": "Show history",
                "idioma": "Language",
                "success": "Success",
                "saved": "QR saved at",
                "error": "Error",
                "csv_success": "QR codes generated from file.",
                "copiado": "Data copied to clipboard!"
            }
        }
        self.create_widgets()
        self.update_fields_state()
        self.update_preview_content()
        self.root.minsize(700, 400)
        self.root.grid_rowconfigure(0, weight=0)   # Si tienes título o cabecera, sin expansión
        self.root.grid_rowconfigure(1, weight=1)   # SOLO esta fila debe crecer: contiene tus datos
        self.root.grid_rowconfigure(2, weight=0)   # Formato QR
        self.root.grid_rowconfigure(3, weight=0)   # Opciones QR
        self.root.grid_rowconfigure(4, weight=0)   # Acciones abajo

        self.root.grid_columnconfigure(0, weight=3)   # Columna de datos de entrada/preferente
        self.root.grid_columnconfigure(1, weight=1)   # Columna de preview (puedes ajustar el weight)

        self.create_widgets()

    def update_fields_state(self):
        formato = self.format_var.get()
        widgets = [
            (self.id_var_entry, formato in ["Completo", "Tarjeta Básica"]),
            (self.name_var_entry, formato in ["Completo", "Tarjeta Básica"]),
            (self.role_var_entry, formato == "Completo"),
            (self.date_var_entry, formato == "Completo"),
            (self.link_var_entry, formato in ["Completo", "Solo Enlace"]),
            (self.custom_entry, formato in ["Completo", "Personalizado"]),
            (self.entry_boxsize, not self.qr_auto_mobile.get()),
            (self.entry_border, not self.qr_auto_mobile.get()),
        ]
        for widget, enabled in widgets:
            state = tk.NORMAL if enabled else tk.DISABLED
            widget.config(state=state)
            try:
                widget.config(bg="#E4FFE4" if enabled else "#F0F0F0")
            except:
                pass
        self.set_help_text()

    def create_widgets(self):
        # --- Título + Idioma ---
        self.label_titulo = tk.Label(self.root, text=self.textos[self.idioma]["title"], font=("Segoe UI", 13, "bold"), bg="#F5F5F5", fg="#2C3E50")
        self.label_titulo.grid(row=0, column=0, padx=(20,5), pady=8, sticky="w")  # El título alineado a la izquierda

        self.combo_idioma = ttk.Combobox(self.root, values=["Español", "English"], state="readonly", width=12)
        self.combo_idioma.set("Español" if self.idioma == "ES" else "English")
        self.combo_idioma.grid(row=0, column=1, padx=(5,20), pady=8, sticky="e")  # El selector alineado a la derecha
        self.combo_idioma.bind("<<ComboboxSelected>>", lambda e: self.cambiar_idioma(self.combo_idioma.get()))

        # --- Datos de entrada con scroll ---
        self.data_frame_container = tk.LabelFrame(self.root, text=self.textos[self.idioma]["datos_entrada"], font=("Segoe UI", 10, "bold"),
                                                bg="#F5F5F5", fg="#2C3E50")
        self.data_frame_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.data_canvas = tk.Canvas(self.data_frame_container, bg="#F5F5F5", highlightthickness=0)
        self.data_scrollbar = tk.Scrollbar(self.data_frame_container, orient="vertical", command=self.data_canvas.yview)
        self.data_canvas.configure(yscrollcommand=self.data_scrollbar.set)

        self.internal_data_frame = tk.Frame(self.data_canvas, bg="#F5F5F5")
        self.data_canvas.create_window((0, 0), window=self.internal_data_frame, anchor="nw")

        self.data_canvas.pack(side="left", fill="both", expand=True)
        self.data_scrollbar.pack(side="right", fill="y")

        # Actualiza el scrollregion al cambiar contenido
        self.internal_data_frame.bind("<Configure>", lambda e: self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all")))

        # Columnas adentro para expansión horizontal
        self.internal_data_frame.columnconfigure(0, weight=0)
        self.internal_data_frame.columnconfigure(1, weight=1)

        # Labels y Entries colocados adentro del frame interno
        self.label_id = tk.Label(self.internal_data_frame, text=self.textos[self.idioma]["id"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_id.grid(row=0, column=0, sticky="w")
        self.id_var_entry = tk.Entry(self.internal_data_frame, textvariable=self.id_var, font=("Segoe UI", 12))
        self.id_var_entry.grid(row=0, column=1, padx=6, pady=3, sticky="ew")

        self.label_nombre = tk.Label(self.internal_data_frame, text=self.textos[self.idioma]["nombre"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_nombre.grid(row=1, column=0, sticky="w")
        self.name_var_entry = tk.Entry(self.internal_data_frame, textvariable=self.name_var, font=("Segoe UI", 12))
        self.name_var_entry.grid(row=1, column=1, padx=6, pady=3, sticky="ew")

        self.label_cargo = tk.Label(self.internal_data_frame, text=self.textos[self.idioma]["cargo"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_cargo.grid(row=2, column=0, sticky="w")
        self.role_var_entry = tk.Entry(self.internal_data_frame, textvariable=self.role_var, font=("Segoe UI", 12))
        self.role_var_entry.grid(row=2, column=1, padx=6, pady=3, sticky="ew")

        self.label_fecha = tk.Label(self.internal_data_frame, text=self.textos[self.idioma]["fecha"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_fecha.grid(row=3, column=0, sticky="w")
        self.date_var_entry = tk.Entry(self.internal_data_frame, textvariable=self.date_var, font=("Segoe UI", 12))
        self.date_var_entry.grid(row=3, column=1, padx=6, pady=3, sticky="ew")

        self.label_enlace = tk.Label(self.internal_data_frame, text=self.textos[self.idioma]["enlace"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_enlace.grid(row=4, column=0, sticky="w")
        self.link_var_entry = tk.Entry(self.internal_data_frame, textvariable=self.link_var, font=("Segoe UI", 12))
        self.link_var_entry.grid(row=4, column=1, padx=6, pady=3, sticky="ew")

        self.label_personalizado = tk.Label(self.internal_data_frame, text=self.textos[self.idioma]["personalizado"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_personalizado.grid(row=5, column=0, sticky="nw")


        # Campo personalizado con scroll interno propio
        self.custom_frame = tk.Frame(self.internal_data_frame, bg="#F5F5F5")
        self.custom_frame.grid(row=5, column=1, padx=6, pady=6, sticky="nsew")
        self.custom_frame.grid_rowconfigure(0, weight=1)
        self.custom_frame.grid_columnconfigure(0, weight=1)

        self.custom_scroll = tk.Scrollbar(self.custom_frame, orient="vertical")
        self.custom_entry = tk.Text(self.custom_frame, height=4, font=("Segoe UI", 12), wrap="word", yscrollcommand=self.custom_scroll.set)
        self.custom_scroll.config(command=self.custom_entry.yview)

        self.custom_entry.grid(row=0, column=0, sticky="nsew")
        self.custom_scroll.grid(row=0, column=1, sticky="ns")

        self.custom_entry.bind("<KeyRelease>", lambda e: self.change_and_preview())

        # ---- Formato de QR ----
        self.format_frame = tk.LabelFrame(self.root, text=self.textos["ES"]["formato_qr"], font=("Segoe UI", 10, "bold"), bg="#F5F5F5", fg="#2C3E50")
        self.format_frame.grid(row=2, column=0, padx=10, pady=4, sticky="ew")
        self.format_frame.columnconfigure(1, weight=1)
        self.label_tipo_qr = tk.Label(self.format_frame, text=self.textos["ES"]["tipo_qr"], background="#F5F5F5", font=("Segoe UI", 9))
        self.label_tipo_qr.grid(row=0, column=0, sticky="w")
        format_options = ["Completo", "Solo Enlace", "Tarjeta Básica", "Personalizado"]
        self.format_cb = ttk.Combobox(self.format_frame, values=format_options, textvariable=self.format_var, state="readonly", width=18)
        self.format_cb.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self.format_cb.bind("<<ComboboxSelected>>", lambda e: (self.update_fields_state(), self.change_and_preview()))
        self.help_label = tk.Label(self.format_frame, text=self.textos["ES"]["ayuda_completo"], font=("Segoe UI", 9), bg="#F5F5F5", fg="#257A5D", anchor="w")
        self.help_label.grid(row=1, column=0, columnspan=2, sticky="ew")

        # ---- Opciones QR ----
        self.options_frame = tk.LabelFrame(self.root, text=self.textos["ES"]["opciones_qr"], font=("Segoe UI", 10, "bold"), bg="#F5F5F5", fg="#2C3E50")
        self.options_frame.grid(row=3, column=0, padx=10, pady=4, sticky="nsew")
        for i in range(2): self.options_frame.columnconfigure(i, weight=1)
        for i in range(8): self.options_frame.rowconfigure(i, weight=1)
        self.label_errorcorr = tk.Label(self.options_frame, text=self.textos["ES"]["errorcorr"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_errorcorr.grid(row=0, column=0)
        self.entry_errorcorr = tk.Entry(self.options_frame, textvariable=self.error_corr_var, width=5, font=("Segoe UI", 9))
        self.entry_errorcorr.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.label_boxsize = tk.Label(self.options_frame, text=self.textos["ES"]["boxsize"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_boxsize.grid(row=1, column=0)
        self.entry_boxsize = tk.Entry(self.options_frame, textvariable=self.box_size_var, width=5, font=("Segoe UI", 9))
        self.entry_boxsize.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.label_border = tk.Label(self.options_frame, text=self.textos["ES"]["border"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_border.grid(row=2, column=0)
        self.entry_border = tk.Entry(self.options_frame, textvariable=self.border_var, width=5, font=("Segoe UI", 9))
        self.entry_border.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.label_previewsize = tk.Label(self.options_frame, text=self.textos["ES"]["tam_preview"], font=("Segoe UI", 9), bg="#F5F5F5")
        self.label_previewsize.grid(row=5, column=0)
        self.entry_previewsize = tk.Entry(self.options_frame, textvariable=self.preview_size_var, width=5, font=("Segoe UI", 9))
        self.entry_previewsize.grid(row=5, column=1, padx=5, pady=2, sticky="ew")
        self.btn_colorqr = tk.Button(self.options_frame, text=self.textos["ES"]["colorqr"], command=self.select_qr_color, font=("Segoe UI", 9), bg="#3498DB", fg="white")
        self.btn_colorqr.grid(row=3, column=0, pady=4, padx=5, sticky="ew")
        self.btn_colorfondo = tk.Button(self.options_frame, text=self.textos["ES"]["colorfondo"], command=self.select_bg_color, font=("Segoe UI", 9), bg="#2ECC71", fg="white")
        self.btn_colorfondo.grid(row=3, column=1, pady=4, padx=5, sticky="ew")
        self.btn_logo = tk.Button(self.options_frame, text=self.textos["ES"]["logo"], command=self.select_logo, font=("Segoe UI", 9), bg="#9B59B6", fg="white")
        self.btn_logo.grid(row=4, column=0, columnspan=2, pady=6, sticky="ew")
        self.chk_auto_mobile = tk.Checkbutton(self.options_frame, text="Modo 100% compatible móvil (recomendado)",
            variable=self.qr_auto_mobile, bg="#F5F5F5", font=("Segoe UI", 9), command=self.change_and_preview)
        self.chk_auto_mobile.grid(row=6, column=0, columnspan=2, sticky="w", padx=2, pady=3)
        self.label_help_mobile = tk.Label(self.options_frame, text="Cuando está activado, tamaño y margen óptimos y desactiva los campos manuales.", font=("Segoe UI", 8), bg="#F5F5F5", fg="#7289a7", wraplength=210, justify="left")
        self.label_help_mobile.grid(row=7, column=0, columnspan=2, sticky="w")

        # ---- Panel vista previa ----
        self.preview_frame = tk.LabelFrame(self.root, text=self.textos["ES"]["vista_previa"], font=("Segoe UI", 10, "bold"), bg="#F5F5F5", fg="#2C3E50")
        self.preview_frame.grid(row=1, column=1, rowspan=3, padx=10, pady=10, sticky="nsew")
        self.preview_frame.columnconfigure(0, weight=1)
        for i in range(3): self.preview_frame.rowconfigure(i, weight=1)
        self.preview_canvas = tk.Canvas(self.preview_frame, width=250, height=250, bg="white", bd=1, relief="solid")
        self.preview_canvas.pack(padx=10, pady=10, expand=True, fill="both")
        self.qr_data_view = tk.Text(self.preview_frame, height=6, width=34, font=("Segoe UI", 8), bg="#EFEFEF", state=tk.DISABLED)
        self.qr_data_view.pack(padx=5, pady=3, expand=True, fill="both")
        self.btn_copiar = tk.Button(self.preview_frame, text=self.textos["ES"]["copiar"], command=self.copiar_portapapeles, font=("Segoe UI", 8), bg="#6EC977")
        self.btn_copiar.pack(padx=5, pady=(0,5), fill="x")

        # ---- Panel acciones con scrollbar ----
        self.action_frame = tk.LabelFrame(self.root, text=self.textos["ES"]["acciones"], font=("Segoe UI", 10, "bold"), bg="#F5F5F5", fg="#2C3E50")
        self.action_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        self.action_frame.columnconfigure(0, weight=1)
        self.action_canvas = tk.Canvas(self.action_frame, borderwidth=0, bg="#F5F5F5", highlightthickness=0)
        self.action_scrollbar = tk.Scrollbar(self.action_frame, orient="vertical", command=self.action_canvas.yview)
        self.action_canvas.configure(yscrollcommand=self.action_scrollbar.set)
        self.scrollable_action_frame = tk.Frame(self.action_canvas, bg="#F5F5F5")
        self.scrollable_action_frame.bind(
            "<Configure>", lambda e: self.action_canvas.configure(scrollregion=self.action_canvas.bbox("all"))
        )
        self.action_canvas.create_window((0, 0), window=self.scrollable_action_frame, anchor="nw")
        self.action_canvas.pack(side="left", fill="both", expand=True)
        self.action_scrollbar.pack(side="right", fill="y")
        self.scrollable_action_frame.columnconfigure(0, weight=1)
        self.btn_vista_previa = tk.Button(self.scrollable_action_frame, text=self.textos["ES"]["vista_prev"], command=self.change_and_preview, font=("Segoe UI", 9), bg="#1ABC9C", fg="white")
        self.btn_vista_previa.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.btn_guardar = tk.Button(self.scrollable_action_frame, text=self.textos["ES"]["guardar_qr"], command=self.save_qr, font=("Segoe UI", 9), bg="#E67E22", fg="white")
        self.btn_guardar.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.btn_csv = tk.Button(self.scrollable_action_frame, text=self.textos["ES"]["csv"], command=self.generate_from_file, font=("Segoe UI", 9), bg="#16A085", fg="white")
        self.btn_csv.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.btn_imprimir = tk.Button(self.scrollable_action_frame, text=self.textos["ES"]["imprimir"], command=self.create_print_sheet, font=("Segoe UI", 9), bg="#C0392B", fg="white")
        self.btn_imprimir.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.btn_tema = tk.Button(self.scrollable_action_frame, text=self.textos["ES"]["tema"], command=self.toggle_tema, font=("Segoe UI", 9), bg="#34495E", fg="white")
        self.btn_tema.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.btn_historial = tk.Button(self.scrollable_action_frame, text=self.textos["ES"]["historial"], command=self.mostrar_historial, font=("Segoe UI", 9), bg="#8395A7", fg="white")
        self.btn_historial.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        # --- Grid maestro (root) ---
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=9)
        self.root.grid_columnconfigure(1, weight=1)

        for var in [self.id_var, self.name_var, self.role_var, self.date_var, self.link_var, self.box_size_var, self.border_var, self.error_corr_var]:
            var.trace_add("write", lambda *args: self.change_and_preview())

        def update_fields_state(self):
            formato = self.format_var.get()
            widgets = [
                (self.id_var_entry, formato in ["Completo", "Tarjeta Básica"]),
                (self.name_var_entry, formato in ["Completo", "Tarjeta Básica"]),
                (self.role_var_entry, formato == "Completo"),
                (self.date_var_entry, formato == "Completo"),
                (self.link_var_entry, formato in ["Completo", "Solo Enlace"]),
                (self.custom_entry, formato in ["Completo", "Personalizado"]),
                (self.entry_boxsize, not self.qr_auto_mobile.get()),
                (self.entry_border, not self.qr_auto_mobile.get()),
            ]
            for widget, enabled in widgets:
                state = tk.NORMAL if enabled else tk.DISABLED
                widget.config(state=state)
                try:
                    widget.config(bg="#E4FFE4" if enabled else "#F0F0F0")
                except:
                    pass
            self.set_help_text()

    def set_help_text(self):
        idioma = self.idioma
        messages = {
            "Completo": self.textos[idioma]["ayuda_completo"],
            "Tarjeta Básica": self.textos[idioma]["ayuda_basica"],
            "Solo Enlace": self.textos[idioma]["ayuda_enlace"],
            "Personalizado": self.textos[idioma]["ayuda_pers"]
        }
        self.help_label.config(text=messages.get(self.format_var.get(), ""))

    def build_qr_data(self):
        formato = self.format_var.get()
        if formato == "Solo Enlace":
            return self.link_var.get()
        elif formato == "Tarjeta Básica":
            campos = []
            if self.id_var.get():
                campos.append(f"ID: {self.id_var.get()}")
            if self.name_var.get():
                campos.append(f"Nombre: {self.name_var.get()}")
            return "\n".join(campos)
        elif formato == "Personalizado":
            return self.custom_entry.get("1.0", tk.END).strip()
        else:
            campos = []
            if self.id_var.get():
                campos.append(f"ID: {self.id_var.get()}")
            if self.name_var.get():
                campos.append(f"Nombre: {self.name_var.get()}")
            if self.role_var.get():
                campos.append(f"Cargo: {self.role_var.get()}")
            if self.date_var.get():
                campos.append(f"Fecha: {self.date_var.get()}")
            if self.link_var.get():
                campos.append(f"Enlace: {self.link_var.get()}")
            custom_text = self.custom_entry.get("1.0", tk.END).strip()
            if custom_text:
                campos.append(custom_text)
            return "\n".join(campos)

    def update_preview_content(self):
        content = self.build_qr_data()
        self.qr_data_view.config(state=tk.NORMAL)
        self.qr_data_view.delete("1.0", tk.END)
        self.qr_data_view.insert("1.0", content)
        self.qr_data_view.config(state=tk.DISABLED)

    def change_and_preview(self, *args):
        self.update_fields_state()
        self.update_preview_content()
        self.generate_preview()

    def validar_campos(self):
        formato = self.format_var.get()
        idioma = self.idioma
        if formato == "Solo Enlace":
            url = self.link_var.get()
            if not (url.startswith("http://") or url.startswith("https://")):
                messagebox.showerror(self.textos[idioma]["error"], "El campo 'Enlace' debe ser una URL válida que comience con http:// o https://")
                return False
        elif formato == "Tarjeta Básica":
            if not (self.id_var.get() or self.name_var.get()):
                messagebox.showerror(self.textos[idioma]["error"], "Debes ingresar al menos ID o Nombre.")
                return False
        elif formato == "Personalizado":
            if not self.custom_entry.get("1.0", tk.END).strip():
                messagebox.showerror(self.textos[idioma]["error"], "El campo personalizado no puede estar vacío.")
                return False
        else:
            if not (self.id_var.get() or self.name_var.get() or self.role_var.get() or self.date_var.get() or self.link_var.get() or self.custom_entry.get("1.0", tk.END).strip()):
                messagebox.showerror(self.textos[idioma]["error"], "Debes ingresar al menos un dato para el código QR.")
                return False
        return True
    
    def cambiar_idioma(self, valor):
        idioma = "EN" if valor == "English" else "ES"
        self.idioma = idioma
        t = self.textos[idioma]
        self.label_titulo.config(text=t["title"])
        self.data_frame_container.config(text=t["datos_entrada"])
        self.label_id.config(text=t["id"])
        self.label_nombre.config(text=t["nombre"])
        self.label_cargo.config(text=t["cargo"])
        self.label_fecha.config(text=t["fecha"])
        self.label_enlace.config(text=t["enlace"])
        self.label_personalizado.config(text=t["personalizado"])
        self.format_frame.config(text=t["formato_qr"])
        self.label_tipo_qr.config(text=t["tipo_qr"])
        if idioma == "EN":
            self.format_cb["values"] = ["Complete", "Link Only", "Basic Card", "Custom"]
            formato_map = {"Completo": "Complete", "Solo Enlace": "Link Only", "Tarjeta Básica": "Basic Card", "Personalizado": "Custom"}
            anterior = self.format_var.get()
            self.format_var.set(formato_map.get(anterior, "Complete"))
        else:
            self.format_cb["values"] = ["Completo", "Solo Enlace", "Tarjeta Básica", "Personalizado"]
            formato_map = {"Complete": "Completo", "Link Only": "Solo Enlace", "Basic Card": "Tarjeta Básica", "Custom": "Personalizado"}
            anterior = self.format_var.get()
            self.format_var.set(formato_map.get(anterior, "Completo"))
        self.help_label.config(text=t["ayuda_completo"])
        self.options_frame.config(text=t["opciones_qr"])
        self.label_errorcorr.config(text=t["errorcorr"])
        self.label_boxsize.config(text=t["boxsize"])
        self.label_border.config(text=t["border"])
        self.label_previewsize.config(text=t["tam_preview"])
        self.btn_colorqr.config(text=t["colorqr"])
        self.btn_colorfondo.config(text=t["colorfondo"])
        self.btn_logo.config(text=t["logo"])
        self.label_help_mobile.config(
            text="Cuando está activado, tamaño y margen óptimos y desactiva los campos manuales."
            if idioma == "ES"
            else "When enabled, optimal size and margin for mobile and disables manual fields."
        )
        self.chk_auto_mobile.config(
            text="Modo 100% compatible móvil (recomendado)" if idioma == "ES" else "100% mobile compatible mode (recommended)"
        )
        self.action_frame.config(text=t["acciones"])
        self.btn_vista_previa.config(text=t["vista_prev"])
        self.btn_guardar.config(text=t["guardar_qr"])
        self.btn_csv.config(text=t["csv"])
        self.btn_imprimir.config(text=t["imprimir"])
        self.btn_tema.config(text=t["tema"])
        self.btn_historial.config(text=t["historial"])
        self.preview_frame.config(text=t["vista_previa"])
        self.btn_copiar.config(text=t["copiar"])
        self.set_help_text()

        # Opciones QR
        self.options_frame.config(text=t["opciones_qr"])
        self.label_errorcorr.config(text=t["errorcorr"])
        self.label_boxsize.config(text=t["boxsize"])
        self.label_border.config(text=t["border"])
        self.label_previewsize.config(text=t["tam_preview"])
        self.btn_colorqr.config(text=t["colorqr"])
        self.btn_colorfondo.config(text=t["colorfondo"])
        self.btn_logo.config(text=t["logo"])
        # Traducción explicativa (texto plano)
        self.label_help_mobile.config(
            text="Cuando está activado, tamaño y margen óptimos y desactiva los campos manuales."
            if idioma == "ES"
            else "When enabled, optimal size and margin for mobile and disables manual fields."
        )
        self.chk_auto_mobile.config(
            text="Modo 100% compatible móvil (recomendado)" if idioma == "ES" else "100% mobile compatible mode (recommended)"
        )
        # Panel acciones
        self.action_frame.config(text=t["acciones"])
        self.btn_vista_previa.config(text=t["vista_prev"])
        self.btn_guardar.config(text=t["guardar_qr"])
        self.btn_csv.config(text=t["csv"])
        self.btn_imprimir.config(text=t["imprimir"])
        self.btn_tema.config(text=t["tema"])
        self.btn_historial.config(text=t["historial"])
        # Panel vista previa y botón copiar
        self.preview_frame.config(text=t["vista_previa"])
        self.btn_copiar.config(text=t["copiar"])
        # Ayuda de formato (según selección)
        self.set_help_text()


    def guardar_historial(self):
        datos = {
            "ID": self.id_var.get(),
            "Nombre": self.name_var.get(),
            "Cargo": self.role_var.get(),
            "Fecha": self.date_var.get(),
            "Enlace": self.link_var.get(),
            "Contenido": self.custom_entry.get("1.0", tk.END).strip(),
            "Formato": self.format_var.get(),
            "Logo": self.logo_path
        }
        self.historial.insert(0, datos)
        self.historial = self.historial[:10]

    def mostrar_historial(self):
        idioma = self.idioma
        historial_win = tk.Toplevel(self.root)
        historial_win.title(self.textos[idioma]["historial"])
        for i, datos in enumerate(self.historial):
            txt = f"{i+1}. ID: {datos['ID']} {self.textos[idioma]['nombre']} {datos['Nombre']} Formato: {datos['Formato']}"
            btn = tk.Button(historial_win, text=txt, command=lambda d=datos: self.cargar_historial(d))
            btn.pack(fill="x", padx=10, pady=2)

    def cargar_historial(self, datos):
        self.id_var.set(datos["ID"])
        self.name_var.set(datos["Nombre"])
        self.role_var.set(datos["Cargo"])
        self.date_var.set(datos["Fecha"])
        self.link_var.set(datos["Enlace"])
        self.custom_entry.delete("1.0", tk.END)
        self.custom_entry.insert("1.0", datos["Contenido"])
        self.format_var.set(datos["Formato"])
        self.logo_path = datos["Logo"]
        self.change_and_preview()

    def copiar_portapapeles(self):
        idioma = self.idioma
        datos = self.build_qr_data()
        self.root.clipboard_clear()
        self.root.clipboard_append(datos)
        messagebox.showinfo(self.textos[idioma]["success"], self.textos[idioma]["copiado"])

    def generate_qr(self):
        data = self.build_qr_data()
        if self.format_var.get() == "Solo Enlace":
            data = data.strip()

        if self.qr_auto_mobile.get():
            qr_temp = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=6,
            )
            qr_temp.add_data(data)
            qr_temp.make(fit=True)
            mod_count = qr_temp.modules_count
            border = qr_temp.border
            desired_size = 1000
            box_size = max(desired_size // (mod_count + 2 * border), 8)
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=box_size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)
        else:
            box_size = max(self.box_size_var.get(), 8)
            border = max(self.border_var.get(), 4)
            error_level = self.error_corr_var.get().upper()
            error_map = {
                "L": qrcode.constants.ERROR_CORRECT_L,
                "M": qrcode.constants.ERROR_CORRECT_M,
                "Q": qrcode.constants.ERROR_CORRECT_Q,
                "H": qrcode.constants.ERROR_CORRECT_H,
            }
            qr = qrcode.QRCode(
                version=None,
                error_correction=error_map.get(error_level, qrcode.constants.ERROR_CORRECT_H),
                box_size=box_size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)
        img = qr.make_image(fill_color=self.qr_color, back_color=self.bg_color).convert("RGB")
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = Image.open(self.logo_path)
                logo_size = int(img.size[0] / 5)
                logo.thumbnail((logo_size, logo_size), Image.LANCZOS)
                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                if logo.mode in ("RGBA", "LA"):
                    img.paste(logo, pos, mask=logo)
                else:
                    img.paste(logo, pos)
            except Exception as e:
                print("Error al insertar logo:", e)
        return img

    def generate_preview(self):
        if not self.validar_campos():
            return
        img = self.generate_qr()
        self.qr_image = img
        size = self.preview_size_var.get()
        img_resized = img.resize((size, size), resample=Image.NEAREST)  # <--
        self.preview_canvas.config(width=size, height=size)
        self.tk_image = ImageTk.PhotoImage(img_resized)
        try:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(size // 2, size // 2, image=self.tk_image)
            self.preview_canvas.image = self.tk_image
        except Exception:
            try:
                self.preview_label.config(image=self.tk_image)
                self.preview_label.image = self.tk_image
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo mostrar la vista previa: {e}")

    def save_qr(self):
        idioma = self.idioma
        if not self.validar_campos():
            return
        self.guardar_historial()
        if not self.qr_image:
            self.generate_preview()
        if not self.qr_image:
            return
        default_name = f"{self.id_var.get()}_{self.name_var.get()}".strip("_")
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("PDF", "*.pdf"), ("SVG", "*.svg")],
        )
        if filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext == ".svg":
                # SVG, igual
                pass  # (tu lógica SVG aquí si usas Segno/SVG)
            else:
                # Antes de guardar, fuerza tamaño 1000x1000 px puro y nearest
                img_fixed = self.qr_image.resize((1000, 1000), resample=Image.NEAREST)
                img_fixed.save(filename, "PNG")
            messagebox.showinfo(self.textos[idioma]["success"], f"{self.textos[idioma]['saved']} {filename}")

    def select_logo(self):
        idioma = self.idioma
        self.logo_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp"), ("Images", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if self.logo_path:
            messagebox.showinfo(self.textos[idioma]["logo"], os.path.basename(self.logo_path))
        self.change_and_preview()

    def select_qr_color(self):
        color = colorchooser.askcolor(title=self.textos[self.idioma]["colorqr"])
        if color[1]:
            self.qr_color = color[1]
            self.change_and_preview()

    def select_bg_color(self):
        color = colorchooser.askcolor(title=self.textos[self.idioma]["colorfondo"])
        if color[1]:
            self.bg_color = color[1]
            self.change_and_preview()

    def toggle_tema(self):
        if self.tema_claro:
            color_fondo = "#263238"
            color_letra = "#F5F5F5"
        else:
            color_fondo = "#F5F5F5"
            color_letra = "#263238"
        self.tema_claro = not self.tema_claro
        self.root.config(bg=color_fondo)
        for widget in self.root.winfo_children():
            try:
                widget.config(bg=color_fondo, fg=color_letra)
            except:
                pass

    def generate_from_file(self):
        idioma = self.idioma
        filepath = filedialog.askopenfilename(filetypes=[("Archivos CSV/Excel", "*.csv;*.xlsx;*.xls")])
        if not filepath:
            return
        outdir = filedialog.askdirectory()
        if not outdir:
            return
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath, encoding="utf-8")
        else:
            df = pd.read_excel(filepath)
        for _, row in df.iterrows():
            self.id_var.set(row.get("ID", ""))
            self.name_var.set(row.get("Nombre", ""))
            self.role_var.set(row.get("Cargo", ""))
            self.date_var.set(row.get("Fecha", ""))
            self.link_var.set(row.get("Enlace", ""))
            self.custom_entry.delete("1.0", tk.END)
            self.custom_entry.insert("1.0", row.get("Contenido", ""))
            self.change_and_preview()
            img = self.generate_qr()
            filename = os.path.join(outdir, f"{self.id_var.get()}_{self.name_var.get()}.png")
            img.save(filename)
        messagebox.showinfo(self.textos[idioma]["success"], self.textos[idioma]["csv_success"])

    def create_print_sheet(self):
        idioma = self.idioma
        if not self.validar_campos():
            return
        if not self.qr_image:
            self.generate_preview()
        if not self.qr_image:
            return
        try:
            filas = int(self.simple_input("Número de filas", "3"))
            columnas = int(self.simple_input("Número de columnas", "7"))
        except:
            filas, columnas = 3, 7
        sheet = Image.new("RGB", (2480, 3508), "white")
        qr_size = 300
        img_qr = self.qr_image.resize((qr_size, qr_size), resample=RESAMPLE_FILTER)
        x, y = 50, 50
        for i in range(filas):
            for j in range(columnas):
                pos = (x + j * (qr_size + 50), y + i * (qr_size + 50))
                sheet.paste(img_qr, pos)
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if filename:
            sheet.save(filename)
            messagebox.showinfo(self.textos[idioma]["success"], f"{self.textos[idioma]['saved']} {filename}")

    def simple_input(self, title, default=""):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        tk.Label(popup, text=title).pack(pady=5)
        entry = tk.Entry(popup)
        entry.insert(0, default)
        entry.pack(pady=5)
        result = {"val": None}
        def on_ok():
            result["val"] = entry.get()
            popup.destroy()
        tk.Button(popup, text="OK", command=on_ok).pack(pady=5)
        popup.wait_window()
        return result["val"]

if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()
