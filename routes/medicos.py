from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Usuario, Medico, Especialidade

# Define o Blueprint com o nome exato que o app.py utiliza
medicos_bp = Blueprint('medicos', __name__)

# ==========================================
# 1. CRIAR MÉDICO (O SEU CÓDIGO)
# ==========================================
@medicos_bp.route('', methods=['POST'])
@jwt_required()
def criar_medico():
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        crm = dados.get('crm')
        id_especialidade = dados.get('id_especialidade')
        senha = dados.get('senha', '123456')

        if not all([nome, email, crm, id_especialidade]):
            return jsonify({'sucesso': False, 'mensagem': 'Preencha todos os campos'}), 400

        if Usuario.query.filter_by(email=email).first():
            return jsonify({'sucesso': False, 'mensagem': 'Email já cadastrado'}), 409
            
        if Medico.query.filter_by(crm=crm).first():
            return jsonify({'sucesso': False, 'mensagem': 'CRM já cadastrado'}), 409

        # Busca a especialidade no banco
        especialidade = Especialidade.query.get(id_especialidade)
        
        # Se não existir, cria automaticamente para evitar o erro do sistema
        if not int(id_especialidade) or not especialidade:
            nomes_especialidades = {
                1: 'Clínica Geral', 
                2: 'Cardiologia', 
                3: 'Neurologia', 
                4: 'Pediatria', 
                5: 'Oftalmologia'
            }
            nome_esp = nomes_especialidades.get(int(id_especialidade or 1), 'Clínica Geral')
            
            especialidade = Especialidade(id=int(id_especialidade or 1), nome=nome_esp)
            db.session.add(especialidade)
            db.session.flush()

        # Cria o usuário vinculado
        novo_usuario = Usuario(nome=nome, email=email, tipo='medico', ativo=True)
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)
        db.session.flush()

        # Cria o médico
        novo_medico = Medico(
            id_usuario=novo_usuario.id,
            crm=crm,
            id_especialidade=especialidade.id
        )
        db.session.add(novo_medico)
        db.session.commit()

        return jsonify({'sucesso': True, 'mensagem': 'Médico cadastrado com sucesso!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


# ==========================================
# 2. LISTAR TODOS OS MÉDICOS (EVITA O "CARREGANDO...")
# ==========================================
@medicos_bp.route('', methods=['GET'])
@jwt_required()
def listar_medicos():
    try:
        medicos = Medico.query.all()
        # Filtra para mandar só os médicos ativos (para sumirem da tela quando deletados)
        medicos_ativos = [m for m in medicos if m.usuario and m.usuario.ativo]
        
        return jsonify({
            'sucesso': True,
            'total': len(medicos_ativos),
            'dados': [m.to_dict() for m in medicos_ativos]
        }), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


# ==========================================
# 3. BUSCAR MÉDICO ESPECÍFICO
# ==========================================
@medicos_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def buscar_medico(id):
    try:
        medico = Medico.query.get(id)
        if not medico or not medico.usuario.ativo:
            return jsonify({'sucesso': False, 'mensagem': 'Médico não encontrado ou inativo'}), 404
            
        return jsonify({'sucesso': True, 'dados': medico.to_dict()}), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


# ==========================================
# 4. EDITAR MÉDICO
# ==========================================
@medicos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def editar_medico(id):
    try:
        medico = Medico.query.get(id)
        if not medico:
            return jsonify({'sucesso': False, 'mensagem': 'Médico não encontrado'}), 404
            
        dados = request.get_json()
        
        if 'nome' in dados:
            medico.usuario.nome = dados['nome']
        if 'id_especialidade' in dados:
            medico.id_especialidade = dados['id_especialidade']
        if 'ativo' in dados:
            medico.usuario.ativo = dados['ativo']
            
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Médico atualizado com sucesso', 'dados': medico.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


# ==========================================
# 5. DELETAR MÉDICO (SOFT DELETE)
# ==========================================
@medicos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar_medico(id):
    try:
        medico = Medico.query.get(id)
        if not medico:
            return jsonify({'sucesso': False, 'mensagem': 'Médico não encontrado'}), 404
            
        # Apenas desativa para não quebrar banco de dados por causa de consultas atreladas
        medico.usuario.ativo = False
        db.session.commit()
        
        return jsonify({'sucesso': True, 'mensagem': 'Médico desativado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500