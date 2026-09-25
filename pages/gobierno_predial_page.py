"""
Portal del Gobierno de Puebla -> Pago de predial.
Es PRECONDICIÓN (Fase 1): solo se usa para llegar al enlace de pago de Memphis.
"""
from config import settings
from config.locators import GobiernoLoc
from core.captcha import resolver_captcha
from pages.base_page import BasePage


class PredialPage(BasePage):

    def abrir_inicio(self):
        self.abrir(settings.URL_GOBIERNO)
        self.esperar_visible(GobiernoLoc.CARD_PREDIAL)

    def ir_a_predial(self):
        self.click(GobiernoLoc.CARD_PREDIAL)
        self.esperar_url_contiene("iniciopredial")
        self.esperar_visible(GobiernoLoc.INPUT_CUENTA)

    def formulario_completo_visible(self):
        campos = [GobiernoLoc.SELECT_TIPO, GobiernoLoc.INPUT_CUENTA, GobiernoLoc.INPUT_DELEGACION,
                  GobiernoLoc.INPUT_LINEA_CAPTURA, GobiernoLoc.IMG_CAPTCHA, GobiernoLoc.INPUT_CAPTCHA,
                  GobiernoLoc.BTN_CONSULTAR]
        return {loc[1]: self.existe(loc) for loc in campos}

    def llenar_cuenta(self, cuenta):
        """Llena por línea de captura si viene en la cuenta; si no, por tipo + cuenta + delegación."""
        if cuenta.get("linea_captura"):
            self.escribir(GobiernoLoc.INPUT_LINEA_CAPTURA, cuenta["linea_captura"])
        else:
            self.seleccionar(GobiernoLoc.SELECT_TIPO, cuenta["tipo"])
            self.escribir(GobiernoLoc.INPUT_CUENTA, cuenta["cuenta"])
            self.escribir(GobiernoLoc.INPUT_DELEGACION, cuenta["delegacion"])

    def refrescar_captcha(self):
        self.click(GobiernoLoc.BTN_REFRESCAR_CAPTCHA)

    def consultar(self):
        self.click(GobiernoLoc.BTN_CONSULTAR)

    def sigue_en_formulario(self):
        return "iniciopredial" in self.url and self.existe(GobiernoLoc.IMG_CAPTCHA, timeout=3)

    def mensaje_error(self):
        textos = self.textos_visibles(GobiernoLoc.MENSAJE_ERROR)
        return " | ".join(textos)

    def consultar_cuenta(self, cuenta, evidencia=None):
        """Llena la cuenta, resuelve captcha y consulta. Reintenta si el captcha fue incorrecto."""
        for intento in range(1, settings.CAPTCHA_REINTENTOS + 1):
            self.llenar_cuenta(cuenta)
            if evidencia:
                evidencia.captura(f"Datos de cuenta capturados ({cuenta['alias']}) - intento {intento}")
            resolver_captcha(self, evidencia)
            self.consultar()
            if not self.sigue_en_formulario():
                return True
            if evidencia:
                evidencia.captura(f"Consulta rechazada: {self.mensaje_error() or 'sin mensaje'}", estado="fallo")
        return False

    def ir_a_boton_de_pago(self):
        """TODO: confirmar el botón del portal que redirige al botón de pago de Memphis."""
        self.click(GobiernoLoc.BTN_PAGAR_EN_LINEA)
        self.esperar_url_contiene("payout?token=", timeout=60)
        return self.url
