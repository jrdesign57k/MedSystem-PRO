"""
MedSystem Mensagens Routes - Comunicação interna da equipe
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Mensagem, Usuario
from sqlalchemy import or_, and_

mensagens_bp = Blueprint('mensagens', __name__)


def _uid():
    return int(get_jwt_identity())


# ════════════════════════════════════════════════════════════
# GET /api/mensagens/contatos
# Lista colegas ativos para iniciar conversa
# ════════════════════════════════════════════════════════════
@mensagens_bp.route('/contatos', methods=['GET'])
@jwt_required()
def listar_contatos():
    try:
        usuario_id = _uid()
        usuarios = Usuario.query.filter(
            Usuario.ativo.is_(True),
            Usuario.id != usuario_id,
        ).order_by(Usuario.nome).all()

        return jsonify({
            'sucesso': True,
            'dados': [
                {
                    'id': u.id,
                    'nome': u.nome,
                    'email': u.email,
                    'tipo': u.tipo,
                }
                for u in usuarios
            ],
        })
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


# ════════════════════════════════════════════════════════════
# GET /api/mensagens/nao-lidas
# Total de mensagens não lidas do usuário logado
# ════════════════════════════════════════════════════════════
@mensagens_bp.route('/nao-lidas', methods=['GET'])
@jwt_required()
def contar_nao_lidas():
    try:
        usuario_id = _uid()
        total = Mensagem.query.filter_by(
            id_destinatario=usuario_id,
            lida=False,
        ).count()
        return jsonify({'sucesso': True, 'total': total})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


# ════════════════════════════════════════════════════════════
# GET /api/mensagens
# Listar conversas do usuário (enviadas + recebidas)
# ════════════════════════════════════════════════════════════
@mensagens_bp.route('', methods=['GET'])
@jwt_required()
def listar_mensagens():
    try:
        usuario_id = _uid()

        mensagens = Mensagem.query.filter(
            or_(
                Mensagem.id_remetente == usuario_id,
                Mensagem.id_destinatario == usuario_id,
            )
        ).order_by(Mensagem.data_envio.desc()).all()

        conversas = {}
        for m in mensagens:
            if m.id_remetente == usuario_id:
                outro_id = m.id_destinatario
                outro_nome = m.destinatario.nome if m.destinatario else 'Usuário'
            else:
                outro_id = m.id_remetente
                outro_nome = m.remetente.nome if m.remetente else 'Usuário'

            if outro_id not in conversas:
                conversas[outro_id] = {
                    'id': outro_id,
                    'nome': outro_nome,
                    'ultimo_envio': m.data_envio.strftime('%d/%m %H:%M') if m.data_envio else '',
                    'ultima_mensagem': m.conteudo,
                    'ultimas_mensagens': [m.conteudo],
                    'nao_lidas': 0,
                    '_ts': m.data_envio,
                }
            elif len(conversas[outro_id]['ultimas_mensagens']) < 3:
                conversas[outro_id]['ultimas_mensagens'].append(m.conteudo)

        for outro_id in conversas:
            conversas[outro_id]['nao_lidas'] = Mensagem.query.filter_by(
                id_destinatario=usuario_id,
                id_remetente=outro_id,
                lida=False,
            ).count()

        lista = sorted(conversas.values(), key=lambda c: c['_ts'] or 0, reverse=True)
        for c in lista:
            c.pop('_ts', None)

        total_nao_lidas = Mensagem.query.filter_by(
            id_destinatario=usuario_id,
            lida=False,
        ).count()

        return jsonify({
            'sucesso': True,
            'conversas': lista,
            'total_nao_lidas': total_nao_lidas,
        })

    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


# ════════════════════════════════════════════════════════════
# POST /api/mensagens
# Enviar mensagem
# ════════════════════════════════════════════════════════════
@mensagens_bp.route('', methods=['POST'])
@jwt_required()
def enviar_mensagem():
    try:
        usuario_id = _uid()
        dados = request.get_json() or {}

        id_destinatario = dados.get('id_destinatario')
        conteudo = (dados.get('conteudo') or '').strip()

        if not id_destinatario or not conteudo:
            return jsonify({
                'sucesso': False,
                'erro': 'Destinatário e conteúdo são obrigatórios',
            }), 400

        destinatario = Usuario.query.filter_by(id=int(id_destinatario), ativo=True).first()
        if not destinatario:
            return jsonify({'sucesso': False, 'erro': 'Destinatário não encontrado'}), 404

        if int(id_destinatario) == usuario_id:
            return jsonify({'sucesso': False, 'erro': 'Não é possível enviar mensagem para si mesmo'}), 400

        mensagem = Mensagem(
            id_remetente=usuario_id,
            id_destinatario=int(id_destinatario),
            assunto=dados.get('assunto'),
            conteudo=conteudo,
        )

        db.session.add(mensagem)
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Mensagem enviada com sucesso',
            'id': mensagem.id,
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


# ════════════════════════════════════════════════════════════
# GET /api/mensagens/:id
# Obter conversa com usuário
# ════════════════════════════════════════════════════════════
@mensagens_bp.route('/<int:outro_usuario_id>', methods=['GET'])
@jwt_required()
def obter_conversa(outro_usuario_id):
    try:
        usuario_id = _uid()

        outro_usuario = Usuario.query.get(outro_usuario_id)
        if not outro_usuario or not outro_usuario.ativo:
            return jsonify({'sucesso': False, 'erro': 'Usuário não encontrado'}), 404

        mensagens = Mensagem.query.filter(
            or_(
                and_(
                    Mensagem.id_remetente == usuario_id,
                    Mensagem.id_destinatario == outro_usuario_id,
                ),
                and_(
                    Mensagem.id_remetente == outro_usuario_id,
                    Mensagem.id_destinatario == usuario_id,
                ),
            )
        ).order_by(Mensagem.data_envio).all()

        Mensagem.query.filter(
            Mensagem.id_destinatario == usuario_id,
            Mensagem.id_remetente == outro_usuario_id,
            Mensagem.lida.is_(False),
        ).update({'lida': True})
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'outro_usuario': {
                'id': outro_usuario.id,
                'nome': outro_usuario.nome,
            },
            'mensagens': [m.to_dict() for m in mensagens],
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


# ════════════════════════════════════════════════════════════
# PUT /api/mensagens/:id/marcar-lida
# Marcar mensagem como lida
# ════════════════════════════════════════════════════════════
@mensagens_bp.route('/<int:msg_id>/marcar-lida', methods=['PUT'])
@jwt_required()
def marcar_lida(msg_id):
    try:
        usuario_id = _uid()

        mensagem = Mensagem.query.get(msg_id)
        if not mensagem or mensagem.id_destinatario != usuario_id:
            return jsonify({'sucesso': False, 'erro': 'Mensagem não encontrada'}), 404

        mensagem.lida = True
        db.session.commit()

        return jsonify({
            'sucesso': True,
            'mensagem': 'Mensagem marcada como lida',
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500
