"""Lectura/escritura de los archivos de datos de prueba (cuentas, tarjetas y enlaces)."""
import json
import os

from config import settings


def _leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def _guardar(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


# ==============================================
# CUENTAS PREDIALES
# ==============================================
def listar_cuentas(estado=None):
    cuentas = _leer(settings.CUENTAS_JSON)["cuentas"]
    return [c for c in cuentas if estado is None or c["estado"] == estado]


def seleccionar_cuenta(alias=None):
    """Regresa la cuenta indicada por alias (o CUENTA_ALIAS), o la primera disponible."""
    alias = alias or os.getenv("CUENTA_ALIAS")
    cuentas = listar_cuentas()
    if alias:
        for c in cuentas:
            if c["alias"] == alias:
                return c
        raise LookupError(f"No existe la cuenta con alias '{alias}' en {settings.CUENTAS_JSON.name}")
    for c in cuentas:
        if c["estado"] == "disponible":
            return c
    raise LookupError(f"No hay cuentas 'disponible' en {settings.CUENTAS_JSON.name}")


def marcar_cuenta(alias, estado, notas=None):
    datos = _leer(settings.CUENTAS_JSON)
    for c in datos["cuentas"]:
        if c["alias"] == alias:
            c["estado"] = estado
            if notas:
                c["notas"] = notas
    _guardar(settings.CUENTAS_JSON, datos)


# ==============================================
# TARJETAS DE PRUEBA
# ==============================================
def tarjeta(nombre):
    t = _leer(settings.TARJETAS_JSON)["tarjetas"][nombre]
    if not t["numero"]:
        raise LookupError(f"Tarjeta de prueba '{nombre}' sin número en {settings.TARJETAS_JSON.name}")
    return t


# ==============================================
# ENLACES DE PAGO (ORIGEN_ENLACE=manual)
# ==============================================
def enlace_fijo(clave):
    return _leer(settings.ENLACES_JSON).get(clave) or None


def consumir_enlace_valido():
    datos = _leer(settings.ENLACES_JSON)
    if not datos["validos"]:
        return None
    url = datos["validos"].pop(0)
    datos["usados"].append(url)
    _guardar(settings.ENLACES_JSON, datos)
    return url
