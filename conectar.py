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
    framePrincipal = tk.Frame(ventana, bg=util.colorFondo) #crea el frame

    # Mostrar imagen del proyecto
    try:
        img_tk = tk.PhotoImage(file="potros-itson.png")
        lbl_img = tk.Label(framePrincipal, image=img_tk, bg=util.colorFondo)
        lbl_img.image = img_tk
        lbl_img.pack(pady=8)
    except Exception as e:

        #Registramos error cargando imagen
        errores.error(f"Error cargando imagen principal: {e}")

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

            #Registramos intento incompleto
            sospechosos.warning("Intento de conexión con campos vacíos")

            mb.showwarning("Campos vacíos", "Llene los campos solicitados")
            return

        if not validar(ip, puerto):

            #Registramos intento inválido
            sospechosos.warning(
                f"Intento inválido -> IP: {ip} | Puerto: {puerto}"
            )

            mb.showerror("Conexión fallida", "IP o puerto inválidos")
            return

        global ip_servidor, puerto_servidor, nombre_usuario
        ip_servidor = ip
        puerto_servidor = int(puerto)
        nombre_usuario = nombre

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

            mb.showerror(
                "Error de conexión",
                f"No se pudo conectar: {e}"
            )

    util.boton(
        framePrincipal,
        f"Conectarse via TCP",
        clickConectarse
    )

    util.boton(
        framePrincipal,
        "Regresar",
        lambda: regresar(framePrincipal, frameMenu)
    )

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