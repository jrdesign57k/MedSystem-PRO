# 🚀 MEDSYSTEM - GUIA DE INÍCIO RÁPIDO

## ✅ STATUS ATUAL
Sistema **PRONTO PARA INICIAR** - Erro de rotas duplicadas **CORRIGIDO**

---

## 🎯 INICIAR A APLICAÇÃO

### Windows (Recomendado)
Abra a pasta `c:\Users\jrdev\Documents\PROJETO CLOUD\medsystem` no Explorador de Arquivos e duplo-clique em:
```
START_APP.bat
```

### Terminal / PowerShell / CMD
```bash
cd "c:\Users\jrdev\Documents\PROJETO CLOUD\medsystem"
python run_app.py
```

---

## 📍 ACESSAR O SISTEMA

Após iniciar o servidor, abra seu navegador e vá para:
```
http://localhost:5000/app/dashboard
```

### Credenciais Padrão

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `medico@medsystem.com` | `MedSystem12#` | Admin / Médico |
| `drcarlos@medsystem.com` | `MedSystem12#` | Médico Exemplo |

---

## 🗂️ ESTRUTURA DO DASHBOARD

### Sidebar (Menu Lateral)
```
🏥 MedSystem
├── Dashboard        → Métricas e gráficos
├── Pacientes        → Listagem e busca
├── Consultas        → Histórico de consultas
├── Exames           → Resultados e agendamentos
├── Diagnósticos     → Diagnósticos registrados
└── ⚙️ Configurações  → Ajustes do sistema
```

### Gráficos Disponíveis
- **Atendimentos**: Linha gráfica com histórico de consultas
- **Classificação de Risco**: Doughnut chart com distribuição de pacientes

---

## 📋 PÁGINAS PRINCIPAIS

### 1. Dashboard (`/app/dashboard`)
- Métricas em tempo real
- 2 Gráficos interativos
- Tabela de últimos atendimentos
- Alertas de pacientes críticos

### 2. Pacientes (`/app/pacientes`)
- Listagem completa com busca
- Filtros por status e risco
- Botões para editar/visualizar

### 3. Novo Paciente (`/app/novo-paciente`)
Formulário com campos:
- Nome completo *(obrigatório)*
- CPF *(obrigatório, validado)*
- Data de Nascimento *(obrigatório)*
- Sexo *(obrigatório)*
- Tipo Sanguíneo
- Telefone
- Email
- Endereço
- Alergias conhecidas
- Observações clínicas

### 4. Ficha do Paciente (`/app/paciente/<id>`)
- Dados completos do paciente
- Histórico de consultas
- Exames realizados
- Prescrições ativas
- Diagnósticos

---

## 🔧 COMPONENTES PRINCIPAIS

### Backend (Flask)
- `app.py` → Configuração principal
- `routes/` → Rotas da API
  - `auth.py` → Autenticação (login/logout)
  - `pacientes.py` → CRUD de pacientes
  - `consultas.py` → Gestão de consultas
  - `additional.py` → Dashboard e exames

### Frontend (Templates)
- `layout.html` → Base com sidebar
- `app_dashboard.html` → Dashboard principal
- `app_pacientes.html` → Lista de pacientes
- `app_novo_paciente.html` → Formulário
- `app_ficha_paciente.html` → Detalhes do paciente

### Banco de Dados
- **Engine**: MySQL
- **Host**: localhost (padrão)
- **Banco**: medsystem
- **Usuário**: root
- **Senha**: (configurada em `.env`)

---

## 📊 API ENDPOINTS

### Autenticação
```
POST /api/auth/login
POST /api/auth/logout
```

### Pacientes
```
GET  /api/pacientes              # Lista todos
POST /api/pacientes              # Cria novo
GET  /api/pacientes/<id>         # Detalhes
PUT  /api/pacientes/<id>         # Atualiza
DEL  /api/pacientes/<id>         # Deleta
```

### Dashboard (Gráficos)
```
GET /api/dashboard/grafico/atendimentos        # Dados gráfico atendimentos
GET /api/dashboard/grafico/classificacao-risco # Dados gráfico risco
```

### Consultas
```
GET  /api/consultas              # Lista
POST /api/consultas              # Cria
```

---

## ⚙️ CONFIGURAÇÕES (`.env`)

```env
# MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=medsystem

# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# JWT
JWT_SECRET_KEY=sua_chave_secreta
```

---

## 🐛 TROUBLESHOOTING

### Erro: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Erro: "Connection refused" no MySQL
- Verifique se MySQL está rodando
- Confirme credenciais em `.env`
- Teste conexão: `mysql -u root -p medsystem`

### Erro: "CORS error"
- CORS já está configurado em `app.py`
- Verifique o domínio de origem no navegador

### Porta 5000 já está em uso
```bash
# Mudar porta em run_app.py ou app.py (linha final)
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## 📝 ARQUIVOS IMPORTANTES

| Arquivo | Função |
|---------|--------|
| `app.py` | Configuração Flask (CORRIGIDO) |
| `run_app.py` | Diagnosticar e iniciar app |
| `START_APP.bat` | Atalho Windows |
| `models.py` | Modelos SQLAlchemy |
| `extensions.py` | Extensões (db, jwt, bcrypt) |
| `.env` | Variáveis de ambiente |
| `requirements.txt` | Dependências Python |

---

## ✨ RECURSOS DO SISTEMA

✅ Dashboard com sidebar navegável
✅ Gráficos interativos (Chart.js)
✅ Sistema de login com JWT
✅ CRUD completo de pacientes
✅ Busca e filtros avançados
✅ Formulário validado
✅ Responsivo para mobile/tablet
✅ Tratamento de erros global
✅ API RESTful documentada

---

## 📞 SUPORTE

Para problemas:
1. Verifique `CORRECAO_ROTAS.md` para detalhes da correção
2. Revise logs do console ao iniciar
3. Confirme dependências: `pip list`
4. Teste banco de dados: `python -c "from models import *; print('OK')"`

---

**Última atualização:** 2026-05-28
**Status:** ✅ FUNCIONANDO
**Versão:** MedSystem 2.0 com Dashboard Completo
