"""
servidorTCP.py

Descripción:
- Servidor TCP del chat seguro

Funcionamiento:
- Acepta conexiones de clientes, valida nombres, sanitiza mensajes
- Maneja mensajes publicos y privados mediante hilos
- Registra eventos en bitacoras

Autores:
- Willian Alexander Tolano Fierros
- Noelia Encinas Noriega
- Abelardo Andre Vega Romero
- Julian Gerardo Izaguirre Menchaca
"""

"""Importaciones"""
import threading
import socket
import queue
import utilerias as util
import Mfa
import logging
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import struct
from bitacoras import(
    accesos,
    mfa,
    mensajes as log_mensajes,
    errores,
    servidor as log_servidor,
    sospechosos
)


#Otro Logger para debuggear en python....
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s (servidorTCP.py) - %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


"""
Generacion del par de claves RSA del servidor.
La clave privada se queda en el servidor para descifrar.
La clave publica se manda a cada cliente al conectarse para que cifre.
"""
_clave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_clave_publica_bytes = _clave_privada.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


def _descifrar(datos_cifrados):
    """Descifra bytes recibidos del cliente con la clave privada RSA del servidor."""
    return _clave_privada.decrypt(
        datos_cifrados,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
def enviar_bloque(cliente, datos: bytes):
    tamano = struct.pack("!I", len(datos))
    cliente.sendall(tamano + datos)


def recibir_exactamente(cliente, cantidad):
    datos = b""

    while len(datos) < cantidad:
        parte = cliente.recv(cantidad - len(datos))

        if not parte:
            raise ConnectionError("El cliente cerró la conexión.")

        datos += parte

    return datos

"""
mensajes:
Cola para compartir mensajes entre hilos y que todos los puedan ver
en otras palabras, es la base del chat grupal.

bloqueo:
Se asegura que no modifiquen la variable varios hilos en simultaneo

condicion:
Hace que el hilo pueda usarse una vez sea liberado por un cliente
"""
cola_mensajes = queue.Queue()
bloqueo = threading.Lock()
condicion = threading.Condition()


"""
Listas para guardar clientes y sus nombres

CODEC: variable encargada de definir el tipo de decodificador
"""
clientes = []
nombres = []
CODEC = "UTF-8"


"""
Variable controladora de clientes activos en simultaneo
El maximo son 5 segun la especificacion del proyecto
"""
CAPACIDAD_MAXIMA = 5
usuariosActivos = 0


"""
funcion que da inicio al servidor
"""
def iniciar(puerto=51225):
    global servidor # Si no se hace global, se vuelve una variable local
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #El servidor es un socket TCP (SOCK_STREAM) IPv4 (AF_INET)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # asigna una configuracion general al socket(socket.SOL_SOCKET), dicha config hace que otro cliente reutilice el puerto, el 1 es para activar
    servidor.bind(("0.0.0.0", puerto)) #Se conecta: IP (0.0.0.0 para aceptar cualquier interfaz), puerto. Parametro de tupla
    servidor.listen() #Espera y atiende los clientes. Tiene una lista de espera en el SO
    print(f"Servidor iniciado en puerto {puerto}")

    #registramos el inicio del servidor en las bitacoras
    #antes se llamaba servidor.info() sobre el socket y tronaba, ahora usamos el logger correcto
    log_servidor.info(f"Servidor iniciado en puerto {puerto}")

    print("Abre varias terminales y ejecuta cliente.py")
    recibir()


"""
Itera en la lista de todos los participantes para enviarles el mensaje que un cliente escribio
al resto de clientes en el server
Usa una copia de la lista para que no truene si alguien se desconecta en medio del envio
"""
def transmitir(mensaje):
    for cliente in list(clientes):
        try:
            cliente.send(mensaje) #manda el mensaje de cada cliente
        except Exception as e: #si un cliente se cayo en medio del envio lo sacamos sin tronar
            errores.error(f"Error transmitiendo a cliente: {e}")
            clientes.remove(cliente)
            cliente.close()


"""
Se encarga de manejar el envio de mensajes a todo el grupo
y a su vez se encarga de eliminar a participantes que abandonaron el chat

La sanitizacion se aplica aqui tambien en el servidor porque el cliente
puede mandar lo que quiera por el socket, no solo lo que escribio en la interfaz
"""
def manejar(cliente):
    global usuariosActivos # evita variable local
    while True:
        try: # si el cliente esta activo
            datos = cliente.recv(2048) #El mensaje lo recibira del cliente
            if not datos:
                raise ConnectionResetError("El cliente cerro la conexion")

            # Desciframos el mensaje con la clave privada RSA
            try:
                mensaje_str = _descifrar(datos).decode(CODEC)
            except Exception:
                # Si no se puede descifrar ignoramos el paquete
                continue

            # El cliente mando la senal de salida voluntaria, limpiamos inmediatamente
            if "__SALIR__" in mensaje_str:
                raise ConnectionResetError("El cliente se desconecto voluntariamente")

            #el formato del mensaje es: (fecha hora) nombre: texto
            #con limite de 5 splits para no partir el cuerpo del mensaje
            partes = mensaje_str.split(" ", 5)

            #si el cuarto elemento es /p es un mensaje privado
            if len(partes) > 3 and partes[3] == "/p":
                mensaje_privado(cliente, partes)
                continue

            #sanitizamos el cuerpo del mensaje antes de transmitirlo al resto
            #el cuerpo siempre esta en la ultima parte, despues del nombre y la fecha
            if len(partes) >= 6:
                cuerpo_limpio = util.sanitizar(partes[5])
                if not cuerpo_limpio:
                    #si quedo vacio despues de limpiar lo descartamos y lo registramos
                    sospechosos.warning(
                        f"Mensaje descartado por sanitizacion, remitente: {partes[2].strip(':')}"
                    )
                    continue
                partes[5] = cuerpo_limpio
                mensaje_str = " ".join(partes)
            else:
                #formato raro, sanitizamos todo el string completo
                mensaje_str = util.sanitizar(mensaje_str)
                if not mensaje_str:
                    continue

            print(f"Mensaje: {mensaje_str}") # decodifica el mensaje para mostrarlo

            #registra el mensaje en las bitacoras
            log_mensajes.info(mensaje_str)

            transmitir(mensaje_str.encode(CODEC)) # Envia el mensaje a cada miembro

        except:  # si se desconecta
            try:
                indice = clientes.index(cliente)  #saca la posicion del cliente (socket)
                nombre = nombres[indice] #extrae el nombre en base al indice
                clientes.remove(cliente) # saca al cliente de la lista (socket)
                nombres.remove(nombre) #elimina el nombre del cliente del registro
            except ValueError:
                nombre = "desconocido"

            cliente.close() #cierra el socket, para que el servidor no se comunique esa direccion

            #registramos la salida del usuario en las bitacoras
            accesos.info(f"{nombre} se desconecto")

            transmitir(f"{nombre} dejo el chat".encode(CODEC)) # envia el aviso al resto
            with bloqueo:
                usuariosActivos -= 1 #disminuye la cantidad de usuarios activos
            with condicion: #solo un hilo a la vez
                condicion.notify() # notifica que el espacio queda disponible
            break                  #despierta un cliente en espera


"""
Acepta a los clientes al servidor y crea hilos que se asocian a cada cliente
Esta funcion gestiona los hilos y a su vez asigna cada hilo a un cliente, anade cada cliente
tanto como su nombre a registros y da avisos

Aqui tambien se sanitiza y valida el nombre que manda el cliente antes de registrarlo
"""
def recibir():
    global usuariosActivos, CAPACIDAD_MAXIMA
    while True:
        espera_turno()
        cliente, direccion = servidor.accept() #Acepta a los clientes al servidor. cliente guarda el socket, direccion la tupla de ip y puerto efimero

        print(f"Conectados con {str(direccion)}") #Muestra quien se conecto

        # Mandamos la clave publica RSA al cliente antes de cualquier otra cosa
        enviar_bloque(cliente, _clave_publica_bytes)

        cliente.sendall("Nombre".encode(CODEC))

        #tratamos de recibir el nombre, si falla cerramos la conexion
        try:
            datos_cifrados = recibir_exactamente(cliente, 256)
            texto = _descifrar(datos_cifrados).decode(CODEC)
        except Exception as e:
            errores.error(f"Error recibiendo nombre de {direccion}: {e}")
            cliente.close()
            continue

        #separamos el texto para extraer el nombre en la misma posicion que siempre manda el cliente
        texto_partes = texto.split(" ", 5)
        nombre_raw = texto_partes[2].strip(":") if len(texto_partes) > 2 else texto

        #sanitizamos el nombre para quitar caracteres raros antes de usarlo
        nombre = util.sanitizar_nombre(nombre_raw)

        #si el nombre quedo vacio o tiene menos de un caracter valido, rechazamos la conexion
        if not util.validar_nombre(nombre):
            sospechosos.warning(f"Nombre invalido recibido desde {direccion[0]}: {nombre_raw}")
            cliente.send("Nombre invalido. Solo letras, numeros y guiones, maximo 20 caracteres.".encode(CODEC))
            cliente.close()
            continue

        if usuario_repetido(cliente, nombre):
            continue

        #Si se quiere saltar lo del MFA, quitar estas tres lineas o ponerlas como comentario
        #if not verificar_mfa(cliente, nombre):
        #  cliente.close()
        #  continue

        nombres.append(nombre)
        clientes.append(cliente)
        print(f'El nombre del cliente es {nombre}')

        #registramos el acceso del usuario en las bitacoras
        accesos.info(f"{nombre} conectado desde {direccion[0]}")

        # Aqui es donde se registra en la bitacora cuando alguien entra al chat
        log_mensajes.info(f"{nombre} se unio al chat")

        transmitir(f'{nombre} se unio al chat'.encode(CODEC))
        cliente.send('Conectado al servidor'.encode(CODEC))

        hilo = threading.Thread(target=manejar, args=(cliente,), daemon=True)
        with bloqueo:
            usuariosActivos += 1
        hilo.start()


def verificar_mfa(cliente, nombre):
    try:
        cliente.sendall("MFA_CORREO".encode(CODEC))

        datos_correo = recibir_exactamente(cliente, 256)
        correo = _descifrar(datos_correo).decode(CODEC).strip()

        log.info(f"Correo recibido de {nombre}: {correo}")

        # registramos el MFA enviado en las bitacoras
        mfa.info(f"Correo enviado a {correo} para {nombre}")

        if not correo:
            log.error(f"Correo vacío recibido para MFA de {nombre}")
            cliente.sendall("MFA_ERROR".encode(CODEC))
            return False

        if not Mfa.enviar_codigo(correo):
            log.error(f"No se pudo enviar codigo MFA a {correo}")
            cliente.sendall("MFA_ERROR".encode(CODEC))
            return False

        cliente.sendall("MFA_CODIGO".encode(CODEC))

        datos_codigo = recibir_exactamente(cliente, 256)
        codigo_ingresado = _descifrar(datos_codigo).decode(CODEC).strip()

        log.debug(f"Codigo recibido de {nombre}: {codigo_ingresado}")

        exito, motivo = Mfa.verificar_codigo(correo, codigo_ingresado)

        if not exito:
            # registramos el fallo de MFA en las bitacoras
            mfa.warning(f"{nombre} fallo MFA: {motivo}")

            log.warning(f"MFA fallido para {nombre}: {motivo}")
            cliente.sendall(f"MFA_FALLO:{motivo}".encode(CODEC))
            return False

        log.info(f"MFA exitoso para {nombre}")
        mfa.info(f"{nombre} autenticado correctamente")
        return True

    except Exception as e:
        errores.error(f"Error durante MFA para {nombre}: {e}")
        log.error(f"Error durante MFA para {nombre}: {e}")

        try:
            cliente.sendall("MFA_ERROR".encode(CODEC))
        except:
            pass

        return False

"""
Busca si un nombre ya existe en el registro de nombres
cliente es el socket
nombre es el nombre de ese socket (o del usuario)

en caso de existir da retroalimentacion al cliente, cierra su socket
regresa verdadero
caso contrario, regresa falso
"""
def usuario_repetido(cliente, nombre):
    if nombre in nombres:

        #registramos el nombre repetido en las bitacoras
        sospechosos.warning(f"Nombre duplicado: {nombre}")

        cliente.send("Nombre en uso, utilice otro usuario".encode(CODEC))
        cliente.close()
        return True
    return False


"""
Envia mensaje solo a un cliente en especifico
cliente es el socket del que manda
partes es el texto que recibe ya decodificado separado en partes

Aqui sanitizamos tanto el cuerpo del mensaje como el nombre del destinatario
en caso de haber excepcion ValueError, notifica al usuario que el nombre no existe
"""
def mensaje_privado(cliente, partes):
    if len(partes) < 6:
        cliente.send("Formato valido: /p nombre mensaje".encode(CODEC))
        return
    try:
        # Extraer remitente, destinatario y mensaje
        remitente_nombre = partes[2].strip(":")
        destinatario_nombre = partes[4]
        cuerpo_raw = partes[5]

        #sanitizamos el cuerpo antes de enviarlo
        cuerpo = util.sanitizar(cuerpo_raw)
        if not cuerpo:
            #si quedo vacio lo rechazamos y lo registramos como sospechoso
            cliente.send("Mensaje privado vacio o con caracteres no permitidos.".encode(CODEC))
            sospechosos.warning(
                f"Mensaje privado descartado de {remitente_nombre} para {destinatario_nombre}"
            )
            return

        #sanitizamos el nombre del destinatario por si viene con caracteres raros
        destinatario_nombre = util.sanitizar_nombre(destinatario_nombre)
        if not util.validar_nombre(destinatario_nombre):
            cliente.send("Nombre de destinatario invalido.".encode(CODEC))
            return

        # Encontrar los sockets de ambos
        indice_destino = nombres.index(destinatario_nombre)
        cliente_destino = clientes[indice_destino]

        # Construir dos mensajes: uno para el receptor y otro para el emisor
        mensaje_para_receptor = f"(privado de {remitente_nombre}): {cuerpo}".encode(CODEC)
        mensaje_para_emisor = f"(privado para {destinatario_nombre}): {cuerpo}".encode(CODEC)

        # Enviar el mensaje correspondiente a cada uno
        cliente_destino.send(mensaje_para_receptor)
        cliente.send(mensaje_para_emisor)

        log_mensajes.info(f"Mensaje privado de {remitente_nombre} para {destinatario_nombre}: {cuerpo}")

    except ValueError:
        cliente.send(f"ERROR. Nombre: {partes[4]} inexistente".encode(CODEC))
        return


"""
pone al hilo en espera si este supera la capacidad maxima
usa while en vez de if para que siga esperando aunque lo despierten por error
"""
def espera_turno():
    with condicion: # controla la cola de espera
        while usuariosActivos >= CAPACIDAD_MAXIMA:
            condicion.wait() #pone el hilo a esperar
    return


if __name__ == "__main__":
    iniciar(51225)