"""
Pantallas del Botón de Pago Memphis (alcance QA, Fase 2).
Locators provisionales en config/locators.py hasta que la página esté publicada.
"""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from config import settings
from config.datos_prueba import CONTACTO_VALIDO, DIRECCION_VALIDA
from config.locators import (ContactoLoc, DireccionLoc, ProcesamientoLoc, ResultadoLoc,
                             TarjetaLoc, ValidacionLoc)
from pages.base_page import BasePage


class ValidacionPage(BasePage):
    def esperar_fin_validacion(self, timeout=30):
        """Espera a que termine la pantalla de validación y aparezca el formulario, un error o 'ya pagado'."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: any(d.find_elements(*loc) for loc in
                          (ContactoLoc.PASO, ValidacionLoc.MENSAJE_ERROR, ValidacionLoc.MENSAJE_YA_PAGADO)),
            message="La validación del enlace no terminó")

    def muestra_formulario(self):
        return self.existe(ContactoLoc.PASO)

    def muestra_error(self):
        return self.existe(ValidacionLoc.MENSAJE_ERROR)

    def muestra_ya_pagado(self):
        return self.existe(ValidacionLoc.MENSAJE_YA_PAGADO)

    def resumen(self):
        return {
            "importe": self.texto(ValidacionLoc.RESUMEN_IMPORTE),
            "concepto": self.texto(ValidacionLoc.RESUMEN_CONCEPTO),
            "referencia": self.texto(ValidacionLoc.RESUMEN_REFERENCIA),
        }


class ContactoPage(BasePage):
    def llenar(self, telefono="", correo=""):
        self.escribir(ContactoLoc.INPUT_TELEFONO, telefono)
        self.escribir(ContactoLoc.INPUT_CORREO, correo)

    def continuar(self):
        self.click(ContactoLoc.BTN_CONTINUAR)

    def valores(self):
        return {"telefono": self.valor(ContactoLoc.INPUT_TELEFONO), "correo": self.valor(ContactoLoc.INPUT_CORREO)}

    def error_telefono(self):
        return self.existe(ContactoLoc.ERROR_TELEFONO)

    def error_correo(self):
        return self.existe(ContactoLoc.ERROR_CORREO)

    def sigue_en_paso(self):
        return self.existe(ContactoLoc.PASO, timeout=2) and not self.existe(DireccionLoc.PASO, timeout=2)


class DireccionPage(BasePage):
    def visible(self, timeout=10):
        return self.existe(DireccionLoc.PASO, timeout)

    def llenar(self, cp="", calle="", numero="", estado=""):
        self.escribir(DireccionLoc.INPUT_CP, cp)
        self.escribir(DireccionLoc.INPUT_CALLE, calle)
        self.escribir(DireccionLoc.INPUT_NUMERO, numero)
        self.escribir(DireccionLoc.INPUT_ESTADO, estado)  # TODO: puede ser <select> o autollenado por CP

    def continuar(self):
        self.click(DireccionLoc.BTN_CONTINUAR)

    def regresar(self):
        self.click(DireccionLoc.BTN_REGRESAR)

    def errores(self):
        return self.textos_visibles(DireccionLoc.ERRORES)

    def error_cp(self):
        return self.texto(DireccionLoc.ERROR_CP) if self.existe(DireccionLoc.ERROR_CP) else ""

    def sigue_en_paso(self):
        return self.visible(2) and not self.existe(TarjetaLoc.PASO, timeout=2)


class TarjetaPage(BasePage):
    def visible(self, timeout=10):
        return self.existe(TarjetaLoc.PASO, timeout)

    def llenar(self, numero="", nombre="", vigencia="", cvv=""):
        if TarjetaLoc.IFRAME:
            self.driver.switch_to.frame(self.esperar_visible(TarjetaLoc.IFRAME))
        self.escribir(TarjetaLoc.INPUT_NUMERO, numero)
        self.escribir(TarjetaLoc.INPUT_NOMBRE, nombre)
        self.escribir(TarjetaLoc.INPUT_VIGENCIA, vigencia)
        self.escribir(TarjetaLoc.INPUT_CVV, cvv)
        if TarjetaLoc.IFRAME:
            self.driver.switch_to.default_content()

    def llenar_con(self, tarjeta):
        self.llenar(tarjeta["numero"], tarjeta["nombre"], tarjeta["vigencia"], tarjeta["cvv"])

    def pagar(self):
        self.click(TarjetaLoc.BTN_PAGAR)

    def numero_mostrado(self):
        return self.valor(TarjetaLoc.INPUT_NUMERO)

    def errores(self):
        return self.textos_visibles(TarjetaLoc.ERRORES)

    def existe_error(self, loc):
        return self.existe(loc)

    def sigue_en_paso(self):
        return self.visible(2) and not self.existe(ProcesamientoLoc.PANTALLA_PROCESANDO, timeout=2)


class ProcesamientoPage(BasePage):
    def procesando_visible(self, timeout=10):
        return self.existe(ProcesamientoLoc.PANTALLA_PROCESANDO, timeout)

    def es_3ds(self, timeout=20):
        return self.existe(ProcesamientoLoc.IFRAME_3DS, timeout)

    def _entrar_3ds(self):
        self.driver.switch_to.frame(self.esperar_visible(ProcesamientoLoc.IFRAME_3DS))

    def autenticar_3ds(self, codigo):
        self._entrar_3ds()
        self.escribir(ProcesamientoLoc.INPUT_CODIGO_3DS, codigo)
        self.click(ProcesamientoLoc.BTN_ENVIAR_3DS)
        self.driver.switch_to.default_content()

    def cancelar_3ds(self):
        self._entrar_3ds()
        self.click(ProcesamientoLoc.BTN_CANCELAR_3DS)
        self.driver.switch_to.default_content()

    def popup_error(self, timeout=30):
        return self.texto(ProcesamientoLoc.POPUP_ERROR, timeout) if self.existe(ProcesamientoLoc.POPUP_ERROR, timeout) else ""


class ResultadoPage(BasePage):
    def esperar(self, timeout=settings.TIMEOUT_PROCESAMIENTO):
        """Regresa 'aprobada' o 'rechazada' según la pantalla final."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_elements(*ResultadoLoc.APROBADA) or d.find_elements(*ResultadoLoc.RECHAZADA),
            message="No apareció la pantalla de resultado")
        return "aprobada" if self.driver.find_elements(*ResultadoLoc.APROBADA) else "rechazada"

    def aprobada(self):
        return self.existe(ResultadoLoc.APROBADA)

    def rechazada(self):
        return self.existe(ResultadoLoc.RECHAZADA)

    def datos(self):
        return {
            "referencia": self.texto(ResultadoLoc.REFERENCIA) if self.existe(ResultadoLoc.REFERENCIA) else "",
            "folio": self.texto(ResultadoLoc.FOLIO) if self.existe(ResultadoLoc.FOLIO) else "",
            "mensaje": self.texto(ResultadoLoc.MENSAJE) if self.existe(ResultadoLoc.MENSAJE) else "",
        }

    def contador(self):
        return self.texto(ResultadoLoc.CONTADOR)

    def continuar(self):
        self.click(ResultadoLoc.BTN_CONTINUAR)

    def reintentar(self):
        self.click(ResultadoLoc.BTN_REINTENTAR)

    def puede_reintentar(self):
        return self.existe(ResultadoLoc.BTN_REINTENTAR)

    def esperar_redireccion_gobierno(self, timeout):
        try:
            self.esperar_url_contiene(settings.DOMINIO_GOBIERNO, timeout)
            return True
        except TimeoutException:
            return False


class FlujoPago:
    """Atajos para recorrer el flujo completo del botón de pago."""

    def __init__(self, driver):
        self.driver = driver
        self.validacion = ValidacionPage(driver)
        self.contacto = ContactoPage(driver)
        self.direccion = DireccionPage(driver)
        self.tarjeta = TarjetaPage(driver)
        self.procesamiento = ProcesamientoPage(driver)
        self.resultado = ResultadoPage(driver)

    def abrir_enlace(self, url):
        self.driver.get(url)
        self.validacion.esperar_fin_validacion()

    def hasta_direccion(self, url, contacto=CONTACTO_VALIDO):
        self.abrir_enlace(url)
        self.contacto.llenar(**contacto)
        self.contacto.continuar()
        assert self.direccion.visible(), "No se avanzó al Paso 2 - Dirección"

    def hasta_tarjeta(self, url, contacto=CONTACTO_VALIDO, direccion=DIRECCION_VALIDA):
        self.hasta_direccion(url, contacto)
        self.direccion.llenar(**direccion)
        self.direccion.continuar()
        assert self.tarjeta.visible(), "No se avanzó al Paso 3 - Tarjeta"

    def pagar(self, url, tarjeta, completar_3ds=True):
        """Recorre todo el flujo y regresa 'aprobada' / 'rechazada'."""
        self.hasta_tarjeta(url)
        self.tarjeta.llenar_con(tarjeta)
        self.tarjeta.pagar()
        if tarjeta.get("requiere_3ds") and completar_3ds and self.procesamiento.es_3ds():
            self.procesamiento.autenticar_3ds(tarjeta["codigo_3ds"])
        return self.resultado.esperar()
