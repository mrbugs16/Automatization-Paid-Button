"""
MÓDULO 04 - PASO 3 DATOS DE TARJETA
· TC-BP-017 a TC-BP-024, TC-BP-059 a TC-BP-063

Reglas de la página: nombre y apellido solo letras (con acento); tarjeta de 15 o 16 dígitos;
vencimiento MMAA vigente; CVV de 3 dígitos. Solo TC-BP-023 confirma un pago.
"""
import pytest

from config.datos_prueba import (APELLIDO_COMPUESTO, CVV_INCOMPLETO, MSG_CVV, MSG_NOMBRE, MSG_REQUERIDO,
                                 MSG_TARJETA_LONGITUD, MSG_TOAST_ERROR, MSG_VIGENCIA_INVALIDA,
                                 MSG_VIGENCIA_LONGITUD, NOMBRE_CON_NUMEROS, NUMERO_TARJETA_CORTO,
                                 NUMERO_TARJETA_INVALIDO, VIGENCIA_INCOMPLETA, VIGENCIA_MES_INVALIDO,
                                 VIGENCIA_VENCIDA)
from core.marcadores import caso, requiere_memphis

pytestmark = [pytest.mark.memphis, requiere_memphis]
CAMPOS = ("name", "lastName", "card", "expiration", "cvv")


def _no_avanza(flujo):
    return flujo.tarjeta.visible(2) and not flujo.confirmacion.visible(2)


@caso("TC-BP-017")
def test_TC_BP_017_tarjeta_valida(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta_de_prueba("principal"))
    evidencia.captura("Tarjeta capturada")
    flujo.tarjeta.continuar()

    assert flujo.confirmacion.visible(), f"No se avanzó al Paso 4: {flujo.tarjeta.errores()}"


@caso("TC-BP-018")
def test_TC_BP_018_tarjeta_vacia(flujo, evidencia, enlace_valido):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.continuar()
    evidencia.captura("Continuar con tarjeta vacía")

    assert _no_avanza(flujo), "El sistema avanzó con la tarjeta vacía"
    sin_mensaje = [c for c in CAMPOS if flujo.tarjeta.error(c) != MSG_REQUERIDO]
    assert not sin_mensaje, f"Campos sin 'Este campo es requerido': {sin_mensaje}"


@caso("TC-BP-019")
def test_TC_BP_019_tarjeta_incompleta(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar(numero=tarjeta_de_prueba("principal")["numero"])
    flujo.tarjeta.continuar()
    evidencia.captura("Solo número de tarjeta")

    assert _no_avanza(flujo), "El sistema avanzó con campos faltantes"
    sin_mensaje = [c for c in ("name", "lastName", "expiration", "cvv") if not flujo.tarjeta.error(c)]
    assert not sin_mensaje, f"Campos faltantes sin mensaje: {sin_mensaje}"


@caso("TC-BP-020")
def test_TC_BP_020_numero_invalido(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta_de_prueba("principal"), numero=NUMERO_TARJETA_INVALIDO)
    flujo.tarjeta.continuar()
    evidencia.captura(f"Tarjeta {NUMERO_TARJETA_INVALIDO}")

    assert flujo.tarjeta.error("card"), "No se mostró 'número de tarjeta inválido' antes de procesar"
    assert _no_avanza(flujo), "Se avanzó a confirmar el pago con un número de tarjeta inválido"


@caso("TC-BP-021")
def test_TC_BP_021_tarjeta_vencida(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta_de_prueba("principal"), vigencia=VIGENCIA_VENCIDA)
    flujo.tarjeta.continuar()
    evidencia.captura("Vigencia 01/20")

    assert _no_avanza(flujo), "Se permitió continuar con tarjeta vencida"
    assert flujo.tarjeta.error("expiration") == MSG_VIGENCIA_INVALIDA, f"Mensaje: '{flujo.tarjeta.error('expiration')}'"


@caso("TC-BP-022")
def test_TC_BP_022_cvv_incompleto(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta_de_prueba("principal"), cvv=CVV_INCOMPLETO)
    flujo.tarjeta.continuar()
    evidencia.captura(f"CVV: {CVV_INCOMPLETO}")

    assert _no_avanza(flujo), "Se permitió continuar con CVV incompleto"
    assert flujo.tarjeta.error("cvv") == MSG_CVV, f"Mensaje: '{flujo.tarjeta.error('cvv')}'"


@caso("TC-BP-023")
@pytest.mark.pago
def test_TC_BP_023_nip_incorrecto(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("nip_incorrecto")
    flujo.hasta_confirmacion(enlace_valido, tarjeta)
    flujo.confirmacion.confirmar_pago()

    assert flujo.resultado.salio_a_3ds(), "El banco no solicitó autenticación 3D Secure"
    evidencia.captura("Sitio del banco (3DS) - capturar un NIP incorrecto")
    resultado = flujo.resultado.esperar()
    evidencia.captura(f"Resultado: {flujo.resultado.titulo()}")

    assert resultado == "rechazada", "El pago no se rechazó con NIP incorrecto"
    assert MSG_TOAST_ERROR in flujo.resultado.toast_error(), "No apareció el aviso emergente de error"
    assert flujo.resultado.puede_reintentar(), "No se ofrece reintentar el pago"


@caso("TC-BP-024")
def test_TC_BP_024_numero_enmascarado(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("principal")
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta)
    mostrado = flujo.tarjeta.valores()["numero"]
    evidencia.captura(f"Número mostrado en el campo: '{mostrado}'")
    flujo.tarjeta.continuar()
    assert flujo.confirmacion.visible(), "No se avanzó al Paso 4"
    en_resumen = flujo.confirmacion.resumen().get("Tarjeta", "")
    evidencia.captura(f"Tarjeta en el resumen: '{en_resumen}'")

    problemas = []
    if sum(c.isdigit() for c in en_resumen) > 4 or not en_resumen.endswith(tarjeta["numero"][-4:]):
        problemas.append(f"el resumen muestra '{en_resumen}'")
    if sum(c.isdigit() for c in mostrado) > 4:
        problemas.append(f"el campo muestra el número completo mientras se escribe ('{mostrado}')")
    assert not problemas, "No se enmascara la tarjeta: " + "; ".join(problemas)


@caso("TC-BP-059")
def test_TC_BP_059_solo_un_apellido(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta_de_prueba("principal"), apellido=APELLIDO_COMPUESTO)
    flujo.tarjeta.continuar()
    mensaje = flujo.tarjeta.error("lastName")
    evidencia.captura(f"Apellido '{APELLIDO_COMPUESTO}' -> '{mensaje}'")

    assert _no_avanza(flujo), "Se aceptó un apellido compuesto (solo debe permitirse un apellido)"
    assert mensaje == MSG_NOMBRE, f"Mensaje en Apellido: '{mensaje}' (esperado '{MSG_NOMBRE}')"


@caso("TC-BP-060")
def test_TC_BP_060_nombre_con_numeros(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta_de_prueba("principal"), nombre=NOMBRE_CON_NUMEROS)
    valor = flujo.tarjeta.valores()["nombre"]
    flujo.tarjeta.continuar()
    evidencia.captura(f"Nombre '{NOMBRE_CON_NUMEROS}' -> quedó '{valor}'")

    assert not any(c.isdigit() for c in valor) or flujo.tarjeta.error("name"), \
        f"El nombre aceptó números sin mostrar error: '{valor}'"


@caso("TC-BP-061")
def test_TC_BP_061_tarjeta_corta(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar_con(tarjeta_de_prueba("principal"), numero=NUMERO_TARJETA_CORTO)
    flujo.tarjeta.continuar()
    evidencia.captura("Tarjeta de 12 dígitos")

    assert _no_avanza(flujo), "Se avanzó con una tarjeta de 12 dígitos"
    assert flujo.tarjeta.error("card") == MSG_TARJETA_LONGITUD, f"Mensaje: '{flujo.tarjeta.error('card')}'"


@caso("TC-BP-062")
def test_TC_BP_062_vencimiento_invalido(flujo, evidencia, enlace_valido, tarjeta_de_prueba):
    tarjeta = tarjeta_de_prueba("principal")
    flujo.hasta_tarjeta(enlace_valido)
    problemas = []
    for vigencia, esperado in ((VIGENCIA_MES_INVALIDO, MSG_VIGENCIA_INVALIDA), (VIGENCIA_INCOMPLETA, MSG_VIGENCIA_LONGITUD)):
        flujo.tarjeta.llenar_con(tarjeta, vigencia=vigencia)
        flujo.tarjeta.continuar()
        mensaje = flujo.tarjeta.error("expiration")
        evidencia.captura(f"Vencimiento '{vigencia}' -> '{mensaje}'")
        if flujo.confirmacion.visible(2):
            problemas.append(f"'{vigencia}' se aceptó")
            flujo.confirmacion.regresar()
        elif mensaje != esperado:
            problemas.append(f"'{vigencia}' mostró '{mensaje}' (esperado '{esperado}')")
    assert not problemas, "; ".join(problemas)


@caso("TC-BP-063")
def test_TC_BP_063_cvv_oculto(flujo, evidencia, enlace_valido):
    flujo.hasta_tarjeta(enlace_valido)
    flujo.tarjeta.llenar(cvv="1234")
    valor = flujo.tarjeta.valores()["cvv"]
    evidencia.captura("CVV con 4 dígitos escritos")

    assert flujo.tarjeta.tipo_cvv() == "password", "El CVV se muestra en texto plano"
    assert len(valor) == 3, f"El CVV conservó {len(valor)} dígitos"
