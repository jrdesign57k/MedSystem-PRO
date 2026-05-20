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
  // Atualiza sidebar (apenas se os elementos existirem)
  const sbAvatar = document.getElementById('sidebar-avatar');
  const sbName = document.getElementById('sidebar-name');
  const sbRole = document.getElementById('sidebar-role');
  
  if (sbAvatar) sbAvatar.textContent = user.iniciais || user.nome.substring(0, 2).toUpperCase();
  if (sbName) sbName.textContent = user.nome;
  if (sbRole) sbRole.textContent = user.tipo || 'Usuário';

  // Atualiza perfil (apenas se os elementos existirem)
  const pfAvatar = document.getElementById('perfil-avatar-lg');
  const pfNome = document.getElementById('perfil-nome-display');
  const pfRole = document.getElementById('perfil-role-display');
  const pfEsp = document.getElementById('perfil-esp-display');
  const pNomeInput = document.getElementById('p-nome');
  const pEmailInput = document.getElementById('p-email');

  if (pfAvatar) pfAvatar.textContent = user.iniciais || user.nome.substring(0, 2).toUpperCase();
  if (pfNome) pfNome.textContent = user.nome;
  if (pfRole) pfRole.textContent = (user.tipo || 'Usuário') + ' • ID ' + user.id;
  if (pfEsp) pfEsp.textContent = user.email;
  if (pNomeInput) pNomeInput.value = user.nome;
  if (pEmailInput) pEmailInput.value = user.email;

  // Elementos de Sessão Opcionais (Evita o travamento se não estiverem no HTML)
  const sessaoEmail = document.getElementById('sessao-email');
  const sessaoHora = document.getElementById('sessao-hora');
  if (sessaoEmail) sessaoEmail.textContent = user.email;
  if (sessaoHora) sessaoHora.textContent = new Date().toLocaleTimeString('pt-BR');

  // Troca de tela de forma segura
  const loginScreen = document.getElementById('login-screen');
  const appScreen = document.getElementById('app-screen');
  
  if (loginScreen) loginScreen.style.display = 'none';
  if (appScreen) appScreen.style.display = 'block';

  showToast('Bem-vindo, ' + user.nome + '! 👋', 'success');
  showPage('dashboard');

  // Carrega os dados reais das APIs do banco MySQL
  carregarDashboard();
  carregarPacientes();
  carregarDadosParaAgendamento();
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
          <td><button class="btn btn-outline" onclick="showToast('Abrindo prontuário...', '')">Visualizar</button></td>
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
          selectMed.innerHTML += `<option value="${m.id}">Dr(a). ${m.usuario.nome} (${m.especialidade.nome})</option>`;
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
// ══════════════════════════════════════
// NOVO PACIENTE (POST) - VERSÃO CORRIGIDA
// ══════════════════════════════════════
async function cadastrarPaciente() {
  const nome = document.getElementById('np-nome').value.trim();
  let cpf   = document.getElementById('np-cpf').value.trim();
  const nasc = document.getElementById('np-nasc').value; // Formato padrão: YYYY-MM-DD
  
  const tel  = document.getElementById('np-tel') ? document.getElementById('np-tel').value.trim() : '';
  const email = document.getElementById('np-email') ? document.getElementById('np-email').value.trim() : '';

  // Validação básica no front
  if (!nome || !cpf || !nasc) {
    showToast('Preencha os campos obrigatórios (*)', 'error'); 
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
        cpf: cpf.replace(/\D/g, ''), // Remove pontos e traços do CPF para não quebrar o banco
        data_nascimento: nasc, // Mantém YYYY-MM-DD
        telefone: tel.replace(/\D/g, ''), // Remove parênteses e espaços do telefone
        email: email,
        sexo: 'M',
        ativo: true
      })
    });

    // ... (código do fetch continua igual)
    const dados = await res.json();
    
    if (res.ok) {
      // 1. Mostra o sucesso
      showToast('Paciente cadastrado com sucesso!', 'success');
      
      // 2. Limpa os campos da tela de forma segura (ignorando se algum não existir)
      document.getElementById('np-nome').value = '';
      document.getElementById('np-cpf').value = '';
      document.getElementById('np-nasc').value = '';
      document.getElementById('np-sexo').value = 'M';
      if (document.getElementById('np-tel')) document.getElementById('np-tel').value = '';
      
      // 3. Atualiza a lista de pacientes no background e muda a tela
      if (typeof carregarPacientes === 'function') {
        carregarPacientes();
      }
      showPage('pacientes'); // Volta para a tabela
      
    } else {
      showToast('Erro: ' + (dados.mensagem || 'Falha ao cadastrar'), 'error');
    }
  } catch (erro) {
    // Se der erro, printa no F12 para sabermos exatamente a linha que quebrou!
    console.error("Erro interno no JavaScript:", erro);
    showToast('Erro de processamento na tela.', 'error');
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
  const motivo = document.getElementById('nc-motivo').value.trim();
  
  if (!pacId || !medId || !data || !motivo) {
    showToast('Preencha todos os campos obrigatórios (*)', 'error'); 
    return;
  }
  
  const hora = slotSelecionado || '00:00';
  // Backend espera formato ISO (ex: "2025-05-20T14:00:00")
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
        motivo: motivo
      })
    });

    const dados = await res.json();

    if (res.ok && dados.sucesso) {
      showToast('Consulta agendada com sucesso!', 'success');
      limparFormConsulta();
      carregarDashboard(); // Atualiza contador de consultas no painel
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

// DATA ATUAL NA BARRA SUPERIOR
const d = new Date();
const dias = ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];
document.getElementById('hoje').textContent =
  dias[d.getDay()] + ', ' + d.toLocaleDateString('pt-BR', {day:'2-digit',month:'long',year:'numeric'});

function showToast(msg, type) {
  const area = document.getElementById('toastArea');
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
// PERFIL
// ══════════════════════════════════════
function salvarPerfil() {
  const nome = document.getElementById('p-nome').value.trim();
  if (!nome) { showToast('O nome não pode estar vazio.', 'error'); return; }
  document.getElementById('perfil-nome-display').textContent = nome;
  document.getElementById('sidebar-name').textContent = nome;
  showToast('Perfil atualizado com sucesso!', 'success');
}

function alterarSenha() {
  const atual = document.getElementById('p-senha-atual').value;
  const nova  = document.getElementById('p-senha-nova').value;
  const conf  = document.getElementById('p-senha-conf').value;
  if (!atual || !nova || !conf) { showToast('Preencha todos os campos de senha.', 'error'); return; }
  if (nova !== conf) { showToast('A nova senha e a confirmação não coincidem.', 'error'); return; }
  if (nova.length < 6) { showToast('A nova senha deve ter pelo menos 6 caracteres.', 'error'); return; }
  // Integração com rota de alterar senha deve ser feita aqui (opcional no momento)
  document.getElementById('p-senha-atual').value = '';
  document.getElementById('p-senha-nova').value = '';
  document.getElementById('p-senha-conf').value = '';
  showToast('Senha alterada com sucesso!', 'success');
}