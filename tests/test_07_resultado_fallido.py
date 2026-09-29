"""
MÓDULO 07 - RESULTADO FALLIDO Y REINTENTO
· TC-BP-032 a TC-BP-035, TC-BP-067 a TC-BP-069

Los rechazos usan la tarjeta 'declinada' (VISA 4110 7600 0000 0065, tipo 3DS 'Not authenticated'),
que el banco rechaza como 'Rechazada por 3DS'.
"""
import pytest

from config.datos_prueba import MSG_TOAST_ERROR
from core.marcadores import caso, pendiente, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis, pytest.mark.pago]
DETALLES_ESPERADOS = ("Estado", "Código de respuesta", "Referencia", "Autorización", "Identificador")
PALABRAS_EN_INGLES = ("payment", "payout", "invalid", "request", "verified", "arguments")


def _rechazo_con(flujo, url, tarjeta):
    resultado = flujo.pagar(url, tarjeta)
    if resultado != "rechazada":
        pendiente(f"La tarjeta usada no fue rechazada (resultado: {resultado}); se necesita una tarjeta de rechazo")
    return flujo.resultado.detalles()


@caso("TC-BP-032")
def test_TC_BP_032_pantalla_rechazada(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    detalles = _rechazo_con(flujo, enlace_valido, tarjeta_de_prueba("declinada"))
    evidencia.nota(f"Detalle: {detalles}")

    assert detalles.get("Estado"), "No se muestra el motivo del rechazo"
    assert MSG_TOAST_ERROR in flujo.resultado.toast_error(), "No apareció el aviso emergente de error"


@caso("TC-BP-033")
def test_TC_BP_033_reintentar(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    _rechazo_con(flujo, enlace_valido, tarjeta_de_prueba("declinada"))
    referencia = flujo.validacion.encabezado().get("Referencia")
    flujo.resultado.reintentar()
    estado = flujo.validacion.esperar_fin_validacion()
    evidencia.captura("Después de Reintentar")

    assert estado == "formulario", f"No se regresó al formulario de pago (estado: {estado})"
    assert flujo.validacion.encabezado().get("Referencia") == referencia, "Se perdió la referencia original"


@caso("TC-BP-034")
def test_TC_BP_034_reintento_con_tarjeta_valida(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    valida = tarjeta_de_prueba("aprobada_sin_3ds")
    _rechazo_con(flujo, enlace_valido, tarjeta_de_prueba("declinada"))
    flujo.resultado.reintentar()
    flujo.validacion.esperar_fin_validacion()

    resultado = flujo.pagar(flujo.driver.current_url, valida)
    assert resultado == "aprobada", f"El segundo intento no se aprobó: {flujo.resultado.detalles()}"


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


@caso("TC-BP-067")
def test_TC_BP_067_detalle_y_toast_de_rechazo(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    detalles = _rechazo_con(flujo, enlace_valido, tarjeta_de_prueba("declinada"))
    toast = flujo.resultado.toast_error()
    evidencia.nota(f"Detalle: {detalles} | Aviso: {toast}")

    faltantes = [c for c in DETALLES_ESPERADOS if c not in detalles]
    assert not faltantes, f"Faltan renglones en el detalle: {faltantes}"
    assert MSG_TOAST_ERROR in toast, f"Aviso emergente inesperado: '{toast}'"


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


@caso("TC-BP-069")
def test_TC_BP_069_textos_de_rechazo(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    detalles = _rechazo_con(flujo, enlace_valido, tarjeta_de_prueba("declinada"))
    textos = {"subtítulo": flujo.resultado.subtitulo(), "estado": detalles.get("Estado", "")}
    evidencia.nota(f"Textos: {textos}")

    en_ingles = {k: v for k, v in textos.items() if any(p in v.lower() for p in PALABRAS_EN_INGLES)}
    assert not en_ingles, f"Textos en inglés o técnicos en la pantalla de rechazo: {en_ingles}"
