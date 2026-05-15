"""
clienteUDP.py

Descripción:
- Utiliza sockets e hilos para comunicarse a un servidor de protocolo UDP codificando con ASCII

Funcionamiento:
- Importa sockets e hilos
- iniciar(): llama a los métodos internos y los importados de utilerías (pedir información, validar, ejecutar hilos)
- conectar(): configura la conexión del cliente, que es un socket (IP y puerto)
- recibir(): recibe instrucciones y mensajes del servidor
- escribir():envía mensajes al servidor junto con nombre de usuario y la fecha y hora
- hilosCliente(): ejecuta las funciones en hilos

Autores:
- Willian Alexander Tolano Fierros
- Noelia Encinas Noriega
- Abelardo Andre Vega Romero
- Julian Gerardo Izaguirre Menchaca
"""

"""Importaciones"""
import socket
import threading
import utilerias as util
global cliente

def iniciar(mostrar_funcion):
    servidor = util.pedirIp()
    puerto = util.pedirPuerto()
    cliente, direccion = conectar(servidor, puerto)
    nombre = util.pedirNombre()
    hilosCliente(recibir, escribir, cliente, direccion, nombre, mostrar_funcion)
    return cliente

def conectar(servidor, puerto):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Validar que el servidor existe enviando un paquete de prueba
    try:
        cliente.settimeout(3)  # Tiempo de espera de 3 segundos
        cliente.sendto(b"PING", (servidor, puerto))  # Envía un paquete de prueba
        # Intenta recibir respuesta
        try:
            response, _ = cliente.recvfrom(1024)
            print(f"Servidor UDP encontrado: {servidor}:{puerto}")
        except socket.timeout:
            print(f"Advertencia: No se recibió respuesta del servidor, pero puede estar disponible")
        cliente.settimeout(None)  # Restaura tiempo de espera a infinito
    except socket.gaierror:
        raise Exception(f"Error de DNS: No se pudo resolver la dirección {servidor}")
    except Exception as e:
        raise Exception(f"Error al validar servidor UDP: {e}")
    
    destino = (servidor, puerto)
    return cliente, destino

def recibir(cliente, direccion, nombre, mostrar_funcion):
    while True:
        try:
            texto, direccion = cliente.recvfrom(1024)
            decodificado = texto.decode("ascii")
            if decodificado == "Nombre: ":
                cliente.sendto(nombre.encode("ascii"), direccion)
            else:
                mostrar_funcion(decodificado)
        except:
            cliente.close()
            break

def escribir(cliente, direccion, nombre):
    while True:
        texto = input("")
        mensaje = f"({util.ahora()}) {nombre}: {texto}"
        cliente.sendto(mensaje.encode("ascii"), direccion)

def hilosCliente(recibir_func, escribir_func, cliente, direccion, nombre, mostrar_funcion):
    threading.Thread(target=recibir_func, args=(cliente, direccion, nombre, mostrar_funcion), daemon=True).start()
    threading.Thread(target=escribir_func, args=(cliente, direccion, nombre), daemon=True).start()
