"""
MedSystem Auth Routes - Autenticação e Login
"""
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models import Usuario, Medico, LogAuditoria
from decorators import admin_required

auth_bp = Blueprint('auth', __name__)

def validar_senha_forte(senha):
    if len(senha) < 8: return False, "Mínimo 8 caracteres"
    if not any(c.isupper() for c in senha): return False, "Mínimo 1 letra maiúscula"
    if not any(c.islower() for c in senha): return False, "Mínimo 1 letra minúscula"
    if not any(c.isdigit() for c in senha): return False, "Mínimo 1 número"
    caracteres_especiais = "!@#$%^&*()_+-=[]{}';:\"\\|,.<>/?`~"
    if not any(c in caracteres_especiais for c in senha): return False, "Mínimo 1 caractere especial"
    return True, "Senha válida"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        try:
            return render_template('login.html')
        except Exception as e:
            return jsonify({'sucesso': False, 'mensagem': f'Erro ao carregar página: {str(e)}'}), 500

    try:
        dados = request.get_json()
        if not dados: return jsonify({'sucesso': False, 'mensagem': 'Dados não fornecidos'}), 400
        
        user = Usuario.query.filter_by(email=dados.get('email')).first()
        if user and user.verificar_senha(dados.get('senha')):
            if not user.ativo:
                return jsonify({'sucesso': False, 'mensagem': 'Usuário inativo'}), 401
                
            access_token = create_access_token(identity=str(user.id))
            
            # --- AJUSTE AQUI: Garante o envio de CRM e Especialidade direto no Login ---
            usuario_dados = user.to_dict()
            usuario_dados['crm'] = 'N/A'
            usuario_dados['especialidade'] = 'N/A'
            
            if user.tipo == 'medico' and getattr(user, 'medico', None):
                usuario_dados['crm'] = user.medico.crm
                usuario_dados['especialidade'] = user.medico.especialidade.nome if user.medico.especialidade else 'N/A'
                
            return jsonify({
                'sucesso': True, 
                'mensagem': 'Login realizado com sucesso', 
                'token': access_token, 
                'usuario': usuario_dados
            }), 200
        
        return jsonify({'sucesso': False, 'mensagem': 'E-mail ou senha incorretos'}), 401
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obter_perfil():
    try:
        usuario = Usuario.query.get(get_jwt_identity())
        if not usuario: return jsonify({'sucesso': False, 'mensagem': 'Usuário não encontrado'}), 404
        
        # --- AJUSTE AQUI: Facilita a leitura para o Frontend ---
        resposta = usuario.to_dict()
        resposta['crm'] = 'N/A'
        resposta['especialidade'] = 'N/A'
        
        if usuario.tipo == 'medico' and getattr(usuario, 'medico', None):
            resposta['crm'] = usuario.medico.crm
            resposta['especialidade'] = usuario.medico.especialidade.nome if usuario.medico.especialidade else 'N/A'
            
        return jsonify({'sucesso': True, 'dados': resposta}), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
@admin_required
def registrar():
    try:
        dados = request.get_json()
        if not dados.get('email') or not dados.get('senha') or not dados.get('nome'):
            return jsonify({'sucesso': False, 'mensagem': 'Dados obrigatórios faltando'}), 400
            
        senha_valida, msg = validar_senha_forte(dados['senha'])
        if not senha_valida: return jsonify({'sucesso': False, 'mensagem': msg}), 400
        
        if Usuario.query.filter_by(email=dados['email']).first():
            return jsonify({'sucesso': False, 'mensagem': 'Email já cadastrado'}), 409
            
        tipo_usuario = dados.get('tipo', 'recepcao')
        
        # 1. Cria o login (Usuario)
        novo_usuario = Usuario(nome=dados['nome'], email=dados['email'], tipo=tipo_usuario, ativo=True)
        novo_usuario.set_senha(dados['senha'])
        db.session.add(novo_usuario)
        
        # 2. Salva temporariamente para o banco gerar o novo_usuario.id
        db.session.flush()
        
        # 3. Se for médico, já cria o perfil atrelado na tabela 'medicos'
        if tipo_usuario == 'medico':
            crm = dados.get('crm')
            id_especialidade = dados.get('id_especialidade')
            
            # Trava de segurança
            if not crm or not id_especialidade:
                db.session.rollback()
                return jsonify({'sucesso': False, 'mensagem': 'CRM e Especialidade são obrigatórios para cadastrar um médico.'}), 400
                
            novo_medico = Medico(
                id_usuario=novo_usuario.id,
                crm=crm,
                id_especialidade=id_especialidade
            )
            db.session.add(novo_medico)
        
        # 4. Registra o log
        log = LogAuditoria(tabela='usuarios', operacao='INSERT', id_registro=novo_usuario.id, detalhe=f'Novo usuário criado ({tipo_usuario})')
        db.session.add(log)
        
        # 5. Salva tudo de forma definitiva
        db.session.commit()
        
        return jsonify({'sucesso': True, 'mensagem': 'Usuário registrado com sucesso', 'dados': novo_usuario.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


@auth_bp.route('/usuarios', methods=['GET'])
@jwt_required()
@admin_required
def listar_usuarios():
    try:
        # Puxa APENAS os usuários ativos
        usuarios = Usuario.query.filter_by(ativo=True).all()
        return jsonify({'sucesso': True, 'total': len(usuarios), 'dados': [u.to_dict() for u in usuarios]}), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

@auth_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def deletar_usuario(id):
    try:
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({'sucesso': False, 'mensagem': 'Usuário não encontrado'}), 404
        
        # Soft Delete
        usuario.ativo = False
        db.session.commit()
        
        return jsonify({'sucesso': True, 'mensagem': 'Usuário desativado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


@auth_bp.route('/especialidades', methods=['GET'])
def listar_especialidades():
    """Retorna lista de todas as especialidades - Sem autenticação para loading inicial"""
    try:
        from models import Especialidade
        especialidades = Especialidade.query.all()
        
        return jsonify({
            'sucesso': True,
            'total': len(especialidades),
            'dados': [{'id': e.id, 'nome': e.nome} for e in especialidades]
        }), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500