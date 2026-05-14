"""
menu.py

Descripción:
- Módulo principal que permite elegir el protocolo de red (TCP o UDP) antes de iniciar la acción de conectar o alojar un servidor.

Funcionamiento:
- Despliega la interfaz principal para elegir el servicio (Unirse a un servidor o Crear un servidor) y el protocolo de comunicación.
- Captura la selección del usuario y pasa el protocolo elegido ('TCP' o 'UDP') a los módulos 'conectar.py' y 'alojar.py'.

Autores:
- Willian Alexander Tolano Fierros
- Noelia Encinas Noriega
- Abelardo Andre Vega Romero
- Julian Gerardo Izaguirre Menchaca
"""

"""Importaciones"""
import conectar # Módulo para el cliente: maneja la conexión a un servidor
import utilerias as util # Módulo de utilidades: funciones varias (validaciones, colores, obtención de IP)
import alojar # Módulo para el servidor: permite crear y alojar un servidor
import tkinter as tk # Biblioteca principal de interfaz gráfica
"""Crea el frame principal del menú y lo configura"""
def crearFrame(ventana):
    frameMenu = tk.Frame(ventana, bg=util.colorFondo)

    util.label(frameMenu, "POTROCHAT", 40)

    descripcion = (
        "Este programa tiene la finalidad conectar varios dispositivos\n"
        "mediante una interfaz amigable desarrollada en Python. El usuario\n"
        "tiene la opción de elegir ser cliente (envíar mensajes) o servidor\n"
        "(alojar mensajes)."
    )
    util.label(frameMenu, descripcion, 15)

    # Cliente (TCP)
    util.boton(frameMenu, "Unirse a un servidor", 
               lambda: conectar.mostrarFrame(ventana, frameMenu))
    
    # Servidor (TCP)
    util.boton(frameMenu, "Crear un servidor", 
               lambda: alojar.mostrarFrame(ventana, frameMenu))
    
    util.boton(frameMenu, "Salir", ventana.destroy)

    util.labelIp(frameMenu)

    return frameMenu
