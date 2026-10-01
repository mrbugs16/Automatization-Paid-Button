"""
MÓDULO 12 - PASO 4: MESES SIN INTERESES (OPCIONAL)
· TC-MSI-001 y TC-MSI-002 (fuera de la matriz)

En el Paso 4 la página muestra "Tu tarjeta participa en promociones de meses sin intereses.
Seleccionar un plan es opcional:" con una sola opción: "6 meses".
La tarjeta principal (VISA •••• 1111) participa en la promoción.
"""
import pytest

from config.datos_prueba import MESES_MSI, OPCIONES_MSI, TEXTO_MSI
from core.marcadores import caso, pendiente, requiere_memphis

MODULO = "12. Paso 4 - Meses sin intereses"
pytestmark = [pytest.mark.memphis, requiere_memphis]


def _exigir_promocion(flujo):
    if not flujo.confirmacion.ofrece_msi():
        pendiente("La tarjeta de prueba no muestra la promoción de meses sin intereses en el Paso 4")


# ==============================================
# TC-MSI-001: SE OFRECE SOLO "6 MESES" Y SE PUEDE SELECCIONAR
# ==============================================
@caso("TC-MSI-001", modulo=MODULO, caso="Paso 4 ofrece solo el plan de 6 meses sin intereses y se puede seleccionar",
      tipo="EXITO", prioridad="Alta",
      pasos="1. Llenar Contacto, Dirección y Tarjeta (VISA que participa)\n2. En el Paso 4 revisar la leyenda de "
            "meses sin intereses\n3. Seleccionar '6 meses'",
      datos="Tarjeta VISA •••• 1111 (principal)",
      esperado="Se muestra la leyenda, la única opción es '6 meses', ninguna viene marcada y al dar clic queda seleccionada")
def test_TC_MSI_001_opcion_6_meses(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("principal"))
    _exigir_promocion(flujo)

    texto = flujo.confirmacion.texto_msi()
    opciones = flujo.confirmacion.opciones_msi()
    preseleccionado = flujo.confirmacion.plan_msi_seleccionado()
    evidencia.nota(f"Leyenda: {texto} | Opciones: {opciones} | Preseleccionado: {preseleccionado or 'ninguno'}")

    assert texto == TEXTO_MSI, f"Leyenda distinta: '{texto}'"
    assert opciones == OPCIONES_MSI, f"Se esperaba solo {OPCIONES_MSI} y se muestran {opciones}"
    assert not preseleccionado, f"El plan es opcional pero viene marcado: '{preseleccionado}'"

    flujo.confirmacion.seleccionar_msi(MESES_MSI)
    evidencia.captura("Plan de 6 meses seleccionado")
    assert flujo.confirmacion.plan_msi_seleccionado() == OPCIONES_MSI[0]


# ==============================================
# TC-MSI-002: PAGO APROBADO A 6 MESES SIN INTERESES
# ==============================================
@caso("TC-MSI-002", modulo=MODULO, caso="Pago aprobado eligiendo 6 meses sin intereses",
      tipo="EXITO", prioridad="Alta",
      pasos="1. Llenar Contacto, Dirección y Tarjeta (VISA que participa)\n2. En el Paso 4 seleccionar '6 meses'\n"
            "3. Dar clic en 'Continuar'",
      datos="Tarjeta VISA •••• 1111 (escenario msi_6_meses)",
      esperado="La transacción se aprueba con el plan de 6 meses sin intereses")
@pytest.mark.pago
def test_TC_MSI_002_pago_6_meses(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("msi_6_meses")
    flujo.hasta_confirmacion(enlace_valido, tarjeta)  # el escenario trae "msi": 6 y el flujo elige el plan
    _exigir_promocion(flujo)
    assert flujo.confirmacion.plan_msi_seleccionado() == OPCIONES_MSI[0], "No quedó seleccionado el plan de 6 meses"

    flujo.confirmacion.confirmar_pago()
    resultado = flujo.resultado.esperar()
    evidencia.captura(f"Resultado: {flujo.resultado.titulo() or resultado}")
    evidencia.nota(f"Detalle: {flujo.resultado.detalles()}")
    assert resultado == "aprobada", f"El pago a 6 meses no se aprobó: {flujo.resultado.detalles()}"
