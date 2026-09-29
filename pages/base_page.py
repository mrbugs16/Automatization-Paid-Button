"""Acciones comunes sobre cualquier pantalla (esperas, clics, escritura)."""
import platform

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        """Escribe tecla por tecla. Limpia con Cmd/Ctrl+A + Borrar para que React y las máscaras se enteren."""
        campo = self.esperar_visible(loc)
        if limpiar and self.propiedad(campo, "value"):
            modificador = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
            campo.send_keys(modificador, "a")
            campo.send_keys(Keys.BACKSPACE)
        if texto:
            campo.send_keys(texto)
        return campo

    def salir_del_campo(self, loc):
        """Quita el foco (dispara las validaciones 'onTouched' de la página)."""
        self.esperar_visible(loc).send_keys(Keys.TAB)

    def seleccionar(self, loc, valor):
        Select(self.esperar_visible(loc)).select_by_value(valor)

    def esperar_opcion(self, loc, valor, timeout=None):
        """Los catálogos (países/estados) llegan por API: espera a que exista la opción."""
        def _existe(d):
            selects = d.find_elements(*loc)
            return bool(selects) and any(o.get_attribute("value") == valor
                                         for o in selects[0].find_elements(By.TAG_NAME, "option"))

        return self._wait(timeout).until(_existe, message=f"La opción '{valor}' no apareció en {loc}")

    def opcion_seleccionada(self, loc):
        return Select(self.esperar_visible(loc)).first_selected_option.get_attribute("value")

    def texto(self, loc, timeout=None):
        return self.esperar_visible(loc, timeout).text.strip()

    def propiedad(self, elemento, nombre):
        """Lee una propiedad del DOM con JS: el driver Chromium de Appium regresa None en get_attribute."""
        return self.driver.execute_script("return arguments[0][arguments[1]];", elemento, nombre)

    def valor(self, loc):
        return self.propiedad(self.esperar_visible(loc), "value") or ""

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
