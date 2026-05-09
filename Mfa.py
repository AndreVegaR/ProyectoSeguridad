"""
mfa.py
 
Descripción:
- Genera un código de 6 dígitos, lo envía al correo del usuario via Gmail
  y lo valida con tiempo de expiración de 5 minutos.
 
Funcionamiento:
- generar_codigo(): crea un código numérico aleatorio de 6 dígitos
- enviar_codigo(correo): genera el código, lo guarda con timestamp y lo manda por correo
- verificar_codigo(correo, codigo_ingresado): valida que el código sea correcto y no haya expirado
 
Autores:
- Julián Gerardo Izaguirre Menchaca
- Willian Alexander Tolano Fierros
- Abelardo Andre Vega Romero
-Noelia Encinas Noriega
"""
 
import smtplib
import random
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv #Para cargar las variables de entorno, es el mismo del de Java, pero con el pitón
import os #el sistema operativo 👀👀👀👀👀👀👀👀👀👀👀👀

# Método que crea un Logger en python (mucho más enredoso que java la verdad)
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s (mfa.py) - %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)

load_dotenv()  # Carga las variables de entorno desde el archivo .env   
CORREO_REMITENTE  = os.getenv("CORREO_REMITENTE")  #El correo de secreto misterioso
APP_PASSWORD      = os.getenv("APP_PASSWORD")      # Contraseña de aplicación del google (Creé una cuenta nueva para que no me hackearan)
SMTP_HOST         = "smtp.gmail.com" #Direccion del servidor SMTP de Gmail (es el protocolo de correos que vimos en clase)
SMTP_PORT         = 587 #Este es el puerto del SMTP
EXPIRACION_MIN    = 5   # El código de verificación expira después de 5 minutos
 
_codigos_activos = {} #Lista en memoria que guarda los códigos
 
 
def generar_codigo() -> str:
    #Genera un número aleatorio de 6 dígitos
    codigo = str(random.randint(100000, 999999))
    log.debug(f"Código generado: {codigo}")
    return codigo
 
 
def enviar_codigo(correo: str) -> bool:
    #Genera un código aleatorio con la función de arriba,  y lo guarda en la variable _codigos_activos con su tiempo de expiración
    codigo = generar_codigo()
    expira = datetime.now() + timedelta(minutes=EXPIRACION_MIN)
    _codigos_activos[correo] = {"codigo": codigo, "expira": expira}
 
    log.info(f"Intentando enviar código a {correo}, expira a las {expira.strftime('%H:%M:%S')}")
 
    try:
        #La librería email.mime.multipart sirve para enviar un mensaje con formato
        mensaje = MIMEMultipart()
        mensaje["From"]    = CORREO_REMITENTE
        mensaje["To"]      = correo
        mensaje["Subject"] = "PotroChat - Código de verificación"
 
        cuerpo = (
            f"Hola,\n\n"
            f"Tu código de verificación para entrar al PotroChat es:\n\n"
            f"    {codigo}\n\n"
            f"Este código expira en {EXPIRACION_MIN} minutos.\n"
        )
        mensaje.attach(MIMEText(cuerpo, "plain"))
 
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as servidor_smtp:
            servidor_smtp.ehlo() #saluda al servidor
            servidor_smtp.starttls() #Usa el cifrado TLS que vimos en clase
            servidor_smtp.ehlo() #Saluda al servidor de nuevo, ahora con el cifrado TLS
            servidor_smtp.login(CORREO_REMITENTE, APP_PASSWORD) #Autentica con las credenciales del .env
            servidor_smtp.sendmail(CORREO_REMITENTE, correo, mensaje.as_string()) #Envía el correo
 
        log.info(f"Código enviado exitosamente a {correo}")
        return True
 
    except smtplib.SMTPAuthenticationError:
        log.error("Fallo de autenticación con Gmail.")
        return False
    except smtplib.SMTPException as e:
        log.error(f"Error SMTP al enviar a {correo}: {e}")
        return False
    except Exception as e:
        log.error(f"Error inesperado al enviar correo a {correo}: {e}")
        return False
 
 
def verificar_codigo(correo: str, codigo_ingresado: str) -> tuple[bool, str]:
    log.debug(f"Verificando código para {correo}: ingresado='{codigo_ingresado}'")
 
    if correo not in _codigos_activos:
        log.warning(f"No hay código activo para {correo}")
        return False, "no_existe"
 
    codigo = _codigos_activos[correo]
 
    if datetime.now() > codigo["expira"]:
        log.warning(f"Código expirado para {correo}")
        del _codigos_activos[correo]
        return False, "expirado"
 
    if codigo_ingresado.strip() != codigo["codigo"]:
        log.warning(f"Código incorrecto para {correo}")
        return False, "incorrecto"
 
    # si pasa todas las excepciones se borra el código para que ya no se pueda usar
    del _codigos_activos[correo]
    log.info(f"Código verificado correctamente para {correo}")
    return True, "ok"