"""Gera PDF de apresentacao MedSystem PRO para Amostratec."""
from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, "MedSystem PRO - Amostratec", align="R")
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, f"Pagina {self.page_no()}", align="C")

    def section(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(15, 23, 42)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(226, 232, 240)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(51, 65, 85)
        self.multi_cell(0, 6, title)
        self.ln(1)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 41, 59)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 41, 59)
        self.multi_cell(0, 5.5, f"  -  {text}")

    def quote(self, text):
        self.ln(2)
        self.set_fill_color(239, 246, 255)
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(51, 65, 85)
        self.multi_cell(0, 6, text, fill=True)
        self.ln(3)

    def table(self, headers, rows, col_w):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(241, 245, 249)
        self.set_text_color(15, 23, 42)
        for i, h in enumerate(headers):
            self.cell(col_w[i], 7, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 41, 59)
        for row in rows:
            x0, y0 = self.get_x(), self.get_y()
            heights = []
            lines = []
            for i, cell in enumerate(row):
                self.set_xy(x0 + sum(col_w[:i]), y0)
                lines.append(self.multi_cell(col_w[i], 5, cell, split_only=True))
            max_lines = max(len(l) for l in lines)
            h = max(7, max_lines * 5)
            for i, cell in enumerate(row):
                self.set_xy(x0 + sum(col_w[:i]), y0)
                self.multi_cell(col_w[i], 5, cell, border=1)
            self.set_xy(x0, y0 + h)
        self.ln(3)


def main():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Capa
    pdf.ln(25)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 12, "MedSystem PRO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 8, "Sistema de Gestao Clinica + Arquitetura Cloud AWS", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Amostratec  |  Cloud Computing", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, "Flask  |  MySQL  |  Terraform  |  AWS", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.section("1. O que e o projeto")
    pdf.body(
        "O MedSystem PRO e um sistema web completo para gestao de consultorio/clinica. "
        "Centraliza agenda, prontuario eletronico, exames, prescricoes, diagnosticos (CID-10), "
        "financeiro, relatorios, equipe e mensagens internas."
    )
    pdf.quote(
        '"Desenvolvemos um sistema clinico funcional e o publicamos na AWS com Terraform: '
        'um unico terraform apply sobe rede, banco privado, API, frontend no S3 e HTTPS via CloudFront."'
    )
    pdf.sub("Login de demonstracao")
    pdf.table(
        ["Campo", "Valor"],
        [
            ["E-mail", "medico@medsystem.com"],
            ["Senha", "MedSystem12#"],
            ["GitHub", "github.com/jrdesign57k/MedSystem-PRO"],
        ],
        [40, 150],
    )

    pdf.section("2. Modulos do sistema")
    pdf.table(
        ["Modulo", "Funcao"],
        [
            ["Dashboard", "Indicadores do dia: consultas, pacientes, alertas"],
            ["Agenda", "Calendario semanal de consultas"],
            ["Pacientes", "Cadastro completo com dados pessoais e medicos"],
            ["Consultas", "Agendamento, status e historico"],
            ["Prontuario", "Anamnese, exame fisico, sinais vitais, conduta"],
            ["Prescricoes / Exames", "Receituarios e solicitacao de exames"],
            ["Diagnosticos", "Registro clinico com CID-10"],
            ["Financeiro", "Receitas, despesas e precos por consulta"],
            ["Relatorios", "Indicadores e exportacao PDF"],
            ["Equipe / Mensagens", "Usuarios, medicos e comunicacao interna"],
        ],
        [45, 145],
    )

    pdf.section("3. Stack tecnologica")
    pdf.sub("Backend")
    for item in [
        "Python 3 / Flask",
        "SQLAlchemy (ORM)",
        "MySQL 8.0",
        "JWT + Bcrypt",
        "API REST (JSON)",
    ]:
        pdf.bullet(item)
    pdf.sub("Frontend")
    for item in [
        "HTML5 + Jinja2 (partials modulares)",
        "CSS3 responsivo (design PRO)",
        "JavaScript vanilla",
        "Interface desktop e mobile",
    ]:
        pdf.bullet(item)

    pdf.section("4. Arquitetura da aplicacao")
    pdf.body(
        "Frontend (browser) -> Backend Flask (11 blueprints) -> MySQL 8.0\n"
        "Todas as rotas da API (exceto login) exigem token JWT no header Authorization."
    )
    pdf.table(
        ["Modulo", "Rota API"],
        [
            ["Autenticacao", "/api/auth"],
            ["Pacientes", "/api/pacientes"],
            ["Consultas", "/api/consultas"],
            ["Exames / Dashboard", "/api/exames  |  /api/dashboard"],
            ["Prontuarios", "/api/prontuarios"],
            ["Financeiro / Relatorios", "/api/financeiro  |  /api/relatorios"],
            ["CID-10 / Mensagens", "/api/cid10  |  /api/mensagens"],
        ],
        [55, 135],
    )

    pdf.add_page()
    pdf.section("5. Arquitetura em nuvem (AWS) - Foco principal")
    pdf.body(
        "Internet -> CloudFront (HTTPS) -> S3 (frontend estatico) + EC2 (API Flask :5000) -> RDS MySQL (subnets privadas).\n"
        "CloudFront e o ponto de entrada unico: entrega o site pelo S3 e encaminha /api/* para a EC2."
    )
    pdf.table(
        ["Servico AWS", "Funcao"],
        [
            ["VPC + Subnets + IGW", "Rede isolada (publica + privada)"],
            ["EC2 (t2.micro)", "Backend Flask com systemd"],
            ["RDS (db.t3.micro)", "Banco MySQL privado e persistente"],
            ["S3", "Hospedagem do frontend estatico"],
            ["CloudFront + OAC", "HTTPS, CDN; S3 acessivel so pelo CloudFront"],
            ["Terraform", "Infraestrutura como codigo (IaC)"],
        ],
        [50, 140],
    )

    pdf.sub("VPC - Rede")
    pdf.table(
        ["Componente", "Configuracao"],
        [
            ["VPC", "10.0.0.0/16 - DNS habilitado"],
            ["Subnet publica", "10.0.1.0/24 (us-east-1a) -> EC2"],
            ["Subnets privadas", "10.0.2.0/24 e 10.0.3.0/24 -> RDS (2 AZs)"],
            ["Internet Gateway", "Internet so pela subnet publica"],
        ],
        [50, 140],
    )

    pdf.sub("Security Groups")
    pdf.bullet("EC2: porta 5000 liberada APENAS para IPs do CloudFront")
    pdf.bullet("EC2: SSH porta 22 para gerenciamento")
    pdf.bullet("RDS: porta 3306 liberada SOMENTE para o Security Group da EC2")

    pdf.section("6. Deploy automatizado (Terraform)")
    for step in [
        "Cria VPC, subnets, security groups e rotas",
        "Sobe RDS MySQL privado",
        "Sobe EC2: instala deps, clona GitHub, cria .env, configura systemd",
        "Envia medsystem_banco.sql da maquina local para EC2 via SSH",
        "EC2 importa schema no RDS pela rede privada",
        "Inicia Flask somente apos banco pronto",
        "Publica frontend no S3 (monta index.html estatico)",
        "Cria CloudFront e exibe URL HTTPS final",
    ]:
        pdf.bullet(step)
    pdf.body("Resultado: terraform output -> https://xxxx.cloudfront.net")

    pdf.section("7. Banco de dados")
    pdf.bullet("Tabelas: usuarios, medicos, paciente, consulta, exames, prescricoes, diagnosticos, receitas, despesas, mensagens, cid10")
    pdf.bullet("Stored Procedures: cadastrar paciente, agendar/cancelar consulta, registrar prontuario, pagamento")
    pdf.bullet("Triggers: auditoria automatica")
    pdf.bullet("Views: agenda do dia, historico paciente, financeiro mensal, exames pendentes")

    pdf.section("8. Seguranca")
    for item in [
        "HTTPS via CloudFront",
        "S3 privado (OAC - so CloudFront le)",
        "API na EC2 acessivel somente via CloudFront",
        "RDS sem IP publico",
        "Senhas com Bcrypt + JWT",
        "Credenciais, .pem e .sql fora do Git",
    ]:
        pdf.bullet(item)

    pdf.add_page()
    pdf.section("9. Roteiro de demonstracao (5-8 min)")
    for i, step in enumerate([
        "Abrir URL do CloudFront (HTTPS) - mostrar responsividade",
        "Fazer login (JWT)",
        "Mostrar Dashboard com dados da API",
        "Abrir Agenda ou Pacientes",
        "Mostrar Prontuario ou Exames",
        "DevTools: chamadas /api/ via CloudFront",
        "Explicar diagrama S3 + EC2 + RDS + CloudFront",
    ], 1):
        pdf.bullet(f"{i}. {step}")

    pdf.section("10. Perguntas frequentes")
    pdf.table(
        ["Pergunta", "Resposta"],
        [
            ["Por que separar S3 e EC2?", "Escalabilidade: estaticos no S3+CDN; logica na EC2"],
            ["Por que CloudFront?", "HTTPS, cache do frontend e controle de acesso a API"],
            ["Como o banco entra no RDS?", "Importacao pela EC2 dentro da VPC, rede privada"],
            ["O que e Terraform?", "Infraestrutura como codigo - reproduzivel"],
            ["Autenticacao?", "JWT; rotas protegidas exigem Bearer token"],
        ],
        [55, 135],
    )

    pdf.section("11. Checklist antes da apresentacao")
    for item in [
        "terraform apply feito e URL do CloudFront anotada",
        "Login testado na URL de producao",
        "Diagrama de arquitetura preparado",
        "Plano B: python run_app.py -> localhost:5000",
        "GitHub atualizado",
    ]:
        pdf.bullet(item)

    pdf.section("12. Fechamento")
    pdf.quote(
        '"O MedSystem PRO une um sistema clinico funcional - API REST, banco relacional avancado '
        'e interface moderna - a uma arquitetura cloud na AWS com boas praticas de seguranca. '
        'E desenvolvimento full stack e cloud computing integrados em um unico projeto."'
    )

    out = "APRESENTACAO_AMOSTRATEC.pdf"
    pdf.output(out)
    print(f"PDF gerado: {out}")


if __name__ == "__main__":
    main()
