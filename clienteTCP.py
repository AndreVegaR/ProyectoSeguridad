"""
clienteTCP.py

Descripción:
- Utiliza sockets e hilos para comunicarse a un servidor de protocolo TCP codificando con ASCII
- Los parámetros los recibe con los datos recolectados de conectar.py

Funcionamiento:
- Importa sockets e hilos
- iniciar(): llama a las funciones internos, recibe 'mostrar_funcion' como parámetro
- conectar(): configura la conexión del cliente, que es un socket (IP y puerto)
- recibir(): recibe instrucciones y mensajes del servidor y usa 'mostrar_funcion' para imprimir
- escribir(): envía mensajes al servidor junto con nombre de usuario y la fecha y hora
- hilosCliente(): ejecuta las funciones en hilos

Autores:
- Aaron Xavier Burciaga Alcantar
- Andreiy Montoya Navarro
- Abelardo Andre Vega Romero
"""

"""Importaciones"""
import socket       # Conecta dispositivos mediante cliente-servidor
import threading    # Ejecuta paralelamente
import utilerias as util  # Funciones varias


"""Encapsula todo en una función para llamarla desde menu.py"""
def iniciar(mostrar_funcion):
    ip = util.pedirIp()
    puerto = util.pedirPuerto()
    nombre = util.pedirNombre()
    cliente = conectar(ip, puerto)  # Establece la conexión con el servidor
    hilosCliente(recibir, escribir, cliente, nombre, mostrar_funcion)  # Llama la función que ejecuta hilos
    return cliente


"""Configura el cliente mediante un socket"""
def conectar(ip, puerto):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket TCP (SOCK_STREAM) IPv4 (AF_INET)
    cliente.settimeout(5)  # Tiempo máximo de espera 5 segundos
    try:
        cliente.connect((ip, puerto))  # Se conecta con el servidor una vez y queda asociado.
    except socket.timeout:
        raise Exception(f"Timeout: No se pudo conectar al servidor TCP en {ip}:{puerto}")
    except ConnectionRefusedError:
        raise Exception(f"Conexión rechazada: No hay servidor TCP escuchando en {ip}:{puerto}")
    except socket.gaierror:
        raise Exception(f"Error de DNS: No se pudo resolver la dirección {ip}")
    except Exception as e:
        raise Exception(f"No se pudo conectar: {e}")
    finally:
        cliente.settimeout(None)  # Restaura el timeout a infinito después de conectar
    return cliente


"""Recibe mensajes del servidor TCP"""
def recibir(cliente, nombre, mostrar_funcion):
    while True:
        try:
            texto = cliente.recv(1024).decode(util.codigo)  # Mensaje decodificado de 1024 bytes mediante ASCII
            if texto == "Nombre: ":  # El servidor pide el nombre al cliente
                cliente.send(nombre.encode(util.codigo))
            else:
                if not texto:
                    continue
                else:
                    mostrar_funcion(texto)  # *** USO DE LA FUNCIÓN PASADA COMO PARÁMETRO ***
        except Exception as e:
            mostrar_funcion(f"Error: {e}")  # Usamos también la función para mostrar el error
            cliente.close()  # Si hay un error, cierra el cliente y rompe el bucle
            break


"""Envía mensajes al servidor TCP"""
def escribir(cliente, nombre):
    while True:
        texto = input("")  # Contenido del mensaje
        mensaje = f"({util.ahora()}) {nombre}: {texto}"  # Mensaje con emisor y fecha
        cliente.send(mensaje.encode(util.codigo))  # Codifica dicho mensaje con ASCII


"""Inserta los métodos en hilos e inicia su funcionamiento con .start()"""
def hilosCliente(recibir, escribir, cliente, nombre, mostrar_funcion):
    # Se agrega 'mostrar_funcion' a los argumentos de 'recibir'
    threading.Thread(target=recibir, args=(cliente, nombre, mostrar_funcion)).start()
    threading.Thread(target=escribir, args=(cliente, nombre)).start()


# NOTA: La llamada final a iniciar() DEBE ser modificada por el usuario al usar este archivo.
# Por ejemplo, si se usa desde otro script (como menu.py), el archivo lo llamaría así:
# cliente_tcp.iniciar(print)
#
# Para que funcione al ejecutar este archivo directamente:
def funcion_para_mostrar(texto):
    print(texto)


if __name__ == "__main__":
    iniciar(funcion_para_mostrar)
