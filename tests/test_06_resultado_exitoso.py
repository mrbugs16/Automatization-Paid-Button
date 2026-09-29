"""
MÓDULO 06 - RESULTADO EXITOSO (fin del alcance QA - redirección al Gobierno)
· TC-BP-029 a TC-BP-031

Cada prueba aprueba un pago y consume el link: se necesita un link nuevo por prueba.
"""
import pytest

from config import settings
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis, pytest.mark.pago]
DETALLES_ESPERADOS = ("Estado", "Código de respuesta", "Referencia", "Autorización", "Identificador")


@caso("TC-BP-029")
def test_TC_BP_029_pantalla_aprobada(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    resultado = flujo.pagar(enlace_valido, tarjeta_de_prueba("principal"))
    detalles = flujo.resultado.detalles()
    evidencia.nota(f"Detalle: {detalles}")
    assert resultado == "aprobada", f"{flujo.resultado.titulo()}: {detalles}"

    vacios = [campo for campo in DETALLES_ESPERADOS if detalles.get(campo, "-") in ("", "-")]
    assert not vacios, f"Datos faltantes en la pantalla de aprobación: {vacios}"


@caso("TC-BP-030")
def test_TC_BP_030_redireccion_automatica(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    assert flujo.pagar(enlace_valido, tarjeta_de_prueba("principal")) == "aprobada", "El pago no se aprobó"
    evidencia.captura(f"Contador: {flujo.resultado.contador()}")

    redirigio = flujo.resultado.esperar_redireccion_gobierno(settings.CONTADOR_REDIRECCION_SEG + 15)
    evidencia.captura("Después del contador")
    assert redirigio, f"No se redirigió a {settings.DOMINIO_GOBIERNO}; URL actual: {flujo.driver.current_url}"


@caso("TC-BP-031")
def test_TC_BP_031_continuar_antes_del_contador(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    assert flujo.pagar(enlace_valido, tarjeta_de_prueba("principal")) == "aprobada", "El pago no se aprobó"
    flujo.resultado.continuar()

    redirigio = flujo.resultado.esperar_redireccion_gobierno(5)
    evidencia.captura("Después de clic en 'Continuar en N s.'")
    assert redirigio, "No se redirigió de inmediato al dar clic en Continuar"
