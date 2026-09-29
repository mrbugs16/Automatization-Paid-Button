"""
Portal del Gobierno de Puebla -> COMPROBANTE DE PAGO.
Es la pantalla a la que redirige el Botón de Pago al terminar un pago aprobado (Fase 3).
Los datos se leen por etiqueta visible porque la página no tiene ids en esos campos.
"""
import re

from config.locators import GobiernoLoc
from pages.base_page import BasePage

ETIQUETAS = {
    "tarjetahabiente": r"Nombre del\s+Tarjetahabiente:",
    "institucion": r"Instituci[oó]n\s+Financiera:",
    "tipo_pago": r"Tipo de Pago:",
    "fecha": r"Fecha de Pago:",
    "autorizacion": r"Autorizaci[oó]n\s+Bancaria:",
}


class ComprobanteGobiernoPage(BasePage):

    def visible(self, timeout=30):
        return self.existe(GobiernoLoc.COMPROBANTE_TITULO, timeout)

    def datos(self):
        """{'tarjetahabiente': ..., 'institucion': ..., 'tipo_pago': ..., 'fecha': ..., 'autorizacion': ...}"""
        texto = self.driver.find_element("css selector", "body").text
        etiquetas = "|".join(ETIQUETAS.values())
        datos = {}
        for clave, etiqueta in ETIQUETAS.items():
            m = re.search(rf"{etiqueta}\s*(.+?)\s*(?={etiquetas}|Si desea imprimir|$)", texto, re.S)
            datos[clave] = " ".join(m.group(1).split()) if m else ""
        return datos

    def fecha_sin_leyenda(self):
        """Fecha tal como se muestra, sin el texto 'Formato(...)' que la página agrega."""
        return self.datos()["fecha"].split("Formato")[0].strip()

    def abrir_pdf(self):
        ventanas = set(self.driver.window_handles)
        self.click(GobiernoLoc.BTN_COMPROBANTE_PDF)
        return ventanas

    def inicio(self):
        self.click(GobiernoLoc.BTN_INICIO)
