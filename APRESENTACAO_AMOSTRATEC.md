# MedSystem PRO
## Sistema de Gestão Clínica + Arquitetura Cloud AWS
**Amostratec · Cloud Computing**

---

## 1. O que é o projeto

O **MedSystem PRO** é um sistema web completo para gestão de consultório/clínica. Centraliza agenda, prontuário eletrônico, exames, prescrições, diagnósticos (CID-10), financeiro, relatórios, equipe e mensagens internas.

> *"Desenvolvemos um sistema clínico funcional e o publicamos na AWS com Terraform: um único `terraform apply` sobe rede, banco privado, API, frontend no S3 e HTTPS via CloudFront."*

| Campo | Valor |
|-------|-------|
| E-mail | medico@medsystem.com |
| Senha | MedSystem12# |
| GitHub | github.com/jrdesign57k/MedSystem-PRO |

---

## 2. Módulos do sistema

| Módulo | Função |
|--------|--------|
| Dashboard | Indicadores do dia |
| Agenda | Calendário semanal de consultas |
| Pacientes | Cadastro completo |
| Consultas | Agendamento e histórico |
| Prontuário | Anamnese, exame físico, conduta |
| Prescrições / Exames | Receituários e solicitações |
| Diagnósticos | Registro com CID-10 |
| Financeiro | Receitas, despesas, preços |
| Relatórios | Indicadores e PDF |
| Equipe / Mensagens | Usuários e comunicação interna |

---

## 3. Stack tecnológica

**Backend:** Python/Flask · SQLAlchemy · MySQL 8 · JWT · Bcrypt · API REST

**Frontend:** HTML + Jinja2 · CSS responsivo · JavaScript vanilla

---

## 4. Arquitetura da aplicação

```
Frontend → Backend Flask (11 blueprints) → MySQL 8.0
```

| Módulo | Rota |
|--------|------|
| Auth | /api/auth |
| Pacientes | /api/pacientes |
| Consultas | /api/consultas |
| Exames/Dashboard | /api/exames · /api/dashboard |
| Prontuários | /api/prontuarios |
| Financeiro | /api/financeiro |
| Relatórios | /api/relatorios |

---

## 5. Arquitetura AWS (foco principal)

```
Internet → CloudFront (HTTPS)
              ├── S3 (frontend)
              └── EC2 :5000 (API) → RDS MySQL (privado)
```

| Serviço | Função |
|---------|--------|
| VPC | Rede 10.0.0.0/16 |
| EC2 | Backend Flask |
| RDS | MySQL privado (2 subnets) |
| S3 | Frontend estático |
| CloudFront | HTTPS + roteamento |
| Terraform | Infraestrutura como código |

**Security Groups:** EC2 porta 5000 só CloudFront · RDS 3306 só EC2

---

## 6. Deploy (terraform apply)

1. Cria VPC e security groups  
2. Sobe RDS privado  
3. Sobe EC2 + systemd  
4. Importa SQL via SSH (rede privada)  
5. Publica frontend no S3  
6. Cria CloudFront → URL HTTPS  

---

## 7. Banco de dados

Tabelas · Stored Procedures · Triggers · Views (agenda, financeiro, exames pendentes)

---

## 8. Segurança

HTTPS · S3 privado · API via CloudFront · RDS sem IP público · Bcrypt + JWT · segredos fora do Git

---

## 9. Demo (5 min)

1. Abrir URL CloudFront  
2. Login  
3. Dashboard → Agenda → Prontuário  
4. Mostrar chamadas /api/ no DevTools  

---

## 10. Fechamento

> *"Sistema clínico funcional + arquitetura cloud AWS com boas práticas de segurança — full stack e cloud computing no mesmo projeto."*
