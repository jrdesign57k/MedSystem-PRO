"""
MedSystem Auth Routes - Autenticação e Login com JWT
"""

from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db  # ✓ Importa do local correto
from models import Usuario, Medico, LogAuditoria
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# ════════════════════════════════════════════════════════════
# LOGIN - GET (Página) e POST (Processamento)
# ════════════════════════════════════════════════════════════
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se for GET, apenas entrega a página HTML
    if request.method == 'GET':
        try:
            return render_template('login.html')
        except Exception as e:
            return jsonify({'sucesso': False, 'mensagem': f'Erro ao carregar página: {str(e)}'}), 500

    # Se for POST, processa os dados do formulário/JSON
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({'sucesso': False, 'mensagem': 'Dados não fornecidos'}), 400

        email = dados.get('email')
        senha = dados.get('senha')

        # Buscar usuário por email
        user = Usuario.query.filter_by(email=email).first()

        # Validar senha usando o método do models.py
        if user and user.verificar_senha(senha):
            if not user.ativo:
                return jsonify({'sucesso': False, 'mensagem': 'Usuário inativo'}), 401

            # Gerar JWT token (usando o ID do usuário como identidade)
            access_token = create_access_token(identity=str(user.id))

            return jsonify({
                'sucesso': True,
                'mensagem': 'Login realizado com sucesso',
                'token': access_token,
                'usuario': user.to_dict()
            }), 200
        
        return jsonify({'sucesso': False, 'mensagem': 'E-mail ou senha incorretos'}), 401

    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': f'Erro interno: {str(e)}'}), 500

# ════════════════════════════════════════════════════════════
# REGISTRAR - POST /api/auth/register (Apenas ADMINS)
# ════════════════════════════════════════════════════════════
@auth_bp.route('/register', methods=['POST']) # Alterado para 'register' para casar com o JS
@jwt_required() # Tranca a rota: exige estar logado
def registrar():
    try:
        # Verifica se quem está tentando criar o usuário é um MASTER/ADMIN
        id_solicitante = get_jwt_identity()
        usuario_solicitante = Usuario.query.get(id_solicitante)
        
        if not usuario_solicitante or (usuario_solicitante.tipo != 'admin' and usuario_solicitante.email != 'medico@medsystem.com'):
            return jsonify({'sucesso': False, 'mensagem': 'Acesso negado. Apenas administradores podem criar usuários.'}), 403

        dados = request.get_json()
        
        if not dados.get('email') or not dados.get('senha') or not dados.get('nome'):
            return jsonify({'sucesso': False, 'mensagem': 'Dados obrigatórios faltando'}), 400
        
        if Usuario.query.filter_by(email=dados['email']).first():
            return jsonify({'sucesso': False, 'mensagem': 'Email já cadastrado'}), 409
        
        # START TRANSACTION
        try:
            novo_usuario = Usuario(
                nome=dados['nome'],
                email=dados['email'],
                tipo=dados.get('tipo', 'recepcao') # Alinhado com as opções do JS (recepcao, medico, admin)
            )
            novo_usuario.set_senha(dados['senha'])
            
            db.session.add(novo_usuario)
            db.session.flush()
            
            # Log de Auditoria Master
            log = LogAuditoria(
                tabela='usuarios',
                operacao='INSERT',
                id_registro=novo_usuario.id,
                detalhe=f'Novo usuário ({novo_usuario.tipo}) criado pelo Master: {usuario_solicitante.nome}'
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Usuário registrado com sucesso',
                'dados': novo_usuario.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            raise e
            
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500

# ════════════════════════════════════════════════════════════
# PERFIL - GET /api/auth/perfil
# ════════════════════════════════════════════════════════════
@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obter_perfil():
    try:
        id_usuario = get_jwt_identity()
        usuario = Usuario.query.get(id_usuario)
        
        if not usuario:
            return jsonify({'sucesso': False, 'mensagem': 'Usuário não encontrado'}), 404
        
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

# ════════════════════════════════════════════════════════════
# ALTERAR SENHA - PUT /api/auth/alterar-senha
# ════════════════════════════════════════════════════════════
@auth_bp.route('/alterar-senha', methods=['PUT'])
@jwt_required()
def alterar_senha():
    try:
        id_usuario = get_jwt_identity()
        usuario = Usuario.query.get(id_usuario)
        
        dados = request.get_json()
        senha_atual = dados.get('senha_atual', '')
        nova_senha = dados.get('nova_senha', '')

        if not usuario.verificar_senha(senha_atual):
            return jsonify({'sucesso': False, 'mensagem': 'Senha atual incorreta'}), 401
        
        # START TRANSACTION
        try:
            usuario.set_senha(nova_senha)
            
            # Log de segurança
            log = LogAuditoria(
                tabela='usuarios',
                operacao='UPDATE',
                id_registro=usuario.id,
                detalhe=f'Usuário atualizou a própria senha'
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({'sucesso': True, 'mensagem': 'Senha alterada com sucesso'}), 200
            
        except Exception as e:
            db.session.rollback()
            raise e
            
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500