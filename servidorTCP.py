"""
servidorTCP.py

Descripción:
-

Funcionamiento:

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
from bitacoras import(
    accesos,
    mfa,
    mensajes,
    errores,
    servidor,
    sospechosos
)


#Otro Logger para debuggear en python....
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s (servidorTCP.py) - %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)
"""Configura el servidor mediante un socket
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #El servidor es un socket TCP (SOCK_STREAM) IPv4 (AF_INET)
servidor.bind(("127.0.0.1", 51225)) #Se conecta: IP (localhost en este caso), puerto (51225 por el 05/12/25). Parámetro de tupla
servidor.listen() #Espera mensajes de clientes
"""
"""


mensajes:
Cola para compartir mensajes entre hilos y que todos los puedan ver
en otras palabras, es la base del chat grupal.

bloqueo:
Se asegura que no modifiquen la variable varios hilos en simultaneo

condicion:
Hace que el hilo pueda usarse una vez sea liberado por un cliente
"""
mensajes = queue.Queue()
bloqueo = threading.Lock()
condicion = threading.Condition()

"""
Listas para guardar clientes y sus nombres

codigo: variable encargada de definir el tipo de decodificador
"""
clientes = []
nombres = []
CODEC = "UTF-8"

"""
Variable controladora de clientes activos en simultaneo
"""
CAPACIDAD_MAXIMA = 6
usuariosActivos = 0

"""
funcion que da inicio al servidor
"""
def iniciar(puerto=51225):
    global servidor # Si no se hace global, se vuelve una variable local
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #El servidor es un socket TCP (SOCK_STREAM) IPv4 (AF_INET)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # asigna una configuracion general al socket(socket.SOL_SOCKET), dicha config hace que otro cliente reutilice el puerto, el 1 es para activar
    servidor.bind(("0.0.0.0", puerto)) #Se conecta: IP (localhost en este caso), puerto (51225 por el 05/12/25). Parámetro de tupla
    servidor.listen() #Espera y atiende los clientes. Tiene una lista de espera en el SO
    print(f"Servidor iniciado en puerto {puerto}")

    #registramos el inicio del servidor en las bitacoras
    servidor.info(f"Servidor iniciado en puerto {puerto}")

    print("Abre varias terminales y ejecuta cliente.py")
    recibir()


"""
Itera en la lista de todos los participantes para enviarles el mensaje que un cliente escribió
al resto de clientes en el server
"""
def transmitir(mensaje):
    for cliente in clientes: 
        try:
            cliente.send(mensaje) #manda el mensaje de cada cliente
        except: #si un cliente es sacado por nombre repetido evita que truene
            clientes.remove(cliente)
            cliente.close()
            


"""
Se encarga de manejar  el envio de mensajes a todo el grupo
y a su vez se encarga de eliminar a participantes que abandonaron el chat
"""
def manejar(cliente):
    global usuariosActivos # evita variable local
    while True:
        try: # si el cliente está activo
            mensaje = cliente.recv(1024) #El mensaje lo recibirá del cliente 
            
            #logica para mensajes privados
            mensaje_str = mensaje.decode(CODEC) #ya lo decodifique
            
            print("DEBUG mensaje =>", repr(mensaje))
            partes = mensaje_str.split(" ", 5)
            print("DEBUG partes =>", repr(partes))
            print("DEBUG lista_nombres =>", repr(nombres))

            if len(partes) > 3 and  partes[3] == "/p":
                print("DEBUG entra a la condicion =>", repr(nombres))
                mensaje_privado(cliente, partes)
                continue

            print(f"Mensaje: {mensaje_str}") # decodifica el mensaje para mostrarlo

            #registra el mensaje en las bitacoras
            mensajes.info(mensaje_str)

            transmitir(mensaje) # Envía el mensajee a cada miembro
                #/p maria hola hola hola hola hola
        except:  # si se desconecta
            indice = clientes.index(cliente)  #saca la posicion del cliente (socket)
            clientes.remove(cliente) # saca al cliente de la lista(socket)
            cliente.close() #cierra el socket, para que el servidor no se comunique esa direccion
            nombre = nombres[indice] #extrae el nombre en base al indice

            #registramos la salida del usuario en las bitacoras
            accesos.info(f"{nombre} se desconectó")

            
            transmitir(f"{nombre} dejó el chat".encode(CODEC)) # envia el mensaje al server
            nombres.remove(nombre) #elimina el nombre del cliente del registro
            usuariosActivos -= 1 #disminiye la cantidad de usuarios activos
            with condicion: #solo un hilo a la vez
                condicion.notify() # notifica que el espacio queda disponible
            break                  #despierta un cliente en espera

    

"""
    Acepta los a los clientes al servidor y crea hilos que se asocian a cada cliente
    Esta funcion gestiona los hilos y a su vez asigna cada hilo a un cliente, añade cada cliente
    tanto como su nombre a registros y da avisos
"""
def recibir():
    global usuariosActivos, CAPACIDAD_MAXIMA
    while True:
        espera_turno()
        cliente, direccion = servidor.accept() #Acepta a los clientes al servidor  cliente guarda el socket, direccion la tupla de ip y puerto efimero
        
        print(f"Conectados con {str(direccion)}") #Muestra quién se conectó
        
        cliente.send("Nombre".encode(CODEC))
        texto = cliente.recv(1024).decode(CODEC)
        texto_partes = texto.split(" ", 5)
        nombre = texto_partes[2].strip(":")
        if usuario_repetido(cliente, nombre):
            continue
        #Si se quiere saltar lo del MFA, quitar estas tres Líneas o ponerlas como comentario
        #if not verificar_mfa(cliente, nombre):
        #    cliente.close()
        #    continue

        nombres.append(nombre)
        clientes.append(cliente)
        print(f'El nombre del cliente es {nombre}')

        #registramos el acceso del usuario en las bitacoras
        accesos.info(f"{nombre} conectado desde {direccion[0]}")
        
        
        # Aqui es donde se registra en la bitacora cuando alguien entra al chat
        mensajes.info(f"{nombre} se unió al chat")
        
        transmitir(f'{nombre} se unió al chat'.encode(CODEC))
        cliente.send('Conectado al servidor ☻'.encode(CODEC))

        hilo = threading.Thread(target=manejar, args=(cliente,))
        with bloqueo:
            usuariosActivos += 1
        hilo.start()

def verificar_mfa(cliente, nombre):

    cliente.send("MFA_CORREO".encode(CODEC))
    correo = cliente.recv(1024).decode(CODEC).strip()
    log.info(f"Correo recibido de {nombre}: {correo}")

    #registramos el MFA enviado en las bitacoras
    mfa.info(f"Correo enviado a {correo} para {nombre}")

    if not Mfa.enviar_codigo(correo):
        log.error(f"No se pudo enviar código MFA a {correo}")
        cliente.send("MFA_ERROR".encode(CODEC))
        return False

    cliente.send("MFA_CODIGO".encode(CODEC))
    codigo_ingresado = cliente.recv(1024).decode(CODEC).strip()
    log.debug(f"Código recibido de {nombre}: {codigo_ingresado}")

    exito, motivo = Mfa.verificar_codigo(correo, codigo_ingresado)
    if not exito:

        #registramos el fallo de MFA en las bitacoras
        mfa.warning(f"{nombre} falló MFA: {motivo}")

        log.warning(f"MFA fallido para {nombre}: {motivo}")
        cliente.send(f"MFA_FALLO:{motivo}".encode(CODEC))
        return False

    log.info(f"MFA exitoso para {nombre}")
    mfa.info(f"{nombre} autenticado correctamente")
    return True

"""
Busca si nombre un nombre ya existe en el registro de nombres
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
Envía mensaje solo a un cliente en específico
cliente es el socket
partes es el texto que recibe (ya decodificado) separado en partes

en caso de haber excepcion ValueError, notifica al usuario
"""
def mensaje_privado(cliente, partes):
    print("DEBUG entra a mensaje privado", repr(nombres))
    if len(partes) < 6:
        print("DEBUG entra a condicion", repr(nombres))
        cliente.send("Formato válido: /p nombre mensaje".encode(CODEC))
        return 
    try:
        # Extraer remitente, destinatario y mensaje
        remitente_nombre = partes[2].strip(":")
        destinatario_nombre = partes[4]
        mensaje_cuerpo = partes[5]

        # Encontrar los sockets de ambos
        indice_destino = nombres.index(destinatario_nombre)
        cliente_destino = clientes[indice_destino]

        # Construir dos mensajes: uno para el receptor y otro para el emisor
        mensaje_para_receptor = f"(privado de {remitente_nombre}): {mensaje_cuerpo}".encode(CODEC)
        mensaje_para_emisor = f"(privado para {destinatario_nombre}): {mensaje_cuerpo}".encode(CODEC)

        # Enviar el mensaje correspondiente a cada uno
        cliente_destino.send(mensaje_para_receptor)
        cliente.send(mensaje_para_emisor)

        mensajes.info(f"Mensaje privado de {remitente_nombre} para {destinatario_nombre}: {mensaje_cuerpo}")

    except ValueError:
        cliente.send(f"⚠️ ERROR. Nombre: {partes[4]} inexistente".encode(CODEC))
        return 
    

"""
pone al hilo en espera si este supera la capacidad maxima
"""
def espera_turno():
    with condicion: # controla la cola de espera
        if usuariosActivos >= CAPACIDAD_MAXIMA:  
            condicion.wait() #pone el hilo a esperar
    return


if __name__ == "__main__":
    iniciar(51225)
