// ─── UI helpers (protótipo PRO) ───
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const pg = document.getElementById('page-' + id);
  if (pg) pg.classList.add('active');
  document.querySelectorAll('.nav-item').forEach(btn => {
    if (btn.getAttribute('onclick')?.includes("'" + id + "'"))
      btn.classList.add('active');
  });
  window.scrollTo(0, 0);
  const notif = document.getElementById('notifPanel');
  if (notif) notif.classList.remove('open');
  if (window.innerWidth <= 1024) closeSidebar();
}

const SIDEBAR_ICON_MENU = '<svg viewBox="0 0 24 24"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';
const SIDEBAR_ICON_CLOSE = '<svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

function syncSidebarToggle() {
  const btn = document.getElementById('sidebarToggle');
  if (!btn) return;
  const open = document.body.classList.contains('sidebar-open');
  btn.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
  btn.innerHTML = open ? SIDEBAR_ICON_CLOSE : SIDEBAR_ICON_MENU;
}

function toggleSidebar() {
  document.body.classList.toggle('sidebar-open');
  syncSidebarToggle();
}
function closeSidebar() {
  document.body.classList.remove('sidebar-open');
  syncSidebarToggle();
}

function switchTab(btn, id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  ['tab-select','tab-insert','tab-update','tab-delete'].forEach(t => {
    const el = document.getElementById(t);
    if (el) el.style.display = (t === id) ? 'block' : 'none';
  });
}

function updateClock() {
  const el = document.getElementById('relogio');
  if (el) el.textContent = new Date().toLocaleTimeString('pt-BR');
}
setInterval(updateClock, 1000);
updateClock();

(function initProDate() {
  const d = new Date();
  const dias = ['Domingo','Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado'];
  const meses = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
  const dataStr = dias[d.getDay()] + ', ' + d.getDate() + ' de ' + meses[d.getMonth()] + ' de ' + d.getFullYear();
  const topDate = document.getElementById('hoje-top');
  if (topDate) topDate.textContent = d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
  const sub = document.getElementById('hoje-sub');
  if (sub) sub.textContent = 'Visão geral — ' + dataStr;
})();

function showToast(msg, type) {
  const area = document.getElementById('toastArea');
  if (!area) return;
  const t = document.createElement('div');
  t.className = 'toast ' + (type || '');
  const icons = {
    success: '<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>',
    error:   '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    warn:    '<svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>',
    info:    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
  };
  t.innerHTML = (icons[type] || icons.info) + '<span>' + msg + '</span>';
  area.appendChild(t);
  setTimeout(() => t.style.opacity = '0', 3000);
  setTimeout(() => t.remove(), 3300);
}

function openModal(id) { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
function toggleNotif() {
  const panel = document.getElementById('notifPanel');
  if (!panel) return;
  const abrir = !panel.classList.contains('open');
  panel.classList.toggle('open');
  if (abrir && typeof carregarNotificacoes === 'function') carregarNotificacoes();
}
function irParaEquipe() {
  if (typeof showPage === 'function') showPage('equipe');
}
window.irParaEquipe = irParaEquipe;
function filtrarTabela(tblId, val) {
  document.querySelectorAll('#' + tblId + ' tbody tr').forEach(r => {
    r.style.display = r.textContent.toLowerCase().includes(val.toLowerCase()) ? '' : 'none';
  });
}
function toggleChk(el) {
  el.classList.toggle('done');
  const items = document.querySelectorAll('.chk-item');
  const done = document.querySelectorAll('.chk-item.done').length;
  const total = items.length;
  const cnt = document.getElementById('chk-count');
  if (cnt) {
    cnt.textContent = done + ' / ' + total;
    cnt.className = 'badge ' + (done === total ? 'badge-green' : done > 0 ? 'badge-blue' : 'badge-amber');
  }
  const bar = document.getElementById('chk-bar');
  if (bar) bar.style.width = (done / total * 100) + '%';
}
function addMed() {
  const list = document.getElementById('med-list');
  if (!list) return;
  const div = document.createElement('div');
  div.className = 'rx-item';
  div.style.cssText = 'margin-bottom:8px;display:flex;gap:8px;align-items:flex-start';
  div.innerHTML = `
    <div style="flex:1">
      <div class="form-grid-3" style="gap:8px">
        <div class="form-group"><label>Medicamento</label><input class="rx-med-nome" placeholder="Ex: Paracetamol 500mg"/></div>
        <div class="form-group"><label>Posologia</label><input class="rx-med-pos" placeholder="Ex: 1 comp. 8/8h"/></div>
        <div class="form-group"><label>Duração</label><input class="rx-med-dur" placeholder="Ex: 7 dias"/></div>
      </div>
    </div>
    <button class="btn btn-ghost btn-sm no-print" style="color:var(--red-light);margin-top:18px" onclick="this.closest('.rx-item').remove()">✕</button>`;
  list.appendChild(div);
}
document.addEventListener('click', e => {
  const p = document.getElementById('notifPanel');
  const btn = document.getElementById('notifBtn');
  if (p && btn && p.classList.contains('open') && !p.contains(e.target) && !btn.contains(e.target))
    p.classList.remove('open');
});

document.addEventListener('DOMContentLoaded', function() {
  const btn = document.getElementById('login-btn');
  if (btn && typeof doLogin === 'function') {
    btn.addEventListener('click', function(e) { e.preventDefault(); doLogin(); });
  }
});
