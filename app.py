"""
MedSystem - Backend Principal (Flask Factory)
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from extensions import db, jwt, bcrypt
import os
from dotenv import load_dotenv


# Carrega as variáveis do arquivo .env a partir do diretório do módulo
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

def create_app():
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')
    
    # ──── CONFIGURAÇÕES DE AMBIENTE (MySQL) ────
    # Resgata as credenciais do .env
    db_user = os.getenv('DB_USER', 'root')
    db_pass = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'medsystem_novo')

    # Configurações do App - String de conexão do SQLAlchemy para MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'medsystem-mestra-2026-secret') # Ideal colocar no .env também

    # ──── INICIALIZAÇÃO DAS EXTENSÕES ────
    # Vincula as ferramentas ao aplicativo
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    with app.app_context():
        # ──── REGISTRO DE ROTAS (BLUEPRINTS) ────
        from models import Usuario 
        from routes.auth import auth_bp
        from routes.pacientes import pacientes_bp
        from routes.consultas import consultas_bp
        from routes.additional import exames_bp, dashboard_bp
        from routes.medicos import medicos_bp

        # Registro das rotas
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(pacientes_bp, url_prefix='/api/pacientes')
        app.register_blueprint(consultas_bp, url_prefix='/api/consultas')
        app.register_blueprint(exames_bp, url_prefix='/api/exames')
        app.register_blueprint(medicos_bp, url_prefix='/api/medicos')
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
        
       # ──── CRIAÇÃO DO BANCO E DADOS INICIAIS ──── 
        try: 
            db.create_all() 
            
            # ──── INSERIR ESPECIALIDADES AUTOMATICAMENTE ────
            from models import Especialidade, Medico  # Certifique-se de que o nome da classe no seu models.py é Especialidade
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

            # Verifica se o usuário ADMIN (Principal) existe 
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
            
            # Verifica se o usuário ADMIN (Principal) existe
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
            
            # Verifica se o usuário de teste (médico comum) existe
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
                
                # Criar registro de médico com CRM formatado (XX000000)
                medico_record = Medico(
                    id_usuario=user.id,
                    crm="SP123456",  # Formato fixo: UF + números
                    id_especialidade=2  # Clínica Geral
                )
                db.session.add(medico_record)
                print("\n" + "="*50)
                print("✓ USUÁRIO MÉDICO CRIADO: drcarlos@medsystem.com")
                print("✓ SENHA DEFINIDA: MedSystem12#")
                print("✓ CRM DEFINIDO: SP123456")
                print("="*50 + "\n")
            
            if admin or medico:
                db.session.commit()
                print("\n✓ Sistema pronto.")
                print("  Admin Principal: medico@medsystem.com / MedSystem12#")
                print("  Médico Exemplo: drcarlos@medsystem.com / MedSystem12#\n")
            else:
                db.session.commit()
                print("\n" + "="*50)
                print("✓ BANCO INICIALIZADO COM SUCESSO")
                print("✓ ADMIN PRINCIPAL CRIADO: medico@medsystem.com")
                print("✓ SENHA: MedSystem12#")
                print("="*50 + "\n")
                
        except Exception as e:
            # Se erro de tabela, tenta fazer DROP ALL e recriar
            if "Table" in str(e) or "doesn't exist" in str(e):
                print(f"\n⚠️ Estrutura de banco desatualizada detectada")
                print(f"   Erro: {str(e)[:100]}...")
                print(f"\n   Removendo estrutura antiga e recriando...\n")
                try:
                    db.drop_all()
                    db.create_all()
                    
                    # Criar especialidades
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
                    db.session.flush()
                    
                    # Criar usuário admin principal
                    admin_user = Usuario(
                        nome="Administrador Principal",
                        email="medico@medsystem.com",
                        tipo="admin",
                        ativo=True
                    )
                    admin_user.set_senha("MedSystem12#")
                    db.session.add(admin_user)
                    db.session.flush()
                    
                    # Criar usuário médico de teste
                    user = Usuario(
                        nome="Dr. Carlos Mendonça",
                        email="drcarlos@medsystem.com",
                        tipo="medico",
                        ativo=True
                    )
                    user.set_senha("MedSystem12#")
                    db.session.add(user)
                    db.session.flush()
                    
                    # Criar registro de médico com CRM formatado
                    medico_record = Medico(
                        id_usuario=user.id,
                        crm="SP123456",  # Formato fixo: UF + números
                        id_especialidade=2  # Clínica Geral
                    )
                    db.session.add(medico_record)
                    db.session.commit()
                    
                    print("="*50)
                    print("✓ BANCO RECRIADO COM SUCESSO")
                    print("✓ ADMIN PRINCIPAL: medico@medsystem.com")
                    print("✓ MÉDICO TESTE: drcarlos@medsystem.com")
                    print("✓ CRM MÉDICO: SP123456")
                    print("✓ ESPECIALIDADES: 8 adicionadas")
                    print("✓ SENHA: MedSystem12#")
                    print("="*50 + "\n")
                except Exception as e2:
                    print(f"\n✗ Erro ao recriar: {e2}\n")
            else:
                print(f"\n⚠️ Erro crítico na inicialização: {e}\n")


    # ──── ROTA PARA O FRONTEND ────
    @app.route('/')
    def index():
        """Entrega a página inicial (index.html com login + dashboard)"""
        try:
            return render_template('index.html')
        except Exception as e:
            print(f"\n⚠️ Erro ao renderizar index.html: {e}\n")
            import traceback
            traceback.print_exc()
            return f"<h1>Erro ao carregar página</h1><p>{str(e)}</p>", 500

    # ──── HEALTH CHECK (REQUISITO DA AULA 16) ────
    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint para verificar a saúde da API e do Banco de Dados"""
        try:
            # Tenta fazer uma consulta simples para testar o banco
            db.session.execute(db.text('SELECT 1'))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "error", "database": "disconnected", "details": str(e)}), 500

    # ──── DASHBOARD ────
    @app.route('/dashboard')
    def dashboard():
        """Entrega a página do dashboard"""
        try:
            return render_template('dashboard.html')
        except Exception as e:
            print(f"\n⚠️ Erro ao renderizar dashboard.html: {e}\n")
            import traceback
            traceback.print_exc()
            return f"<h1>Erro ao carregar dashboard</h1><p>{str(e)}</p>", 500

    # ──── APP ROUTES (COM SIDEBAR) ────
    @app.route('/app/dashboard')
    def app_dashboard():
        """Dashboard com sidebar"""
        try:
            return render_template('app_dashboard.html', page='dashboard')
        except Exception as e:
            return f"<h1>Erro</h1><p>{str(e)}</p>", 500

    @app.route('/app/pacientes')
    def app_pacientes():
        """Listagem de pacientes"""
        try:
            return render_template('app_pacientes.html', page='pacientes')
        except Exception as e:
            return f"<h1>Erro</h1><p>{str(e)}</p>", 500

    @app.route('/app/paciente/<int:paciente_id>')
    def app_ficha_paciente(paciente_id):
        """Ficha detalhada do paciente"""
        try:
            return render_template('app_ficha_paciente.html', page='pacientes', paciente_id=paciente_id)
        except Exception as e:
            return f"<h1>Erro</h1><p>{str(e)}</p>", 500

    @app.route('/app/novo-paciente')
    def app_novo_paciente():
        """Formulário novo paciente"""
        try:
            return render_template('app_novo_paciente.html', page='novo-paciente')
        except Exception as e:
            return f"<h1>Erro</h1><p>{str(e)}</p>", 500

    @app.route('/app/editar-paciente/<int:paciente_id>')
    def app_editar_paciente(paciente_id):
        """Formulário editar paciente"""
        try:
            return render_template('app_novo_paciente.html', page='pacientes', paciente_id=paciente_id, edit_mode=True)
        except Exception as e:
            return f"<h1>Erro</h1><p>{str(e)}</p>", 500

    @app.route('/app/consultas')
    def app_consultas():
        """Listagem de consultas (placeholder)"""
        return render_template('app_dashboard.html', page='consultas')

    @app.route('/app/exames')
    def app_exames():
        """Listagem de exames (placeholder)"""
        return render_template('app_dashboard.html', page='exames')

    @app.route('/app/diagnosticos')
    def app_diagnosticos():
        """Listagem de diagnósticos (placeholder)"""
        return render_template('app_dashboard.html', page='diagnosticos')

    # ──── HANDLER DE ERROS GLOBAL ────
    @app.errorhandler(500)
    def handle_500_error(error):
        """Captura erros 500 e mostra detalhes"""
        print(f"\n✗ ERRO 500: {error}\n")
        import traceback
        traceback.print_exc()
        return f"<h1>Erro Interno do Servidor</h1><p>{str(error)}</p>", 500

    @app.errorhandler(404)
    def handle_404_error(error):
        """Captura erros 404"""
        return f"<h1>Página não encontrada</h1><p>{str(error)}</p>", 404

    return app

if __name__ == '__main__':
    # Cria o app e inicia o servidor
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)