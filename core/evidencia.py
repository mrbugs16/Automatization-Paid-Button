"""
Evidencia por caso de prueba.

Estructura generada en cada ejecución:
    evidencias/<AAAAMMDD_HHMMSS>/
        reporte.html
        resultados.json
        matriz_resultados.xlsx
        capturas/<TC-ID>/01_descripcion.png, 02_..., 99_FALLO.png
"""
import re
import unicodedata
from datetime import datetime


def _slug(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "_", texto).strip("_")[:60] or "captura"


class Evidencia:
    def __init__(self, caso_id, dir_ejecucion):
        self.caso_id = caso_id
        self.dir_ejecucion = dir_ejecucion
        self.dir_caso = dir_ejecucion / "capturas" / caso_id
        self.pasos = []
        self.driver = None

    def captura(self, descripcion, estado="info", driver=None):
        """Toma screenshot y lo registra como paso. estado: info | ok | fallo."""
        driver = driver or self.driver
        numero = len(self.pasos) + 1
        archivo = None
        if driver is not None:
            self.dir_caso.mkdir(parents=True, exist_ok=True)
            ruta = self.dir_caso / f"{numero:02d}_{_slug(descripcion)}.png"
            try:
                driver.save_screenshot(str(ruta))
                archivo = ruta.relative_to(self.dir_ejecucion).as_posix()
            except Exception as e:  # el navegador pudo haberse cerrado
                descripcion = f"{descripcion} (sin captura: {e.__class__.__name__})"
        self.pasos.append({
            "numero": numero,
            "descripcion": descripcion,
            "estado": estado,
            "archivo": archivo,
            "hora": datetime.now().strftime("%H:%M:%S"),
        })
        print(f"   📸 [{self.caso_id}] {numero:02d} {descripcion}")
        return archivo

    def nota(self, descripcion, estado="info"):
        """Registra un paso sin captura (ej. validaciones pendientes en backend)."""
        self.pasos.append({
            "numero": len(self.pasos) + 1,
            "descripcion": descripcion,
            "estado": estado,
            "archivo": None,
            "hora": datetime.now().strftime("%H:%M:%S"),
        })
        print(f"   📝 [{self.caso_id}] {descripcion}")
