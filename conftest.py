"""
Fixtures y hooks de pytest:
- driver / evidencia / flujo / enlace_valido / cuenta_predial
- Registro de resultados por caso y generación del reporte HTML + matriz con resultados.
"""
import json
import time
import webbrowser
from datetime import datetime

import pytest

from config import settings
from core import datos
from core.driver_factory import crear_driver
from core.enlace_pago import obtener_enlace_valido
from core.evidencia import Evidencia
from core.marcadores import PREFIJO_MANUAL, PREFIJO_PENDIENTE, pendiente
from core.matriz import cargar_matriz, escribir_resultados
from core.reporte_html import generar_reporte
from pages.memphis_pages import FlujoPago

EJECUCION = datetime.now().strftime("%Y%m%d_%H%M%S")
DIR_EJECUCION = settings.DIR_EVIDENCIAS / EJECUCION
RESULTADOS = {}
INICIO = datetime.now()


def pytest_addoption(parser):
    parser.addoption("--cuenta", default=None, help="Alias de la cuenta en data/cuentas_predial.json")
    parser.addoption("--abrir-reporte", action="store_true", help="Abre el reporte HTML al terminar")


def _caso_id(item):
    marca = item.get_closest_marker("caso")
    return marca.args[0] if marca else item.name


# ==============================================
# FIXTURES
# ==============================================
@pytest.fixture
def evidencia(request):
    ev = Evidencia(_caso_id(request.node), DIR_EJECUCION)
    request.node.evidencia = ev
    return ev


@pytest.fixture
def driver(evidencia):
    drv = crear_driver()
    evidencia.driver = drv
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture
def flujo(driver):
    return FlujoPago(driver)


@pytest.fixture
def cuenta_predial(request):
    try:
        return datos.seleccionar_cuenta(request.config.getoption("--cuenta"))
    except LookupError as e:
        pendiente(str(e))


@pytest.fixture
def tarjeta_de_prueba():
    """Uso: tarjeta_de_prueba("aprobada_sin_3ds"). Marca Pendiente si falta la tarjeta en data/tarjetas_prueba.json."""
    def _obtener(nombre):
        try:
            return datos.tarjeta(nombre)
        except LookupError as e:
            pendiente(str(e))
    return _obtener


@pytest.fixture
def enlace_valido(request, driver, evidencia):
    cuenta = None
    if settings.ORIGEN_ENLACE == "gobierno":
        cuenta = request.getfixturevalue("cuenta_predial")
    url = obtener_enlace_valido(driver, cuenta, evidencia)
    if not url:
        pendiente(f"Sin enlace de pago válido (ORIGEN_ENLACE={settings.ORIGEN_ENLACE}); agrega uno en data/enlaces_prueba.json")
    return url


# ==============================================
# REGISTRO DE RESULTADOS
# ==============================================
def _clasificar(reporte):
    if reporte.passed:
        return "Aprobado", "Resultado conforme a lo esperado"
    if reporte.skipped:
        motivo = reporte.longrepr[2] if isinstance(reporte.longrepr, tuple) else str(reporte.longrepr)
        motivo = motivo.replace("Skipped: ", "")
        if motivo.startswith(PREFIJO_MANUAL):
            return "Manual", motivo[len(PREFIJO_MANUAL):].strip()
        if motivo.startswith(PREFIJO_PENDIENTE):
            return "Pendiente", motivo[len(PREFIJO_PENDIENTE):].strip()
        return "Pendiente", motivo
    if reporte.when == "call":
        return "Fallido", ""
    return "Error", ""


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    salida = yield
    reporte = salida.get_result()
    caso_id = _caso_id(item)

    # Solo nos interesa el resultado de la ejecución, o el setup si falló/se omitió
    if reporte.when == "setup" and reporte.passed:
        item._inicio = time.time()
        return
    if reporte.when == "teardown" and (reporte.passed or caso_id in RESULTADOS):
        return

    estado, obtenido = _clasificar(reporte)
    ev = getattr(item, "evidencia", None)
    error = ""
    if estado in ("Fallido", "Error"):
        error = reporte.longreprtext[-4000:]
        mensaje = str(call.excinfo.value) if call.excinfo else ""
        obtenido = mensaje.splitlines()[0] if mensaje else "Error durante la ejecución"
        if ev:
            ev.captura(f"FALLO - {obtenido[:80]}", estado="fallo")
    elif estado == "Aprobado" and ev:
        ev.captura("Resultado final", estado="ok")

    marca = item.get_closest_marker("caso")
    RESULTADOS[caso_id] = {
        "estado": estado,
        "obtenido": obtenido,
        "error": error,
        "duracion": round(time.time() - getattr(item, "_inicio", time.time()), 1),
        "pasos_evidencia": ev.pasos if ev else [],
        "meta": dict(marca.kwargs) if marca else {"caso": item.name},
    }


def pytest_sessionfinish(session, exitstatus):
    if not RESULTADOS:
        return
    DIR_EJECUCION.mkdir(parents=True, exist_ok=True)
    matriz = cargar_matriz()

    casos = []
    # 1) Casos fuera de la matriz (ej. precondición en portal del Gobierno)
    for caso_id, r in RESULTADOS.items():
        if caso_id not in matriz:
            casos.append({"id": caso_id, **r["meta"], **{k: v for k, v in r.items() if k != "meta"}})
    # 2) Los 49 casos de la matriz, en su orden, ejecutados o no
    for caso_id, fila in matriz.items():
        r = RESULTADOS.get(caso_id, {"estado": "No ejecutado", "obtenido": "", "error": "", "duracion": 0, "pasos_evidencia": []})
        casos.append({**fila, **{k: v for k, v in r.items() if k != "meta"}})

    datos_reporte = {
        "ejecucion": EJECUCION,
        "inicio": INICIO.strftime("%d/%m/%Y %H:%M:%S"),
        "fin": datetime.now().strftime("%H:%M:%S"),
        "driver": settings.MODO_DRIVER,
        "memphis": settings.MEMPHIS_DISPONIBLE,
        "casos": casos,
    }
    (DIR_EJECUCION / "resultados.json").write_text(json.dumps(datos_reporte, ensure_ascii=False, indent=2), encoding="utf-8")
    reporte = DIR_EJECUCION / "reporte.html"
    generar_reporte(datos_reporte, reporte)
    escribir_resultados(
        {c["id"]: c for c in casos if c["estado"] != "No ejecutado"},
        DIR_EJECUCION / "matriz_resultados.xlsx",
    )

    print(f"\n📊 Reporte: {reporte}")
    if session.config.getoption("--abrir-reporte"):
        webbrowser.open(reporte.as_uri())
