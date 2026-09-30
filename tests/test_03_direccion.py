"""
MÓDULO 03 - PASO 2 DIRECCIÓN
· TC-BP-012 a TC-BP-016, TC-BP-056 y TC-BP-058

Reglas de la página: calle, CP, ciudad, país y estado obligatorios; CP de 5 dígitos;
calle y ciudad solo letras sin acento, números y espacios.
"""
import pytest
from selenium.webdriver.support.ui import Select

from config.datos_prueba import (CONTACTO_VALIDO, CP_CORTO, CP_INCOMPLETO, DIRECCION_VALIDA, MSG_CP,
                                 MSG_NATIVO_SELECCIONA)
from config.locators import DireccionLoc
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


def _no_avanza(flujo):
    return flujo.direccion.visible(2) and not flujo.tarjeta.visible(2)


@caso("TC-BP-012")
def test_TC_BP_012_direccion_valida(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(**DIRECCION_VALIDA)
    evidencia.captura("Dirección capturada (México / Puebla)")
    flujo.direccion.continuar()

    assert flujo.tarjeta.visible(), f"No se avanzó al Paso 3: {flujo.direccion.errores()}"


@caso("TC-BP-013")
def test_TC_BP_013_direccion_vacia(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.continuar()
    evidencia.captura("Continuar con dirección vacía")

    assert _no_avanza(flujo), "El sistema avanzó con la dirección vacía"
    aviso = flujo.direccion.mensaje_nativo_estado()
    evidencia.nota(f"Aviso del navegador en Estado: '{aviso}'")
    assert aviso == MSG_NATIVO_SELECCIONA, f"No se mostró el aviso '{MSG_NATIVO_SELECCIONA}' (se obtuvo: '{aviso}')"


@caso("TC-BP-014")
def test_TC_BP_014_cp_incompleto(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(**{**DIRECCION_VALIDA, "cp": CP_INCOMPLETO})
    flujo.direccion.continuar()
    evidencia.captura(f"CP: {CP_INCOMPLETO}")

    assert _no_avanza(flujo), "El sistema avanzó con un CP incompleto"
    assert flujo.direccion.error_cp() == MSG_CP, f"Mensaje: '{flujo.direccion.error_cp()}'"


@caso("TC-BP-015")
def test_TC_BP_015_cp_menos_digitos(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(**{**DIRECCION_VALIDA, "cp": CP_CORTO})
    flujo.direccion.continuar()
    evidencia.captura(f"CP: {CP_CORTO}")

    assert _no_avanza(flujo), f"Se aceptó el CP '{CP_CORTO}' con menos de 5 dígitos"
    assert flujo.direccion.error_cp() == MSG_CP, f"Mensaje: '{flujo.direccion.error_cp()}'"


@caso("TC-BP-016")
def test_TC_BP_016_regresar_conserva_contacto(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.regresar()
    evidencia.captura("De regreso en Paso 1 - Contacto")
    mostrado = flujo.contacto.telefono_mostrado()
    if mostrado != CONTACTO_VALIDO["telefono"]:
        evidencia.nota(f"Observación: el teléfono regresa con formato '{mostrado}'")

    assert flujo.contacto.valores() == CONTACTO_VALIDO, f"Se perdieron los datos: {flujo.contacto.valores()}"


@caso("TC-BP-056")
def test_TC_BP_056_estado_sin_seleccionar(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(**{**DIRECCION_VALIDA, "estado": ""})
    flujo.direccion.continuar()
    evidencia.captura("Estado sin seleccionar")

    assert _no_avanza(flujo), "El sistema avanzó sin Estado"
    aviso = flujo.direccion.mensaje_nativo_estado()
    evidencia.nota(f"Aviso del navegador en Estado: '{aviso}'")
    assert aviso == MSG_NATIVO_SELECCIONA, f"No se mostró el aviso '{MSG_NATIVO_SELECCIONA}' (se obtuvo: '{aviso}')"


@caso("TC-BP-058")
def test_TC_BP_058_cambiar_pais_reinicia_estado(flujo, evidencia, enlace_valido):
    flujo.hasta_direccion(enlace_valido)
    flujo.direccion.llenar(**DIRECCION_VALIDA)
    select_pais = Select(flujo.direccion.esperar_visible(DireccionLoc.SELECT_PAIS))
    otro = next((o.get_attribute("value") for o in select_pais.options
                 if o.get_attribute("value") not in ("", DIRECCION_VALIDA["pais"])), None)
    assert otro, "El catálogo de países solo tiene México"

    flujo.direccion.seleccionar(DireccionLoc.SELECT_PAIS, otro)
    evidencia.captura(f"País cambiado a {otro}")
    assert flujo.direccion.opcion_seleccionada(DireccionLoc.SELECT_ESTADO) == "", \
        "El Estado de México se conservó al cambiar de país"
