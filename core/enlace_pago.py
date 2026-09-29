"""
Obtención del enlace de pago de Memphis según ORIGEN_ENLACE (manual | api | gobierno).
El enlace se puede reutilizar mientras el pago no se apruebe.
"""
import time
from urllib.parse import urlparse

import requests
from selenium.common.exceptions import WebDriverException

from config import settings
from config.locators import GobiernoLoc
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


def _link_memphis_actual(driver):
    """URL del botón de pago con token e identifier. La app limpia la URL al cargar,
    pero guarda ambos valores en sessionStorage (payment_uuid / payment_identifier)."""
    url = driver.current_url
    host = urlparse(url).hostname or ""
    if not host.endswith("memphis.mx"):
        return None
    if "token=" in url and "identifier=" in url:
        return url
    token, identificador = driver.execute_script(
        "return [sessionStorage.getItem('payment_uuid'), sessionStorage.getItem('payment_identifier')];")
    if token and identificador:
        return f"https://{host}/payout?token={token}&identifier={identificador}"
    return None


def capturar_desde_portal(driver, evidencia=None, timeout=settings.TIMEOUT_CAPTURA_REFERENCIA):
    """Abre Predial y espera a que el tester capture la referencia/folio + captcha y dé 'Consultar'.
    En la pantalla del adeudo intenta dar clic en el botón de pago; si no lo encuentra, lo da el tester.
    Regresa la URL del botón de pago de Memphis, o None si se agotó el tiempo."""
    predial = PredialPage(driver)
    predial.abrir_inicio()
    predial.ir_a_predial()
    predial.scroll_a(GobiernoLoc.INPUT_CAPTCHA)
    if evidencia:
        evidencia.captura("Portal - Pago de predial: esperando referencia y captcha")

    print("\n" + "=" * 64)
    print(f"🧾 SE NECESITA UNA REFERENCIA NUEVA (tienes {timeout // 60} min):")
    print("   1. En Chrome, captura la referencia / línea de captura / cuenta.")
    print("   2. Captura el captcha y da clic en 'Consultar'.")
    print("   3. Si en la siguiente pantalla no avanza solo, da clic en el botón de pago.")
    print("=" * 64)

    limite = time.time() + timeout
    intento_boton = False
    while time.time() < limite:
        try:
            url = _link_memphis_actual(driver)
            if url:
                if evidencia:
                    evidencia.captura("Botón de pago abierto desde el portal")
                return url
            if "indexI" in driver.current_url and not intento_boton:
                intento_boton = True
                if predial.existe(GobiernoLoc.BTN_PAGAR_EN_LINEA, timeout=3):
                    if evidencia:
                        evidencia.captura("Portal - detalle del adeudo")
                    predial.click(GobiernoLoc.BTN_PAGAR_EN_LINEA)
        except WebDriverException:
            pass  # la página está navegando
        time.sleep(0.5)
    return None


def obtener_enlace_valido(driver=None, cuenta=None, evidencia=None):
    """Regresa la URL de un enlace de pago sin usar, o None si no hay de dónde sacarlo."""
    origen = settings.ORIGEN_ENLACE
    if origen == "manual":
        url = datos.enlace_vigente()
    elif origen == "api":
        url = generar_por_api()
    elif origen == "gobierno":
        url = generar_por_gobierno(driver, cuenta or datos.seleccionar_cuenta(), evidencia)
    else:
        raise ValueError(f"ORIGEN_ENLACE no soportado: {origen}")
    if url and evidencia:
        evidencia.nota(f"Enlace de pago ({origen}): {url}")
    return url
