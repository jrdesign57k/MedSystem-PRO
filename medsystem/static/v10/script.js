// ══════════════════════════════════════
// VARIÁVEIS GLOBAIS
// ══════════════════════════════════════
let currentUser = null;
let slotSelecionado = '';

// ══════════════════════════════════════
// LOGIN / LOGOUT - INTEGRADO COM BACKEND
// ══════════════════════════════════════
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
  
  if (user.tipo === 'admin') {
    if (typeof carregarUsuarios === 'function') carregarUsuarios();
    if (typeof carregarMedicos === 'function') carregarMedicos();
    carregarEspecialidades(); 
    
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
  document.getElementById('login-senha').value = '';
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
async function carregarDashboard() {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;

    const res = await fetch('/api/dashboard/estatisticas', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const json = await res.json();

    if (json.sucesso) {
      const d = json.dados;
      setMetricValue('consultas_hoje', d.consultas_hoje);
      setMetricValue('pacientes_ativos', d.pacientes_ativos);
      setMetricValue('exames_pendentes', d.exames_pendentes);

      const tbodyDash = document.querySelector('#tabela-dash-consultas tbody')
        || document.querySelector('#agenda-hoje-tbody');
      if (tbodyDash) {
        if (d.ultimas_consultas && d.ultimas_consultas.length > 0) {
          tbodyDash.innerHTML = '';
          d.ultimas_consultas.forEach(c => {
            const cols = tbodyDash.closest('table')?.querySelectorAll('thead th').length || 3;
            if (cols >= 5) {
              tbodyDash.innerHTML += `
                <tr>
                  <td class="td-mono">${c.hora || '—'}</td>
                  <td class="td-name">${c.paciente_nome}</td>
                  <td><span class="badge badge-blue">${c.tipo || 'Consulta'}</span></td>
                  <td><span class="badge badge-amber">${c.status}</span></td>
                  <td><button class="btn btn-ghost btn-sm" onclick="abrirProntuario(${c.id_paciente || 0})">→</button></td>
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
    }

    await carregarExamesPendentes();
    await carregarAlertasDashboard();
  } catch (erro) {
    console.error('Erro no dashboard:', erro);
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
      container.innerHTML = '';
      json.dados.slice(0, 4).forEach(alerta => {
        const dataTexto = alerta.data ? new Date(alerta.data).toLocaleDateString('pt-BR') : 'Data não disponível';
        const isCritico = alerta.gravidade === 'CRITICA' || alerta.gravidade === 'CRÍTICA';
        const dotClass = isCritico ? 'red' : 'amber';

        if (container.classList.contains('timeline')) {
          container.innerHTML += `
            <li class="tl-item">
              <div class="tl-dot ${dotClass}"><svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg></div>
              <div class="tl-content">
                <div class="tl-title">${alerta.paciente} — ${alerta.tipo} <span class="badge badge-${isCritico ? 'red' : 'amber'}" style="margin-left:6px">${alerta.gravidade}</span></div>
                <div class="tl-body">${alerta.descricao || 'Sem descrição adicional.'}</div>
                <div class="tl-date">${dataTexto}</div>
              </div>
            </li>`;
        } else {
          container.innerHTML += `
            <div class="alerta-item ${isCritico ? 'alerta-critico' : 'alerta-grave'}">
              <div class="alerta-icon">${isCritico ? '⚠' : '❗'}</div>
              <div class="alerta-content">
                <div class="alerta-title">${alerta.paciente} — ${alerta.tipo}</div>
                <div class="alerta-text">${alerta.descricao || 'Sem descrição adicional.'}</div>
                <div class="alerta-meta">${dataTexto} · ${alerta.gravidade}</div>
              </div>
            </div>`;
        }
      });
    } else {
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

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${paciente.nome}</td>
          <td>${paciente.cpf}</td>
          <td>${dataFmt}</td>
          <td>${paciente.telefone || '—'}</td>
          <td><button class="btn btn-outline" onclick="abrirProntuario(${idCorreto})">Visualizar</button></td>
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
    const [resPacientes, resMedicos] = await Promise.all([
      fetch('/api/pacientes', { headers }),
      fetch('/api/medicos', { headers })
    ]);

    const jsonPacientes = await resPacientes.json();
    const jsonMedicos = await resMedicos.json();

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
  const endereco = enderecoEl ? enderecoEl.value.trim() : '';
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
        motivo: motivo
      })
    });

    const dados = await res.json();

    if (res.ok && dados.sucesso) {
      showToast('Consulta agendada com sucesso!', 'success');
      limparFormConsulta();
      carregarDashboard(); 
      carregarConsultas(); 
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
  if(obs) obs.value = '';
  document.querySelectorAll('.agenda-slot').forEach(s => s.classList.remove('selected'));
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
        const nomeMed = (c.medico && c.medico.nome) || '—';
        const idCons = c.id || c.id_consulta || '';

        tr.innerHTML = `
          <td class="td-mono">#${String(idCons).padStart(4, '0')}</td>
          <td class="td-name">${nomePac}</td>
          <td class="td-mono">${dataFmt} ${horaFmt}</td>
          <td>${nomeMed}</td>
          <td>${c.motivo || '—'}</td>
          <td><span class="badge badge-amber">${c.status || 'Agendada'}</span></td>
          <td><button class="btn btn-outline btn-sm" onclick="abrirProntuario(${idPac})">Abrir</button></td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (erro) { console.error('Erro ao buscar consultas:', erro); }
}

async function abrirProntuario(idPaciente) {
  // ──── TRAVA DE SEGURANÇA ────
  if (!idPaciente || idPaciente === 'undefined') {
    showToast('Erro interno: O paciente não possui um ID válido.', 'error');
    return;
  }

  // 1. Muda para a tela na mesma hora
  showPage('prontuario');
  
  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`/api/pacientes/${idPaciente}`, { 
        headers: { 'Authorization': 'Bearer ' + token } 
    });
    
    // Verifica se a API deu erro 500 ou 404 antes de ler o JSON
    if (!res.ok) {
        showToast('Erro no servidor ao buscar paciente.', 'error');
        return;
    }

    const json = await res.json();

    if (json.sucesso && json.dados) {
      const p = json.dados;
      
      // TRATAMENTO DE SEGURANÇA: Garante que o nome não seja nulo para não quebrar a tela
      const nomePaciente = p.nome || 'Nome Indisponível';
      
      const nomeEl = document.querySelector('#page-prontuario .patient-name') || document.querySelector('.patient-name');
      const avatarEl = document.querySelector('#page-prontuario .patient-avatar-lg')
        || document.querySelector('.patient-avatar');
      if (nomeEl) nomeEl.textContent = nomePaciente;
      if (avatarEl) avatarEl.textContent = nomePaciente.substring(0, 2).toUpperCase();
      
      const infoVals = document.querySelectorAll('#page-prontuario .info-val');
      if(infoVals.length >= 2) {
          
        // TRATAMENTO DE SEGURANÇA: Garante que o CPF não seja nulo
        let cpfStr = p.cpf || 'N/A';
        // Só aplica o replace se o CPF tiver apenas números e 11 caracteres
        if (cpfStr.length === 11 && !cpfStr.includes('.')) {
            cpfStr = cpfStr.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
        }
        
        infoVals[0].textContent = cpfStr;
        infoVals[1].innerHTML = p.alergias ? `<span class="allergy-tag">⚠ ${p.alergias}</span>` : 'Nenhuma alergia registrada';
      }
    } else {
      showToast('Paciente não encontrado no banco de dados.', 'error');
    }
  } catch (erro) { 
    console.error("Erro interno ao carregar prontuário:", erro);
    showToast('Erro ao carregar prontuário. Verifique o console.', 'error'); 
  }
}

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

    if (res.ok && json.sucesso) {
      showToast('✅ Acesso criado com sucesso!', 'success');
      
      if(typeof limparFormUsuario === 'function') limparFormUsuario();
      
      showPage('usuarios');
      
      if (typeof carregarUsuarios === 'function') carregarUsuarios();
      if (tipo === 'medico' && typeof carregarMedicos === 'function') carregarMedicos();
      if (typeof carregarDadosParaAgendamento === 'function') carregarDadosParaAgendamento();
      
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