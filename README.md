# [MEMPHIS] Botón de Pago · Automatización QA

Pruebas E2E del Botón de Pago del Gobierno de Puebla con **Python + Appium (Google Chrome) + pytest**.
Cubre los 71 casos activos de `data/Matriz Pruebas Boton Pago.xlsx` y genera evidencia (capturas + reporte HTML con filtros) en cada ejecución.

---

## Alcance

| Fase | Qué es | En esta suite |
|---|---|---|
| 1 · Gobierno de Puebla | Portal `pabel` → Predial o Infracciones (Tránsito) → consulta → genera el enlace | `tests/test_00_gobierno_predial.py` (TC-GOB-001 Predial, TC-GOB-002 Infracciones; solo precondición, no cuenta en los 69) |
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
  gobierno_predial_page.py      Portal del Gobierno: Predial (precondición)
  gobierno_infracciones_page.py Portal del Gobierno: Infracciones / Tránsito (precondición)
  gobierno_comprobante_page.py  Portal del Gobierno: COMPROBANTE DE PAGO (fin del flujo)
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
python3 -m pytest --abrir-reporte                       # TODO de una
python3 -m pytest -k TC_BP_050 --abrir-reporte          # happy path
python3 -m pytest -m "memphis and not pago"             # todas las validaciones, sin cobrar
python3 -m pytest -m memphis                            # Memphis completo (incluye pagos)
python3 -m pytest -m gobierno                           # portal del Gobierno
python3 -m pytest -k TC_BP_006                          # un caso
python3 -m pytest --servicio transito --abrir-reporte    # links de Tránsito (Infracciones)
python3 -m pytest --servicio predial                     # links de Predial (default)
```

### Variables de entorno principales

| Variable | Valores | Default |
|---|---|---|
| `MODO_DRIVER` | `appium_desktop` · `appium_android` · `selenium` | `appium_desktop` |
| `MEMPHIS_DISPONIBLE` | `true` / `false` | `true` (con `false` todo Memphis sale *Pendiente*) |
| `SERVICIO` | `predial` · `transito` (igual que `--servicio`) | `predial` |
| `ENLACE_PAGO` | link de pago a usar | `enlaces_prueba.json` → `vigente` |
| `TRESDS_MODO` | `manual` · `auto` | `manual` (espera a que captures el NIP/código del banco) |
| `ORIGEN_ENLACE` | `manual` · `api` · `gobierno` | `manual` |
| `CAPTCHA_MODO` | `manual` · `fijo` · `deshabilitado` | `manual` |
| `CAPTCHA_VALOR` | valor fijo si el Gobierno lo habilita en QA | — |
| `CUENTA_ALIAS` | alias de `cuentas_predial.json` | primera `disponible` |
| `PLAN_MSI` | vacío · `6` (todos los pagos eligen *6 meses* si la tarjeta participa) | vacío (una sola exhibición) |
| `TIMEOUT_TOKEN_SEG` | máximo que TC-BP-005/044 esperan a que expire el token | `120` (si no pasa nada, falla por tiempo excedido) |

---

## Link de pago y pruebas que cobran

- Cada trámite tiene su lista en `data/enlaces_prueba.json`: `vigentes` (Predial) y `vigentes_transito` (Tránsito / Infracciones). Se usa la del trámite elegido con `--servicio`.
- Todas las pruebas usan el primer link de su lista. Se puede reutilizar mientras el pago **no se apruebe**.
- Las pruebas marcadas `pago` confirman un pago y **se corren al final**, después de todas las validaciones. Cada pago aprobado mueve su link a `pagados` y las pruebas siguen con el siguiente de la lista.
- Pon en `vigentes` un link por cada prueba que aprueba un pago (alrededor de 18). Si se acaban, esas pruebas quedan *Pendiente*.
- **Si no hay un link válido**, la suite abre el portal → **Predial** (tipo + cuenta + delegación, o línea de captura) o → **Infracciones** (folio de infracción, o línea de captura) según `--servicio`, y espera **3 minutos** (`TIMEOUT_CAPTURA_REFERENCIA`) a que captures en Chrome la referencia/folio y el captcha y des *Consultar*. En la pantalla del adeudo intenta dar clic en el botón de pago (si no lo encuentra, dalo tú). El link de Memphis que se obtiene se guarda en `vigentes` y se reutiliza. Si no tienes referencias a la mano, escribe **`s`** y Enter en la terminal para **saltar**: no se vuelve a pedir en esa corrida y las pruebas sin link quedan *Pendiente*. Para desactivar la pausa desde el inicio: `PEDIR_REFERENCIA=false`.
- Para validar formularios sin cobrar nada: `python3 -m pytest -m "memphis and not pago"`.

## Tarjetas (3D Secure)

`data/tarjetas_prueba.json` tiene el catálogo de tarjetas de prueba 3DS (`catalogo_3ds`) y el escenario que usa cada prueba (`tarjetas`). Vencimiento: cualquier fecha futura; CVV: cualquier 3 dígitos.

| Tipo 3DS | VISA | MasterCard | Comportamiento | Escenario |
|---|---|---|---|---|
| Not challenge (**sin 3DS**) | 4111 1111 1111 1111 | 5180 3000 0000 0005 | Se aprueba sin pedir código | `principal`, `aprobada_sin_3ds`, `sin_3ds_mc` |
| Challenge (**con 3DS**) | 4110 7600 0000 0008 / 0032 | 5292 5943 8206 0745 / 5180 3000 0000 0047 | El banco pide un código: captúralo en Chrome | `aprobada_con_3ds`, `nip_incorrecto`, `challenge_mc` |
| Attempt | 4110 7600 0000 0040 | 5180 3000 0000 0054 | Se aprueba sin reto | `attempt` |
| Not authenticated | 4110 7600 0000 0065 | 5180 3000 0000 0039 | Se rechaza ("Rechazada por 3DS") | `declinada` |

Tarjetas reales de QA van en `data/tarjetas_prueba.local.json` (ignorado por Git); si un escenario existe en ambos archivos, gana el local. La matriz tiene la misma tabla en la hoja **Tarjetas 3DS**.

## Meses sin intereses (Paso 4)

En el Paso 4 la página muestra *"Tu tarjeta participa en promociones de meses sin intereses. Seleccionar un plan es opcional:"* con **una sola opción: 6 meses** (la tarjeta VISA •••• 1111 participa).

- `tests/test_12_meses_sin_intereses.py`: **TC-MSI-001** valida la leyenda, que solo exista *6 meses*, que no venga marcada y que se pueda seleccionar (no cobra). **TC-MSI-002** paga eligiendo 6 meses (cobra; escenario `msi_6_meses`).
- Un escenario de `tarjetas_prueba.json` con `"msi": 6` elige el plan solo; con `PLAN_MSI=6` lo eligen todos los pagos. Si la tarjeta no participa, el flujo sigue sin plan.

## Cuentas prediales

`data/cuentas_predial.json` guarda la lista de cuentas de QA. Cada una tiene `alias`, `tipo` (PU/PR), `cuenta`, `delegacion`, `linea_captura` y `estado` (`disponible` · `usada` · `invalida`).
Las pruebas toman la primera `disponible` o la indicada con `--cuenta`. Si `linea_captura` viene llena se consulta por línea de captura; si no, por tipo + cuenta + delegación.

## Captcha

El captcha del portal cambia en cada carga y es un control de seguridad del Gobierno, así que la suite **no** intenta leerlo con OCR:

- **manual** (default): el script resalta el campo, toma captura y espera (hasta `CAPTCHA_TIMEOUT` s) a que escribas los 5 caracteres en Chrome; después da clic en *Consultar* solo. No presiones Enter.
- **fijo** / **deshabilitado**: para cuando el equipo del Gobierno habilite un captcha fijo o lo desactive en el ambiente de QA.

Como la Fase 1 está fuera de alcance, lo ideal es obtener los enlaces con `ORIGEN_ENLACE=api` (POST a `transmission-sequence`), que no pasa por el captcha. Para eso falta que desarrollo comparta cómo se calcula `mp_signature`.

## Casos eliminados

En la revisión del 30/09/2026 se quitaron 30 casos de la matriz (y sus pruebas). Sus filas quedan con solo el ID, sin renumerar, y no se cuentan en la Portada ni en el Dashboard.

## Reporte

`evidencias/<fecha_hora>/reporte.html` incluye un resumen (aprobados / fallidos / pendientes / manuales), filtros por estado, **trámite (Tránsito / Predial)**, **3DS (con / sin)**, **marca (VISA / MasterCard)**, módulo, tipo y prioridad, búsqueda, y las capturas de cada paso (clic para ampliar).
Cada caso muestra etiquetas con su trámite, si la tarjeta usada es con o sin 3DS (al pasar el cursor, el tipo: Challenge, Not challenge…) y la marca. Los casos que no usan tarjeta no llevan etiqueta de 3DS ni marca.
`matriz_resultados.xlsx` es una copia de la matriz con *Resultado Obtenido* y *Estado* llenos.

Estados: **Aprobado** · **Fallido** (falló una validación; es un defecto a reportar) · **Error** (falló la preparación, ej. Appium apagado) · **Pendiente** (falta un dato de prueba, o el caso quedó *Bloqueado* porque requiere un pago aprobado) · **Manual** · **No ejecutado**.

---

## Pendientes

- [ ] Tarjetas sandbox en `data/tarjetas_prueba.local.json` (aprobada con y sin 3DS, declinada, NIP incorrecto)
- [ ] Algoritmo de `mp_signature` para `ORIGEN_ENLACE=api` (`core/enlace_pago.py::firmar`)
- [ ] Tiempo de vida del token y del 3DS (`TIMEOUT_TOKEN_SEG`, `TIMEOUT_3DS_SEG`)
- [ ] Botón del portal del Gobierno que redirige a Memphis (`GobiernoLoc.BTN_PAGAR_EN_LINEA`)
- [ ] Validación de "un solo cobro" en backend (TC-BP-004, 035, 037, 042, 043)
