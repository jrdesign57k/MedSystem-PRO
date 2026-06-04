/**
 * MedSystem PRO - API Client
 * Centralized API client for all backend endpoints
 * Handles JWT authentication, error handling, and request management
 */

class APIClient {
  // CORREÇÃO: Lê a constante injetada dinamicamente pelo Terraform
  constructor(baseURL = window.API_URL || '/api') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('access_token');
  }

  /**
   * Core request method - handles all API calls with auth header
   * @param {string} endpoint - API endpoint path
   * @param {object} options - fetch options (method, body, headers, etc)
   * @returns {Promise<object>} - JSON response
   * @throws {Error} - If response is not ok
   */
  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` })
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: { ...headers, ...options.headers }
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} ${response.statusText} - ${error}`);
    }

    return response.json();
  }

  /**
   * Token Management Methods
   */

  setToken(token) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  getToken() {
    return this.token || localStorage.getItem('access_token');
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  /**
   * ============================================
   * AUTH ENDPOINTS
   * ============================================
   */

  async login(email, senha) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, senha })
    });
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  }

  async logout() {
    this.clearToken();
    return this.request('/auth/logout', { method: 'POST' });
  }

  async refreshToken() {
    const data = await this.request('/auth/refresh', { method: 'POST' });
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    return data;
  }

  /**
   * ============================================
   * PACIENTES ENDPOINTS
   * ============================================
   */

  async getPaciente(paciente_id) {
    return this.request(`/pacientes/${paciente_id}`, { method: 'GET' });
  }

  async createPaciente(data) {
    return this.request('/pacientes', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updatePaciente(paciente_id, data) {
    return this.request(`/pacientes/${paciente_id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  /**
   * ============================================
   * CONSULTAS ENDPOINTS
   * ============================================
   */

  async getConsultas(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/consultas${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async getConsulta(consulta_id) {
    return this.request(`/consultas/${consulta_id}`, { method: 'GET' });
  }

  async createConsulta(data) {
    return this.request('/consultas', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateConsulta(consulta_id, data) {
    return this.request(`/consultas/${consulta_id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  /**
   * ============================================
   * EXAMES ENDPOINTS
   * ============================================
   */

  async getExames(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/exames${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async createExame(data) {
    return this.request('/exames', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateExame(exame_id, data) {
    return this.request(`/exames/${exame_id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  /**
   * ============================================
   * PRONTUARIOS ENDPOINTS
   * ============================================
   */

  async createProntuario(data) {
    return this.request('/prontuarios', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateProntuario(prontuario_id, data) {
    return this.request(`/prontuarios/${prontuario_id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async getProntuario(prontuario_id) {
    return this.request(`/prontuarios/${prontuario_id}`, { method: 'GET' });
  }

  /**
   * ============================================
   * FINANCEIRO (FINANCIAL) ENDPOINTS
   * ============================================
   */

  async getFinanceiro(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/financeiro${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async getReceitas(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/financeiro/receitas${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async postReceita(data) {
    return this.request('/financeiro/receitas', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async getDespesas(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/financeiro/despesas${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async postDespesa(data) {
    return this.request('/financeiro/despesas', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  /**
   * ============================================
   * RELATORIOS (REPORTS) ENDPOINTS
   * ============================================
   */

  async getRelatorios(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/relatorios${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async getRelatoriosDialo(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/relatorios/diario${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async getRelatoriosSemanal(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/relatorios/semanal${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async getRelatoriosMensal(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/relatorios/mensal${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  /**
   * ============================================
   * CID10 ENDPOINTS
   * ============================================
   */

  async searchCID10(query) {
    const params = new URLSearchParams({ q: query }).toString();
    return this.request(`/cid10/search?${params}`, { method: 'GET' });
  }

  /**
   * ============================================
   * MENSAGENS (MESSAGES) ENDPOINTS
   * ============================================
   */

  async getConversas(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/mensagens/conversas${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async enviarMensagem(data) {
    return this.request('/mensagens/enviar', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async marcarLido(mensagem_id) {
    return this.request(`/mensagens/${mensagem_id}/lido`, {
      method: 'PUT'
    });
  }

  /**
   * ============================================
   * DASHBOARD ENDPOINTS
   * ============================================
   */

  async getDashboard(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/dashboard${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  async getAgendaSemana(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/dashboard/agenda-semana${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }

  /**
   * ============================================
   * MEDICOS (DOCTORS) ENDPOINTS
   * ============================================
   */

  async getMedicos(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    return this.request(`/medicos${queryParams ? '?' + queryParams : ''}`, { method: 'GET' });
  }
}

window.api = new APIClient();

if (typeof module !== 'undefined' && module.exports) {
  module.exports = APIClient;
}