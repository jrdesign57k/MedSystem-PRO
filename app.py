"""
MedSystem - Backend Principal (Flask Factory)
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from extensions import db, jwt, bcrypt
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

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
    db_name = os.getenv('DB_NAME', 'medsystem')

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
        from routes.additional import exames_bp, medicos_bp, dashboard_bp

        # Registro das rotas
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(pacientes_bp, url_prefix='/api/pacientes')
        app.register_blueprint(consultas_bp, url_prefix='/api/consultas')
        app.register_blueprint(exames_bp, url_prefix='/api/exames')
        app.register_blueprint(medicos_bp, url_prefix='/api/medicos')
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
        
        # ──── CRIAÇÃO DO BANCO E USUÁRIO INICIAL ────
        try:
            db.create_all()
            
            # Verifica se o usuário padrão existe
            medico = Usuario.query.filter_by(email='medico@medsystem.com').first()
            if not medico:
                user = Usuario(
                    nome="Dr. Carlos Mendonça",
                    email="medico@medsystem.com",
                    tipo="medico",
                    ativo=True
                )
                user.set_senha("123456")
                db.session.add(user)
                db.session.commit()
                print("\n" + "="*50)
                print("✓ BANCO DE DADOS MYSQL INICIALIZADO")
                print("✓ USUÁRIO CRIADO: medico@medsystem.com")
                print("✓ SENHA DEFINIDA: 123456")
                print("="*50 + "\n")
            else:
                print("\n✓ Sistema pronto. Login: medico@medsystem.com\n")
                
        except Exception as e:
            # Se erro de tabela, tenta fazer DROP ALL e recriar
            if "Table" in str(e) or "doesn't exist" in str(e):
                print(f"\n⚠️ Estrutura de banco desatualizada detectada")
                print(f"   Erro: {str(e)[:100]}...")
                print(f"\n   Removendo estrutura antiga e recriando...\n")
                try:
                    db.drop_all()
                    db.create_all()
                    
                    # Criar usuário padrão
                    user = Usuario(
                        nome="Dr. Carlos Mendonça",
                        email="medico@medsystem.com",
                        tipo="medico",
                        ativo=True
                    )
                    user.set_senha("123456")
                    db.session.add(user)
                    db.session.commit()
                    
                    print("="*50)
                    print("✓ BANCO RECRIADO COM SUCESSO")
                    print("✓ USUÁRIO CRIADO: medico@medsystem.com")
                    print("✓ SENHA DEFINIDA: 123456")
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