"""
MÓDULO 02 - PASO 1 DATOS DE CONTACTO
· TC-BP-006 a TC-BP-011, TC-BP-052 a TC-BP-054

Reglas de la página: correo obligatorio; teléfono opcional (si se captura, de 10 a 13 dígitos).
"""
import pytest

from config.datos_prueba import (CONTACTO_VALIDO, CORREO_SIN_ARROBA, CORREOS_INVALIDOS, MSG_CORREO_INVALIDO,
                                 MSG_REQUERIDO, MSG_TELEFONO, TELEFONO_CON_LETRAS, TELEFONO_INCOMPLETO,
                                 TELEFONO_LARGO)
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]
CORREO = CONTACTO_VALIDO["correo"]
TELEFONO = CONTACTO_VALIDO["telefono"]


def _no_avanza(flujo):
    return flujo.contacto.visible(2) and not flujo.direccion.visible(2)


@caso("TC-BP-006")
def test_TC_BP_006_contacto_valido(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(**CONTACTO_VALIDO)
    evidencia.captura("Contacto capturado")
    flujo.contacto.continuar()

    assert flujo.direccion.visible(), f"No se avanzó al Paso 2: {flujo.contacto.errores()}"


@caso("TC-BP-007")
def test_TC_BP_007_contacto_vacio(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar("", "")
    flujo.contacto.continuar()
    evidencia.captura("Continuar con formulario vacío")

    assert _no_avanza(flujo), "El sistema avanzó con el formulario vacío"
    assert flujo.contacto.error_correo() == MSG_REQUERIDO, f"Mensaje en correo: '{flujo.contacto.error_correo()}'"
    assert not flujo.contacto.error_telefono(), "El teléfono es opcional y no debería marcar error"


@caso("TC-BP-008")
def test_TC_BP_008_solo_telefono(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=TELEFONO, correo="")
    flujo.contacto.continuar()
    evidencia.captura("Solo teléfono capturado")

    assert _no_avanza(flujo), "El sistema avanzó sin correo"
    assert flujo.contacto.error_correo() == MSG_REQUERIDO, f"Mensaje en correo: '{flujo.contacto.error_correo()}'"


@caso("TC-BP-009")
def test_TC_BP_009_correo_formato_incorrecto(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=TELEFONO, correo=CORREO_SIN_ARROBA)
    flujo.contacto.continuar()
    evidencia.captura(f"Correo: {CORREO_SIN_ARROBA}")

    assert _no_avanza(flujo), "El sistema avanzó con un correo sin arroba"
    assert flujo.contacto.error_correo() == MSG_CORREO_INVALIDO, f"Mensaje: '{flujo.contacto.error_correo()}'"


@caso("TC-BP-010")
def test_TC_BP_010_telefono_incompleto(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=TELEFONO_INCOMPLETO, correo=CORREO)
    flujo.contacto.continuar()
    evidencia.captura(f"Teléfono: {TELEFONO_INCOMPLETO}")

    assert _no_avanza(flujo), "El sistema avanzó con un teléfono incompleto"
    assert flujo.contacto.error_telefono() == MSG_TELEFONO, f"Mensaje: '{flujo.contacto.error_telefono()}'"


@caso("TC-BP-011")
def test_TC_BP_011_telefono_con_letras(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=TELEFONO_CON_LETRAS, correo=CORREO)
    valor = flujo.contacto.telefono_mostrado()
    flujo.contacto.continuar()
    evidencia.captura(f"Teléfono escrito '{TELEFONO_CON_LETRAS}' -> quedó '{valor}'")

    assert valor.isdigit() or flujo.contacto.error_telefono(), f"El campo aceptó letras ('{valor}') sin mostrar error"
    assert _no_avanza(flujo), "El sistema avanzó con un teléfono que contiene letras"


@caso("TC-BP-052")
def test_TC_BP_052_telefono_opcional(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono="", correo=CORREO)
    evidencia.captura("Solo correo capturado")
    flujo.contacto.continuar()

    assert flujo.direccion.visible(), f"No se avanzó sin teléfono: {flujo.contacto.errores()}"


@caso("TC-BP-053")
def test_TC_BP_053_correos_invalidos(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    aceptados = []
    for correo in CORREOS_INVALIDOS:
        flujo.contacto.llenar(telefono=TELEFONO, correo=correo)
        flujo.contacto.continuar()
        if flujo.direccion.visible(3):
            aceptados.append(correo)
            evidencia.captura(f"ACEPTADO: {correo}", estado="fallo")
            flujo.direccion.regresar()
            flujo.contacto.visible()
        else:
            evidencia.captura(f"Rechazado: {correo} -> {flujo.contacto.error_correo()}")

    assert not aceptados, f"Se aceptaron correos inválidos: {aceptados}"


@caso("TC-BP-054")
def test_TC_BP_054_telefono_largo(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    flujo.contacto.llenar(telefono=TELEFONO_LARGO, correo=CORREO)
    mostrado = flujo.contacto.telefono_mostrado()
    digitos = "".join(c for c in mostrado if c.isdigit())
    evidencia.captura(f"Se escribieron 14 dígitos -> el campo muestra '{mostrado}'")
    if len(digitos) <= 13:
        evidencia.nota(f"El campo limita la captura a {len(digitos)} dígitos")
        return

    flujo.contacto.continuar()
    mensaje = flujo.contacto.error_telefono()
    assert _no_avanza(flujo), f"El sistema aceptó un teléfono de {len(digitos)} dígitos"
    assert "13" in mensaje or "máximo" in mensaje.lower(), f"El mensaje no indica el máximo permitido: '{mensaje}'"
