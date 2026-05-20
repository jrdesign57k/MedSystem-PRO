# 🏥 MedSystem - SaaS

Um sistema de gestão médica completo e escalável desenvolvido em **Flask** com banco de dados **MySQL**, oferecendo funcionalidades de autenticação, gerenciamento de pacientes, consultas e exames.

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Tech Stack](#tech-stack)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Executar](#como-executar)
- [Endpoints da API](#endpoints-da-api)
- [Segurança](#segurança)
- [Contribuição](#contribuição)

---

## 🎯 Visão Geral

**MedSystem** é uma plataforma SaaS para gestão de consultórios médicos e clínicas, oferecendo:

- ✅ Autenticação segura com JWT
- ✅ Gestão de pacientes
- ✅ Agendamento de consultas
- ✅ Registro de exames
- ✅ Dashboard interativo
- ✅ API RESTful
- ✅ Interface web responsiva

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 2.x
- **Banco de Dados:** MySQL 5.7+
- **ORM:** SQLAlchemy
- **Autenticação:** JWT (PyJWT)
- **Hash:** Bcrypt
- **CORS:** Flask-CORS

### Frontend
- **HTML5** / **CSS3** / **JavaScript (Vanilla)**
- **Interface responsiva e moderna**

### Ambiente
- **Python:** 3.8+
- **Gerenciador de pacotes:** pip
- **Ambiente virtual:** venv

---

## 📁 Estrutura do Projeto

```
novo00/
├── app.py                      # Aplicação principal (Flask Factory)
├── database.py                 # Configurações de banco de dados
├── extensions.py               # Extensões Flask (db, jwt, bcrypt)
├── models.py                   # Modelos SQLAlchemy
├── requirements.txt            # Dependências Python
├── .env.example                # Template de variáveis de ambiente
├── .gitignore                  # Arquivos ignorados pelo Git
│
├── routes/                     # Endpoints da API
│   ├── __init__.py
│   ├── auth.py                 # Autenticação (login, signup)
│   ├── pacientes.py            # CRUD de pacientes
│   ├── consultas.py            # Gestão de consultas
│   ├── exames.py               # Gestão de exames
│   └── additional.py           # Endpoints adicionais
│
├── static/                     # Arquivos estáticos
│   └── v10/
│       ├── style.css           # Estilos CSS
│       └── script.js           # JavaScript frontend
│
├── templates/                  # HTML (Jinja2)
│   └── index.html              # Página principal
│
├── instance/                   # Dados de instância (local, não versionado)
│   └── medsystem.db            # Banco SQLite local (dev)
│
└── NOVO V3.sql                 # Schema do banco de dados
```

---

## ⚙️ Pré-requisitos

Certifique-se de ter instalado:

- **Python 3.8+** → [Download](https://www.python.org/)
- **MySQL 5.7+** → [Download](https://www.mysql.com/)
- **Git** → [Download](https://git-scm.com/)
- **pip** (vem com Python)

---

## 📥 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/wjr007/Projeto-MedSystem---SaaS-.git
cd novo00
```

### 2. Crie um ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

Execute o script SQL para criar as tabelas:

```bash
mysql -u root -p medsystem < NOVO\ V3.sql
```

---

## 🔧 Configuração

### 1. Crie o arquivo `.env`

Copie o template e preencha com seus dados:

```bash
cp .env.example .env
```

### 2. Edite o `.env` com suas credenciais

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_NAME=medsystem

# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py

# JWT Secret (gere uma chave segura!)
JWT_SECRET_KEY=sua_chave_secretissima_aqui
```

### ⚠️ Importante: Segurança

- **NUNCA commite o arquivo `.env`** com credenciais reais
- O `.env` está protegido pelo `.gitignore`
- Use o `.env.example` como template para novos ambientes
- Gere chaves JWT seguras para produção

---

## 🚀 Como Executar

### Modo Desenvolvimento

```bash
# Ative o ambiente virtual (se não estiver ativo)
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Execute a aplicação
python run_app.py
```

A aplicação estará disponível em: **http://localhost:5000**

### Modo Produção

Para produção, recomenda-se usar um servidor WSGI como **Gunicorn**:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

---

## 📡 Endpoints da API

### Autenticação
- `POST /auth/login` - Login de usuário
- `POST /auth/signup` - Registro de novo usuário
- `POST /auth/logout` - Logout

### Pacientes
- `GET /pacientes` - Listar todos os pacientes
- `GET /pacientes/<id>` - Obter detalhes de um paciente
- `POST /pacientes` - Criar novo paciente
- `PUT /pacientes/<id>` - Atualizar paciente
- `DELETE /pacientes/<id>` - Deletar paciente

### Consultas
- `GET /consultas` - Listar consultas
- `POST /consultas` - Agendar consulta
- `PUT /consultas/<id>` - Atualizar consulta
- `DELETE /consultas/<id>` - Cancelar consulta

### Exames
- `GET /exames` - Listar exames
- `POST /exames` - Criar novo exame
- `PUT /exames/<id>` - Atualizar exame
- `DELETE /exames/<id>` - Deletar exame

---

## 🔒 Segurança

### Boas Práticas Implementadas

✅ **Proteção de Credenciais**
- Arquivo `.env` ignorado pelo Git
- `.env.example` como template seguro

✅ **Autenticação JWT**
- Tokens seguros para API
- Renovação de tokens
- Expiração configurável

✅ **Hash de Senhas**
- Bcrypt para hash seguro
- Nada de senhas em plaintext

✅ **CORS Configurado**
- Restrições de origem
- Proteção contra ataques CSRF

### Checklist de Segurança em Produção

- [ ] Defina `FLASK_ENV=production`
- [ ] Use chave JWT forte e única
- [ ] Configure HTTPS/SSL
- [ ] Use variáveis de ambiente para credenciais
- [ ] Configure banco de dados com usuário limitado
- [ ] Implemente rate limiting
- [ ] Adicione logging e monitoramento
- [ ] Realize testes de segurança

---

## 🤝 Contribuição

Para contribuir com o projeto:

1. **Fork** o repositório
2. Crie uma **branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. Abra um **Pull Request**

### Padrões de Commit

Use mensagens semânticas:

```
feat: Adiciona nova funcionalidade
fix: Corrige um bug
docs: Atualiza documentação
style: Mudanças de formatação
refactor: Refatoração de código
test: Adiciona/atualiza testes
chore: Tarefas de manutenção
```

---

## 📞 Suporte

Para dúvidas ou problemas:

- 📧 Email: [junior57k@gmail.com]
- 🐛 Issues: [GitHub Issues](https://github.com/wjr007/Projeto-MedSystem---SaaS-/issues)
- 💬 Discussões: [GitHub Discussions](https://github.com/wjr007/Projeto-MedSystem---SaaS-/discussions)


## 📄 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Seu Nome**
- GitHub: [@wjr007](https://github.com/wjr007)
- LinkedIn: [[linkedin](https://www.linkedin.com/in/walteir-luiz-de-morais-junior-42a21928a/)]

---

## 🎉 Créditos

Desenvolvido para a comunidade médica. 

**Última atualização:** 2026-05-20
