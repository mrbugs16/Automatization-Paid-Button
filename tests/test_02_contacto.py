"""
MÓDULO 02 - PASO 1 DATOS DE CONTACTO
· TC-BP-006 a TC-BP-011
"""
import pytest

from config.datos_prueba import (CONTACTO_VALIDO, CORREO_SIN_ARROBA, TELEFONO_CON_LETRAS,
                                 TELEFONO_INCOMPLETO)
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-006")
def test_TC_BP_006_contacto_valido(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(**CONTACTO_VALIDO)
    evidencia.captura("Contacto capturado")
    flujo.contacto.continuar()

    assert flujo.direccion.visible(), "No se avanzó al Paso 2 - Dirección"


@caso("TC-BP-007")
def test_TC_BP_007_contacto_vacio(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar("", "")
    flujo.contacto.continuar()
    evidencia.captura("Continuar con formulario vacío")

    assert flujo.contacto.sigue_en_paso(), "El sistema avanzó con el formulario vacío"
    assert flujo.contacto.error_telefono(), "Falta mensaje de campo obligatorio en teléfono"
    assert flujo.contacto.error_correo(), "Falta mensaje de campo obligatorio en correo"


@caso("TC-BP-008")
def test_TC_BP_008_solo_telefono(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=CONTACTO_VALIDO["telefono"], correo="")
    flujo.contacto.continuar()
    evidencia.captura("Solo teléfono capturado")

    assert flujo.contacto.sigue_en_paso(), "El sistema avanzó sin correo"
    assert flujo.contacto.error_correo(), "Falta mensaje de correo obligatorio"


@caso("TC-BP-009")
def test_TC_BP_009_correo_formato_incorrecto(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=CONTACTO_VALIDO["telefono"], correo=CORREO_SIN_ARROBA)
    flujo.contacto.continuar()
    evidencia.captura(f"Correo: {CORREO_SIN_ARROBA}")

    assert flujo.contacto.sigue_en_paso(), "El sistema avanzó con un correo inválido"
    assert flujo.contacto.error_correo(), "Falta mensaje de correo inválido"


@caso("TC-BP-010")
def test_TC_BP_010_telefono_incompleto(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=TELEFONO_INCOMPLETO, correo=CONTACTO_VALIDO["correo"])
    flujo.contacto.continuar()
    evidencia.captura(f"Teléfono: {TELEFONO_INCOMPLETO}")

    assert flujo.contacto.sigue_en_paso(), "El sistema avanzó con un teléfono incompleto"
    assert flujo.contacto.error_telefono(), "Falta mensaje de teléfono inválido"


@caso("TC-BP-011")
def test_TC_BP_011_telefono_con_letras(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=TELEFONO_CON_LETRAS, correo=CONTACTO_VALIDO["correo"])
    valor = flujo.contacto.valores()["telefono"]
    evidencia.captura(f"Teléfono escrito: '{TELEFONO_CON_LETRAS}' -> quedó '{valor}'")
    flujo.contacto.continuar()

    rechaza_letras = valor.isdigit() or valor == ""
    assert rechaza_letras or flujo.contacto.error_telefono(), \
        f"El campo aceptó letras ('{valor}') sin mostrar error"
