"""
MedSystem - Backend Principal (API REST Pura)
"""
from flask import Flask, jsonify
from flask_cors import CORS
from extensions import db, jwt, bcrypt
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env a partir do diretório do módulo
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

def create_app():
    app = Flask(__name__)
    
    # ──── CONFIGURAÇÕES DE AMBIENTE (MySQL) ────
    db_user = os.getenv('DB_USER', 'root')
    db_pass = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'medsystem_novo')

    # Configurações do App - String de conexão do SQLAlchemy para MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'medsystem-mestra-2026-secret')

    # ──── INICIALIZAÇÃO DAS EXTENSÕES ────
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app) # Permite que o Frontend no S3 acesse a API na EC2 sem problemas de CORS

    with app.app_context():
        # ──── REGISTRO DE ROTAS (BLUEPRINTS) ────
        from models import Usuario 
        from routes.auth import auth_bp
        from routes.pacientes import pacientes_bp
        from routes.consultas import consultas_bp
        from routes.additional import exames_bp, dashboard_bp
        from routes.medicos import medicos_bp
        from routes.prontuario import prontuario_bp
        from routes.financeiro import financeiro_bp
        from routes.cid10 import cid10_bp
        from routes.mensagens import mensagens_bp
        from routes.relatorios import relatorios_bp

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
        
        # ──── CRIAÇÃO DO BANCO E DADOS INICIAIS ──── 
        try: 
            db.create_all() 
            
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
                    print("✓ 8 Especialidades médicas inseridas com sucesso!")
            except Exception as esp_err:
                print(f"ℹ Nota: {esp_err}")

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
                db.session.commit()
                print("✓ Usuário Admin criado.")
                
        except Exception as e:
            print(f"⚠️ Erro na inicialização: {e}")
            
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
                db.session.flush()
            
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
                    id_especialidade=2
                )
                db.session.add(medico_record)
            
            db.session.commit()

    # ──── HEALTH CHECK (REQUISITO DA AULA 16) ────
    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint para verificar a saúde da API e do Banco de Dados"""
        try:
            db.session.execute(db.text('SELECT 1'))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "error", "database": "disconnected", "details": str(e)}), 500

    # ──── HANDLER DE ERROS GLOBAL (FORMATO JSON) ────
    @app.errorhandler(500)
    def handle_500_error(error):
        print(f"\n✗ ERRO 500: {error}\n")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error", "message": str(error)}), 500

    @app.errorhandler(404)
    def handle_404_error(error):
        return jsonify({"error": "Not Found", "message": "O endpoint solicitado não existe."}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)