"""
PRECONDICIÓN (Fase 1 - Gobierno de Puebla, fuera del alcance de la matriz).
Llega desde el portal del Gobierno hasta la pantalla de 'Pago de predial'.

· TC-GOB-001: Abrir portal y entrar a 'Predial'
"""
import pytest

from core.marcadores import caso
from pages.gobierno_predial_page import PredialPage

MODULO = "00. Precondición - Portal Gobierno de Puebla (fuera de alcance)"
pytestmark = pytest.mark.gobierno


# ==============================================
# TC-GOB-001: ABRIR PORTAL Y ENTRAR A PREDIAL
# ==============================================
@caso("TC-GOB-001", modulo=MODULO, caso="Abrir portal del Gobierno y entrar a 'Predial'",
      tipo="EXITO", prioridad="Alta",
      pasos="1. Abrir el portal de pagos del Gobierno\n2. Dar clic en 'Predial'",
      datos="N/A",
      esperado="Se muestra la pantalla 'Pago de predial' con tipo, cuenta, delegación, línea de captura y captcha")
def test_TC_GOB_001_ir_a_predial(driver, evidencia):
    predial = PredialPage(driver)

    predial.abrir_inicio()
    evidencia.captura("Portal de pagos del Gobierno")

    predial.ir_a_predial()
    evidencia.captura("Pantalla Pago de predial")

    campos = predial.formulario_completo_visible()
    faltantes = [c for c, visible in campos.items() if not visible]
    assert not faltantes, f"Campos no visibles en Pago de predial: {faltantes}"
