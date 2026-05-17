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

"""Importaciones"""
import conectar # Módulo para el cliente: maneja la conexión a un servidor
import utilerias as util # Módulo de utilidades: funciones varias (validaciones, colores, obtención de IP)
import alojar # Módulo para el servidor: permite crear y alojar un servidor
import tkinter as tk # Biblioteca principal de interfaz gráfica
 
"""Crea el frame principal del menú y lo configura"""
def crearFrame(ventana):
    # Frame de fondo que cubre toda la ventana
    frameFondo = tk.Frame(ventana, bg=util.colorFondo)
 
    # Panel tipo tarjeta centrado — ancho calculado para que quepan las líneas de texto
    frameMenu = tk.Frame(frameFondo, bg="#161b22")
    frameMenu.place(relx=0.5, rely=0.5, anchor="center", width=700)
 
    tk.Frame(frameMenu, bg="#1f6feb", height=4).pack(fill="x")
 
    util.label(frameMenu, "POTROCHAT", 40)
 
    # Subtítulo ITSON
    tk.Label(
        frameMenu,
        text="ITSON  ·  Seguridad Informática",
        font=(util.fuente, 10),
        bg="#161b22",
        fg="#58a6ff",
        justify="center"
    ).pack(pady=(0, 8))
 
    # mensaje muy normalito pero se los voy a dejar pasar
    # sin wraplength para que respete los \n y no parta palabras
    descripcion = (
        "Este programa tiene la finalidad conectar varios dispositivos\n"
        "mediante una interfaz amigable desarrollada en Python. El usuario\n"
        "tiene la opción de elegir ser cliente (envíar mensajes) o servidor\n"
        "(alojar mensajes)."
    )
    tk.Label(
        frameMenu,
        text=descripcion,
        font=(util.fuente, 12, "bold"),
        bg="#161b22",
        fg=util.colorTexto,
        justify="center"
    ).pack(pady=10)
 
    # Cliente (TCP)
    util.boton(frameMenu, "Unirse a un servidor",
               lambda: conectar.mostrarFrame(ventana, frameFondo))
 
    # Servidor (TCP)
    util.boton(frameMenu, "Crear un servidor",
               lambda: alojar.mostrarFrame(ventana, frameFondo))
 
    # Salir en rojo
    util.boton(frameMenu, "Salir", ventana.destroy, color="#6e1c1c")
 
    # IP visible
    tk.Label(
        frameMenu,
        text=f"Dirección IP: {util.ip()}",
        font=(util.fuente, 12, "bold"),
        bg="#161b22",
        fg="#58a6ff",
        justify="center"
    ).pack(pady=(16, 12))
 
    tk.Frame(frameMenu, bg="#1f6feb", height=2).pack(fill="x")
 
    return frameFondo