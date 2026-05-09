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

frameMenu.pack(fill="both", expand=True)

ventana.mainloop() #Bucle para que siga abierta la ventana