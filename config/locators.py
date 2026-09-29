"""
Localizadores (By, valor) de todas las pantallas.
Solo CSS o XPath: el driver Chromium de Appium no acepta By.ID ni By.NAME.

- GobiernoLoc: tomados del portal real (srvtestwl.pueblacapital.gob.mx/pabel/iniciopredial).
- Memphis*: tomados del botón de pago real (pagospueblacapital-dev.memphis.mx/payout).
  La app es React: los ids de los campos y las clases salen del código de la página.
"""
from selenium.webdriver.common.by import By


# ==============================================
# PORTAL GOBIERNO DE PUEBLA (FUERA DE ALCANCE QA, SOLO PRECONDICIÓN)
# ==============================================
class GobiernoLoc:
    CARD_PREDIAL = (By.CSS_SELECTOR, "a.card-estilo-predial")
    FORMULARIO = (By.CSS_SELECTOR, "#forma")
    SELECT_TIPO = (By.CSS_SELECTOR, "#tipo")                 # PU = Urbano, PR = Rústico
    INPUT_CUENTA = (By.CSS_SELECTOR, "#cuenta")              # máx. 7 dígitos
    INPUT_DELEGACION = (By.CSS_SELECTOR, "#delegacion")      # máx. 2 dígitos
    INPUT_LINEA_CAPTURA = (By.CSS_SELECTOR, "#lc")           # máx. 24 dígitos
    IMG_CAPTCHA = (By.CSS_SELECTOR, "#captcha")
    BTN_REFRESCAR_CAPTCHA = (By.CSS_SELECTOR, "a[onclick*='changeRefresh']")
    INPUT_CAPTCHA = (By.CSS_SELECTOR, "[name='answer']")           # máx. 5 caracteres
    BTN_CONSULTAR = (By.CSS_SELECTOR, "form#forma button[type='submit']")
    MENSAJE_ERROR = (By.CSS_SELECTOR, ".alert, .error, .text-danger, .invalid-feedback")

    # TODO: pantalla posterior a "Consultar" (detalle del adeudo y botón que manda a Memphis)
    BTN_PAGAR_EN_LINEA = (By.XPATH, "//*[self::a or self::button][contains(translate(., 'PAGAR', 'pagar'), 'pagar')]")


# ==============================================
# MEMPHIS - ENCABEZADO Y STEPPER (visibles en los 4 pasos)
# ==============================================
class EncabezadoLoc:
    IMPORTE = (By.CSS_SELECTOR, ".stepper__detail__header .text-value")      # "$2280.45"
    CONCEPTO = (By.CSS_SELECTOR, ".stepper__detail__header .text-concept")   # "Concepto de pago: ..."
    FECHA = (By.CSS_SELECTOR, ".stepper__detail__header .text-date")
    FILAS = (By.CSS_SELECTOR, ".stepper__detail__row")                       # Solicitante / Descripción / Referencia
    PASO_ACTIVO = (By.CSS_SELECTOR, "button.number-content--active")          # texto = número de paso


def boton_paso(numero):
    """Botón circular del stepper (1 Contacto, 2 Dirección, 3 Tarjeta, 4 Pago)."""
    return (By.XPATH, f"//button[contains(@class,'number-content') and normalize-space()='{numero}']")


# ==============================================
# MEMPHIS - VALIDACIÓN DEL ENLACE / ESTADOS DE PANTALLA
# ==============================================
class ValidacionLoc:
    SPINNER = (By.CSS_SELECTOR, ".status__spinner-container")                 # "Validando link de pago"
    ENCABEZADO_ESTADO = (By.CSS_SELECTOR, ".status__header .status-heading")  # "Link de pago no válido"
    MENSAJE_ESTADO = (By.CSS_SELECTOR, ".status__header .status-message")


# ==============================================
# MEMPHIS - CAMPOS Y BOTONES COMUNES
# ==============================================
class FormularioLoc:
    BTN_CONTINUAR = (By.XPATH, "//button[normalize-space()='Continuar']")
    BTN_REGRESAR = (By.XPATH, "//button[normalize-space()='Regresar']")
    ERRORES = (By.CSS_SELECTOR, ".input__error, .select__error")


def error_de(id_campo):
    """Mensaje de error que la app pinta dentro del recuadro del campo (input o select)."""
    return (By.XPATH,
            f"//div[contains(@class,'input--error') or contains(@class,'select--error')]"
            f"[.//*[@id='{id_campo}']]//span[contains(@class,'__error')]")


# ==============================================
# MEMPHIS - PASO 1 CONTACTO
# ==============================================
class ContactoLoc:
    INPUT_TELEFONO = (By.CSS_SELECTOR, "#mobile")   # opcional, 10 a 13 dígitos
    INPUT_CORREO = (By.CSS_SELECTOR, "#email")      # obligatorio


# ==============================================
# MEMPHIS - PASO 2 DIRECCIÓN
# ==============================================
class DireccionLoc:
    INPUT_CALLE = (By.CSS_SELECTOR, "#street")      # solo letras, números y espacios
    INPUT_CP = (By.CSS_SELECTOR, "#zip-code")       # exactamente 5 dígitos
    INPUT_CIUDAD = (By.CSS_SELECTOR, "#city")       # solo letras, números y espacios
    SELECT_PAIS = (By.CSS_SELECTOR, "#country")     # value = código alfa-3 (MEX)
    SELECT_ESTADO = (By.CSS_SELECTOR, "#state")     # value = código alfa-3 (PUE)


# ==============================================
# MEMPHIS - PASO 3 DATOS DE TARJETA
# ==============================================
class TarjetaLoc:
    INPUT_NOMBRE = (By.CSS_SELECTOR, "#name")
    INPUT_APELLIDO = (By.CSS_SELECTOR, "#lastName")
    INPUT_NUMERO = (By.CSS_SELECTOR, "#card")           # máscara 0000 0000 0000 0000
    INPUT_VIGENCIA = (By.CSS_SELECTOR, "#expiration")   # máscara 00/00
    INPUT_CVV = (By.CSS_SELECTOR, "#cvv")               # type=password, máx. 3


# ==============================================
# MEMPHIS - PASO 4 CONFIRMACIÓN ("Revisa tu información antes de pagar")
# ==============================================
class ConfirmacionLoc:
    CONTENEDOR = (By.CSS_SELECTOR, ".payment-summary-container")
    FILAS = (By.CSS_SELECTOR, ".payment-summary__row")    # <span>etiqueta</span><strong>valor</strong>


# ==============================================
# MEMPHIS - RESULTADO (procesando / aprobada / rechazada)
# ==============================================
class ResultadoLoc:
    TITULO = (By.CSS_SELECTOR, ".status__detail-heading .status-heading")    # "Transacción aprobada/rechazada"
    SUBTITULO = (By.CSS_SELECTOR, ".status__detail-heading .status-message")
    FILAS = (By.CSS_SELECTOR, ".status__detail-row")                         # Estado, Código de respuesta, ...
    ETIQUETA = (By.CSS_SELECTOR, ".status-detail-label")
    VALOR = (By.CSS_SELECTOR, ".status-detail-value")
    IMAGEN = (By.CSS_SELECTOR, "img.status-image")                           # alt = success | error | validating
    CONTADOR = (By.CSS_SELECTOR, ".counter__text-dinamyc")                   # "10 segundos"
    BTN_CONTINUAR = (By.XPATH, "//button[starts-with(normalize-space(),'Continuar en')]")
    BTN_REINTENTAR = (By.XPATH, "//button[normalize-space()='Reintentar']")
    TOAST_ERROR = (By.CSS_SELECTOR, ".custom-toast__container--error")
    TOAST = (By.CSS_SELECTOR, "[class*='custom-toast__container']")
