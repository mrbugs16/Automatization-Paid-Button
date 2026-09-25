"""
MÓDULO 01 - ACCESO AL ENLACE DE PAGO (inicio del alcance QA - página Memphis)
· TC-BP-001 a TC-BP-005
"""
import time

import pytest

from config import settings
from core import datos
from core.marcadores import caso, pendiente, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-001")
def test_TC_BP_001_enlace_valido(flujo, evidencia, enlace_valido):
    flujo.driver.get(enlace_valido)
    evidencia.captura("Pantalla de validación del enlace")
    flujo.validacion.esperar_fin_validacion()
    evidencia.captura("Formulario después de la validación")

    assert flujo.validacion.muestra_formulario(), "No se mostró el formulario tras validar el enlace"
    resumen = flujo.validacion.resumen()
    evidencia.nota(f"Resumen mostrado: {resumen}")
    assert all(resumen.values()), f"Faltan datos del resumen (importe/concepto/referencia): {resumen}"


@caso("TC-BP-002")
def test_TC_BP_002_enlace_invalido(flujo, evidencia):
    enlaces = {clave: datos.enlace_fijo(clave) for clave in ("vencido", "mal_formado")}
    enlaces = {clave: url for clave, url in enlaces.items() if url}
    if not enlaces:
        pendiente("Faltan los enlaces 'vencido' / 'mal_formado' en data/enlaces_prueba.json")

    for clave, url in enlaces.items():
        flujo.abrir_enlace(url)
        evidencia.captura(f"Enlace {clave}")
        assert flujo.validacion.muestra_error(), f"No se mostró mensaje de error para el enlace {clave}"
        assert not flujo.validacion.muestra_formulario(), f"Se permitió continuar con el enlace {clave}"


@caso("TC-BP-003")
def test_TC_BP_003_enlace_ya_pagado(flujo, evidencia):
    url = datos.enlace_fijo("pagado")
    if not url:
        pendiente("Falta el enlace 'pagado' en data/enlaces_prueba.json")

    flujo.abrir_enlace(url)
    evidencia.captura("Enlace de transacción ya pagada")

    assert flujo.validacion.muestra_ya_pagado(), "No se indicó que el pago ya fue realizado"
    assert not flujo.validacion.muestra_formulario(), "Se permitió volver a capturar un pago ya realizado"


@caso("TC-BP-004")
def test_TC_BP_004_mismo_enlace_dos_pestanas(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_sin_3ds")
    driver = flujo.driver

    pestana_a = driver.current_window_handle
    driver.switch_to.new_window("tab")
    pestana_b = driver.current_window_handle
    flujo.hasta_tarjeta(enlace_valido)
    evidencia.captura("Pestaña B lista en Paso 3")

    driver.switch_to.window(pestana_a)
    resultado = flujo.pagar(enlace_valido, tarjeta)
    evidencia.captura(f"Pestaña A - resultado: {resultado}")
    assert resultado == "aprobada", "El pago en la Pestaña A no se aprobó"

    driver.switch_to.window(pestana_b)
    flujo.tarjeta.llenar_con(tarjeta)
    flujo.tarjeta.pagar()
    evidencia.captura("Pestaña B - intento de segundo pago")
    assert flujo.validacion.muestra_ya_pagado() or flujo.resultado.rechazada(), \
        "La Pestaña B no indicó que la transacción ya fue procesada"
    evidencia.nota("⚠ Validar en backend que exista un solo cobro para la referencia")


@caso("TC-BP-005")
def test_TC_BP_005_token_expira_sin_interaccion(flujo, evidencia, enlace_valido):
    flujo.abrir_enlace(enlace_valido)
    evidencia.captura("Formulario recién abierto")

    print(f"   ⏳ Esperando {settings.TOKEN_TTL_SEG + 5}s a que expire el token…")
    time.sleep(settings.TOKEN_TTL_SEG + 5)
    evidencia.captura("Después del tiempo de vida del token")

    flujo.contacto.llenar(telefono="2221234567", correo="contribuyente@correo.com")
    flujo.contacto.continuar()
    flujo.validacion.esperar_fin_validacion(timeout=60)
    evidencia.captura("Después de intentar continuar")

    assert flujo.validacion.muestra_formulario(), "No se reinició el flujo con un token nuevo"
    assert not flujo.validacion.muestra_error(), "Se quedó en un error sin salida al expirar el token"
