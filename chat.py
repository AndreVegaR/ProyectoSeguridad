"""
Chat.py
Interfaz gráfica del cliente con soporte para:
✔ TCP
✔ UDP
✔ Mensajes privados desde combobox
✔ Detección de usuarios conectados/desconectados

Autores:
- Aaron Xavier Burciaga Alcantar
- Andreiy Montoya Navarro
- Abelardo Andre Vega Romero
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket

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

            self.ejecutando = True
            return True
        except Exception as e:
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
                #self.socket.sendall(self.nombre.encode(self.codigo))
                # El servidor TCP espera un formato específico: "(fecha) nombre: mensaje"
                # Para que el servidor pueda extraer el nombre, simulamos ese formato.
                mensaje_nombre = f"dummy dummy {self.nombre}:"
                self.socket.sendall(mensaje_nombre.encode(self.codigo))

                # Esperamos la respuesta del servidor para saber si el nombre fue aceptado.
                respuesta_servidor = self.socket.recv(1024).decode(self.codigo)
                if "nombre en uso" in respuesta_servidor.lower():
                    self.socket.close()
                    # Lanzamos una excepción para que sea capturada y mostrada al usuario.
                    raise ConnectionRefusedError(respuesta_servidor)
        except ConnectionRefusedError:
            raise # Re-lanzamos solo si el nombre está en uso
    def enviar(self, mensaje):
        """
        Envía un mensaje al servidor usando el protocolo correspondiente.
        Retorna True si el envío fue exitoso, False en caso de error.
        """
        try:
            self.socket.sendall(mensaje.encode(self.codigo))
            return True
        except:
            return False

    def bucle_recibir(self, callback):
        """
        Bucle principal que escucha constantemente los mensajes del servidor.
        Cuando recibe un mensaje, lo decodifica y lo pasa a la función
        'callback' para que sea procesado por la interfaz de usuario.
        """
        try:
            while self.ejecutando:
                try:
                    datos = self.socket.recv(1024)
                    if not datos:
                        break
                    mensaje = datos.decode(self.codigo)
                    if mensaje:
                        callback(mensaje)
                except:
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
        except:
            pass


class VentanaChat:
    """
    Gestiona la interfaz gráfica (GUI) de la ventana de chat.
    Se encarga de mostrar mensajes y manejar la interacción del usuario.
    """
    def __init__(self, ventana_principal, ip, puerto, nombre):
        self.ventana_principal = ventana_principal
        self.ip = ip
        self.puerto = puerto
        self.nombre = nombre

        self.crear_ventana()
        self.configurar_interfaz()

        if not self.iniciar_cliente():
            return

    def crear_ventana(self):
        """
        Crea y configura la ventana Toplevel para el chat.
        """
        self.ventana_chat = tk.Toplevel(self.ventana_principal)
        self.ventana_chat.title(f"Chat - {self.nombre} Seguridad Informática")
        self.ventana_chat.minsize(500, 400)
        self.centrar_ventana(700, 500)
        self.ventana_chat.protocol("WM_DELETE_WINDOW", self.al_cerrar)

    def configurar_interfaz(self):
        """
        Construye y posiciona todos los widgets (botones, etiquetas, etc.) en la ventana de chat.
        """
        # --- Frame Superior (Techo) ---
        frame_techo = tk.Frame(self.ventana_chat, bg="#85dcff", height=40)
        frame_techo.pack(side='top', fill='x', padx=5, pady=5)
        tk.Label(
            frame_techo,
            text=f"Conectado como {self.nombre}",
            bg="#85dcff",
            font=("Arial", 12)
        ).pack(pady=5)

       
        # Contiene los controles para enviar mensajes
        pie = tk.Frame(self.ventana_chat, height=50)
        pie.pack(padx=10, pady=10, side="bottom", fill="x")

        # Instrucción para mensajes privados
        comando_privado = "/p"
        tk.Label(pie, text=f"Usa '{comando_privado} <nombre> <mensaje>' para privado").pack(side="top", anchor="w")

        self.campo_entrada = tk.Entry(pie)
        self.campo_entrada.bind("<Return>", lambda e: self.al_enviar())
        self.campo_entrada.pack(side="left", expand=True, fill="x", pady=(5,0))

        tk.Button(pie, text="Enviar", command=self.al_enviar).pack(side="right", padx=10)

        # ---------------- ÁREA DE MENSAJES ----------------
        frame_mensajes = tk.Frame(self.ventana_chat, bg="#f0f0f0", bd=3, relief=tk.SUNKEN)
        frame_mensajes.pack(fill='both', expand=True, padx=10, pady=5)

        self.texto_mensajes = tk.Text(
            frame_mensajes, wrap=tk.WORD, bg="white", fg="black",
            state=tk.DISABLED, padx=5, pady=5, relief=tk.FLAT
        )
        scrollbar = tk.Scrollbar(frame_mensajes, command=self.texto_mensajes.yview)
        self.texto_mensajes.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.texto_mensajes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def iniciar_cliente(self):
        """
        Crea una instancia del ClienteChat y arranca el hilo de recepción de mensajes.
        Muestra un error si la conexión inicial falla.
        Retorna True si el cliente se inicia correctamente, False en caso contrario.
        """
        self.cliente = ClienteChat( self.ip, self.puerto)

        if not self.cliente.iniciar(self.nombre):
            messagebox.showerror("Error", "No se pudo conectar al servidor")
            self.ventana_chat.destroy()
            return False

        self.mostrar_mensaje_sistema(f"Conectado a {self.ip}:{self.puerto}")

        threading.Thread(
            target=self.cliente.bucle_recibir,
            args=(self.manejar_mensaje_entrante,),
            daemon=True
        ).start()
        return True

    def centrar_ventana(self, w, h):
        """
        Calcula la posición para centrar la ventana en la pantalla.
        """
        cx = (self.ventana_chat.winfo_screenwidth() // 2) - (w // 2)
        cy = (self.ventana_chat.winfo_screenheight() // 2) - (h // 2)
        self.ventana_chat.geometry(f"{w}x{h}+{cx}+{cy}")

    def al_enviar(self):
        """
        Se ejecuta al presionar 'Enviar' o la tecla Enter.
        Formatea el mensaje (público o privado) y lo envía a través del cliente de red.
        """
        texto = self.campo_entrada.get().strip()
        if not texto:
            return

        comando_privado_tcp = "/p "

        # Si es un mensaje privado, lo enviamos tal cual
        if texto.startswith(comando_privado_tcp):

            import utilerias as util
            paquete = f"({util.ahora()}) {self.nombre}: {texto}"

            self.cliente.enviar(paquete)
        # Si es un mensaje público, le añadimos el formato
        else:
            import utilerias as util
            paquete = f"({util.ahora()}) {self.nombre}: {texto}"
            self.cliente.enviar(paquete)

        self.campo_entrada.delete(0, tk.END)

    def manejar_mensaje_entrante(self, mensaje):
        """
        Recibe un mensaje del hilo de red y lo pone en la cola de eventos
        de Tkinter para ser procesado de forma segura en el hilo principal de la GUI.
        """
        self.ventana_chat.after(0, self._procesar_mensaje_en_ui, mensaje)

    def _procesar_mensaje_en_ui(self, texto):
        """
        Se ejecuta en el hilo de la GUI.
        Parsea el texto del mensaje entrante para determinar su tipo (privado,
        público, sistema, etc.) y llama a la función de visualización correspondiente.
        """
        # Mensaje privado (TCP y UDP)
        if texto.startswith("(privado de") or texto.startswith("(privado para"):
            try:
                partes = texto.split(":", 1)
                info = partes[0] # (privado de/para Nombre)
                mensaje = partes[1].strip()

                # Mensaje recibido de otro usuario
                if info.startswith("(privado de"):
                    remitente = info.split(" ")[2].strip(")")
                    self.mostrar_mensaje(remitente, f"→ {mensaje}", es_privado=True)
                
                # Confirmación de nuestro mensaje enviado
                else: # (privado para)
                    destinatario = info.split(" ")[2].strip(")")
                    self.mostrar_mensaje(self.nombre, f"→ {destinatario}: {mensaje}", es_propio=True, es_privado=True)

            except Exception:
                self.mostrar_mensaje_sistema(texto) # Si el formato es inesperado, lo muestra como sistema
            return

        # Nuevo usuario
        if "se unió al chat" in texto:
            nombre = texto.split()[0]
            self.mostrar_mensaje_sistema(f"{nombre} se unió")
            return

        # Público
        if ":" in texto:
            # El formato del servidor TCP es: (fecha) nombre: mensaje
            # El formato del servidor UDP es: nombre: mensaje
            partes = texto.split(":", 1)
            remitente_info = partes[0]
            contenido = partes[1].strip()

            # Extraemos solo el nombre del remitente, que es la última "palabra" antes de los dos puntos.
            remitente = remitente_info.split()[-1].strip(":")

            # Si el mensaje es público (no es un comando de MP de TCP), lo mostramos
            if not contenido.startswith("/p"):
                self.mostrar_mensaje(
                    remitente, contenido, es_propio=(remitente == self.nombre)
                )
            return  # Ya procesamos el mensaje, salimos de la función

        # Mensajes del sistema
        self.mostrar_mensaje_sistema(texto)

    def mostrar_mensaje_sistema(self, mensaje):
        """
        Wrapper para mostrar un mensaje con el estilo de 'Sistema'.
        """
        self.mostrar_mensaje("Sistema", mensaje)

    def mostrar_mensaje(self, remitente, mensaje,
                        es_propio=False, es_privado=False):

        """
        Inserta un mensaje formateado y coloreado en el área de texto del chat.
        Define y aplica etiquetas (tags) de Tkinter para dar estilo al texto
        (color para mensajes propios, privados, de sistema, etc.).
        """

        self.texto_mensajes.config(state=tk.NORMAL)

        # Define los estilos en español
        if "sistema" not in self.texto_mensajes.tag_names():
            self.texto_mensajes.tag_configure("sistema", foreground="blue")
            self.texto_mensajes.tag_configure("propio", foreground="green")
            self.texto_mensajes.tag_configure("otro", foreground="black")
            self.texto_mensajes.tag_configure("privado", foreground="purple")
            self.texto_mensajes.tag_configure("hora", foreground="gray")

        if remitente == "Sistema":
            tag = "sistema"
        elif es_privado:
            tag = "privado"
        elif es_propio:
            tag = "propio"
        else:
            tag = "otro"

        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        self.texto_mensajes.insert(tk.END, f"[{timestamp}] ", ("hora",))
        self.texto_mensajes.insert(tk.END, f"{remitente}", (tag,))
        self.texto_mensajes.insert(tk.END, f": {mensaje}\n")

        self.texto_mensajes.config(state=tk.DISABLED)
        self.texto_mensajes.see(tk.END)

    
   
    def al_cerrar(self):
        """
        Se ejecuta cuando el usuario cierra la ventana de chat.
        Se asegura de cerrar la conexión de red antes de destruir la ventana.
        """
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
