"""
Chat.py
Interfaz gráfica del cliente con soporte para:
✔ TCP
✔ UDP
✔ Mensajes privados desde combobox
✔ Detección de usuarios conectados/desconectados

Autores:
- Willian Alexander Tolano Fierros
- Noelia Encinas Noriega
- Abelardo Andre Vega Romero
- Julian Gerardo Izaguirre Menchaca
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket

#Bitácoras del sistema
from bitacoras import accesos, mensajes, errores, mfa


class ClienteChat:
    """
    Maneja la lógica de red del cliente.
    Se encarga de la conexión, envío y recepción de mensajes para TCP y UDP.
    """

    def __init__(self,ip, puerto):
        self.ip = ip
        self.puerto = puerto
        self.socket = None
        self.nombre = None
        self.ejecutando = False
        self.codigo = "utf-8"

    def iniciar(self, nombre):
        """
        Inicia la conexión del cliente con el servidor.
        Realiza el handshake inicial para registrar el nombre de usuario.
        Retorna True si la conexión es exitosa, False en caso contrario.
        """
        self.nombre = nombre
        try:

            self._iniciar_tcp()

            #Registramos acceso exitoso del cliente
            accesos.info(f"{nombre} conectado a {self.ip}:{self.puerto}")

            self.ejecutando = True
            return True
        except Exception as e:

            #Registramos error de conexión
            errores.error(f"Error al iniciar cliente {nombre}: {e}")

            print(f"Error al iniciar cliente: {e}")
            return False
        
    def _iniciar_tcp(self):
        """
        Establece una conexión TCP y realiza el handshake para validar el nombre.
        Lanza una excepción si el nombre ya está en uso o si la conexión falla.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((self.ip, self.puerto))
        self.socket.settimeout(None)

        try:
            datos = self.socket.recv(1024).decode(self.codigo)
            if "nombre" in datos.lower():
                mensaje_nombre = f"dummy dummy {self.nombre}:"
                self.socket.sendall(mensaje_nombre.encode(self.codigo))

                respuesta = self.socket.recv(1024).decode(self.codigo)

                if "nombre en uso" in respuesta.lower():

                    #Registramos intento con nombre duplicado
                    accesos.warning(f"Nombre duplicado: {self.nombre}")

                    self.socket.close()
                    raise ConnectionRefusedError(respuesta)

                #el servidor pide el MFA
                if respuesta == "MFA_CORREO":
                    correo = self._pedir_correo()
                    self.socket.sendall(correo.encode(self.codigo))

                    instruccion = self.socket.recv(1024).decode(self.codigo)

                    if instruccion == "MFA_ERROR":

                        #Registramos error al enviar MFA
                        errores.error(f"No se pudo enviar MFA a {correo}")

                        self.socket.close()
                        raise ConnectionRefusedError("No se pudo enviar el código MFA.")

                    if instruccion == "MFA_CODIGO":
                        codigo = self._pedir_codigo()
                        self.socket.sendall(codigo.encode(self.codigo))

                        resultado = self.socket.recv(1024).decode(self.codigo)

                        if resultado.startswith("MFA_FALLO"):

                            #Registramos fallo MFA
                            mfa.warning(f"{self.nombre} falló autenticación")

                            motivo = resultado.split(":")[1] if ":" in resultado else "desconocido"
                            self.socket.close()
                            raise ConnectionRefusedError(f"Código MFA inválido: {motivo}")

                        else:

                            #Registramos MFA exitoso
                            mfa.info(f"{self.nombre} autenticado correctamente")

        except ConnectionRefusedError:
            raise

    #Pantalla de correo       
    def _pedir_correo(self):
        import tkinter.simpledialog as sd
        correo = sd.askstring("Verificación MFA", "Ingresa tu correo para recibir el código:")
        return correo.strip() if correo else ""

    #Pantalla de código 
    def _pedir_codigo(self):
        import tkinter.simpledialog as sd
        codigo = sd.askstring("Verificación MFA", "Ingresa el código que llegó a tu correo:")
        return codigo.strip() if codigo else ""
    
    def enviar(self, mensaje):
        """
        Envía un mensaje al servidor usando el protocolo correspondiente.
        Retorna True si el envío fue exitoso, False en caso de error.
        """
        try:
            self.socket.sendall(mensaje.encode(self.codigo))

            #Registramos mensaje enviado
            mensajes.info(f"{self.nombre}: {mensaje}")

            return True
        except Exception as e:

            #Registramos error al enviar mensaje
            errores.error(f"Error enviando mensaje: {e}")

            return False

    def bucle_recibir(self, callback):
        """
        Bucle principal que escucha constantemente los mensajes del servidor.
        """
        try:
            while self.ejecutando:
                try:
                    datos = self.socket.recv(1024)
                    if not datos:
                        break

                    mensaje = datos.decode(self.codigo)

                    if mensaje:

                        #Registramos mensaje recibido
                        mensajes.info(f"Recibido -> {mensaje}")

                        callback(mensaje)

                except Exception as e:

                    #Registramos error de recepción
                    errores.error(f"Error recibiendo mensaje: {e}")

                    break

        finally:
            self.ejecutando = False

    def cerrar(self):
        """
        Cierra el socket de red de forma segura.
        """
        self.ejecutando = False
        try:
            if self.socket:
                self.socket.close()

                #Registramos cierre de conexión
                accesos.info(f"{self.nombre} cerró conexión")

        except Exception as e:

            #Registramos error cerrando socket
            errores.error(f"Error cerrando conexión: {e}")


class VentanaChat:
    """
    Gestiona la interfaz gráfica (GUI) de la ventana de chat.
    """

    def __init__(self, ventana_principal, ip, puerto, nombre):
        self.ventana_principal = ventana_principal
        self.ip = ip
        self.puerto = puerto
        self.nombre = nombre
        self.cliente = ClienteChat(ip, puerto)

        if not self.cliente.iniciar(nombre):
            messagebox.showerror("Error", "No se pudo conectar al servidor")
            return

        self.crear_ventana()
        self.configurar_interfaz()
        self.mostrar_mensaje_sistema(f"Conectado a {ip}:{puerto}")

        threading.Thread(
            target=self.cliente.bucle_recibir,
            args=(self.manejar_mensaje_entrante,),
            daemon=True
        ).start()

    def crear_ventana(self):
        self.ventana_chat = tk.Toplevel(self.ventana_principal)
        self.ventana_chat.title(f"Chat - {self.nombre} Seguridad Informática")
        self.ventana_chat.minsize(500, 400)
        self.centrar_ventana(700, 500)
        self.ventana_chat.protocol("WM_DELETE_WINDOW", self.al_cerrar)

    def configurar_interfaz(self):

        frame_techo = tk.Frame(self.ventana_chat, bg="#85dcff", height=40)
        frame_techo.pack(side='top', fill='x', padx=5, pady=5)

        tk.Label(
            frame_techo,
            text=f"Conectado como {self.nombre}",
            bg="#85dcff",
            font=("Arial", 12)
        ).pack(pady=5)

        pie = tk.Frame(self.ventana_chat, height=50)
        pie.pack(padx=10, pady=10, side="bottom", fill="x")

        comando_privado = "/p"

        tk.Label(
            pie,
            text=f"Usa '{comando_privado} <nombre> <mensaje>' para privado"
        ).pack(side="top", anchor="w")

        self.campo_entrada = tk.Entry(pie)
        self.campo_entrada.bind("<Return>", lambda e: self.al_enviar())
        self.campo_entrada.pack(side="left", expand=True, fill="x", pady=(5,0))

        tk.Button(pie, text="Enviar", command=self.al_enviar).pack(side="right", padx=10)

        frame_mensajes = tk.Frame(self.ventana_chat, bg="#f0f0f0", bd=3, relief=tk.SUNKEN)
        frame_mensajes.pack(fill='both', expand=True, padx=10, pady=5)

        self.texto_mensajes = tk.Text(
            frame_mensajes,
            wrap=tk.WORD,
            bg="white",
            fg="black",
            state=tk.DISABLED
        )

        scrollbar = tk.Scrollbar(frame_mensajes, command=self.texto_mensajes.yview)
        self.texto_mensajes.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.texto_mensajes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def centrar_ventana(self, w, h):
        cx = (self.ventana_chat.winfo_screenwidth() // 2) - (w // 2)
        cy = (self.ventana_chat.winfo_screenheight() // 2) - (h // 2)
        self.ventana_chat.geometry(f"{w}x{h}+{cx}+{cy}")

    def al_enviar(self):

        texto = self.campo_entrada.get().strip()

        if not texto:
            return

        import utilerias as util
        paquete = f"({util.ahora()}) {self.nombre}: {texto}"

        self.cliente.enviar(paquete)

        self.campo_entrada.delete(0, tk.END)

    def manejar_mensaje_entrante(self, mensaje):
        self.ventana_chat.after(0, self._procesar_mensaje_en_ui, mensaje)

    def _procesar_mensaje_en_ui(self, texto):
        self.mostrar_mensaje_sistema(texto)

    def mostrar_mensaje_sistema(self, mensaje):
        self.mostrar_mensaje("Sistema", mensaje)

    def mostrar_mensaje(self, remitente, mensaje):
        self.texto_mensajes.config(state=tk.NORMAL)
        self.texto_mensajes.insert(tk.END, f"{remitente}: {mensaje}\n")
        self.texto_mensajes.config(state=tk.DISABLED)
        self.texto_mensajes.see(tk.END)

    def al_cerrar(self):
        try:
            self.cliente.cerrar()
        except:
            pass

        self.ventana_chat.destroy()


def iniciar_chat(ventana, ip, puerto, nombre):
    """
    Función de entrada para crear y lanzar una nueva ventana de chat.
    """
    return VentanaChat(ventana, ip, puerto, nombre)