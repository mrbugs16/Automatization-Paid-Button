# [MEMPHIS] Botón de Pago · Automatización QA

Pruebas E2E del Botón de Pago del Gobierno de Puebla con **Python + Appium (Google Chrome) + pytest**.
Cubre los 69 casos de `data/Matriz Pruebas Boton Pago.xlsx` y genera evidencia (capturas + reporte HTML con filtros) en cada ejecución.

---

## Alcance

| Fase | Qué es | En esta suite |
|---|---|---|
| 1 · Gobierno de Puebla | Portal `pabel` → Predial → consulta → genera el enlace | `tests/test_00_gobierno_predial.py` (solo precondición, no cuenta en los 69) |
| 2 · Memphis (nuestro desarrollo) | Enlace → 1 Contacto → 2 Dirección → 3 Tarjeta → 4 Confirmación → 3DS → resultado | `tests/test_00_happy_path.py` y `test_01` … `test_10` (TC-BP-001 a TC-BP-069) |
| 3 · Redirección al Gobierno | Solo se valida que ocurra | TC-BP-030 / TC-BP-031 |

---

## Estructura

```
config/
  settings.py        URLs, modo de driver, captcha, tiempos (todo sobrescribible por variables de entorno)
  locators.py        Localizadores reales (Gobierno y Memphis). Solo CSS/XPath
  datos_prueba.py    Datos de prueba y mensajes exactos que muestra la página
core/
  driver_factory.py  Appium → Chrome escritorio / Chrome Android / Selenium de respaldo
  captcha.py         Estrategia del captcha (manual / fijo / deshabilitado)
  enlace_pago.py     Obtiene el enlace de pago (manual / api / gobierno)
  evidencia.py       Capturas por caso
  matriz.py          Lee la matriz Excel y escribe una copia con resultados
  reporte_html.py    Reporte HTML con filtros
pages/
  gobierno_predial_page.py
  memphis_pages.py   Validación, Contacto, Dirección, Tarjeta, Confirmación, Resultado (+3DS) y FlujoPago
data/
  cuentas_predial.json   Lista de cuentas de QA (se rotan)
  tarjetas_prueba.json        Escenarios de tarjeta SIN números (se sube al repo)
  tarjetas_prueba.local.json  Números de tarjeta reales de QA (NO se sube; ignorado por Git)
  enlaces_prueba.json         Link de pago vigente y enlaces fijos (vencido, pagado)
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
python3 -m pytest -m "not lento" --abrir-reporte        # TODO de una (~20 min, sin esperas largas)
python3 -m pytest --abrir-reporte                       # TODO completo (+5 min por el 3DS de TC-BP-028)
python3 -m pytest -k TC_BP_050 --abrir-reporte          # happy path
python3 -m pytest -m "memphis and not pago"             # todas las validaciones, sin cobrar
python3 -m pytest -m memphis                            # Memphis completo (incluye pagos)
python3 -m pytest -m gobierno                           # portal del Gobierno
python3 -m pytest -k TC_BP_006                          # un caso
```

### Variables de entorno principales

| Variable | Valores | Default |
|---|---|---|
| `MODO_DRIVER` | `appium_desktop` · `appium_android` · `selenium` | `appium_desktop` |
| `MEMPHIS_DISPONIBLE` | `true` / `false` | `true` (con `false` todo Memphis sale *Pendiente*) |
| `ENLACE_PAGO` | link de pago a usar | `enlaces_prueba.json` → `vigente` |
| `TRESDS_MODO` | `manual` · `auto` | `manual` (espera a que captures el NIP/código del banco) |
| `ORIGEN_ENLACE` | `manual` · `api` · `gobierno` | `manual` |
| `CAPTCHA_MODO` | `manual` · `fijo` · `deshabilitado` | `manual` |
| `CAPTCHA_VALOR` | valor fijo si el Gobierno lo habilita en QA | — |
| `CUENTA_ALIAS` | alias de `cuentas_predial.json` | primera `disponible` |
| `TIMEOUT_TOKEN_SEG` | máximo que TC-BP-005/044 esperan a que expire el token | `120` (si no pasa nada, falla por tiempo excedido) |

---

## Link de pago y pruebas que cobran

- Todas las pruebas usan el link `vigente` de `data/enlaces_prueba.json`. Se puede reutilizar mientras el pago **no se apruebe**.
- Las pruebas marcadas `pago` confirman un pago real en el ambiente. Cuando uno se aprueba, el link pasa a `pagado` y las siguientes pruebas quedan *Pendiente* pidiendo un link nuevo: pega uno nuevo en `vigente`.
- Para validar formularios sin cobrar nada: `python3 -m pytest -m "memphis and not pago"`.

## Tarjetas

`data/tarjetas_prueba.json` define los escenarios (`principal`, `aprobada_sin_3ds`, `aprobada_con_3ds`, `declinada`, `nip_incorrecto`) **sin números**. Los números van en `data/tarjetas_prueba.local.json`, con la misma estructura, y ese archivo nunca se sube al repo. Si un escenario no tiene número, sus pruebas salen *Pendiente*.

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

Estados: **Aprobado** · **Fallido** (falló una validación; es un defecto a reportar) · **Error** (falló la preparación, ej. Appium apagado) · **Pendiente** (falta un dato de prueba, o el caso quedó *Bloqueado* porque requiere un pago aprobado) · **Manual** · **No ejecutado**.

---

## Pendientes

- [ ] Tarjetas sandbox en `data/tarjetas_prueba.local.json` (aprobada con y sin 3DS, declinada, NIP incorrecto)
- [ ] Algoritmo de `mp_signature` para `ORIGEN_ENLACE=api` (`core/enlace_pago.py::firmar`)
- [ ] Tiempo de vida del token y del 3DS (`TIMEOUT_TOKEN_SEG`, `TIMEOUT_3DS_SEG`)
- [ ] Botón del portal del Gobierno que redirige a Memphis (`GobiernoLoc.BTN_PAGAR_EN_LINEA`)
- [ ] Validación de "un solo cobro" en backend (TC-BP-004, 035, 037, 042, 043)
