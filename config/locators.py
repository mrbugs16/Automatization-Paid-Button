"""
Localizadores (By, valor) de todas las pantallas.
Solo CSS o XPath: el driver Chromium de Appium no acepta By.ID ni By.NAME.

- GobiernoLoc: tomados del portal real (srvtestwl.pueblacapital.gob.mx/pabel/iniciopredial).
- Memphis*: PROVISIONALES. El botón de pago aún no está publicado; en cuanto exista
  hay que reemplazarlos por los reales (idealmente pedir a desarrollo atributos data-testid).
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
# MEMPHIS - VALIDACIÓN DEL ENLACE
# ==============================================
class ValidacionLoc:
    PANTALLA_VALIDANDO = (By.CSS_SELECTOR, "[data-testid='validando-enlace']")        # TODO
    MENSAJE_ERROR = (By.CSS_SELECTOR, "[data-testid='error-enlace']")                 # TODO
    MENSAJE_YA_PAGADO = (By.CSS_SELECTOR, "[data-testid='transaccion-procesada']")    # TODO
    RESUMEN_IMPORTE = (By.CSS_SELECTOR, "[data-testid='resumen-importe']")            # TODO
    RESUMEN_CONCEPTO = (By.CSS_SELECTOR, "[data-testid='resumen-concepto']")          # TODO
    RESUMEN_REFERENCIA = (By.CSS_SELECTOR, "[data-testid='resumen-referencia']")      # TODO


# ==============================================
# MEMPHIS - PASO 1 CONTACTO
# ==============================================
class ContactoLoc:
    PASO = (By.CSS_SELECTOR, "[data-testid='paso-contacto']")                         # TODO
    INPUT_TELEFONO = (By.CSS_SELECTOR, "input[name='telefono']")                      # TODO
    INPUT_CORREO = (By.CSS_SELECTOR, "input[name='correo']")                          # TODO
    BTN_CONTINUAR = (By.XPATH, "//button[normalize-space()='Continuar']")             # TODO
    ERROR_TELEFONO = (By.CSS_SELECTOR, "[data-testid='error-telefono']")              # TODO
    ERROR_CORREO = (By.CSS_SELECTOR, "[data-testid='error-correo']")                  # TODO
    TAB_CONTACTO = (By.CSS_SELECTOR, "[data-testid='stepper-contacto']")              # TODO


# ==============================================
# MEMPHIS - PASO 2 DIRECCIÓN
# ==============================================
class DireccionLoc:
    PASO = (By.CSS_SELECTOR, "[data-testid='paso-direccion']")                        # TODO
    INPUT_CP = (By.CSS_SELECTOR, "input[name='codigoPostal']")                        # TODO
    INPUT_CALLE = (By.CSS_SELECTOR, "input[name='calle']")                            # TODO
    INPUT_NUMERO = (By.CSS_SELECTOR, "input[name='numero']")                          # TODO
    INPUT_ESTADO = (By.CSS_SELECTOR, "[name='estado']")                               # TODO
    BTN_CONTINUAR = (By.XPATH, "//button[normalize-space()='Continuar']")             # TODO
    BTN_REGRESAR = (By.XPATH, "//button[normalize-space()='Regresar']")               # TODO
    ERRORES = (By.CSS_SELECTOR, "[data-testid^='error-']")                            # TODO
    ERROR_CP = (By.CSS_SELECTOR, "[data-testid='error-cp']")                          # TODO


# ==============================================
# MEMPHIS - PASO 3 TARJETA
# ==============================================
class TarjetaLoc:
    PASO = (By.CSS_SELECTOR, "[data-testid='paso-tarjeta']")                          # TODO
    IFRAME = None  # TODO: si los campos de tarjeta viven en un iframe del procesador, poner su locator
    INPUT_NUMERO = (By.CSS_SELECTOR, "input[name='numeroTarjeta']")                   # TODO
    INPUT_NOMBRE = (By.CSS_SELECTOR, "input[name='nombreTitular']")                   # TODO
    INPUT_VIGENCIA = (By.CSS_SELECTOR, "input[name='vigencia']")                      # TODO
    INPUT_CVV = (By.CSS_SELECTOR, "input[name='cvv']")                                # TODO
    BTN_PAGAR = (By.XPATH, "//button[normalize-space()='Pagar']")                     # TODO
    ERRORES = (By.CSS_SELECTOR, "[data-testid^='error-']")                            # TODO
    ERROR_NUMERO = (By.CSS_SELECTOR, "[data-testid='error-numero']")                  # TODO
    ERROR_VIGENCIA = (By.CSS_SELECTOR, "[data-testid='error-vigencia']")              # TODO
    ERROR_CVV = (By.CSS_SELECTOR, "[data-testid='error-cvv']")                        # TODO


# ==============================================
# MEMPHIS - PROCESAMIENTO / 3D SECURE
# ==============================================
class ProcesamientoLoc:
    PANTALLA_PROCESANDO = (By.XPATH, "//*[contains(., 'Procesando transacci')]")      # TODO
    IFRAME_3DS = (By.CSS_SELECTOR, "iframe[name*='3ds'], iframe[id*='3ds']")          # TODO
    INPUT_CODIGO_3DS = (By.CSS_SELECTOR, "input[type='password'], input[name*='otp']")  # TODO
    BTN_ENVIAR_3DS = (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")  # TODO
    BTN_CANCELAR_3DS = (By.XPATH, "//*[self::a or self::button][contains(., 'Cancel')]")  # TODO
    POPUP_ERROR = (By.CSS_SELECTOR, "[role='dialog'], .modal.show")                   # TODO


# ==============================================
# MEMPHIS - RESULTADO
# ==============================================
class ResultadoLoc:
    APROBADA = (By.XPATH, "//*[contains(., 'Transacci') and contains(., 'aprobada')]")    # TODO
    RECHAZADA = (By.XPATH, "//*[contains(., 'Transacci') and contains(., 'rechazada')]")  # TODO
    REFERENCIA = (By.CSS_SELECTOR, "[data-testid='resultado-referencia']")            # TODO
    FOLIO = (By.CSS_SELECTOR, "[data-testid='resultado-folio']")                      # TODO
    MENSAJE = (By.CSS_SELECTOR, "[data-testid='resultado-mensaje']")                  # TODO
    CONTADOR = (By.CSS_SELECTOR, "[data-testid='contador-redireccion']")              # TODO
    BTN_CONTINUAR = (By.XPATH, "//button[normalize-space()='Continuar']")             # TODO
    BTN_REINTENTAR = (By.XPATH, "//button[normalize-space()='Reintentar']")           # TODO
