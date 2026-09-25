"""
MÓDULO 05 - PROCESAMIENTO DEL PAGO Y AUTENTICACIÓN DEL BANCO (3D SECURE)
· TC-BP-025 a TC-BP-028
"""
import time

import pytest

from config import settings
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-025")
def test_TC_BP_025_pago_sin_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_sin_3ds")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta)
    flujo.tarjeta.pagar()

    assert not flujo.procesamiento.es_3ds(timeout=5), "Se pidió 3DS a una tarjeta configurada sin 3DS"
    resultado = flujo.resultado.esperar()
    evidencia.captura(f"Resultado: {resultado}")
    assert resultado == "aprobada"


@caso("TC-BP-026")
def test_TC_BP_026_pago_con_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_con_3ds")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta)
    flujo.tarjeta.pagar()

    assert flujo.procesamiento.es_3ds(), "El banco no solicitó autenticación 3D Secure"
    evidencia.captura("Pantalla del banco (3DS)")
    flujo.procesamiento.autenticar_3ds(tarjeta["codigo_3ds"])

    resultado = flujo.resultado.esperar()
    evidencia.captura(f"De regreso en Memphis - {resultado}")
    assert resultado == "aprobada"


@caso("TC-BP-027")
def test_TC_BP_027_cancelar_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_con_3ds")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta)
    flujo.tarjeta.pagar()

    assert flujo.procesamiento.es_3ds(), "El banco no solicitó autenticación 3D Secure"
    flujo.procesamiento.cancelar_3ds()
    evidencia.captura("3DS cancelado")

    resultado = flujo.resultado.esperar()
    assert resultado == "rechazada", "No se mostró error tras cancelar 3DS"
    assert flujo.resultado.puede_reintentar(), "No se ofrece reintentar el pago"


@caso("TC-BP-028")
def test_TC_BP_028_timeout_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_con_3ds")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta)
    flujo.tarjeta.pagar()

    assert flujo.procesamiento.es_3ds(), "El banco no solicitó autenticación 3D Secure"
    evidencia.captura("Pantalla del banco (3DS) sin interacción")
    print(f"   ⏳ Esperando {settings.TIMEOUT_3DS_SEG}s sin responder 3DS…")
    time.sleep(settings.TIMEOUT_3DS_SEG)

    resultado = flujo.resultado.esperar()
    evidencia.captura("Después del tiempo de espera")
    assert resultado == "rechazada", "No se mostró el mensaje de tiempo agotado"
    evidencia.nota("⚠ Validar en backend que no exista cobro para la referencia")
