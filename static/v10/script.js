// ══════════════════════════════════════
// VARIÁVEIS GLOBAIS
// ══════════════════════════════════════
let currentUser = null;
let slotSelecionado = '';

// ══════════════════════════════════════
// LOGIN / LOGOUT - INTEGRADO COM BACKEND
// ══════════════════════════════════════
function doLogin() {
  const email = document.getElementById('login-email').value.trim().toLowerCase();
  const senha = document.getElementById('login-senha').value;
  const errEl = document.getElementById('login-error');
  const btn   = document.getElementById('login-btn');

  errEl.style.display = 'none';
  document.getElementById('login-email').classList.remove('error');
  document.getElementById('login-senha').classList.remove('error');

  if (!email || !senha) {
    errEl.style.display = 'block';
    errEl.textContent = '⚠ Preencha e-mail e senha para continuar.';
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Verificando...';

  fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, senha })
  })
  .then(response => response.json())
  .then(data => {
    if (data.sucesso) {
      localStorage.setItem('token', data.token);
      localStorage.setItem('usuario', JSON.stringify(data.usuario));
      
      currentUser = data.usuario;
      loginSuccess(data.usuario);
    } else {
      errEl.style.display = 'block';
      errEl.textContent = '⚠ ' + data.mensagem;
      document.getElementById('login-email').classList.add('error');
      document.getElementById('login-senha').classList.add('error');
      btn.disabled = false;
      btn.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" style="stroke:#fff;fill:none"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4M10 17l5-5-5-5M15 12H3"/></svg> Entrar no sistema';
    }
  })
  .catch(error => {
    console.error('Erro:', error);
    errEl.style.display = 'block';
    errEl.textContent = '⚠ Erro ao conectar com servidor. Tente novamente.';
    btn.disabled = false;
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" style="stroke:#fff;fill:none"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4M10 17l5-5-5-5M15 12H3"/></svg> Entrar no sistema';
  });
}

function loginSuccess(user) {
  const sbAvatar = document.getElementById('sidebar-avatar');
  const sbName = document.getElementById('sidebar-name');
  const sbRole = document.getElementById('sidebar-role');
  
  // ──── CORREÇÃO AQUI: Lendo os dados diretos do primeiro nível mapeado no Flask ────
  const pCrmInput = document.getElementById('p-crm');
  const pEspInput = document.getElementById('p-esp');
  
  if (pCrmInput) pCrmInput.value = user.crm || 'N/A';
  if (pEspInput) pEspInput.value = user.especialidade || 'N/A';
  
  if (sbAvatar) sbAvatar.textContent = user.iniciais || user.nome.substring(0, 2).toUpperCase();
  if (sbName) sbName.textContent = user.nome;
  if (sbRole) sbRole.textContent = user.tipo || 'Usuário';

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
  
  // Ajustado para mostrar a especialidade em vez do e-mail no subtítulo do perfil se for médico
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
  if (appScreen) appScreen.style.display = 'block';

  showToast('Bem-vindo, ' + user.nome + '! 👋', 'success');
  showPage('dashboard');

  carregarDashboard();
  carregarPacientes();
  carregarDadosParaAgendamento();
  carregarConsultas(); 
  
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
  
  document.getElementById('app-screen').style.display = 'none';
  document.getElementById('login-screen').style.display = 'flex';
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
      const elCons = document.getElementById('dash-consultas');
      const elPacs = document.getElementById('dash-pacientes');
      const elExams = document.getElementById('dash-exames');
      
      if(elCons) elCons.textContent = d.consultas_hoje;
      if(elPacs) elPacs.textContent = d.pacientes_ativos;
      if(elExams) elExams.textContent = d.exames_pendentes;

      if (d.ultimas_consultas && d.ultimas_consultas.length > 0) {
        const tbodyDash = document.querySelector('#tabela-dash-consultas tbody');
        if (tbodyDash) {
          tbodyDash.innerHTML = '';
          d.ultimas_consultas.forEach(c => {
            tbodyDash.innerHTML += `
              <tr>
                <td class="td-name">${c.paciente_nome}</td>
                <td class="td-mono">${c.hora}</td>
                <td><span class="badge badge-blue">${c.status}</span></td>
              </tr>
            `;
          });
        }
      } else {
        const tbodyDash = document.querySelector('#tabela-dash-consultas tbody');
        if (tbodyDash) {
          tbodyDash.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #999;">Nenhuma consulta agendada para hoje</td></tr>';
        }
      }
    }
  } catch (erro) {
    console.error('Erro no dashboard:', erro);
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

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${paciente.nome}</td>
          <td>${paciente.cpf}</td>
          <td>${dataFmt}</td>
          <td>${paciente.telefone || '—'}</td>
          <td><button class="btn btn-outline" onclick="abrirProntuario(${paciente.id})">Visualizar</button></td>
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
  const endereco = document.getElementById('np-endereco') ? document.getElementById('np-endereco').value.trim() : '';
  const alergias = document.getElementById('np-alergias') ? document.getElementById('np-alergias').value.trim() : '';
  const observacoes = document.getElementById('np-observacoes') ? document.getElementById('np-observacoes').value.trim() : '';
  
  // Sinais Vitais (Opcionais)
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
        // Sinais Vitais
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
      
      // Limpar formulário
      document.getElementById('np-nome').value = '';
      document.getElementById('np-cpf').value = '';
      document.getElementById('np-nasc').value = '';
      document.getElementById('np-sexo').value = '';
      if (document.getElementById('np-tel')) document.getElementById('np-tel').value = '';
      if (document.getElementById('np-email')) document.getElementById('np-email').value = '';
      if (document.getElementById('np-sangue')) document.getElementById('np-sangue').value = '';
      if (document.getElementById('np-endereco')) document.getElementById('np-endereco').value = '';
      if (document.getElementById('np-alergias')) document.getElementById('np-alergias').value = '';
      if (document.getElementById('np-observacoes')) document.getElementById('np-observacoes').value = '';
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
  // Remove tudo que não for número ou letra (permite números e a sigla do estado)
  let v = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
  
  // Limita o tamanho máximo em 12 caracteres de forma programática
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

const d = new Date();
const dias = ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];
const hojeElement = document.getElementById('hoje');
if (hojeElement) {
    hojeElement.textContent = dias[d.getDay()] + ', ' + d.toLocaleDateString('pt-BR', {day:'2-digit',month:'long',year:'numeric'});
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
        const dataFmt = new Date(c.data_consulta).toLocaleDateString('pt-BR');
        const horaFmt = c.hora_consulta || '—';
        tr.innerHTML = `
          <td class="td-name">${c.paciente.nome}</td>
          <td class="td-mono">${dataFmt}</td>
          <td class="td-mono">${horaFmt}</td>
          <td>${c.medico.nome}</td>
          <td>${c.motivo}</td>
          <td><span class="badge badge-amber">${c.status || 'Agendada'}</span></td>
          <td><button class="btn btn-outline" onclick="abrirProntuario(${c.paciente.id})">Abrir</button></td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (erro) { console.error('Erro ao buscar consultas:', erro); }
}

async function abrirProntuario(idPaciente) {
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
      
      document.querySelector('.patient-name').textContent = nomePaciente;
      document.querySelector('.patient-avatar').textContent = nomePaciente.substring(0,2).toUpperCase();
      
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