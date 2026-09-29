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
    """Combina tarjetas_prueba.json con tarjetas_prueba.local.json (el local tiene los números)."""
    tarjetas = _leer(settings.TARJETAS_JSON)["tarjetas"]
    if settings.TARJETAS_LOCAL_JSON.exists():
        for clave, datos_local in _leer(settings.TARJETAS_LOCAL_JSON)["tarjetas"].items():
            tarjetas[clave] = {**tarjetas.get(clave, {}), **datos_local}
    t = tarjetas.get(nombre)
    if not t or not t.get("numero"):
        raise LookupError(f"Tarjeta de prueba '{nombre}' sin número en {settings.TARJETAS_LOCAL_JSON.name}")
    return t


# ==============================================
# ENLACES DE PAGO (ORIGEN_ENLACE=manual)
# ==============================================
def enlace_fijo(clave):
    return _leer(settings.ENLACES_JSON).get(clave) or None


def enlace_vigente():
    """Primer link sin pagar de la lista (o ENLACE_PAGO si se pasó por variable)."""
    return settings.ENLACE_PAGO or next(iter(_leer(settings.ENLACES_JSON).get("vigentes", [])), None)


def enlace_pagado():
    return next(reversed(_leer(settings.ENLACES_JSON).get("pagados", [])), None)


def marcar_enlace_pagado(url):
    """Tras un pago aprobado el link ya no sirve: pasa de 'vigentes' a 'pagados' y se usa el siguiente."""
    datos = _leer(settings.ENLACES_JSON)
    if url in datos.get("vigentes", []):
        datos["vigentes"].remove(url)
        datos.setdefault("pagados", []).append(url)
        _guardar(settings.ENLACES_JSON, datos)
        restantes = len(datos["vigentes"])
        print(f"   🔗 Link pagado; quedan {restantes} link(s) vigente(s) en {settings.ENLACES_JSON.name}")


def tarjetas_3ds(tipo=None):
    """Catálogo de tarjetas de prueba 3DS (opcionalmente filtrado: 'Not challenge', 'Challenge', 'Attempt', 'Not authenticated')."""
    catalogo = _leer(settings.TARJETAS_JSON).get("catalogo_3ds", [])
    return [t for t in catalogo if tipo is None or t["tipo_3ds"] == tipo]
