"""
MÓDULO 06 - RESULTADO EXITOSO (fin del alcance QA - redirección al Gobierno)
· TC-BP-029 a TC-BP-031
"""
import pytest

from config import settings
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-029")
def test_TC_BP_029_pantalla_aprobada(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    resultado = flujo.pagar(enlace_valido, tarjeta_de_prueba("aprobada_sin_3ds"))
    evidencia.captura("Pantalla Transacción aprobada")
    assert resultado == "aprobada"

    datos_resultado = flujo.resultado.datos()
    evidencia.nota(f"Datos mostrados: {datos_resultado}")
    assert datos_resultado["referencia"], "No se muestra la referencia"
    assert datos_resultado["folio"], "No se muestra el folio/autorización"


@caso("TC-BP-030")
def test_TC_BP_030_redireccion_automatica(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    assert flujo.pagar(enlace_valido, tarjeta_de_prueba("aprobada_sin_3ds")) == "aprobada"
    evidencia.captura(f"Contador: {flujo.resultado.contador()}")

    redirigio = flujo.resultado.esperar_redireccion_gobierno(settings.CONTADOR_REDIRECCION_SEG + 15)
    evidencia.captura("Después del contador")
    assert redirigio, f"No se redirigió a {settings.DOMINIO_GOBIERNO}; URL actual: {flujo.driver.current_url}"


@caso("TC-BP-031")
def test_TC_BP_031_continuar_antes_del_contador(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    assert flujo.pagar(enlace_valido, tarjeta_de_prueba("aprobada_sin_3ds")) == "aprobada"
    flujo.resultado.continuar()

    redirigio = flujo.resultado.esperar_redireccion_gobierno(3)
    evidencia.captura("Después de clic en Continuar")
    assert redirigio, "No se redirigió de inmediato al dar clic en Continuar"
