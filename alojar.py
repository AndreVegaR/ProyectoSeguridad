"""
alojar.py

Descripción:
- Interfaz gráfica para crear/alojar un servidor

Autores:
- Willian Alexander Tolano Fierros
- Noelia Encinas Noriega
- Abelardo Andre Vega Romero
- Julian Gerardo Izaguirre Menchaca
"""

"""Importaciones"""
import servidorTCP
import utilerias as util
import tkinter as tk
from tkinter import messagebox as mb
import threading

from bitacoras import servidor, errores, sospechosos


""" Verificación del protocolo: regresa la función iniciar según TCP/UDP """
def verificacionProtocolo(protocolo):
    global protocolo_servidor
    protocolo_servidor = "TCP"
    return servidorTCP.iniciar


"""Oculta el menú y muestra esta pantalla"""
def mostrarFrame(ventana, frameMenu):
    frameMenu.pack_forget()
    frameAlojar = crearFrame(ventana, frameMenu)
    frameAlojar.pack(fill="both", expand=True)


"""Regresa al menú principal"""
def regresar(frameAlojar, frameMenu):
    frameAlojar.pack_forget()
    frameMenu.pack(fill="both", expand=True)


def crearFrame(ventana, frameMenu):
    framePrincipal = tk.Frame(ventana, bg=util.colorFondo)
    
    # Mostrar protocolo seleccionado
    util.label(framePrincipal, f"Crear servidor - Seguridad informática", 18)
    
    campoServidor = util.frameInfo(framePrincipal, "Nombre del servidor", 20)
    campoAnfitrion = util.frameInfo(framePrincipal, "Anfitrión", 15)
    campoPuerto = util.frameInfo(framePrincipal, "Puerto del servidor", 5)
    
    def clickAlojar():
        servidor_nombre = campoServidor.get()
        puerto = campoPuerto.get()
        anfitrion = campoAnfitrion.get()

        if not servidor_nombre or not puerto:

            #registramos intento incompleto
            sospechosos.warning("Intento de alojar servidor con campos vacíos")

            mb.showwarning(
                "Campos vacíos",
                "Llene los campos solicitados"
            )
            return

        if util.validarPuerto(puerto):
            try:
                hilo_servidor = threading.Thread(
                    target=lambda: servidorTCP.iniciar(int(puerto)),
                    daemon=True
                )
                hilo_servidor.start()

                #registramos inicio del servidor
                servidor.info(
                    f"Servidor '{servidor_nombre}' iniciado en puerto {puerto} por {anfitrion}"
                )

                mb.showinfo(
                    "Servidor iniciado",
                    f"Servidor TCP iniciado en puerto {puerto}\n"
                    f"Anfitrión: {anfitrion}"
                )

            except OSError as e:

                #registramos error de puerto
                errores.error(f"Error puerto {puerto}: {e}")

                if e.errno in (48, 98):
                    mb.showerror(
                        "Error",
                        f"El puerto {puerto} ya está en uso."
                    )
                else:
                    mb.showerror(
                        "Error",
                        f"No se pudo iniciar el servidor:\n{e}"
                    )

            except Exception as e:

                #registramos error inesperado
                errores.error(str(e))

                mb.showerror(
                    "Error inesperado",
                    str(e)
                )

            return

        #registramos puerto inválido
        sospechosos.warning(f"Intento de alojar con puerto inválido: {puerto}")

        mb.showerror(
            "Error",
            "Puerto inválido"
        )

    util.boton(framePrincipal, f"Alojar servidor", clickAlojar)
    util.boton(framePrincipal, "Regresar", lambda: regresar(framePrincipal, frameMenu))

    return framePrincipal