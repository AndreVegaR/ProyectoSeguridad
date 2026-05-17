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
- Willian Alexander Tolano Fierros
- Noelia Encinas Noriega
- Abelardo Andre Vega Romero
- Julian Gerardo Izaguirre Menchaca
"""

"""Importaciones"""
import socket #Para ip()
from datetime import datetime as dt #Para ahora()
import tkinter as tk #Interfaz gráfica para wrappers
import re
import hashlib
import os

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
colorFondo = "#0d1117"
colorBotones = "#1f6feb"
colorTexto = "#e6edf3"
fuente = "Courier New"
codigo = "utf-8"

"""Wrapper de un botón con diseño mejorado patrocinado"""
def boton(ventana, texto, funcion, color=None):
    c = color if color else colorBotones
    btn = tk.Button(
        ventana,
        text=texto,
        width=22,
        height=2,
        bg=c,
        fg="#ffffff",
        font=(fuente, 12, "bold"),
        relief="flat",
        cursor="hand2",
        activebackground="#388bfd",
        activeforeground="#ffffff",
        command=funcion
    )
    btn.pack(pady=8, ipadx=4)
    # Hover effect
    btn.bind("<Enter>", lambda e: btn.config(bg="#388bfd"))
    btn.bind("<Leave>", lambda e: btn.config(bg=c))

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
def frameInfo(ventana, texto, caracteres, ocultar=False):
    frame = tk.Frame(ventana, bg="#161b22")
    frame.pack(pady=8, padx=40, fill="x")
    lbl = tk.Label(frame, text=texto, font=(fuente, 10), bg="#161b22", fg="#8b949e", anchor="w")
    lbl.pack(fill="x", pady=(0, 4))
    show = "*" if ocultar else ""
    # Contenedor con borde visible para que se note el campo
    borde = tk.Frame(frame, bg="#30363d", padx=1, pady=1)
    borde.pack(fill="x")
    dato = tk.Entry(
        borde,
        width=max(caracteres, 28),
        font=(fuente, 12),
        bg="#0d1117",
        fg=colorTexto,
        insertbackground=colorTexto,
        relief="flat",
        bd=6,
        show=show
    )
    dato.pack(fill="x")
    # Resalta el borde al hacer foco en el campo
    dato.bind("<FocusIn>",  lambda e: borde.config(bg="#1f6feb"))
    dato.bind("<FocusOut>", lambda e: borde.config(bg="#30363d"))
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

# voy aplicar la sanitización para el proyecto
# Caracteres permitidos en mensajes
_PATRON_SEGURO = re.compile(r"[^\w\s.,;:!?¿¡()\-@#/\"'áéíóúÁÉÍÓÚñÑüÜ]", re.UNICODE)
# Longitud maxima de un mensaje
LONGITUD_MAX_MENSAJE = 200
# Caracteres permitidos en nombres de usuario
_PATRON_NOMBRE = re.compile(r"[^\w\-]", re.UNICODE)
LONGITUD_MAX_NOMBRE = 20

def sanitizar(texto):
    """
    Limpia un mensaje elimina caracteres potencialmente peligrosos y 
    trunca si excede el limite todavia recuerdo el ultimo examen del profe carlos soy bueno
    Regresa el texto limpio, o cadena vacia si queda vacio tras la limpieza.
    """
    if not isinstance(texto, str):
        return ""
    texto = texto.strip()
    texto = _PATRON_SEGURO.sub("", texto)# quita caracteres no permitidos
    texto = texto[:LONGITUD_MAX_MENSAJE]# trunca si es muy largo
    return texto

def sanitizar_nombre(nombre):
    """
    Limpia un nombre de usuario deberia poner algun nombre prohibido 
    como Willian Tolano porque eso seria como un trolano
    Regresa el nombre limpio, o cadena vacía si queda vacio
    """
    if not isinstance(nombre, str):
        return ""
    nombre = nombre.strip()
    nombre = _PATRON_NOMBRE.sub("", nombre)
    nombre = nombre[:LONGITUD_MAX_NOMBRE]
    return nombre

def validar_nombre(nombre):
    """Verificamos que el nombre tenga entre 1 y 20 caracteres permitidos"""
    limpio = sanitizar_nombre(nombre)
    return len(limpio) >= 1

# aplicacion especial de hasheos Julián
# Archivo donde se guardan usuarios y sus contraseñas hasheadas
ARCHIVO_USUARIOS = "usuarios.dat"
def _hashear(contrasena, sal=None):
    """
    Genera un hash SHA-256 con sal de la contraseña.
    Si no se provee sal, genera una aleatoria de 16 bytes.
    Regresa (sal_hex, hash_hex).
    y pues la sal es un valor aleatorio que se agrega a la contraseña antes de hashearla
    """
    if sal is None:
        sal = os.urandom(16)
    else:
        sal = bytes.fromhex(sal)
    h = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), sal, 310_000)
    return sal.hex(), h.hex()

def registrar_usuario(nombre, contrasena):
    """
    Guarda el usuario con contraseña hasheada en el archivo de usuarios.
    Regresa True si se registro, False si el usuario ya existe.
    """
    nombre = sanitizar_nombre(nombre)
    if not nombre:
        return False
    usuarios = _cargar_usuarios()
    if nombre in usuarios:
        return False  # usuario ya existe
    sal, h = _hashear(contrasena)
    usuarios[nombre] = f"{sal}:{h}"
    _guardar_usuarios(usuarios)
    return True

def verificar_contrasena(nombre, contrasena):
    """
    Verifica si la contraseña del usuario es correcta.
    Regresa True si coincide, False en caso contrario.
    """
    usuarios = _cargar_usuarios()
    if nombre not in usuarios:
        return False
    sal, h_guardado = usuarios[nombre].split(":", 1)
    _, h_ingresado = _hashear(contrasena, sal)
    return h_ingresado == h_guardado

def usuario_existe(nombre):
    """Verifica si el nombre de usuario ya está registrado."""
    return nombre in _cargar_usuarios()

def _cargar_usuarios():
    """Carga el diccionario {nombre: sal:hash} desde el archivo."""
    usuarios = {}
    if not os.path.exists(ARCHIVO_USUARIOS):
        return usuarios
    with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if "=" in linea:
                nombre, valor = linea.split("=", 1)
                usuarios[nombre.strip()] = valor.strip()
    return usuarios

def _guardar_usuarios(usuarios):
    """Guarda el diccionario de usuarios en el archivo."""
    with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
        for nombre, valor in usuarios.items():
            f.write(f"{nombre}={valor}\n")