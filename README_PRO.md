# MedSystem PRO - Sistema de Gestão Clínica Completo

## 🎯 Visão Geral

MedSystem PRO é um sistema completo de gestão de clínica médica com 10 módulos integrados, incluindo dashboard clínico, agenda semanal, prontuário eletrônico, prescrições, exames, diagnósticos (CID-10), gestão financeira, relatórios, equipe médica e mensagens internas.

## ✨ Módulos Implementados

### 1. **Dashboard Clínico** 📊
- Métricas do dia (consultas, pacientes, alertas)
- Próximos retornos (timeline)
- Exames pendentes
- Alertas clínicos de diagnósticos graves
- **Endpoint**: `GET /api/dashboard`

### 2. **Agenda Semanal** 📅
- Visualização em grid semanal (seg-sex)
- Horários: 08:00, 09:30, 11:00, 14:00, 15:30
- Estatísticas: total, confirmadas, aguardando, canceladas
- **Endpoint**: `GET /api/dashboard/agenda/semana`

### 3. **Consultas** 👨‍⚕️
- Tabela com histórico de consultas
- Filtro por paciente
- Status: Agendada, Em andamento, Concluída
- **Endpoints**:
  - `GET /api/consultas` - listar com paginação
  - `GET /api/consultas/:id` - detalhe
  - `POST /api/consultas` - criar
  - `PUT /api/consultas/:id` - atualizar

### 4. **Ficha do Paciente** 🗂️
- Dados pessoais completos
- Sinais vitais (FC, PA, Temp, SpO2, Peso)
- Histórico clínico (timeline)
- Medicamentos em uso
- **Endpoints**:
  - `GET /api/pacientes/:id` - ficha completa
  - `GET /api/pacientes/:id/historico` - timeline clínico

### 5. **Prontuário Eletrônico** 📋
- Anamnese (queixa principal, história, antecedentes)
- Exame Físico (sinais vitais, ausculta)
- Diagnóstico com CID-10
- Plano Terapêutico
- Exames Solicitados
- Assinatura Digital
- **Endpoints**:
  - `POST /api/prontuarios` - criar
  - `GET /api/prontuarios/:id` - obter
  - `PUT /api/prontuarios/:id` - atualizar

### 6. **Prescrições** 💊
- Nova prescrição com medicamentos
- Tipo de receita (Simples, Controlada Azul, Controlada Amarela)
- Histórico de receituários emitidos
- Impressão e emissão
- **Endpoints**:
  - `GET /api/prescricoes` - listar
  - `POST /api/prescricoes` - criar
  - `PUT /api/prescricoes/:id` - atualizar

### 7. **Exames** 🧪
- Solicitação de exames
- Histórico com resultados
- Prioridades: Urgente, Normal, Baixa
- Status: Aguardando, Em análise, Disponível
- Visualização de laudos
- **Endpoints**:
  - `GET /api/exames` - listar
  - `POST /api/exames` - solicitar
  - `PUT /api/exames/:id` - resultado

### 8. **Diagnósticos** 🔍
- Histórico de diagnósticos
- Búsqueda de CID-10
- Codificação completa
- **Endpoints**:
  - `GET /api/diagnosticos` - listar
  - `GET /api/cid10/busca?q=termo` - buscar CID
  - `GET /api/cid10/:codigo` - detalhe CID

### 9. **Gestão Financeira** 💰
- Dashboard com receitas/despesas mensais
- Receita por categoria (Particular, Convênio, etc)
- Lançamentos recentes
- Lucro líquido
- **Endpoints**:
  - `GET /api/financeiro` - resumo
  - `GET /api/financeiro/receitas` - receitas
  - `POST /api/financeiro/receitas` - criar receita
  - `GET /api/financeiro/despesas` - despesas
  - `POST /api/financeiro/despesas` - criar despesa

### 10. **Relatórios** 📈
- Indicadores clínicos (consultas/mês, novos pacientes, retornos)
- Top 5 diagnósticos
- Consultas por médico
- Comparação com período anterior
- **Endpoints**:
  - `GET /api/relatorios` - indicadores mensais
  - `GET /api/relatorios/diario?data=YYYY-MM-DD` - relatório diário
  - `GET /api/relatorios/semanal` - relatório semanal
  - `GET /api/relatorios/mensal?mes=1&ano=2025` - relatório mensal

### EXTRAS

**Equipe Médica** 👥
- Cards com informações de cada médico
- Status (Online, Em consulta)
- Próximas consultas
- Total de consultas do mês

**Mensagens Internas** 💬
- Chat seguro entre profissionais
- Conversas agrupadas
- Marca como lida
- **Endpoints**:
  - `GET /api/mensagens` - listar conversas
  - `POST /api/mensagens` - enviar
  - `GET /api/mensagens/:id` - conversa completa
  - `PUT /api/mensagens/:id/marcar-lida` - marcar como lida

**Novo Paciente** ➕
- Formulário completo com validação
- Checklist de admissão (6 itens)
- Barra de progresso
- Últimos cadastros

## 🏗️ Arquitetura

### Models Expandidos
```
Usuario (auth)
├── Medico
│   ├── Especialidade
│   ├── Consulta
│   ├── Prescricao
│   ├── Exame
│   ├── Diagnostico
│   ├── Receita
│   └── Mensagem
├── Paciente
│   ├── Consulta
│   ├── Prescricao
│   ├── Exame
│   ├── Diagnostico
│   ├── SinalVital
│   ├── ContatoEmergencia
│   └── Receita
├── CID10 (referência)
├── Receita (financeiro)
├── Despesa (financeiro)
└── Mensagem (comunicação)
```

### Estrutura de Rotas
```
/api/auth/              - Autenticação
/api/pacientes/         - CRUD Pacientes
/api/consultas/         - CRUD Consultas
/api/exames/            - CRUD Exames
/api/medicos/           - CRUD Médicos
/api/prontuarios/       - Prontuários Eletrônicos
/api/financeiro/        - Gestão Financeira
/api/relatorios/        - Relatórios
/api/cid10/             - CID-10 (Diagnósticos)
/api/mensagens/         - Mensagens Internas
/api/dashboard/         - Dashboard + Agenda Semanal
```

## 🚀 Instalação & Uso

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente (.env)
```
DB_USER=root
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_NAME=medsystem_novo
JWT_SECRET_KEY=sua_chave_secreta
```

### 3. Criar Banco de Dados
```bash
mysql -u root -p -e "CREATE DATABASE medsystem_novo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 4. Inicializar Aplicação
```bash
python run_app.py
```

### 5. Popular CID-10
```bash
python seed_cid10.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 🔐 Autenticação

Todas as rotas (exceto `/api/auth/login`) requerem token JWT no header:

```
Authorization: Bearer {token}
```

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "medico@medsystem.com",
  "senha": "MedSystem12#"
}

Response:
{
  "sucesso": true,
  "token": "eyJ...",
  "usuario": { ... }
}
```

## 📊 Exemplos de Uso

### 1. Obter Dashboard
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:5000/api/dashboard
```

### 2. Agendar Consulta
```bash
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "id_paciente": 1,
    "id_medico": 1,
    "data_consulta": "2025-05-10T14:30:00",
    "motivo": "Palpitações",
    "tipo_consulta": "1ª Consulta"
  }' \
  http://localhost:5000/api/consultas
```

### 3. Buscar CID-10
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:5000/api/cid10/busca?q=hipertensão"
```

### 4. Criar Prontuário
```bash
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "id_consulta": 1,
    "queixa_principal": "Febre há 3 dias",
    "historia_molesita_atual": "Febre 38-39°C",
    "antecedentes_pessoais": "Sem comorbidades",
    "exame_fisico": "MV presente bilateralmente",
    "hipotese_diagnostica": "Síndrome gripal",
    "plano_terapeutico": "Repouso, hidratação",
    "pa": "120/80",
    "fc": 72,
    "temperatura": 38.5
  }' \
  http://localhost:5000/api/prontuarios
```

### 5. Listar Financeiro
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:5000/api/financeiro
```

## 🎨 Design System

### Cores
- **Primária**: `#2563eb` (Blue)
- **Sucesso**: `#16a34a` (Green)
- **Alerta**: `#d97706` (Amber)
- **Erro**: `#dc2626` (Red)
- **Info**: `#0d9488` (Teal)

### Tipografia
- **Fonte Principal**: Geist (sans-serif)
- **Serif**: Instrument Serif
- **Monospace**: Geist Mono

### Status & Badges
- **Consulta**: Agendada (amber), Em andamento (blue), Concluída (green)
- **Receita**: Pendente (amber), Pago (green), Cancelado (red)
- **Exame**: Aguardando (amber), Em análise (blue), Disponível (green)
- **Diagnóstico**: Leve (green), Moderada (amber), Grave (red)

## 📝 Campos Principais

### Consulta
- id_consulta (PK)
- id_paciente (FK)
- id_medico (FK)
- data_consulta
- hora_consulta
- status (AGENDADA, CONCLUÍDA, CANCELADA)
- motivo
- tipo_consulta (1ª Consulta, Retorno, Urgência)
- queixa_principal
- historia_molesita_atual
- exame_fisico
- hipotese_diagnostica
- plano_terapeutico

### Receita
- id (PK)
- id_consulta (FK)
- id_paciente (FK)
- id_medico (FK)
- descricao
- valor
- tipo (Particular, Convênio, etc)
- data_receita
- data_pagamento
- status (PENDENTE, PAGO, CANCELADO)

### CID-10
- id (PK)
- codigo (UNIQUE)
- descricao
- categoria (Cardiovascular, Respiratória, etc)

## ⚙️ Configurações

### Paginação
- Padrão: 10 itens por página
- Máximo: 100 itens por página

### Filtros Suportados
- Por status
- Por data (range)
- Por categoria
- Por prioridade

## 🧪 Dados de Teste

### Especialidades (Inseridas Automaticamente)
1. Cardiologia
2. Clínica Geral
3. Pediatria
4. Ginecologia e Obstetrícia
5. Ortopedia
6. Neurologia
7. Oftalmologia
8. Cirurgia Geral

### CID-10 Populados (seed_cid10.py)
- I10: Hipertensão Arterial
- E11: Diabetes Mellitus tipo 2
- J06.9: IVAS
- E muito mais...

## 📋 Checklist de Funcionalidades

### Frontend
- [x] Interface com 10 módulos
- [x] Responsividade
- [x] Navegação sidebar
- [x] Topbar com notificações
- [x] Modais para ações
- [x] Tabelas com filtro
- [x] Formulários com validação
- [x] Badges e cores por status
- [x] Animações suaves
- [x] Sistema de toasts

### Backend
- [x] Modelos expandidos
- [x] Rotas CRUD completas
- [x] Autenticação JWT
- [x] Paginação
- [x] Filtros de data/status
- [x] Tratamento de erros
- [x] Logs de auditoria
- [x] Transações ACID
- [x] Validação de dados
- [x] CORS habilitado

## 🔄 Próximos Passos

1. Integração com frontend (React/Vue)
2. PDF export para prontuários
3. SMS/Email para lembretes
4. Integração com labs para resultados automáticos
5. App mobile
6. Multi-tenancy
7. Analytics avançados
8. Integrações com sistemas de convênio

## 📄 Licença

Proprietário - MedSystem PRO

## 👥 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.

---

**Versão**: 1.0.0  
**Última Atualização**: Junho de 2025  
**Status**: 🟢 Produção
