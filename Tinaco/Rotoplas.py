from multiprocessing import Process, Manager, Lock, Event
import time
import random

class TinacoContext:
    def __init__(self):
        self.lock = Lock()
        self.capacidad_max = 1000  # Tods los litros iniciales
        self.capacidad_min = 100  
        self.nivel_agua = 300      
        self.bomba_activa = False
        self.bomba_evento = Event()
        self.lluvia_evento = Event()
        
        # Flujos de agua
        #Litros por ciclo
        self.flujo_pluvial = 15    
        self.flujo_cisterna = 30   
        self.consumo_jardin = 10   
        self.consumo_lavadero = 8 
        self.consumo_banio = 5     
        
        # Estado de los componentes
        self.fuentes = {'Pluvial': False, 'Cisterna': False}
        self.consumos = {'Jardin': False, 'Lavadero': False, 'Banio': False}
    
    def llenar_desde_pluvial(self):
        with self.lock:
            if self.nivel_agua + self.flujo_pluvial <= self.capacidad_max:
                self.nivel_agua += self.flujo_pluvial
                self.fuentes['Pluvial'] = True
                return True
            else:
                self.fuentes['Pluvial'] = False
                return False
    
    def llenar_desde_cisterna(self):
        with self.lock:
            if self.nivel_agua + self.flujo_cisterna <= self.capacidad_max:
                self.nivel_agua += self.flujo_cisterna
                self.fuentes['Cisterna'] = True
                return True
            else:
                self.fuentes['Cisterna'] = False
                return False
    
    def activar_bomba(self):
        with self.lock:
            if not self.bomba_activa and self.nivel_agua > self.capacidad_max * 0.25:
                self.bomba_activa = True
                self.bomba_evento.set()
                return True
            return False
    
    def desactivar_bomba(self):
        with self.lock:
            if self.bomba_activa:
                self.bomba_activa = False
                self.bomba_evento.clear()
                return True
            return False
    
    def consumir_jardin(self):
        with self.lock:
            # Jardín solo puede consumir si el nivel está por encima del 50%
            nivel_minimo_jardin = self.capacidad_max * 0.5
            
            if self.nivel_agua > nivel_minimo_jardin and self.nivel_agua - self.consumo_jardin >= self.capacidad_min:
                self.nivel_agua -= self.consumo_jardin
                self.consumos['Jardin'] = True
                return True
            else:
                self.consumos['Jardin'] = False
                return False
    
    def consumir_lavadero(self):
        with self.lock:
            # Lavadero no puede consumir si el nivel baja del 3%
            nivel_minimo_lavadero = self.capacidad_max * 0.03
            
            if self.nivel_agua > nivel_minimo_lavadero and self.nivel_agua - self.consumo_lavadero >= nivel_minimo_lavadero:
                self.nivel_agua -= self.consumo_lavadero
                self.consumos['Lavadero'] = True
                return True
            else:
                self.consumos['Lavadero'] = False
                return False
    
    def consumir_banio(self):
        with self.lock:
            # Baño siempre puede consumir a menos que esté vacío
            if self.nivel_agua > 0 and self.nivel_agua - self.consumo_banio >= 0:
                self.nivel_agua -= self.consumo_banio
                self.consumos['Banio'] = True
                return True
            else:
                self.consumos['Banio'] = False
                return False
    
    def obtener_estado(self):
        with self.lock:
            return {
                'nivel_agua': self.nivel_agua,
                'porcentaje': (self.nivel_agua / self.capacidad_max) * 100,
                'bomba_activa': self.bomba_activa,
                'fuentes': self.fuentes.copy(),
                'consumos': self.consumos.copy()
            }


def proceso_pluvial(tinaco, terminar_evento):
    print("Proceso Pluvial iniciado")
    
    while not terminar_evento.is_set():
        # Simulación aleatoria de lluvia (20% de probabilidad)
        if random.random() < 0.2:
            tinaco.lluvia_evento.set()
            print("Está lloviendo")
        else:
            tinaco.lluvia_evento.clear()
            
        if tinaco.lluvia_evento.is_set():
            if tinaco.llenar_desde_pluvial():
                print(f"Llenando desde Pluvial: {tinaco.flujo_pluvial} litros")
            else:
                print("No se puede llenar más desde Pluvial (capacidad máxima)")
        
        time.sleep(4)  # Verificar cada 4 segundos


def proceso_cisterna(tinaco, terminar_evento):
    print("Proceso Cisterna iniciado")
    
    while not terminar_evento.is_set():
        estado = tinaco.obtener_estado()
        
        # Activar llenado si el nivel es menor al 30%
        if estado['porcentaje'] < 30:
            tinaco.activar_bomba()
            if tinaco.llenar_desde_cisterna():
                print(f"Bombeando desde Cisterna: {tinaco.flujo_cisterna} litros")
            else:
                print("No se puede llenar más desde Cisterna (capacidad máxima)")
                tinaco.desactivar_bomba()
        elif estado['porcentaje'] >= 90:
            # Desactivar bomba si el tinaco está casi lleno
            tinaco.desactivar_bomba()
            
        time.sleep(3)  # Verificar cada 3 segundos


def proceso_bomba(tinaco, terminar_evento):
    print("Proceso Bomba iniciado")
    
    while not terminar_evento.is_set():
        # Esperar a que la bomba se active
        if tinaco.bomba_evento.wait(timeout=1):
            print("Bomba encendida")
            
            # Mientras la bomba esté activa y haya consumo
            while tinaco.bomba_activa and not terminar_evento.is_set():
                estado = tinaco.obtener_estado()
                
                # Verificar si hay algún consumo activo
                consumos_activos = any(estado['consumos'].values())
                
                # Verificar nivel del agua
                if not consumos_activos or estado['porcentaje'] < 25:
                    tinaco.desactivar_bomba()
                    print("Bomba apagada")
                    break
                
                time.sleep(1)


def proceso_jardin(tinaco, terminar_evento):
    print("Proceso Jardín iniciado")
    
    while not terminar_evento.is_set():
        if tinaco.consumir_jardin():
            print(f"Consumiendo agua para Jardín: {tinaco.consumo_jardin} litros")
        else:
            print("No se puede usar agua para Jardín (nivel insuficiente)")
            
        time.sleep(5)  # Regar cada 5 segundos


def proceso_lavadero(tinaco, terminar_evento):
    print("Proceso Lavadero iniciado")
    
    while not terminar_evento.is_set():
        if tinaco.consumir_lavadero():
            print(f"Consumiendo agua para Lavadero: {tinaco.consumo_lavadero} litros")
        else:
            print("No se puede usar agua para Lavadero (nivel insuficiente)")
            
        time.sleep(4)  # Usar lavadero cada 4 segundos


def proceso_banio(tinaco, terminar_evento):
    print("Proceso Baño iniciado")
    
    while not terminar_evento.is_set():
        if tinaco.consumir_banio():
            print(f"Consumiendo agua para Baño: {tinaco.consumo_banio} litros")
        else:
            print("No se puede usar agua para Baño (tinaco vacío)")
            
        time.sleep(3)  # Usar baño cada 3 segundos


def main():
    # Crear Manager y registrar TinacoContext
    with Manager() as manager:
        # Crear evento de terminación
        terminar_evento = manager.Event()
        
        # Crear contexto compartido
        tinaco = TinacoContext()
        
        # procesos
        procesos = [
            Process(name="Pluvial", target=proceso_pluvial, args=(tinaco, terminar_evento)),
            Process(name="Cisterna", target=proceso_cisterna, args=(tinaco, terminar_evento)),
            Process(name="Bomba", target=proceso_bomba, args=(tinaco, terminar_evento)),
            Process(name="Jardin", target=proceso_jardin, args=(tinaco, terminar_evento)),
            Process(name="Lavadero", target=proceso_lavadero, args=(tinaco, terminar_evento)),
            Process(name="Banio", target=proceso_banio, args=(tinaco, terminar_evento)),
        ]
        
        # Iniciar procesos
        for proceso in procesos:
            proceso.start()
            print(f"Proceso {proceso.name} iniciado con PID {proceso.pid}")
        
        try:
            # Importamos e iniciamos la GUI
            from RotoplasGui import RotoplasGUI
            
            # Iniciar GUI
            app = RotoplasGUI(tinaco)
            app.protocol("WM_DELETE_WINDOW", lambda: terminar_evento.set())
            app.mainloop()
        except KeyboardInterrupt:
            print("\nInterrupción del teclado detectada.")
        finally:
            # Señalizar terminación
            terminar_evento.set()
            print("Señal de terminación enviada a todos los procesos.")
            
            # Esperar a que todos los procesos terminen
            for proceso in procesos:
                proceso.join(timeout=2)
                if proceso.is_alive():
                    print(f"Proceso {proceso.name} no respondió, terminando forzosamente.")
                    proceso.terminate()
            
            print("Sistema terminado correctamente.")


if __name__ == "__main__":
    main()