"""
MÓDULO 07 - RESULTADO FALLIDO Y REINTENTO
· TC-BP-033, TC-BP-035 y TC-BP-068

Los rechazos usan la tarjeta 'declinada' (VISA 4110 7600 0000 0065, tipo 3DS 'Not authenticated'),
que el banco rechaza como 'Rechazada por 3DS'.
"""
import pytest

from core.marcadores import caso, pendiente, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis, pytest.mark.pago]
DETALLES_ESPERADOS = ("Estado", "Código de respuesta", "Referencia", "Autorización", "Identificador")
PALABRAS_EN_INGLES = ("payment", "payout", "invalid", "request", "verified", "arguments")


def _rechazo_con(flujo, url, tarjeta):
    resultado = flujo.pagar(url, tarjeta)
    if resultado != "rechazada":
        pendiente(f"La tarjeta usada no fue rechazada (resultado: {resultado}); se necesita una tarjeta de rechazo")
    return flujo.resultado.detalles()


@caso("TC-BP-033")
def test_TC_BP_033_reintentar(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    _rechazo_con(flujo, enlace_valido, tarjeta_de_prueba("declinada"))
    referencia = flujo.validacion.encabezado().get("Referencia")
    flujo.resultado.reintentar()
    estado = flujo.validacion.esperar_fin_validacion()
    evidencia.captura("Después de Reintentar")

    assert estado == "formulario", f"No se regresó al formulario de pago (estado: {estado})"
    assert flujo.validacion.encabezado().get("Referencia") == referencia, "Se perdió la referencia original"


@caso("TC-BP-035")
def test_TC_BP_035_reintentos_repetidos(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    declinada = tarjeta_de_prueba("declinada")
    _rechazo_con(flujo, enlace_valido, declinada)

    for intento in range(2, 5):
        assert flujo.resultado.puede_reintentar(), f"Sin opción de reintentar en el intento {intento}"
        flujo.resultado.reintentar()
        flujo.validacion.esperar_fin_validacion()
        resultado = flujo.pagar(flujo.driver.current_url, declinada)
        assert resultado == "rechazada", f"Intento {intento}: resultado inesperado '{resultado}'"
    evidencia.nota("⚠ Validar en backend que no exista ningún cobro parcial")


@caso("TC-BP-068")
def test_TC_BP_068_reintentar_tras_rechazo_3ds(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("declinada")
    primero = _rechazo_con(flujo, enlace_valido, tarjeta)
    evidencia.nota(f"Primer intento: {primero}")

    flujo.resultado.reintentar()
    flujo.validacion.esperar_fin_validacion()
    flujo.pagar(flujo.driver.current_url, tarjeta)
    segundo = flujo.resultado.detalles()
    evidencia.nota(f"Segundo intento: {segundo}")

    assert "invalid arguments" not in segundo.get("Estado", "").lower(), \
        f"El reintento falló con: {segundo.get('Estado')}"
