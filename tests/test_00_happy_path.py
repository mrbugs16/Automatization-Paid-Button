"""
MÓDULO 00 - HAPPY PATH (flujo completo de pago con datos válidos)
· TC-BP-050

Es la prueba base: si esta falla, el resto del flujo no se puede validar.
Cada paso deja captura en la evidencia.
"""
import pytest

from config.datos_prueba import CONTACTO_VALIDO, DIRECCION_VALIDA
from core import datos
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-050")
@pytest.mark.pago
def test_TC_BP_050_happy_path(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("principal")

    # Validación del enlace
    estado = flujo.abrir_enlace(enlace_valido)
    assert estado == "formulario", f"El enlace no mostró el formulario (estado: {estado})"
    evidencia.nota(f"Encabezado: {flujo.validacion.encabezado()}")

    # Paso 1 - Contacto
    flujo.contacto.llenar(**CONTACTO_VALIDO)
    evidencia.captura("Paso 1 - Contacto capturado")
    flujo.contacto.continuar()
    assert flujo.direccion.visible(), f"No se avanzó al Paso 2: {flujo.contacto.errores()}"

    # Paso 2 - Dirección
    flujo.direccion.llenar(**DIRECCION_VALIDA)
    evidencia.captura("Paso 2 - Dirección capturada")
    flujo.direccion.continuar()
    assert flujo.tarjeta.visible(), f"No se avanzó al Paso 3: {flujo.direccion.errores()}"

    # Paso 3 - Tarjeta
    flujo.tarjeta.llenar_con(tarjeta)
    evidencia.captura("Paso 3 - Tarjeta capturada")
    flujo.tarjeta.continuar()
    assert flujo.confirmacion.visible(), f"No se avanzó al Paso 4: {flujo.tarjeta.errores()}"

    # Paso 4 - Confirmación
    resumen = flujo.confirmacion.resumen()
    evidencia.captura("Paso 4 - Revisa tu información antes de pagar")
    evidencia.nota(f"Resumen: {resumen}")
    flujo.confirmacion.confirmar_pago()

    # 3DS (si aplica) y resultado
    resultado = flujo.resultado.esperar()
    detalles = flujo.resultado.detalles()
    evidencia.captura(f"Resultado: {flujo.resultado.titulo()}")
    evidencia.nota(f"Detalle: {detalles}")
    if resultado == "aprobada":
        datos.marcar_enlace_pagado(enlace_valido)

    assert resultado == "aprobada", (
        f"{flujo.resultado.titulo()} - Estado: {detalles.get('Estado', '-')}, "
        f"código {detalles.get('Código de respuesta', '-')}")
    assert detalles.get("Código de respuesta") == "00", f"Código de respuesta inesperado: {detalles}"
