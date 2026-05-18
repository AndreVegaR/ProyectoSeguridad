"""
Chat.py
Interfaz grafica del cliente con soporte para:
TCP
Mensajes privados con /p nombre mensaje
Deteccion de usuarios conectados/desconectados
Sanitizacion de entrada antes de enviar al servidor

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
import utilerias as util
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import struct
#Bitacoras del sistema
from bitacoras import accesos, mensajes, errores, mfa


class ClienteChat:
    """
    Maneja la logica de red del cliente.
    Se encarga de la conexion, envio y recepcion de mensajes para TCP.
    """

    def __init__(self, ip, puerto):
        self.ip = ip
        self.puerto = puerto
        self.socket = None
        self.nombre = None
        self.ejecutando = False
        self.codigo = "utf-8"
        self._clave_publica = None  # Se recibe del servidor al conectar

    def _cifrar(self, texto):
        """Cifra un string con la clave publica RSA del servidor."""
        return self._clave_publica.encrypt(
            texto.encode(self.codigo),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    def _recibir_exactamente(self, cantidad):
        datos = b""

        while len(datos) < cantidad:
            parte = self.socket.recv(cantidad - len(datos))

            if not parte:
                raise ConnectionError("Conexión cerrada mientras se recibían datos.")

            datos += parte

        return datos
    
    def iniciar(self, nombre):
        """
        Inicia la conexion del cliente con el servidor.
        Realiza el handshake inicial para registrar el nombre de usuario.
        Retorna True si la conexion es exitosa, False en caso contrario.
        """
        self.nombre = nombre
        try:

            self._iniciar_tcp()

            #Registramos acceso exitoso del cliente
            accesos.info(f"{nombre} conectado a {self.ip}:{self.puerto}")

            self.ejecutando = True
            return True
        except Exception as e:
            errores.error(f"Error al iniciar cliente {nombre}: {e}")

            try:
                if self.socket:
                    self.socket.close()
            except:
                pass

            print(f"Error al iniciar cliente: {e}")
            return False

    def _iniciar_tcp(self):
        """
        Establece una conexion TCP y realiza el handshake para validar el nombre.
        Lanza una excepcion si el nombre ya esta en uso o si la conexion falla.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((self.ip, self.puerto))
        

        try:
            # Primero recibimos la clave publica RSA del servidor (viene en PEM, ~450 bytes)
            tamano_bytes = self._recibir_exactamente(4)
            tamano = struct.unpack("!I", tamano_bytes)[0]

            pem = self._recibir_exactamente(tamano)
            self._clave_publica = serialization.load_pem_public_key(pem)

            datos = self.socket.recv(1024).decode(self.codigo)
            if "nombre" in datos.lower():
                mensaje_nombre = f"dummy dummy {self.nombre}:"
                self.socket.sendall(self._cifrar(mensaje_nombre))

                respuesta = self.socket.recv(1024).decode(self.codigo)

                if "nombre en uso" in respuesta.lower() or "invalido" in respuesta.lower():

                    #Registramos intento con nombre duplicado o invalido
                    accesos.warning(f"Nombre rechazado por el servidor: {self.nombre}")

                    self.socket.close()
                    raise ConnectionRefusedError(respuesta)

                #el servidor pide el MFA
                if respuesta == "MFA_CORREO":
                    correo = self._pedir_correo()

                    if not correo:
                        self.socket.close()
                        raise ConnectionRefusedError("Debes ingresar un correo para MFA.")

                    self.socket.sendall(self._cifrar(correo))

                    instruccion = self.socket.recv(1024).decode(self.codigo)

                    if instruccion == "MFA_ERROR":
                        errores.error(f"No se pudo enviar MFA a {correo}")
                        self.socket.close()
                        raise ConnectionRefusedError("No se pudo enviar el codigo MFA.")

                    if instruccion != "MFA_CODIGO":
                        self.socket.close()
                        raise ConnectionRefusedError(f"Respuesta inesperada del servidor: {instruccion}")

                    codigo = self._pedir_codigo()

                    if not codigo:
                        self.socket.close()
                        raise ConnectionRefusedError("Debes ingresar el codigo MFA.")

                    self.socket.sendall(self._cifrar(codigo))

                    resultado = self.socket.recv(1024).decode(self.codigo)

                    if resultado.startswith("MFA_FALLO"):
                        mfa.warning(f"{self.nombre} fallo autenticacion")

                        motivo = resultado.split(":", 1)[1] if ":" in resultado else "desconocido"
                        self.socket.close()
                        raise ConnectionRefusedError(f"Codigo MFA invalido: {motivo}")

                    mfa.info(f"{self.nombre} autenticado correctamente")
                self.socket.settimeout(None)
        except ConnectionRefusedError:
            raise

    #Pantalla de correo
    def _pedir_correo(self):
        import tkinter.simpledialog as sd
        correo = sd.askstring("Verificacion MFA", "Ingresa tu correo para recibir el codigo:")
        return correo.strip() if correo else ""

    #Pantalla de codigo
    def _pedir_codigo(self):
        import tkinter.simpledialog as sd
        codigo = sd.askstring("Verificacion MFA", "Ingresa el codigo que llego a tu correo:")
        return codigo.strip() if codigo else ""

    def enviar(self, mensaje):
        """
        Envia un mensaje al servidor.
        Retorna True si el envio fue exitoso, False en caso de error.
        """
        try:
            self.socket.sendall(self._cifrar(mensaje))

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

                    #Registramos error de recepcion
                    errores.error(f"Error recibiendo mensaje: {e}")

                    break

        finally:
            self.ejecutando = False

    def cerrar(self):
        """
        Cierra el socket de red de forma segura.
        """
        self.ejecutando = False

        sock = self.socket
        self.socket = None

        try:
            if sock:
                try:
                    sock.settimeout(1)

                    despedida = f"({__import__('utilerias').ahora()}) {self.nombre}: __SALIR__"
                    sock.sendall(self._cifrar(despedida))

                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except Exception:
                        pass

                except Exception:
                    pass

                finally:
                    try:
                        sock.close()
                    except Exception:
                        pass

                accesos.info(f"{self.nombre} cerro conexion")
        except Exception as e:
            errores.error(f"Error cerrando conexion: {e}")


class VentanaChat:
    """
    Gestiona la interfaz grafica de la ventana de chat.
    """

    def __init__(self, ventana_principal, ip, puerto, nombre):
        self.ventana_principal = ventana_principal
        self.ip = ip
        self.puerto = puerto
        self.nombre = nombre
        self.cliente = ClienteChat(ip, puerto)

        if not self.cliente.iniciar(nombre):
            messagebox.showerror("Error", "No se pudo conectar al servidor")
            raise ConnectionError("No se pudo conectar al servidor")

        self.crear_ventana()
        self.configurar_interfaz()
        self.mostrar_mensaje_sistema(f"Conectado a {ip}:{puerto}")

        threading.Thread(
            target=self.cliente.bucle_recibir,
            args=(self.manejar_mensaje_entrante,),
            daemon=True
        ).start()
        self.segundos_inactividad = 0
        self.limite_inactividad = 60  # 1 minuto
        self.monitor_id = None # Referencia para cancelar/reiniciar el ciclo
        self.iniciar_monitoreo_inactividad() # Inicia el contador

    def iniciar_monitoreo_inactividad(self):
        """Incrementa el contador cada segundo y verifica si supero el limite."""
        self.segundos_inactividad += 1

        if self.segundos_inactividad >= self.limite_inactividad:
            self.cerrar_por_inactividad()
        else:
            # Vuelve a llamar a esta funcion en 1000ms (1 segundo)
            self.monitor_id = self.ventana_chat.after(1000, self.iniciar_monitoreo_inactividad)

    def reiniciar_cronometro(self, evento=None):
        """Pone el contador a cero cada vez que el usuario interactua."""
        self.segundos_inactividad = 0

    def cerrar_por_inactividad(self):
        """Cierra la conexion y la ventana informando al usuario."""
        messagebox.showwarning("Sesion expirada", "Se ha cerrado la sesion por 1 minuto de inactividad.")
        self.al_cerrar() # Reutiliza la funcion de cierre seguro

    def crear_ventana(self):
        self.ventana_chat = tk.Toplevel(self.ventana_principal)
        self.ventana_chat.title(f"Chat - {self.nombre} Seguridad Informatica")
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

        # Detectar cualquier tecla o clic en la ventana de chat
        self.ventana_chat.bind_all("<Any-KeyPress>", self.reiniciar_cronometro)
        self.ventana_chat.bind_all("<Button-1>", self.reiniciar_cronometro)

        pie = tk.Frame(self.ventana_chat, height=50)
        pie.pack(padx=10, pady=10, side="bottom", fill="x")

        comando_privado = "/p"

        tk.Label(
            pie,
            text=f"Usa '{comando_privado} <nombre> <mensaje>' para privado"
        ).pack(side="top", anchor="w")

        self.campo_entrada = tk.Entry(pie)
        self.campo_entrada.bind("<Return>", lambda e: self.al_enviar())
        self.campo_entrada.pack(side="left", expand=True, fill="x", pady=(5, 0))

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

        self.reiniciar_cronometro()

        comando_privado_tcp = "/p "

        if texto.startswith(comando_privado_tcp):
            # Si es un mensaje privado separamos destinatario y cuerpo
            # formato esperado: /p destinatario cuerpo del mensaje
            partes_privado = texto.split(" ", 2)

            if len(partes_privado) < 3:
                self.mostrar_mensaje_sistema("Formato correcto: /p nombre mensaje")
                return

            #sanitizamos el nombre del destinatario antes de mandarlo
            destinatario = util.sanitizar_nombre(partes_privado[1])
            if not util.validar_nombre(destinatario):
                self.mostrar_mensaje_sistema("El nombre del destinatario no es valido.")
                return

            #sanitizamos el cuerpo del mensaje privado
            cuerpo = util.sanitizar(partes_privado[2])
            if not cuerpo:
                self.mostrar_mensaje_sistema("El mensaje privado no puede estar vacio.")
                return

            paquete = f"({util.ahora()}) {self.nombre}: /p {destinatario} {cuerpo}"

        else:
            # Si es un mensaje publico sanitizamos el texto antes de armarlo
            # antes de este fix paquete nunca se asignaba para mensajes publicos
            # y causaba NameError o mandaba el paquete del mensaje anterior
            cuerpo = util.sanitizar(texto)
            if not cuerpo:
                self.mostrar_mensaje_sistema("El mensaje contiene solo caracteres no permitidos.")
                return

            paquete = f"({util.ahora()}) {self.nombre}: {cuerpo}"

        if not self.cliente.enviar(paquete):
            self.mostrar_mensaje_sistema("No se pudo enviar el mensaje.")

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
        """
        Se ejecuta cuando el usuario cierra la ventana de chat.
        Se asegura de cerrar la conexion de red antes de destruir la ventana.
        """
        if self.monitor_id:
            try:
                self.ventana_chat.after_cancel(self.monitor_id)
            except:
                pass
        try:
            self.cliente.cerrar()
        except:
            pass
        self.ventana_chat.destroy()


def iniciar_chat(ventana, ip, puerto, nombre):
    """
    Funcion de entrada para crear y lanzar una nueva ventana de chat.
    """
    return VentanaChat(ventana, ip, puerto, nombre)