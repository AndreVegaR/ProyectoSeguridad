"""
servidorTCP.py

Descripción:
-

Funcionamiento:

Autores:
-Aaron Xavier Burciaga Alcantar
-Andreiy Montoya Navarro
-Abelardo Andre Vega Romero
"""

"""Importaciones"""
import threading
import socket
import queue
import utilerias as util
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
codigo = "UTF-8"

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
            mensaje_str = mensaje.decode(codigo) #ya lo decodifique
            
            print("DEBUG mensaje =>", repr(mensaje))
            partes = mensaje_str.split(" ", 5)
            print("DEBUG partes =>", repr(partes))
            print("DEBUG lista_nombres =>", repr(nombres))

            if len(partes) > 3 and  partes[3] == "/p":
                print("DEBUG entra a la condicion =>", repr(nombres))
                mensaje_privado(cliente, partes)
                continue

            print(f"Mensaje: {mensaje_str}") # decodifica el mensaje para mostrarlo
            transmitir(mensaje) # Envía el mensajee a cada miembro
                #/p maria hola hola hola hola hola
        except:  # si se desconecta
            indice = clientes.index(cliente)  #saca la posicion del cliente (socket)
            clientes.remove(cliente) # saca al cliente de la lista(socket)
            cliente.close() #cierra el socket, para que el servidor no se comunique esa direccion
            nombre = nombres[indice] #extrae el nombre en base al indice
            transmitir(f"{nombre} dejó el chat".encode(codigo)) # envia el mensaje al server
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
        
        cliente.send("Nombre".encode(codigo)) #codifica el nombre del cliente
        texto  = cliente.recv(1024).decode(codigo) #decodifica el nombre del cliente
        texto_partes = texto.split(" ", 5) #separa texto en partes
        nombre = texto_partes[2].strip(":") # saca solo el nombre
        if usuario_repetido(cliente, nombre):    #verifica si el nombre ya existe
            continue # ignora lo de abajo
        
        nombres.append(nombre) # agrega el nombre al registro de nombres
        clientes.append(cliente) # agrega al cliente al registro de clientes
        
        
        print(f'El nombre del cliente es {nombre}')
        transmitir(f'{nombre} se unió al chat'.encode(codigo))    
        cliente.send('Conectado al servidor ☻'.encode(codigo))
        
        # target indica la funcion que manejará el hilo
        # args con quien trabajara, es decir, al cliente que se asocia
        hilo = threading.Thread(target=manejar, args=(cliente,)) #se crea el hilo que conecta el servidor con el cliente
        with bloqueo: # un hilo a la vez
            usuariosActivos += 1 # modifica el contador
        hilo.start() # empieza el hilo




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
        cliente.send("Nombre en uso, utilice otro usuario".encode(codigo))
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
        cliente.send("Formato válido: /p nombre mensaje".encode(codigo))
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
        mensaje_para_receptor = f"(privado de {remitente_nombre}): {mensaje_cuerpo}".encode(codigo)
        mensaje_para_emisor = f"(privado para {destinatario_nombre}): {mensaje_cuerpo}".encode(codigo)

        # Enviar el mensaje correspondiente a cada uno
        cliente_destino.send(mensaje_para_receptor)
        cliente.send(mensaje_para_emisor)

    except ValueError:
        cliente.send(f"⚠️ ERROR. Nombre: {partes[4]} inexistente".encode(codigo))
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
