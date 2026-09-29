"""
MÓDULO 09 - COMPATIBILIDAD Y ACCESIBILIDAD
· TC-BP-047 a TC-BP-049

TC-BP-048 se automatiza con MODO_DRIVER=appium_android (Chrome en celular Android).
Edge y Safari requieren otros drivers de Appium; mientras tanto quedan como manuales.
"""
import pytest

from config import settings
from core.marcadores import caso, manual, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-047")
@manual("Ejecutar el flujo completo en Edge y Safari (Chrome se cubre con el resto de la suite)")
def test_TC_BP_047_navegadores():
    pass


@caso("TC-BP-048")
@pytest.mark.pago
@pytest.mark.skipif(settings.MODO_DRIVER != "appium_android",
                    reason="MANUAL: ejecutar con MODO_DRIVER=appium_android (Chrome en celular Android)")
def test_TC_BP_048_celular(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    resultado = flujo.pagar(enlace_valido, tarjeta_de_prueba("principal"))
    evidencia.captura(f"Flujo completo en celular: {resultado}")
    assert resultado == "aprobada", f"Detalle: {flujo.resultado.detalles()}"


@caso("TC-BP-049")
@manual("Revisión de legibilidad y claridad de textos desde la perspectiva del contribuyente")
def test_TC_BP_049_legibilidad():
    pass
