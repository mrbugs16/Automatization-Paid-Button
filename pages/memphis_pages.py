"""
Pantallas del Botón de Pago Memphis (alcance QA, Fase 2).

Flujo real: Validando link -> 1 Contacto -> 2 Dirección -> 3 Datos de Tarjeta
            -> 4 Pago (confirmación) -> [3DS en el sitio del banco] -> Resultado
"""
import time
from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from config import settings
from config.datos_prueba import CONTACTO_VALIDO, DIRECCION_VALIDA, TITULO_APROBADA, TITULO_RECHAZADA
from core import datos
from config.locators import (ConfirmacionLoc, ContactoLoc, DireccionLoc, EncabezadoLoc, FormularioLoc,
                             ResultadoLoc, TarjetaLoc, ValidacionLoc, boton_paso, error_de, opcion_msi)
from pages.base_page import BasePage


class MemphisPage(BasePage):
    """Acciones compartidas por los 4 pasos del formulario."""

    def continuar(self):
        self.click(FormularioLoc.BTN_CONTINUAR)

    def regresar(self):
        self.click(FormularioLoc.BTN_REGRESAR)

    def error(self, id_campo, timeout=2):
        """Texto del error del campo, o '' si no hay error.
        Se lee aunque no esté visible: la página oculta el mensaje mientras el campo tiene el foco."""
        try:
            elemento = self._wait(timeout).until(lambda d: d.find_elements(*error_de(id_campo)))[0]
            return (self.propiedad(elemento, "textContent") or "").strip()
        except TimeoutException:
            return ""

    def errores(self):
        return [(self.propiedad(e, "textContent") or "").strip()
                for e in self.driver.find_elements(*FormularioLoc.ERRORES)]

    def paso_activo(self):
        return int(self.texto(EncabezadoLoc.PASO_ACTIVO))

    def ir_al_paso(self, numero):
        self.click(boton_paso(numero))


# ==============================================
# VALIDACIÓN DEL ENLACE Y ENCABEZADO
# ==============================================
class ValidacionPage(MemphisPage):
    def esperar_fin_validacion(self, timeout=30):
        """Espera a que termine 'Validando link de pago'. Regresa: formulario | invalido | resultado."""
        def _estado(d):
            if d.find_elements(*ContactoLoc.INPUT_CORREO):
                return "formulario"
            if self._es_invalido(d):
                return "invalido"
            if d.find_elements(*ResultadoLoc.TITULO):
                return "resultado"
            return False
        return WebDriverWait(self.driver, timeout).until(_estado, message="La validación del enlace no terminó")

    @staticmethod
    def _es_invalido(driver):
        # "Validando link de pago" y "Link de pago no válido" usan la misma clase; la carga tiene spinner
        return bool(driver.find_elements(*ValidacionLoc.ENCABEZADO_ESTADO)) and \
            not driver.find_elements(*ValidacionLoc.SPINNER)

    def muestra_formulario(self):
        return self.existe(ContactoLoc.INPUT_CORREO)

    def esperar_reaccion_por_token(self, timeout=settings.TIMEOUT_TOKEN_SEG):
        """Vigila la página sin tocarla hasta 'timeout' segundos. Regresa qué pasó al expirar el token
        ('recargo' | 'revalidando' | 'invalido' | 'cambio de URL') o None si no pasó nada."""
        url_inicial = self.driver.current_url
        self.driver.execute_script("window.__qa_marca = true;")  # desaparece si la página se recarga
        limite = time.time() + timeout
        while time.time() < limite:
            if not self.driver.execute_script("return window.__qa_marca === true;"):
                return "recargo"
            if self.driver.find_elements(*ValidacionLoc.SPINNER):
                return "revalidando"
            if self._es_invalido(self.driver):
                return "invalido"
            if self.driver.current_url != url_inicial:
                return "cambio de URL"
            time.sleep(2)
        return None

    def muestra_invalido(self):
        return self._es_invalido(self.driver)

    def mensaje_invalido(self):
        return f"{self.texto(ValidacionLoc.ENCABEZADO_ESTADO)} - {self.texto(ValidacionLoc.MENSAJE_ESTADO)}"

    def encabezado(self):
        """{'importe': '$2280.45', 'concepto': '...', 'fecha': '...', 'Solicitante': '', 'Descripción': ..., 'Referencia': ...}"""
        datos = {
            "importe": self.texto(EncabezadoLoc.IMPORTE),
            "concepto": self.texto(EncabezadoLoc.CONCEPTO).replace("Concepto de pago:", "").strip(),
            "fecha": self.texto(EncabezadoLoc.FECHA),
        }
        for fila in self.driver.find_elements(*EncabezadoLoc.FILAS):
            etiqueta, _, valor = fila.text.partition(":")
            datos[etiqueta.strip()] = valor.strip()
        return datos


# ==============================================
# PASO 1 - CONTACTO
# ==============================================
class ContactoPage(MemphisPage):
    def visible(self, timeout=10):
        return self.existe(ContactoLoc.INPUT_CORREO, timeout)

    def llenar(self, telefono="", correo=""):
        self.escribir(ContactoLoc.INPUT_TELEFONO, telefono)
        self.escribir(ContactoLoc.INPUT_CORREO, correo)

    def telefono_mostrado(self):
        """Texto tal cual aparece en el campo (la página le da formato, ej. '(5540) 076-333')."""
        return self.valor(ContactoLoc.INPUT_TELEFONO)

    def valores(self):
        """Teléfono solo con dígitos, para comparar datos sin depender del formato visual."""
        return {"telefono": "".join(c for c in self.telefono_mostrado() if c.isdigit()),
                "correo": self.valor(ContactoLoc.INPUT_CORREO)}

    def error_telefono(self):
        return self.error("mobile")

    def error_correo(self):
        return self.error("email")


# ==============================================
# PASO 2 - DIRECCIÓN
# ==============================================
class DireccionPage(MemphisPage):
    def visible(self, timeout=10):
        return self.existe(DireccionLoc.INPUT_CALLE, timeout)

    def llenar(self, calle="", cp="", ciudad="", pais="MEX", estado=""):
        self.escribir(DireccionLoc.INPUT_CALLE, calle)
        self.escribir(DireccionLoc.INPUT_CP, cp)
        self.escribir(DireccionLoc.INPUT_CIUDAD, ciudad)
        if pais:
            self.esperar_opcion(DireccionLoc.SELECT_PAIS, pais)
            if self.opcion_seleccionada(DireccionLoc.SELECT_PAIS) != pais:
                self.seleccionar(DireccionLoc.SELECT_PAIS, pais)
        if estado:
            self.esperar_opcion(DireccionLoc.SELECT_ESTADO, estado)  # el catálogo depende del país
            self.seleccionar(DireccionLoc.SELECT_ESTADO, estado)

    def valores(self):
        return {
            "calle": self.valor(DireccionLoc.INPUT_CALLE),
            "cp": self.valor(DireccionLoc.INPUT_CP),
            "ciudad": self.valor(DireccionLoc.INPUT_CIUDAD),
            "pais": self.opcion_seleccionada(DireccionLoc.SELECT_PAIS),
            "estado": self.opcion_seleccionada(DireccionLoc.SELECT_ESTADO),
        }

    def error_cp(self):
        return self.error("zip-code")

    def mensaje_nativo_estado(self):
        """El select de Estado tiene 'required' HTML: Chrome muestra su propio globo (en inglés)
        y bloquea el envío antes de las validaciones de la página."""
        return self.propiedad(self.esperar_visible(DireccionLoc.SELECT_ESTADO), "validationMessage") or ""


# ==============================================
# PASO 3 - DATOS DE TARJETA
# ==============================================
class TarjetaPage(MemphisPage):
    def visible(self, timeout=10):
        return self.existe(TarjetaLoc.INPUT_NUMERO, timeout)

    def llenar(self, nombre="", apellido="", numero="", vigencia="", cvv=""):
        self.escribir(TarjetaLoc.INPUT_NOMBRE, nombre)
        self.escribir(TarjetaLoc.INPUT_APELLIDO, apellido)
        self.escribir(TarjetaLoc.INPUT_NUMERO, numero)
        self.escribir(TarjetaLoc.INPUT_VIGENCIA, vigencia)
        self.escribir(TarjetaLoc.INPUT_CVV, cvv)

    def llenar_con(self, tarjeta, **cambios):
        datos = {k: tarjeta[k] for k in ("nombre", "apellido", "numero", "vigencia", "cvv")}
        self.llenar(**{**datos, **cambios})

    def valores(self):
        return {
            "nombre": self.valor(TarjetaLoc.INPUT_NOMBRE),
            "apellido": self.valor(TarjetaLoc.INPUT_APELLIDO),
            "numero": self.valor(TarjetaLoc.INPUT_NUMERO),
            "vigencia": self.valor(TarjetaLoc.INPUT_VIGENCIA),
            "cvv": self.valor(TarjetaLoc.INPUT_CVV),
        }

    def tipo_cvv(self):
        return self.esperar_visible(TarjetaLoc.INPUT_CVV).get_attribute("type")


# ==============================================
# PASO 4 - CONFIRMACIÓN ANTES DE PAGAR
# ==============================================
class ConfirmacionPage(MemphisPage):
    def visible(self, timeout=10):
        return self.existe(ConfirmacionLoc.CONTENEDOR, timeout)

    def resumen(self):
        """{'Nombre completo': 'Juan Hernandez', 'Correo': ..., 'Tarjeta': '•••• 7401', ...}"""
        datos = {}
        for fila in self.driver.find_elements(*ConfirmacionLoc.FILAS):
            partes = fila.text.split("\n", 1)
            datos[partes[0].strip()] = partes[1].strip() if len(partes) > 1 else ""
        return datos

    # ---------- meses sin intereses (opcional) ----------
    def ofrece_msi(self, timeout=3):
        """True si la página muestra 'Tu tarjeta participa en promociones de meses sin intereses...'."""
        return self.existe(ConfirmacionLoc.TEXTO_MSI, timeout)

    def texto_msi(self):
        return self.texto(ConfirmacionLoc.TEXTO_MSI)

    def opciones_msi(self):
        """Textos de los planes ofrecidos, ej. ['6 meses']."""
        textos = []
        for radio in self.driver.find_elements(*ConfirmacionLoc.RADIOS_MSI):
            texto = self.driver.execute_script(
                "const r = arguments[0];"
                "const l = r.closest('label') || (r.id && document.querySelector(`label[for='${r.id}']`));"
                "if (l) return l.innerText;"
                "let n = r.nextSibling; while (n && !(n.textContent || '').trim()) n = n.nextSibling;"
                "return n ? n.textContent : '';", radio)
            textos.append(" ".join((texto or "").split()))
        return textos

    def plan_msi_seleccionado(self):
        """Texto del plan marcado, o '' si se paga en una sola exhibición."""
        for radio, texto in zip(self.driver.find_elements(*ConfirmacionLoc.RADIOS_MSI), self.opciones_msi()):
            if self.propiedad(radio, "checked"):
                return texto
        return ""

    def seleccionar_msi(self, meses=6):
        radio = self.esperar_visible(opcion_msi(meses))
        try:
            radio.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", radio)
        if not self.propiedad(radio, "checked"):
            raise AssertionError(f"No se pudo seleccionar el plan de {meses} meses sin intereses")

    def confirmar_pago(self):
        self.continuar()


# ==============================================
# RESULTADO (incluye la espera del 3DS)
# ==============================================
class ResultadoPage(MemphisPage):
    def en_memphis(self):
        return (urlparse(self.driver.current_url).hostname or "").endswith("memphis.mx")

    def titulo(self):
        elementos = self.driver.find_elements(*ResultadoLoc.TITULO)
        return elementos[0].text.strip() if elementos else ""

    def subtitulo(self):
        elementos = self.driver.find_elements(*ResultadoLoc.SUBTITULO)
        return elementos[0].text.strip() if elementos else ""

    def esperar(self, timeout=settings.TIMEOUT_PROCESAMIENTO):
        """Espera el resultado final. Si el banco redirige a 3DS, espera a que regrese.
        Regresa: 'aprobada' | 'rechazada' | 'invalido'."""
        limite = time.time() + timeout
        avisado_3ds = False
        while time.time() < limite:
            if not self.en_memphis():
                if not avisado_3ds:
                    avisado_3ds = True
                    limite = max(limite, time.time() + settings.TIMEOUT_3DS_SEG)
                    if settings.TRESDS_MODO == "manual":
                        print("\n" + "=" * 60)
                        print("🏦 3D SECURE: la página salió al sitio del banco.")
                        print("   Tarjeta 'Challenge': captura el código/reto en Chrome. El script espera el regreso.")
                        print("   Tarjetas 'Not challenge', 'Attempt' y 'Not authenticated' regresan solas.")
                        print("=" * 60)
            else:
                titulo = self.titulo()
                if titulo.startswith(TITULO_APROBADA):
                    return "aprobada"
                if titulo.startswith(TITULO_RECHAZADA):
                    return "rechazada"
                if ValidacionPage._es_invalido(self.driver):
                    return "invalido"
            time.sleep(1)
        raise TimeoutException(f"No apareció la pantalla de resultado (última URL: {self.driver.current_url})")

    def salio_a_3ds(self, timeout=15):
        """True si la app redirigió al sitio del banco para autenticar."""
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: not self.en_memphis())
            return True
        except TimeoutException:
            return False

    def aprobada(self):
        return self.titulo().startswith(TITULO_APROBADA)

    def rechazada(self):
        return self.titulo().startswith(TITULO_RECHAZADA)

    def detalles(self):
        """{'Estado': ..., 'Código de respuesta': ..., 'Referencia': ..., 'Autorización': ..., 'Identificador': ...}"""
        datos = {}
        for fila in self.driver.find_elements(*ResultadoLoc.FILAS):
            etiqueta = fila.find_element(*ResultadoLoc.ETIQUETA).text.strip().rstrip(":")
            datos[etiqueta] = fila.find_element(*ResultadoLoc.VALOR).text.strip()
        return datos

    def toast_error(self, timeout=5):
        return self.texto(ResultadoLoc.TOAST_ERROR, timeout) if self.existe(ResultadoLoc.TOAST_ERROR, timeout) else ""

    def puede_reintentar(self):
        return self.existe(ResultadoLoc.BTN_REINTENTAR)

    def reintentar(self):
        self.click(ResultadoLoc.BTN_REINTENTAR)

    def contador(self):
        return self.texto(ResultadoLoc.CONTADOR)

    def continuar(self):
        self.click(ResultadoLoc.BTN_CONTINUAR)

    def esperar_redireccion_gobierno(self, timeout):
        try:
            self.esperar_url_contiene(settings.DOMINIO_GOBIERNO, timeout)
            return True
        except TimeoutException:
            return False


# ==============================================
# FLUJO COMPLETO
# ==============================================
class FlujoPago:
    """Atajos para recorrer el botón de pago. Si recibe 'evidencia', toma captura en cada paso."""

    def __init__(self, driver, evidencia=None):
        self.driver = driver
        self.evidencia = evidencia
        self.validacion = ValidacionPage(driver)
        self.contacto = ContactoPage(driver)
        self.direccion = DireccionPage(driver)
        self.tarjeta = TarjetaPage(driver)
        self.confirmacion = ConfirmacionPage(driver)
        self.resultado = ResultadoPage(driver)

    def _captura(self, descripcion):
        if self.evidencia:
            self.evidencia.captura(descripcion)

    def abrir_enlace(self, url):
        self.driver.get(url)
        estado = self.validacion.esperar_fin_validacion()
        self._captura(f"Enlace abierto ({estado})")
        return estado

    def hasta_direccion(self, url, contacto=CONTACTO_VALIDO):
        assert self.abrir_enlace(url) == "formulario", "El enlace no mostró el formulario de pago"
        self.contacto.llenar(**contacto)
        self._captura("Paso 1 - Contacto capturado")
        self.contacto.continuar()
        assert self.direccion.visible(), f"No se avanzó al Paso 2 - Dirección: {self.contacto.errores()}"

    def hasta_tarjeta(self, url, contacto=CONTACTO_VALIDO, direccion=DIRECCION_VALIDA):
        self.hasta_direccion(url, contacto)
        self.direccion.llenar(**direccion)
        self._captura("Paso 2 - Dirección capturada")
        self.direccion.continuar()
        assert self.tarjeta.visible(), f"No se avanzó al Paso 3 - Tarjeta: {self.direccion.errores()}"

    def hasta_confirmacion(self, url, tarjeta, **kwargs):
        self.hasta_tarjeta(url, **kwargs)
        self.tarjeta.llenar_con(tarjeta)
        self._captura("Paso 3 - Tarjeta capturada")
        self.tarjeta.continuar()
        assert self.confirmacion.visible(), f"No se avanzó al Paso 4 - Confirmación: {self.tarjeta.errores()}"
        self._captura("Paso 4 - Revisa tu información antes de pagar")
        plan = tarjeta.get("msi") or settings.PLAN_MSI
        if plan and self.confirmacion.ofrece_msi():
            self.confirmacion.seleccionar_msi(int(plan))
            self._captura(f"Paso 4 - Plan de {plan} meses sin intereses seleccionado")

    def pagar(self, url, tarjeta, **kwargs):
        """Recorre todo el flujo, confirma el pago y regresa 'aprobada' / 'rechazada' / 'invalido'."""
        self.hasta_confirmacion(url, tarjeta, **kwargs)
        self.confirmacion.confirmar_pago()
        resultado = self.resultado.esperar()
        self._captura(f"Resultado: {self.resultado.titulo() or resultado}")
        if resultado == "aprobada":
            datos.marcar_enlace_pagado(url)
        return resultado
