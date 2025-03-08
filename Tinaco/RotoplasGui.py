import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

class RotoplasGUI(ctk.CTk):
    def __init__(self, tinaco):
        super().__init__()
        
        self.tinaco = tinaco
        
        # Configuración de la ventana
        self.title("Sistema Rotoplas Monitor (Multiprocessing)")
        self.geometry("1024x768")
        self.minsize(800, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Frame principal con grid
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Header Frame
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Título con estilo mejorado
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="SISTEMA DE MONITOREO ROTOPLAS (MULTIPROCESSING)",
            font=("Roboto", 24, "bold"),
            text_color="#3B82F6"
        )
        self.title_label.grid(row=0, column=0, pady=15)
        
        # Content Frame con 2 columnas
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=2)
        self.content_frame.grid_columnconfigure(1, weight=3)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Panel izquierdo - Medidor de agua
        self.left_panel = ctk.CTkFrame(self.content_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Contenedor para medidor y etiqueta
        self.meter_container = ctk.CTkFrame(self.left_panel)
        self.meter_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título del medidor
        self.meter_title = ctk.CTkLabel(
            self.meter_container,
            text="Nivel de Agua",
            font=("Roboto", 20, "bold")
        )
        self.meter_title.pack(pady=10)
        
        # Medidor de agua mejorado
        self.water_level = ctk.CTkProgressBar(
            self.meter_container,
            orientation="vertical",
            height=300,
            width=40,
            progress_color="#3B82F6",
            border_width=2,
            border_color="#1E3A8A"
        )
        self.water_level.pack(pady=20)
        self.water_level.set(0)
        
        # Información de agua con estilo mejorado
        self.water_info = ctk.CTkLabel(
            self.meter_container,
            text="0L",
            font=("Roboto", 24, "bold")
        )
        self.water_info.pack(pady=10)
        
        # Bomba indicador
        self.bomba_frame = ctk.CTkFrame(self.meter_container)
        self.bomba_frame.pack(pady=10)
        
        self.bomba_label = ctk.CTkLabel(
            self.bomba_frame,
            text="Estado de la Bomba:",
            font=("Roboto", 16, "bold")
        )
        self.bomba_label.pack(side="left", padx=5)
        
        self.bomba_status = ctk.CTkLabel(
            self.bomba_frame,
            text="Inactiva",
            font=("Roboto", 16),
            text_color="#EF4444"
        )
        self.bomba_status.pack(side="left", padx=5)
        
        # Panel derecho - Estados
        self.right_panel = ctk.CTkFrame(self.content_frame)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Sección de entradas
        self.create_status_section(
            self.right_panel, 
            "ENTRADAS DE AGUA", 
            ["Pluvial", "Cisterna"], 
            0
        )
        
        # Sección de salidas
        self.create_status_section(
            self.right_panel, 
            "TOMAS DE AGUA", 
            ["Jardin", "Lavadero", "Banio"], 
            1
        )
        
        # Botón de simulación de lluvia
        self.rain_button = ctk.CTkButton(
            self.right_panel,
            text="Simular Lluvia",
            command=self.toggle_rain,
            font=("Roboto", 16, "bold"),
            height=40
        )
        self.rain_button.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        
        # Footer con información adicional
        self.create_footer()
        
        # Iniciar actualización
        self.is_raining = False
        self.after(500, self.update_display)
    
    def toggle_rain(self):
        if self.is_raining:
            self.tinaco.lluvia_evento.clear()
            self.is_raining = False
            self.rain_button.configure(text="Simular Lluvia")
        else:
            self.tinaco.lluvia_evento.set()
            self.is_raining = True
            self.rain_button.configure(text="Detener Lluvia")

    def create_status_section(self, parent, title, items, row):
        section = ctk.CTkFrame(parent)
        section.grid(row=row, column=0, sticky="ew", padx=10, pady=10)
        section.grid_columnconfigure(0, weight=1)
        
        # Título de sección
        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=("Roboto", 20, "bold"),
            text_color="#3B82F6"
        )
        title_label.pack(pady=10)
        
        # Contenedor para indicadores
        indicators_container = ctk.CTkFrame(section)
        indicators_container.pack(fill="x", padx=20, pady=10)
        
        # Crear indicadores
        if title.startswith("ENTRADAS"):
            self.input_indicators = {}
            for item in items:
                self.input_indicators[item] = self.create_indicator(indicators_container, item)
        else:
            self.output_indicators = {}
            for item in items:
                self.output_indicators[item] = self.create_indicator(indicators_container, item)

    def create_indicator(self, parent, name):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5)
        frame.grid_columnconfigure(1, weight=1)
        
        # Icono o indicador visual
        status_indicator = ctk.CTkLabel(
            frame, 
            text="●",
            font=("Roboto", 24),
            text_color="#EF4444"
        )
        status_indicator.pack(side="left", padx=10)
        
        # Nombre del indicador
        name_label = ctk.CTkLabel(
            frame,
            text=name,
            font=("Roboto", 16, "bold")
        )
        name_label.pack(side="left", padx=10)
        
        # Estado
        status = ctk.CTkLabel(
            frame,
            text="Desactivado",
            font=("Roboto", 16),
            text_color="#EF4444"
        )
        status.pack(side="right", padx=20)
        
        return {"indicator": status_indicator, "status": status}

    def create_footer(self):
        footer = ctk.CTkFrame(self.main_frame)
        footer.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        footer.grid_columnconfigure(0, weight=1)
        
        status_text = ctk.CTkLabel(
            footer,
            text="Sistema Funcionando Correctamente",
            font=("Roboto", 12)
        )
        status_text.pack(pady=5)

    def update_display(self):
        # Obtener estado actual
        estado = self.tinaco.obtener_estado()
        
        # Actualizar nivel de agua
        level = estado['nivel_agua'] / self.tinaco.capacidad_max
        self.water_level.set(level)
        self.water_info.configure(text=f"{estado['nivel_agua']:.1f}L ({estado['porcentaje']:.1f}%)")
        
        # Actualizar estado de bomba
        self.bomba_status.configure(
            text="Activa" if estado['bomba_activa'] else "Inactiva",
            text_color="#22C55E" if estado['bomba_activa'] else "#EF4444"
        )
        
        # Actualizar indicadores de entrada
        for source, status in estado['fuentes'].items():
            self.input_indicators[source]["status"].configure(
                text="Activo" if status else "Desactivado",
                text_color="#22C55E" if status else "#EF4444"
            )
            self.input_indicators[source]["indicator"].configure(
                text_color="#22C55E" if status else "#EF4444"
            )
            
        # Actualizar indicadores de toma
        for outlet, status in estado['consumos'].items():
            self.output_indicators[outlet]["status"].configure(
                text="Activo" if status else "Desactivado",
                text_color="#22C55E" if status else "#EF4444"
            )
            self.output_indicators[outlet]["indicator"].configure(
                text_color="#22C55E" if status else "#EF4444"
            )
        
        # próxima actualización
        self.after(500, self.update_display)