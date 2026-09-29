"""
MÓDULO 05 - PROCESAMIENTO DEL PAGO Y AUTENTICACIÓN DEL BANCO (3D SECURE)
· TC-BP-025 a TC-BP-028, TC-BP-095 a TC-BP-098

El 3DS es una redirección de página completa: la app sale al sitio del banco y regresa.
Tarjetas de prueba por tipo (data/tarjetas_prueba.json -> catalogo_3ds):
  Not challenge     -> se aprueba sin reto (pruebas SIN 3DS)
  Challenge         -> el banco pide un código; el tester lo captura en Chrome (TRESDS_MODO=manual)
  Attempt           -> autenticación intentada; se aprueba sin reto
  Not authenticated -> la autenticación falla; se rechaza
"""
import time

import pytest

from config import settings
from config.datos_prueba import MSG_TOAST_ERROR
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis, pytest.mark.pago]


def _pagar_sin_reto(flujo, evidencia, url, tarjeta):
    """Tarjetas que no deben pedir nada al usuario: el resultado llega solo, sin capturar códigos."""
    flujo.hasta_confirmacion(url, tarjeta)
    flujo.confirmacion.confirmar_pago()
    paso_por_banco = flujo.resultado.salio_a_3ds(timeout=5)
    resultado = flujo.resultado.esperar(timeout=60)
    evidencia.captura(f"{tarjeta['marca']} {tarjeta['tipo_3ds']}: {flujo.resultado.titulo()}")
    evidencia.nota(f"Redirección al banco: {'sí (sin reto)' if paso_por_banco else 'no'} | Detalle: {flujo.resultado.detalles()}")
    return resultado


@caso("TC-BP-025")
def test_TC_BP_025_pago_sin_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    resultado = _pagar_sin_reto(flujo, evidencia, enlace_valido, tarjeta_de_prueba("aprobada_sin_3ds"))
    assert resultado == "aprobada", f"Tarjeta Not challenge no aprobada: {flujo.resultado.detalles()}"


@caso("TC-BP-026")
def test_TC_BP_026_pago_con_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("aprobada_con_3ds"))
    flujo.confirmacion.confirmar_pago()

    assert flujo.resultado.salio_a_3ds(), "El banco no solicitó autenticación 3D Secure"
    evidencia.captura("Reto 3D Secure del banco (VISA) - capturar el código")
    resultado = flujo.resultado.esperar()
    evidencia.captura(f"De regreso en Memphis - {flujo.resultado.titulo()}")
    assert resultado == "aprobada", f"Detalle: {flujo.resultado.detalles()}"


@caso("TC-BP-027")
def test_TC_BP_027_cancelar_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("aprobada_con_3ds"))
    flujo.confirmacion.confirmar_pago()

    assert flujo.resultado.salio_a_3ds(), "El banco no solicitó autenticación 3D Secure"
    evidencia.captura("Sitio del banco (3DS) - se abandonará con 'Atrás'")
    flujo.driver.back()  # equivalente a cerrar/cancelar la pantalla del banco
    time.sleep(3)
    evidencia.captura("Después de abandonar el 3DS")

    en_resultado = flujo.resultado.rechazada() and flujo.resultado.puede_reintentar()
    en_formulario = flujo.confirmacion.visible(3) or flujo.contacto.visible(3)
    assert en_resultado or en_formulario, "No se regresó al flujo de Memphis con opción de reintentar"


@caso("TC-BP-095")
def test_TC_BP_095_attempt(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    resultado = _pagar_sin_reto(flujo, evidencia, enlace_valido, tarjeta_de_prueba("attempt"))
    assert resultado == "aprobada", f"Tarjeta Attempt no aprobada: {flujo.resultado.detalles()}"


@caso("TC-BP-096")
def test_TC_BP_096_not_authenticated(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    resultado = _pagar_sin_reto(flujo, evidencia, enlace_valido, tarjeta_de_prueba("declinada"))
    assert resultado == "rechazada", "La tarjeta Not authenticated no fue rechazada"
    assert MSG_TOAST_ERROR in flujo.resultado.toast_error(), "No apareció el aviso emergente de error"
    assert flujo.resultado.puede_reintentar(), "No se ofrece 'Reintentar' tras el rechazo por 3DS"


@caso("TC-BP-097")
def test_TC_BP_097_sin_3ds_mastercard(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    resultado = _pagar_sin_reto(flujo, evidencia, enlace_valido, tarjeta_de_prueba("sin_3ds_mc"))
    assert resultado == "aprobada", f"MasterCard Not challenge no aprobada: {flujo.resultado.detalles()}"


@caso("TC-BP-098")
def test_TC_BP_098_challenge_mastercard(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("challenge_mc"))
    flujo.confirmacion.confirmar_pago()

    assert flujo.resultado.salio_a_3ds(), "El banco no mostró el reto 3D Secure"
    evidencia.captura("Reto 3D Secure del banco (MasterCard) - capturar el código")
    resultado = flujo.resultado.esperar()
    evidencia.captura(f"De regreso en Memphis - {flujo.resultado.titulo()}")
    assert resultado == "aprobada", f"Detalle: {flujo.resultado.detalles()}"


@caso("TC-BP-028")
@pytest.mark.lento
def test_TC_BP_028_timeout_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("aprobada_con_3ds"))
    flujo.confirmacion.confirmar_pago()

    assert flujo.resultado.salio_a_3ds(), "El banco no solicitó autenticación 3D Secure"
    evidencia.captura("Sitio del banco (3DS) sin interacción")
    print(f"   ⏳ Esperando {settings.TIMEOUT_3DS_SEG}s sin responder el 3DS…")
    time.sleep(settings.TIMEOUT_3DS_SEG)

    resultado = flujo.resultado.esperar()
    evidencia.captura("Después del tiempo de espera")
    assert resultado == "rechazada", "No se mostró el mensaje de tiempo agotado"
    evidencia.nota("⚠ Validar en backend que no exista cobro para la referencia")
