"""
conectar.py

Descripción:
- Interfaz gráfica que pide nombre de usuario, ip, puerto y protocolo para después conectar con el servidor

Funcionamiento:
- Pide IP, puerto, nombre y tipo de protocolo
- Valida que IP y puerto sean válidos
- Si todo sale bien, llama al módulo chat.py con el respectivo protocolo

Autores:
- Willian Alexander Tolano Fierros
- Noelia Encinas Noriega
- Abelardo Andre Vega Romero
- Julian Gerardo Izaguirre Menchaca
"""

"""Importaciones"""
import utilerias as util # Funciones varias para validaciones y utilidades
import tkinter as tk # Interfaz gráfica
from tkinter import messagebox as mb # Ventanas con mensajes de advertencia y error
import logging

from bitacoras import(
    accesos,
    errores,
    sospechosos
)

#Variables para guardar la informacion de conexion y usuario
ip_servidor = None
puerto_servidor = None
nombre_usuario = None

#Otro Logger para debuggear en python
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s (conectar.py) - %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


"""Oculta el menú y muestra la pantalla de conectar"""
def mostrarFrame(ventana, frameMenu):
    frameMenu.pack_forget() #Esconde el frame del menu principal
    frameConectar = crearFrame(ventana, frameMenu) #Crea el frame de conexión
    frameConectar.pack(fill="both", #Se llena por altura y anchura
                       expand=True) #Crece dentro de la ventana principal


"""Regresa al menú principal"""
def regresar(frameConectar, frameMenu):
    frameConectar.pack_forget() #oculta este frame
    frameMenu.pack(fill="both", expand=True) #igual que arriba


"""Crea lo gráfico para la pantalla de conectar"""
def crearFrame(ventana, frameMenu):
    # Frame de fondo que cubre toda la ventana
    framePrincipal = tk.Frame(ventana, bg=util.colorFondo)

    # Panel tipo tarjeta centrado — mismo estilo que el menú
    panel = tk.Frame(framePrincipal, bg="#161b22")
    panel.place(relx=0.5, rely=0.5, anchor="center", width=480)

    # Barra azul superior
    tk.Frame(panel, bg="#1f6feb", height=4).pack(fill="x")

    contenido = tk.Frame(panel, bg="#161b22", padx=36, pady=28)
    contenido.pack(fill="both", expand=True)

    # Título de la pantalla
    tk.Label(
        contenido,
        text="Unirse al chat",
        font=(util.fuente, 26, "bold"),
        bg="#161b22",
        fg=util.colorTexto
    ).pack()

    # Subtítulo
    tk.Label(
        contenido,
        text="Ingresa los datos del servidor",
        font=(util.fuente, 10),
        bg="#161b22",
        fg="#58a6ff"
    ).pack(pady=(2, 14))

    # Línea separadora
    tk.Frame(contenido, bg="#30363d", height=1).pack(fill="x", pady=(0, 16))

    campoIP     = util.frameInfo(contenido, "Dirección IP del servidor", 18) # Pide IP
    campoPuerto = util.frameInfo(contenido, "Puerto del servidor", 5)         # Pide puerto
    campoNombre = util.frameInfo(contenido, "Nombre de usuario", 20)          # Pide usuario

    # Label para mostrar errores inline sin interrumpir con popups
    lbl_error = tk.Label(contenido, text="", font=(util.fuente, 10),bg="#161b22", fg="#f85149")
    lbl_error.pack(pady=(8, 0))

    """Método que maneja la ejecución cuando se presione el botón"""
    def clickConectarse():
        ip     = campoIP.get()
        puerto = campoPuerto.get()
        nombre = campoNombre.get()

        if not ip or not puerto or not nombre:

            #Registramos intento incompleto
            sospechosos.warning("Intento de conexión con campos vacíos")

            lbl_error.config(text="Llene todos los campos")
            return

        if not validar(ip, puerto):

            #Registramos intento inválido
            sospechosos.warning(
                f"Intento invalido: IP: {ip} | Puerto: {puerto}"
            )

            lbl_error.config(text="IP o puerto inválidos")
            return

        lbl_error.config(text="") # limpiamos el error si todo está bien

        global ip_servidor, puerto_servidor, nombre_usuario
        ip_servidor     = ip
        puerto_servidor = int(puerto)
        nombre_usuario  = nombre

        try:

            #Registramos intento de conexión válido
            accesos.info(
                f"{nombre_usuario} intentando conectar a {ip_servidor}:{puerto_servidor}"
            )

            import chat
            chat.iniciar_chat(
                ventana,
                ip_servidor,
                puerto_servidor,
                nombre_usuario
            )

            #Registramos conexión exitosa
            accesos.info(
                f"{nombre_usuario} conectado correctamente"
            )

        except Exception as e:

            #Registramos fallo de conexión
            errores.error(
                f"Error conectando {nombre_usuario}: {e}"
            )

            lbl_error.config(text=f"No se pudo conectar: {e}")

    util.boton(contenido, " Conectarse via TCP", clickConectarse)

    util.boton(
        contenido,
        "Regresar",
        lambda: regresar(framePrincipal, frameMenu),
        color="#21262d" # gris oscuro para diferenciarlo del botón principal
    )

    # Barra azul inferior
    tk.Frame(panel, bg="#1f6feb", height=2).pack(fill="x")

    return framePrincipal # Regresa el frame creado con todo lo gráfico


#getters para reutilizar la información de conexión en otros módulos
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
def validar(ip, puerto): #regresa verdadero si se cumple lo siguiente
    return (
        util.validarIp(ip) #IP válida
        and util.validarPuerto(puerto) #Puerto válido
    )