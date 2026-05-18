import logging
import os
#Esto es lo que permite guardar logs en archivos
from logging.handlers import RotatingFileHandler

#Nombre de la carpeta donde se guardan las bitácoras
CARPETA = "bitacoras"

#Revisa si existe la carpeta de bitácoras, si no existe, la crea con la función makedirs (como la del linux)
if not os.path.exists(CARPETA):
    os.makedirs(CARPETA)

#Función que crea y configura un logger, recibe dos parámetros, el primero siendo el nombre del logger, y el segundo el archivo
#Donde se guardará
def crear_logger(nombre, archivo):

    #Obtiene el logger con el nombre del parámetro, en caso de no existir, lo crea
    logger = logging.getLogger(nombre)
    #define el nivel mínimo de todos los loggers (exluye al de debug)
    logger.setLevel(logging.INFO)

    #Revisa si el logger ya tiene manejadores agregados
    if not logger.handlers:

        handler = RotatingFileHandler(
            f"{CARPETA}/{archivo}",
            maxBytes=5 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8"
        )

        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        handler.setFormatter(formato)
        logger.addHandler(handler)

    return logger


accesos = crear_logger("ACCESOS", "accesos.log")
mfa = crear_logger("MFA", "mfa.log")
mensajes = crear_logger("MENSAJES", "mensajes.log")
errores = crear_logger("ERRORES", "errores.log")
servidor = crear_logger("SERVIDOR", "servidor.log")
sospechosos = crear_logger("SOSPECHOSOS", "sospechosos.log")