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
- Willian Alexander Tolano Fierros
- Noelia Encinas Noriega
- Abelardo Andre Vega Romero
- Julian Gerardo Izaguirre Menchaca
"""

"""Importaciones"""
import socket       # Conecta dispositivos mediante cliente-servidor
import threading    # Ejecuta paralelamente
import utilerias as util  # Funciones varias

evento_conectado = threading.Event()

"""Encapsula todo en una función para llamarla desde menu.py"""
def iniciar(mostrar_funcion):
    ip = util.pedirIp()
    puerto = util.pedirPuerto()
    nombre = util.pedirNombre()
    cliente = conectar(ip, puerto) 
    hilosCliente(recibir, escribir, cliente, nombre, mostrar_funcion)
    return cliente


"""Configura el cliente mediante un socket"""
def conectar(ip, puerto):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket TCP (SOCK_STREAM) IPv4 (AF_INET)
    cliente.settimeout(5)  # Tiempo de espera 5 segundos
    try:
        cliente.connect((ip, puerto))  # Se conecta con el servidor una vez y queda asociado
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
            texto = cliente.recv(1024).decode(util.codigo)
            if not texto:
                continue
            # El servidor pide el nombre
            if texto == "Nombre":
                cliente.send(nombre.encode(util.codigo))
            # El servidor pide el correo para MFA
            elif texto == "MFA_CORREO":
                correo = input("Ingresa tu correo para MFA: ")
                cliente.send(correo.encode(util.codigo))
            # El servidor pide el código MFA
            elif texto == "MFA_CODIGO":
                codigo = input("Ingresa el código MFA recibido: ")
                cliente.send(codigo.encode(util.codigo))
            # Error al enviar el correo MFA
            elif texto == "MFA_ERROR":
                mostrar_funcion("Error: no se pudo enviar el código MFA.")
                cliente.close()
                break
            # Código incorrecto, expirado o inexistente
            elif texto.startswith("MFA_FALLO"):
                motivo = texto.split(":", 1)[1] if ":" in texto else "desconocido"
                mostrar_funcion(f"MFA fallido. Motivo: {motivo}")
                cliente.close()
                break
            # Ya terminó el login correctamente
            elif texto == "Conectado al servidor":
                evento_conectado.set()
                mostrar_funcion(texto)
            # Cualquier otro mensaje normal del chat
            else:
                mostrar_funcion(texto)
        except Exception as e:
            mostrar_funcion(f"Error: {e}")
            cliente.close()
            break


"""Envía mensajes al servidor TCP"""
def escribir(cliente, nombre):
    evento_conectado.wait()
    while True:
        texto = input("")
        mensaje = f"({util.ahora()}) {nombre}: {texto}"
        cliente.send(mensaje.encode(util.codigo))


"""Inserta los métodos en hilos e inicia su funcionamiento con .start()"""
def hilosCliente(recibir, escribir, cliente, nombre, mostrar_funcion):
    # Se agrega 'mostrar_funcion' a los argumentos de 'recibir'
    threading.Thread(target=recibir, args=(cliente, nombre, mostrar_funcion)).start()
    threading.Thread(target=escribir, args=(cliente, nombre)).start()


# la llamada final a iniciar() DEBE ser modificada por el usuario al usar este archivo
def funcion_para_mostrar(texto):
    print(texto)


if __name__ == "__main__":
    iniciar(funcion_para_mostrar)
