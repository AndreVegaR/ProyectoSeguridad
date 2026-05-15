import logging
import os
from logging.handlers import RotatingFileHandler

CARPETA = "bitacoras"

if not os.path.exists(CARPETA):
    os.makedirs(CARPETA)


def crear_logger(nombre, archivo):

    logger = logging.getLogger(nombre)
    logger.setLevel(logging.INFO)

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