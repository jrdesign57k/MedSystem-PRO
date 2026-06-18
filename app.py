"""
MedSystem - Backend Principal Integrado (API + Frontend)
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from extensions import db, jwt, bcrypt
import os
from dotenv import load_dotenv

# Configurações de Caminho Absoluto
base_dir = os.path.dirname(os.path.abspath(__file__))
med_dir = os.path.join(base_dir, 'medsystem')

# Carrega as variáveis do .env FORÇANDO a ignorar qualquer cache antigo do Windows
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

def create_app():
    # Criação do App ensinando o Flask onde procurar o HTML e o CSS
    app = Flask(__name__,
                static_folder=os.path.join(med_dir, 'static'),
                static_url_path='/static',
                template_folder=os.path.join(med_dir, 'templates'))

    # ──── CONFIGURAÇÕES DE AMBIENTE SEGURAS (MySQL) ────
    db_user = os.getenv('DB_USER', 'root')
    db_pass = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', '127.0.0.1')
    db_name = os.getenv('DB_NAME', 'medsystem')

    # Monta a string de conexão
    if db_pass:
        uri = f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}'
    else:
        uri = f'mysql+mysqlconnector://{db_user}@{db_host}/{db_name}'

    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'medsystem-mestra-2026-secret')

    # ──── INICIALIZAÇÃO DAS EXTENSÕES ────
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    with app.app_context():
        # ──── REGISTRO DE ROTAS (BLUEPRINTS) ────
        from models import Usuario
        from medsystem.routes.auth import auth_bp
        from medsystem.routes.pacientes import pacientes_bp
        from medsystem.routes.consultas import consultas_bp
        from medsystem.routes.additional import exames_bp, dashboard_bp
        from medsystem.routes.medicos import medicos_bp
        from medsystem.routes.prontuario import prontuario_bp
        from medsystem.routes.financeiro import financeiro_bp
        from medsystem.routes.cid10 import cid10_bp
        from medsystem.routes.mensagens import mensagens_bp
        from medsystem.routes.relatorios import relatorios_bp
        from medsystem.routes.prescricoes import prescricoes_bp
        from medsystem.routes.portal import portal_bp

        # Registro das rotas da API
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(pacientes_bp, url_prefix='/api/pacientes')
        app.register_blueprint(consultas_bp, url_prefix='/api/consultas')
        app.register_blueprint(exames_bp, url_prefix='/api/exames')
        app.register_blueprint(medicos_bp, url_prefix='/api/medicos')
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
        app.register_blueprint(prontuario_bp, url_prefix='/api/prontuarios')
        app.register_blueprint(financeiro_bp, url_prefix='/api/financeiro')
        app.register_blueprint(cid10_bp, url_prefix='/api/cid10')
        app.register_blueprint(mensagens_bp, url_prefix='/api/mensagens')
        app.register_blueprint(relatorios_bp, url_prefix='/api/relatorios')
        app.register_blueprint(prescricoes_bp, url_prefix='/api/prescricoes')
        app.register_blueprint(portal_bp, url_prefix='/api/portal')

        # ──── CRIAÇÃO DO BANCO E DADOS INICIAIS ────
        try:
            from medsystem.database.schema_upgrade import upgrade_schema
            upgrade_schema()
            db.create_all()

            # Cria views, procedures (com transacao) e triggers de auditoria.
            # Roda antes do seed para os triggers auditarem os inserts demo.
            from medsystem.database.db_objects import aplicar_objetos_banco
            aplicar_objetos_banco()

            # Inserção automática de Especialidades
            from models import Especialidade, Medico
            try:
                if not Especialidade.query.first():
                    especialidades_padrao = [
                        Especialidade(id=1, nome='Cardiologia'),
                        Especialidade(id=2, nome='Clínica Geral'),
                        Especialidade(id=3, nome='Pediatria'),
                        Especialidade(id=4, nome='Ginecologia e Obstetrícia'),
                        Especialidade(id=5, nome='Ortopedia'),
                        Especialidade(id=6, nome='Neurologia'),
                        Especialidade(id=7, nome='Oftalmologia'),
                        Especialidade(id=8, nome='Cirurgia Geral')
                    ]
                    db.session.bulk_save_objects(especialidades_padrao)
                    db.session.commit()
                    print("[OK] 8 Especialidades medicas inseridas com sucesso!")
            except Exception as esp_err:
                print(f"[INFO] Nota: {esp_err}")

            # Tabela de preços (Particular e Convênio)
            from models import PrecoConsulta
            if not PrecoConsulta.query.first():
                precos_padrao = [
                    PrecoConsulta(tipo_consulta='1ª Consulta', modalidade='Particular', nome_convenio=None, valor=250.0),
                    PrecoConsulta(tipo_consulta='Retorno', modalidade='Particular', nome_convenio=None, valor=150.0),
                    PrecoConsulta(tipo_consulta='Urgência', modalidade='Particular', nome_convenio=None, valor=350.0),
                    PrecoConsulta(tipo_consulta='1ª Consulta', modalidade='Convenio', nome_convenio='Unimed', valor=120.0),
                    PrecoConsulta(tipo_consulta='Retorno', modalidade='Convenio', nome_convenio='Unimed', valor=80.0),
                    PrecoConsulta(tipo_consulta='1ª Consulta', modalidade='Convenio', nome_convenio='SulAmérica', valor=110.0),
                    PrecoConsulta(tipo_consulta='Retorno', modalidade='Convenio', nome_convenio='SulAmérica', valor=75.0),
                    PrecoConsulta(tipo_consulta='1ª Consulta', modalidade='Convenio', nome_convenio='Bradesco Saúde', valor=115.0),
                    PrecoConsulta(tipo_consulta='Retorno', modalidade='Convenio', nome_convenio='Bradesco Saúde', valor=78.0),
                ]
                db.session.bulk_save_objects(precos_padrao)
                db.session.commit()
                print("[OK] Tabela de precos (Particular/Convenio) criada!")

            # Criação do usuário Administrador Principal
            admin = Usuario.query.filter_by(email='medico@medsystem.com').first()
            if not admin:
                admin_user = Usuario(
                    nome="Administrador Principal",
                    email="medico@medsystem.com",
                    tipo="admin",
                    ativo=True
                )
                admin_user.set_senha("MedSystem12#")
                db.session.add(admin_user)

            # Criação do usuário Médico Teste (Necessário para associar CRM)
            medico = Usuario.query.filter_by(email='drcarlos@medsystem.com').first()
            if not medico:
                user = Usuario(
                    nome="Dr. Carlos Mendonça",
                    email="drcarlos@medsystem.com",
                    tipo="medico",
                    ativo=True
                )
                user.set_senha("MedSystem12#")
                db.session.add(user)
                db.session.flush()

                medico_record = Medico(
                    id_usuario=user.id,
                    crm="SP123456",
                    id_especialidade=(
                        Especialidade.query.filter_by(nome='Clínica Geral').first().id
                        if Especialidade.query.filter_by(nome='Clínica Geral').first()
                        else 1
                    )
                )
                db.session.add(medico_record)

            db.session.commit()

            from medsystem.database.seed_usuarios import seed_usuarios_demo
            seed_usuarios_demo()

            from medsystem.database.seed_demo import executar_seeds
            executar_seeds()

            from medsystem.database.seed_portal import seed_portal_pacientes
            seed_portal_pacientes()

        except Exception as e:
            print(f'[AVISO] Erro no banco (tabelas ja existem ou ajuste pendente): {e}')


    # ──── ROTA DO FRONTEND (Versão única PRO) ────
    @app.route('/')
    def index():
        """Interface única MedSystem PRO (modular, integrada ao backend)"""
        return render_template('index.html')


    # ──── HEALTH CHECK (Monitoramento do Servidor) ────
    @app.route('/health', methods=['GET'])
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "error", "database": "disconnected", "details": str(e)}), 500


    # ──── HANDLERS DE ERROS GLOBAIS ────
    @app.errorhandler(500)
    def handle_500_error(error):
        print(f"\n[ERRO] 500: {error}\n")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "message": str(error)}), 500

    @app.errorhandler(404)
    def handle_404_error(error):
        return jsonify({"error": "Not Found", "message": "O endpoint ou página solicitada não existe."}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    debug = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes')
    app.run(debug=debug, host='0.0.0.0', port=5000, use_reloader=False)
