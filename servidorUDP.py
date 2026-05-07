"""
servidorUDP.py

Descripción:
- Servidor UDP que maneja múltiples clientes usando hilos y una cola de mensajes.
- Incluye:
  ✔ Validación de nombres no repetidos
  ✔ Mensajes privados con el formato: /privado Nombre Mensaje

Autores:
- Aaron Xavier Burciaga Alcantar
- Andreiy Montoya Navarro
- Abelardo Andre Vega Romero
"""

import socket
import threading
import queue
import utilerias as util

servidor = None
puerto = None

mensajes = queue.Queue()

clientes = []
nombres = []

bloqueo = threading.Lock()
CAPACIDAD_MAXIMA = 6


def iniciar(puerto_param=5000):
    global servidor, puerto
    try:
        puerto = puerto_param
        servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind(("0.0.0.0", puerto))
        
        print(f"Servidor UDP iniciado en {util.ip()}:{puerto}")
        print("Esperando conexiones...")

        threading.Thread(target=recibir, daemon=True).start()
        threading.Thread(target=transmitir, daemon=True).start()

    except OSError as e:
        print(f"Error al iniciar servidor UDP: {e}")
        raise


def recibir():
    while True:
        try:
            mensaje, direccion = servidor.recvfrom(1024)
            mensajes.put((mensaje, direccion))
        except:
            pass


def transmitir():
    while True:
        while not mensajes.empty():
            mensaje, direccion = mensajes.get()
            if not mensaje:
                continue

            texto = mensaje.decode(util.codigo).strip()

            with bloqueo:

                # Nuevo cliente → su primer mensaje es su nombre
                if direccion not in clientes:

                    if len(clientes) >= CAPACIDAD_MAXIMA:
                        servidor.sendto("Servidor lleno".encode(util.codigo), direccion)
                        continue

                    nombre = texto

                    if nombre in nombres:
                        servidor.sendto("Nombre no disponible".encode(util.codigo), direccion)
                        continue

                    clientes.append(direccion)
                    nombres.append(nombre)

                    anuncio = f"{nombre} se ha unido al chat :)"
                    print(anuncio)

                    for c in clientes:
                        servidor.sendto(anuncio.encode(util.codigo), c)

                    continue

                # Salida del usuario
                if texto == "/exit":
                    idx = clientes.index(direccion)
                    nombre = nombres[idx]

                    anuncio = f"{nombre} dejó el chat"
                    print(anuncio)

                    for c in clientes:
                        servidor.sendto(anuncio.encode(util.codigo), c)

                    clientes.pop(idx)
                    nombres.pop(idx)
                    continue

                # Mensaje privado
                if texto.startswith("/p"):
                    partes = texto.split(" ", 2)

                    if len(partes) < 3:
                        servidor.sendto("Uso: /privado Nombre Mensaje".encode(util.codigo), direccion)
                        continue

                    _, destino, cuerpo = partes

                    if destino not in nombres:
                        servidor.sendto(f"El usuario {destino} no existe".encode(util.codigo), direccion)
                        continue

                    idx_origen = clientes.index(direccion)
                    remitente = nombres[idx_origen]

                    idx_destino = nombres.index(destino)
                    direccion_destino = clientes[idx_destino]

                    # Construir dos mensajes: uno para el receptor y otro para el emisor
                    mensaje_para_receptor = f"(privado de {remitente}): {cuerpo}".encode(util.codigo)
                    mensaje_para_emisor = f"(privado para {destino}): {cuerpo}".encode(util.codigo)

                    servidor.sendto(mensaje_para_receptor, direccion_destino)
                    servidor.sendto(mensaje_para_emisor, direccion)
                    continue

                # Mensaje público
                idx = clientes.index(direccion)
                nombre = nombres[idx]

                print(f"{nombre}: {texto}")

                mensaje_final = f"{nombre}: {texto}"

                for c in clientes:
                    try:
                        servidor.sendto(mensaje_final.encode(util.codigo), c)
                    except:
                        if c in clientes:
                            idx2 = clientes.index(c)
                            clientes.pop(idx2)
                            nombres.pop(idx2)


if __name__ == "__main__":
    puerto_terminal = util.pedirPuerto()
    iniciar(int(puerto_terminal))
