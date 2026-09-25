"""
MÓDULO 07 - RESULTADO FALLIDO Y REINTENTO
· TC-BP-032 a TC-BP-035
"""
import pytest

from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-032")
def test_TC_BP_032_pantalla_rechazada(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    resultado = flujo.pagar(enlace_valido, tarjeta_de_prueba("declinada"))
    evidencia.captura("Pantalla Transacción rechazada")

    assert resultado == "rechazada"
    mensaje = flujo.resultado.datos()["mensaje"]
    evidencia.nota(f"Mensaje al contribuyente: {mensaje}")
    assert mensaje, "No se muestra un mensaje comprensible del rechazo"


@caso("TC-BP-033")
def test_TC_BP_033_reintentar(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    assert flujo.pagar(enlace_valido, tarjeta_de_prueba("declinada")) == "rechazada"
    referencia = flujo.resultado.datos()["referencia"]
    flujo.resultado.reintentar()
    evidencia.captura("Después de Reintentar")

    assert flujo.tarjeta.visible(), "No se regresó al formulario de pago"
    if referencia:
        assert referencia in flujo.driver.page_source, "Se perdió la referencia original"


@caso("TC-BP-034")
def test_TC_BP_034_reintento_con_tarjeta_valida(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    assert flujo.pagar(enlace_valido, tarjeta_de_prueba("declinada")) == "rechazada"
    evidencia.captura("Primer intento rechazado")
    flujo.resultado.reintentar()

    valida = tarjeta_de_prueba("aprobada_sin_3ds")
    flujo.tarjeta.llenar_con(valida)
    flujo.tarjeta.pagar()
    resultado = flujo.resultado.esperar()
    evidencia.captura(f"Segundo intento: {resultado}")
    assert resultado == "aprobada"


@caso("TC-BP-035")
def test_TC_BP_035_reintentos_repetidos(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    declinada = tarjeta_de_prueba("declinada")
    assert flujo.pagar(enlace_valido, declinada) == "rechazada"

    for intento in range(2, 5):
        flujo.resultado.reintentar()
        assert flujo.tarjeta.visible(), f"Usuario bloqueado en el intento {intento}"
        flujo.tarjeta.llenar_con(declinada)
        flujo.tarjeta.pagar()
        resultado = flujo.resultado.esperar()
        evidencia.captura(f"Intento {intento}: {resultado}")
        assert resultado == "rechazada"
    evidencia.nota("⚠ Validar en backend que no exista ningún cobro parcial")
