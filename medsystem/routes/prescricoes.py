"""
MedSystem Prescrições — emissão e histórico de receituários
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from decorators import role_required
from models import Prescricao, Paciente, Medico, Consulta, Usuario, LogAuditoria

prescricoes_bp = Blueprint('prescricoes', __name__)


def _parse_quantidade(val):
    if val is None or val == '':
        return None
    if isinstance(val, int):
        return val
    digits = ''.join(c for c in str(val) if c.isdigit())
    return int(digits) if digits else None


def _medico_logado():
    usuario = Usuario.query.get(int(get_jwt_identity()))
    if not usuario:
        return None, None
    if usuario.tipo == 'admin':
        return usuario, Medico.query.first()
    medico = Medico.query.filter_by(id_usuario=usuario.id).first()
    return usuario, medico


def _consulta_para_prescricao(id_paciente, id_medico):
    consulta = (
        Consulta.query.filter_by(id_paciente=id_paciente)
        .order_by(Consulta.data_consulta.desc())
        .first()
    )
    if consulta:
        return consulta

    consulta = Consulta(
        id_paciente=id_paciente,
        id_medico=id_medico,
        data_consulta=datetime.utcnow(),
        hora_consulta=datetime.now().strftime('%H:%M'),
        status='EM_ATENDIMENTO',
        motivo='Prescrição médica',
        tipo_consulta='Retorno',
    )
    db.session.add(consulta)
    db.session.flush()
    return consulta


def _agrupar_prescricoes(presc):
    """Agrupa medicamentos emitidos juntos na mesma receita."""
    if not presc.data_prescricao:
        return [presc]
    inicio = presc.data_prescricao.replace(second=0, microsecond=0)
    fim = inicio + timedelta(minutes=1)
    return (
        Prescricao.query.filter(
            Prescricao.id_consulta == presc.id_consulta,
            Prescricao.tipo_receita == presc.tipo_receita,
            Prescricao.orientacoes == presc.orientacoes,
            Prescricao.data_prescricao >= inicio,
            Prescricao.data_prescricao < fim,
        )
        .order_by(Prescricao.id)
        .all()
    )


def _montar_receita_pdf(prescricoes, paciente, medico, usuario):
    ids = [p.id for p in prescricoes]
    esp = medico.especialidade.nome if medico.especialidade else 'Clínica Geral'
    data_ref = prescricoes[0].data_prescricao
    return {
        'numero': f'R{ids[0]:04d}',
        'paciente': paciente.nome,
        'cpf': paciente.cpf,
        'medico': usuario.nome if usuario else '—',
        'crm': medico.crm or '—',
        'especialidade': esp,
        'tipo_receita': prescricoes[0].tipo_receita,
        'orientacoes': prescricoes[0].orientacoes or '',
        'data': data_ref.strftime('%d/%m/%Y') if data_ref else datetime.now().strftime('%d/%m/%Y'),
        'medicamentos': [
            {
                'medicamento': p.medicamento,
                'posologia': p.posologia,
                'duracao': p.duracao,
                'quantidade': p.quantidade,
            }
            for p in prescricoes
        ],
    }


@prescricoes_bp.route('', methods=['GET'])
@jwt_required()
@role_required('admin', 'medico')
def listar_prescricoes():
    try:
        prescricoes = (
            Prescricao.query.order_by(Prescricao.data_prescricao.desc())
            .limit(100)
            .all()
        )
        dados = []
        for p in prescricoes:
            item = p.to_dict()
            paciente = Paciente.query.get(p.id_paciente)
            medico = Medico.query.get(p.id_medico)
            item['paciente_nome'] = paciente.nome if paciente else '—'
            item['medico_nome'] = medico.usuario.nome if medico and medico.usuario else '—'
            item['numero'] = f'R{p.id:04d}'
            item['data_fmt'] = (
                p.data_prescricao.strftime('%d/%m/%y')
                if p.data_prescricao else '—'
            )
            dados.append(item)

        return jsonify({'sucesso': True, 'dados': dados}), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


@prescricoes_bp.route('/<int:id_prescricao>/receita', methods=['GET'])
@jwt_required()
@role_required('admin', 'medico')
def obter_receita_pdf(id_prescricao):
    try:
        presc = Prescricao.query.get(id_prescricao)
        if not presc:
            return jsonify({'sucesso': False, 'mensagem': 'Receita não encontrada'}), 404

        paciente = Paciente.query.get(presc.id_paciente)
        medico = Medico.query.get(presc.id_medico)
        if not paciente or not medico:
            return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos da receita'}), 404

        usuario = Usuario.query.get(medico.id_usuario)
        grupo = _agrupar_prescricoes(presc)
        return jsonify({
            'sucesso': True,
            'receita': _montar_receita_pdf(grupo, paciente, medico, usuario),
        }), 200
    except Exception as e:
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500


@prescricoes_bp.route('', methods=['POST'])
@jwt_required()
@role_required('admin', 'medico')
def emitir_prescricao():
    try:
        usuario, medico = _medico_logado()
        if not medico:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Médico não encontrado para emitir receita'
            }), 400

        dados = request.get_json() or {}
        id_paciente = dados.get('id_paciente')
        medicamentos = dados.get('medicamentos') or []
        tipo_receita = dados.get('tipo_receita') or 'Simples'
        orientacoes = dados.get('orientacoes') or ''

        if not id_paciente:
            return jsonify({'sucesso': False, 'mensagem': 'Selecione um paciente'}), 400

        paciente = Paciente.query.get(int(id_paciente))
        if not paciente or not paciente.ativo:
            return jsonify({'sucesso': False, 'mensagem': 'Paciente não encontrado'}), 404

        meds_validos = [m for m in medicamentos if (m.get('medicamento') or '').strip()]
        if not meds_validos:
            return jsonify({'sucesso': False, 'mensagem': 'Informe ao menos um medicamento'}), 400

        consulta = _consulta_para_prescricao(paciente.id_paciente, medico.id)
        criadas = []

        for med in meds_validos:
            posologia = (med.get('posologia') or '').strip()
            duracao = (med.get('duracao') or '').strip()
            if duracao:
                posologia = f'{posologia} · Duração: {duracao}' if posologia else f'Duração: {duracao}'
            if not posologia:
                posologia = 'Conforme orientação médica'

            presc = Prescricao(
                id_consulta=consulta.id_consulta,
                id_medico=medico.id,
                id_paciente=paciente.id_paciente,
                medicamento=med['medicamento'].strip(),
                dosagem=(med.get('dosagem') or '').strip() or None,
                posologia=posologia,
                duracao=duracao or None,
                quantidade=_parse_quantidade(med.get('quantidade')),
                tipo_receita=tipo_receita,
                orientacoes=orientacoes or None,
                status='ATIVA',
            )
            db.session.add(presc)
            criadas.append(presc)

        db.session.flush()
        ids = [p.id for p in criadas]
        db.session.add(LogAuditoria(
            tabela='prescricoes',
            operacao='INSERT',
            id_registro=ids[0],
            detalhe=f'Receita emitida para {paciente.nome} ({len(criadas)} medicamento(s))',
        ))
        db.session.commit()

        esp = medico.especialidade.nome if medico.especialidade else 'Clínica Geral'
        return jsonify({
            'sucesso': True,
            'mensagem': 'Receita emitida com sucesso',
            'receita': _montar_receita_pdf(criadas, paciente, medico, usuario),
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'mensagem': str(e)}), 500
