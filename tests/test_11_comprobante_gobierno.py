"""
MÓDULO 06 (continuación) - COMPROBANTE DE PAGO EN EL PORTAL DEL GOBIERNO
· TC-BP-099

Tras un pago aprobado, el Botón de Pago redirige (contador de 10 s) al 'COMPROBANTE DE PAGO' del Gobierno.
Se valida que los datos coincidan con los que mostró Memphis. Cada prueba aprueba un pago (consume un link).
"""
import re

import pytest

from config import settings
from core.marcadores import caso, exigir_aprobado, requiere_memphis
from pages.gobierno_comprobante_page import ComprobanteGobiernoPage

pytestmark = [pytest.mark.memphis, requiere_memphis, pytest.mark.pago]


def _pagar_y_llegar_al_comprobante(flujo, evidencia, url, tarjeta):
    exigir_aprobado(flujo.pagar(url, tarjeta), flujo.resultado.detalles())
    detalles = flujo.resultado.detalles()
    flujo.resultado.esperar_redireccion_gobierno(settings.CONTADOR_REDIRECCION_SEG + 15)
    comprobante = ComprobanteGobiernoPage(flujo.driver)
    assert comprobante.visible(), f"No se mostró el 'COMPROBANTE DE PAGO' del Gobierno (URL: {flujo.driver.current_url})"
    evidencia.captura("Comprobante de pago del Gobierno")
    return comprobante, detalles


@caso("TC-BP-099")
def test_TC_BP_099_datos_del_comprobante(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("principal")
    comprobante, memphis = _pagar_y_llegar_al_comprobante(flujo, evidencia, enlace_valido, tarjeta)
    gobierno = comprobante.datos()
    evidencia.nota(f"Memphis: {memphis} | Gobierno: {gobierno}")

    problemas = []
    if gobierno["autorizacion"] != memphis.get("Autorización"):
        problemas.append(f"autorización distinta (Memphis '{memphis.get('Autorización')}' vs Gobierno '{gobierno['autorizacion']}')")
    nombre = f"{tarjeta['nombre']} {tarjeta['apellido']}"
    if gobierno["tarjetahabiente"] != nombre:
        problemas.append(f"tarjetahabiente '{gobierno['tarjetahabiente']}' (esperado '{nombre}')")
    fecha = comprobante.fecha_sin_leyenda()
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}", fecha):
        problemas.append(f"fecha '{fecha}' no tiene el formato DD/MM/YYYY HH24:MI:SS que anuncia la página")
    if "Formato" in gobierno["fecha"]:
        problemas.append("se muestra al contribuyente la leyenda técnica 'Formato(...)' junto a la fecha")
    if not all(gobierno.values()):
        problemas.append(f"campos vacíos: {[k for k, v in gobierno.items() if not v]}")
    assert not problemas, "Comprobante con diferencias: " + "; ".join(problemas)
