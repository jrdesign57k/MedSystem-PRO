"""
MedSystem Pacientes Routes - CRUD com transações COMMIT/ROLLBACK
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Paciente, LogAuditoria, Usuario
from datetime import datetime

pacientes_bp = Blueprint('pacientes', __name__)

# ════════════════════════════════════════════════════════════
# GET /api/pacientes
# Listar todos os pacientes ativos
# ════════════════════════════════════════════════════════════
@pacientes_bp.route('', methods=['GET'])
@jwt_required()
def listar_pacientes():
    """Lista todos os pacientes ativos"""
    try:
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = request.args.get('por_pagina', 10, type=int)
        
        query = Paciente.query.filter_by(ativo=True)
        total = query.count()
        
        pacientes = query.paginate(page=pagina, per_page=por_pagina)
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Pacientes carregados',
            'total': total,
            'pagina': pagina,
            'dados': [p.to_dict() for p in pacientes.items]
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao listar pacientes: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# GET /api/pacientes/<id>
# Buscar paciente por ID
# ════════════════════════════════════════════════════════════
@pacientes_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def buscar_paciente(id):
    """Busca um paciente específico"""
    try:
        paciente = Paciente.query.get(id)
        
        if not paciente or not paciente.ativo:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Paciente não encontrado'
            }), 404
        
        return jsonify({
            'sucesso': True,
            'dados': paciente.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# GET /api/pacientes/cpf/<cpf>
# Buscar paciente por CPF
# ════════════════════════════════════════════════════════════
@pacientes_bp.route('/cpf/<cpf>', methods=['GET'])
@jwt_required()
def buscar_por_cpf(cpf):
    """Busca paciente por CPF"""
    try:
        paciente = Paciente.query.filter_by(cpf=cpf, ativo=True).first()
        
        if not paciente:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Paciente não encontrado'
            }), 404
        
        return jsonify({
            'sucesso': True,
            'dados': paciente.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# GET /api/pacientes/buscar?nome=João
# Buscar paciente por nome (LIKE)
# ════════════════════════════════════════════════════════════
@pacientes_bp.route('/buscar', methods=['GET'])
@jwt_required()
def buscar_por_nome():
    """Busca pacientes por nome"""
    try:
        nome = request.args.get('nome', '', type=str)
        
        if not nome:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Informe um nome para buscar'
            }), 400
        
        pacientes = Paciente.query.filter(
            Paciente.nome.ilike(f'%{nome}%'),
            Paciente.ativo == True
        ).all()
        
        return jsonify({
            'sucesso': True,
            'total': len(pacientes),
            'dados': [p.to_dict() for p in pacientes]
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# POST /api/pacientes
# Criar novo paciente (INSERT + COMMIT)
# ════════════════════════════════════════════════════════════
@pacientes_bp.route('', methods=['POST'])
@jwt_required()
def criar_paciente():
    try:
        dados = request.get_json()
        
        # Validação
        if not dados.get('cpf') or not dados.get('nome'):
            return jsonify({
                'sucesso': False,
                'mensagem': 'CPF e nome são obrigatórios'
            }), 400
        
        # Verificar CPF duplicado
        if Paciente.query.filter_by(cpf=dados['cpf']).first():
            return jsonify({
                'sucesso': False,
                'mensagem': 'CPF já cadastrado'
            }), 409
        
        # START TRANSACTION - Criar paciente
        try:
            paciente = Paciente(
                cpf=dados['cpf'],
                nome=dados['nome'],
                data_nascimento=datetime.fromisoformat(dados['data_nascimento']).date(),
                sexo=dados.get('sexo', 'M'),
                telefone=dados.get('telefone'),
                email=dados.get('email'),
                endereco=dados.get('endereco'),
                tipo_sanguineo=dados.get('tipo_sanguineo'),
                alergias=dados.get('alergias'),
                observacoes=dados.get('observacoes'),
                ativo=True
            )
            
            db.session.add(paciente)
            db.session.flush()  # Obtém o ID antes de commit
            
            # Log auditoria - CORRIGIDO: paciente.id_paciente
            log = LogAuditoria(
                tabela='paciente',
                operacao='INSERT',
                id_registro=paciente.id_paciente,
                detalhe=f'Novo paciente: {paciente.nome}'
            )
            db.session.add(log)
            
            db.session.commit()  # ✓ COMMIT
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Paciente cadastrado com sucesso',
                'dados': paciente.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()  # ✗ ROLLBACK
            raise e
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao cadastrar paciente: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# PUT /api/pacientes/<id>
# Atualizar dados do paciente (UPDATE + COMMIT)
# ════════════════════════════════════════════════════════════
@pacientes_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar_paciente(id):
    try:
        paciente = Paciente.query.get(id)
        
        if not paciente or not paciente.ativo:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Paciente não encontrado'
            }), 404
        
        dados = request.get_json()
        
        # START TRANSACTION - Atualizar paciente
        try:
            # Atualizar apenas campos fornecidos (COALESCE)
            if 'nome' in dados:
                paciente.nome = dados['nome']
            if 'telefone' in dados:
                paciente.telefone = dados['telefone']
            if 'email' in dados:
                paciente.email = dados['email']
            if 'endereco' in dados:
                paciente.endereco = dados['endereco']
            if 'tipo_sanguineo' in dados:
                paciente.tipo_sanguineo = dados['tipo_sanguineo']
            if 'alergias' in dados:
                paciente.alergias = dados['alergias']
            if 'observacoes' in dados:
                paciente.observacoes = dados['observacoes']
            
            db.session.flush()
            
            # Log auditoria - CORRIGIDO: paciente.id_paciente
            log = LogAuditoria(
                tabela='paciente',
                operacao='UPDATE',
                id_registro=paciente.id_paciente,
                detalhe=f'Paciente atualizado: {paciente.nome}'
            )
            db.session.add(log)
            db.session.commit()  # ✓ COMMIT
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Paciente atualizado com sucesso',
                'dados': paciente.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()  # ✗ ROLLBACK
            raise e
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao atualizar paciente: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# DELETE /api/pacientes/<id>
# Desativar paciente (SOFT DELETE + COMMIT)
# ════════════════════════════════════════════════════════════
@pacientes_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar_paciente(id):
    try:
        paciente = Paciente.query.get(id)
        
        if not paciente:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Paciente não encontrado'
            }), 404
        
        # START TRANSACTION - Desativar paciente
        try:
            nome_paciente = paciente.nome
            paciente.ativo = False
            
            db.session.flush()
            
            # Log auditoria - CORRIGIDO: paciente.id_paciente
            log = LogAuditoria(
                tabela='paciente',
                operacao='DELETE',
                id_registro=paciente.id_paciente,
                detalhe=f'Paciente desativado: {nome_paciente}'
            )
            db.session.add(log)
            db.session.commit()  # ✓ COMMIT
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Paciente desativado com sucesso'
            }), 200
            
        except Exception as e:
            db.session.rollback()  # ✗ ROLLBACK
            raise e
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro ao desativar paciente: {str(e)}'
        }), 500