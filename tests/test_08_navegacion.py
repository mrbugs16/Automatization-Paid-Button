"""
MÓDULO 08 - CASOS ESPECIALES DE NAVEGACIÓN (usuario con poco conocimiento técnico)
· TC-BP-036 a TC-BP-046
"""
import time

import pytest

from config import settings
from config.datos_prueba import CONTACTO_VALIDO, CORREO_CON_ESPACIOS, DIRECCION_VALIDA
from config.locators import FormularioLoc
from core.driver_factory import simular_sin_conexion
from core.marcadores import caso, exigir_aprobado, pendiente, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]
ERRORES_TECNICOS = ("exception", "stack trace", "internal server error", "cannot read properties", "typeerror")


def _estado_consistente(flujo):
    """Tras recargar/navegar la página debe quedar en un estado válido, sin errores técnicos."""
    texto = flujo.driver.find_element("css selector", "body").text.lower()
    assert not any(e in texto for e in ERRORES_TECNICOS), "Se muestra un error técnico en pantalla"
    if flujo.direccion.visible(2) or flujo.tarjeta.visible(1) or flujo.confirmacion.visible(1):
        return True
    return flujo.validacion.esperar_fin_validacion() in ("formulario", "resultado", "invalido")


def _sin_red(flujo, activo):
    try:
        simular_sin_conexion(flujo.driver, activo)
    except Exception as e:  # el driver Chromium de escritorio no siempre lo soporta
        pendiente(f"No se pudo simular la pérdida de conexión con este driver: {e.__class__.__name__}")


@caso("TC-BP-036")
def test_TC_BP_036_f5_durante_llenado(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(calle="Reforma 245", cp="16200", ciudad="", pais="", estado="")
    evidencia.captura("Paso 2 parcialmente lleno")

    flujo.driver.refresh()
    evidencia.captura("Después de F5")
    assert _estado_consistente(flujo), "La página no quedó en un estado correcto tras recargar"


@caso("TC-BP-037")
@pytest.mark.pago
def test_TC_BP_037_f5_en_procesando(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("principal"))
    flujo.confirmacion.confirmar_pago()
    flujo.driver.refresh()
    evidencia.captura("Inmediatamente después de F5")

    estado = flujo.validacion.esperar_fin_validacion(timeout=settings.TIMEOUT_PROCESAMIENTO)
    evidencia.captura(f"Estado tras recargar: {estado}")
    assert _estado_consistente(flujo), "La página quedó en un estado inconsistente"
    evidencia.nota("⚠ Validar en backend que exista un solo cobro")


@caso("TC-BP-038")
def test_TC_BP_038_atras_durante_llenado(flujo, evidencia, enlace_valido):
    flujo.driver.get(settings.URL_GOBIERNO)  # el contribuyente llega desde el portal del Gobierno
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(calle="Reforma 245", cp="", ciudad="", pais="", estado="")
    flujo.driver.back()
    time.sleep(2)
    evidencia.captura("Después de 'Atrás' del navegador")

    if not flujo.resultado.en_memphis():
        evidencia.nota(f"'Atrás' salió del botón de pago hacia {flujo.driver.current_url}; lo capturado se pierde")
        return
    assert _estado_consistente(flujo), "El formulario quedó en estado inconsistente"


@caso("TC-BP-039")
@pytest.mark.pago
def test_TC_BP_039_atras_adelante_tras_aprobada(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    exigir_aprobado(flujo.pagar(enlace_valido, tarjeta_de_prueba("principal")), flujo.resultado.detalles())
    for accion in ("back", "forward"):
        getattr(flujo.driver, accion)()
        time.sleep(2)
        evidencia.captura(f"Navegador: {accion}")
        assert not flujo.confirmacion.visible(3) and not flujo.tarjeta.visible(1), \
            "Se permitió volver a capturar/confirmar el pago ya cobrado"


@caso("TC-BP-040")
@pytest.mark.pago
def test_TC_BP_040_cerrar_pestana_en_procesando(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    driver = flujo.driver
    principal = driver.current_window_handle
    driver.switch_to.new_window("tab")
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("principal"))
    flujo.confirmacion.confirmar_pago()
    evidencia.captura("Procesando - se cerrará la pestaña")
    driver.close()

    driver.switch_to.window(principal)
    time.sleep(settings.TIMEOUT_PROCESAMIENTO // 3)
    estado = flujo.abrir_enlace(enlace_valido)
    evidencia.nota(f"Estado al reabrir el enlace: {estado}")
    assert _estado_consistente(flujo), "El enlace quedó en un estado inconsistente"
    evidencia.nota("⚠ Si el pago se aprobó, el enlace ya no debe permitir pagar; validar en backend")


@caso("TC-BP-041")
def test_TC_BP_041_sin_internet_en_formulario(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(**CONTACTO_VALIDO)
    _sin_red(flujo, True)
    flujo.contacto.continuar()
    evidencia.captura("Sin conexión")

    _sin_red(flujo, False)
    time.sleep(2)
    evidencia.captura("Conexión restablecida")
    if flujo.direccion.visible(3):
        evidencia.nota("El avance del Paso 1 al 2 no requiere internet: la página avanzó sin avisar la falta de conexión")
        return
    assert flujo.contacto.valores() == CONTACTO_VALIDO, "Se perdieron los datos capturados al perder conexión"


@caso("TC-BP-042")
@pytest.mark.pago
def test_TC_BP_042_sin_internet_tras_pagar(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("principal"))
    flujo.confirmacion.confirmar_pago()
    _sin_red(flujo, True)
    time.sleep(5)
    _sin_red(flujo, False)

    resultado = flujo.resultado.esperar()
    evidencia.captura(f"Al reconectar: {resultado}")
    evidencia.nota("⚠ Validar en backend que exista un solo cobro")


@caso("TC-BP-043")
@pytest.mark.pago
def test_TC_BP_043_doble_clic_pagar(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("principal"))
    boton = flujo.confirmacion.esperar_clickeable(FormularioLoc.BTN_CONTINUAR)
    clics = 0
    for _ in range(5):
        try:
            boton.click()
            clics += 1
        except Exception:
            break  # el botón se deshabilitó o desapareció: comportamiento esperado
    evidencia.nota(f"Clics aceptados por el botón: {clics}")
    resultado = flujo.resultado.esperar()
    evidencia.captura(f"Resultado tras clics repetidos: {resultado}")
    evidencia.nota("⚠ Validar en backend que exista un solo cobro")


@caso("TC-BP-044")
def test_TC_BP_044_inactividad_con_datos(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(**DIRECCION_VALIDA)
    evidencia.captura("Paso 2 lleno, inicia inactividad")
    limite = settings.TIMEOUT_TOKEN_SEG

    print(f"   ⏳ Vigilando {limite}s de inactividad (el token no debe expirar)…")
    reaccion = flujo.validacion.esperar_reaccion_por_token(limite)
    evidencia.captura(f"Tras {limite}s de inactividad: {reaccion or 'sin cambios'}")
    assert not reaccion, f"El token expiró o el flujo se reinició por inactividad ({reaccion})"

    flujo.direccion.continuar()
    evidencia.captura("Después de continuar")
    assert flujo.tarjeta.visible(), f"No se pudo continuar sin perder lo capturado: {flujo.direccion.errores()}"


@caso("TC-BP-045")
@pytest.mark.pago
def test_TC_BP_045_enlace_en_proceso_en_otra_pestana(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    driver = flujo.driver
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("principal"))
    flujo.confirmacion.confirmar_pago()  # queda en proceso / 3DS
    time.sleep(1)
    if flujo.resultado.aprobada() or flujo.resultado.rechazada():
        pendiente("Bloqueado: el primer pago terminó al instante (sin 3DS); se necesita una tarjeta que "
                  "deje el pago en proceso para abrir el link en paralelo")
    driver.switch_to.new_window("tab")
    estado = flujo.abrir_enlace(enlace_valido)
    evidencia.captura(f"Mismo enlace en otra pestaña: {estado}")
    assert estado != "formulario", "Se permitió iniciar un segundo cobro mientras el primero está en proceso"


@caso("TC-BP-046")
def test_TC_BP_046_correo_con_espacios(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=CONTACTO_VALIDO["telefono"], correo=CORREO_CON_ESPACIOS)
    flujo.contacto.continuar()
    evidencia.captura("Correo con espacios")
    assert flujo.direccion.visible() or flujo.contacto.error_correo(), \
        "No se limpiaron los espacios ni se mostró un error claro"
