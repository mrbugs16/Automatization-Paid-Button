"""Genera evidencias/<ejecucion>/reporte.html: resumen, filtros y capturas por caso."""
import json

PLANTILLA = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reporte Botón de Pago</title>
<style>
:root{
  --bg:#f6f7f9;--panel:#fff;--text:#1d2330;--muted:#5f6b7a;--line:#e3e6eb;--accent:#7a1f45;
  --ok:#1e7b46;--ok-bg:#e3f4ea;--bad:#b3261e;--bad-bg:#fbe5e3;--pend:#8a6100;--pend-bg:#fff3d1;
  --man:#1f5f9e;--man-bg:#e2eefa;--none:#5f6b7a;--none-bg:#eceef1;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#12151b;--panel:#1b1f27;--text:#e6e9ef;--muted:#9aa4b2;--line:#2c323d;--accent:#e07aa5;
  --ok:#6fd49a;--ok-bg:#16301f;--bad:#ff8a80;--bad-bg:#3a1a18;--pend:#f2c14e;--pend-bg:#3a2f12;
  --man:#8cbcf0;--man-bg:#172a3f;--none:#9aa4b2;--none-bg:#262b34;
}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 -apple-system,Segoe UI,Roboto,sans-serif}
header{background:var(--accent);color:#fff;padding:20px 24px}
header h1{margin:0;font-size:20px}
header p{margin:4px 0 0;opacity:.85;font-size:13px}
main{max-width:1200px;margin:0 auto;padding:20px 16px 60px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin-bottom:14px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.kpi b{display:block;font-size:24px}
.kpi span{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.barra{display:flex;height:10px;border-radius:5px;overflow:hidden;background:var(--none-bg);margin-bottom:18px}
.barra div{height:100%}
.filtros{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:14px;position:sticky;top:0;z-index:5}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);background:transparent;color:var(--text);border-radius:999px;padding:5px 12px;cursor:pointer;font-size:13px}
.chip[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:#fff}
select,input[type=search]{background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:8px;padding:6px 8px;font-size:13px;max-width:100%}
input[type=search]{flex:1;min-width:180px}
.contador{color:var(--muted);font-size:13px;margin:0 0 8px}
.caso{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--none);border-radius:10px;margin-bottom:10px}
.caso[data-estado=Aprobado]{border-left-color:var(--ok)}
.caso[data-estado=Fallido],.caso[data-estado=Error]{border-left-color:var(--bad)}
.caso[data-estado=Pendiente]{border-left-color:var(--pend)}
.caso[data-estado=Manual]{border-left-color:var(--man)}
.caso summary{list-style:none;cursor:pointer;padding:12px 14px;display:grid;grid-template-columns:110px 1fr auto;gap:10px;align-items:center}
.caso summary::-webkit-details-marker{display:none}
.id{font-family:ui-monospace,Menlo,monospace;font-weight:600;font-size:13px}
.titulo small{display:block;color:var(--muted);font-size:12px}
.tags{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.tag{font-size:11px;padding:2px 8px;border-radius:999px;background:var(--none-bg);color:var(--none);white-space:nowrap}
.estado-Aprobado{background:var(--ok-bg);color:var(--ok)}
.estado-Fallido,.estado-Error{background:var(--bad-bg);color:var(--bad)}
.estado-Pendiente{background:var(--pend-bg);color:var(--pend)}
.estado-Manual{background:var(--man-bg);color:var(--man)}
.tag.servicio{background:var(--accent);color:#fff}
.tag.tds-con{background:var(--man-bg);color:var(--man)}
.tag.tds-sin{background:var(--pend-bg);color:var(--pend)}
.tag.marca{border:1px solid var(--line);background:transparent;color:var(--text)}
.detalle{padding:0 14px 14px;border-top:1px solid var(--line)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:12px}
.detalle h4{margin:12px 0 4px;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.detalle p,.detalle pre{margin:0;white-space:pre-wrap;word-break:break-word}
.detalle pre{font:12px/1.4 ui-monospace,Menlo,monospace;background:var(--bg);padding:8px;border-radius:6px;max-height:220px;overflow:auto}
.pasos{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin-top:6px}
.paso{border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--bg)}
.paso img{width:100%;height:110px;object-fit:cover;object-position:top;display:block;cursor:zoom-in}
.paso div{padding:6px 8px;font-size:12px}
.paso.fallo{border-color:var(--bad)}
.paso.ok{border-color:var(--ok)}
.vacio{color:var(--muted);font-style:italic}
#visor{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;z-index:20;padding:20px;flex-direction:column;gap:8px}
#visor img{max-width:100%;max-height:88vh;border-radius:6px}
#visor p{color:#fff;margin:0;font-size:13px}
@media (max-width:700px){
  .caso summary{grid-template-columns:1fr}.tags{justify-content:flex-start}.grid2{grid-template-columns:1fr}
}
</style>
</head>
<body>
<header>
  <h1>Reporte de automatización · Botón de Pago</h1>
  <p id="meta"></p>
</header>
<main>
  <section class="kpis" id="kpis"></section>
  <div class="barra" id="barra"></div>
  <section class="filtros">
    <div class="chips" id="chips"></div>
    <select id="fServicio" aria-label="Trámite"><option value="">Tránsito y Predial</option></select>
    <select id="fSeguridad" aria-label="3D Secure"><option value="">Con y sin 3DS</option></select>
    <select id="fMarca" aria-label="Marca de tarjeta"><option value="">VISA y MasterCard</option></select>
    <select id="fModulo"><option value="">Todos los módulos</option></select>
    <select id="fTipo"><option value="">Todos los tipos</option></select>
    <select id="fPrioridad"><option value="">Todas las prioridades</option></select>
    <input type="search" id="fTexto" placeholder="Buscar por ID, caso o mensaje…">
  </section>
  <p class="contador" id="contador"></p>
  <section id="lista"></section>
</main>
<div id="visor" role="dialog"><img alt=""><p></p></div>
<script id="datos" type="application/json">__DATOS__</script>
<script>
const D = JSON.parse(document.getElementById('datos').textContent);
const ESTADOS = ['Aprobado','Fallido','Error','Pendiente','Manual','No ejecutado'];
const COLOR = {Aprobado:'var(--ok)',Fallido:'var(--bad)',Error:'var(--bad)',Pendiente:'var(--pend)',Manual:'var(--man)','No ejecutado':'var(--none)'};
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let filtroEstado = '';

document.getElementById('meta').textContent =
  `Ejecución ${D.ejecucion} · ${D.inicio} → ${D.fin} · Trámite: ${D.servicio || '—'} · Driver: ${D.driver} · Memphis disponible: ${D.memphis ? 'sí' : 'no'}`
  + (D.nota ? ` · ${D.nota}` : '');

const cuenta = e => D.casos.filter(c => c.estado === e).length;
const total = D.casos.length, ejecutados = cuenta('Aprobado') + cuenta('Fallido') + cuenta('Error');
const pct = ejecutados ? Math.round(cuenta('Aprobado') * 100 / ejecutados) : 0;
document.getElementById('kpis').innerHTML =
  [['Total', total], ['Aprobados', cuenta('Aprobado')], ['Fallidos', cuenta('Fallido') + cuenta('Error')],
   ['Pendientes', cuenta('Pendiente')], ['Manuales', cuenta('Manual')], ['% éxito ejecutados', pct + '%']]
  .map(([t, v]) => `<div class="kpi"><b>${v}</b><span>${t}</span></div>`).join('');
document.getElementById('barra').innerHTML = ESTADOS.map(e => {
  const n = cuenta(e); return n ? `<div title="${e}: ${n}" style="width:${n*100/total}%;background:${COLOR[e]}"></div>` : '';
}).join('');

const chips = document.getElementById('chips');
['', ...ESTADOS].forEach(e => {
  const n = e ? cuenta(e) : total;
  if (e && !n) return;
  const b = document.createElement('button');
  b.className = 'chip'; b.textContent = `${e || 'Todos'} (${n})`;
  b.setAttribute('aria-pressed', e === filtroEstado);
  b.onclick = () => { filtroEstado = e; chips.querySelectorAll('.chip').forEach(x => x.setAttribute('aria-pressed', x === b)); pintar(); };
  chips.appendChild(b);
});
const llenar = (id, campo) => [...new Set(D.casos.map(c => c[campo]).filter(Boolean))].sort()
  .forEach(v => document.getElementById(id).insertAdjacentHTML('beforeend', `<option>${esc(v)}</option>`));
llenar('fModulo', 'modulo'); llenar('fTipo', 'tipo'); llenar('fPrioridad', 'prioridad');
// Trámite, 3DS y marca: siempre se ofrecen ambas opciones; una prueba con varias tarjetas guarda "VISA / MasterCard"
const opciones = (id, valores) => valores.forEach(v => document.getElementById(id).insertAdjacentHTML('beforeend', `<option>${esc(v)}</option>`));
opciones('fServicio', ['Tránsito', 'Predial']); opciones('fSeguridad', ['Con 3DS', 'Sin 3DS']); opciones('fMarca', ['VISA', 'MasterCard']);
const incluye = (valor, buscado) => !buscado || String(valor || '').split(' / ').includes(buscado);
['fServicio','fSeguridad','fMarca','fModulo','fTipo','fPrioridad','fTexto'].forEach(id => document.getElementById(id).addEventListener('input', pintar));

function tarjeta(c) {
  const pasos = (c.pasos_evidencia || []).map(p => `
    <div class="paso ${p.estado}">
      ${p.archivo ? `<img loading="lazy" src="${esc(p.archivo)}" alt="${esc(p.descripcion)}" data-desc="${esc(c.id + ' · ' + p.descripcion)}">` : ''}
      <div>${p.numero}. ${esc(p.descripcion)}<br><small>${esc(p.hora)}</small></div>
    </div>`).join('');
  return `<details class="caso" data-estado="${esc(c.estado)}">
    <summary>
      <span class="id">${esc(c.id)}</span>
      <span class="titulo">${esc(c.caso)}<small>${esc(c.modulo)}</small></span>
      <span class="tags">
        ${c.servicio ? `<span class="tag servicio">${esc(c.servicio)}</span>` : ''}
        ${c.seguridad ? `<span class="tag ${c.seguridad.includes('Con') ? 'tds-con' : 'tds-sin'}" title="${esc(c.tipo_3ds)}">${esc(c.seguridad)}</span>` : ''}
        ${c.marca ? `<span class="tag marca">${esc(c.marca)}</span>` : ''}
        <span class="tag">${esc(c.tipo)}</span><span class="tag">${esc(c.prioridad)}</span>
        ${c.duracion ? `<span class="tag">${c.duracion}s</span>` : ''}
        <span class="tag estado-${esc(c.estado).replace(' ','_')}">${esc(c.estado)}</span>
      </span>
    </summary>
    <div class="detalle">
      <div class="grid2">
        <div><h4>Resultado esperado</h4><p>${esc(c.esperado) || '<span class="vacio">—</span>'}</p></div>
        <div><h4>Resultado obtenido</h4><p>${esc(c.obtenido) || '<span class="vacio">—</span>'}</p></div>
      </div>
      <div class="grid2">
        <div><h4>Pasos a seguir</h4><p>${esc(c.pasos)}</p></div>
        <div><h4>Datos de prueba</h4><p>${esc(c.datos) || '—'}</p></div>
      </div>
      <div class="grid2">
        <div><h4>Trámite</h4><p>${esc(c.servicio) || '<span class="vacio">—</span>'}</p></div>
        <div><h4>Tarjeta</h4><p>${c.marca ? `${esc(c.marca)} · ${esc(c.seguridad)} (${esc(c.tipo_3ds)})` : '<span class="vacio">Sin tarjeta</span>'}</p></div>
      </div>
      ${c.error ? `<h4>Detalle del error</h4><pre>${esc(c.error)}</pre>` : ''}
      <h4>Evidencia (${(c.pasos_evidencia || []).length})</h4>
      ${pasos ? `<div class="pasos">${pasos}</div>` : '<p class="vacio">Sin capturas</p>'}
    </div>
  </details>`;
}

function pintar() {
  const m = fModulo.value, t = fTipo.value, p = fPrioridad.value, q = fTexto.value.trim().toLowerCase();
  const visibles = D.casos.filter(c =>
    (!filtroEstado || c.estado === filtroEstado) && (!fServicio.value || c.servicio === fServicio.value) &&
    incluye(c.seguridad, fSeguridad.value) && incluye(c.marca, fMarca.value) && (!m || c.modulo === m) && (!t || c.tipo === t) &&
    (!p || c.prioridad === p) && (!q || [c.id, c.caso, c.obtenido, c.error, c.servicio, c.marca, c.seguridad].join(' ').toLowerCase().includes(q)));
  document.getElementById('contador').textContent = `Mostrando ${visibles.length} de ${total} casos`;
  document.getElementById('lista').innerHTML = visibles.map(tarjeta).join('') || '<p class="vacio">Sin resultados con esos filtros.</p>';
}
pintar();

const visor = document.getElementById('visor');
document.addEventListener('click', e => {
  if (e.target.matches('.paso img')) {
    visor.querySelector('img').src = e.target.src;
    visor.querySelector('p').textContent = e.target.dataset.desc;
    visor.style.display = 'flex';
  } else if (visor.contains(e.target)) visor.style.display = 'none';
});
document.addEventListener('keydown', e => { if (e.key === 'Escape') visor.style.display = 'none'; });
</script>
</body>
</html>
"""


def generar_reporte(datos, destino):
    contenido = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    destino.write_text(PLANTILLA.replace("__DATOS__", contenido), encoding="utf-8")
