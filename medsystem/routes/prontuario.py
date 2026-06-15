"""
MedSystem Prontuário Routes - Prontuário eletrônico (médico/admin)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from decorators import role_required
from models import Consulta, Paciente, Medico, SinalVital, Diagnostico, Exame, Usuario

prontuario_bp = Blueprint('prontuario', __name__)


def _usuario_logado():
    user_id = get_jwt_identity()
    return Usuario.query.get(int(user_id)) if user_id else None


def _medico_do_usuario(usuario):
    if not usuario:
        return None
    return Medico.query.filter_by(id_usuario=usuario.id).first()


def _verificar_acesso(consulta):
    usuario = _usuario_logado()
    if not usuario:
        return False, 'Usuário não autenticado', 401
    if usuario.tipo == 'admin':
        return True, None, None
    if usuario.tipo == 'medico':
        medico = _medico_do_usuario(usuario)
        if medico and consulta.id_medico == medico.id:
            return True, None, None
        return False, 'Acesso restrito: prontuário disponível apenas ao médico responsável', 403
    return False, 'Acesso restrito a médicos', 403


def _serializar_prontuario(consulta):
    id_consulta = consulta.id_consulta
    sinais = SinalVital.query.filter_by(id_consulta=id_consulta).first()
    diagnosticos = Diagnostico.query.filter_by(id_consulta=id_consulta).all()
    exames = Exame.query.filter_by(id_consulta=id_consulta).all()
    paciente = consulta.paciente

    return {
        'sucesso': True,
        'consulta': {
            'id': id_consulta,
            'id_paciente': consulta.id_paciente,
            'id_medico': consulta.id_medico,
            'paciente': paciente.nome if paciente else '',
            'medico': consulta.medico.usuario.nome if (consulta.medico and consulta.medico.usuario) else '',
            'medico_crm': consulta.medico.crm if consulta.medico else '',
            'medico_especialidade': (
                consulta.medico.especialidade.nome
                if consulta.medico and consulta.medico.especialidade else 'Clínica Geral'
            ),
            'data': consulta.data_consulta.strftime('%d/%m/%Y') if consulta.data_consulta else '',
            'hora': consulta.hora_consulta or '',
            'status': consulta.status,
            'motivo': consulta.motivo,
            'tipo_consulta': consulta.tipo_consulta,
            'queixa_principal': consulta.queixa_principal,
            'historia_molestia_atual': consulta.historia_molestia_atual,
            'antecedentes_pessoais': consulta.antecedentes_pessoais,
            'antecedentes_familiares': consulta.antecedentes_familiares,
            'exame_fisico': consulta.exame_fisico,
            'hipotese_diagnostica': consulta.hipotese_diagnostica,
            'plano_terapeutico': consulta.plano_terapeutico,
            'observacoes_consulta': consulta.observacoes_consulta,
        },
        'paciente': paciente.to_dict() if paciente else {},
        'sinais_vitais': sinais.to_dict() if sinais else {},
        'diagnosticos': [d.to_dict() for d in diagnosticos],
        'exames': [e.to_dict() for e in exames],
    }


def _aplicar_campos_prontuario(consulta, dados):
    for campo in (
        'queixa_principal', 'historia_molestia_atual', 'antecedentes_pessoais',
        'antecedentes_familiares', 'exame_fisico', 'hipotese_diagnostica',
        'plano_terapeutico', 'observacoes_consulta'
    ):
        if campo in dados:
            setattr(consulta, campo, dados.get(campo))

    if dados.get('finalizar'):
        consulta.status = 'CONCLUIDA'
    elif consulta.status == 'AGENDADA':
        consulta.status = 'EM_ATENDIMENTO'


def _salvar_sinais_vitais(id_consulta, dados):
    sinal = SinalVital.query.filter_by(id_consulta=id_consulta).first()
    if not sinal:
        sinal = SinalVital(id_consulta=id_consulta)
        db.session.add(sinal)

    if 'pa' in dados:
        sinal.pressao_arterial = dados.get('pa')
    if 'fc' in dados:
        sinal.frequencia_cardiaca = dados.get('fc')
    if 'temperatura' in dados:
        sinal.temperatura = dados.get('temperatura')
    if 'spo2' in dados:
        sinal.saturacao_oxigenio = dados.get('spo2')
    if 'peso' in dados:
        sinal.peso = dados.get('peso')


# ════════════════════════════════════════════════════════════
# GET /api/prontuarios/paciente/:id — consultas do paciente
# ════════════════════════════════════════════════════════════
@prontuario_bp.route('/paciente/<int:id_paciente>', methods=['GET'])
@jwt_required()
@role_required('admin', 'medico')
def consultas_paciente_prontuario(id_paciente):
    try:
        paciente = Paciente.query.get(id_paciente)
        if not paciente or not paciente.ativo:
            return jsonify({'sucesso': False, 'mensagem': 'Paciente não encontrado'}), 404

        q = Consulta.query.filter_by(id_paciente=id_paciente).filter(
            Consulta.status != 'CANCELADA'
        )

        usuario = _usuario_logado()
        if usuario and usuario.tipo == 'medico':
            medico = _medico_do_usuario(usuario)
            if not medico:
                return jsonify({'sucesso': False, 'mensagem': 'Perfil médico não vinculado'}), 403
            q = q.filter_by(id_medico=medico.id)

        consultas = q.order_by(Consulta.data_consulta.desc()).all()
        lista = []
        for c in consultas:
            lista.append({
                'id': c.id_consulta,
                'data': c.data_consulta.strftime('%d/%m/%Y') if c.data_consulta else '',
                'hora': c.hora_consulta or '',
                'status': c.status,
                'motivo': c.motivo or c.tipo_consulta or 'Consulta',
                'medico': c.medico.usuario.nome if (c.medico and c.medico.usuario) else '',
                'tem_prontuario': bool(c.queixa_principal or c.historia_molestia_atual or c.exame_fisico),
            })

        return jsonify({
            'sucesso': True,
            'paciente': {'id': paciente.id_paciente, 'nome': paciente.nome},
            'consultas': lista,
        }), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


# ════════════════════════════════════════════════════════════
# POST /api/prontuarios — salvar prontuário
# ════════════════════════════════════════════════════════════
@prontuario_bp.route('', methods=['POST'])
@jwt_required()
@role_required('admin', 'medico')
def criar_prontuario():
    try:
        dados = request.get_json() or {}
        id_consulta = dados.get('id_consulta')
        consulta = Consulta.query.get(id_consulta)
        if not consulta:
            return jsonify({'sucesso': False, 'mensagem': 'Consulta não encontrada'}), 404

        ok, msg, code = _verificar_acesso(consulta)
        if not ok:
            return jsonify({'sucesso': False, 'mensagem': msg}), code

        _aplicar_campos_prontuario(consulta, dados)
        _salvar_sinais_vitais(id_consulta, dados)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Prontuário salvo com sucesso',
            'id_consulta': id_consulta,
            'status': consulta.status,
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


# ════════════════════════════════════════════════════════════
# GET /api/prontuarios/:id
# ════════════════════════════════════════════════════════════
@prontuario_bp.route('/<int:id_consulta>', methods=['GET'])
@jwt_required()
@role_required('admin', 'medico')
def obter_prontuario(id_consulta):
    try:
        consulta = Consulta.query.get(id_consulta)
        if not consulta:
            return jsonify({'sucesso': False, 'mensagem': 'Consulta não encontrada'}), 404

        ok, msg, code = _verificar_acesso(consulta)
        if not ok:
            return jsonify({'sucesso': False, 'mensagem': msg}), code

        return jsonify(_serializar_prontuario(consulta)), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


# ════════════════════════════════════════════════════════════
# PUT /api/prontuarios/:id
# ════════════════════════════════════════════════════════════
@prontuario_bp.route('/<int:id_consulta>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'medico')
def atualizar_prontuario(id_consulta):
    try:
        dados = request.get_json() or {}
        consulta = Consulta.query.get(id_consulta)
        if not consulta:
            return jsonify({'sucesso': False, 'mensagem': 'Consulta não encontrada'}), 404

        ok, msg, code = _verificar_acesso(consulta)
        if not ok:
            return jsonify({'sucesso': False, 'mensagem': msg}), code

        _aplicar_campos_prontuario(consulta, dados)
        _salvar_sinais_vitais(id_consulta, dados)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Prontuário atualizado com sucesso',
            'status': consulta.status,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500
