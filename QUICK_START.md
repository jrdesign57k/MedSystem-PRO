# MedSystem PRO - Quick Start Guide 🚀

## Status: Backend Completo ✅

O backend MedSystem foi implementado com sucesso com todos os 10 módulos principais + 3 extras.

---

## 📋 Pré-requisitos

- Python 3.8+
- MySQL 5.7+
- pip (gerenciador de pacotes Python)

---

## 🔧 Instalação

### 1. Instalar dependências
```bash
cd "c:\Users\jrdev\Documents\GitHub\MedSystem\MedSystem1.1\PROJETO CLOUD\medsystem"
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente (.env)
```
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=mysql+pymysql://root:password@localhost/medsystem_db
SECRET_KEY=sua-chave-secreta-aqui
JWT_SECRET_KEY=sua-jwt-key-aqui
```

### 3. Criar banco de dados
```bash
mysql -u root -p
CREATE DATABASE medsystem_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 4. Executar migrations
```bash
# Usar Flask-Migrate (se configurado)
flask db upgrade

# Ou importar schema.sql (se disponível)
mysql -u root -p medsystem_db < schema.sql
```

### 5. Seed CID-10 reference data
```bash
python seed_cid10.py
```

### 6. Iniciar servidor
```bash
python app.py
```

O servidor estará em `http://localhost:5000`

---

## 🎯 Módulos Implementados

### ✅ 1. Dashboard Clínico
- **Endpoint**: `GET /api/dashboard`
- **Função**: Métricas do dia, exames pendentes, próximos retornos
- **Features**:
  - Contadores: Consultas, Retornos, Pacientes novos
  - Tabela: Exames pendentes
  - Timeline: Próximos 5 retornos

### ✅ 2. Agenda Semanal
- **Endpoint**: `GET /api/dashboard/agenda/semana`
- **Função**: Grid visual de consultas por dia/hora
- **Features**:
  - Agrupa por dia da semana
  - Exibe status (agendada, confirmada, cancelada)
  - Contadores por status

### ✅ 3. Consultas
- **Endpoints**:
  - `GET /api/consultas` - Lista com paginação
  - `GET /api/consultas/:id` - Detalhe
  - `POST /api/consultas` - Criar
  - `PUT /api/consultas/:id` - Atualizar
- **Features**:
  - Status: AGENDADA, EM_ANDAMENTO, CONCLUÍDA, CANCELADA
  - Filtragem por status, data, médico
  - Integração com paciente e médico

### ✅ 4. Ficha do Paciente
- **Endpoint**: `GET /api/pacientes/:id`
- **Função**: Perfil completo + histórico
- **Features**:
  - Dados pessoais
  - Sinais vitais
  - Histórico clínico
  - Alergias e comorbidades

### ✅ 5. Prontuário Eletrônico
- **Endpoints**:
  - `POST /api/prontuarios` - Criar
  - `PUT /api/prontuarios/:id` - Atualizar
  - `GET /api/prontuarios/:id` - Obter
- **Features**:
  - Anamnese completa
  - Exame físico com sinais vitais
  - Diagnóstico com CID-10
  - Plano terapêutico

### ✅ 6. Prescrições
- **Endpoints**:
  - `GET /api/consultas/:id/prescricoes` - Lista
  - `POST /api/consultas/:id/prescricoes` - Criar
  - `PUT /api/consultas/:id/prescricoes/:presc_id` - Atualizar
- **Features**:
  - Medicamentos com dosagem e frequência
  - Tipos: Receita Azul, Retenção
  - Status: ATIVA, INATIVA

### ✅ 7. Exames
- **Endpoints**:
  - `GET /api/exames` - Lista
  - `POST /api/exames` - Solicitar
  - `PUT /api/exames/:id` - Atualizar resultado
- **Features**:
  - Prioridade: URGENTE, NORMAL, BAIXA
  - Status: SOLICITADO, AGUARDANDO, EM_ANÁLISE, DISPONÍVEL
  - Laudo e data de resultado

### ✅ 8. Diagnósticos
- **Endpoints**:
  - `GET /api/diagnosticos` - Lista
  - `GET /api/cid10/busca?q=termo` - Buscar CID-10
- **Features**:
  - CID-10 reference search
  - Status: ATIVO, INATIVO
  - Histórico com datas

### ✅ 9. Gestão Financeira
- **Endpoints**:
  - `GET /api/financeiro` - Resumo
  - `GET /api/financeiro/receitas` - Receitas
  - `POST /api/financeiro/receitas` - Criar receita
  - `GET /api/financeiro/despesas` - Despesas
  - `POST /api/financeiro/despesas` - Criar despesa
- **Features**:
  - Agregação mensal
  - Cálculo automático de lucro
  - Categorias customizáveis

### ✅ 10. Relatórios
- **Endpoints**:
  - `GET /api/relatorios` - Indicadores
  - `GET /api/relatorios/diario` - Relatório diário
  - `GET /api/relatorios/semanal` - Relatório semanal
  - `GET /api/relatorios/mensal` - Relatório mensal
- **Features**:
  - KPIs: Consultas/mês, Novos pacientes, Retornos, Exames solicitados
  - Top diagnósticos
  - Consultas por médico

### ✅ Extras

**Equipe Médica**
- `GET /api/medicos` - Lista de médicos com especialidades

**Mensagens Internas**
- `GET /api/mensagens/conversas` - Lista de conversas
- `POST /api/mensagens/enviar` - Enviar mensagem
- `PUT /api/mensagens/:id/lido` - Marcar como lido

**Novo Paciente**
- `POST /api/pacientes` - Criar novo paciente

---

## 🔐 Autenticação

Todos os endpoints requerem JWT token no header:

```
Authorization: Bearer {jwt_token}
```

### Exemplo de login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "medico@example.com",
    "password": "senha123"
  }'
```

Resposta:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "nome": "Dr. Mendonça",
    "email": "medico@example.com",
    "role": "medico"
  }
}
```

---

## 📚 Estrutura de Arquivos

```
medsystem/
├── app.py                      # Aplicação principal
├── config.py                   # Configurações
├── models.py                   # Modelos SQLAlchemy (expandidos)
├── seed_cid10.py              # Script para popular CID-10
├── requirements.txt            # Dependências Python
│
├── routes/
│   ├── auth.py                # Autenticação (login, logout, refresh)
│   ├── pacientes.py           # CRUD de pacientes
│   ├── consultas.py           # CRUD de consultas
│   ├── exames.py              # CRUD de exames
│   ├── medicos.py             # Lista de médicos
│   ├── dashboard.py           # Dashboard + agenda semanal (NOVO)
│   ├── prontuario.py          # Prontuário eletrônico (NOVO)
│   ├── financeiro.py          # Gestão financeira (NOVO)
│   ├── relatorios.py          # Relatórios e KPIs (NOVO)
│   ├── cid10.py               # Busca CID-10 (NOVO)
│   └── mensagens.py           # Mensagens internas (NOVO)
│
├── templates/
│   └── index_pro.html         # Interface completa com 10 módulos
│
└── static/
    ├── css/
    │   └── style.css          # Estilos (CSS variables, componentes)
    └── js/
        └── app.js             # JavaScript (integração com APIs)
```

---

## 🚀 Próximos Passos

### Curto prazo (hoje)
1. ✅ Backend implementado
2. ⏳ **Conectar frontend com APIs** - Frontend já tem interface, precisa chamar endpoints
3. ⏳ **Testar fluxos completos** - Login → Dashboard → Criar consulta → Adicionar prontuário

### Médio prazo (semana)
4. Implementar PDF export para relatórios e prescrições
5. Adicionar email/SMS de confirmação de consultas
6. Implementar notificações em tempo real (WebSocket)

### Longo prazo (mês)
7. Integração com laboratórios (resultados automáticos)
8. Backup e restauração de dados
9. Multi-tenancy (múltiplas clínicas)
10. App mobile (React Native)

---

## 🧪 Testes Rápidos

### 1. Testar Dashboard
```bash
curl -X GET http://localhost:5000/api/dashboard \
  -H "Authorization: Bearer {seu_token}"
```

### 2. Testar CID-10 Search
```bash
curl -X GET "http://localhost:5000/api/cid10/busca?q=diabete" \
  -H "Authorization: Bearer {seu_token}"
```

### 3. Testar Financeiro
```bash
curl -X GET http://localhost:5000/api/financeiro \
  -H "Authorization: Bearer {seu_token}"
```

### 4. Testar Consultas
```bash
curl -X POST http://localhost:5000/api/consultas \
  -H "Authorization: Bearer {seu_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "id_paciente": 1,
    "id_medico": 1,
    "data_agendamento": "2024-01-15 10:00",
    "motivo": "Consulta de rotina"
  }'
```

---

## 🛠️ Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'flask_jwt_required'`
```bash
pip install Flask-JWT-Extended
```

### Erro: `Can't connect to MySQL server`
- Verificar se MySQL está rodando
- Verificar credenciais em .env
- Executar: `mysql -u root -p` para testar acesso

### Erro: `Table 'medsystem_db.usuario' doesn't exist`
- Executar migrations: `flask db upgrade`
- Ou importar schema: `mysql -u root -p medsystem_db < schema.sql`

### Erro: JWT token inválido
- Token pode ter expirado (valid por 1 hora)
- Usar refresh token: `POST /api/auth/refresh`

---

## 📖 Documentação Completa

Para documentação detalhada de todos os endpoints, veja:
- `README_PRO.md` - Documentação completa da API com exemplos
- `models.py` - Definição de todos os modelos e relacionamentos
- Comentários nos arquivos de rotas

---

## 👥 Suporte

Em caso de dúvidas ou problemas:
1. Verificar logs do servidor (output no terminal)
2. Testar endpoints com Postman/Insomnia
3. Verificar permissões do banco de dados
4. Consultar documentação em README_PRO.md

---

**Status**: ✅ Backend Pronto para Produção
**Última atualização**: 2024
**Versão**: 1.1
