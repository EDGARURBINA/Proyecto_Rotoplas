from multiprocessing import Process, Manager
import time
import random
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from RotoplasGui import RotoplasGUI


# Importar TinacoContext
from tinaco_context import TinacoContext

def proceso_pluvial(tinaco, terminar_evento):
    """
    Proceso que simula la entrada de agua pluvial.
    Se activa aleatoriamente o por simulación manual.
    """
    print("Proceso Pluvial iniciado")
    
    while not terminar_evento.is_set():
        # Simulación aleatoria de lluvia (20% de probabilidad)
        if random.random() < 0.2:
            tinaco.lluvia_evento.set()
            print("Está lloviendo")
        else:
            # No interferimos con la lluvia manual
            if not tinaco.lluvia_evento.is_set():
                pass
            
        if tinaco.lluvia_evento.is_set():
            if tinaco.llenar_desde_pluvial():
                pass  # El mensaje ya se imprime en el método
            else:
                pass  # El mensaje ya se imprime en el método
        
        time.sleep(4)  # Verificar cada 4 segundos


def proceso_cisterna(tinaco, terminar_evento):
    """
    Proceso que gestiona el llenado desde la cisterna.
    Se activa cuando el nivel del agua es bajo.
    """
    print("Proceso Cisterna iniciado")
    
    while not terminar_evento.is_set():
        estado = tinaco.obtener_estado()
        
        # Activar llenado si el nivel es menor al 30%
        if estado['porcentaje'] < 30:
            tinaco.activar_bomba()
            if tinaco.llenar_desde_cisterna():
                pass  # El mensaje ya se imprime en el método
            else:
                pass  # El mensaje ya se imprime en el método
                tinaco.desactivar_bomba()
        elif estado['porcentaje'] >= 90:
            # Desactivar bomba si el tinaco está casi lleno
            tinaco.desactivar_bomba()
            
        time.sleep(3)  # Verificar cada 3 segundos


def proceso_bomba(tinaco, terminar_evento):
    """
    Proceso que controla la bomba de presión.
    La bomba se activa cuando alguna toma está abierta y el nivel es superior al 25%.
    """
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
    """
    Proceso que simula el consumo de agua para el jardín.
    Solo consume si el nivel está por encima del 50%.
    """
    print("Proceso Jardín iniciado")
    
    while not terminar_evento.is_set():
        tinaco.consumir_jardin()  # El mensaje ya se imprime en el método
        time.sleep(5)  # Regar cada 5 segundos


def proceso_lavadero(tinaco, terminar_evento):
    """
    Proceso que simula el consumo de agua para el lavadero.
    No debe llevar el tinaco a menos del 3%.
    """
    print("Proceso Lavadero iniciado")
    
    while not terminar_evento.is_set():
        tinaco.consumir_lavadero()  # El mensaje ya se imprime en el método
        time.sleep(4)  # Usar lavadero cada 4 segundos


def proceso_banio(tinaco, terminar_evento):
    """
    Proceso que simula el consumo de agua para el baño.
    Siempre puede consumir mientras haya agua.
    """
    print("Proceso Baño iniciado")
    
    while not terminar_evento.is_set():
        tinaco.consumir_banio()  # El mensaje ya se imprime en el método
        time.sleep(3)  # Usar baño cada 3 segundos


def main():
    """Función principal que inicia el sistema completo."""
    #contexto compartido
    manager = Manager()
    terminar_evento = manager.Event()
    
    # se crea el objeti tinacocontexts
    tinaco = TinacoContext()
    
    #  procesos
    procesos = [
        Process(name="Pluvial", target=proceso_pluvial, args=(tinaco, terminar_evento)),
        Process(name="Cisterna", target=proceso_cisterna, args=(tinaco, terminar_evento)),
        Process(name="Bomba", target=proceso_bomba, args=(tinaco, terminar_evento)),
        Process(name="Jardin", target=proceso_jardin, args=(tinaco, terminar_evento)),
        Process(name="Lavadero", target=proceso_lavadero, args=(tinaco, terminar_evento)),
        Process(name="Banio", target=proceso_banio, args=(tinaco, terminar_evento)),
    ]
    
    # Inicia los  procesos
    for proceso in procesos:
        proceso.start()
        print(f"Proceso {proceso.name} iniciado con PID {proceso.pid}")
    
    try:
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