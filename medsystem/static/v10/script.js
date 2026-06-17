// ══════════════════════════════════════
// VARIÁVEIS GLOBAIS
// ══════════════════════════════════════
let currentUser = null;
let slotSelecionado = '';

// ══════════════════════════════════════
// LOGIN / LOGOUT - INTEGRADO COM BACKEND
// ══════════════════════════════════════
function limparCamposLogin() {
  const email = document.getElementById('login-email');
  const senha = document.getElementById('login-senha');
  if (email) email.value = '';
  if (senha) senha.value = '';
}
window.limparCamposLogin = limparCamposLogin;

function doLogin() {
  const emailEl = document.getElementById('login-email');
  const senhaEl = document.getElementById('login-senha');
  const errEl = document.getElementById('login-error');
  const btn   = document.getElementById('login-btn');

  if (!emailEl || !senhaEl || !btn) {
    alert('Erro: tela de login incompleta. Recarregue a pagina.');
    return;
  }

  const email = emailEl.value.trim().toLowerCase();
  const senha = senhaEl.value;

  if (errEl) {
    errEl.style.display = 'none';
    errEl.textContent = '';
  }
  emailEl.classList.remove('error');
  senhaEl.classList.remove('error');

  if (!email || !senha) {
    if (errEl) {
      errEl.style.display = 'block';
      errEl.textContent = 'Preencha e-mail e senha para continuar.';
    }
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Verificando...';

  fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, senha })
  })
  .then(async response => {
    let data = {};
    try { data = await response.json(); } catch (e) { /* resposta nao-JSON */ }
    if (!response.ok || !data.sucesso) {
      throw new Error(data.mensagem || 'E-mail ou senha incorretos');
    }
    return data;
  })
  .then(data => {
    localStorage.setItem('token', data.token);
    localStorage.setItem('usuario', JSON.stringify(data.usuario));
    currentUser = data.usuario;
    loginSuccess(data.usuario);
    if (typeof carregarNotificacoes === 'function') carregarNotificacoes();
  })
  .catch(error => {
    console.error('Erro login:', error);
    if (errEl) {
      errEl.style.display = 'block';
      errEl.textContent = error.message || 'Erro ao conectar com servidor.';
    }
    emailEl.classList.add('error');
    senhaEl.classList.add('error');
  })
  .finally(() => {
    btn.disabled = false;
    btn.textContent = 'Entrar no sistema';
  });
}

window.doLogin = doLogin;

function toggleSenha(btn) {
  const input = document.getElementById('login-senha');
  if (!input) return;
  const mostrar = input.type === 'password';
  input.type = mostrar ? 'text' : 'password';
  const olhoAberto = '<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/>';
  const olhoFechado = '<path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-7-11-7a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 7 11 7a18.5 18.5 0 01-2.16 3.19M1 1l22 22"/>';
  btn.innerHTML = '<svg viewBox="0 0 24 24">' + (mostrar ? olhoFechado : olhoAberto) + '</svg>';
}
window.toggleSenha = toggleSenha;

function setMetricValue(metric, value) {
  const idMap = {
    consultas_hoje: 'dash-consultas',
    pacientes_ativos: 'dash-pacientes',
    exames_pendentes: 'dash-exames',
    novos_pacientes: 'dash-novos'
  };
  const byId = document.getElementById(idMap[metric]);
  if (byId) byId.textContent = value;
  const byMetric = document.querySelector('[data-metric="' + metric + '"]');
  if (byMetric) byMetric.textContent = value;
}

function loginSuccess(user) {
  const sbAvatar = document.getElementById('sidebar-avatar') || document.querySelector('.sidebar-footer .avatar');
  const sbName = document.getElementById('sidebar-name') || document.querySelector('.sidebar-footer .user-name');
  const sbRole = document.getElementById('sidebar-role') || document.querySelector('.sidebar-footer .user-role');
  
  // Lendo os dados diretos do primeiro nível mapeado no Flask
  const pCrmInput = document.getElementById('p-crm');
  const pEspInput = document.getElementById('p-esp');
  
  if (pCrmInput) pCrmInput.value = user.crm || 'N/A';
  if (pEspInput) pEspInput.value = user.especialidade || 'N/A';
  
  const iniciais = user.iniciais || (user.nome ? user.nome.substring(0, 2).toUpperCase() : 'US');
  if (sbAvatar) sbAvatar.textContent = iniciais;
  if (sbName) sbName.textContent = user.nome;
  if (sbRole) {
    const roleText = user.tipo === 'medico'
      ? ((user.crm || 'CRM N/A') + ' · ' + (user.especialidade || 'Médico'))
      : (user.tipo || 'Usuário');
    sbRole.textContent = roleText;
  }

  const navAdmin = document.getElementById('nav-admin');
  if (navAdmin) {
    navAdmin.style.display = user.tipo === 'admin' ? 'block' : 'none';
  }

  const pfAvatar = document.getElementById('perfil-avatar-lg');
  const pfNome = document.getElementById('perfil-nome-display');
  const pfRole = document.getElementById('perfil-role-display');
  const pfEsp = document.getElementById('perfil-esp-display');
  const pNomeInput = document.getElementById('p-nome');
  const pEmailInput = document.getElementById('p-email');

  if (pfAvatar) pfAvatar.textContent = user.iniciais || user.nome.substring(0, 2).toUpperCase();
  if (pfNome) pfNome.textContent = user.nome;
  if (pfRole) pfRole.textContent = (user.tipo || 'Usuário') + ' • ID ' + user.id;
  
  if (pfEsp) pfEsp.textContent = user.tipo === 'medico' ? user.especialidade : user.email;
  
  if (pNomeInput) pNomeInput.value = user.nome;
  if (pEmailInput) pEmailInput.value = user.email;

  const sessaoEmail = document.getElementById('sessao-email');
  const sessaoHora = document.getElementById('sessao-hora');
  if (sessaoEmail) sessaoEmail.textContent = user.email;
  if (sessaoHora) sessaoHora.textContent = new Date().toLocaleTimeString('pt-BR');

  const loginScreen = document.getElementById('login-screen');
  const appScreen = document.getElementById('app-screen');
  
  if (loginScreen) loginScreen.style.display = 'none';
  if (appScreen) {
    appScreen.style.display = 'block';
    appScreen.classList.add('active');
  }

  showToast('Bem-vindo, ' + user.nome + '! 👋', 'success');
  showPage('dashboard');

  carregarDashboard();
  carregarPacientes();
  carregarDadosParaAgendamento();
  carregarConsultas();

  if (typeof carregarModuloPro === 'function') carregarModuloPro('dashboard');

  if (typeof aplicarPermissoesEquipe === 'function') aplicarPermissoesEquipe(user);
  if (typeof carregarNotificacoes === 'function') carregarNotificacoes();

  if (user.tipo === 'admin' || user.tipo === 'medico') {
    if (typeof carregarEspecialidades === 'function') carregarEspecialidades();
    const inputSenha = document.getElementById('nu-senha');
    if (inputSenha && typeof exibirIndicadorForcaSenha === 'function') {
      exibirIndicadorForcaSenha(inputSenha, 'nu-senha-force');
    }
  }
}

function doLogout() {
  currentUser = null;
  localStorage.removeItem('token');
  localStorage.removeItem('usuario');

  const appScreen = document.getElementById('app-screen');
  const loginScreen = document.getElementById('login-screen');
  if (appScreen) {
    appScreen.style.display = 'none';
    appScreen.classList.remove('active');
  }
  if (loginScreen) loginScreen.style.display = 'flex';
  limparCamposLogin();
  document.getElementById('login-error').style.display = 'none';
  document.getElementById('login-email').classList.remove('error');
  document.getElementById('login-senha').classList.remove('error');
  
  const btn = document.getElementById('login-btn');
  btn.disabled = false;
  btn.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" style="stroke:#fff;fill:none"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4M10 17l5-5-5-5M15 12H3"/></svg> Entrar no sistema';
  showToast('Sessão encerrada com sucesso.', '');
}

// ══════════════════════════════════════
// BUSCAS NA API (GET)
// ══════════════════════════════════════
function fmtMoedaDash(v) {
  return 'R$ ' + Number(v || 0).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

async function carregarDashboard() {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;

    const res = await fetch('/api/dashboard/estatisticas', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const json = await res.json();

    if (!res.ok || !json.sucesso) {
      showToast(json.mensagem || 'Erro ao carregar dashboard', 'error');
      console.error('Dashboard API:', json);
      return;
    }

    const d = json.dados;
    setMetricValue('consultas_hoje', d.consultas_hoje ?? 0);
    setMetricValue('pacientes_ativos', d.pacientes_ativos ?? 0);
    setMetricValue('exames_pendentes', d.exames_pendentes ?? 0);
    setMetricValue('novos_pacientes', d.novos_pacientes ?? 0);

    const agendaData = document.getElementById('dash-agenda-data');
    if (agendaData && d.data_hoje) {
      agendaData.textContent = 'Hoje, ' + d.data_hoje;
    }

    const receitaMes = d.receita_mes ?? 0;
    const receitaPaga = d.receita_paga ?? 0;
    const meta = 25000;
    const pct = Math.min(100, Math.round((receitaMes / meta) * 100));
    const setTxt = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    setTxt('dash-receita-mes', fmtMoedaDash(receitaMes));
    setTxt('dash-receita-paga', fmtMoedaDash(receitaPaga));
    setTxt('dash-receita-pendente', fmtMoedaDash(Math.max(0, receitaMes - receitaPaga)));
    setTxt('dash-receita-pct', pct + '%');
    const bar = document.getElementById('dash-receita-bar');
    if (bar) bar.style.width = pct + '%';
    const mesAtual = new Date().toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' });
    setTxt('dash-fat-titulo', 'Faturamento — ' + mesAtual);

    const tbodyDash = document.querySelector('#tabela-dash-consultas tbody')
      || document.getElementById('agenda-hoje-tbody');
    const podePront = typeof podeAcessarProntuario === 'function' && podeAcessarProntuario();
    if (tbodyDash) {
      if (d.ultimas_consultas && d.ultimas_consultas.length > 0) {
        tbodyDash.innerHTML = '';
        d.ultimas_consultas.forEach(c => {
          const cols = tbodyDash.closest('table')?.querySelectorAll('thead th').length || 3;
          const btnPront = podePront
            ? `<button class="btn btn-ghost btn-sm btn-prontuario" onclick="abrirProntuario(${c.id_paciente || 0}, ${c.id_consulta || 0})">→</button>`
            : '';
          if (cols >= 5) {
            const idCons = c.id_consulta || 0;
            tbodyDash.innerHTML += `
              <tr class="agenda-row-click" style="cursor:pointer" onclick="verAgendamento(${idCons})" title="Clique para ver o agendamento">
                <td class="td-mono">${c.hora || '—'}</td>
                <td class="td-name">${c.paciente_nome}</td>
                <td><span class="badge badge-blue">${c.tipo || 'Consulta'}</span></td>
                <td><span class="badge badge-amber">${c.status}</span></td>
                <td onclick="event.stopPropagation()">${btnPront}</td>
              </tr>`;
          } else {
            tbodyDash.innerHTML += `
              <tr>
                <td class="td-name">${c.paciente_nome}</td>
                <td class="td-mono">${c.hora}</td>
                <td><span class="badge badge-blue">${c.status}</span></td>
              </tr>`;
          }
        });
      } else {
        const colspan = tbodyDash.closest('table')?.querySelectorAll('thead th').length || 3;
        tbodyDash.innerHTML = '<tr><td colspan="' + colspan + '" style="text-align:center;color:#999;">Nenhuma consulta agendada para hoje</td></tr>';
      }
    }

    const retornosEl = document.getElementById('proximos-retornos-timeline');
    if (retornosEl) {
      const retornos = d.proximos_retornos || [];
      if (retornos.length) {
        retornosEl.innerHTML = retornos.map((r, i) => `
          <li class="tl-item">
            <div class="tl-dot ${i % 2 ? 'green' : 'blue'}"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg></div>
            <div class="tl-content">
              <div class="tl-title">${r.paciente}</div>
              <div class="tl-body">${r.motivo} · ${r.medico}</div>
              <div class="tl-date">${r.data}${r.hora ? ' · ' + r.hora : ''}</div>
            </div>
          </li>`).join('');
      } else {
        retornosEl.innerHTML = '<li class="tl-item"><div class="tl-content"><div class="tl-body" style="color:#999">Nenhum retorno agendado.</div></div></li>';
      }
    }

    await carregarExamesPendentes();
    await carregarAlertasDashboard();
  } catch (erro) {
    console.error('Erro no dashboard:', erro);
    showToast('Erro de conexão ao carregar dashboard', 'error');
  }
}

async function carregarExamesPendentes() {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;

    const res = await fetch('/api/exames/pendentes', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const json = await res.json();
    const tbody = document.querySelector('#tabela-dash-exames tbody')
      || document.getElementById('exames-pendentes-tbody');
    if (!tbody) return;

    if (json.sucesso && json.dados && Object.keys(json.dados).length > 0) {
      tbody.innerHTML = '';
      Object.entries(json.dados).slice(0, 5).forEach(([paciente, info]) => {
        const urgente = info.exames.some(exame => exame.status === 'EM_ANALISE' || exame.prioridade === 'URGENTE');
        if (tbody.id === 'exames-pendentes-tbody') {
          const ex = info.exames[0] || {};
          tbody.innerHTML += `
            <tr>
              <td class="td-name">${paciente}</td>
              <td class="text-sm">${ex.nome_exame || 'Exame'}</td>
              <td><span class="badge ${urgente ? 'badge-red' : 'badge-amber'}">${urgente ? 'Urgente' : 'Normal'}</span></td>
              <td>${ex.data_solicitacao ? new Date(ex.data_solicitacao).toLocaleDateString('pt-BR') : '—'}</td>
              <td><span class="badge badge-blue">${ex.status || 'Solicitado'}</span></td>
            </tr>`;
        } else {
          tbody.innerHTML += `
            <tr>
              <td class="td-name">${paciente}</td>
              <td>${info.quantidade}</td>
              <td class="${urgente ? 'badge-red' : 'badge-green'}">${urgente ? 'SIM' : 'NÃO'}</td>
            </tr>`;
        }
      });
    } else {
      const colspan = tbody.closest('table')?.querySelectorAll('thead th').length || 3;
      tbody.innerHTML = '<tr><td colspan="' + colspan + '" style="text-align:center;color:#999;">Nenhum exame pendente encontrado</td></tr>';
    }
  } catch (erro) {
    console.error('Erro ao carregar exames pendentes:', erro);
  }
}

async function carregarAlertasDashboard() {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;

    const res = await fetch('/api/dashboard/alertas', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const json = await res.json();
    const container = document.getElementById('alertas-list');
    if (!container) return;

    if (json.sucesso && Array.isArray(json.dados) && json.dados.length > 0) {
      const badge = document.getElementById('dash-alertas-badge');
      if (badge) badge.textContent = json.dados.length + ' ativo' + (json.dados.length > 1 ? 's' : '');
      container.innerHTML = '';
      json.dados.slice(0, 6).forEach(alerta => {
        const dataTexto = alerta.data ? new Date(alerta.data).toLocaleDateString('pt-BR') : 'Data não disponível';
        const g = (alerta.gravidade || 'LEVE').toUpperCase();
        let badge = 'green', dotClass = 'green', alertaClass = 'alerta-leve';
        if (g.includes('CRIT')) { badge = 'red'; dotClass = 'red'; alertaClass = 'alerta-critico'; }
        else if (g === 'GRAVE') { badge = 'amber'; dotClass = 'amber'; alertaClass = 'alerta-grave'; }
        else if (g === 'MODERADA') { badge = 'amber'; dotClass = 'amber'; alertaClass = 'alerta-moderado'; }

        if (container.classList.contains('timeline')) {
          container.innerHTML += `
            <li class="tl-item">
              <div class="tl-dot ${dotClass}"><svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg></div>
              <div class="tl-content">
                <div class="tl-title">${alerta.paciente} — ${alerta.tipo || g} <span class="badge badge-${badge}" style="margin-left:6px">${g}</span></div>
                <div class="tl-body">${alerta.descricao || 'Sem descrição adicional.'}</div>
                <div class="tl-date">${dataTexto}</div>
              </div>
            </li>`;
        } else {
          container.innerHTML += `
            <div class="alerta-item ${alertaClass}">
              <div class="alerta-icon">${g.includes('CRIT') ? '⚠' : g === 'GRAVE' ? '❗' : '●'}</div>
              <div class="alerta-content">
                <div class="alerta-title">${alerta.paciente} — ${alerta.tipo || g}</div>
                <div class="alerta-text">${alerta.descricao || 'Sem descrição adicional.'}</div>
                <div class="alerta-meta">${dataTexto} · ${g}</div>
              </div>
            </div>`;
        }
      });
    } else {
      const badge = document.getElementById('dash-alertas-badge');
      if (badge) badge.textContent = '0 ativos';
      if (container.classList.contains('timeline')) {
        container.innerHTML = '<li class="tl-item"><div class="tl-content"><div class="tl-body" style="color:#999">Nenhum alerta clínico no momento.</div></div></li>';
      } else {
        container.innerHTML = '<div class="alerta-empty">Nenhum alerta clínico no momento.</div>';
      }
    }
  } catch (erro) {
    console.error('Erro ao carregar alertas do dashboard:', erro);
  }
}

async function carregarPacientes() {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;

    const res = await fetch('/api/pacientes', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const json = await res.json();

    if (json.sucesso) {
      const tbody = document.querySelector('#tabela-pacientes tbody');
      if (!tbody) return;
      tbody.innerHTML = ''; 

      json.dados.forEach(paciente => {
        let dataFmt = paciente.data_nascimento 
            ? new Date(paciente.data_nascimento).toLocaleDateString('pt-BR', {timeZone: 'UTC'}) 
            : '—';

        // ──── CORREÇÃO: Pega o ID de onde ele estiver ────
        const idCorreto = paciente.id || paciente.id_paciente;

        const podePront = typeof podeAcessarProntuario === 'function' && podeAcessarProntuario();
        const btnPront = podePront
          ? `<button class="btn btn-outline btn-prontuario" onclick="abrirProntuario(${idCorreto})">Prontuário</button>`
          : '';

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${paciente.nome}</td>
          <td>${paciente.cpf}</td>
          <td>${dataFmt}</td>
          <td>${typeof formatarTelefone === 'function' ? formatarTelefone(paciente.telefone) : (paciente.telefone || '—')}</td>
          <td>${btnPront || '<span class="text-3">—</span>'}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (erro) {
    console.error('Erro ao buscar pacientes:', erro);
  }
}

async function carregarDadosParaAgendamento() {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;

    const headers = { 'Authorization': 'Bearer ' + token };
    const [resPacientes, resMedicos, resPrecos] = await Promise.all([
      fetch('/api/pacientes', { headers }),
      fetch('/api/medicos', { headers }),
      fetch('/api/financeiro/precos', { headers })
    ]);

    const jsonPacientes = await resPacientes.json();
    const jsonMedicos = await resMedicos.json();
    const jsonPrecos = await resPrecos.json();

    if (jsonPacientes.sucesso) {
      const selectPac = document.getElementById('nc-pac');
      if (selectPac) {
        selectPac.innerHTML = '<option value="">Selecione um Paciente...</option>';
        jsonPacientes.dados.forEach(p => {
          selectPac.innerHTML += `<option value="${p.id}">${p.nome} (CPF: ${p.cpf})</option>`;
        });
      }
    }

    if (jsonMedicos.sucesso) {
      const selectMed = document.getElementById('nc-med');
      if (selectMed) {
        selectMed.innerHTML = '<option value="">Selecione um Médico...</option>';
        jsonMedicos.dados.forEach(m => {
          const nomeMedico = m.nome || (m.usuario ? m.usuario.nome : 'Médico');
          const espNome = m.especialidade ? (m.especialidade.nome || m.especialidade) : 'N/A';
          selectMed.innerHTML += `<option value="${m.id}">Dr(a). ${nomeMedico} (${espNome})</option>`;
        });
      }
    }

    if (jsonPrecos.sucesso) {
      const selectConv = document.getElementById('nc-convenio');
      if (selectConv) {
        const convenios = new Set(['Particular']);
        (jsonPrecos.precos || []).forEach(p => {
          if (p.modalidade === 'Convenio' && p.nome_convenio) convenios.add(p.nome_convenio);
        });
        selectConv.innerHTML = [...convenios].map(c =>
          `<option value="${c}">${c}</option>`
        ).join('');
      }
    }

    if (typeof atualizarPreviewPrecoAgendamento === 'function') {
      atualizarPreviewPrecoAgendamento();
    }

    const ncData = document.getElementById('nc-data');
    const ncMed = document.getElementById('nc-med');
    if (ncData && !ncData.dataset.horariosBound) {
      ncData.dataset.horariosBound = '1';
      ncData.addEventListener('change', () => {
        if (typeof carregarHorariosDisponiveis === 'function') carregarHorariosDisponiveis();
      });
      if (!ncData.value) {
        ncData.value = new Date().toISOString().slice(0, 10);
      }
    }
    if (ncMed && !ncMed.dataset.horariosBound) {
      ncMed.dataset.horariosBound = '1';
      ncMed.addEventListener('change', () => {
        if (typeof carregarHorariosDisponiveis === 'function') carregarHorariosDisponiveis();
      });
    }
    if (typeof carregarHorariosDisponiveis === 'function') {
      carregarHorariosDisponiveis();
    }
  } catch (erro) {
    console.error('Erro ao carregar dados de agendamento:', erro);
  }
}

// ══════════════════════════════════════
// NOVO PACIENTE (POST)
// ══════════════════════════════════════
async function cadastrarPaciente() {
  const nome = document.getElementById('np-nome').value.trim();
  let cpf   = document.getElementById('np-cpf').value.trim();
  const nasc = document.getElementById('np-nasc').value;
  const sexo = document.getElementById('np-sexo').value;
  const tel  = document.getElementById('np-tel') ? document.getElementById('np-tel').value.trim() : '';
  const email = document.getElementById('np-email') ? document.getElementById('np-email').value.trim() : '';
  const sangue = document.getElementById('np-sangue') ? document.getElementById('np-sangue').value : '';
  const enderecoEl = document.getElementById('np-endereco') || document.getElementById('np-end');
  const alergiasEl = document.getElementById('np-alergias') || document.getElementById('np-alerg');
  const observacoesEl = document.getElementById('np-observacoes') || document.getElementById('np-obs');
  const endereco = typeof montarEnderecoCompleto === 'function'
    ? montarEnderecoCompleto()
    : (enderecoEl ? enderecoEl.value.trim() : '');
  const cep = document.getElementById('np-cep')?.value?.replace(/\D/g, '') || null;
  const logradouro = document.getElementById('np-logradouro')?.value?.trim() || null;
  const numero = document.getElementById('np-numero')?.value?.trim() || null;
  const complemento = document.getElementById('np-complemento')?.value?.trim() || null;
  const bairro = document.getElementById('np-bairro')?.value?.trim() || null;
  const cidade = document.getElementById('np-cidade')?.value?.trim() || null;
  const uf = document.getElementById('np-uf')?.value?.trim().toUpperCase() || null;
  const alergias = alergiasEl ? alergiasEl.value.trim() : '';
  const observacoes = observacoesEl ? observacoesEl.value.trim() : '';
  
  const peso = document.getElementById('np-peso') ? document.getElementById('np-peso').value : '';
  const altura = document.getElementById('np-altura') ? document.getElementById('np-altura').value : '';
  const pressao = document.getElementById('np-pressao') ? document.getElementById('np-pressao').value.trim() : '';
  const fc = document.getElementById('np-fc') ? document.getElementById('np-fc').value : '';

  if (!nome || !cpf || !nasc || !sexo) {
    showToast('❌ Preencha os campos obrigatórios (*)', 'error'); 
    return;
  }

  if (typeof validarCPF === 'function' && !validarCPF(cpf)) {
    showToast('❌ CPF inválido. Verifique os números.', 'error');
    document.getElementById('np-cpf').focus();
    return;
  }

  if (typeof validarDataNascimento === 'function') {
      const idade = validarDataNascimento(nasc);
      if (idade < 0) {
        showToast('❌ Data de nascimento não pode ser no futuro.', 'error');
        return;
      }
      if (idade > 150) {
        showToast('❌ Data de nascimento inválida.', 'error');
        return;
      }
  }

  if (email && typeof validarEmail === 'function' && !validarEmail(email)) {
    showToast('❌ Email inválido.', 'error');
    return;
  }

  if (tel && typeof validarTelefone === 'function' && !validarTelefone(tel)) {
    showToast('❌ Telefone deve ter entre 10 e 11 dígitos.', 'error');
    return;
  }

  try {
    const token = localStorage.getItem('token');
    
    const res = await fetch('/api/pacientes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({ 
        nome: nome, 
        cpf: cpf.replace(/\D/g, ''),
        data_nascimento: nasc,
        sexo: sexo,
        telefone: tel.replace(/\D/g, ''),
        email: email,
        tipo_sanguineo: sangue || null,
        endereco: endereco || null,
        cep: cep,
        logradouro: logradouro,
        numero: numero,
        complemento: complemento,
        bairro: bairro,
        cidade: cidade,
        uf: uf,
        alergias: alergias || null,
        observacoes: observacoes || null,
        peso: peso ? parseFloat(peso) : null,
        altura: altura ? parseInt(altura) : null,
        pressao: pressao || null,
        frequencia_cardiaca: fc ? parseInt(fc) : null,
        ativo: true
      })
    });

    const dados = await res.json();
    
    if (res.ok && dados.sucesso) {
      showToast('✅ Paciente cadastrado com sucesso!', 'success');
      
      document.getElementById('np-nome').value = '';
      document.getElementById('np-cpf').value = '';
      document.getElementById('np-nasc').value = '';
      document.getElementById('np-sexo').value = '';
      if (document.getElementById('np-tel')) document.getElementById('np-tel').value = '';
      if (document.getElementById('np-email')) document.getElementById('np-email').value = '';
      if (document.getElementById('np-sangue')) document.getElementById('np-sangue').value = '';
      if (enderecoEl) enderecoEl.value = '';
      ['np-cep','np-logradouro','np-numero','np-complemento','np-bairro','np-cidade','np-uf'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });
      if (alergiasEl) alergiasEl.value = '';
      if (observacoesEl) observacoesEl.value = '';
      if (document.getElementById('np-peso')) document.getElementById('np-peso').value = '';
      if (document.getElementById('np-altura')) document.getElementById('np-altura').value = '';
      if (document.getElementById('np-pressao')) document.getElementById('np-pressao').value = '';
      if (document.getElementById('np-fc')) document.getElementById('np-fc').value = '';
      
      if (typeof carregarPacientes === 'function') carregarPacientes();
      if (typeof carregarDadosParaAgendamento === 'function') carregarDadosParaAgendamento();
      
      showPage('pacientes');
      
    } else if (res.status === 409) {
      showToast('❌ CPF já cadastrado no sistema.', 'error');
    } else if (res.status === 403) {
      showToast('❌ Você não tem permissão para fazer isso.', 'error');
    } else {
      showToast('❌ Erro: ' + (dados.mensagem || 'Falha ao cadastrar'), 'error');
    }
  } catch (erro) {
    console.error("Erro interno no JavaScript:", erro);
    showToast('❌ Erro de conexão com o servidor.', 'error');
  }
}

// ══════════════════════════════════════
// NOVA CONSULTA (POST)
// ══════════════════════════════════════
function selecionarSlot(el, hora) {
  if (el.classList.contains('slot-busy')) return;
  document.querySelectorAll('.agenda-slot').forEach(s => s.classList.remove('selected'));
  el.classList.add('selected');
  slotSelecionado = hora;
  showToast('Horário ' + hora + ' selecionado.', '');
}

async function agendarConsulta() {
  const pacId = document.getElementById('nc-pac').value;
  const medId = document.getElementById('nc-med').value;
  const data = document.getElementById('nc-data').value;
  const hora = document.getElementById('nc-hora').value;
  const motivo = document.getElementById('nc-motivo').value.trim();
  
  if (!pacId || !medId || !data || !hora || !motivo) {
    showToast('Preencha todos os campos obrigatórios (*)', 'error'); 
    return;
  }
  
  const dataIso = `${data}T${hora}:00`; 
  const tipo = document.getElementById('nc-tipo')?.value || '1ª Consulta';
  const convenio = document.getElementById('nc-convenio')?.value || 'Particular';
  const obs = document.getElementById('nc-obs')?.value?.trim();

  try {
    const token = localStorage.getItem('token');
    const res = await fetch('/api/consultas', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({
        id_paciente: parseInt(pacId),
        id_medico: parseInt(medId),
        data_consulta: dataIso,
        hora_consulta: hora,
        motivo: motivo,
        tipo_consulta: tipo,
        convenio: convenio,
        observacoes: obs || null
      })
    });

    const dados = await res.json();

    if (res.ok && dados.sucesso) {
      let msg = dados.mensagem || 'Consulta agendada com sucesso!';
      if (dados.aviso_preco) msg += ' (' + dados.aviso_preco + ')';
      showToast(msg, dados.receita ? 'success' : 'warn');
      limparFormConsulta();
      closeModal('modal-consulta');
      carregarDashboard(); 
      carregarConsultas();
      if (typeof carregarAgendaSemanal === 'function') carregarAgendaSemanal();
    } else {
      showToast('Erro: ' + (dados.mensagem || 'Falha ao agendar'), 'error');
    }
  } catch (erro) {
    console.error('Erro:', erro);
    showToast('Erro de conexão com o servidor.', 'error');
  }
}

function limparFormConsulta() {
  document.getElementById('nc-pac').value = '';
  document.getElementById('nc-med').value = '';
  document.getElementById('nc-data').value = '';
  document.getElementById('nc-hora').value = '';
  document.getElementById('nc-motivo').value = '';
  const obs = document.getElementById('nc-obs');
  if (obs) obs.value = '';
  document.querySelectorAll('.hora-slot-btn.selecionado').forEach(s => s.classList.remove('selecionado'));
  const slots = document.getElementById('nc-horarios-slots');
  if (slots) {
    slots.innerHTML = '<div class="hora-slots-hint">Selecione médico e data para ver os horários</div>';
  }
  slotSelecionado = '';
}

// ══════════════════════════════════════
// MÁSCARAS E NAVEGAÇÃO
// ══════════════════════════════════════
function mascaraCPF(input) {
  let v = input.value.replace(/\D/g,'').slice(0,11);
  v = v.replace(/(\d{3})(\d)/,'$1.$2');
  v = v.replace(/(\d{3})(\d)/,'$1.$2');
  v = v.replace(/(\d{3})(\d{1,2})$/,'$1-$2');
  input.value = v;
}

function mascaraTel(input) {
  let v = input.value.replace(/\D/g,'').slice(0,11);
  v = v.replace(/^(\d{2})(\d)/,'($1) $2');
  v = v.replace(/(\d{5})(\d)/,'$1-$2');
  input.value = v;
}

function mascaraCRM(input) {
  let v = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (v.length > 12) {
    v = v.slice(0, 12);
  }
  input.value = v;
}

function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const pg = document.getElementById('page-' + id);
  if (pg) pg.classList.add('active');
  document.querySelectorAll('.nav-item').forEach(btn => {
    if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes("'" + id + "'"))
      btn.classList.add('active');
  });
  window.scrollTo(0, 0);
}

const dataHoje = new Date();
const diasSemana = ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];
const hojeElement = document.getElementById('hoje');
if (hojeElement) {
    hojeElement.textContent = diasSemana[dataHoje.getDay()] + ', ' + dataHoje.toLocaleDateString('pt-BR', {day:'2-digit',month:'long',year:'numeric'});
}

function showToast(msg, type) {
  const area = document.getElementById('toastArea');
  if(!area) return;
  const t = document.createElement('div');
  t.className = 'toast ' + (type || '');
  t.textContent = msg;
  area.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

function filtrarConsultas(val) {
  const rows = document.querySelectorAll('#tabela-consultas tbody tr');
  rows.forEach(r => {
    r.style.display = r.textContent.toLowerCase().includes(val.toLowerCase()) ? '' : 'none';
  });
}

// ══════════════════════════════════════
// PERFIL E FUNÇÕES AUXILIARES DE GET
// ══════════════════════════════════════
function salvarPerfil() {
  const nome = document.getElementById('p-nome').value.trim();
  if (!nome) { showToast('O nome não pode estar vazio.', 'error'); return; }
  document.getElementById('perfil-nome-display').textContent = nome;
  document.getElementById('sidebar-name').textContent = nome;
  showToast('Perfil atualizado com sucesso!', 'success');
}

function editarPerfil() {
  showToast('Em desenvolvimento.', 'success');
}

function alterarSenha() {
  const atual = document.getElementById('p-senha-atual').value;
  const nova  = document.getElementById('p-senha-nova').value;
  const conf  = document.getElementById('p-senha-conf').value;
  if (!atual || !nova || !conf) { showToast('Preencha todos os campos de senha.', 'error'); return; }
  if (nova !== conf) { showToast('A nova senha e a confirmação não coincidem.', 'error'); return; }
  if (nova.length < 6) { showToast('A nova senha deve ter pelo menos 6 caracteres.', 'error'); return; }
  
  document.getElementById('p-senha-atual').value = '';
  document.getElementById('p-senha-nova').value = '';
  document.getElementById('p-senha-conf').value = '';
  showToast('Senha alterada com sucesso!', 'success');
}

async function carregarConsultas() {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch('/api/consultas', { headers: { 'Authorization': 'Bearer ' + token } });
    const json = await res.json();

    if (json.sucesso) {
      const tbody = document.querySelector('#tabela-consultas tbody');
      if (!tbody) return;
      tbody.innerHTML = ''; 

      json.dados.forEach(c => {
        const tr = document.createElement('tr');
        const dataFmt = c.data_consulta ? new Date(c.data_consulta).toLocaleDateString('pt-BR') : '—';
        const horaFmt = c.hora_consulta || '—';
        const idPac = c.id_paciente || (c.paciente && (c.paciente.id || c.paciente.id_paciente));
        const nomePac = (c.paciente && c.paciente.nome) || 'Paciente';
        const nomeMed = c.medico_nome
          || (c.medico && (c.medico.nome || (c.medico.usuario && c.medico.usuario.nome)))
          || '—';
        const idCons = c.id || c.id_consulta || '';

        const podePront = typeof podeAcessarProntuario === 'function' && podeAcessarProntuario();
        const btnPront = podePront
          ? `<button class="btn btn-outline btn-sm btn-prontuario" onclick="abrirProntuario(${idPac}, ${idCons})">Prontuário</button>`
          : '<span class="text-3">—</span>';

        tr.innerHTML = `
          <td class="td-mono">#${String(idCons).padStart(4, '0')}</td>
          <td class="td-name">${nomePac}</td>
          <td class="td-mono">${dataFmt} ${horaFmt}</td>
          <td>${nomeMed}</td>
          <td>${c.motivo || '—'}</td>
          <td><span class="badge badge-amber">${c.status || 'Agendada'}</span></td>
          <td>${btnPront}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (erro) { console.error('Erro ao buscar consultas:', erro); }
}

// abrirProntuario() definido em pro.js (acesso médico/admin)

// ══════════════════════════════════════
// NOVO USUÁRIO / NOVO MÉDICO (UNIFICADO)
// ══════════════════════════════════════
async function carregarEspecialidades() {
  try {
    const res = await fetch('/api/auth/especialidades');
    
    let especialidades = [];
    if (res.ok) {
        const json = await res.json();
        if (json.sucesso) especialidades = json.dados;
    }

    const selectEsp = document.getElementById('nu-especialidade');
    if (selectEsp) {
      selectEsp.innerHTML = '<option value="">Selecione a especialidade...</option>';
      especialidades.forEach(esp => {
        selectEsp.innerHTML += `<option value="${esp.id}">${esp.nome}</option>`;
      });
    }
  } catch (erro) {
    console.error('Erro ao carregar especialidades:', erro);
  }
}

async function novoUsuario() {
  const nome = document.getElementById('nu-nome').value.trim();
  const email = document.getElementById('nu-email').value.trim();
  const senha = document.getElementById('nu-senha').value;
  const tipo = document.getElementById('nu-tipo').value;

  if (!nome || !email || !senha) {
    showToast('❌ Preencha Nome, E-mail e Senha.', 'error');
    return;
  }

  let payload = { nome, email, senha, tipo };

  if (tipo === 'medico') {
    const crm = document.getElementById('nu-crm').value.trim();
    const id_especialidade = document.getElementById('nu-especialidade').value;
    
    if (!crm || !id_especialidade) {
      showToast('❌ Para cadastrar um médico, CRM e Especialidade são obrigatórios.', 'error');
      return;
    }
    payload.crm = crm;
    payload.id_especialidade = parseInt(id_especialidade);
  }

  try {
    const token = localStorage.getItem('token');
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify(payload)
    });

    const json = await res.json();

    if (json.sucesso) {
      showToast('✅ Acesso criado com sucesso!', 'success');
      toggleFormUsuario(false);
      document.getElementById('nu-nome').value = '';
      document.getElementById('nu-email').value = '';
      document.getElementById('nu-senha').value = '';
      document.getElementById('nu-tipo').value = 'recepcao';
      if (document.getElementById('nu-crm')) document.getElementById('nu-crm').value = '';
      toggleCamposMedicoUsuario();

      showPage('equipe');
      if (typeof carregarEquipe === 'function') carregarEquipe();
      
    } else {
      showToast('❌ ' + (json.mensagem || 'Erro ao criar usuário'), 'error');
    }
  } catch (erro) {
    console.error('Erro:', erro);
    showToast('❌ Erro de conexão com o servidor', 'error');
  }
}

// MOBILE: Toggle do sidebar com overlay
document.addEventListener('DOMContentLoaded', function() {
  limparCamposLogin();
  setTimeout(limparCamposLogin, 100);
  setTimeout(limparCamposLogin, 500);

  const btn = document.getElementById('mobile-menu-btn');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.style.display = 'none';
  }

  if (btn && sidebar) {
    btn.addEventListener('click', function() {
      const opening = !sidebar.classList.contains('open');
      if (opening) {
        sidebar.classList.add('open');
        if (overlay) overlay.style.display = 'block';
      } else {
        closeSidebar();
      }
    });
  }

  if (overlay) overlay.addEventListener('click', closeSidebar);

  // Fecha o menu ao redimensionar para desktop
  window.addEventListener('resize', function() {
    if (window.innerWidth > 768) closeSidebar();
  });
});