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

## 7b. Banco em detalhe (modelagem relacional avançada)

MySQL 8 no RDS, com **duas camadas**: o app usa o ORM (SQLAlchemy) para o CRUD do dia a dia; por baixo há objetos de banco que mostram modelagem avançada. **Tudo criado automaticamente no startup.**

**As 4 peças**
- **Tabelas** (~15): criadas pelo SQLAlchemy a partir de `models.py`.
- **Views** (4): `vw_agenda_hoje`, `vw_historico_paciente`, `vw_financeiro_mensal`, `vw_exames_pendentes`. Encapsulam JOINs complexos. → Demo ao vivo: card "Financeiro Mensal" em **Relatórios** lê `vw_financeiro_mensal`.
- **Procedures** (6) com **transação**: `sp_cadastrar_paciente`, `sp_agendar_consulta`, `sp_registrar_pagamento`... usam `START TRANSACTION` + `COMMIT`/`ROLLBACK` e validações (CPF duplicado, conflito de horário).
- **Triggers** (6): auditoria automática em `logs_auditoria` a cada INSERT/UPDATE/DELETE.

**Fluxo no deploy (automático, nada manual)**
```
App sobe na EC2
 1. SQLAlchemy cria as TABELAS
 2. schema_upgrade ajusta colunas
 3. db_objects cria VIEWS + PROCEDURES + TRIGGERS (migrations/004_objetos_banco.sql)
 4. SEED roda → INSERTs disparam TRIGGERS → logs_auditoria nasce populada
```

**3 provas rápidas na demo**
| Recurso | Como mostrar |
|---------|--------------|
| View | Relatórios → card "Financeiro Mensal · via VIEW" |
| Procedure + transação | `CALL sp_cadastrar_paciente(...)` no cliente SQL |
| Trigger | `SELECT * FROM logs_auditoria ORDER BY id DESC;` |

**Se perguntarem "por que lógica no banco se já tem no app?"**
> Camadas complementares: o app valida para a UX; o banco garante integridade independente de quem acessa — transações evitam dados pela metade, triggers garantem auditoria sempre, views centralizam consultas complexas.

**Cola de uma linha**
> "MySQL no RDS com ORM para o CRUD, mais views, procedures transacionais e triggers de auditoria — criados automaticamente no deploy e demonstráveis ao vivo."

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
