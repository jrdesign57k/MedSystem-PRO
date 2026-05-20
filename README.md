# 🏥 MedSystem - SaaS

Um sistema de gestão médica completo e escalável desenvolvido em **Flask** com banco de dados **MySQL** e infraestrutura automatizada na **AWS** via **Terraform**. Oferece funcionalidades de autenticação, gerenciamento de pacientes, consultas e exames.

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
- ✅ Infraestrutura como Código (IaC) na AWS

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 2.x
- **Banco de Dados:** MySQL 5.7+ (AWS RDS)
- **ORM:** SQLAlchemy
- **Autenticação:** JWT (PyJWT)
- **Hash:** Bcrypt
- **CORS:** Flask-CORS

### Cloud & Infraestrutura (IaC)
- **Provedor:** Amazon Web Services (AWS)
- **Servidor:** EC2 (Ubuntu)
- **Provisionamento:** Terraform
- **Servidor Web:** Nginx + Gunicorn

### Frontend
- **HTML5** / **CSS3** / **JavaScript (Vanilla)**
- **Interface responsiva e moderna**

---

## 📁 Estrutura do Projeto

```text
PROJETO CLOUD/
├── .terraform/                              # Configurações ocultas do Terraform
├── LICENSE.txt                              # Licença do projeto
├── terraform-provider-aws_v5.100.0_x5.exe   # Binário do provedor AWS
├── medsystem/                               # Código fonte da aplicação Flask
│   ├── routes/                              # Endpoints da API (Blueprints)
│   │   ├── __init__.py
│   │   ├── additional.py
│   │   ├── auth.py
│   │   ├── consultas.py
│   │   └── pacientes.py
│   ├── static/v10/                          # Arquivos estáticos (CSS, JS, Imagens)
│   ├── templates/                           # Templates HTML (Jinja2)
│   │   └── index.html
│   ├── _cleanup_exec.py                     # Script utilitário de limpeza
│   ├── .env.example                         # Template de variáveis de ambiente
│   ├── .gitignore                           # Arquivos ignorados pelo Git
│   ├── app.py                               # Aplicação principal (Flask Factory)
│   ├── cleanup_backend.py                   # Lógica de limpeza do backend
│   ├── database.py                          # Configurações de banco de dados
│   ├── EXECUTAR_LIMPEZA.bat                 # Batch script de manutenção
│   ├── extensions.py                        # Extensões Flask (db, jwt, bcrypt)
│   ├── INTEGRACAO_README.md                 # Doc de integração
│   ├── LIMPEZA_README.md                    # Doc de rotinas de limpeza
│   ├── models.py                            # Modelos SQLAlchemy
│   ├── NOVO V3.sql                          # Schema do banco de dados MySQL
│   ├── README.md                            # Documentação principal
│   ├── requirements.txt                     # Dependências Python
│   ├── run_app.py                           # Arquivo de execução local
│   └── solucao_simples.py                   # Script de solução rápida
├── .terraform.lock.hcl                      # Arquivo de trava de dependências do Terraform
├── ec2.tf                                   # Criação da instância de servidor na AWS
├── outputs.tf                               # Saídas do Terraform (IP Público, Endpoint RDS)
├── provider.tf                              # Declaração do provedor cloud (AWS)
├── rds.tf                                   # Criação do banco de dados na AWS
├── security_groups.tf                       # Regras de firewall e portas (22, 80, 3306)
├── terraform.tfstate                        # Estado atual da infraestrutura
├── terraform.tfstate.backup                 # Backup de estado da infraestrutura
├── variables.tf                             # Variáveis dinâmicas da infraestrutura
└── vpc.tf                                   # Configuração de rede virtual da nuvem

⚙️ Pré-requisitos

Certifique-se de ter instalado:

    Python 3.8+ → Download

    Terraform → Download

    AWS CLI configurado localmente

    Git → Download

📥 Instalação (Local)
1. Clone o repositório
Bash

git clone [https://github.com/wjr007/Projeto-MedSystem---SaaS-.git](https://github.com/wjr007/Projeto-MedSystem---SaaS-.git)
cd medsystem

2. Crie um ambiente virtual
Bash

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

3. Instale as dependências
Bash

pip install -r requirements.txt

🔧 Configuração
1. Crie o arquivo .env

Copie o template e preencha com seus dados (utilize o Endpoint do RDS se estiver na nuvem):
Bash

cp .env.example .env

2. Edite o .env com suas credenciais
Snippet de código

# Database Configuration
DB_HOST=localhost (Ou Endpoint RDS)
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_NAME=medsystem

# JWT Secret
JWT_SECRET_KEY=sua_chave_secretissima_aqui

🚀 Como Executar
Modo Desenvolvimento (Local)
Bash

# Ative o ambiente virtual e execute
python run_app.py

A aplicação estará disponível em: http://localhost:5000
Subindo a Infraestrutura (AWS via Terraform)

Na raiz do projeto (onde estão os arquivos .tf):
Bash

terraform init
terraform apply
# Digite 'yes' para confirmar a criação da EC2 e do RDS

Modo Produção (No servidor EC2)
Bash

gunicorn -w 2 -b 127.0.0.1:5000 "app:create_app()" --daemon

📡 Endpoints da API
Autenticação

    POST /api/auth/login - Login de usuário

    POST /api/auth/signup - Registro de novo usuário

Pacientes

    GET /api/pacientes - Listar pacientes

    POST /api/pacientes - Criar novo paciente

    PUT /api/pacientes/<id> - Atualizar paciente

    DELETE /api/pacientes/<id> - Deletar paciente

Consultas

    GET /api/consultas - Listar consultas

    POST /api/consultas - Agendar consulta

(E rotas correspondentes em /api/exames, /api/medicos e /api/dashboard)
🔒 Segurança

✅ Autenticação JWT (Renovação e expiração configuráveis)
✅ Hash Bcrypt (Sem armazenamento de senhas em plaintext)
✅ CORS Configurado (Proteção contra acesso não autorizado)
✅ Grupos de Segurança AWS (Acesso de banco de dados e SSH controlados via Terraform)
🤝 Contribuição

Para contribuir com o projeto:

    Fork o repositório

    Crie uma branch para sua feature (git checkout -b feature/AmazingFeature)

    Commit suas mudanças (git commit -m 'feat: Adiciona nova funcionalidade')

    Push para a branch (git push origin feature/AmazingFeature)

    Abra um Pull Request

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

    LinkedIn: [linkedin]
