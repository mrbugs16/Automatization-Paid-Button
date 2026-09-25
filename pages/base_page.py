"""Acciones comunes sobre cualquier pantalla (esperas, clics, escritura)."""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config import settings


class BasePage:
    def __init__(self, driver, timeout=settings.TIMEOUT):
        self.driver = driver
        self.timeout = timeout

    def _wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout)

    # ---------- navegación ----------
    def abrir(self, url):
        self.driver.get(url)

    @property
    def url(self):
        return self.driver.current_url

    def recargar(self):
        self.driver.refresh()

    def atras(self):
        self.driver.back()

    def adelante(self):
        self.driver.forward()

    # ---------- esperas ----------
    def esperar_visible(self, loc, timeout=None):
        return self._wait(timeout).until(EC.visibility_of_element_located(loc), message=f"No visible: {loc}")

    def esperar_clickeable(self, loc, timeout=None):
        return self._wait(timeout).until(EC.element_to_be_clickable(loc), message=f"No clickeable: {loc}")

    def esperar_url_contiene(self, texto, timeout=None):
        return self._wait(timeout).until(EC.url_contains(texto), message=f"La URL no contiene '{texto}'")

    def existe(self, loc, timeout=3):
        try:
            self.esperar_visible(loc, timeout)
            return True
        except TimeoutException:
            return False

    # ---------- acciones ----------
    def click(self, loc):
        self.esperar_clickeable(loc).click()

    def escribir(self, loc, texto, limpiar=True):
        campo = self.esperar_visible(loc)
        if limpiar:
            campo.clear()
        if texto:
            campo.send_keys(texto)
        return campo

    def seleccionar(self, loc, valor):
        Select(self.esperar_visible(loc)).select_by_value(valor)

    def texto(self, loc, timeout=None):
        return self.esperar_visible(loc, timeout).text.strip()

    def valor(self, loc):
        return self.esperar_visible(loc).get_attribute("value") or ""

    def textos_visibles(self, loc):
        return [e.text.strip() for e in self.driver.find_elements(*loc) if e.is_displayed() and e.text.strip()]

    def scroll_a(self, loc):
        elemento = self.esperar_visible(loc)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elemento)
        return elemento

    def resaltar(self, loc, color="#e0245e"):
        elemento = self.esperar_visible(loc)
        self.driver.execute_script(
            "arguments[0].style.outline='3px solid ' + arguments[1];", elemento, color)

    def quitar_resaltado(self, loc):
        try:
            for e in self.driver.find_elements(*loc):
                self.driver.execute_script("arguments[0].style.outline='';", e)
        except Exception:
            pass
