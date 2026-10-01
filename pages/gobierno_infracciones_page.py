"""
Portal del Gobierno de Puebla -> Pago de infracciones (Tránsito).
Es PRECONDICIÓN (Fase 1): solo se usa para llegar al enlace de pago de Memphis.
Formulario: folio de infracción (#folio) o línea de captura (#lc) + captcha + 'Consultar'.
"""
from config.locators import GobiernoLoc
from pages.gobierno_predial_page import PredialPage


class InfraccionesPage(PredialPage):

    def ir_a_infracciones(self):
        self.click(GobiernoLoc.CARD_INFRACCIONES)
        self.esperar_url_contiene("indexI")
        self.esperar_visible(GobiernoLoc.INPUT_FOLIO)

    def formulario_completo_visible(self):
        campos = [GobiernoLoc.INPUT_FOLIO, GobiernoLoc.INPUT_LINEA_CAPTURA, GobiernoLoc.IMG_CAPTCHA,
                  GobiernoLoc.INPUT_CAPTCHA, GobiernoLoc.BTN_CONSULTAR]
        return {loc[1]: self.existe(loc) for loc in campos}

    def sigue_en_formulario(self):
        return "indexI" in self.url and self.existe(GobiernoLoc.IMG_CAPTCHA, timeout=3)
