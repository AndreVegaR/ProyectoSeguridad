"""
main.py

Descripción:
- Módulo de apoyo que solo guarda y muestra las diferentes pantallas (frames) del programa

Funcionamiento:
- Recibe los diferentes frames del programa y los muestra según se navegue

Autores:
- Aaron Xavier Burciaga Alcantar
- Andreiy Montoya Navarro
- Abelardo Andre Vega Romero

"""
import tkinter as tk #Interfaz gráfica
import menu #Pantalla de menú principal
import conectar #Pantalla para conectarse a un servidor
import alojar #Pantalla para crear un servidor
#import chat #Pantalla del chat
import utilerias as util #Funciones varias

ventana = tk.Tk() #Crea la ventana principal
ventana.title("Menú de servicios") #Título de la ventana
ventana.state("zoomed") #Pantalla completa
ventana.configure(bg=util.colorFondo) #Color de fondo
ventana.protocol("WM_DELETE_WINDOW", ventana.destroy) #Se puede con el botón x

frameMenu = menu.crearFrame(ventana) #Crea a la pantall de menú
frameConectar = conectar.crearFrame(ventana, frameMenu) #Crea a la pantalla para unirse a un servidor
frameAlojar = alojar.crearFrame(ventana, frameMenu) #Crea la pantalla para crear un servidor
#frameChat = chat.crearChat(ventana, frameMenu) #Crea la pantalla del chat

"""Función para mostrar un frame y ocultar el otro"""
def mostrarFrame(frameMostrar):
    for frame in (frameMenu, frameConectar, frameAlojar):
        frame.pack_forget()
    frameMostrar.pack(fill="both", expand=True)

frameMenu.mostrar = mostrarFrame #Pasa la función a los frames
frameConectar.mostrar = mostrarFrame
frameAlojar.mostrar = mostrarFrame

mostrarFrame(frameMenu) #Mostrar menú al inicio

ventana.mainloop() #Bucle para que siga abierta la ventana