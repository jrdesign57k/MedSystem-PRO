"""
Portal do Paciente — exames, prontuário e notificações (somente leitura).
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from decorators import role_required
from models import (
    Usuario, Paciente, Exame, Consulta, SinalVital,
    Diagnostico, NotificacaoPaciente, Medico,
)

portal_bp = Blueprint('portal', __name__)


def _uid():
    return int(get_jwt_identity())


def _paciente_logado():
    user = Usuario.query.get(_uid())
    if not user or user.tipo != 'paciente' or not user.ativo:
        return None, user
    paciente = Paciente.query.filter_by(id_usuario=user.id, ativo=True).first()
    return paciente, user


def _require_paciente():
    paciente, _user = _paciente_logado()
    return paciente


def _serializar_exame_paciente(exame):
    medico_nome = 'Médico'
    if exame.medico and exame.medico.usuario:
        medico_nome = exame.medico.usuario.nome
    return {
        'id': exame.id,
        'nome_exame': exame.nome_exame,
        'status': exame.status,
        'prioridade': exame.prioridade,
        'resultado': exame.resultado,
        'laudo': exame.laudo,
        'medico': medico_nome,
        'data_solicitacao': exame.data_solicitacao.isoformat() if exame.data_solicitacao else None,
        'data_resultado': exame.data_resultado.isoformat() if exame.data_resultado else None,
        'tem_resultado': bool(exame.resultado or exame.laudo or exame.status in ('DISPONÍVEL', 'CONCLUIDO', 'CONCLUÍDO')),
    }


def _serializar_prontuario_paciente(consulta):
    id_consulta = consulta.id_consulta
    sinais = SinalVital.query.filter_by(id_consulta=id_consulta).first()
    diagnosticos = Diagnostico.query.filter_by(id_consulta=id_consulta).all()
    exames = Exame.query.filter_by(id_consulta=id_consulta).all()
    medico_nome = consulta.medico.usuario.nome if (consulta.medico and consulta.medico.usuario) else 'Médico'
    esp = (
        consulta.medico.especialidade.nome
        if consulta.medico and consulta.medico.especialidade else 'Clínica Geral'
    )

    return {
        'id': id_consulta,
        'data': consulta.data_consulta.strftime('%d/%m/%Y') if consulta.data_consulta else '',
        'hora': consulta.hora_consulta or '',
        'status': consulta.status,
        'motivo': consulta.motivo,
        'tipo_consulta': consulta.tipo_consulta,
        'medico': medico_nome,
        'especialidade': esp,
        'queixa_principal': consulta.queixa_principal,
        'plano_terapeutico': consulta.plano_terapeutico,
        'observacoes': consulta.observacoes_consulta,
        'sinais_vitais': sinais.to_dict() if sinais else {},
        'diagnosticos': [
            {'cid': d.cid, 'descricao': d.descricao, 'gravidade': d.gravidade}
            for d in diagnosticos
        ],
        'exames': [_serializar_exame_paciente(e) for e in exames],
    }


@portal_bp.route('/perfil', methods=['GET'])
@jwt_required()
@role_required('paciente')
def portal_perfil():
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403
    dados = paciente.to_dict()
    dados['cpf_mascarado'] = (dados.get('cpf') or '')[:3] + '.***.***-**' if dados.get('cpf') else ''
    return jsonify({'sucesso': True, 'dados': dados})


@portal_bp.route('/exames', methods=['GET'])
@jwt_required()
@role_required('paciente')
def portal_exames():
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403

    exames = Exame.query.filter_by(id_paciente=paciente.id_paciente).order_by(Exame.data_solicitacao.desc()).all()
    return jsonify({
        'sucesso': True,
        'total': len(exames),
        'dados': [_serializar_exame_paciente(e) for e in exames],
    })


@portal_bp.route('/exames/<int:id>', methods=['GET'])
@jwt_required()
@role_required('paciente')
def portal_exame_detalhe(id):
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403

    exame = Exame.query.filter_by(id=id, id_paciente=paciente.id_paciente).first()
    if not exame:
        return jsonify({'sucesso': False, 'mensagem': 'Exame não encontrado'}), 404

    return jsonify({'sucesso': True, 'dados': _serializar_exame_paciente(exame)})


@portal_bp.route('/consultas', methods=['GET'])
@jwt_required()
@role_required('paciente')
def portal_consultas():
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403

    consultas = Consulta.query.filter_by(id_paciente=paciente.id_paciente).order_by(Consulta.data_consulta.desc()).all()
    lista = []
    for c in consultas:
        medico_nome = c.medico.usuario.nome if (c.medico and c.medico.usuario) else 'Médico'
        lista.append({
            'id': c.id_consulta,
            'data': c.data_consulta.strftime('%d/%m/%Y') if c.data_consulta else '',
            'hora': c.hora_consulta or '',
            'status': c.status,
            'motivo': c.motivo,
            'medico': medico_nome,
            'tipo_consulta': c.tipo_consulta,
        })
    return jsonify({'sucesso': True, 'total': len(lista), 'dados': lista})


@portal_bp.route('/prontuario', methods=['GET'])
@jwt_required()
@role_required('paciente')
def portal_prontuario_lista():
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403

    consultas = Consulta.query.filter_by(id_paciente=paciente.id_paciente).order_by(Consulta.data_consulta.desc()).all()
    return jsonify({
        'sucesso': True,
        'dados': [_serializar_prontuario_paciente(c) for c in consultas],
    })


@portal_bp.route('/prontuario/<int:id_consulta>', methods=['GET'])
@jwt_required()
@role_required('paciente')
def portal_prontuario_detalhe(id_consulta):
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403

    consulta = Consulta.query.filter_by(id_consulta=id_consulta, id_paciente=paciente.id_paciente).first()
    if not consulta:
        return jsonify({'sucesso': False, 'mensagem': 'Consulta não encontrada'}), 404

    return jsonify({'sucesso': True, 'dados': _serializar_prontuario_paciente(consulta)})


@portal_bp.route('/notificacoes', methods=['GET'])
@jwt_required()
@role_required('paciente')
def portal_notificacoes():
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403

    notifs = NotificacaoPaciente.query.filter_by(id_paciente=paciente.id_paciente).order_by(
        NotificacaoPaciente.data_criacao.desc()
    ).all()
    nao_lidas = sum(1 for n in notifs if not n.lida)
    return jsonify({
        'sucesso': True,
        'total': len(notifs),
        'nao_lidas': nao_lidas,
        'dados': [n.to_dict() for n in notifs],
    })


@portal_bp.route('/notificacoes/nao-lidas', methods=['GET'])
@jwt_required()
@role_required('paciente')
def portal_notificacoes_nao_lidas():
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403

    total = NotificacaoPaciente.query.filter_by(id_paciente=paciente.id_paciente, lida=False).count()
    return jsonify({'sucesso': True, 'total': total})


@portal_bp.route('/notificacoes/<int:notif_id>/lida', methods=['PUT'])
@jwt_required()
@role_required('paciente')
def portal_marcar_notificacao_lida(notif_id):
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403

    notif = NotificacaoPaciente.query.filter_by(id=notif_id, id_paciente=paciente.id_paciente).first()
    if not notif:
        return jsonify({'sucesso': False, 'mensagem': 'Notificação não encontrada'}), 404

    notif.lida = True
    db.session.commit()
    return jsonify({'sucesso': True, 'mensagem': 'Notificação marcada como lida'})


@portal_bp.route('/notificacoes/marcar-todas', methods=['PUT'])
@jwt_required()
@role_required('paciente')
def portal_marcar_todas_lidas():
    paciente = _require_paciente()
    if not paciente:
        return jsonify({'sucesso': False, 'mensagem': 'Acesso restrito ao portal do paciente'}), 403

    NotificacaoPaciente.query.filter_by(id_paciente=paciente.id_paciente, lida=False).update({'lida': True})
    db.session.commit()
    return jsonify({'sucesso': True, 'mensagem': 'Todas as notificações foram marcadas como lidas'})
