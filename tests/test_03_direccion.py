"""
MÓDULO 03 - PASO 2 DIRECCIÓN
· TC-BP-012 a TC-BP-016
"""
import pytest

from config.datos_prueba import CONTACTO_VALIDO, CP_INCOMPLETO, CP_INEXISTENTE, DIRECCION_VALIDA
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-012")
def test_TC_BP_012_direccion_valida(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(**DIRECCION_VALIDA)
    evidencia.captura("Dirección capturada")
    flujo.direccion.continuar()

    assert flujo.tarjeta.visible(), "No se avanzó al Paso 3 - Tarjeta"


@caso("TC-BP-013")
def test_TC_BP_013_direccion_vacia(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.continuar()
    evidencia.captura("Continuar con dirección vacía")

    assert flujo.direccion.sigue_en_paso(), "El sistema avanzó con la dirección vacía"
    errores = flujo.direccion.errores()
    evidencia.nota(f"Mensajes mostrados: {errores}")
    assert len(errores) >= 4, f"Se esperaban mensajes en cada campo, se mostraron {len(errores)}"


@caso("TC-BP-014")
def test_TC_BP_014_cp_incompleto(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(**{**DIRECCION_VALIDA, "cp": CP_INCOMPLETO})
    flujo.direccion.continuar()
    evidencia.captura(f"CP: {CP_INCOMPLETO}")

    assert flujo.direccion.sigue_en_paso(), "El sistema avanzó con un CP incompleto"
    assert flujo.direccion.error_cp(), "Falta mensaje de código postal inválido"


@caso("TC-BP-015")
def test_TC_BP_015_cp_inexistente(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(**{**DIRECCION_VALIDA, "cp": CP_INEXISTENTE})
    evidencia.captura(f"CP: {CP_INEXISTENTE}")

    mensaje = flujo.direccion.error_cp()
    assert mensaje, "No se avisó que no hay colonias para el CP"
    flujo.direccion.llenar(**DIRECCION_VALIDA)
    evidencia.captura("CP corregido")
    assert not flujo.direccion.error_cp(), "No se permitió corregir el código postal"


@caso("TC-BP-016")
def test_TC_BP_016_regresar_conserva_contacto(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.regresar()
    evidencia.captura("De regreso en Paso 1 - Contacto")

    assert flujo.contacto.valores() == CONTACTO_VALIDO, \
        f"Se perdieron los datos de contacto: {flujo.contacto.valores()}"
