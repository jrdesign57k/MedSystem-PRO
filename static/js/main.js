// MedSystem PRO - Main Application Initialization & Event Listeners
// ================================================================

// Track current active page
let currentPage = 'dashboard';

// Initialize app on document ready
document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

/**
 * Initialize application:
 * - Check JWT token
 * - Redirect to login if not authenticated
 * - Load dashboard if authenticated
 * - Setup event listeners
 */
async function initApp() {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    window.location.href = '/login';
    return;
  }
  
  // Set token for API module
  if (window.api) {
    window.api.setToken(token);
  }
  
  // Setup global error handler
  setupErrorHandler();
  
  // Setup all event listeners
  setupEventListeners();
  
  // Load dashboard on page open
  await carregarDashboard();
}

/**
 * Global error handler for unhandled errors
 */
function setupErrorHandler() {
  window.addEventListener('error', handleError);
  
  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
    handleError({
      message: event.reason?.message || 'Erro na operação',
      error: event.reason
    });
  });
}

/**
 * Handle and display errors
 */
function handleError(errorEvent) {
  const errorMessage = errorEvent.message || 'Erro desconhecido';
  const errorSource = errorEvent.filename || 'Unknown source';
  const errorLine = errorEvent.lineno || 0;
  
  console.error(`[ERROR] ${errorMessage} at ${errorSource}:${errorLine}`, errorEvent.error);
  
  // Show error toast to user
  showToast(`Erro: ${errorMessage}`, 'error');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
  // Create toast element
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 16px 24px;
    border-radius: 4px;
    z-index: 9999;
    animation: slideIn 0.3s ease-in-out;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  `;
  
  // Set background color based on type
  const colors = {
    success: '#4CAF50',
    error: '#f44336',
    warning: '#ff9800',
    info: '#2196F3'
  };
  
  toast.style.backgroundColor = colors[type] || colors.info;
  toast.style.color = 'white';
  
  // Add animation styles
  if (!document.querySelector('style[data-toast-styles]')) {
    const style = document.createElement('style');
    style.setAttribute('data-toast-styles', 'true');
    style.textContent = `
      @keyframes slideIn {
        from {
          transform: translateX(400px);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      @keyframes slideOut {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(400px);
          opacity: 0;
        }
      }
      .toast {
        animation: slideOut 0.3s ease-in-out forwards;
        animation-delay: 3s;
      }
    `;
    document.head.appendChild(style);
  }
  
  document.body.appendChild(toast);
  
  // Remove toast after animation
  setTimeout(() => toast.remove(), 3500);
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
  // Navigation buttons (data-page attribute)
  document.querySelectorAll('[data-page]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const pageName = btn.dataset.page;
      switchPage(pageName);
    });
  });
  
  // Logout button
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      handleLogout();
    });
  }
  
  // Login form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      handleLogin();
    });
  }
  
  // Agendar (Schedule) button
  const agendarBtn = document.getElementById('btn-agendar');
  if (agendarBtn) {
    agendarBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchPage('agenda');
      document.getElementById('new-agendamento-form')?.scrollIntoView({ behavior: 'smooth' });
    });
  }
  
  // Nova Consulta button
  const novaConsultaBtn = document.getElementById('btn-nova-consulta');
  if (novaConsultaBtn) {
    novaConsultaBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchPage('consultas');
      document.getElementById('new-consulta-form')?.scrollIntoView({ behavior: 'smooth' });
    });
  }
  
  // Novo Paciente button
  const novoPacienteBtn = document.getElementById('btn-novo-paciente');
  if (novoPacienteBtn) {
    novoPacienteBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchPage('pacientes');
      document.getElementById('new-paciente-form')?.scrollIntoView({ behavior: 'smooth' });
    });
  }
  
  // New form submissions
  const agendamentoForm = document.getElementById('new-agendamento-form');
  if (agendamentoForm) {
    agendamentoForm.addEventListener('submit', (e) => {
      e.preventDefault();
      handleCreateAgendamento();
    });
  }
  
  const consultaForm = document.getElementById('new-consulta-form');
  if (consultaForm) {
    consultaForm.addEventListener('submit', (e) => {
      e.preventDefault();
      handleCreateConsulta();
    });
  }
  
  const pacienteForm = document.getElementById('new-paciente-form');
  if (pacienteForm) {
    pacienteForm.addEventListener('submit', (e) => {
      e.preventDefault();
      handleCreatePaciente();
    });
  }
  
  // Keyboard shortcuts
  setupKeyboardShortcuts();
}

/**
 * Setup keyboard shortcuts
 * F5: Refresh dashboard
 */
function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // F5 to refresh dashboard
    if (e.key === 'F5' || e.keyCode === 116) {
      e.preventDefault();
      if (currentPage === 'dashboard') {
        carregarDashboard();
        showToast('Dashboard atualizado via F5', 'info');
      }
    }
    
    // Ctrl+R or Cmd+R while on dashboard
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
      if (currentPage === 'dashboard') {
        e.preventDefault();
        carregarDashboard();
        showToast('Dashboard atualizado', 'info');
      }
    }
  });
}

/**
 * Switch between pages with smooth transition
 */
function switchPage(pageName) {
  // Hide all pages
  document.querySelectorAll('[data-page-content]').forEach(page => {
    page.style.display = 'none';
    page.style.opacity = '0';
  });
  
  // Show selected page
  const selectedPage = document.getElementById(`page-${pageName}`);
  if (selectedPage) {
    selectedPage.style.display = 'block';
    setTimeout(() => {
      selectedPage.style.opacity = '1';
    }, 10);
    
    // Update active button state
    document.querySelectorAll('[data-page]').forEach(btn => {
      btn.classList.remove('active');
      if (btn.dataset.page === pageName) {
        btn.classList.add('active');
      }
    });
    
    // Update current page and load data
    currentPage = pageName;
    loadPageData(pageName);
  }
}

/**
 * Load data for specific page
 */
async function loadPageData(pageName) {
  try {
    await ensureTokenValid();
    
    switch(pageName) {
      case 'dashboard':
        await carregarDashboard();
        break;
      case 'agenda':
        await carregarAgenda();
        break;
      case 'consultas':
        await carregarConsultas();
        break;
      case 'pacientes':
        await carregarPacientes();
        break;
      case 'relatorios':
        await carregarRelatorios();
        break;
      default:
        console.log(`Page ${pageName} loaded`);
    }
  } catch (error) {
    console.error(`Erro ao carregar página ${pageName}:`, error);
    showToast(`Erro ao carregar dados: ${error.message}`, 'error');
  }
}

/**
 * Ensure JWT token is valid, refresh if needed
 */
async function ensureTokenValid() {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    window.location.href = '/login';
    throw new Error('Token não encontrado');
  }
  
  // Decode token to check expiration
  const payload = parseJwt(token);
  
  if (!payload) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
    throw new Error('Token inválido');
  }
  
  const expiryTime = payload.exp * 1000;
  const currentTime = Date.now();
  const timeUntilExpiry = expiryTime - currentTime;
  
  // If token expires in less than 5 minutes, refresh it
  if (timeUntilExpiry < 5 * 60 * 1000) {
    await refreshToken();
  }
}

/**
 * Refresh JWT token
 */
async function refreshToken() {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('Refresh token não encontrado');
    }
    
    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    if (!response.ok) {
      throw new Error('Falha ao renovar token');
    }
    
    const data = await response.json();
    
    localStorage.setItem('access_token', data.access_token);
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }
    
    if (window.api) {
      window.api.setToken(data.access_token);
    }
  } catch (error) {
    console.error('Erro ao renovar token:', error);
    handleLogout();
    throw error;
  }
}

/**
 * Parse JWT token
 */
function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map((c) => {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Erro ao parsear JWT:', error);
    return null;
  }
}

/**
 * Load dashboard data from backend API
 * Fetches metrics, pending exams, and upcoming appointments
 */
async function carregarDashboard() {
  try {
    if (!window.api) {
      console.error('API module not available');
      showToast('Erro: API module not available', 'error');
      return;
    }
    
    showLoading('Carregando dashboard...');
    
    // Call backend API
    const data = await window.api.getDashboard();
    
    if (!data || !data.sucesso) {
      throw new Error('Falha ao carregar dashboard');
    }
    
    // ═══════════════════════════════════
    // UPDATE METRIC CARDS
    // ═══════════════════════════════════
    const updateMetric = (metricName, value) => {
      const element = document.querySelector(`[data-metric="${metricName}"]`);
      if (element) {
        element.textContent = value || 0;
      }
    };
    
    updateMetric('consultas_hoje', data.metricas.consultas_hoje);
    updateMetric('pacientes_ativos', data.metricas.pacientes_ativos);
    updateMetric('exames_pendentes', data.metricas.exames_pendentes);
    updateMetric('novos_pacientes', data.metricas.novos_pacientes);
    
    // Update page subtitle with date
    const hojeSubElement = document.getElementById('hoje-sub');
    if (hojeSubElement && data.data) {
      const dayName = getDayName(new Date());
      hojeSubElement.textContent = `Visão geral de ${dayName}, ${data.data}`;
    }
    
    // ═══════════════════════════════════
    // UPDATE EXAMES PENDENTES TABLE
    // ═══════════════════════════════════
    const examesTableBody = document.getElementById('exames-pendentes-tbody');
    if (examesTableBody && data.exames_pendentes && data.exames_pendentes.length > 0) {
      examesTableBody.innerHTML = data.exames_pendentes.map(exame => {
        const priorityClass = getPriorityClass(exame.prioridade);
        const priorityColor = getPriorityColor(exame.prioridade);
        const statusBadgeClass = getStatusBadgeClass(exame.status);
        
        return `
          <tr>
            <td class="td-name">${exame.paciente || 'N/A'}</td>
            <td class="text-sm">${exame.exame || 'N/A'}</td>
            <td><span class="badge badge-${priorityClass}">${exame.prioridade}</span></td>
            <td>${formatData(exame.data_solicitacao) || 'N/A'}</td>
            <td><span class="badge badge-${statusBadgeClass}">${exame.status}</span></td>
          </tr>
        `;
      }).join('');
    } else if (examesTableBody) {
      examesTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text3);">Nenhum exame pendente</td></tr>';
    }
    
    // ═══════════════════════════════════
    // UPDATE PRÓXIMOS RETORNOS TIMELINE
    // ═══════════════════════════════════
    const timelineContainer = document.getElementById('proximos-retornos-timeline');
    if (timelineContainer && data.proximos_retornos && data.proximos_retornos.length > 0) {
      timelineContainer.innerHTML = data.proximos_retornos.map((retorno, index) => {
        const colors = ['blue', 'green', 'amber', 'purple', 'teal'];
        const dotColor = colors[index % colors.length];
        
        return `
          <li class="tl-item">
            <div class="tl-dot ${dotColor}">
              <svg viewBox="0 0 24 24">
                <rect x="3" y="4" width="18" height="18" rx="2"/>
                <path d="M16 2v4M8 2v4M3 10h18"/>
              </svg>
            </div>
            <div class="tl-content">
              <div class="tl-title">${retorno.paciente || 'N/A'}</div>
              <div class="tl-body">${retorno.motivo || 'Consulta'} · ${retorno.medico || 'Médico'}</div>
              <div class="tl-date">${retorno.data || 'N/A'} · ${retorno.hora || 'Horário'}</div>
            </div>
          </li>
        `;
      }).join('');
    } else if (timelineContainer) {
      timelineContainer.innerHTML = '<li style="padding:16px;text-align:center;color:var(--text3);">Nenhum retorno agendado</li>';
    }
    
    hideLoading();
    showToast('Dashboard atualizado com sucesso', 'success');
    
  } catch (error) {
    hideLoading();
    console.error('Erro ao carregar dashboard:', error);
    showToast(`Erro ao carregar dashboard: ${error.message}`, 'error');
  }
}

/**
 * Get Portuguese day name from date
 */
function getDayName(date) {
  const days = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
  return days[date.getDay()];
}

/**
 * Get CSS class for priority badge based on prioridade value
 */
function getPriorityClass(prioridade) {
  if (!prioridade) return 'gray';
  
  const priorityLower = prioridade.toLowerCase();
  if (priorityLower.includes('urgente')) return 'red';
  if (priorityLower.includes('normal') || priorityLower.includes('média')) return 'amber';
  if (priorityLower.includes('baixa')) return 'green';
  
  return 'gray';
}

/**
 * Get color for priority badge
 */
function getPriorityColor(prioridade) {
  const priorityLower = prioridade?.toLowerCase() || '';
  if (priorityLower.includes('urgente')) return 'var(--red-light)';
  if (priorityLower.includes('normal') || priorityLower.includes('média')) return 'var(--amber-light)';
  if (priorityLower.includes('baixa')) return 'var(--green-light)';
  
  return 'var(--text3)';
}

/**
 * Get CSS class for status badge
 */
function getStatusBadgeClass(status) {
  if (!status) return 'gray';
  
  const statusLower = status.toLowerCase();
  if (statusLower.includes('solicitado')) return 'blue';
  if (statusLower.includes('aguardando') || statusLower.includes('análise')) return 'amber';
  if (statusLower.includes('completo') || statusLower.includes('realizado')) return 'green';
  if (statusLower.includes('cancelado')) return 'red';
  
  return 'gray';
}

/**
 * Load agenda data
 */
async function carregarAgenda() {
  try {
    if (!window.api) {
      console.error('API module not available');
      return;
    }
    
    const data = await window.api.getAgenda();
    
    const agendaList = document.getElementById('agenda-list');
    if (agendaList) {
      agendaList.innerHTML = '';
      
      if (data.agendamentos && data.agendamentos.length > 0) {
        data.agendamentos.forEach(agendamento => {
          const item = document.createElement('div');
          item.className = 'agenda-item';
          item.innerHTML = `
            <div class="agenda-info">
              <h4>${agendamento.paciente_nome || 'N/A'}</h4>
              <p>${agendamento.data} - ${agendamento.hora}</p>
              <p class="agenda-observacoes">${agendamento.observacoes || ''}</p>
            </div>
            <div class="agenda-actions">
              <button class="btn-small" onclick="editarAgendamento(${agendamento.id})">Editar</button>
              <button class="btn-small btn-danger" onclick="deletarAgendamento(${agendamento.id})">Deletar</button>
            </div>
          `;
          agendaList.appendChild(item);
        });
      } else {
        agendaList.innerHTML = '<p>Nenhum agendamento encontrado</p>';
      }
    }
    
    showToast('Agenda carregada com sucesso', 'success');
  } catch (error) {
    console.error('Erro ao carregar agenda:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Load consultas data
 */
async function carregarConsultas() {
  try {
    if (!window.api) {
      console.error('API module not available');
      return;
    }
    
    const data = await window.api.getConsultas();
    
    const consultasList = document.getElementById('consultas-list');
    if (consultasList) {
      consultasList.innerHTML = '';
      
      if (data.consultas && data.consultas.length > 0) {
        data.consultas.forEach(consulta => {
          const item = document.createElement('div');
          item.className = 'consulta-item';
          item.innerHTML = `
            <div class="consulta-info">
              <h4>${consulta.paciente_nome || 'N/A'}</h4>
              <p>Data: ${consulta.data}</p>
              <p>Especialidade: ${consulta.especialidade || 'N/A'}</p>
              <p class="consulta-diagnostico">${consulta.diagnostico || 'Sem diagnóstico'}</p>
            </div>
            <div class="consulta-actions">
              <button class="btn-small" onclick="editarConsulta(${consulta.id})">Editar</button>
              <button class="btn-small btn-danger" onclick="deletarConsulta(${consulta.id})">Deletar</button>
            </div>
          `;
          consultasList.appendChild(item);
        });
      } else {
        consultasList.innerHTML = '<p>Nenhuma consulta encontrada</p>';
      }
    }
    
    showToast('Consultas carregadas com sucesso', 'success');
  } catch (error) {
    console.error('Erro ao carregar consultas:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Load pacientes data
 */
async function carregarPacientes() {
  try {
    if (!window.api) {
      console.error('API module not available');
      return;
    }
    
    const data = await window.api.getPacientes();
    
    const pacientesList = document.getElementById('pacientes-list');
    if (pacientesList) {
      pacientesList.innerHTML = '';
      
      if (data.pacientes && data.pacientes.length > 0) {
        data.pacientes.forEach(paciente => {
          const item = document.createElement('div');
          item.className = 'paciente-item';
          item.innerHTML = `
            <div class="paciente-info">
              <h4>${paciente.nome || 'N/A'}</h4>
              <p>CPF: ${paciente.cpf || 'N/A'}</p>
              <p>Telefone: ${paciente.telefone || 'N/A'}</p>
              <p>Email: ${paciente.email || 'N/A'}</p>
            </div>
            <div class="paciente-actions">
              <button class="btn-small" onclick="editarPaciente(${paciente.id})">Editar</button>
              <button class="btn-small btn-danger" onclick="deletarPaciente(${paciente.id})">Deletar</button>
            </div>
          `;
          pacientesList.appendChild(item);
        });
      } else {
        pacientesList.innerHTML = '<p>Nenhum paciente encontrado</p>';
      }
    }
    
    showToast('Pacientes carregados com sucesso', 'success');
  } catch (error) {
    console.error('Erro ao carregar pacientes:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Load relatórios data
 */
async function carregarRelatorios() {
  try {
    if (!window.api) {
      console.error('API module not available');
      return;
    }
    
    const data = await window.api.getRelatorios();
    
    // Render charts if available
    if (typeof renderRelatorioCharts === 'function') {
      renderRelatorioCharts(data);
    }
    
    showToast('Relatórios carregados com sucesso', 'success');
  } catch (error) {
    console.error('Erro ao carregar relatórios:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Handle login
 */
async function handleLogin() {
  try {
    const emailInput = document.getElementById('login-email');
    const senhaInput = document.getElementById('login-senha');
    
    if (!emailInput || !senhaInput) {
      showToast('Formulário de login não encontrado', 'error');
      return;
    }
    
    const email = emailInput.value.trim();
    const senha = senhaInput.value;
    
    if (!email || !senha) {
      showToast('Email e senha são obrigatórios', 'warning');
      return;
    }
    
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, senha })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Falha ao fazer login');
    }
    
    const data = await response.json();
    
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    if (window.api) {
      window.api.setToken(data.access_token);
    }
    
    showToast('Login realizado com sucesso!', 'success');
    
    setTimeout(() => {
      window.location.href = '/';
    }, 1000);
  } catch (error) {
    console.error('Erro ao fazer login:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Handle logout
 */
function handleLogout() {
  if (confirm('Tem certeza que deseja fazer logout?')) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    showToast('Logout realizado com sucesso', 'success');
    
    setTimeout(() => {
      window.location.href = '/login';
    }, 1000);
  }
}

/**
 * Handle create agendamento
 */
async function handleCreateAgendamento() {
  try {
    await ensureTokenValid();
    
    const pacienteInput = document.getElementById('agendamento-paciente');
    const dataInput = document.getElementById('agendamento-data');
    const horaInput = document.getElementById('agendamento-hora');
    const observacoesInput = document.getElementById('agendamento-observacoes');
    
    if (!pacienteInput || !dataInput || !horaInput) {
      showToast('Formulário incompleto', 'warning');
      return;
    }
    
    const formData = {
      paciente_id: pacienteInput.value,
      data: dataInput.value,
      hora: horaInput.value,
      observacoes: observacoesInput?.value || ''
    };
    
    if (!window.api) {
      throw new Error('API module not available');
    }
    
    await window.api.createAgendamento(formData);
    
    showToast('Agendamento criado com sucesso!', 'success');
    
    document.getElementById('new-agendamento-form').reset();
    await carregarAgenda();
  } catch (error) {
    console.error('Erro ao criar agendamento:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Handle create consulta
 */
async function handleCreateConsulta() {
  try {
    await ensureTokenValid();
    
    const pacienteInput = document.getElementById('consulta-paciente');
    const dataInput = document.getElementById('consulta-data');
    const especialidadeInput = document.getElementById('consulta-especialidade');
    const diagnosticoInput = document.getElementById('consulta-diagnostico');
    
    if (!pacienteInput || !dataInput || !especialidadeInput) {
      showToast('Formulário incompleto', 'warning');
      return;
    }
    
    const formData = {
      paciente_id: pacienteInput.value,
      data: dataInput.value,
      especialidade: especialidadeInput.value,
      diagnostico: diagnosticoInput?.value || ''
    };
    
    if (!window.api) {
      throw new Error('API module not available');
    }
    
    await window.api.createConsulta(formData);
    
    showToast('Consulta criada com sucesso!', 'success');
    
    document.getElementById('new-consulta-form').reset();
    await carregarConsultas();
  } catch (error) {
    console.error('Erro ao criar consulta:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Handle create paciente
 */
async function handleCreatePaciente() {
  try {
    await ensureTokenValid();
    
    const nomeInput = document.getElementById('paciente-nome');
    const cpfInput = document.getElementById('paciente-cpf');
    const emailInput = document.getElementById('paciente-email');
    const telefoneInput = document.getElementById('paciente-telefone');
    
    if (!nomeInput || !cpfInput || !emailInput) {
      showToast('Formulário incompleto', 'warning');
      return;
    }
    
    const formData = {
      nome: nomeInput.value,
      cpf: cpfInput.value,
      email: emailInput.value,
      telefone: telefoneInput?.value || ''
    };
    
    if (!window.api) {
      throw new Error('API module not available');
    }
    
    await window.api.createPaciente(formData);
    
    showToast('Paciente criado com sucesso!', 'success');
    
    document.getElementById('new-paciente-form').reset();
    await carregarPacientes();
  } catch (error) {
    console.error('Erro ao criar paciente:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Editar agendamento
 */
async function editarAgendamento(id) {
  showToast('Funcionalidade em desenvolvimento', 'info');
}

/**
 * Deletar agendamento
 */
async function deletarAgendamento(id) {
  if (!confirm('Tem certeza que deseja deletar este agendamento?')) return;
  
  try {
    await ensureTokenValid();
    
    if (!window.api) {
      throw new Error('API module not available');
    }
    
    await window.api.deleteAgendamento(id);
    
    showToast('Agendamento deletado com sucesso!', 'success');
    await carregarAgenda();
  } catch (error) {
    console.error('Erro ao deletar agendamento:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Editar consulta
 */
async function editarConsulta(id) {
  showToast('Funcionalidade em desenvolvimento', 'info');
}

/**
 * Deletar consulta
 */
async function deletarConsulta(id) {
  if (!confirm('Tem certeza que deseja deletar esta consulta?')) return;
  
  try {
    await ensureTokenValid();
    
    if (!window.api) {
      throw new Error('API module not available');
    }
    
    await window.api.deleteConsulta(id);
    
    showToast('Consulta deletada com sucesso!', 'success');
    await carregarConsultas();
  } catch (error) {
    console.error('Erro ao deletar consulta:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

/**
 * Editar paciente
 */
async function editarPaciente(id) {
  showToast('Funcionalidade em desenvolvimento', 'info');
}

/**
 * Deletar paciente
 */
async function deletarPaciente(id) {
  if (!confirm('Tem certeza que deseja deletar este paciente?')) return;
  
  try {
    await ensureTokenValid();
    
    if (!window.api) {
      throw new Error('API module not available');
    }
    
    await window.api.deletePaciente(id);
    
    showToast('Paciente deletado com sucesso!', 'success');
    await carregarPacientes();
  } catch (error) {
    console.error('Erro ao deletar paciente:', error);
    showToast(`Erro: ${error.message}`, 'error');
  }
}

// Make functions global for HTML onclick attributes
window.editarAgendamento = editarAgendamento;
window.deletarAgendamento = deletarAgendamento;
window.editarConsulta = editarConsulta;
window.deletarConsulta = deletarConsulta;
window.editarPaciente = editarPaciente;
window.deletarPaciente = deletarPaciente;
window.switchPage = switchPage;
window.handleLogout = handleLogout;
