# MedSystem PRO - Próximos Passos de Implementação

## 🎯 Objetivo
Integrar o frontend (index_pro.html) com o backend (APIs Flask) para uma aplicação funcional completa.

---

## ✅ O Que Já Foi Feito

### Backend (100% completo)
- ✅ Modelos SQLAlchemy expandidos (Consulta, Prescricao, Exame, Diagnóstico + 5 novos)
- ✅ 11 blueprints de rotas implementadas com autenticação JWT
- ✅ CID-10 reference table com 20+ diagnoses
- ✅ Documentação completa (README_PRO.md, QUICK_START.md)

### Frontend (HTML/CSS/JS fornecido pelo usuário)
- ✅ Interface de 10 módulos em `templates/index_pro.html`
- ✅ Styling completo com CSS variables
- ⏳ **Falta**: Integração com APIs via JavaScript

---

## ⏳ Próximos Passos (Prioridade)

### FASE 1: Conectar Frontend aos Endpoints (2-3 horas)

#### 1.1 Criar `static/js/api.js` - Camada de comunicação com API
```javascript
// static/js/api.js - Gateway para todas as APIs
class APIClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('access_token');
  }

  // Métodos auxiliares
  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` })
    };
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: { ...headers, ...options.headers }
    });
    
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return response.json();
  }

  // Dashboard
  getDashboard() { return this.request('/dashboard'); }
  getAgendaSemana() { return this.request('/dashboard/agenda/semana'); }

  // Consultas
  getConsultas(page = 1, status = null) {
    let url = `/consultas?page=${page}`;
    if (status) url += `&status=${status}`;
    return this.request(url);
  }
  getConsultaById(id) { return this.request(`/consultas/${id}`); }
  createConsulta(data) { return this.request('/consultas', { method: 'POST', body: JSON.stringify(data) }); }
  updateConsulta(id, data) { return this.request(`/consultas/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }

  // Pacientes
  getPacienteById(id) { return this.request(`/pacientes/${id}`); }
  createPaciente(data) { return this.request('/pacientes', { method: 'POST', body: JSON.stringify(data) }); }
  updatePaciente(id, data) { return this.request(`/pacientes/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }

  // Prontuários
  createProntuario(data) { return this.request('/prontuarios', { method: 'POST', body: JSON.stringify(data) }); }
  updateProntuario(id, data) { return this.request(`/prontuarios/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
  getProntuarioById(id) { return this.request(`/prontuarios/${id}`); }

  // Financeiro
  getFinanceiro() { return this.request('/financeiro'); }
  getReceitas(page = 1) { return this.request(`/financeiro/receitas?page=${page}`); }
  createReceita(data) { return this.request('/financeiro/receitas', { method: 'POST', body: JSON.stringify(data) }); }
  getDespesas(page = 1) { return this.request(`/financeiro/despesas?page=${page}`); }
  createDespesa(data) { return this.request('/financeiro/despesas', { method: 'POST', body: JSON.stringify(data) }); }

  // Exames
  getExames(page = 1, status = null) {
    let url = `/exames?page=${page}`;
    if (status) url += `&status=${status}`;
    return this.request(url);
  }
  createExame(data) { return this.request('/exames', { method: 'POST', body: JSON.stringify(data) }); }
  updateExame(id, data) { return this.request(`/exames/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }

  // CID-10
  searchCID10(query) { return this.request(`/cid10/busca?q=${encodeURIComponent(query)}`); }
  getCID10ById(codigo) { return this.request(`/cid10/${codigo}`); }

  // Relatórios
  getRelatorios(periodo = 'mensal') { return this.request(`/relatorios/${periodo}`); }

  // Mensagens
  getConversas() { return this.request('/mensagens/conversas'); }
  enviarMensagem(data) { return this.request('/mensagens/enviar', { method: 'POST', body: JSON.stringify(data) }); }
  marcarLido(id) { return this.request(`/mensagens/${id}/lido`, { method: 'PUT' }); }

  // Médicos
  getMedicos() { return this.request('/medicos'); }
}

// Instância global
window.api = new APIClient();
```

#### 1.2 Atualizar `templates/index_pro.html` - Integração com JavaScript

**Alterações necessárias:**
1. Remover dados mockados (hardcoded arrays de consultas, pacientes, etc.)
2. Substituir por chamadas `api.getDashboard()`, `api.getConsultas()`, etc.
3. Adicionar event listeners aos botões (Salvar, Excluir, Agendar)
4. Mapear respostas JSON para DOM

**Exemplo - Dashboard:**
```javascript
// Em vez de:
const mockConsultas = [ /* array hardcoded */ ];

// Fazer:
async function carregarDashboard() {
  try {
    const data = await api.getDashboard();
    document.querySelector('[data-metric="consultas"]').textContent = data.total_consultas;
    document.querySelector('[data-metric="retornos"]').textContent = data.retornos;
    document.querySelector('[data-metric="novos"]').textContent = data.novos_pacientes;
    // ... atualizar HTML com dados dinâmicos
  } catch (error) {
    console.error('Erro ao carregar dashboard:', error);
    showToast('Erro ao carregar dashboard', 'error');
  }
}

// Chamar ao carregar página
document.addEventListener('DOMContentLoaded', carregarDashboard);
```

#### 1.3 Criar `static/js/ui.js` - Helpers de UI

```javascript
// static/js/ui.js - Utilitários de UI (toasts, modals, formatação)

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => toast.remove(), 3000);
}

function showModal(title, content, buttons = []) {
  // Criar modal dinamicamente
  // Exemplo: { text: 'Salvar', onclick: () => { ... } }
}

function formatData(date) {
  return new Date(date).toLocaleDateString('pt-BR');
}

function formatMoeda(valor) {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatTelefone(tel) {
  return tel.replace(/(\d{2})(\d{4,5})(\d{4})/, '($1) $2-$3');
}
```

---

### FASE 2: Integração de Módulos Específicos (3-4 horas)

#### 2.1 Dashboard Clínico
- [ ] Carregamento de métricas via `api.getDashboard()`
- [ ] Tabela de exames pendentes atualizada em tempo real
- [ ] Timeline de retornos
- [ ] Filtros por data/status

**Arquivo a modificar**: `templates/index_pro.html` (página #page-dashboard)

#### 2.2 Agenda Semanal
- [ ] Grid semanal via `api.getAgendaSemana()`
- [ ] Botões Anterior/Hoje/Próxima para navegação
- [ ] Clique em horário abre modal "Agendar Consulta"
- [ ] Integração com `createConsulta()`

**Arquivo a modificar**: `templates/index_pro.html` (página #page-agenda)

#### 2.3 Consultas
- [ ] Lista com paginação via `api.getConsultas(page)`
- [ ] Filtro por nome, status, data
- [ ] Botão "Abrir" → vai para Prontuário
- [ ] CRUD completo

**Arquivo a modificar**: `templates/index_pro.html` (página #page-consultas)

#### 2.4 Ficha do Paciente
- [ ] Carregamento via `api.getPacienteById(id)`
- [ ] Edição de dados pessoais
- [ ] Histórico clínico (timeline)
- [ ] Sinais vitais

**Arquivo a modificar**: `templates/index_pro.html` (página #page-pacientes)

#### 2.5 Prontuário Eletrônico
- [ ] Formulário completo via `api.createProntuario()`
- [ ] CID-10 search via `api.searchCID10()`
- [ ] Assinatura digital
- [ ] Salvar/Atualizar

**Arquivo a modificar**: `templates/index_pro.html` (página #page-prontuario)

#### 2.6 Prescrições
- [ ] Nova prescrição via `api.createPrescricao()`
- [ ] Histórico via `api.getPrescricoes()`
- [ ] Botão "Gerar & Imprimir"
- [ ] PDF export (vide FASE 3)

**Arquivo a modificar**: `templates/index_pro.html` (página #page-prescricoes)

#### 2.7 Exames
- [ ] Lista via `api.getExames()`
- [ ] Solicitar novo via `api.createExame()`
- [ ] Upload de laudo via `api.updateExame()`
- [ ] Filtros por status, prioridade

**Arquivo a modificar**: `templates/index_pro.html` (página #page-exames)

#### 2.8 Diagnósticos
- [ ] Lista via `api.getDiagnosticos()`
- [ ] Busca CID-10 com dropdown dinâmico
- [ ] Histórico com datas
- [ ] Status ativo/inativo

**Arquivo a modificar**: `templates/index_pro.html` (página #page-diagnosticos)

#### 2.9 Gestão Financeira
- [ ] Resumo mensal via `api.getFinanceiro()`
- [ ] Receitas e despesas com filtros
- [ ] Gráfico de barras por categoria
- [ ] Cálculo automático de lucro

**Arquivo a modificar**: `templates/index_pro.html` (página #page-financeiro)

#### 2.10 Relatórios
- [ ] Indicadores via `api.getRelatorios()`
- [ ] Filtros por período (diário, semanal, mensal)
- [ ] Gráficos de barras (diagnósticos, médicos)
- [ ] Botões: PDF, Excel

**Arquivo a modificar**: `templates/index_pro.html` (página #page-relatorios)

---

### FASE 3: Funcionalidades Avançadas (2-3 horas)

#### 3.1 PDF Export
- [ ] Instalar `python-docx` e `reportlab`
- [ ] Criar rota `POST /api/relatorios/export/pdf`
- [ ] Implementar template de relatório (prescrição, diagnóstico, etc.)

#### 3.2 Email de Confirmação
- [ ] Integrar `Flask-Mail`
- [ ] Template de e-mail para confirmação de consulta
- [ ] Enviar após `createConsulta()`

#### 3.3 Notificações em Tempo Real
- [ ] Integrar WebSocket (`python-socketio`)
- [ ] Notificações de nova consulta, exame disponível, etc.

---

### FASE 4: Testes e Validação (1-2 horas)

#### 4.1 Testes Unitários
```bash
# Backend
pytest tests/test_api.py -v

# Frontend (com Jasmine/Jest)
npm test
```

#### 4.2 Testes de Integração
- [ ] Fluxo completo: Login → Dashboard → Agendar consulta → Prontuário → Exame
- [ ] Verificar atualização de métricas em tempo real
- [ ] Testar erro de autenticação (token expirado)

#### 4.3 Testes de Performance
- [ ] Carregar lista com 1000+ consultas
- [ ] Paginar adequadamente
- [ ] Cache de CID-10

---

## 📊 Matriz de Tarefas

| Tarefa | Prioridade | Estimativa | Status |
|--------|-----------|------------|--------|
| api.js - Camada de comunicação | 🔴 Alta | 1h | ⏳ |
| Dashboard integração | 🔴 Alta | 1h | ⏳ |
| Agenda + modal agendar | 🔴 Alta | 1h | ⏳ |
| Consultas CRUD | 🔴 Alta | 1.5h | ⏳ |
| Prontuário + CID-10 search | 🟠 Média | 1.5h | ⏳ |
| Ficha paciente | 🟠 Média | 1h | ⏳ |
| Exames | 🟠 Média | 1h | ⏳ |
| Diagnósticos | 🟠 Média | 0.5h | ⏳ |
| Financeiro | 🟠 Média | 1h | ⏳ |
| Relatórios | 🟠 Média | 1h | ⏳ |
| PDF Export | 🟡 Baixa | 1h | ⏳ |
| Email confirmação | 🟡 Baixa | 0.5h | ⏳ |
| Testes | 🟠 Média | 2h | ⏳ |

**Total Estimado**: 14-15 horas

---

## 🚀 Como Começar

### Passo 1: Criar `static/js/api.js`
Copie o código fornecido acima para criar a camada de API.

### Passo 2: Adicionar ao `templates/index_pro.html`
```html
<!-- No final do body, antes de </body> -->
<script src="/static/js/api.js"></script>
<script src="/static/js/ui.js"></script>
<script src="/static/js/main.js"></script>
```

### Passo 3: Criar `static/js/main.js`
Arquivo principal com inicialização e event listeners.

### Passo 4: Iniciar servidor
```bash
python app.py
```

### Passo 5: Abrir no navegador
```
http://localhost:5000/main
```

---

## ⚠️ Considerações Importantes

1. **Autenticação**: Todos os endpoints requerem JWT. Verificar login antes de chamar APIs.
2. **CORS**: Se frontend está em domínio diferente, verificar `config.py` para CORS settings.
3. **Paginação**: Endpoints retornam 10 items por página. Implementar navegação.
4. **Validação**: Validar dados no frontend ANTES de enviar ao backend.
5. **Error Handling**: Implementar try/catch em todos os `async/await`.

---

## 📚 Referências Rápidas

- **Documentação completa**: `README_PRO.md`
- **Quick Start**: `QUICK_START.md`
- **Modelos**: `models.py`
- **Rotas**: `routes/*.py`

---

**Última atualização**: 2024
**Versão**: 1.1
**Status**: Pronto para implementação de frontend
