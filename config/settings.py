"""
Configuración global del proyecto Botón de Pago.

Todo se puede sobrescribir con variables de entorno, por ejemplo:
    MEMPHIS_DISPONIBLE=true CAPTCHA_MODO=manual pytest
"""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _bool(nombre, default="false"):
    return os.getenv(nombre, default).strip().lower() in ("1", "true", "si", "sí", "yes")


# ==============================================
# DRIVER (APPIUM -> GOOGLE CHROME)
# ==============================================
# appium_desktop : Appium server + driver "chromium" -> Chrome de escritorio
# appium_android : Appium server + UiAutomator2 -> Chrome en Android (TC-BP-048)
# selenium       : Chrome local sin Appium (respaldo para depurar)
MODO_DRIVER = os.getenv("MODO_DRIVER", "appium_desktop")
APPIUM_URL = os.getenv("APPIUM_URL", "http://127.0.0.1:4723")
ANDROID_DEVICE = os.getenv("ANDROID_DEVICE", "emulator-5554")
HEADLESS = _bool("HEADLESS")
VENTANA = (1440, 900)
TIMEOUT = int(os.getenv("TIMEOUT", "20"))

# ==============================================
# URLS
# ==============================================
URL_GOBIERNO = os.getenv("URL_GOBIERNO", "https://srvtestwl.pueblacapital.gob.mx:7016/pabel/")
DOMINIO_GOBIERNO = "pueblacapital.gob.mx"

DOMINIO_MEMPHIS = "pagospueblacapital-dev.memphis.mx"
URL_MEMPHIS_PAYOUT = os.getenv(
    "URL_MEMPHIS_PAYOUT", "https://pagospueblacapital-dev.memphis.mx/payout?token={token}"
)
URL_API_TRANSMISION = os.getenv(
    "URL_API_TRANSMISION", "https://centra.memphis.mx/api-dev/transmission-sequence"
)

# Con false, todas las pruebas de Memphis se reportan como "Pendiente" (útil si el ambiente cae).
MEMPHIS_DISPONIBLE = _bool("MEMPHIS_DISPONIBLE", "true")

# De dónde sale el enlace de pago para cada prueba de Memphis:
# manual   : ENLACE_PAGO o data/enlaces_prueba.json -> "vigente" (se reutiliza mientras no se pague)
# api      : se genera con POST a transmission-sequence (requiere firma HMAC)
# gobierno : se recorre el portal del Gobierno (Predial -> captcha -> pagar)
ORIGEN_ENLACE = os.getenv("ORIGEN_ENLACE", "manual")
# Trámite del Gobierno que genera el link de pago (también con --servicio):
# predial  : Pagos en línea -> Predial (cuenta predial o línea de captura)
# transito : Pagos en línea -> Infracciones (folio de infracción o línea de captura)
SERVICIO = os.getenv("SERVICIO", "predial").strip().lower()
SERVICIOS = {"predial": "Predial", "transito": "Tránsito"}
ENLACE_PAGO = os.getenv("ENLACE_PAGO", "")
# Si no hay link válido, la suite abre el portal (Predial o Infracciones según SERVICIO) y espera
# 3 min a que el tester capture la referencia/folio + captcha y dé 'Consultar'. Con false, queda Pendiente.
PEDIR_REFERENCIA = _bool("PEDIR_REFERENCIA", "true")
TIMEOUT_CAPTURA_REFERENCIA = int(os.getenv("TIMEOUT_CAPTURA_REFERENCIA", "180"))

# ==============================================
# 3D SECURE
# ==============================================
# El banco autentica con una redirección de página completa (sale de Memphis y regresa).
# manual : si el banco pide código/NIP, el script espera a que el tester lo capture
# auto   : solo espera el regreso (para tarjetas sandbox que no piden interacción)
TRESDS_MODO = os.getenv("TRESDS_MODO", "manual")

# ==============================================
# CAPTCHA (PORTAL DEL GOBIERNO)
# ==============================================
# manual        : el script espera a que el tester escriba el captcha en Chrome
# fijo          : se usa CAPTCHA_VALOR (si el Gobierno habilita un valor fijo en QA)
# deshabilitado : el ambiente de QA no muestra captcha
CAPTCHA_MODO = os.getenv("CAPTCHA_MODO", "manual")
CAPTCHA_VALOR = os.getenv("CAPTCHA_VALOR", "")
CAPTCHA_TIMEOUT = int(os.getenv("CAPTCHA_TIMEOUT", "120"))
CAPTCHA_REINTENTOS = int(os.getenv("CAPTCHA_REINTENTOS", "3"))

# ==============================================
# TIEMPOS DE NEGOCIO (CONFIRMAR CON DESARROLLO)
# ==============================================
# Máximo que TC-BP-005/044 esperan a que el token expire y la página reaccione; si no pasa nada, falla
TIMEOUT_TOKEN_SEG = int(os.getenv("TIMEOUT_TOKEN_SEG", "120"))
CONTADOR_REDIRECCION_SEG = int(os.getenv("CONTADOR_REDIRECCION_SEG", "10"))
TIMEOUT_PROCESAMIENTO = int(os.getenv("TIMEOUT_PROCESAMIENTO", "90"))
TIMEOUT_3DS_SEG = int(os.getenv("TIMEOUT_3DS_SEG", "300"))  # TODO: confirmar con el banco

# ==============================================
# DATOS Y EVIDENCIA
# ==============================================
DIR_DATOS = RAIZ / "data"
MATRIZ_XLSX = DIR_DATOS / "Matriz Pruebas Boton Pago.xlsx"
HOJA_MATRIZ = "Matriz de Pruebas"
CUENTAS_JSON = DIR_DATOS / "cuentas_predial.json"
TARJETAS_JSON = DIR_DATOS / "tarjetas_prueba.json"
TARJETAS_LOCAL_JSON = DIR_DATOS / "tarjetas_prueba.local.json"  # no se sube al repo
ENLACES_JSON = DIR_DATOS / "enlaces_prueba.json"
DIR_EVIDENCIAS = RAIZ / "evidencias"
