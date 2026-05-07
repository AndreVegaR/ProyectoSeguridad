"""
menu.py

Descripción:
- Módulo principal que permite elegir el protocolo de red (TCP o UDP) antes de iniciar la acción de conectar o alojar un servidor.

Funcionamiento:
- Despliega la interfaz principal para elegir el servicio (Unirse a un servidor o Crear un servidor) y el protocolo de comunicación.
- Captura la selección del usuario y pasa el protocolo elegido ('TCP' o 'UDP') a los módulos 'conectar.py' y 'alojar.py'.

Autores:
- Aaron Xavier Burciaga Alcantar
- Andreiy Montoya Navarro
- Abelardo Andre Vega Romero
"""

"""Importaciones"""
import conectar # Módulo para el cliente: maneja la conexión a un servidor
import utilerias as util # Módulo de utilidades: funciones varias (validaciones, colores, obtención de IP)
import alojar # Módulo para el servidor: permite crear y alojar un servidor
import tkinter as tk # Biblioteca principal de interfaz gráfica
from tkinter import ttk # Necesario para usar el Combobox (lista desplegable de protocolos)

"""Crea el frame principal del menú y lo configura"""
def crearFrame(ventana):
    frameMenu = tk.Frame(ventana, bg=util.colorFondo) # Crea el contenedor principal (la pantalla) y le asigna el color de fondo

    util.label(frameMenu, "POTROCHAT", 40) # Muestra el título principal del programa

    descripcion = (
        "Este programa tiene la finalidad conectar varios dispositivos\n"
        "mediante una interfaz amigable desarrollada en Python. El usuario\n"
        "tiene la opción de elegir ser cliente (envíar mensajes) o servidor\n"
        "(alojar mensajes), así como de manejar el protocolo que desee."
    )
    util.label(frameMenu, descripcion, 15) # Muestra la descripción del programa

    # Frame contenedor para la etiqueta y el Combobox
    frameProtocolo = tk.Frame(frameMenu, bg=util.colorFondo)
    frameProtocolo.pack(pady=10)

    util.label(frameProtocolo, "Protocolo a usar:", 18)

    # Combobox de selección TCP/UDP
    protocolo = ttk.Combobox(frameProtocolo, 
                             values=["TCP", "UDP"], 
                             state="readonly", # No permite escribir texto, solo seleccionar
                             width=10)
    protocolo.current(0)  # Establece "TCP" como valor por defecto (índice 0)
    protocolo.pack(pady=5) # Muestra el Combobox

    # Botón para unirse (Cliente). Usa lambda para ejecutar la función al hacer clic.
    # Llama a 'conectar.mostrarFrame', pasando el protocolo seleccionado dinámicamente con 'protocolo.get()'.
    util.boton(frameMenu, "Unirse a un servidor", 
               lambda: conectar.mostrarFrame(ventana, frameMenu, protocolo.get()))
    
    # Botón para crear (Servidor). Llama a 'alojar.mostrarFrame', pasando el protocolo seleccionado.
    util.boton(frameMenu, "Crear un servidor", 
               lambda: alojar.mostrarFrame(ventana, frameMenu, protocolo.get()))
    
    util.boton(frameMenu, "Salir", ventana.destroy) # Cierra la ventana y sale del programa

    util.labelIp(frameMenu) # Muestra la IP local del dispositivo para referencia

    return frameMenu # Regresa el contenedor principal del menú