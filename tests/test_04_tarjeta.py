"""
MÓDULO 04 - PASO 3 DATOS DE TARJETA
· TC-BP-017 a TC-BP-024
"""
import pytest

from config.datos_prueba import CVV_INCOMPLETO, NUMERO_TARJETA_INVALIDO, VIGENCIA_VENCIDA
from config.locators import TarjetaLoc
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]


@caso("TC-BP-017")
def test_TC_BP_017_tarjeta_valida(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_sin_3ds")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta)
    evidencia.captura("Tarjeta capturada")
    flujo.tarjeta.pagar()

    assert flujo.procesamiento.procesando_visible(), "No se mostró 'Procesando transacción'"
    evidencia.captura("Procesando transacción")


@caso("TC-BP-018")
def test_TC_BP_018_tarjeta_vacia(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.pagar()
    evidencia.captura("Pagar con formulario vacío")

    assert flujo.tarjeta.sigue_en_paso(), "El sistema avanzó con la tarjeta vacía"
    assert len(flujo.tarjeta.errores()) >= 4, "Faltan mensajes de campo obligatorio"


@caso("TC-BP-019")
def test_TC_BP_019_tarjeta_incompleta(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_sin_3ds")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar(numero=tarjeta["numero"])
    flujo.tarjeta.pagar()
    evidencia.captura("Solo número de tarjeta")

    assert flujo.tarjeta.sigue_en_paso(), "El sistema avanzó con campos faltantes"
    errores = flujo.tarjeta.errores()
    evidencia.nota(f"Mensajes: {errores}")
    assert len(errores) >= 3, "Faltan mensajes en nombre, vigencia y CVV"


@caso("TC-BP-020")
def test_TC_BP_020_numero_invalido(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar(NUMERO_TARJETA_INVALIDO, "JUAN PEREZ", "12/30", "123")
    flujo.tarjeta.pagar()
    evidencia.captura(f"Tarjeta: {NUMERO_TARJETA_INVALIDO}")

    assert flujo.tarjeta.existe_error(TarjetaLoc.ERROR_NUMERO), "Falta mensaje de número de tarjeta inválido"
    assert not flujo.procesamiento.procesando_visible(timeout=3), "Se intentó procesar el pago"


@caso("TC-BP-021")
def test_TC_BP_021_tarjeta_vencida(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_sin_3ds")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar(tarjeta["numero"], tarjeta["nombre"], VIGENCIA_VENCIDA, tarjeta["cvv"])
    flujo.tarjeta.pagar()
    evidencia.captura(f"Vigencia: {VIGENCIA_VENCIDA}")

    assert flujo.tarjeta.existe_error(TarjetaLoc.ERROR_VIGENCIA), "Falta mensaje de tarjeta vencida"
    assert flujo.tarjeta.sigue_en_paso(), "Se permitió continuar con tarjeta vencida"


@caso("TC-BP-022")
def test_TC_BP_022_cvv_incompleto(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_sin_3ds")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar(tarjeta["numero"], tarjeta["nombre"], tarjeta["vigencia"], CVV_INCOMPLETO)
    flujo.tarjeta.pagar()
    evidencia.captura(f"CVV: {CVV_INCOMPLETO}")

    assert flujo.tarjeta.existe_error(TarjetaLoc.ERROR_CVV), "Falta mensaje de CVV inválido"
    assert flujo.tarjeta.sigue_en_paso(), "Se permitió continuar con CVV incompleto"


@caso("TC-BP-023")
def test_TC_BP_023_nip_incorrecto(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("nip_incorrecto")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta)
    flujo.tarjeta.pagar()

    assert flujo.procesamiento.es_3ds(), "El banco no solicitó autenticación 3D Secure"
    evidencia.captura("Pantalla del banco (3DS)")
    flujo.procesamiento.autenticar_3ds(tarjeta["codigo_3ds"])

    mensaje = flujo.procesamiento.popup_error()
    evidencia.captura(f"Popup: {mensaje[:60]}")
    assert mensaje, "No apareció el popup de pago rechazado por NIP incorrecto"


@caso("TC-BP-024")
def test_TC_BP_024_numero_enmascarado(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("aprobada_sin_3ds")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar(numero=tarjeta["numero"])
    mostrado = flujo.tarjeta.numero_mostrado()
    evidencia.captura("Número de tarjeta capturado")

    visibles = sum(c.isdigit() for c in mostrado)
    assert mostrado[-4:] == tarjeta["numero"][-4:], "No se muestran los últimos 4 dígitos"
    assert visibles <= 4, f"Se ven {visibles} dígitos; solo deberían verse los últimos 4"
