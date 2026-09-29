"""
Marcadores para vincular cada prueba con la matriz y clasificar su estado en el reporte.

    @caso("TC-BP-006")                      -> toma nombre, módulo, tipo, etc. de la matriz
    @requiere_memphis                       -> 'Pendiente' mientras MEMPHIS_DISPONIBLE=false
    @manual("motivo")                       -> 'Manual' (no automatizable / requiere intervención)
"""
import pytest

from config import settings

PREFIJO_PENDIENTE = "PENDIENTE:"
PREFIJO_MANUAL = "MANUAL:"


def caso(caso_id, **meta):
    return pytest.mark.caso(caso_id, **meta)


requiere_memphis = pytest.mark.skipif(
    not settings.MEMPHIS_DISPONIBLE,
    reason=f"{PREFIJO_PENDIENTE} Botón de pago Memphis aún no disponible (integración con API en curso)",
)


def manual(motivo):
    return pytest.mark.skip(reason=f"{PREFIJO_MANUAL} {motivo}")


def pendiente(motivo):
    """Para usar dentro de una prueba cuando falta un dato (enlace, tarjeta, etc.)."""
    pytest.skip(f"{PREFIJO_PENDIENTE} {motivo}")


def exigir_aprobado(resultado, detalles=None):
    """Para casos cuya PRECONDICIÓN es un pago aprobado: si no se aprobó, el caso no se pudo probar."""
    if resultado != "aprobada":
        estado = (detalles or {}).get("Estado", resultado)
        pytest.skip(f"{PREFIJO_PENDIENTE} Bloqueado: requiere un pago aprobado y la tarjeta fue rechazada ({estado})")
