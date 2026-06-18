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

async function apiPost(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: apiHeaders(),
    body: JSON.stringify(body || {}),
  });
  let json = {};
  try { json = await res.json(); } catch (e) {
    json = { sucesso: false, mensagem: 'Resposta invalida do servidor' };
  }
  if (!res.ok) json.sucesso = false;
  if (!json.mensagem && !res.ok) json.mensagem = 'Erro HTTP ' + res.status;
  return json;
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
    prescricoes: carregarPrescricoes,
    portal_inicio: carregarPortalInicio,
    portal_exames: carregarPortalExames,
    portal_prontuario: carregarPortalProntuario,
    portal_notificacoes: carregarPortalNotificacoes,
    // prontuário: aberto via abrirProntuario() / abrirProntuarioInicio() — não resetar aqui
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
    const slots = json.dados.horarios || ['08:00', '09:30', '11:00', '14:00', '15:30', '17:00'];

    const sub = document.querySelector('#page-agenda .page-sub');
    if (sub && dias.length) {
      sub.textContent = 'Semana de ' + dias[0].dia + ' a ' + dias[dias.length - 1].dia;
    }

    const corAppt = (status) => {
      const s = (status || '').toUpperCase();
      if (s === 'EM_ATENDIMENTO' || s === 'EM_ANDAMENTO') return 'amber';
      if (s === 'CONCLUIDA') return 'purple';
      if (s.includes('URG')) return 'red';
      return 'green';
    };

    const esc = (s) => String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

    let html = '<div class="agenda-cell agenda-head"></div>';
    dias.forEach(d => {
      html += `<div class="agenda-cell agenda-head${d.hoje ? ' today' : ''}">${d.label || d.dia}${d.hoje ? ' ●' : ''}<br><small>${d.dia || ''}</small></div>`;
    });
    slots.forEach(hora => {
      html += `<div class="agenda-cell agenda-time">${hora}</div>`;
      dias.forEach(d => {
        const appt = (d.consultas || []).find(c => c.hora === hora);
        html += appt
          ? `<div class="agenda-cell agenda-cell-appt"><div class="appt ${corAppt(appt.status)}" role="button" tabindex="0" title="Ver agendamento — ${esc(appt.paciente)}" onclick="verAgendamento(${appt.id_consulta})" onkeydown="if(event.key==='Enter')verAgendamento(${appt.id_consulta})"><div class="appt-name">${esc(appt.paciente)}</div><div class="appt-info">${esc(appt.motivo || 'Consulta')}</div><div class="appt-reservado">Clique para ver</div></div></div>`
          : '<div class="agenda-cell"></div>';
      });
    });
    grid.innerHTML = html;
  } catch (e) { console.error('Erro agenda:', e); }
}

let _agendDetalhe = { id_consulta: null, id_paciente: null };

function _badgeStatusAgenda(status) {
  const s = (status || 'AGENDADA').toUpperCase();
  if (s === 'CONCLUIDA') return 'badge-green';
  if (s === 'EM_ATENDIMENTO' || s === 'EM_ANDAMENTO') return 'badge-amber';
  if (s === 'CANCELADA') return 'badge-red';
  return 'badge-blue';
}

function _rotuloStatusAgenda(status) {
  const map = {
    AGENDADA: 'Agendada',
    EM_ATENDIMENTO: 'Em atendimento',
    EM_ANDAMENTO: 'Em andamento',
    CONCLUIDA: 'Concluída',
    CANCELADA: 'Cancelada'
  };
  return map[(status || '').toUpperCase()] || status || 'Agendada';
}

async function verAgendamento(idConsulta) {
  if (!idConsulta) return;

  _agendDetalhe = { id_consulta: idConsulta, id_paciente: null };
  const loading = document.getElementById('agend-detalhe-loading');
  const conteudo = document.getElementById('agend-detalhe-conteudo');
  if (loading) { loading.style.display = ''; loading.textContent = 'Carregando...'; }
  if (conteudo) conteudo.style.display = 'none';

  openModal('modal-agendamento');

  try {
    const json = await apiGet('/api/consultas/' + idConsulta);
    if (!json.sucesso || !json.dados) {
      if (loading) loading.textContent = json.mensagem || 'Agendamento não encontrado';
      showToast(json.mensagem || 'Erro ao carregar agendamento', 'error');
      return;
    }

    const c = json.dados;
    const idPac = c.id_paciente || (c.paciente && (c.paciente.id || c.paciente.id_paciente));
    _agendDetalhe.id_paciente = idPac;

    let telefone = '—';
    if (idPac) {
      try {
        const jp = await apiGet('/api/pacientes/' + idPac);
        if (jp.sucesso && jp.dados) telefone = jp.dados.telefone || '—';
      } catch (_) { /* opcional */ }
    }

    const nome = (c.paciente && c.paciente.nome) || 'Paciente';
    const idCons = c.id || c.id_consulta;
    const dataFmt = c.data_consulta
      ? new Date(c.data_consulta).toLocaleDateString('pt-BR', { timeZone: 'UTC' })
      : '—';
    const horaFmt = c.hora_consulta || (c.data_consulta ? new Date(c.data_consulta).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '—');
    const medico = (c.medico && c.medico.nome) || '—';

    const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    set('agend-paciente', nome);
    set('agend-numero', '#' + String(idCons).padStart(4, '0'));
    set('agend-data', dataFmt);
    set('agend-hora', horaFmt);
    set('agend-medico', medico);
    set('agend-tipo', c.tipo_consulta || 'Consulta');
    set('agend-convenio', c.convenio || 'Particular');
    set('agend-telefone', typeof formatarTelefone === 'function' ? formatarTelefone(telefone) : telefone);
    set('agend-motivo', c.motivo || 'Não informado');

    const avatar = document.getElementById('agend-avatar');
    if (avatar) avatar.textContent = nome.substring(0, 2).toUpperCase();

    const st = document.getElementById('agend-status');
    if (st) {
      st.textContent = _rotuloStatusAgenda(c.status);
      st.className = 'badge ' + _badgeStatusAgenda(c.status);
    }

    const btnPront = document.getElementById('agend-btn-prontuario');
    if (btnPront) {
      btnPront.style.display = (typeof podeAcessarProntuario === 'function' && podeAcessarProntuario()) ? '' : 'none';
    }

    if (loading) loading.style.display = 'none';
    if (conteudo) conteudo.style.display = '';
  } catch (e) {
    console.error('Erro verAgendamento:', e);
    if (loading) loading.textContent = 'Erro ao carregar agendamento';
    showToast('Erro ao carregar agendamento', 'error');
  }
}

function fecharAgendamentoAbrirProntuario() {
  const { id_paciente, id_consulta } = _agendDetalhe;
  closeModal('modal-agendamento');
  if (id_paciente && typeof abrirProntuario === 'function') {
    abrirProntuario(id_paciente, id_consulta);
  }
}

function fecharAgendamentoVerConsultas() {
  closeModal('modal-agendamento');
  showPage('consultas');
  if (typeof carregarConsultas === 'function') carregarConsultas();
}

async function carregarHorariosDisponiveis() {
  const medId = document.getElementById('nc-med')?.value;
  const data = document.getElementById('nc-data')?.value;
  const container = document.getElementById('nc-horarios-slots');
  const hiddenHora = document.getElementById('nc-hora');
  if (!container) return;

  if (!medId || !data) {
    container.innerHTML = '<div class="hora-slots-hint">Selecione o médico e a data para ver os horários disponíveis</div>';
    if (hiddenHora) hiddenHora.value = '';
    return;
  }

  container.innerHTML = '<div class="hora-slots-hint">Carregando horários...</div>';
  try {
    const json = await apiGet('/api/consultas/horarios-disponiveis?id_medico=' + medId + '&data=' + data);
    if (!json.sucesso) {
      container.innerHTML = '<div class="hora-slots-hint">' + (json.mensagem || 'Erro ao carregar') + '</div>';
      return;
    }
    if (hiddenHora) hiddenHora.value = '';
    let html = '';
    (json.horarios || []).forEach(h => {
      if (h.disponivel) {
        html += '<button type="button" class="hora-slot-btn" onclick="selecionarHoraAgendamento(this,\'' + h.hora + '\')">' +
          '<div class="hora-slot-hora">' + h.hora + '</div><div class="hora-slot-status">Disponível</div></button>';
      } else {
        const pac = (h.paciente || 'Paciente').replace(/'/g, '&#39;');
        html += '<div class="hora-slot-btn ocupado" title="Reservado — ' + pac + '">' +
          '<div class="hora-slot-hora">' + h.hora + '</div><div class="hora-slot-status">Reservado</div></div>';
      }
    });
    container.innerHTML = html || '<div class="hora-slots-hint">Nenhum horário na grade</div>';
  } catch (e) {
    container.innerHTML = '<div class="hora-slots-hint">Erro ao carregar horários</div>';
  }
}

function selecionarHoraAgendamento(btn, hora) {
  document.querySelectorAll('.hora-slot-btn:not(.ocupado)').forEach(b => b.classList.remove('selecionado'));
  btn.classList.add('selecionado');
  const el = document.getElementById('nc-hora');
  if (el) el.value = hora;
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
    const lista = json.cids || json.dados || [];
    if (!json.sucesso || !lista.length) {
      el.innerHTML = '<div style="padding:20px;text-align:center;color:#999">Nenhum resultado</div>';
      return;
    }
    el.innerHTML = lista.map(c =>
      `<div onclick="showToast('CID ${c.codigo} selecionado','success')" style="padding:10px 14px;border-bottom:1px solid var(--border);cursor:pointer">
        <strong>${c.codigo}</strong> — ${c.descricao}
      </div>`
    ).join('');
  } catch (e) { console.error('Erro CID:', e); }
}

async function carregarFinanceiro() {
  try {
    const [dash, precos] = await Promise.all([
      apiGet('/api/financeiro'),
      apiGet('/api/financeiro/precos')
    ]);
    if (dash.sucesso) renderFinanceiroDashboard(dash);
    if (precos.sucesso) renderTabelaPrecos(precos.precos || []);
  } catch (e) { console.error('Erro financeiro:', e); }
}

function fmtMoeda(v) {
  return 'R$ ' + Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function renderFinanceiroDashboard(json) {
  const m = json.metricas || {};
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set('fin-receita-mensal', fmtMoeda(m.receita_mensal));
  set('fin-consultas-pagas', m.consultas_pagas ?? 0);
  set('fin-a-receber', fmtMoeda(m.a_receber));
  set('fin-despesas', fmtMoeda(m.despesas));
  if (json.periodo) {
    set('fin-periodo', json.periodo.inicio + ' — ' + json.periodo.fim);
    const titulo = document.getElementById('fin-cat-titulo');
    if (titulo) titulo.textContent = 'Receita por Categoria — ' + json.periodo.inicio.slice(3);
  }

  const catEl = document.getElementById('fin-categorias');
  if (catEl) {
    const cats = json.categorias || [];
    const total = cats.reduce((s, c) => s + (c.valor || 0), 0) || 1;
    catEl.innerHTML = cats.length
      ? cats.map(c => {
          const pct = Math.round((c.valor / total) * 100);
          return `<div style="margin-bottom:14px">
            <div class="flex-bet text-sm mb16"><span style="font-weight:600">${c.nome}</span><span style="font-weight:700">${fmtMoeda(c.valor)}</span></div>
            <div class="finance-bar"><div class="finance-fill" style="width:${pct}%;background:linear-gradient(90deg,var(--blue),var(--teal-light))"></div></div>
            <div class="text-xs text-3" style="margin-top:4px">${pct}% do total</div>
          </div>`;
        }).join('') + `<div class="divider"></div><div class="flex-bet"><span style="font-weight:700">Total</span><span style="font-weight:700;font-size:16px;color:var(--green-light)">${fmtMoeda(total)}</span></div>`
      : '<div style="text-align:center;color:var(--text4);padding:20px">Nenhuma receita no período</div>';
  }

  const tbody = document.getElementById('tbody-fin-lancamentos');
  if (tbody) {
    const lanc = json.lancamentos || [];
    tbody.innerHTML = lanc.length
      ? lanc.map(l => {
          const positivo = l.valor >= 0;
          const badge = l.tipo === 'Entrada' ? 'badge-green' : 'badge-red';
          return `<tr>
            <td class="td-mono">${l.data}</td>
            <td>${l.descricao || '—'}</td>
            <td><span class="badge ${badge}">${l.tipo}</span></td>
            <td style="font-weight:700;color:${positivo ? 'var(--green-light)' : 'var(--red-light)'}">${positivo ? '+' : ''}${fmtMoeda(Math.abs(l.valor))}</td>
          </tr>`;
        }).join('')
      : '<tr><td colspan="4" style="text-align:center;color:var(--text4)">Sem lançamentos no mês</td></tr>';
  }
}

function renderTabelaPrecos(precos) {
  const tbody = document.getElementById('tbody-precos');
  if (!tbody) return;
  tbody.innerHTML = precos.length
    ? precos.map(p => `<tr>
        <td>${p.tipo_consulta}</td>
        <td><span class="badge ${p.modalidade === 'Particular' ? 'badge-green' : 'badge-blue'}">${p.modalidade}</span></td>
        <td>${p.nome_convenio || '—'}</td>
        <td style="font-weight:700">${fmtMoeda(p.valor)}</td>
        <td>
          <button class="btn btn-ghost btn-sm" onclick="editarPrecoConsulta(${p.id}, ${p.valor})">Editar</button>
          <button class="btn btn-ghost btn-sm" style="color:var(--red-light)" onclick="excluirPrecoConsulta(${p.id})">Excluir</button>
        </td>
      </tr>`).join('')
    : '<tr><td colspan="5" style="text-align:center;color:var(--text4)">Nenhum preço cadastrado</td></tr>';
}

function toggleFormPreco(show) {
  const box = document.getElementById('form-preco-box');
  if (!box) return;
  const abrir = show !== false && (show === true || box.style.display === 'none');
  box.style.display = abrir ? 'block' : 'none';
  if (abrir) {
    document.getElementById('preco-tipo').value = '1ª Consulta';
    document.getElementById('preco-modalidade').value = 'Particular';
    document.getElementById('preco-convenio').value = '';
    document.getElementById('preco-valor').value = '';
    toggleCampoConvenioPreco();
  }
}

function toggleCampoConvenioPreco() {
  const mod = document.getElementById('preco-modalidade')?.value;
  const grp = document.getElementById('preco-convenio-group');
  if (grp) grp.style.display = mod === 'Convenio' ? 'block' : 'none';
}

async function salvarPrecoConsulta() {
  const tipo = document.getElementById('preco-tipo')?.value;
  const modalidade = document.getElementById('preco-modalidade')?.value;
  const nome_convenio = document.getElementById('preco-convenio')?.value?.trim();
  const valor = parseFloat(document.getElementById('preco-valor')?.value);
  if (!valor || valor <= 0) {
    showToast('Informe um valor válido', 'error');
    return;
  }
  if (modalidade === 'Convenio' && !nome_convenio) {
    showToast('Informe o nome do convênio', 'error');
    return;
  }
  try {
    const res = await fetch('/api/financeiro/precos', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({ tipo_consulta: tipo, modalidade, nome_convenio, valor })
    });
    const json = await res.json();
    if (!json.sucesso) throw new Error(json.mensagem || json.erro || 'Erro ao salvar');
    showToast(json.mensagem || 'Preço salvo', 'success');
    toggleFormPreco(false);
    carregarFinanceiro();
  } catch (e) {
    showToast(e.message || 'Erro ao salvar preço', 'error');
  }
}

async function editarPrecoConsulta(id, valorAtual) {
  const novo = prompt('Novo valor (R$):', String(valorAtual));
  if (novo === null) return;
  const valor = parseFloat(novo.replace(',', '.'));
  if (!valor || valor <= 0) {
    showToast('Valor inválido', 'error');
    return;
  }
  try {
    const res = await fetch('/api/financeiro/precos/' + id, {
      method: 'PUT',
      headers: apiHeaders(),
      body: JSON.stringify({ valor })
    });
    const json = await res.json();
    if (!json.sucesso) throw new Error(json.mensagem || json.erro);
    showToast('Preço atualizado', 'success');
    carregarFinanceiro();
  } catch (e) {
    showToast(e.message || 'Erro ao atualizar', 'error');
  }
}

async function excluirPrecoConsulta(id) {
  if (!confirm('Remover este preço da tabela?')) return;
  try {
    const res = await fetch('/api/financeiro/precos/' + id, {
      method: 'DELETE',
      headers: apiHeaders()
    });
    const json = await res.json();
    if (!json.sucesso) throw new Error(json.mensagem || json.erro);
    showToast('Preço removido', 'success');
    carregarFinanceiro();
  } catch (e) {
    showToast(e.message || 'Erro ao excluir', 'error');
  }
}

window.toggleFormPreco = toggleFormPreco;
window.toggleCampoConvenioPreco = toggleCampoConvenioPreco;
window.salvarPrecoConsulta = salvarPrecoConsulta;
window.editarPrecoConsulta = editarPrecoConsulta;
window.excluirPrecoConsulta = excluirPrecoConsulta;

let _relatorioData = null;

async function carregarRelatorios(comAviso) {
  const escR = (s) => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  const setTxt = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
  try {
    const json = await apiGet('/api/relatorios');
    if (!json || !json.sucesso) {
      const aviso = '<div class="text-3 text-sm" style="text-align:center;padding:12px">Não foi possível carregar os dados</div>';
      const ed = document.getElementById('rel-diagnosticos'); if (ed) ed.innerHTML = aviso;
      const em = document.getElementById('rel-medicos'); if (em) em.innerHTML = aviso;
      if (comAviso) showToast('Não foi possível gerar o relatório', 'error');
      return;
    }
    _relatorioData = json;

    const ind = json.indicadores || {};
    const periodo = (json.periodo && json.periodo.mes) ? json.periodo.mes : '';
    setTxt('rel-periodo', periodo ? ('Indicadores de ' + periodo) : 'Indicadores clínicos e operacionais');

    setTxt('rel-consultas', ind.consultas_mes ?? 0);
    const varc = Number(ind.variacao_consultas || 0);
    const deltaEl = document.getElementById('rel-consultas-delta');
    if (deltaEl) {
      deltaEl.textContent = (varc >= 0 ? '↑ ' : '↓ ') + Math.abs(varc) + '% vs mês ant.';
      deltaEl.className = 'stat-delta ' + (varc >= 0 ? 'up' : 'down');
    }
    setTxt('rel-novos', ind.novos_pacientes ?? 0);
    setTxt('rel-novos-label', periodo || '—');
    setTxt('rel-retornos', ind.retornos ?? 0);
    setTxt('rel-retornos-delta', (ind.taxa_retorno ?? 0) + '% do total');
    setTxt('rel-exames', ind.exames_solicitados ?? 0);
    setTxt('rel-exames-label', periodo || '—');

    // Top diagnósticos
    const cores = ['var(--red-light)', 'var(--blue-light)', 'var(--amber-light)', 'var(--teal-light)', 'var(--purple-light)'];
    const diag = json.top_diagnosticos || [];
    const elDiag = document.getElementById('rel-diagnosticos');
    if (elDiag) {
      if (!diag.length) {
        elDiag.innerHTML = '<div class="text-3 text-sm" style="text-align:center;padding:12px">Nenhum diagnóstico no período</div>';
      } else {
        const maxD = Math.max(...diag.map(d => d.casos || 0), 1);
        elDiag.innerHTML = diag.map((d, i) => {
          const pct = Math.round(((d.casos || 0) / maxD) * 100);
          return `<div style="margin-bottom:12px">
            <div class="flex-bet text-sm mb16"><span style="font-weight:600">${escR(d.cid)} · ${escR(d.descricao)}</span><span>${d.casos || 0} casos</span></div>
            <div class="finance-bar"><div class="finance-fill" style="width:${pct}%;background:${cores[i % cores.length]}"></div></div>
          </div>`;
        }).join('');
      }
    }

    // Consultas por médico
    const coresM = ['var(--blue-mid)', 'var(--green-light)', 'var(--purple-light)', 'var(--amber-light)', 'var(--teal-light)'];
    const avs = ['avatar-blue', 'avatar-green', 'avatar-purple'];
    const meds = json.consultas_por_medico || [];
    const elMed = document.getElementById('rel-medicos');
    if (elMed) {
      if (!meds.length) {
        elMed.innerHTML = '<div class="text-3 text-sm" style="text-align:center;padding:12px">Nenhuma consulta no período</div>';
      } else {
        const maxM = Math.max(...meds.map(m => m.consultas || 0), 1);
        elMed.innerHTML = meds.map((m, i) => {
          const pct = Math.round(((m.consultas || 0) / maxM) * 100);
          const ini = String(m.nome || '?').split(' ').filter(Boolean).slice(0, 2).map(p => p[0]).join('').toUpperCase();
          return `<div style="margin-bottom:14px">
            <div class="flex-bet mb16">
              <div style="display:flex;align-items:center;gap:8px"><div class="avatar ${avs[i % avs.length]}" style="width:28px;height:28px;font-size:11px">${escR(ini)}</div><span style="font-weight:600">${escR(m.nome)}</span></div>
              <span style="font-weight:700">${m.consultas || 0}</span>
            </div>
            <div class="finance-bar"><div class="finance-fill" style="width:${pct}%;background:${coresM[i % coresM.length]}"></div></div>
          </div>`;
        }).join('');
      }
    }

    carregarFinanceiroView();

    if (comAviso) showToast('Relatório gerado!', 'success');
  } catch (e) {
    console.error('Erro relatórios:', e);
    if (comAviso) showToast('Erro ao gerar relatório', 'error');
  }
}

async function carregarFinanceiroView() {
  const el = document.getElementById('rel-financeiro-view');
  if (!el) return;
  const meses = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  const fmt = (v) => 'R$ ' + Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  try {
    const json = await apiGet('/api/relatorios/financeiro-mensal');
    if (!json.sucesso || !json.meses?.length) {
      el.innerHTML = '<div class="text-3 text-sm" style="text-align:center;padding:12px">Sem dados financeiros</div>';
      return;
    }
    el.innerHTML = `<table class="table" style="width:100%">
      <thead><tr><th>Período</th><th>Recebido</th><th>Pendente</th><th>Registros</th></tr></thead>
      <tbody>${json.meses.map(m =>
        `<tr><td>${meses[m.mes] || m.mes}/${m.ano}</td><td>${fmt(m.total_recebido)}</td><td>${fmt(m.total_pendente)}</td><td>${m.total_registros}</td></tr>`
      ).join('')}</tbody>
    </table>`;
  } catch (e) {
    console.error('Erro view financeiro:', e);
    el.innerHTML = '<div class="text-3 text-sm" style="text-align:center;padding:12px">Erro ao carregar</div>';
  }
}

function gerarRelatorioPDF() {
  if (!window.jspdf || !window.jspdf.jsPDF) {
    showToast('Biblioteca de PDF não carregada. Verifique a conexão.', 'error');
    return;
  }
  if (!_relatorioData) {
    showToast('Carregue o relatório antes de exportar', 'warn');
    return;
  }
  const d = _relatorioData;
  const ind = d.indicadores || {};
  const periodo = (d.periodo && d.periodo.mes) ? d.periodo.mes : '';
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  doc.setFontSize(18);
  doc.setTextColor(26, 86, 219);
  doc.text('MedSystem PRO — Relatório', 14, 20);
  doc.setFontSize(11);
  doc.setTextColor(90, 90, 90);
  doc.text('Período: ' + (periodo || '—'), 14, 28);
  doc.text('Gerado em: ' + new Date().toLocaleString('pt-BR'), 14, 34);

  doc.autoTable({
    startY: 42,
    head: [['Indicador', 'Valor']],
    body: [
      ['Consultas no mês', String(ind.consultas_mes ?? 0)],
      ['Variação vs mês anterior', (ind.variacao_consultas ?? 0) + '%'],
      ['Novos pacientes', String(ind.novos_pacientes ?? 0)],
      ['Retornos', String(ind.retornos ?? 0)],
      ['Taxa de retorno', (ind.taxa_retorno ?? 0) + '%'],
      ['Exames solicitados', String(ind.exames_solicitados ?? 0)],
    ],
    theme: 'striped',
    headStyles: { fillColor: [37, 99, 235] },
  });

  const diag = d.top_diagnosticos || [];
  if (diag.length) {
    doc.autoTable({
      startY: doc.lastAutoTable.finalY + 8,
      head: [['CID', 'Diagnóstico', 'Casos']],
      body: diag.map(x => [x.cid || '', x.descricao || '', String(x.casos || 0)]),
      theme: 'striped',
      headStyles: { fillColor: [37, 99, 235] },
    });
  }

  const meds = d.consultas_por_medico || [];
  if (meds.length) {
    doc.autoTable({
      startY: doc.lastAutoTable.finalY + 8,
      head: [['Médico', 'CRM', 'Consultas']],
      body: meds.map(x => [x.nome || '', x.crm || '', String(x.consultas || 0)]),
      theme: 'striped',
      headStyles: { fillColor: [37, 99, 235] },
    });
  }

  const nome = 'relatorio-medsystem-' + (periodo || 'atual').replace(/[^\w]+/g, '-').toLowerCase() + '.pdf';
  doc.save(nome);
  showToast('PDF exportado!', 'success');
}

async function carregarEquipe() {
  aplicarPermissoesEquipe(currentUser || JSON.parse(localStorage.getItem('usuario') || 'null'));
  try {
    const jsonMed = await apiGet('/api/medicos');
    const tbodyMed = document.querySelector('#tabela-equipe tbody');
    if (tbodyMed && jsonMed.sucesso) {
      tbodyMed.innerHTML = (jsonMed.dados || []).map(m =>
        `<tr><td class="td-name">${m.nome || 'Médico'}</td><td>${m.crm || '—'}</td><td>${m.especialidade?.nome || m.especialidade || '—'}</td><td><span class="badge badge-green">Ativo</span></td></tr>`
      ).join('') || '<tr><td colspan="4" style="text-align:center">Nenhum médico</td></tr>';
    }
  } catch (e) { console.error('Erro equipe médicos:', e); }

  if (!podeGerenciarUsuarios()) return;
  try {
    const json = await apiGet('/api/auth/usuarios');
    const tbody = document.getElementById('tabela-usuarios');
    const thAcoes = document.getElementById('th-usuarios-acoes');
    const isAdmin = ehAdministrador();
    if (thAcoes) thAcoes.style.display = isAdmin ? '' : 'none';

    if (!tbody || !json.sucesso) return;
    const badgeTipo = t => ({
      admin: 'badge-purple', medico: 'badge-blue', recepcao: 'badge-amber'
    }[t] || 'badge-blue');
    const eu = currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
    const cols = isAdmin ? 5 : 4;

    tbody.innerHTML = (json.dados || []).map(u => {
      const souEu = eu && String(eu.id) === String(u.id);
      const btnExcluir = isAdmin && !souEu
        ? `<td><button type="button" class="btn btn-sm btn-danger" onclick="excluirUsuario(${u.id}, ${JSON.stringify(u.nome)})">Excluir</button></td>`
        : (isAdmin ? '<td><span class="text-xs text-3">—</span></td>' : '');
      return `<tr>
        <td class="td-name">${u.nome}${souEu ? ' <span class="badge badge-blue">Você</span>' : ''}</td>
        <td>${u.email}</td>
        <td><span class="badge ${badgeTipo(u.tipo)}">${(u.tipo || '').toUpperCase()}</span></td>
        <td><span class="badge badge-green">Ativo</span></td>
        ${btnExcluir}
      </tr>`;
    }).join('') || `<tr><td colspan="${cols}" style="text-align:center">Nenhum usuário</td></tr>`;
  } catch (e) { console.error('Erro usuários:', e); }
}

function ehAdministrador() {
  const u = currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  return u && u.tipo === 'admin';
}

async function excluirUsuario(id, nome) {
  if (!ehAdministrador()) {
    showToast('Apenas administradores podem excluir usuários', 'warn');
    return;
  }
  const eu = currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  if (eu && String(eu.id) === String(id)) {
    showToast('Você não pode excluir seu próprio usuário', 'error');
    return;
  }
  if (!confirm(`Deseja excluir o usuário "${nome}"?\n\nO acesso será desativado e ele não poderá mais entrar no sistema.`)) return;

  try {
    const res = await fetch('/api/auth/usuarios/' + id, {
      method: 'DELETE',
      headers: apiHeaders()
    });
    const json = await res.json();
    if (json.sucesso) {
      showToast('Usuário excluído com sucesso', 'success');
      carregarEquipe();
      if (typeof carregarDadosParaAgendamento === 'function') carregarDadosParaAgendamento();
    } else {
      showToast(json.mensagem || 'Erro ao excluir usuário', 'error');
    }
  } catch (e) {
    showToast('Erro de conexão ao excluir usuário', 'error');
  }
}

function podeGerenciarUsuarios() {
  const u = currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  return u && (u.tipo === 'admin' || u.tipo === 'medico');
}

function aplicarPermissoesEquipe(user) {
  const u = user || currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  const gerencia = u && (u.tipo === 'admin' || u.tipo === 'medico');
  const acoes = document.getElementById('equipe-acoes-criar');
  const secUsuarios = document.getElementById('secao-usuarios-sistema');
  const formBox = document.getElementById('form-usuario-box');
  const optAdmin = document.getElementById('nu-tipo-admin');
  if (acoes) acoes.style.display = gerencia ? '' : 'none';
  if (secUsuarios) secUsuarios.style.display = gerencia ? '' : 'none';
  if (formBox && !gerencia) formBox.style.display = 'none';
  if (optAdmin) optAdmin.style.display = (u && u.tipo === 'admin') ? '' : 'none';
  if (typeof aplicarPermissoesProntuario === 'function') aplicarPermissoesProntuario(u);
}

function toggleFormUsuario(show) {
  if (!podeGerenciarUsuarios()) {
    showToast('Recepção não pode cadastrar usuários', 'warn');
    return;
  }
  const box = document.getElementById('form-usuario-box');
  if (!box) return;
  const abrir = show !== false && (show === true || box.style.display === 'none');
  box.style.display = abrir ? 'block' : 'none';
  if (abrir && typeof carregarEspecialidades === 'function') carregarEspecialidades();
}

function toggleCamposMedicoUsuario() {
  const tipo = document.getElementById('nu-tipo')?.value;
  const show = tipo === 'medico';
  const crm = document.getElementById('nu-crm-group');
  const esp = document.getElementById('nu-esp-group');
  if (crm) crm.style.display = show ? 'block' : 'none';
  if (esp) esp.style.display = show ? 'block' : 'none';
}

function _estiloAlertaRisco(gravidade) {
  const g = (gravidade || 'LEVE').toUpperCase();
  if (g.includes('CRIT')) return { bg: 'var(--red-light)', badge: 'red', icon: 'alert' };
  if (g === 'GRAVE') return { bg: '#ed8936', badge: 'amber', icon: 'alert' };
  if (g === 'MODERADA') return { bg: 'var(--amber-light)', badge: 'amber', icon: 'doc' };
  return { bg: 'var(--green-light)', badge: 'green', icon: 'doc' };
}

async function carregarNotificacoes() {
  const list = document.getElementById('notifList');
  const dot = document.getElementById('notifDot');
  const title = document.getElementById('notif-panel-title');
  const action = document.getElementById('notif-panel-action');
  if (!list) return;

  const u = currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  if (u && u.tipo === 'paciente') {
    if (title) title.textContent = 'Minhas notificações';
    if (action) action.onclick = marcarTodasNotifPortal;
    list.innerHTML = '<div class="notif-empty">Carregando...</div>';
    try {
      const json = await apiGet('/api/portal/notificacoes');
      const notifs = json.sucesso ? (json.dados || []) : [];
      if (!notifs.length) {
        list.innerHTML = '<div class="notif-empty">Nenhuma notificação no momento.</div>';
        if (dot) dot.style.display = 'none';
        return;
      }
      const naoLidas = json.nao_lidas || 0;
      if (dot) dot.style.display = naoLidas > 0 ? '' : 'none';
      list.innerHTML = notifs.slice(0, 10).map(n => {
        const when = n.data_criacao ? new Date(n.data_criacao).toLocaleString('pt-BR') : '';
        const click = n.tipo === 'exame'
          ? `onclick="showPage('portal_exames'); document.getElementById('notifPanel')?.classList.remove('open'); marcarNotifPortal(${n.id})"`
          : `onclick="showPage('portal_notificacoes'); document.getElementById('notifPanel')?.classList.remove('open'); marcarNotifPortal(${n.id})"`;
        return `<div class="notif-item" ${click} style="${n.lida ? 'opacity:.7' : ''}">
          <div class="notif-icon" style="background:var(--blue-light)"><svg viewBox="0 0 24 24"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/></svg></div>
          <div style="min-width:0;flex:1">
            <div class="notif-text"><strong>${escHtmlChat(n.titulo)}</strong></div>
            <div class="notif-text" style="color:var(--text3);margin-top:2px">${escHtmlChat(n.mensagem)}</div>
            <div class="notif-time">${when}</div>
          </div>
        </div>`;
      }).join('');
    } catch (e) {
      list.innerHTML = '<div class="notif-empty">Erro ao carregar notificações.</div>';
    }
    return;
  }

  if (title) title.textContent = 'Alertas clínicos';
  if (action) action.onclick = marcarNotificacoesLidas;
  list.innerHTML = '<div class="notif-empty">Carregando...</div>';
  try {
    const json = await apiGet('/api/dashboard/alertas');
    const alertas = json.sucesso ? (json.dados || []) : [];
    if (!alertas.length) {
      list.innerHTML = '<div class="notif-empty">Nenhum alerta clínico no momento.</div>';
      if (dot) dot.style.display = 'none';
      return;
    }
    if (dot) dot.style.display = '';
    list.innerHTML = alertas.slice(0, 10).map(a => {
      const est = _estiloAlertaRisco(a.gravidade);
      const icon = est.icon === 'alert'
        ? '<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>'
        : '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>';
      const when = a.data ? new Date(a.data).toLocaleDateString('pt-BR') : 'Recente';
      const click = a.id_paciente && podeAcessarProntuario()
        ? `onclick="abrirProntuario(${a.id_paciente}, ${a.id_consulta || 'null'}); document.getElementById('notifPanel')?.classList.remove('open')"`
        : `onclick="showPage('dashboard'); document.getElementById('notifPanel')?.classList.remove('open')"`;
      return `<div class="notif-item" ${click}>
        <div class="notif-icon" style="background:${est.bg}"><svg viewBox="0 0 24 24">${icon}</svg></div>
        <div style="min-width:0;flex:1">
          <div class="notif-text"><strong>${a.paciente}</strong> <span class="badge badge-${est.badge}" style="margin-left:4px;font-size:10px">${a.tipo || a.gravidade}</span></div>
          <div class="notif-text" style="color:var(--text3);margin-top:2px">${a.descricao || ''}</div>
          <div class="notif-time">${when}</div>
        </div>
      </div>`;
    }).join('');
  } catch (e) {
    list.innerHTML = '<div class="notif-empty">Erro ao carregar alertas.</div>';
    console.error('Erro notificações:', e);
  }
}

function marcarNotificacoesLidas() {
  const u = currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  if (u && u.tipo === 'paciente') {
    marcarTodasNotifPortal();
    return;
  }
  const dot = document.getElementById('notifDot');
  if (dot) dot.style.display = 'none';
  showToast('Alertas marcados como lidos', 'info');
}

function ehPaciente() {
  const u = currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  return u && u.tipo === 'paciente';
}

function aplicarPermissoesPaciente(user) {
  const u = user || currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  const paciente = u && u.tipo === 'paciente';
  const navStaff = document.getElementById('nav-staff');
  const navPaciente = document.getElementById('nav-paciente');
  const search = document.getElementById('topbar-staff-search');
  const btnEquipe = document.getElementById('topbar-btn-equipe');
  if (navStaff) navStaff.style.display = paciente ? 'none' : '';
  if (navPaciente) navPaciente.style.display = paciente ? '' : 'none';
  if (search) search.style.display = paciente ? 'none' : '';
  if (btnEquipe) btnEquipe.style.display = paciente ? 'none' : '';
  if (paciente && u.nome) {
    const el = document.getElementById('portal-nome-paciente');
    if (el) el.textContent = u.nome.split(' ')[0];
    const sbRole = document.getElementById('sidebar-role');
    if (sbRole) sbRole.textContent = 'Portal do Paciente';
  }
}

function fmtDataPortal(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleDateString('pt-BR');
}

function badgeStatusExame(status) {
  const s = (status || '').toUpperCase();
  if (s.includes('DISPON') || s.includes('CONCLU')) return 'badge-green';
  if (s.includes('ANAL') || s.includes('AGUARD')) return 'badge-amber';
  return 'badge-blue';
}

async function atualizarBadgePortalNotif() {
  const badge = document.getElementById('nav-badge-portal-notif');
  const dot = document.getElementById('notifDot');
  if (!ehPaciente()) return;
  try {
    const json = await apiGet('/api/portal/notificacoes/nao-lidas');
    const total = json.sucesso ? (json.total || 0) : 0;
    if (badge) {
      if (total > 0) {
        badge.textContent = total > 99 ? '99+' : String(total);
        badge.style.display = '';
      } else {
        badge.style.display = 'none';
      }
    }
    if (dot) dot.style.display = total > 0 ? '' : 'none';
  } catch (e) { /* ignore */ }
}

async function carregarPortalInicio() {
  if (!ehPaciente()) return;
  try {
    const [exames, consultas, notifs] = await Promise.all([
      apiGet('/api/portal/exames'),
      apiGet('/api/portal/consultas'),
      apiGet('/api/portal/notificacoes'),
    ]);
    const elEx = document.getElementById('portal-resumo-exames');
    const elCon = document.getElementById('portal-resumo-consultas');
    const elNot = document.getElementById('portal-resumo-notif');
    if (elEx) elEx.textContent = exames.total ?? (exames.dados || []).length;
    if (elCon) elCon.textContent = consultas.total ?? (consultas.dados || []).length;
    if (elNot) elNot.textContent = notifs.nao_lidas ?? 0;

    const box = document.getElementById('portal-inicio-notifs');
    const lista = notifs.dados || [];
    if (box) {
      box.innerHTML = lista.length
        ? lista.slice(0, 5).map(n => `
          <div style="padding:12px 16px;border-bottom:1px solid var(--border);${n.lida ? 'opacity:.75' : ''}">
            <strong>${escHtmlChat(n.titulo)}</strong>
            <div style="font-size:13px;color:var(--text3);margin-top:4px">${escHtmlChat(n.mensagem)}</div>
          </div>`).join('')
        : '<div style="padding:16px;color:#999;text-align:center">Nenhuma notificação</div>';
    }
    atualizarBadgePortalNotif();
  } catch (e) {
    console.error('Erro portal inicio:', e);
  }
}

async function carregarPortalExames() {
  const tbody = document.querySelector('#tabela-portal-exames tbody');
  if (!tbody) return;
  try {
    const json = await apiGet('/api/portal/exames');
    const exames = json.dados || [];
    tbody.innerHTML = exames.length
      ? exames.map(e => `<tr>
          <td class="td-name">${escHtmlChat(e.nome_exame)}</td>
          <td>${escHtmlChat(e.medico)}</td>
          <td>${fmtDataPortal(e.data_solicitacao)}</td>
          <td><span class="badge ${badgeStatusExame(e.status)}">${escHtmlChat(e.status)}</span></td>
          <td style="max-width:280px">${e.tem_resultado ? escHtmlChat(e.resultado || e.laudo || 'Disponível') : '<span style="color:#999">Aguardando</span>'}</td>
        </tr>`).join('')
      : '<tr><td colspan="5" style="text-align:center;color:#999">Nenhum exame registrado</td></tr>';
  } catch (e) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#999">Erro ao carregar</td></tr>';
  }
}

async function carregarPortalProntuario() {
  const lista = document.getElementById('portal-lista-consultas');
  if (!lista) return;
  try {
    const json = await apiGet('/api/portal/prontuario');
    const consultas = json.dados || [];
    lista.innerHTML = consultas.length
      ? consultas.map(c => `
        <div style="padding:12px 16px;border-bottom:1px solid var(--border);cursor:pointer" onclick="verProntuarioPortal(${c.id})">
          <strong>${escHtmlChat(c.data)} ${escHtmlChat(c.hora)}</strong>
          <div style="font-size:13px;color:var(--text3)">${escHtmlChat(c.medico)} · ${escHtmlChat(c.motivo || c.tipo_consulta || '')}</div>
          <span class="badge badge-blue" style="margin-top:4px">${escHtmlChat(c.status)}</span>
        </div>`).join('')
      : '<div style="padding:16px;color:#999;text-align:center">Nenhuma consulta no prontuário</div>';
    if (consultas.length) verProntuarioPortal(consultas[0].id);
  } catch (e) {
    lista.innerHTML = '<div style="padding:16px;color:#999;text-align:center">Erro ao carregar</div>';
  }
}

async function verProntuarioPortal(idConsulta) {
  const body = document.getElementById('portal-prontuario-body');
  if (!body) return;
  body.innerHTML = '<div style="padding:20px;color:#999;text-align:center">Carregando...</div>';
  try {
    const json = await apiGet('/api/portal/prontuario/' + idConsulta);
    const c = json.dados;
    if (!json.sucesso || !c) {
      body.innerHTML = '<div style="padding:20px;color:#999">Consulta não encontrada</div>';
      return;
    }
    const diag = (c.diagnosticos || []).map(d =>
      `<li><strong>${escHtmlChat(d.cid)}</strong> — ${escHtmlChat(d.descricao)}</li>`).join('') || '<li>Nenhum diagnóstico registrado</li>';
    const exames = (c.exames || []).map(e =>
      `<li>${escHtmlChat(e.nome_exame)} — <span class="badge ${badgeStatusExame(e.status)}">${escHtmlChat(e.status)}</span>${e.resultado ? ': ' + escHtmlChat(e.resultado) : ''}</li>`).join('') || '<li>Nenhum exame nesta consulta</li>';
    const sv = c.sinais_vitais || {};
    body.innerHTML = `
      <div style="padding:16px">
        <h3 style="margin:0 0 8px">${escHtmlChat(c.data)} · ${escHtmlChat(c.medico)}</h3>
        <p style="color:var(--text3);margin:0 0 16px">${escHtmlChat(c.especialidade)} · ${escHtmlChat(c.tipo_consulta || '')}</p>
        ${c.queixa_principal ? `<p><strong>Queixa:</strong> ${escHtmlChat(c.queixa_principal)}</p>` : ''}
        ${c.plano_terapeutico ? `<p><strong>Orientações:</strong> ${escHtmlChat(c.plano_terapeutico)}</p>` : ''}
        ${Object.keys(sv).length ? `<p><strong>Sinais vitais:</strong> PA ${escHtmlChat(sv.pressao_arterial || '—')} · FC ${sv.frequencia_cardiaca || '—'} · Temp ${sv.temperatura || '—'}°C</p>` : ''}
        <p><strong>Diagnósticos</strong></p><ul>${diag}</ul>
        <p><strong>Exames</strong></p><ul>${exames}</ul>
      </div>`;
  } catch (e) {
    body.innerHTML = '<div style="padding:20px;color:#999">Erro ao carregar prontuário</div>';
  }
}

async function carregarPortalNotificacoes() {
  const box = document.getElementById('portal-lista-notificacoes');
  if (!box) return;
  try {
    const json = await apiGet('/api/portal/notificacoes');
    const notifs = json.dados || [];
    box.innerHTML = notifs.length
      ? notifs.map(n => `
        <div style="padding:14px 16px;border-bottom:1px solid var(--border);${n.lida ? 'opacity:.7' : ''}">
          <div style="display:flex;justify-content:space-between;gap:8px">
            <strong>${escHtmlChat(n.titulo)}</strong>
            ${!n.lida ? `<button type="button" class="btn btn-ghost btn-sm" onclick="marcarNotifPortal(${n.id})">Marcar lida</button>` : ''}
          </div>
          <div style="font-size:13px;margin-top:6px">${escHtmlChat(n.mensagem)}</div>
          <div style="font-size:11px;color:#aaa;margin-top:4px">${n.data_criacao ? new Date(n.data_criacao).toLocaleString('pt-BR') : ''}</div>
        </div>`).join('')
      : '<div style="padding:16px;color:#999;text-align:center">Nenhuma notificação</div>';
    atualizarBadgePortalNotif();
  } catch (e) {
    box.innerHTML = '<div style="padding:16px;color:#999;text-align:center">Erro ao carregar</div>';
  }
}

async function marcarNotifPortal(id) {
  try {
    await fetch('/api/portal/notificacoes/' + id + '/lida', { method: 'PUT', headers: apiHeaders() });
    carregarPortalNotificacoes();
    carregarPortalInicio();
    carregarNotificacoes();
    atualizarBadgePortalNotif();
  } catch (e) { showToast('Erro ao marcar notificação', 'error'); }
}

async function marcarTodasNotifPortal() {
  try {
    await fetch('/api/portal/notificacoes/marcar-todas', { method: 'PUT', headers: apiHeaders() });
    showToast('Notificações marcadas como lidas', 'info');
    carregarPortalNotificacoes();
    carregarPortalInicio();
    carregarNotificacoes();
    atualizarBadgePortalNotif();
  } catch (e) { showToast('Erro ao marcar notificações', 'error'); }
}

window.aplicarPermissoesPaciente = aplicarPermissoesPaciente;
window.carregarPortalInicio = carregarPortalInicio;
window.carregarPortalExames = carregarPortalExames;
window.carregarPortalProntuario = carregarPortalProntuario;
window.carregarPortalNotificacoes = carregarPortalNotificacoes;
window.verProntuarioPortal = verProntuarioPortal;
window.marcarNotifPortal = marcarNotifPortal;
window.marcarTodasNotifPortal = marcarTodasNotifPortal;
window.atualizarBadgePortalNotif = atualizarBadgePortalNotif;

window.aplicarPermissoesEquipe = aplicarPermissoesEquipe;
window.toggleFormUsuario = toggleFormUsuario;
window.toggleCamposMedicoUsuario = toggleCamposMedicoUsuario;
window.carregarNotificacoes = carregarNotificacoes;
window.marcarNotificacoesLidas = marcarNotificacoesLidas;
window.podeGerenciarUsuarios = podeGerenciarUsuarios;
window.excluirUsuario = excluirUsuario;
window.ehAdministrador = ehAdministrador;

let chatAtualId = null;

function iniciaisChat(nome) {
  if (!nome) return '??';
  const partes = nome.trim().split(/\s+/).filter(Boolean);
  if (!partes.length) return '??';
  if (partes.length === 1) return partes[0].slice(0, 2).toUpperCase();
  return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase();
}

function escHtmlChat(texto) {
  return String(texto || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function fmtHoraChat(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

async function atualizarBadgeMensagens(total) {
  const badge = document.getElementById('nav-badge-mensagens');
  if (!badge) return;
  try {
    if (total === undefined || total === null) {
      const json = await apiGet('/api/mensagens/nao-lidas');
      total = json.sucesso ? (json.total || 0) : 0;
    }
    if (total > 0) {
      badge.textContent = total > 99 ? '99+' : String(total);
      badge.style.display = '';
    } else {
      badge.style.display = 'none';
    }
  } catch (e) {
    badge.style.display = 'none';
  }
}

async function carregarContatosChat() {
  const sel = document.getElementById('chat-destinatario');
  if (!sel) return;
  try {
    const json = await apiGet('/api/mensagens/contatos');
    if (!json.sucesso) return;
    const uid = Number(currentUser?.id);
    sel.innerHTML = '<option value="">Selecione um colega...</option>' +
      (json.dados || [])
        .filter(u => Number(u.id) !== uid)
        .map(u => {
          const perfil = u.tipo === 'medico' ? 'Médico' : u.tipo === 'recepcao' ? 'Recepção' : u.tipo === 'admin' ? 'Admin' : u.tipo;
          return `<option value="${u.id}">${escHtmlChat(u.nome)} (${perfil})</option>`;
        }).join('');
  } catch (e) {
    console.error('Erro contatos chat:', e);
  }
}

function toggleNovaConversa() {
  const wrap = document.getElementById('chat-nova-wrap');
  if (!wrap) return;
  const abrir = wrap.style.display === 'none';
  wrap.style.display = abrir ? 'block' : 'none';
  if (abrir) carregarContatosChat();
}

async function iniciarNovaConversa() {
  const sel = document.getElementById('chat-destinatario');
  if (!sel || !sel.value) {
    showToast('Selecione um colega para conversar', 'warn');
    return;
  }
  const nome = sel.options[sel.selectedIndex].text.replace(/\s*\([^)]*\)$/, '');
  await selectChat(parseInt(sel.value, 10), nome);
  const wrap = document.getElementById('chat-nova-wrap');
  if (wrap) wrap.style.display = 'none';
}

async function carregarMensagens() {
  try {
    const json = await apiGet('/api/mensagens');
    const lista = document.getElementById('chat-list');
    if (!lista) return;
    if (!json.sucesso) {
      lista.innerHTML = '<div style="padding:16px;color:#999;text-align:center">Erro ao carregar conversas</div>';
      return;
    }

    const conversas = json.conversas || [];
    lista.innerHTML = conversas.length
      ? conversas.map(c => {
          const badge = c.nao_lidas > 0
            ? `<span style="float:right;background:var(--blue-mid);color:#fff;font-size:11px;padding:2px 7px;border-radius:10px">${c.nao_lidas}</span>`
            : '';
          return `<div class="chat-list-item" style="padding:10px 14px;border-bottom:1px solid var(--border);cursor:pointer" onclick="selectChat(${c.id},'${escHtmlChat(c.nome).replace(/'/g, "\\'")}')">
            <strong>${escHtmlChat(c.nome)}</strong>${badge}
            <br><small style="color:#888">${escHtmlChat(c.ultima_mensagem || c.ultimas_mensagens?.[0] || '')}</small>
            <br><small style="color:#aaa">${escHtmlChat(c.ultimo_envio || '')}</small>
          </div>`;
        }).join('')
      : '<div style="padding:16px;color:#999;text-align:center">Nenhuma conversa ainda.<br>Use <strong>+ Nova</strong> para iniciar.</div>';

    await atualizarBadgeMensagens(json.total_nao_lidas);
    await carregarContatosChat();
  } catch (e) {
    console.error('Erro mensagens:', e);
  }
}

async function selectChat(usuarioId, nome) {
  chatAtualId = usuarioId;
  const titulo = document.getElementById('chat-header-name');
  const sub = document.getElementById('chat-header-sub');
  const avatar = document.getElementById('chat-header-avatar');
  const input = document.getElementById('msg-input');
  if (titulo) titulo.textContent = nome || 'Conversa';
  if (sub) sub.textContent = 'Conversa interna';
  if (avatar) avatar.textContent = iniciaisChat(nome);
  if (input) {
    input.disabled = false;
    input.focus();
  }

  try {
    const json = await apiGet('/api/mensagens/' + usuarioId);
    const area = document.getElementById('chat-body');
    if (!area || !json.sucesso) return;
    const uid = Number(currentUser?.id);
    area.innerHTML = (json.mensagens || []).map(m => {
      const sent = Number(m.id_remetente) === uid;
      return `<div style="margin:8px 0;text-align:${sent ? 'right' : 'left'}">
        <span style="display:inline-block;max-width:85%;padding:8px 12px;border-radius:10px;background:${sent ? 'var(--blue-mid)' : 'var(--surface2)'};${sent ? 'color:#fff;' : ''}">${escHtmlChat(m.conteudo)}</span>
        <div style="font-size:11px;color:#aaa;margin-top:2px;${sent ? 'text-align:right' : ''}">${fmtHoraChat(m.data_envio)}</div>
      </div>`;
    }).join('') || '<div style="color:#999;text-align:center;padding:20px">Inicie a conversa enviando uma mensagem</div>';
    area.scrollTop = area.scrollHeight;
    carregarMensagens();
    atualizarBadgeMensagens();
  } catch (e) {
    console.error('Erro conversa:', e);
  }
}

async function sendMsg() {
  const input = document.getElementById('msg-input');
  if (!input || !chatAtualId) {
    showToast('Selecione ou inicie uma conversa', 'warn');
    return;
  }
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
      showToast(json.erro || json.mensagem || 'Erro ao enviar', 'error');
    }
  } catch (e) {
    showToast('Erro de conexão', 'error');
  }
}

window.carregarMensagens = carregarMensagens;
window.selectChat = selectChat;
window.sendMsg = sendMsg;
window.toggleNovaConversa = toggleNovaConversa;
window.iniciarNovaConversa = iniciarNovaConversa;
window.atualizarBadgeMensagens = atualizarBadgeMensagens;

async function agendarConsultaModal() {
  const pacId = document.getElementById('nc-pac')?.value;
  const medId = document.getElementById('nc-med')?.value;
  const data = document.getElementById('nc-data')?.value;
  const hora = document.getElementById('nc-hora')?.value;
  const motivo = document.getElementById('nc-motivo')?.value?.trim();
  const tipo = document.getElementById('nc-tipo')?.value || '1ª Consulta';
  const convenio = document.getElementById('nc-convenio')?.value || 'Particular';
  const obs = document.getElementById('nc-obs')?.value?.trim();
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
        motivo,
        tipo_consulta: tipo,
        convenio,
        observacoes: obs || null
      })
    });
    const json = await res.json();
    if (json.sucesso) {
      closeModal('modal-consulta');
      let msg = json.mensagem || 'Consulta agendada com sucesso!';
      if (json.aviso_preco) msg += ' (' + json.aviso_preco + ')';
      showToast(msg, json.receita ? 'success' : 'warn');
      if (typeof carregarDashboard === 'function') carregarDashboard();
      if (typeof carregarConsultas === 'function') carregarConsultas();
      if (typeof carregarAgendaSemanal === 'function') carregarAgendaSemanal();
    } else {
      showToast(json.mensagem || 'Falha ao agendar', 'error');
    }
  } catch (e) { showToast('Erro de conexão', 'error'); }
}

async function atualizarPreviewPrecoAgendamento() {
  const tipo = document.getElementById('nc-tipo')?.value || '1ª Consulta';
  const convenio = document.getElementById('nc-convenio')?.value || 'Particular';
  const el = document.getElementById('nc-preco-valor');
  if (!el) return;
  el.textContent = 'Consultando...';
  try {
    const q = new URLSearchParams({ tipo_consulta: tipo, convenio });
    const json = await apiGet('/api/financeiro/precos/consultar?' + q.toString());
    if (json.sucesso && json.preco) {
      el.textContent = fmtMoeda(json.preco.valor) + ' (' + (json.preco.modalidade === 'Particular' ? 'Particular' : json.preco.nome_convenio) + ')';
      el.style.color = 'var(--green-light)';
    } else {
      el.textContent = 'Preço não cadastrado — cadastre em Financeiro';
      el.style.color = 'var(--amber-light)';
    }
  } catch (e) {
    el.textContent = '—';
    el.style.color = '';
  }
}

window.atualizarPreviewPrecoAgendamento = atualizarPreviewPrecoAgendamento;
window.agendarConsultaModal = agendarConsultaModal;
window.carregarHorariosDisponiveis = carregarHorariosDisponiveis;
window.selecionarHoraAgendamento = selecionarHoraAgendamento;
window.verAgendamento = verAgendamento;
window.fecharAgendamentoAbrirProntuario = fecharAgendamentoAbrirProntuario;
window.fecharAgendamentoVerConsultas = fecharAgendamentoVerConsultas;

// ══════════════════════════════════════
// PRONTUÁRIO ELETRÔNICO (médico/admin)
// ══════════════════════════════════════
let _prontPacienteId = null;
let _prontConsultaId = null;

function podeAcessarProntuario() {
  const u = currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  return u && (u.tipo === 'admin' || u.tipo === 'medico');
}

function aplicarPermissoesProntuario(user) {
  const u = user || currentUser || JSON.parse(localStorage.getItem('usuario') || 'null');
  const pode = u && (u.tipo === 'admin' || u.tipo === 'medico');
  const nav = document.getElementById('nav-prontuario');
  if (nav) nav.style.display = pode ? '' : 'none';
  document.querySelectorAll('.btn-prontuario').forEach(btn => {
    btn.style.display = pode ? '' : 'none';
  });
}

function _popularSelectPacientes(selectEl, pacientes, placeholder) {
  if (!selectEl) return;
  selectEl.innerHTML = `<option value="">${placeholder}</option>`;
  (pacientes || []).forEach(p => {
    const id = p.id || p.id_paciente;
    selectEl.innerHTML += `<option value="${id}">${p.nome} (CPF: ${_fmtCpf(p.cpf)})</option>`;
  });
}

async function _carregarPacientesParaSelect(selectIds) {
  try {
    const json = await apiGet('/api/pacientes?por_pagina=500');
    if (!json.sucesso) return;
    const lista = json.dados || [];
    selectIds.forEach(id => _popularSelectPacientes(document.getElementById(id), lista, 'Selecione o paciente...'));
  } catch (e) {
    console.error('Erro ao carregar pacientes:', e);
  }
}

function _coletarMedicamentosPagina() {
  return Array.from(document.querySelectorAll('#med-list .rx-item')).map(item => ({
    medicamento: item.querySelector('.rx-med-nome')?.value?.trim() || '',
    posologia: item.querySelector('.rx-med-pos')?.value?.trim() || '',
    duracao: item.querySelector('.rx-med-dur')?.value?.trim() || '',
  })).filter(m => m.medicamento);
}

function _badgeTipoReceita(tipo) {
  if (!tipo) return '<span class="badge badge-blue">Simples</span>';
  if (tipo.includes('Azul')) return '<span class="badge badge-amber">C. Azul</span>';
  if (tipo.includes('Amarela')) return '<span class="badge badge-amber">C. Amarela</span>';
  return '<span class="badge badge-blue">Simples</span>';
}

async function carregarPrescricoes() {
  await _carregarPacientesParaSelect(['rx-paciente-select', 'rx-modal-paciente']);
  await carregarHistoricoPrescricoes();
  _vincularBotoesPrescricao();
}

function _vincularBotoesPrescricao() {
  const btnGerar = document.getElementById('btn-gerar-receita');
  if (btnGerar && !btnGerar.dataset.bound) {
    btnGerar.dataset.bound = '1';
    btnGerar.addEventListener('click', (e) => {
      e.preventDefault();
      emitirReceita(false);
    });
  }
  const btnModal = document.getElementById('btn-modal-gerar-receita');
  if (btnModal && !btnModal.dataset.bound) {
    btnModal.dataset.bound = '1';
    btnModal.addEventListener('click', (e) => {
      e.preventDefault();
      emitirReceita(true);
    });
  }
}

async function carregarHistoricoPrescricoes() {
  const tbody = document.getElementById('rx-historico-tbody');
  if (!tbody) return;
  try {
    const json = await apiGet('/api/prescricoes');
    if (!json.sucesso || !json.dados?.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-sm text-3">Nenhuma receita emitida ainda.</td></tr>';
      return;
    }
    tbody.innerHTML = json.dados.map(p => `
      <tr>
        <td class="td-mono">${p.numero || ('R' + String(p.id).padStart(4, '0'))}</td>
        <td class="td-name">${p.paciente_nome || '—'}</td>
        <td class="td-mono">${p.data_fmt || '—'}</td>
        <td>${p.medicamento || '—'}</td>
        <td>${_badgeTipoReceita(p.tipo_receita)}</td>
        <td><button type="button" class="btn btn-ghost btn-sm" title="Baixar PDF" onclick="reimprimirReceita(${p.id})">PDF</button></td>
      </tr>
    `).join('');
  } catch (e) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-sm text-3">Erro ao carregar histórico.</td></tr>';
  }
}

function _pdfDisponivel() {
  return !!(window.jspdf && window.jspdf.jsPDF);
}

function _autoTableDisponivel(doc) {
  return doc && typeof doc.autoTable === 'function';
}

function gerarReceitaPDF(receita) {
  try {
    if (!_pdfDisponivel()) {
      showToast('Biblioteca PDF indisponivel. Recarregue a pagina.', 'error');
      return false;
    }
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    if (!_autoTableDisponivel(doc)) {
      showToast('Plugin de tabela PDF nao carregou. Recarregue a pagina.', 'error');
      return false;
    }

    doc.setFontSize(18);
    doc.setTextColor(26, 86, 219);
    doc.text('MedSystem PRO — Receituario', 14, 20);
    doc.setFontSize(11);
    doc.setTextColor(90, 90, 90);
    doc.text('Tipo: ' + (receita.tipo_receita || 'Simples'), 14, 28);
    doc.text('Gerado em: ' + new Date().toLocaleString('pt-BR'), 14, 34);

    let y = 42;

    y = _autoTabelaProntuario(doc, y, ['Campo', 'Paciente'], _linhasProntuario([
      ['Numero', receita.numero],
      ['Paciente', receita.paciente],
      ['CPF', receita.cpf],
      ['Data', receita.data],
      ['Tipo de Receita', receita.tipo_receita],
    ]));

    const meds = receita.medicamentos || [];
    if (meds.length) {
      doc.autoTable({
        startY: y,
        head: [['Medicamento', 'Posologia', 'Duracao']],
        body: meds.map(m => {
          let pos = m.posologia || '—';
          if (m.quantidade) pos += (pos !== '—' ? ' · ' : '') + 'Qtd: ' + m.quantidade;
          return [m.medicamento || '—', pos, m.duracao || '—'];
        }),
        theme: 'striped',
        headStyles: { fillColor: [37, 99, 235] },
        styles: { fontSize: 10, overflow: 'linebreak' },
        margin: { left: 14, right: 14 },
      });
      y = doc.lastAutoTable.finalY + 8;
    }

    if (receita.orientacoes) {
      doc.autoTable({
        startY: y,
        head: [['Orientacoes ao Paciente']],
        body: [[receita.orientacoes]],
        theme: 'striped',
        headStyles: { fillColor: [37, 99, 235] },
        styles: { fontSize: 10, overflow: 'linebreak' },
        margin: { left: 14, right: 14 },
      });
      y = doc.lastAutoTable.finalY + 8;
    }

    const crmEsp = [
      receita.crm ? 'CRM ' + receita.crm : '',
      receita.especialidade || 'Clinica Geral',
    ].filter(Boolean).join(' · ');
    _autoTabelaProntuario(doc, y, ['Medico', 'CRM / Especialidade'], [
      [receita.medico || '—', crmEsp || '—'],
    ]);

    const slug = (receita.paciente || 'paciente')
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^\w]+/g, '-').toLowerCase().replace(/^-|-$/g, '').slice(0, 30);
    const nomeArquivo = (receita.numero || 'receita').toLowerCase() + '-' + (slug || 'paciente') + '.pdf';
    doc.save(nomeArquivo);
    showToast('Receita gerada e PDF baixado!', 'success');
    return true;
  } catch (err) {
    console.error('gerarReceitaPDF:', err);
    showToast('Erro ao gerar PDF: ' + (err.message || 'falha desconhecida'), 'error');
    return false;
  }
}

function imprimirReceita(receita) {
  return gerarReceitaPDF(receita);
}

function _coletarDadosReceita(modal) {
  if (modal) {
    const med = document.getElementById('rx-modal-med')?.value?.trim();
    if (!med) return null;
    return {
      id_paciente: document.getElementById('rx-modal-paciente')?.value,
      tipo: document.getElementById('rx-modal-tipo')?.value,
      orientacoes: document.getElementById('rx-modal-orient')?.value?.trim() || '',
      medicamentos: [{
        medicamento: med,
        posologia: document.getElementById('rx-modal-pos')?.value?.trim() || '',
        duracao: document.getElementById('rx-modal-dur')?.value?.trim() || '',
        quantidade: document.getElementById('rx-modal-qtd')?.value?.trim() || null,
      }],
    };
  }
  return {
    id_paciente: document.getElementById('rx-paciente-select')?.value,
    tipo: document.getElementById('rx-tipo-select')?.value,
    orientacoes: document.getElementById('rx-orientacoes')?.value?.trim() || '',
    medicamentos: _coletarMedicamentosPagina(),
  };
}

async function _salvarReceita(gerarPdf, modal) {
  const dados = _coletarDadosReceita(modal);
  if (!dados) { showToast('Informe o medicamento', 'warn'); return; }
  if (!dados.id_paciente) { showToast('Selecione um paciente', 'warn'); return; }
  if (!dados.medicamentos.length) { showToast('Informe ao menos um medicamento', 'warn'); return; }

  const btnId = modal ? 'btn-modal-gerar-receita' : 'btn-gerar-receita';
  const btn = document.getElementById(btnId);
  const labelOriginal = btn ? btn.innerHTML : '';
  if (btn) { btn.disabled = true; btn.textContent = 'Gerando...'; }

  try {
    const json = await apiPost('/api/prescricoes', {
      id_paciente: parseInt(dados.id_paciente, 10),
      tipo_receita: dados.tipo,
      orientacoes: dados.orientacoes,
      medicamentos: dados.medicamentos,
    });
    if (!json.sucesso) {
      showToast(json.mensagem || 'Erro ao emitir receita', 'error');
      return;
    }
    if (modal) closeModal('modal-prescricao');
    if (gerarPdf) {
      if (json.receita) {
        const ok = imprimirReceita(json.receita);
        if (!ok) showToast('Receita salva, mas o PDF nao foi gerado.', 'warn');
      } else {
        showToast('Receita salva, mas dados do PDF indisponiveis.', 'warn');
      }
    } else {
      showToast('Receita salva com sucesso!', 'success');
    }
    await carregarHistoricoPrescricoes();
  } catch (e) {
    console.error('emitir receita:', e);
    showToast('Erro de conexao ao emitir receita', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = labelOriginal; }
  }
}

async function emitirReceita(modal) {
  if (typeof emitirReceita._busy !== 'undefined' && emitirReceita._busy) return;
  emitirReceita._busy = true;
  try {
    await _salvarReceita(true, !!modal);
  } finally {
    emitirReceita._busy = false;
  }
}

async function salvarRascunhoReceita(modal) {
  return _salvarReceita(false, !!modal);
}

async function reimprimirReceita(idPrescricao) {
  try {
    const json = await apiGet('/api/prescricoes/' + idPrescricao + '/receita');
    if (!json.sucesso || !json.receita) {
      showToast(json.mensagem || 'Nao foi possivel carregar a receita', 'error');
      return;
    }
    imprimirReceita(json.receita);
  } catch (e) {
    showToast('Erro ao gerar PDF da receita', 'error');
  }
}

function _fmtCpf(cpf) {
  const s = (cpf || '').replace(/\D/g, '');
  if (s.length === 11) return s.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  return cpf || '—';
}

function _calcIdade(dataNasc) {
  if (!dataNasc) return '—';
  const n = new Date(dataNasc);
  const hoje = new Date();
  let idade = hoje.getFullYear() - n.getFullYear();
  const m = hoje.getMonth() - n.getMonth();
  if (m < 0 || (m === 0 && hoje.getDate() < n.getDate())) idade--;
  return idade + ' anos';
}

function _mostrarBloqueioProntuario() {
  showPage('prontuario');
  const bloq = document.getElementById('pront-bloqueado');
  const cont = document.getElementById('pront-conteudo');
  if (bloq) bloq.style.display = '';
  if (cont) cont.style.display = 'none';
}

function _mostrarConteudoProntuario() {
  const bloq = document.getElementById('pront-bloqueado');
  const cont = document.getElementById('pront-conteudo');
  if (bloq) bloq.style.display = 'none';
  if (cont) cont.style.display = '';
}

function abrirProntuarioInicio() {
  if (!podeAcessarProntuario()) {
    _mostrarBloqueioProntuario();
    return;
  }
  _mostrarConteudoProntuario();
  showPage('prontuario');
  _prontPacienteId = null;
  _prontConsultaId = null;
  document.getElementById('pront-area-clinica').style.display = 'none';
  document.getElementById('pront-bar-selecao').style.display = '';
  document.getElementById('pront-consulta-wrap').style.display = 'none';
  document.getElementById('pront-subtitulo').textContent = 'Selecione um paciente para abrir o prontuário';
  carregarListaPacientesProntuario();
}

async function carregarListaPacientesProntuario() {
  const sel = document.getElementById('pront-paciente-select');
  if (!sel) return;
  try {
    const json = await apiGet('/api/pacientes?por_pagina=500');
    if (!json.sucesso) return;
    sel.innerHTML = '<option value="">Selecione o paciente...</option>';
    (json.dados || []).forEach(p => {
      const id = p.id || p.id_paciente;
      sel.innerHTML += `<option value="${id}">${p.nome} (CPF: ${_fmtCpf(p.cpf)})</option>`;
    });
  } catch (e) { console.error('Erro pacientes prontuário:', e); }
}

async function selecionarPacienteProntuario() {
  const id = document.getElementById('pront-paciente-select')?.value;
  if (!id) { showToast('Selecione um paciente', 'warn'); return; }
  await abrirProntuario(parseInt(id));
}

async function abrirProntuario(idPaciente, idConsulta) {
  if (!podeAcessarProntuario()) {
    showToast('Prontuário disponível apenas para médicos', 'error');
    return;
  }

  idPaciente = parseInt(idPaciente, 10);
  idConsulta = idConsulta ? parseInt(idConsulta, 10) : null;

  if (!idPaciente || Number.isNaN(idPaciente)) {
    showToast('Paciente inválido', 'error');
    return;
  }

  _mostrarConteudoProntuario();
  showPage('prontuario');
  _prontPacienteId = idPaciente;
  document.getElementById('pront-bar-selecao').style.display = 'none';
  document.getElementById('pront-area-clinica').style.display = 'none';
  document.getElementById('pront-consulta-wrap').style.display = 'none';
  document.getElementById('pront-subtitulo').textContent = 'Carregando prontuário...';

  try {
    const json = await apiGet('/api/prontuarios/paciente/' + idPaciente);
    if (!json.sucesso) {
      showToast(json.mensagem || 'Erro ao carregar consultas', 'error');
      document.getElementById('pront-bar-selecao').style.display = '';
      document.getElementById('pront-subtitulo').textContent = 'Selecione um paciente e uma consulta';
      return;
    }

    const consultas = json.consultas || [];
    if (!consultas.length) {
      document.getElementById('pront-area-clinica').style.display = 'none';
      document.getElementById('pront-bar-selecao').style.display = '';
      document.getElementById('pront-consulta-wrap').style.display = 'none';
      document.getElementById('pront-subtitulo').textContent = 'Paciente sem consultas ativas';
      showToast('Este paciente não possui consultas para abrir prontuário', 'warn');
      return;
    }

    const sel = document.getElementById('pront-consulta-select');
    sel.innerHTML = consultas.map(c =>
      `<option value="${c.id}">${c.data} ${c.hora} — ${c.motivo} (${c.status})</option>`
    ).join('');

    const idEscolhida = idConsulta && consultas.some(c => c.id === idConsulta)
      ? idConsulta
      : consultas[0].id;
    sel.value = idEscolhida;
    await carregarProntuarioConsulta(idEscolhida);
  } catch (e) {
    console.error('Erro abrir prontuário:', e);
    showToast('Erro ao abrir prontuário', 'error');
    document.getElementById('pront-bar-selecao').style.display = '';
    document.getElementById('pront-subtitulo').textContent = 'Selecione um paciente e uma consulta';
  }
}

async function trocarConsultaProntuario() {
  const id = parseInt(document.getElementById('pront-consulta-select')?.value);
  if (id) await carregarProntuarioConsulta(id);
}

function _classeVital(boxId, valor, tipo) {
  const box = document.getElementById(boxId);
  if (!box) return;
  box.classList.remove('vital-ok', 'vital-warn', 'vital-alert', 'vital-norm');
  if (valor === '' || valor == null) { box.classList.add('vital-norm'); return; }
  const v = parseFloat(valor);
  if (tipo === 'temp') {
    box.classList.add(v >= 38 ? 'vital-alert' : v >= 37.5 ? 'vital-warn' : 'vital-ok');
  } else if (tipo === 'spo2') {
    box.classList.add(v < 92 ? 'vital-alert' : v < 95 ? 'vital-warn' : 'vital-ok');
  } else if (tipo === 'fc') {
    box.classList.add(v > 100 || v < 50 ? 'vital-warn' : 'vital-ok');
  } else {
    box.classList.add('vital-ok');
  }
}

function _renderExameChip(nome, status) {
  return `<div class="chip"><svg viewBox="0 0 24 24" style="width:13px;height:13px;stroke:var(--text3);fill:none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/></svg>${nome}${status ? ' <span class="badge badge-blue">' + status + '</span>' : ''}</div>`;
}

async function carregarProntuarioConsulta(idConsulta) {
  _prontConsultaId = idConsulta;
  try {
    const res = await fetch('/api/prontuarios/' + idConsulta, { headers: apiHeaders() });
    const json = await res.json();
    if (!res.ok || !json.sucesso) {
      showToast(json.mensagem || json.erro || 'Erro ao carregar prontuário', 'error');
      return;
    }

    document.getElementById('pront-area-clinica').style.display = '';
    document.getElementById('pront-consulta-wrap').style.display = '';
    const c = json.consulta || {};
    const p = json.paciente || {};

    document.getElementById('pront-subtitulo').textContent =
      'Consulta #' + String(c.id).padStart(4, '0') + ' · ' + (c.paciente || p.nome || '') + ' · ' + c.data + (c.hora ? ' ' + c.hora : '');

    const nome = c.paciente || p.nome || 'Paciente';
    document.querySelector('#page-prontuario .pront-nome').textContent = nome;
    document.querySelector('#page-prontuario .pront-avatar').textContent = nome.substring(0, 2).toUpperCase();
    document.getElementById('pront-cpf').textContent = _fmtCpf(p.cpf);
    document.getElementById('pront-idade').textContent = _calcIdade(p.data_nascimento);
    document.getElementById('pront-tel').textContent =
      typeof formatarTelefone === 'function' ? formatarTelefone(p.telefone) : (p.telefone || '—');
    document.getElementById('pront-alergias').innerHTML = p.alergias
      ? '<span class="allergy-tag">⚠ ' + p.alergias + '</span>'
      : '';

    document.getElementById('pront-queixa').value = c.queixa_principal || c.motivo || '';
    document.getElementById('pront-hma').value = c.historia_molestia_atual || '';
    document.getElementById('pront-ap').value = c.antecedentes_pessoais || '';
    document.getElementById('pront-af').value = c.antecedentes_familiares || '';
    document.getElementById('pront-exame-fisico').value = c.exame_fisico || '';
    document.getElementById('pront-hipotese').value = c.hipotese_diagnostica || '';
    document.getElementById('pront-plano').value = c.plano_terapeutico || '';

    const sv = json.sinais_vitais || {};
    document.getElementById('pront-pa').value = sv.pressao_arterial || '';
    document.getElementById('pront-fc').value = sv.frequencia_cardiaca || '';
    document.getElementById('pront-temp').value = sv.temperatura || '';
    document.getElementById('pront-spo2').value = sv.saturacao_oxigenio || '';
    document.getElementById('pront-peso').value = sv.peso || '';
    document.getElementById('pront-fr').value = sv.frequencia_respiratoria || '';
    _classeVital('vital-temp-box', sv.temperatura, 'temp');
    _classeVital('vital-spo2-box', sv.saturacao_oxigenio, 'spo2');
    _classeVital('vital-fc-box', sv.frequencia_cardiaca, 'fc');
    _classeVital('vital-pa-box', sv.pressao_arterial, 'pa');
    _classeVital('vital-peso-box', sv.peso, 'peso');

    const diags = json.diagnosticos || [];
    const cidBox = document.getElementById('pront-cid-box');
    if (diags.length) {
      const d = diags[0];
      cidBox.style.display = '';
      document.getElementById('pront-cid-codigo').textContent = d.cid || '';
      document.getElementById('pront-cid-desc').textContent = d.descricao || '';
      document.getElementById('pront-cid-grav').textContent = d.gravidade || '—';
    } else {
      cidBox.style.display = 'none';
    }

    const exEl = document.getElementById('pront-exames-list');
    const exames = json.exames || [];
    exEl.innerHTML = exames.length
      ? exames.map(e => _renderExameChip(e.nome_exame || 'Exame', e.status)).join('')
      : '<div class="text-sm text-3">Nenhum exame solicitado nesta consulta.</div>';

    document.getElementById('pront-medico-nome').textContent = c.medico || 'Médico responsável';
    document.getElementById('pront-medico-crm').textContent =
      'CRM ' + (c.medico_crm || '—') + ' · ' + (c.medico_especialidade || 'Clínica Geral');

    const finalizado = c.status === 'CONCLUIDA';
    document.getElementById('btn-salvar-prontuario').disabled = finalizado;
  } catch (e) {
    console.error('Erro carregar prontuário:', e);
    showToast('Erro ao carregar prontuário', 'error');
  }
}

function assinarProntuario() {
  if (!_prontConsultaId) {
    showToast('Nenhuma consulta selecionada', 'warn');
    return;
  }
  salvarProntuario(true).then(() => {
    showToast('Prontuário assinado e atendimento finalizado!', 'success');
  });
}

function _dadosProntuarioForm(finalizar) {
  return {
    id_consulta: _prontConsultaId,
    queixa_principal: document.getElementById('pront-queixa')?.value?.trim(),
    historia_molestia_atual: document.getElementById('pront-hma')?.value?.trim(),
    antecedentes_pessoais: document.getElementById('pront-ap')?.value?.trim(),
    antecedentes_familiares: document.getElementById('pront-af')?.value?.trim(),
    exame_fisico: document.getElementById('pront-exame-fisico')?.value?.trim(),
    hipotese_diagnostica: document.getElementById('pront-hipotese')?.value?.trim(),
    plano_terapeutico: document.getElementById('pront-plano')?.value?.trim(),
    pa: document.getElementById('pront-pa')?.value?.trim(),
    fc: document.getElementById('pront-fc')?.value ? parseInt(document.getElementById('pront-fc').value) : null,
    temperatura: document.getElementById('pront-temp')?.value ? parseFloat(document.getElementById('pront-temp').value) : null,
    spo2: document.getElementById('pront-spo2')?.value ? parseInt(document.getElementById('pront-spo2').value) : null,
    peso: document.getElementById('pront-peso')?.value ? parseFloat(document.getElementById('pront-peso').value) : null,
    finalizar: !!finalizar,
  };
}

async function salvarProntuario(finalizar) {
  if (!podeAcessarProntuario()) {
    showToast('Acesso negado', 'error');
    return false;
  }
  if (!_prontConsultaId) {
    showToast('Selecione uma consulta', 'warn');
    return false;
  }
  const dados = _dadosProntuarioForm(finalizar);
  if (!dados.queixa_principal) {
    showToast('Informe a queixa principal', 'error');
    return false;
  }
  try {
    const res = await fetch('/api/prontuarios/' + _prontConsultaId, {
      method: 'PUT',
      headers: apiHeaders(),
      body: JSON.stringify(dados),
    });
    const json = await res.json();
    if (json.sucesso) {
      if (!finalizar) showToast('Prontuário salvo com sucesso!', 'success');
      await carregarProntuarioConsulta(_prontConsultaId);
      if (typeof carregarConsultas === 'function') carregarConsultas();
      return true;
    }
    showToast(json.mensagem || json.erro || 'Erro ao salvar', 'error');
    return false;
  } catch (e) {
    showToast('Erro de conexão', 'error');
    return false;
  }
}

function _coletarDadosProntuarioImpressao() {
  const val = id => document.getElementById(id)?.value?.trim() || '';
  const txt = id => document.getElementById(id)?.textContent?.trim() || '';
  const examesEl = document.getElementById('pront-exames-list');
  let exames = 'Nenhum exame solicitado nesta consulta.';
  if (examesEl) {
    const chips = examesEl.querySelectorAll('.chip');
    if (chips.length) {
      exames = Array.from(chips).map(c => c.textContent.trim()).join(' · ');
    }
  }
  const cidVisivel = document.getElementById('pront-cid-box')?.style.display !== 'none';
  const vitais = [
    val('pront-temp') && `Temp: ${val('pront-temp')} °C`,
    val('pront-fc') && `FC: ${val('pront-fc')} bpm`,
    val('pront-fr') && `FR: ${val('pront-fr')} rpm`,
    val('pront-pa') && `PA: ${val('pront-pa')} mmHg`,
    val('pront-spo2') && `SpO2: ${val('pront-spo2')}%`,
    val('pront-peso') && `Peso: ${val('pront-peso')} kg`,
  ].filter(Boolean).join(' · ');

  return {
    subtitulo: document.getElementById('pront-subtitulo')?.textContent || 'Prontuario Eletronico',
    paciente: document.querySelector('#page-prontuario .pront-nome')?.textContent || '—',
    cpf: document.getElementById('pront-cpf')?.textContent || '—',
    idade: document.getElementById('pront-idade')?.textContent || '—',
    tel: document.getElementById('pront-tel')?.textContent || '—',
    alergias: (document.getElementById('pront-alergias')?.textContent || '').replace('⚠', '').trim(),
    queixa: val('pront-queixa'),
    hma: val('pront-hma'),
    ap: val('pront-ap'),
    af: val('pront-af'),
    vitais,
    exameFisico: val('pront-exame-fisico'),
    hipotese: val('pront-hipotese'),
    plano: val('pront-plano'),
    cid: cidVisivel ? `${txt('pront-cid-codigo')} — ${txt('pront-cid-desc')}` : '',
    gravidade: cidVisivel ? txt('pront-cid-grav') : '',
    exames,
    medico: document.getElementById('pront-medico-nome')?.textContent || '—',
    medicoCrm: document.getElementById('pront-medico-crm')?.textContent || '—',
    data: new Date().toLocaleDateString('pt-BR'),
  };
}

function _linhasProntuario(pares) {
  return pares
    .filter(([, v]) => v != null && String(v).trim() && String(v).trim() !== '—')
    .map(([k, v]) => [k, String(v)]);
}

function _autoTabelaProntuario(doc, startY, head, body) {
  if (!body.length) return startY;
  const duasColunas = head.length === 2;
  doc.autoTable({
    startY,
    head: [head],
    body,
    theme: 'striped',
    headStyles: { fillColor: [37, 99, 235] },
    styles: { fontSize: 10, overflow: 'linebreak', cellPadding: 3 },
    columnStyles: duasColunas
      ? { 0: { cellWidth: 58, fontStyle: 'bold' }, 1: { cellWidth: 'auto' } }
      : {},
    margin: { left: 14, right: 14 },
  });
  return doc.lastAutoTable.finalY + 8;
}

function gerarProntuarioPDF(d) {
  if (!window.jspdf || !window.jspdf.jsPDF) {
    showToast('Biblioteca de PDF nao carregada. Verifique a conexao.', 'error');
    return false;
  }
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  doc.setFontSize(18);
  doc.setTextColor(26, 86, 219);
  doc.text('MedSystem PRO — Prontuário', 14, 20);
  doc.setFontSize(11);
  doc.setTextColor(90, 90, 90);
  doc.text(d.subtitulo || 'Prontuario eletronico', 14, 28);
  doc.text('Gerado em: ' + new Date().toLocaleString('pt-BR'), 14, 34);

  let y = 42;

  y = _autoTabelaProntuario(doc, y, ['Campo', 'Paciente'], _linhasProntuario([
    ['Nome', d.paciente],
    ['CPF', d.cpf],
    ['Idade', d.idade],
    ['Telefone', d.tel],
    ['Alergias', d.alergias],
  ]));

  y = _autoTabelaProntuario(doc, y, ['Campo', 'Anamnese'], _linhasProntuario([
    ['Queixa Principal', d.queixa],
    ['Historia da Molestia Atual', d.hma],
    ['Antecedentes Pessoais', d.ap],
    ['Antecedentes Familiares', d.af],
  ]));

  if (d.vitais) {
    y = _autoTabelaProntuario(doc, y, ['Sinais Vitais', 'Valor'], [['Registro', d.vitais]]);
  }

  const exameRows = _linhasProntuario([['Achados do Exame Fisico', d.exameFisico]]);
  if (exameRows.length) {
    y = _autoTabelaProntuario(doc, y, ['Campo', 'Exame Fisico'], exameRows);
  }

  if (d.cid) {
    const partes = d.cid.split(' — ');
    const codigo = partes[0] || d.cid;
    const descricao = partes.slice(1).join(' — ') || d.hipotese || '—';
    doc.autoTable({
      startY: y,
      head: [['CID', 'Diagnostico', 'Gravidade']],
      body: [[codigo, descricao, d.gravidade || '—']],
      theme: 'striped',
      headStyles: { fillColor: [37, 99, 235] },
      styles: { fontSize: 10, overflow: 'linebreak' },
      margin: { left: 14, right: 14 },
    });
    y = doc.lastAutoTable.finalY + 8;
  }

  const diagRows = _linhasProntuario([
    ['Hipotese Diagnostica', d.hipotese],
    ['Plano Terapeutico', d.plano],
  ]);
  if (diagRows.length) {
    y = _autoTabelaProntuario(doc, y, ['Campo', 'Conduta'], diagRows);
  }

  if (d.exames) {
    doc.autoTable({
      startY: y,
      head: [['Exames Solicitados']],
      body: [[d.exames]],
      theme: 'striped',
      headStyles: { fillColor: [37, 99, 235] },
      styles: { fontSize: 10, overflow: 'linebreak' },
      margin: { left: 14, right: 14 },
    });
    y = doc.lastAutoTable.finalY + 8;
  }

  const crmEsp = (d.medicoCrm || '—').replace(/^CRM\s*/i, '');
  _autoTabelaProntuario(doc, y, ['Medico', 'CRM / Especialidade'], [
    [d.medico || '—', crmEsp],
  ]);

  const slug = (d.paciente || 'paciente')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^\w]+/g, '-').toLowerCase().replace(/^-|-$/g, '').slice(0, 40);
  doc.save('prontuario-' + (slug || 'paciente') + '.pdf');
  showToast('PDF do prontuario exportado!', 'success');
  return true;
}

function imprimirProntuario() {
  const area = document.getElementById('pront-area-clinica');
  if (!area || area.style.display === 'none') {
    showToast('Abra um prontuario antes de imprimir', 'warn');
    return;
  }
  gerarProntuarioPDF(_coletarDadosProntuarioImpressao());
}

window.podeAcessarProntuario = podeAcessarProntuario;
window.aplicarPermissoesProntuario = aplicarPermissoesProntuario;
window.abrirProntuarioInicio = abrirProntuarioInicio;
window.abrirProntuario = abrirProntuario;
window.selecionarPacienteProntuario = selecionarPacienteProntuario;
window.trocarConsultaProntuario = trocarConsultaProntuario;
window.carregarProntuarioConsulta = carregarProntuarioConsulta;
window.salvarProntuario = salvarProntuario;
window.assinarProntuario = assinarProntuario;
window.imprimirProntuario = imprimirProntuario;
window.carregarPrescricoes = carregarPrescricoes;
window.emitirReceita = emitirReceita;
window.salvarRascunhoReceita = salvarRascunhoReceita;
window.reimprimirReceita = reimprimirReceita;
window.gerarReceitaPDF = gerarReceitaPDF;

let _searchTimer = null;
function fecharBuscaGlobal() {
  const box = document.getElementById('globalSearchResults');
  if (box) box.classList.remove('open');
}

function abrirPacienteDaBusca(id) {
  fecharBuscaGlobal();
  const input = document.getElementById('globalSearch');
  if (input) input.value = '';
  if (typeof podeAcessarProntuario === 'function' && podeAcessarProntuario() && typeof abrirProntuario === 'function') {
    abrirProntuario(id);
  } else {
    showPage('pacientes');
  }
}
window.abrirPacienteDaBusca = abrirPacienteDaBusca;

function globalSearchFn(val) {
  clearTimeout(_searchTimer);
  const box = document.getElementById('globalSearchResults');
  if (!box) return;
  const termo = (val || '').trim();
  if (termo.length < 2) { fecharBuscaGlobal(); return; }

  _searchTimer = setTimeout(async () => {
    try {
      const json = await apiGet('/api/pacientes/buscar?q=' + encodeURIComponent(termo));
      const lista = json.dados || [];
      if (!json.sucesso) { fecharBuscaGlobal(); return; }

      if (!lista.length) {
        box.innerHTML = '<div class="search-empty">Nenhum paciente encontrado</div>';
      } else {
        box.innerHTML = lista.map(p => {
          const id = p.id || p.id_paciente;
          const nome = String(p.nome || '').replace(/</g, '&lt;');
          const cpf = String(p.cpf || '—').replace(/</g, '&lt;');
          return `<div class="search-item" onclick="abrirPacienteDaBusca(${id})">
            <div><div class="si-nome">${nome}</div><div class="si-cpf">CPF: ${cpf}</div></div>
            <span class="si-go">abrir →</span>
          </div>`;
        }).join('');
      }
      box.classList.add('open');
    } catch (e) { console.error('Busca:', e); fecharBuscaGlobal(); }
  }, 300);
}
window.globalSearchFn = globalSearchFn;

document.addEventListener('click', (e) => {
  const wrap = document.querySelector('.topbar-search');
  if (wrap && !wrap.contains(e.target)) fecharBuscaGlobal();
});

function limparForm() {
  ['np-nome','np-cpf','np-nasc','np-tel','np-email','np-cep','np-logradouro','np-numero',
   'np-complemento','np-bairro','np-cidade','np-uf','np-alerg','np-obs'].forEach(id => {
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
    if (typeof carregarNotificacoes === 'function') carregarNotificacoes();
  } catch (e) {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
  }
  if (typeof _vincularBotoesPrescricao === 'function') _vincularBotoesPrescricao();
});
