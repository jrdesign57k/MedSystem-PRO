# MedSystem PRO

Sistema de gestão clínica completo desenvolvido em **Flask**, com interface web moderna, responsiva e integrada a uma API RESTful. Reúne agenda, prontuário eletrônico, prescrições, exames, financeiro, relatórios e mais — tudo em uma única aplicação.

---

## Visão Geral

O **MedSystem PRO** centraliza a rotina de um consultório/clínica em módulos integrados:

- Autenticação segura com JWT
- Dashboard clínico com indicadores do dia
- Agenda semanal de consultas
- Cadastro e ficha completa de pacientes
- Prontuário eletrônico (anamnese, exame físico, diagnóstico, conduta)
- Prescrições e receituários
- Solicitação e acompanhamento de exames
- Diagnósticos com CID-10
- Gestão financeira (receitas e despesas)
- Relatórios e indicadores
- Equipe médica e mensagens internas
- Interface responsiva (desktop, tablet e mobile)

---

## Tech Stack

**Backend**
- Python 3.10+ / Flask
- SQLAlchemy (ORM)
- MySQL
- Flask-JWT-Extended (autenticação)
- Flask-Bcrypt (hash de senhas)
- Flask-CORS

**Frontend**
- HTML5 + Jinja2 (templates modulares por partials)
- CSS3 (design system "PRO", responsivo)
- JavaScript (Vanilla, ES6)

---

## Estrutura do Projeto

```text
PROJETO CLOUD/
├── app.py                        # Aplicação Flask (factory) + rotas do frontend
├── run_app.py                    # Inicialização local
├── extensions.py                 # Instâncias (db, jwt, bcrypt)
├── models.py                     # Modelos SQLAlchemy
├── requirements.txt              # Dependências Python
├── .env.example                  # Modelo de variáveis de ambiente
└── medsystem/
    ├── routes/                   # Blueprints da API
    │   ├── auth.py               # Autenticação
    │   ├── pacientes.py
    │   ├── consultas.py
    │   ├── additional.py         # Exames + Dashboard
    │   ├── medicos.py
    │   ├── prontuario.py
    │   ├── financeiro.py
    │   ├── cid10.py
    │   ├── mensagens.py
    │   └── relatorios.py
    ├── static/v10/               # CSS / JS
    │   ├── pro.css               # Design system principal (PRO)
    │   ├── style.css             # Estilos da tela de login + complementos
    │   ├── ui.js                 # Helpers de UI
    │   ├── script.js             # Login e bootstrap da aplicação
    │   ├── pro.js                # Integração dos módulos com a API
    │   └── validacoes.js
    └── templates/
        ├── index.html            # Página única (monta os partials)
        └── partials/
            ├── _login.html
            ├── _sidebar.html
            ├── _topbar.html
            ├── _modais.html
            └── pages/            # Um partial por módulo
                ├── dashboard.html
                ├── agenda.html
                ├── consultas.html
                ├── pacientes.html
                ├── prontuario.html
                ├── prescricoes.html
                ├── exames.html
                ├── diagnostico.html
                ├── financeiro.html
                ├── relatorios.html
                ├── equipe.html
                ├── mensagens.html
                └── novo_paciente.html
```

---

## Pré-requisitos

- [Python 3.10+](https://www.python.org/downloads/)
- [MySQL 8.0](https://dev.mysql.com/downloads/) (local ou remoto)
- [Git](https://git-scm.com/)

---

## Instalação (local)

1. Clone o repositório:

```bash
git clone https://github.com/jrdesign57k/MedSystem-PRO.git
cd MedSystem-PRO
```

2. Crie e ative um ambiente virtual:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Configuração

Crie um arquivo `.env` na raiz (use o `.env.example` como base):

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=medsystem
JWT_SECRET_KEY=defina_uma_chave_secreta
```

Crie o banco vazio uma vez (as tabelas são criadas automaticamente na primeira execução):

```sql
CREATE DATABASE medsystem CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## Como Executar

```bash
python run_app.py
```

A aplicação ficará disponível em: **http://localhost:5000**

### Acesso padrão

| Campo  | Valor                  |
|--------|------------------------|
| E-mail | `medico@medsystem.com` |
| Senha  | `MedSystem12#`         |

> Na primeira execução o sistema cria automaticamente as tabelas, as especialidades e o usuário de acesso padrão.

---

## Principais Endpoints da API

Todas as rotas (exceto o login) exigem o header `Authorization: Bearer <token>`.

| Módulo        | Rota base            |
|---------------|----------------------|
| Autenticação  | `/api/auth`          |
| Pacientes     | `/api/pacientes`     |
| Consultas     | `/api/consultas`     |
| Exames        | `/api/exames`        |
| Médicos       | `/api/medicos`       |
| Dashboard     | `/api/dashboard`     |
| Prontuários   | `/api/prontuarios`   |
| Financeiro    | `/api/financeiro`    |
| CID-10        | `/api/cid10`         |
| Mensagens     | `/api/mensagens`     |
| Relatórios    | `/api/relatorios`    |

Exemplo de login:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"medico@medsystem.com","senha":"MedSystem12#"}'
```

---

## Segurança

- Senhas armazenadas com hash **Bcrypt** (nunca em texto puro)
- Autenticação via **JWT** com expiração
- **CORS** configurado
- Validação de dados nas rotas

---

## Licença

Projeto sob a licença MIT. Consulte o arquivo `LICENSE` para detalhes.
