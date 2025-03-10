from multiprocessing import Lock, Manager

class TinacoContext:
    def __init__(self):
        
        manager = Manager()
        self.lock = manager.Lock()
        self.lluvia_evento = manager.Event()
        self.bomba_evento = manager.Event()
        
        # Configuration values
        self.capacidad_max = 1000  # Capacidad máxima en litros
        self.capacidad_min = 100   # Capacidad mínima en litros
        self.nivel_agua = 300      # Nivel inicial de agua
        self.bomba_activa = False
        
        # Flujos de agua (litros por ciclo)
        self.flujo_pluvial = 15    
        self.flujo_cisterna = 30   
        self.consumo_jardin = 10   
        self.consumo_lavadero = 8 
        self.consumo_banio = 5     
        
        # Estado de los componentes
        self.fuentes = {'Pluvial': False, 'Cisterna': False}
        self.consumos = {'Jardin': False, 'Lavadero': False, 'Banio': False}
    
    def llenar_desde_pluvial(self):
        """Método para llenar el tinaco desde agua pluvial, respetando la capacidad máxima."""
        with self.lock:
            nivel_anterior = self.nivel_agua
            porcentaje_anterior = (nivel_anterior / self.capacidad_max) * 100
            
            if self.nivel_agua + self.flujo_pluvial <= self.capacidad_max:
                self.nivel_agua += self.flujo_pluvial
                self.fuentes['Pluvial'] = True
                
                porcentaje_actual = (self.nivel_agua / self.capacidad_max) * 100
                porcentaje_agregado = porcentaje_actual - porcentaje_anterior
                print(f"Se añadió {porcentaje_agregado:.1f}% desde Pluvial, nivel actual = {porcentaje_actual:.1f}%")
                return True
            else:
                self.fuentes['Pluvial'] = False
                print(f"No se puede llenar más desde Pluvial (capacidad máxima: {self.capacidad_max}L)")
                return False
    
    def llenar_desde_cisterna(self):
        """Método para llenar el tinaco desde la cisterna, respetando la capacidad máxima."""
        with self.lock:
            nivel_anterior = self.nivel_agua
            porcentaje_anterior = (nivel_anterior / self.capacidad_max) * 100
            
            if self.nivel_agua + self.flujo_cisterna <= self.capacidad_max:
                self.nivel_agua += self.flujo_cisterna
                self.fuentes['Cisterna'] = True
                
                porcentaje_actual = (self.nivel_agua / self.capacidad_max) * 100
                porcentaje_agregado = porcentaje_actual - porcentaje_anterior
                print(f"Se añadió {porcentaje_agregado:.1f}% desde Cisterna, nivel actual = {porcentaje_actual:.1f}%")
                return True
            else:
                self.fuentes['Cisterna'] = False
                print(f"No se puede llenar más desde Cisterna (capacidad máxima: {self.capacidad_max}L)")
                return False
    
    def activar_bomba(self):
        """Activa la bomba si el nivel de agua supera el 25% de la capacidad."""
        with self.lock:
            nivel_minimo_bomba = self.capacidad_max * 0.25
            if not self.bomba_activa and self.nivel_agua > nivel_minimo_bomba:
                self.bomba_activa = True
                self.bomba_evento.set()
                print(f"Bomba activada (nivel: {(self.nivel_agua / self.capacidad_max) * 100:.1f}%)")
                return True
            elif not self.bomba_activa:
                print(f"No se puede activar la bomba, nivel insuficiente: {(self.nivel_agua / self.capacidad_max) * 100:.1f}%")
            return False
    
    def desactivar_bomba(self):
        """Desactiva la bomba de agua."""
        with self.lock:
            if self.bomba_activa:
                self.bomba_activa = False
                self.bomba_evento.clear()
                print(f"Bomba desactivada (nivel: {(self.nivel_agua / self.capacidad_max) * 100:.1f}%)")
                return True
            return False
    
    def consumir_jardin(self):
        """
        Consume agua para el jardín si se cumplen las restricciones:
        - Nivel > 50% de la capacidad
        - No baja del mínimo permitido
        """
        with self.lock:
            nivel_anterior = self.nivel_agua
            porcentaje_anterior = (nivel_anterior / self.capacidad_max) * 100
            
            # Jardín solo puede consumir si el nivel está por encima del 50%
            nivel_minimo_jardin = self.capacidad_max * 0.5
            
            if self.nivel_agua > nivel_minimo_jardin and self.nivel_agua - self.consumo_jardin >= self.capacidad_min:
                self.nivel_agua -= self.consumo_jardin
                self.consumos['Jardin'] = True
                
                porcentaje_actual = (self.nivel_agua / self.capacidad_max) * 100
                porcentaje_consumido = porcentaje_anterior - porcentaje_actual
                print(f"El jardín consumió {porcentaje_consumido:.1f}%, nivel actual = {porcentaje_actual:.1f}%")
                return True
            else:
                self.consumos['Jardin'] = False
                print(f"No se puede usar agua para Jardín (nivel insuficiente: {porcentaje_anterior:.1f}%)")
                return False
    
    def consumir_lavadero(self):
        """
        Consume agua para el lavadero si se cumplen las restricciones:
        - No debe llevar el tinaco a menos del 3%
        """
        with self.lock:
            nivel_anterior = self.nivel_agua
            porcentaje_anterior = (nivel_anterior / self.capacidad_max) * 100
            
            # Lavadero no puede consumir si el nivel baja del 3%
            nivel_minimo_lavadero = self.capacidad_max * 0.03
            
            if self.nivel_agua > nivel_minimo_lavadero and self.nivel_agua - self.consumo_lavadero >= nivel_minimo_lavadero:
                self.nivel_agua -= self.consumo_lavadero
                self.consumos['Lavadero'] = True
                
                porcentaje_actual = (self.nivel_agua / self.capacidad_max) * 100
                porcentaje_consumido = porcentaje_anterior - porcentaje_actual
                print(f"El lavadero consumió {porcentaje_consumido:.1f}%, nivel actual = {porcentaje_actual:.1f}%")
                return True
            else:
                self.consumos['Lavadero'] = False
                print(f"No se puede usar agua para Lavadero (nivel insuficiente: {porcentaje_anterior:.1f}%)")
                return False
    
    def consumir_banio(self):
        """
        Consume agua para el baño:
        - Siempre disponible mientras haya agua
        """
        with self.lock:
            nivel_anterior = self.nivel_agua
            porcentaje_anterior = (nivel_anterior / self.capacidad_max) * 100
            
            # Baño siempre puede consumir a menos que esté vacío
            if self.nivel_agua > 0 and self.nivel_agua - self.consumo_banio >= 0:
                self.nivel_agua -= self.consumo_banio
                self.consumos['Banio'] = True
                
                porcentaje_actual = (self.nivel_agua / self.capacidad_max) * 100
                porcentaje_consumido = porcentaje_anterior - porcentaje_actual
                print(f"El baño consumió {porcentaje_consumido:.1f}%, nivel actual = {porcentaje_actual:.1f}%")
                return True
            else:
                self.consumos['Banio'] = False
                print(f"No se puede usar agua para Baño (tinaco vacío)")
                return False
    
    def obtener_estado(self):
        """Obtiene el estado actual del tinaco y sus componentes."""
        with self.lock:
            return {
                'nivel_agua': self.nivel_agua,
                'porcentaje': (self.nivel_agua / self.capacidad_max) * 100,
                'bomba_activa': self.bomba_activa,
                'fuentes': self.fuentes.copy(),
                'consumos': self.consumos.copy()
            }