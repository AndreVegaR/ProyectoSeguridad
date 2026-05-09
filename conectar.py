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
import Mfa
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
    campoCorreo = util.frameInfo(framePrincipal, "Correo electrónico", 25) # Pide correo para la autenticación Multifactor
    """Método que maneja la ejecución cuando se presione el botón"""
    def clickConectarse():
        ip = campoIP.get()
        puerto = campoPuerto.get()
        nombre = campoNombre.get()
        correo= campoCorreo.get().strip()
        if not ip or not puerto or not nombre or not correo: # Uno de los cuatro campos está vacío
            mb.showwarning("Campos vacíos", "Llene los campos solicitados")
            return
        
        if not validar(ip, puerto): # Valida IP y puerto
            mb.showerror("Conexión fallida", "IP o puerto inválidos")
            return
        #Si todo sale bien debería de imprimir esto
        log.info(f"Datos válidos. Enviando código MFA a {correo}")
 
        # Se envía el código de autenticación antes de entrar al chat
        if not Mfa.enviar_codigo(correo):
            mb.showerror("Error MFA", "No se pudo enviar el código")
            return
        #Si pasa todas las validaciones se imprime este mensaje de éxito
        mb.showinfo("Código enviado", f"Se envió un código de verificación a {correo}.\n")
        
        global ip_servidor, puerto_servidor, nombre_usuario
        ip_servidor = ip
        puerto_servidor = int(puerto)
        nombre_usuario = nombre

        mostrarVerificacionMFA(ventana, framePrincipal, frameMenu, correo)
    
    util.boton(framePrincipal, f"Conectarse via TCP", clickConectarse) # Botón para validaciones, muestra el protocolo
    util.boton(framePrincipal, "Regresar", lambda: regresar(framePrincipal, frameMenu)) # Regresa al menú principal

    return framePrincipal # Regresa el frame creado con todo lo gráfico

# Getters para reutilizar la información de conexión en otros módulos

#Método que muestra la pantalla de verificación del MFA
def mostrarVerificacionMFA(ventana, frameConectar, frameMenu, correo):
    frameConectar.pack_forget() # Esconde la pantalla anterior
    frameMFA = crearFrameMFA(ventana, frameConectar, frameMenu, correo)
    frameMFA.pack(fill="both", expand=True)

#Método que crea la pantalla de la autenticación Multifactor
def crearFrameMFA(ventana, frameConectar, frameMenu, correo):
    frameMFA = tk.Frame(ventana, bg=util.colorFondo)
 
    util.label(frameMFA, "Verificación Autenticación Multifactor", 22)
    util.label(frameMFA, f"Ingresa el código enviado a:\n{correo}", 13)
 
    campoCodigo = util.frameInfo(frameMFA, "Código de 6 dígitos", 10)
 
    def clickVerificar():
        codigo_ingresado = campoCodigo.get().strip()
        log.debug(f"Verificando código ingresado para {correo}")
 
        exito, motivo = Mfa.verificar_codigo(correo, codigo_ingresado)
 
        if exito:
            log.info(f"MFA exitoso para {correo}. Abriendo chat.")
            frameMFA.pack_forget()
            try:
                import chat
                chat.iniciar_chat(ventana, ip_servidor, puerto_servidor, nombre_usuario)
                # Regresar a menú después de abrir el chat
                frameMenu.pack(fill="both", expand=True)
            except Exception as e:
                log.error(f"Error al abrir chat: {e}")
                mb.showerror("Error de conexión", f"No se pudo conectar: {e}")
                frameMenu.pack(fill="both", expand=True)
        else:
            # si falla, muestra un mensaje personalizado según el motivo del fallo
            if motivo == "expirado":
                log.warning(f"Código expirado para {correo}")
                mb.showerror("Código expirado", "El código venció.")
                frameMFA.pack_forget()
                frameMenu.pack(fill="both", expand=True)
            elif motivo == "incorrecto":
                log.warning(f"Código incorrecto para {correo}")
                mb.showerror("Código incorrecto", "El código no coincide.")
            else:
                log.error(f"Estado inesperado en verificación MFA: {motivo}")
                mb.showerror("Error", "Ocurrió un error inesperado.")
                frameMFA.pack_forget()
                frameMenu.pack(fill="both", expand=True)
 
    def clickReenviar():
        log.info(f"Reenviando código MFA a {correo}")
        if Mfa.enviar_codigo(correo):
            mb.showinfo("Código reenviado", f"Se envió un nuevo código a {correo}.")
        else:
            mb.showerror("Error", "No se pudo reenviar el código.")
 
    util.boton(frameMFA, "Verificar", clickVerificar)
    util.boton(frameMFA, "Reenviar código", clickReenviar)
 
    return frameMFA

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