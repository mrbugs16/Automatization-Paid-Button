# [MEMPHIS] Botón de Pago · Automatización QA

Pruebas E2E del Botón de Pago del Gobierno de Puebla con **Python + Appium (Google Chrome) + pytest**.
Cubre los 49 casos de `data/Matriz Pruebas Boton Pago.xlsx` y genera evidencia (capturas + reporte HTML con filtros) en cada ejecución.

---

## Alcance

| Fase | Qué es | En esta suite |
|---|---|---|
| 1 · Gobierno de Puebla | Portal `pabel` → Predial → consulta → genera el enlace | `tests/test_00_gobierno_predial.py` (solo precondición, no cuenta en los 49) |
| 2 · Memphis (nuestro desarrollo) | Enlace de pago → Contacto → Dirección → Tarjeta → 3DS → resultado | `tests/test_01` … `test_09` (TC-BP-001 a TC-BP-049) |
| 3 · Redirección al Gobierno | Solo se valida que ocurra | TC-BP-030 / TC-BP-031 |

---

## Estructura

```
config/
  settings.py        URLs, modo de driver, captcha, tiempos (todo sobrescribible por variables de entorno)
  locators.py        Localizadores. Gobierno = reales. Memphis = provisionales (# TODO)
  datos_prueba.py    Datos fijos de la matriz (teléfono, correo, CP, etc.)
core/
  driver_factory.py  Appium → Chrome escritorio / Chrome Android / Selenium de respaldo
  captcha.py         Estrategia del captcha (manual / fijo / deshabilitado)
  enlace_pago.py     Obtiene el enlace de pago (manual / api / gobierno)
  evidencia.py       Capturas por caso
  matriz.py          Lee la matriz Excel y escribe una copia con resultados
  reporte_html.py    Reporte HTML con filtros
pages/
  gobierno_predial_page.py
  memphis_pages.py   Validación, Contacto, Dirección, Tarjeta, Procesamiento/3DS, Resultado + FlujoPago
data/
  cuentas_predial.json   Lista de cuentas de QA (se rotan)
  tarjetas_prueba.json   Tarjetas sandbox por escenario
  enlaces_prueba.json    Enlaces de pago (modo manual)
tests/               Un archivo por módulo de la matriz
evidencias/<fecha_hora>/  reporte.html · resultados.json · matriz_resultados.xlsx · capturas/<TC-ID>/*.png
```

---

## Instalación (una sola vez)

```bash
pip3 install -r requirements.txt
appium driver install chromium
```

## Ejecución

1. Levantar Appium en otra terminal: `appium --relaxed-security`
2. Correr las pruebas:

```bash
pytest                                   # toda la suite
pytest -m gobierno                       # solo el portal del Gobierno (lo único ejecutable hoy)
pytest -k TC_BP_006                      # un caso
pytest --cuenta=urbano_02 -m gobierno    # usar una cuenta específica de la lista
pytest --abrir-reporte                   # abrir el HTML al terminar
MEMPHIS_DISPONIBLE=true pytest -m memphis  # cuando el botón de pago esté publicado
```

### Variables de entorno principales

| Variable | Valores | Default |
|---|---|---|
| `MODO_DRIVER` | `appium_desktop` · `appium_android` · `selenium` | `appium_desktop` |
| `MEMPHIS_DISPONIBLE` | `true` / `false` | `false` (los 49 casos salen como *Pendiente*) |
| `ORIGEN_ENLACE` | `manual` · `api` · `gobierno` | `manual` |
| `CAPTCHA_MODO` | `manual` · `fijo` · `deshabilitado` | `manual` |
| `CAPTCHA_VALOR` | valor fijo si el Gobierno lo habilita en QA | — |
| `CUENTA_ALIAS` | alias de `cuentas_predial.json` | primera `disponible` |
| `TOKEN_TTL_SEG` | vida del token (TC-BP-005 / 044) | `900` (confirmar con desarrollo) |

---

## Cuentas prediales

`data/cuentas_predial.json` guarda la lista de cuentas de QA. Cada una tiene `alias`, `tipo` (PU/PR), `cuenta`, `delegacion`, `linea_captura` y `estado` (`disponible` · `usada` · `invalida`).
Las pruebas toman la primera `disponible` o la indicada con `--cuenta`. Si `linea_captura` viene llena se consulta por línea de captura; si no, por tipo + cuenta + delegación.

## Captcha

El captcha del portal cambia en cada carga y es un control de seguridad del Gobierno, así que la suite **no** intenta leerlo con OCR:

- **manual** (default): el script resalta el campo, toma captura y espera (hasta `CAPTCHA_TIMEOUT` s) a que escribas los 5 caracteres en Chrome; después da clic en *Consultar* solo. No presiones Enter.
- **fijo** / **deshabilitado**: para cuando el equipo del Gobierno habilite un captcha fijo o lo desactive en el ambiente de QA.

Como la Fase 1 está fuera de alcance, lo ideal es obtener los enlaces con `ORIGEN_ENLACE=api` (POST a `transmission-sequence`), que no pasa por el captcha. Para eso falta que desarrollo comparta cómo se calcula `mp_signature`.

## Reporte

`evidencias/<fecha_hora>/reporte.html` incluye un resumen (aprobados / fallidos / pendientes / manuales), filtros por estado, módulo, tipo y prioridad, búsqueda, y las capturas de cada paso (clic para ampliar).
`matriz_resultados.xlsx` es una copia de la matriz con *Resultado Obtenido* y *Estado* llenos.

Estados: **Aprobado** · **Fallido** (falló una validación) · **Error** (falló la preparación, ej. Appium apagado) · **Pendiente** (falta la página o un dato de prueba) · **Manual** · **No ejecutado**.

---

## Pendientes para cuando llegue la página de Memphis

- [ ] Reemplazar los locators `# TODO` de `config/locators.py` (pedir `data-testid` a desarrollo)
- [ ] Tarjetas sandbox en `data/tarjetas_prueba.json` (aprobada con y sin 3DS, declinada, NIP incorrecto)
- [ ] Algoritmo de `mp_signature` para `ORIGEN_ENLACE=api` (`core/enlace_pago.py::firmar`)
- [ ] Tiempo de vida del token y del 3DS (`TOKEN_TTL_SEG`, `TIMEOUT_3DS_SEG`)
- [ ] Botón del portal del Gobierno que redirige a Memphis (`GobiernoLoc.BTN_PAGAR_EN_LINEA`)
- [ ] Validación de "un solo cobro" en backend (TC-BP-004, 035, 037, 042, 043)
