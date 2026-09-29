"""
MÓDULO 10 - PASO 4 CONFIRMACIÓN ANTES DE PAGAR ("Revisa tu información antes de pagar")
· TC-BP-064 a TC-BP-066

Ninguna de estas pruebas confirma el pago: se quedan en el Paso 4.
"""
import pytest

from config.datos_prueba import CONTACTO_VALIDO, DIRECCION_VALIDA
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-064")
def test_TC_BP_064_resumen_antes_de_pagar(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("principal")
    flujo.hasta_confirmacion(enlace_valido, tarjeta)
    resumen = flujo.confirmacion.resumen()
    evidencia.nota(f"Resumen: {resumen}")

    esperado = {
        "Nombre completo": f"{tarjeta['nombre']} {tarjeta['apellido']}",
        "Correo": CONTACTO_VALIDO["correo"],
        "Teléfono": CONTACTO_VALIDO["telefono"],
        "Dirección": DIRECCION_VALIDA["calle"],
        "Ciudad": DIRECCION_VALIDA["ciudad"],
        "Código postal": DIRECCION_VALIDA["cp"],
    }
    diferencias = {campo: (valor, resumen.get(campo)) for campo, valor in esperado.items()
                   if resumen.get(campo) != valor}
    tarjeta_resumen = resumen.get("Tarjeta", "")
    if not tarjeta_resumen.endswith(tarjeta["numero"][-4:]) or sum(c.isdigit() for c in tarjeta_resumen) > 4:
        diferencias["Tarjeta"] = (f"•••• {tarjeta['numero'][-4:]}", tarjeta_resumen)
    vigencia = "".join(c for c in resumen.get("Vencimiento", "") if c.isdigit())
    if vigencia != tarjeta["vigencia"]:
        diferencias["Vencimiento"] = (tarjeta["vigencia"], resumen.get("Vencimiento"))

    assert not diferencias, f"El resumen no coincide con lo capturado (esperado, mostrado): {diferencias}"


@caso("TC-BP-065")
def test_TC_BP_065_regresar_desde_confirmacion(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("principal")
    flujo.hasta_confirmacion(enlace_valido, tarjeta)
    perdidos = []

    flujo.confirmacion.regresar()
    assert flujo.tarjeta.visible(), "'Regresar' no llevó al Paso 3"
    valores = flujo.tarjeta.valores()
    evidencia.captura("Regreso al Paso 3")
    if (valores["nombre"], valores["apellido"]) != (tarjeta["nombre"], tarjeta["apellido"]):
        perdidos.append(f"tarjeta: {valores}")

    flujo.tarjeta.regresar()
    assert flujo.direccion.visible(), "'Regresar' no llevó al Paso 2"
    evidencia.captura("Regreso al Paso 2")
    if flujo.direccion.valores() != DIRECCION_VALIDA:
        perdidos.append(f"dirección: {flujo.direccion.valores()}")

    flujo.direccion.regresar()
    assert flujo.contacto.visible(), "'Regresar' no llevó al Paso 1"
    evidencia.captura("Regreso al Paso 1")
    if flujo.contacto.valores() != CONTACTO_VALIDO:
        perdidos.append(f"contacto: {flujo.contacto.valores()}")

    assert not perdidos, "Se perdieron datos al regresar: " + " | ".join(perdidos)

    for pagina, siguiente in ((flujo.contacto, flujo.direccion), (flujo.direccion, flujo.tarjeta),
                              (flujo.tarjeta, flujo.confirmacion)):
        pagina.continuar()
        assert siguiente.visible(), f"No se pudo volver a avanzar: {pagina.errores()}"
    evidencia.captura("De nuevo en el Paso 4")


@caso("TC-BP-066")
def test_TC_BP_066_navegar_con_stepper(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_confirmacion(enlace_valido, tarjeta_de_prueba("principal"))

    flujo.confirmacion.ir_al_paso(1)
    assert flujo.contacto.visible(), "El número '1' del indicador no llevó al Paso 1"
    evidencia.captura("Paso 1 desde el indicador")
    assert flujo.contacto.valores() == CONTACTO_VALIDO, f"Se perdieron datos: {flujo.contacto.valores()}"

    # Borrar el correo e intentar saltar directo al Paso 4 con el indicador
    flujo.contacto.llenar(telefono=CONTACTO_VALIDO["telefono"], correo="")
    flujo.contacto.ir_al_paso(4)
    evidencia.captura("Intento de saltar al Paso 4 con el correo vacío")
    assert not flujo.confirmacion.visible(3), "El indicador permitió saltarse la validación del correo"
