"""
MedSystem Mensagens Routes - Comunicação interna da equipe
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Mensagem, Usuario
from datetime import datetime

mensagens_bp = Blueprint('mensagens', __name__)

# ════════════════════════════════════════════════════════════
# GET /api/mensagens
# Listar mensagens do usuário
# ════════════════════════════════════════════════════════════
@mensagens_bp.route('', methods=['GET'])
@jwt_required()
def listar_mensagens():
    try:
        usuario_id = get_jwt_identity()
        tipo = request.args.get('tipo', 'recebidas')  # recebidas, enviadas
        
        if tipo == 'recebidas':
            mensagens = Mensagem.query.filter_by(
                id_destinatario=usuario_id
            ).order_by(Mensagem.data_envio.desc()).all()
        else:
            mensagens = Mensagem.query.filter_by(
                id_remetente=usuario_id
            ).order_by(Mensagem.data_envio.desc()).all()
        
        # Agrupar em conversas
        conversas = {}
        for m in mensagens:
            outro_id = m.id_remetente if tipo == 'recebidas' else m.id_destinatario
            outro_nome = m.remetente.nome if tipo == 'recebidas' else m.destinatario.nome
            
            if outro_id not in conversas:
                conversas[outro_id] = {
                    'id': outro_id,
                    'nome': outro_nome,
                    'ultimo_envio': m.data_envio.strftime('%H:%M'),
                    'ultimas_mensagens': []
                }
            
            if len(conversas[outro_id]['ultimas_mensagens']) < 3:
                conversas[outro_id]['ultimas_mensagens'].append(m.conteudo)
        
        return jsonify({
            'sucesso': True,
            'conversas': list(conversas.values())
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
        usuario_id = get_jwt_identity()
        dados = request.get_json()
        
        mensagem = Mensagem(
            id_remetente=usuario_id,
            id_destinatario=dados.get('id_destinatario'),
            assunto=dados.get('assunto'),
            conteudo=dados.get('conteudo')
        )
        
        db.session.add(mensagem)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Mensagem enviada com sucesso',
            'id': mensagem.id
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
        usuario_id = get_jwt_identity()
        
        # Buscar todas as mensagens da conversa
        mensagens = Mensagem.query.filter(
            db.or_(
                db.and_(
                    Mensagem.id_remetente == usuario_id,
                    Mensagem.id_destinatario == outro_usuario_id
                ),
                db.and_(
                    Mensagem.id_remetente == outro_usuario_id,
                    Mensagem.id_destinatario == usuario_id
                )
            )
        ).order_by(Mensagem.data_envio).all()
        
        # Marcar como lidas
        Mensagem.query.filter(
            Mensagem.id_destinatario == usuario_id,
            Mensagem.id_remetente == outro_usuario_id,
            Mensagem.lida == False
        ).update({'lida': True})
        db.session.commit()
        
        outro_usuario = Usuario.query.get(outro_usuario_id)
        
        return jsonify({
            'sucesso': True,
            'outro_usuario': {
                'id': outro_usuario.id,
                'nome': outro_usuario.nome
            },
            'mensagens': [m.to_dict() for m in mensagens]
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# PUT /api/mensagens/:id/marcar-lida
# Marcar mensagem como lida
# ════════════════════════════════════════════════════════════
@mensagens_bp.route('/<int:msg_id>/marcar-lida', methods=['PUT'])
@jwt_required()
def marcar_lida(msg_id):
    try:
        usuario_id = get_jwt_identity()
        
        mensagem = Mensagem.query.get(msg_id)
        if not mensagem or mensagem.id_destinatario != usuario_id:
            return jsonify({'sucesso': False, 'erro': 'Mensagem não encontrada'}), 404
        
        mensagem.lida = True
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Mensagem marcada como lida'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500
