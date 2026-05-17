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


"""Crea lo gráfico para la pantalla de alojar servidor"""
def crearFrame(ventana, frameMenu):
    # Frame de fondo que cubre toda la ventana
    framePrincipal = tk.Frame(ventana, bg=util.colorFondo)

    # Panel tipo tarjeta centrado — acento verde porque es el lado servidor
    panel = tk.Frame(framePrincipal, bg="#161b22")
    panel.place(relx=0.5, rely=0.5, anchor="center", width=480)

    # Barra verde superior (verde = servidor, azul = cliente)
    tk.Frame(panel, bg="#238636", height=4).pack(fill="x")

    contenido = tk.Frame(panel, bg="#161b22", padx=36, pady=28)
    contenido.pack(fill="both", expand=True)

    # Título de la pantalla
    tk.Label(
        contenido,
        text="Crear servidor",
        font=(util.fuente, 26, "bold"),
        bg="#161b22",
        fg=util.colorTexto
    ).pack()

    # Subtítulo
    tk.Label(
        contenido,
        text="Configura y lanza tu servidor TCP",
        font=(util.fuente, 10),
        bg="#161b22",
        fg="#3fb950" # verde para que combine con la barra superior
    ).pack(pady=(2, 14))

    # Línea separadora
    tk.Frame(contenido, bg="#30363d", height=1).pack(fill="x", pady=(0, 16))

    campoServidor  = util.frameInfo(contenido, "Nombre del servidor", 20)
    campoAnfitrion = util.frameInfo(contenido, "Anfitrión", 15)
    campoPuerto    = util.frameInfo(contenido, "Puerto del servidor", 5)

    # Label para mostrar errores inline sin interrumpir con popups
    lbl_error = tk.Label(contenido, text="", font=(util.fuente, 10), bg="#161b22", fg="#f85149", wraplength=400)
    lbl_error.pack(pady=(8, 0))

    def clickAlojar():
        servidor_nombre = campoServidor.get()
        puerto          = campoPuerto.get()
        anfitrion       = campoAnfitrion.get()

        if not servidor_nombre or not puerto:

            #registramos intento incompleto
            sospechosos.warning("Intento de alojar servidor con campos vacios")

            lbl_error.config(text="Nombre del servidor y puerto son obligatorios no te hagas pato")
            return

        if util.validarPuerto(puerto):
            lbl_error.config(text="") # limpiamos el error si todo está bien
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
                    lbl_error.config(text=f"El puerto {puerto} ya está en uso BRO")
                else:
                    lbl_error.config(text=f"No se pudo iniciar el servidor: {e}")

            except Exception as e:

                #registramos error inesperado
                errores.error(str(e))

                lbl_error.config(text=f"Error inesperado: {e}")

            return

        #registramos puerto inválido
        sospechosos.warning(f"Intento de alojar con puerto invalido: {puerto}")

        lbl_error.config(text="Puerto invalido")

    util.boton(contenido, "Alojar servidor", clickAlojar, color="#1a7f37")

    util.boton(
        contenido,
        "Regresar",
        lambda: regresar(framePrincipal, frameMenu),
        color="#21262d" # gris oscuro para diferenciarlo del botón principal
    )

    # Barra verde inferior
    tk.Frame(panel, bg="#238636", height=2).pack(fill="x")

    return framePrincipal