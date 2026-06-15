// ══════════════════════════════════════
// MedSystem PRO — Integração API
// ══════════════════════════════════════

function apiHeaders() {
  const token = localStorage.getItem('token');
  return token
    ? { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' }
    : { 'Content-Type': 'application/json' };
}

async function apiGet(url) {
  const res = await fetch(url, { headers: apiHeaders() });
  return res.json();
}

function carregarModuloPro(pageId) {
  const loaders = {
    dashboard: () => typeof carregarDashboard === 'function' && carregarDashboard(),
    agenda: carregarAgendaSemanal,
    consultas: () => typeof carregarConsultas === 'function' && carregarConsultas(),
    pacientes: () => typeof carregarPacientes === 'function' && carregarPacientes(),
    exames: carregarExames,
    diagnostico: carregarDiagnosticos,
    financeiro: carregarFinanceiro,
    relatorios: carregarRelatorios,
    equipe: carregarEquipe,
    mensagens: carregarMensagens,
    novo_paciente: () => typeof carregarPacientes === 'function' && carregarPacientes()
  };
  if (loaders[pageId]) loaders[pageId]();
}

async function carregarAgendaSemanal() {
  try {
    const json = await apiGet('/api/dashboard/agenda/semana');
    const grid = document.querySelector('#page-agenda .agenda-grid');
    if (!grid || !json.sucesso || !json.dados) return;
    const dias = json.dados.dias || [];
    const slots = json.dados.horarios || ['08:00', '09:30', '11:00', '14:00', '15:30'];
    let html = '<div class="agenda-cell agenda-head"></div>';
    dias.forEach(d => {
      html += `<div class="agenda-cell agenda-head${d.hoje ? ' today' : ''}">${d.label || d.dia}</div>`;
    });
    slots.forEach(hora => {
      html += `<div class="agenda-cell agenda-time">${hora}</div>`;
      dias.forEach(d => {
        const appt = (d.consultas || []).find(c => c.hora === hora);
        html += appt
          ? `<div class="agenda-cell"><div class="appt green"><div class="appt-name">${appt.paciente}</div><div class="appt-info">${appt.motivo || 'Consulta'}</div></div></div>`
          : '<div class="agenda-cell"></div>';
      });
    });
    grid.innerHTML = html;
  } catch (e) { console.error('Erro agenda:', e); }
}

async function carregarExames() {
  try {
    const json = await apiGet('/api/exames');
    const tbody = document.querySelector('#tabela-exames tbody') || document.querySelector('#page-exames tbody');
    if (!tbody || !json.sucesso) return;
    tbody.innerHTML = '';
    if (!json.dados?.length) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#999;">Nenhum exame registrado</td></tr>';
      return;
    }
    json.dados.forEach(ex => {
      tbody.innerHTML += `<tr>
        <td class="td-name">Paciente #${ex.id_paciente}</td>
        <td>${ex.nome_exame || 'Exame'}</td>
        <td class="td-mono">${ex.data_solicitacao ? new Date(ex.data_solicitacao).toLocaleDateString('pt-BR') : '—'}</td>
        <td>—</td>
        <td><span class="badge badge-amber">${ex.status || 'Solicitado'}</span></td>
        <td><span class="badge badge-blue">${ex.prioridade || 'Normal'}</span></td>
        <td>—</td>
      </tr>`;
    });
  } catch (e) { console.error('Erro exames:', e); }
}

async function carregarDiagnosticos() {
  try {
    const json = await apiGet('/api/relatorios');
    if (!json.sucesso || !json.dados?.top_diagnosticos) return;
    const el = document.getElementById('cid-result');
    if (!el) return;
    const lista = json.dados.top_diagnosticos;
    el.innerHTML = lista.length
      ? lista.map(d => `<div style="padding:10px 14px;border-bottom:1px solid var(--border)"><strong>${d.cid}</strong> — ${d.descricao} <span class="badge badge-blue">${d.total}</span></div>`).join('')
      : '<div style="padding:20px;text-align:center;color:#999">Sem diagnósticos</div>';
  } catch (e) { console.error('Erro diagnósticos:', e); }
}

async function buscarCID(q) {
  const el = document.getElementById('cid-result');
  if (!el) return;
  if (!q || q.length < 2) {
    el.innerHTML = '<div style="text-align:center;padding:32px;color:var(--text4)">Digite para buscar CID-10</div>';
    return;
  }
  try {
    const json = await apiGet('/api/cid10/busca?q=' + encodeURIComponent(q));
    if (!json.sucesso || !json.dados?.length) {
      el.innerHTML = '<div style="padding:20px;text-align:center;color:#999">Nenhum resultado</div>';
      return;
    }
    el.innerHTML = json.dados.map(c =>
      `<div onclick="showToast('CID ${c.codigo} selecionado','success')" style="padding:10px 14px;border-bottom:1px solid var(--border);cursor:pointer">
        <strong>${c.codigo}</strong> — ${c.descricao}
      </div>`
    ).join('');
  } catch (e) { console.error('Erro CID:', e); }
}

async function carregarFinanceiro() {
  try {
    const json = await apiGet('/api/financeiro');
    if (!json.sucesso) return;
    const tbody = document.querySelector('#page-financeiro tbody');
    if (!tbody || !json.dados?.receitas_recentes) return;
    tbody.innerHTML = json.dados.receitas_recentes.map(r =>
      `<tr><td>${r.descricao || 'Receita'}</td><td>R$ ${(r.valor || 0).toFixed(2)}</td><td>${r.status || 'PENDENTE'}</td></tr>`
    ).join('') || '<tr><td colspan="3" style="text-align:center">Sem dados</td></tr>';
  } catch (e) { console.error('Erro financeiro:', e); }
}

async function carregarRelatorios() {
  try {
    await apiGet('/api/relatorios');
  } catch (e) { console.error('Erro relatórios:', e); }
}

async function carregarEquipe() {
  try {
    const json = await apiGet('/api/medicos');
    const tbody = document.querySelector('#tabela-equipe tbody');
    if (!tbody || !json.sucesso) return;
    tbody.innerHTML = (json.dados || []).map(m =>
      `<tr><td class="td-name">${m.nome || 'Médico'}</td><td>${m.crm || '—'}</td><td>${m.especialidade?.nome || m.especialidade || '—'}</td><td><span class="badge badge-green">Ativo</span></td></tr>`
    ).join('') || '<tr><td colspan="4" style="text-align:center">Nenhum médico</td></tr>';
  } catch (e) { console.error('Erro equipe:', e); }
}

let chatAtualId = null;

async function carregarMensagens() {
  try {
    const json = await apiGet('/api/mensagens');
    const lista = document.getElementById('chat-list');
    if (!lista || !json.sucesso) return;
    const conversas = Object.values(json.dados || {});
    lista.innerHTML = conversas.length
      ? conversas.map(c =>
          `<div style="padding:10px 14px;border-bottom:1px solid var(--border);cursor:pointer" onclick="selectChat(${c.usuario_id},'${(c.nome||'').replace(/'/g,"\\'")}')">
            <strong>${c.nome || 'Usuário'}</strong><br><small>${c.ultimas_mensagens?.[0] || ''}</small>
          </div>`
        ).join('')
      : '<div style="padding:16px;color:#999;text-align:center">Nenhuma conversa</div>';
  } catch (e) { console.error('Erro mensagens:', e); }
}

async function selectChat(usuarioId, nome) {
  chatAtualId = usuarioId;
  const titulo = document.getElementById('chat-header-name');
  if (titulo) titulo.textContent = nome || 'Conversa';
  try {
    const json = await apiGet('/api/mensagens/' + usuarioId);
    const area = document.getElementById('chat-body');
    if (!area || !json.sucesso) return;
    area.innerHTML = (json.mensagens || []).map(m => {
      const sent = m.id_remetente === currentUser?.id;
      return `<div style="margin:8px 0;text-align:${sent ? 'right' : 'left'}"><span style="display:inline-block;padding:8px 12px;border-radius:10px;background:${sent ? 'var(--blue-mid)' : 'var(--surface2)'};${sent ? 'color:#fff;' : ''}">${m.conteudo}</span></div>`;
    }).join('') || '<div style="color:#999;text-align:center;padding:20px">Inicie a conversa</div>';
  } catch (e) { console.error('Erro conversa:', e); }
}

async function sendMsg() {
  const input = document.getElementById('msg-input');
  if (!input || !chatAtualId) { showToast('Selecione uma conversa', 'warn'); return; }
  const texto = input.value.trim();
  if (!texto) return;
  try {
    const res = await fetch('/api/mensagens', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({ id_destinatario: chatAtualId, conteudo: texto })
    });
    const json = await res.json();
    if (json.sucesso) {
      input.value = '';
      selectChat(chatAtualId, document.getElementById('chat-header-name')?.textContent);
    } else {
      showToast(json.mensagem || 'Erro ao enviar', 'error');
    }
  } catch (e) { showToast('Erro de conexão', 'error'); }
}

async function agendarConsultaModal() {
  const pacId = document.getElementById('nc-pac')?.value;
  const medId = document.getElementById('nc-med')?.value;
  const data = document.getElementById('nc-data')?.value;
  const hora = document.getElementById('nc-hora')?.value;
  const motivo = document.getElementById('nc-motivo')?.value?.trim();
  if (!pacId || !medId || !data || !hora || !motivo) {
    showToast('Preencha todos os campos obrigatórios (*)', 'error');
    return;
  }
  try {
    const res = await fetch('/api/consultas', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({
        id_paciente: parseInt(pacId),
        id_medico: parseInt(medId),
        data_consulta: `${data}T${hora}:00`,
        hora_consulta: hora,
        motivo
      })
    });
    const json = await res.json();
    if (json.sucesso) {
      closeModal('modal-consulta');
      showToast('Consulta agendada com sucesso!', 'success');
      if (typeof carregarDashboard === 'function') carregarDashboard();
      if (typeof carregarConsultas === 'function') carregarConsultas();
    } else {
      showToast(json.mensagem || 'Falha ao agendar', 'error');
    }
  } catch (e) { showToast('Erro de conexão', 'error'); }
}

let _searchTimer = null;
function globalSearchFn(val) {
  clearTimeout(_searchTimer);
  if (!val || val.length < 2) return;
  _searchTimer = setTimeout(async () => {
    try {
      const json = await apiGet('/api/pacientes/buscar?q=' + encodeURIComponent(val));
      if (json.sucesso && json.dados?.length) {
        showPage('pacientes');
        const tbody = document.querySelector('#tabela-pacientes tbody');
        if (tbody) {
          tbody.innerHTML = json.dados.map(p =>
            `<tr><td>${p.nome}</td><td>${p.cpf}</td><td>${p.telefone || '—'}</td>
             <td><button class="btn btn-outline btn-sm" onclick="abrirProntuario(${p.id || p.id_paciente})">Abrir</button></td></tr>`
          ).join('');
        }
      }
    } catch (e) { console.error('Busca:', e); }
  }, 350);
}

function limparForm() {
  ['np-nome','np-cpf','np-nasc','np-tel','np-email','np-end','np-alerg','np-obs'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
}

// Hook showPage
(function () {
  const original = window.showPage;
  if (!original) return;
  window.showPage = function (id) {
    original(id);
    carregarModuloPro(id);
  };
})();

// Abrir modal de consulta → carregar selects
(function () {
  const original = window.openModal;
  window.openModal = function (id) {
    if (original) original(id);
    else document.getElementById(id)?.classList.add('open');
    if (id === 'modal-consulta' && typeof carregarDadosParaAgendamento === 'function') {
      carregarDadosParaAgendamento();
    }
  };
})();

// Restaurar sessão (valida token antes de abrir o app)
document.addEventListener('DOMContentLoaded', async function () {
  const token = localStorage.getItem('token');
  if (!token) return;

  try {
    const res = await fetch('/api/auth/perfil', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const json = await res.json();
    if (!res.ok || !json.sucesso || !json.dados) {
      localStorage.removeItem('token');
      localStorage.removeItem('usuario');
      return;
    }

    currentUser = json.dados;
    localStorage.setItem('usuario', JSON.stringify(currentUser));

    const loginScreen = document.getElementById('login-screen');
    const appScreen = document.getElementById('app-screen');
    if (loginScreen) loginScreen.style.display = 'none';
    if (appScreen) {
      appScreen.style.display = 'block';
      appScreen.classList.add('active');
    }
    loginSuccess(currentUser);
  } catch (e) {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
  }
});
