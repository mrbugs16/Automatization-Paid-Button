"""
Obtención del enlace de pago de Memphis según ORIGEN_ENLACE (manual | api | gobierno).
El enlace se puede reutilizar mientras el pago no se apruebe.
"""
import select
import sys
import time
from urllib.parse import urlparse

import requests
from selenium.common.exceptions import WebDriverException

from config import settings
from config.locators import GobiernoLoc
from core import datos
from pages.gobierno_infracciones_page import InfraccionesPage
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


# Si el tester elige "saltar", no se vuelve a pedir referencia en el resto de la corrida
captura_saltada = False


def _tester_pidio_saltar():
    """Lee sin bloquear la terminal: 's', '4' o 'saltar' + Enter salta la captura."""
    try:
        if not sys.stdin.isatty():
            return False
        listo, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(listo) and sys.stdin.readline().strip().lower() in ("s", "4", "saltar")
    except (OSError, ValueError, AttributeError):
        return False  # sin terminal interactiva (ej. panel de Testing): solo aplica el tiempo límite


def _abrir_formulario_portal(driver):
    """Abre en el portal el formulario del trámite configurado (SERVICIO). Regresa (página, pantalla, qué capturar)."""
    if settings.SERVICIO == "transito":
        pagina = InfraccionesPage(driver)
        pagina.abrir_inicio()
        pagina.ir_a_infracciones()
        return pagina, "Pago de infracciones", "el folio de infracción o la línea de captura"
    pagina = PredialPage(driver)
    pagina.abrir_inicio()
    pagina.ir_a_predial()
    return pagina, "Pago de predial", "la cuenta predial (tipo, cuenta y delegación) o la línea de captura"


def capturar_desde_portal(driver, evidencia=None, timeout=settings.TIMEOUT_CAPTURA_REFERENCIA):
    """Abre Predial o Infracciones (según SERVICIO) y espera a que el tester capture la referencia/folio
    + captcha y dé 'Consultar'. En la pantalla del adeudo intenta dar clic en el botón de pago; si no lo
    encuentra, lo da el tester. Regresa la URL del botón de pago de Memphis, o None si se agotó el tiempo
    o el tester saltó."""
    global captura_saltada
    if captura_saltada:
        return None
    pagina, pantalla, que_capturar = _abrir_formulario_portal(driver)
    pagina.scroll_a(GobiernoLoc.INPUT_CAPTCHA)
    if evidencia:
        evidencia.captura(f"Portal - {pantalla}: esperando referencia y captcha")

    print("\n" + "=" * 64)
    plazo = f"{timeout // 60} min" if timeout % 60 == 0 else f"{timeout} s"
    print(f"🧾 SE NECESITA UNA REFERENCIA NUEVA DE {settings.SERVICIOS[settings.SERVICIO].upper()} (tienes {plazo}):")
    print(f"   1. En Chrome ('{pantalla}'), captura {que_capturar}.")
    print("   2. Captura el captcha y da clic en 'Consultar'.")
    print("   3. Si en la siguiente pantalla no avanza solo, da clic en el botón de pago.")
    print("   4. ¿No tienes referencias? Escribe  s  y presiona Enter en esta terminal para SALTAR")
    print("      (no se volverá a pedir en esta corrida; esas pruebas quedan Pendiente).")
    print("=" * 64)

    limite = time.time() + timeout
    intento_boton = False
    while time.time() < limite:
        if _tester_pidio_saltar():
            captura_saltada = True
            print("   ⏭️  Captura de referencia saltada: el resto de pruebas sin link quedarán Pendiente.")
            if evidencia:
                evidencia.nota("El tester saltó la captura de referencia")
            return None
        try:
            url = _link_memphis_actual(driver)
            if url:
                if evidencia:
                    evidencia.captura("Botón de pago abierto desde el portal")
                return url
            # Ya no está el captcha: el tester dio 'Consultar' y se muestra el detalle del adeudo
            en_portal = settings.DOMINIO_GOBIERNO in driver.current_url
            if en_portal and not intento_boton and not pagina.existe(GobiernoLoc.IMG_CAPTCHA, timeout=1):
                intento_boton = True
                if pagina.existe(GobiernoLoc.BTN_PAGAR_EN_LINEA, timeout=3):
                    if evidencia:
                        evidencia.captura("Portal - detalle del adeudo")
                    pagina.click(GobiernoLoc.BTN_PAGAR_EN_LINEA)
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
