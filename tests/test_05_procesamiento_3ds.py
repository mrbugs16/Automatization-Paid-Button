"""
MÓDULO 05 - PROCESAMIENTO DEL PAGO Y AUTENTICACIÓN DEL BANCO (3D SECURE)
· TC-BP-025 a TC-BP-028

El 3DS es una redirección de página completa: la app sale al sitio del banco y regresa.
"""
import time

import pytest

from config import settings
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis, pytest.mark.pago]


@caso("TC-BP-025")
def test_TC_BP_025_pago_sin_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("aprobada_sin_3ds"))
    flujo.confirmacion.confirmar_pago()

    assert not flujo.resultado.salio_a_3ds(timeout=10), "Se pidió 3DS a una tarjeta configurada sin 3DS"
    resultado = flujo.resultado.esperar()
    evidencia.captura(f"Resultado: {flujo.resultado.titulo()}")
    assert resultado == "aprobada", f"Detalle: {flujo.resultado.detalles()}"


@caso("TC-BP-026")
def test_TC_BP_026_pago_con_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("aprobada_con_3ds"))
    flujo.confirmacion.confirmar_pago()

    assert flujo.resultado.salio_a_3ds(), "El banco no solicitó autenticación 3D Secure"
    evidencia.captura("Sitio del banco (3DS)")
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
