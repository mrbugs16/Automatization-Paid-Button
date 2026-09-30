"""
MÓDULO 01 - ACCESO AL ENLACE DE PAGO (inicio del alcance QA - página Memphis)
· TC-BP-001 a TC-BP-005
"""
import pytest

from config import settings
from config.datos_prueba import CONTACTO_VALIDO, MSG_LINK_INVALIDO
from core import datos
from core.marcadores import caso, exigir_aprobado, pendiente, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-001")
def test_TC_BP_001_enlace_valido(flujo, evidencia, enlace_valido):
    flujo.driver.get(enlace_valido)
    evidencia.captura("Pantalla 'Validando link de pago'")

    estado = flujo.validacion.esperar_fin_validacion()
    evidencia.captura("Después de la validación")
    assert estado == "formulario", f"No se mostró el formulario (estado: {estado})"

    encabezado = flujo.validacion.encabezado()
    evidencia.nota(f"Encabezado: {encabezado}")
    faltantes = [c for c in ("importe", "concepto", "Referencia") if not encabezado.get(c)]
    assert not faltantes, f"Faltan datos en el encabezado: {faltantes}"


@caso("TC-BP-002")
def test_TC_BP_002_enlace_invalido(flujo, evidencia):
    enlaces = {clave: datos.enlace_fijo(clave) for clave in ("vencido", "mal_formado")}
    enlaces = {clave: url for clave, url in enlaces.items() if url}
    if not enlaces:
        pendiente("Faltan los enlaces 'vencido' / 'mal_formado' en data/enlaces_prueba.json")

    for clave, url in enlaces.items():
        estado = flujo.abrir_enlace(url)
        evidencia.captura(f"Enlace {clave}")
        assert estado == "invalido", f"El enlace {clave} no mostró error (estado: {estado})"
        mensaje = flujo.validacion.mensaje_invalido()
        assert MSG_LINK_INVALIDO in mensaje, f"Mensaje inesperado para el enlace {clave}: {mensaje}"


@caso("TC-BP-003")
def test_TC_BP_003_enlace_ya_pagado(flujo, evidencia):
    url = datos.enlace_pagado()
    if not url:
        pendiente("Aún no hay links pagados en data/enlaces_prueba.json (se llena solo tras un pago aprobado)")

    estado = flujo.abrir_enlace(url)
    evidencia.captura("Enlace de transacción ya pagada")
    assert estado != "formulario", "Se permitió volver a capturar un pago ya realizado"


@caso("TC-BP-004")
@pytest.mark.pago
def test_TC_BP_004_mismo_enlace_dos_pestanas(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("principal")
    driver = flujo.driver

    pestana_a = driver.current_window_handle
    driver.switch_to.new_window("tab")
    pestana_b = driver.current_window_handle
    flujo.hasta_confirmacion(enlace_valido, tarjeta)
    evidencia.captura("Pestaña B lista en Paso 4")

    driver.switch_to.window(pestana_a)
    exigir_aprobado(flujo.pagar(enlace_valido, tarjeta), flujo.resultado.detalles())

    driver.switch_to.window(pestana_b)
    flujo.confirmacion.confirmar_pago()
    resultado_b = flujo.resultado.esperar()
    evidencia.captura(f"Pestaña B - segundo intento: {resultado_b}")
    assert resultado_b != "aprobada", "La Pestaña B aprobó un segundo cobro con el mismo enlace"
    evidencia.nota("⚠ Validar en backend que exista un solo cobro para la referencia")


@caso("TC-BP-005")
def test_TC_BP_005_token_no_expira_sin_interaccion(flujo, evidencia, enlace_valido):
    """Regla de revisión (29/09/2026): el token NO debe expirar; si la referencia queda en uso, se solicita liberarla."""
    flujo.abrir_enlace(enlace_valido)
    limite = settings.TIMEOUT_TOKEN_SEG

    print(f"   ⏳ Vigilando {limite}s sin interactuar (el token no debe expirar)…")
    reaccion = flujo.validacion.esperar_reaccion_por_token(limite)
    evidencia.captura(f"Tras {limite}s sin interactuar: {reaccion or 'sin cambios'}")
    assert not reaccion, f"El token expiró o el flujo se reinició por inactividad ({reaccion})"

    flujo.contacto.llenar(**CONTACTO_VALIDO)
    flujo.contacto.continuar()
    evidencia.captura("Después de continuar")
    assert flujo.direccion.visible(), f"No se pudo continuar el pago tras la inactividad: {flujo.contacto.errores()}"
