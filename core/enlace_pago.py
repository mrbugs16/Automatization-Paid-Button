"""
Obtención del enlace de pago de Memphis según ORIGEN_ENLACE (manual | api | gobierno).
Cada enlace es de un solo uso, por eso cada prueba pide uno nuevo.
"""
import time

import requests

from config import settings
from core import datos
from pages.gobierno_predial_page import PredialPage


def firmar(payload):
    """TODO: la documentación (v1.4) no describe cómo se calcula mp_signature (HMAC).
    Solicitar a desarrollo el algoritmo, la cadena a firmar y la llave de QA."""
    raise NotImplementedError("Algoritmo de firma mp_signature pendiente de confirmar con desarrollo")


def generar_por_api(importe="1.00", servicio=2):
    sufijo = str(int(time.time() * 1000))[-12:]
    payload = {
        "s_transm": sufijo,                    # numérico, único
        "c_referencia": f"QA-{sufijo}",
        "t_servicio": servicio,               # 2 = predial
        "t_importe": importe,
        "s_desc": "QA automatizacion - Pago de impuesto predial",
        "t_origen": 1,
        "s_nombre": "QA Automatizacion",
        "val_9": 2,
        "val_10": "",
        "val_7": "",
        "val_8": "",
        "val_13": settings.URL_GOBIERNO,
    }
    payload["mp_signature"] = firmar(payload)
    respuesta = requests.post(settings.URL_API_TRANSMISION, json=payload, timeout=30)
    respuesta.raise_for_status()
    return settings.URL_MEMPHIS_PAYOUT.format(token=respuesta.json()["token"])


def generar_por_gobierno(driver, cuenta, evidencia=None):
    predial = PredialPage(driver)
    predial.abrir_inicio()
    predial.ir_a_predial()
    if not predial.consultar_cuenta(cuenta, evidencia):
        raise RuntimeError(f"No fue posible consultar la cuenta {cuenta['alias']} en el portal del Gobierno")
    return predial.ir_a_boton_de_pago()


def obtener_enlace_valido(driver=None, cuenta=None, evidencia=None):
    """Regresa la URL de un enlace de pago sin usar, o None si no hay de dónde sacarlo."""
    origen = settings.ORIGEN_ENLACE
    if origen == "manual":
        url = datos.consumir_enlace_valido()
    elif origen == "api":
        url = generar_por_api()
    elif origen == "gobierno":
        url = generar_por_gobierno(driver, cuenta or datos.seleccionar_cuenta(), evidencia)
    else:
        raise ValueError(f"ORIGEN_ENLACE no soportado: {origen}")
    if url and evidencia:
        evidencia.nota(f"Enlace de pago ({origen}): {url}")
    return url
