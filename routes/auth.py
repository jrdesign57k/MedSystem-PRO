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
            return jsonify({'sucesso': True, 'mensagem': 'Login realizado com sucesso', 'token': access_token, 'usuario': user.to_dict()}), 200
        
        return jsonify({'sucesso': False, 'mensagem': 'E-mail ou senha incorretos'}), 401
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
            
        novo_usuario = Usuario(nome=dados['nome'], email=dados['email'], tipo=dados.get('tipo', 'recepcao'), ativo=True)
        novo_usuario.set_senha(dados['senha'])
        db.session.add(novo_usuario)
        
        log = LogAuditoria(tabela='usuarios', operacao='INSERT', id_registro=novo_usuario.id, detalhe='Novo usuário criado')
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'sucesso': True, 'mensagem': 'Usuário registrado com sucesso', 'dados': novo_usuario.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obter_perfil():
    try:
        usuario = Usuario.query.get(get_jwt_identity())
        if not usuario: return jsonify({'sucesso': False, 'mensagem': 'Usuário não encontrado'}), 404
        
        resposta = usuario.to_dict()
        if usuario.tipo == 'medico' and getattr(usuario, 'medico', None):
            resposta['medico'] = {
                'id': usuario.medico.id,
                'crm': usuario.medico.crm,
                'especialidade': usuario.medico.especialidade.nome if usuario.medico.especialidade else 'N/A'
            }
        return jsonify({'sucesso': True, 'dados': resposta}), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

@auth_bp.route('/alterar-senha', methods=['PUT'])
@jwt_required()
def alterar_senha():
    try:
        usuario = Usuario.query.get(get_jwt_identity())
        dados = request.get_json()
        if not usuario.verificar_senha(dados.get('senha_atual', '')):
            return jsonify({'sucesso': False, 'mensagem': 'Senha atual incorreta'}), 401
            
        usuario.set_senha(dados.get('nova_senha', ''))
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Senha alterada com sucesso'}), 200
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