"""
MÓDULO 08 - CASOS ESPECIALES DE NAVEGACIÓN (usuario con poco conocimiento técnico)
· TC-BP-036 a TC-BP-046
"""
import time

import pytest

from config import settings
from config.datos_prueba import CONTACTO_VALIDO, CORREO_CON_ESPACIOS
from config.locators import TarjetaLoc
from core.driver_factory import simular_sin_conexion
from core.marcadores import caso, pendiente, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


def _estado_consistente(flujo):
    """La página está en un paso válido o en un resultado, sin errores técnicos visibles."""
    fuente = flujo.driver.page_source.lower()
    errores_tecnicos = ["exception", "stack trace", "internal server error", "cannot read properties"]
    assert not any(e in fuente for e in errores_tecnicos), "Se muestra un error técnico en pantalla"
    return (flujo.validacion.muestra_formulario() or flujo.direccion.visible(2) or flujo.tarjeta.visible(2)
            or flujo.resultado.aprobada() or flujo.resultado.rechazada() or flujo.validacion.muestra_ya_pagado())


def _hasta_procesando(flujo, url, tarjeta):
    flujo.hasta_tarjeta(url)
    flujo.tarjeta.llenar_con(tarjeta)
    flujo.tarjeta.pagar()
    assert flujo.procesamiento.procesando_visible(), "No se mostró 'Procesando transacción'"


@caso("TC-BP-036")
def test_TC_BP_036_f5_durante_llenado(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(cp="72000", calle="Reforma")
    evidencia.captura("Paso 2 parcialmente lleno")

    flujo.driver.refresh()
    time.sleep(2)
    evidencia.captura("Después de F5")
    assert _estado_consistente(flujo), "La página no quedó en un estado correcto tras recargar"


@caso("TC-BP-037")
def test_TC_BP_037_f5_en_procesando(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    _hasta_procesando(flujo, enlace_valido, tarjeta_de_prueba("aprobada_sin_3ds"))
    flujo.driver.refresh()
    time.sleep(3)
    evidencia.captura("Después de F5 en Procesando")

    assert flujo.resultado.aprobada() or flujo.resultado.rechazada() or flujo.validacion.muestra_ya_pagado(), \
        "Al recargar no se muestra el resultado real del pago"
    evidencia.nota("⚠ Validar en backend que exista un solo cobro")


@caso("TC-BP-038")
def test_TC_BP_038_atras_durante_llenado(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(cp="72000")
    flujo.driver.back()
    time.sleep(2)
    evidencia.captura("Después de Atrás del navegador")
    assert _estado_consistente(flujo), "El formulario quedó en estado inconsistente"


@caso("TC-BP-039")
def test_TC_BP_039_atras_adelante_tras_aprobada(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    assert flujo.pagar(enlace_valido, tarjeta_de_prueba("aprobada_sin_3ds")) == "aprobada"
    flujo.driver.back()
    time.sleep(2)
    evidencia.captura("Atrás tras aprobada")
    assert not flujo.tarjeta.visible(3), "Se permitió volver a capturar la tarjeta"

    flujo.driver.forward()
    time.sleep(2)
    evidencia.captura("Adelante")
    assert not flujo.tarjeta.visible(3), "Se permitió volver a capturar la tarjeta"


@caso("TC-BP-040")
def test_TC_BP_040_cerrar_pestana_en_procesando(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    driver = flujo.driver
    principal = driver.current_window_handle
    driver.switch_to.new_window("tab")
    _hasta_procesando(flujo, enlace_valido, tarjeta_de_prueba("aprobada_sin_3ds"))
    evidencia.captura("Procesando - se cerrará la pestaña")
    driver.close()

    driver.switch_to.window(principal)
    time.sleep(settings.TIMEOUT_PROCESAMIENTO // 3)
    flujo.abrir_enlace(enlace_valido)
    evidencia.captura("Enlace reabierto")
    assert not flujo.validacion.muestra_formulario(), "El enlace permite volver a pagar"


@caso("TC-BP-041")
def test_TC_BP_041_sin_internet_en_formulario(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(**CONTACTO_VALIDO)
    try:
        simular_sin_conexion(flujo.driver, True)
    except NotImplementedError as e:
        pendiente(str(e))
    flujo.contacto.continuar()
    evidencia.captura("Sin conexión")

    simular_sin_conexion(flujo.driver, False)
    time.sleep(2)
    evidencia.captura("Conexión restablecida")
    assert flujo.contacto.valores() == CONTACTO_VALIDO or flujo.direccion.visible(), \
        "Se perdieron los datos capturados al perder conexión"


@caso("TC-BP-042")
def test_TC_BP_042_sin_internet_tras_pagar(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta_de_prueba("aprobada_sin_3ds"))
    flujo.tarjeta.pagar()
    try:
        simular_sin_conexion(flujo.driver, True)
    except NotImplementedError as e:
        pendiente(str(e))
    time.sleep(5)
    simular_sin_conexion(flujo.driver, False)

    resultado = flujo.resultado.esperar()
    evidencia.captura(f"Al reconectar: {resultado}")
    evidencia.nota("⚠ Validar en backend que exista un solo cobro")


@caso("TC-BP-043")
def test_TC_BP_043_doble_clic_pagar(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta_de_prueba("aprobada_sin_3ds"))
    boton = flujo.tarjeta.esperar_clickeable(TarjetaLoc.BTN_PAGAR)
    for _ in range(5):
        try:
            boton.click()
        except Exception:
            break  # el botón se deshabilitó o desapareció: comportamiento esperado
    resultado = flujo.resultado.esperar()
    evidencia.captura(f"Resultado tras clics repetidos: {resultado}")
    evidencia.nota("⚠ Validar en backend que exista un solo cobro")


@caso("TC-BP-044")
def test_TC_BP_044_inactividad_con_datos(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(**CONTACTO_VALIDO)
    evidencia.captura("Formulario parcialmente lleno")

    time.sleep(settings.TOKEN_TTL_SEG + 5)
    flujo.contacto.continuar()
    flujo.validacion.esperar_fin_validacion(timeout=60)
    evidencia.captura("Después de la inactividad")
    assert flujo.validacion.muestra_formulario(), "No se reinició el flujo con un token nuevo"
    assert not flujo.validacion.muestra_error(), "Se quedó en un error sin salida"


@caso("TC-BP-045")
def test_TC_BP_045_enlace_en_proceso_en_otra_pestana(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    driver = flujo.driver
    _hasta_procesando(flujo, enlace_valido, tarjeta_de_prueba("aprobada_con_3ds"))  # 3DS lo deja "en proceso"
    driver.switch_to.new_window("tab")
    flujo.abrir_enlace(enlace_valido)
    evidencia.captura("Mismo enlace en otra pestaña")
    assert not flujo.validacion.muestra_formulario(), "Se permitió iniciar un segundo cobro en paralelo"


@caso("TC-BP-046")
def test_TC_BP_046_correo_con_espacios(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=CONTACTO_VALIDO["telefono"], correo=CORREO_CON_ESPACIOS)
    flujo.contacto.continuar()
    evidencia.captura("Correo con espacios")
    assert flujo.direccion.visible() or flujo.contacto.error_correo(), \
        "No se limpiaron los espacios ni se mostró un error claro"
