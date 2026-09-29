"""
Manejo del captcha del portal del Gobierno.

El captcha es un control de seguridad del Gobierno y cambia en cada carga, por eso
NO se intenta leer con OCR. Opciones soportadas (CAPTCHA_MODO):

- manual        : el script resalta el campo y espera a que el tester escriba el código
                  directamente en Chrome; en cuanto el campo tiene 5 caracteres, continúa.
- fijo          : usa CAPTCHA_VALOR (si el equipo del Gobierno configura un valor fijo en QA).
- deshabilitado : el ambiente de QA no muestra captcha.
"""
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait

from config import settings
from config.locators import GobiernoLoc


def resolver_captcha(page, evidencia=None):
    modo = settings.CAPTCHA_MODO
    if modo == "deshabilitado":
        return

    campo = page.esperar_visible(GobiernoLoc.INPUT_CAPTCHA)
    campo.clear()

    if modo == "fijo":
        if not settings.CAPTCHA_VALOR:
            raise ValueError("CAPTCHA_MODO=fijo requiere la variable CAPTCHA_VALOR")
        campo.send_keys(settings.CAPTCHA_VALOR)
        return

    longitud = int(campo.get_attribute("maxlength") or 5)
    page.scroll_a(GobiernoLoc.IMG_CAPTCHA)
    page.resaltar(GobiernoLoc.INPUT_CAPTCHA)
    campo.click()
    if evidencia:
        evidencia.captura("Captcha mostrado - esperando captura manual")

    print("\n" + "=" * 60)
    print(f"🔐 CAPTCHA: escribe el código de la imagen en Chrome ({longitud} caracteres).")
    print("   No presiones Enter; el script da clic en 'Consultar' por ti.")
    print(f"   Tiempo máximo: {settings.CAPTCHA_TIMEOUT} s")
    print("=" * 60)

    def _capturado(_):
        try:
            return len(page.propiedad(campo, "value") or "") >= longitud
        except StaleElementReferenceException:
            return True  # el tester envió el formulario manualmente

    WebDriverWait(page.driver, settings.CAPTCHA_TIMEOUT, poll_frequency=0.5).until(
        _capturado, message="No se capturó el captcha a tiempo"
    )
    page.quitar_resaltado(GobiernoLoc.INPUT_CAPTCHA)
