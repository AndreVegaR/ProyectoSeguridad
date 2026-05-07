"""
utilerias.py

Descripción:
- Funciones varias que hacen más robusto y seguro el programa
- Llamadas desde otros lugares para legibilidad de código

Funcionamiento:
- ahora(): regresa fecha y hora. Esto evita evita tener que importar datetime en cada módulo
- ip(): obtiene la IP del dispositivo mediante una conexión de prueba
- validarIp(): valida que uan IP tenga el formato Ipv4
- validaPuerto(): valida que un puerto esté dentro del rango permitido
- Guarda colores en variables que deben importarse. Eso evita tener que ponerlo en cada label, button, etc.
- Posee dif

Autores:
- Aaron Xavier Burciaga Alcantar
- Andreiy Montoya Navarro
- Abelardo Andre Vega Romero
"""

"""Importaciones"""
import socket #Para ip()
from datetime import datetime as dt #Para ahora()
import tkinter as tk #Interfaz gráfica para wrappers

"""Regresa un string con la fecha y hora"""
def ahora():
    return dt.now().strftime("%d/%m/%Y %H:%M:%S")

"""Se coneta a un servidor público de Cloudfare solo como prueba para obtener la IP"""
def ip():
    prueba = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket de prueba
    try: #Bloque try-finally para garantizar que siempre se cierre el socket
        prueba.connect(("1.1.1.1", 80))  #Servidor público
        ip = prueba.getsockname()[0] #El 0 es el primer elemento de la tupla (ip, puerto)
    finally:
        prueba.close()
    return ip 


"""Valida que una dirección esté en el formato IPv4"""
def validarIp(ip):
    numeros = ip.split(".") 
    return ( #Regresa True si se cumple lo siguiente:
            len(numeros) == 4 #Son cuatro números
            and all( 
                    num.isdigit() #Son dígitos
                    and 0 <= int(num) <= 255 #Está entre el 0 y 255
                    for num in numeros #Es la iteración en partes
                )
    )

"""Valida un puerto dentro del rango"""
def validarPuerto(puerto):
    return ( #Regresa True si se cumple lo siguiente:
        puerto.isdigit() #Son dígitos
        and 1 <= int(puerto) <= 65535 #Rango permitido
    )

"""Variables utilizadas en el programa"""
colorFondo = "grey20"
colorBotones = "grey10"
colorTexto = "white"
fuente = "Arial"
codigo = "utf-8"

"""Wrapper de un botón para así manejarlo fácilmente en otros lugares"""
def boton(ventana, #Atributo de dónde va a salir (ventana o frame)
          texto, #Texto del botón
          funcion): #Función que va a ejecutar
    btn = tk.Button(ventana, #Donde va a aparecer
                    text=texto, #Texto
                    width=20, #Anchura
                    height=3, #Altura
                    bg=colorBotones, #Color del botón
                    fg=colorTexto, #Color del texto
                    command=funcion) #Función a ejecutar
    btn.pack(pady=10) #Padding

"""Wrapper de un label para así manejarlo fácilmente en otros lugares"""
def label(ventana, texto, tamanio):
    lbl = tk.Label(ventana, #Donde va a aparecer
                   text=texto, #Texto que va a tener
                   justify="center", #Justificación
                   font=(fuente, tamanio, "bold"), #Arial en negritas
                   bg=colorFondo, 
                   fg=colorTexto) 
    lbl.pack(pady=10)

"""Wrapper de un label estandarizado que muestra la IP"""
def labelIp(ventana):
    lbl = tk.Label(ventana,
                   text=f"Dirección IP: {ip()}",
                   justify="center",
                   font=(fuente, 10, "bold"),
                   bg=colorFondo, 
                   fg=colorTexto) 
    lbl.pack(pady=30)
    return lbl

"""Wrapper para un frame que solicita información"""
def frameInfo(ventana, texto, caracteres):
    frame = tk.Frame(ventana, bg=colorFondo)
    frame.pack(pady=10)
    lbl = tk.Label(frame, text=texto, font=(fuente, 15, "bold"), bg=colorFondo, fg=colorTexto)
    lbl.pack(side="left", padx=caracteres)
    dato = tk.Entry(frame, width=caracteres)
    dato.pack(side="left", padx=caracteres)
    return dato




###
"""Métodos solo para terminal. Remover cuando se decida formalmente"""
def pedirIp():
    while True:
        servidor = input("Dirección IP del servidor: ")
        if validarIp(servidor):
            return servidor
        print("IP inválida")

def pedirPuerto():
    while True:
        puerto = input("Puerto del servidor: ")
        if validarPuerto(puerto): 
            return int(puerto)
        print("Puerto inválido") 

def pedirNombre():
    while True:
        nombre = input("Nombre de usuario (enter para usar IP): ")
        if not nombre:
            nombre = ip()
        print(f"Entraste como {nombre}")
        return nombre

def pedirNombreChat(nombreUsuario):
    while True:
        sala = input("Nombre de la sala de chat (enter para default): ")
        if not sala:
            sala = f"Sala de {nombreUsuario}"
        nombreChat = f"{sala} | Por {nombreUsuario}"
        return nombreChat
### 