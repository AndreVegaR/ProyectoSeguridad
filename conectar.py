"""
conectar.py

Descripción:
- Interfaz gráfica que pide nombre de usuario, ip, puerto y protocolo para después conectar con el servidor

Funcionamiento:
- Pide IP, puerto, nombre y tipo de protocolo
- Valida que IP y puerto sean válidos
- Si todo sale bien, llama al módulo chat.py con el respectivo protocolo

Autores:
- Aaron Xavier Burciaga Alcantar
- Andreiy Montoya Navarro
- Abelardo Andre Vega Romero
"""

"""Importaciones"""
import utilerias as util # Funciones varias para validaciones y utilidades
import tkinter as tk # Interfaz gráfica
from tkinter import messagebox as mb # Ventanas con mensajes de advertencia y error
import logging

# Variables de estado para compartir la conexión con otros módulos
ip_servidor = None
puerto_servidor = None
nombre_usuario = None

#Otro Logger para debuggear en python....
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s (conectar.py) - %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


"""Oculta el menú y muestra la pantalla de conectar"""
def mostrarFrame(ventana, frameMenu):
    frameMenu.pack_forget() # Esconde el frame del menú principal
    frameConectar = crearFrame(ventana, frameMenu) # Crea el frame de conexión
    frameConectar.pack(fill="both", # Se llena tanto por altura y anchura
                       expand=True) # Crece dentro de la ventana principal

"""Regresa al menú principal"""
def regresar(frameConectar, frameMenu):
    frameConectar.pack_forget() # Oculta este frame
    frameMenu.pack(fill="both", expand=True) # El frame del menú se llena por ambos ejes y crece

"""Crea lo gráfico para la pantalla de conectar"""
def crearFrame(ventana, frameMenu):
    framePrincipal = tk.Frame(ventana, bg=util.colorFondo) # Crea el frame

    # Mostrar imagen del proyecto
    try:
        img_tk = tk.PhotoImage(file="potros-itson.png")
        lbl_img = tk.Label(framePrincipal, image=img_tk, bg=util.colorFondo)
        lbl_img.image = img_tk
        lbl_img.pack(pady=8)
    except Exception:
        pass

    # Mostrar protocolo seleccionado
    util.label(framePrincipal, f"Conectarse a servidor", 18)

    campoIP = util.frameInfo(framePrincipal, "Dirección IP del servidor", 18) # Pide IP
    campoPuerto = util.frameInfo(framePrincipal, "Puerto del servidor", 5) # Pide puerto
    campoNombre = util.frameInfo(framePrincipal, "Nombre de usuario", 20) # Pide usuario
    """Método que maneja la ejecución cuando se presione el botón"""
    
    def clickConectarse():
        ip = campoIP.get()
        puerto = campoPuerto.get()
        nombre = campoNombre.get()

        if not ip or not puerto or not nombre:
            mb.showwarning("Campos vacíos", "Llene los campos solicitados")
            return

        if not validar(ip, puerto):
            mb.showerror("Conexión fallida", "IP o puerto inválidos")
            return

        global ip_servidor, puerto_servidor, nombre_usuario
        ip_servidor = ip
        puerto_servidor = int(puerto)
        nombre_usuario = nombre

        try:
            import chat
            chat.iniciar_chat(ventana, ip_servidor, puerto_servidor, nombre_usuario)
        except Exception as e:
            mb.showerror("Error de conexión", f"No se pudo conectar: {e}")

    util.boton(framePrincipal, f"Conectarse via TCP", clickConectarse) # Botón para validaciones, muestra el protocolo
    util.boton(framePrincipal, "Regresar", lambda: regresar(framePrincipal, frameMenu)) # Regresa al menú principal

    return framePrincipal # Regresa el frame creado con todo lo gráfico

# Getters para reutilizar la información de conexión en otros módulos


def obtener_ip_servidor():
    """Regresa la IP del servidor proporcionada en la conexión"""
    return ip_servidor

def obtener_puerto_servidor():
    """Regresa el puerto del servidor proporcionada en la conexión"""
    return puerto_servidor

def obtener_nombre_usuario():
    """Regresa el nombre de usuario proporcionado en la conexión"""
    return nombre_usuario


"""Método que valida la información proporcionada"""
def validar(ip, puerto): # Regresa verdadero si se cumple lo siguiente
    return (util.validarIp(ip) # IP válida
    and util.validarPuerto(puerto)) # Puerto válido