"""
MedSystem Additional Routes - Exames e Dashboard
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Exame, TipoExame, Consulta, Paciente, LogAuditoria, Diagnostico
from datetime import datetime, timedelta

exames_bp = Blueprint('exames', __name__)
dashboard_bp = Blueprint('dashboard', __name__)

# ════════════════════════════════════════════════════════════
# EXAMES
# ════════════════════════════════════════════════════════════

@exames_bp.route('', methods=['GET'])
@jwt_required()
def listar_exames():
    """Lista todos os exames"""
    try:
        status = request.args.get('status', None)
        query = Exame.query
        
        if status:
            query = query.filter_by(status=status)
        
        # Como data_solicitacao não existe no modelo atual, ordenamos pelo ID
        exames = query.order_by(Exame.id.desc()).all()
        
        return jsonify({
            'sucesso': True,
            'total': len(exames),
            'dados': [e.to_dict() for e in exames]
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@exames_bp.route('/pendentes', methods=['GET'])
@jwt_required()
def listar_exames_pendentes():
    """Lista exames pendentes (CURSOR - simulado com query)"""
    try:
        exames = Exame.query.filter(
            Exame.status.in_(['SOLICITADO', 'EM_ANALISE'])
        ).order_by(Exame.id).all()
        
        # Agrupar por paciente
        exames_por_paciente = {}
        for exame in exames:
            # Busca a consulta associada para achar o paciente
            consulta = Consulta.query.get(exame.id_consulta)
            if not consulta:
                continue
                
            paciente = Paciente.query.get(consulta.id_paciente)
            if not paciente:
                continue
                
            paciente_nome = paciente.nome
            if paciente_nome not in exames_por_paciente:
                exames_por_paciente[paciente_nome] = {
                    'id_paciente': paciente.id_paciente,
                    'quantidade': 0,
                    'exames': []
                }
            exames_por_paciente[paciente_nome]['quantidade'] += 1
            exames_por_paciente[paciente_nome]['exames'].append(exame.to_dict())
        
        return jsonify({
            'sucesso': True,
            'total': len(exames_por_paciente),
            'dados': exames_por_paciente
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@exames_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def buscar_exame(id):
    """Busca um exame específico"""
    try:
        exame = Exame.query.get(id)
        
        if not exame:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Exame não encontrado'
            }), 404
        
        return jsonify({
            'sucesso': True,
            'dados': exame.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@exames_bp.route('/<int:id>/resultado', methods=['PUT'])
@jwt_required()
def registrar_resultado_exame(id):
    """Registra resultado do exame"""
    try:
        exame = Exame.query.get(id)
        
        if not exame:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Exame não encontrado'
            }), 404
        
        dados = request.get_json()
        
        try:
            exame.resultado = dados.get('resultado')
            exame.status = dados.get('status', 'CONCLUIDO')
            
            db.session.flush()
            
            log = LogAuditoria(
                tabela='exames',
                operacao='UPDATE',
                id_registro=exame.id,
                detalhe=f'Resultado registrado para o exame ID: {exame.id}'
            )
            db.session.add(log)
            db.session.commit()  # ✓ COMMIT
            
            return jsonify({
                'sucesso': True,
                'mensagem': 'Resultado registrado com sucesso',
                'dados': exame.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()  # ✗ ROLLBACK
            raise e
            
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════

@dashboard_bp.route('/estatisticas', methods=['GET'])
@jwt_required()
def obter_estatisticas():
    """Retorna estatísticas do dashboard"""
    try:
        hoje = datetime.now().date()
        
        # Consultas de hoje
        consultas_hoje = Consulta.query.filter(
            Consulta.data_consulta >= datetime(hoje.year, hoje.month, hoje.day),
            Consulta.data_consulta < datetime(hoje.year, hoje.month, hoje.day) + timedelta(days=1)
        ).count()
        
        # Pacientes ativos
        pacientes_ativos = Paciente.query.filter_by(ativo=True).count()
        
        # Exames pendentes
        exames_pendentes = Exame.query.filter(
            Exame.status.in_(['SOLICITADO', 'EM_ANALISE'])
        ).count()
        
        # Consultas próximas (próximos 7 dias)
        data_futura = hoje + timedelta(days=7)
        consultas_proximas = Consulta.query.filter(
            Consulta.data_consulta >= datetime(hoje.year, hoje.month, hoje.day),
            Consulta.data_consulta <= datetime(data_futura.year, data_futura.month, data_futura.day)
        ).count()
        
        return jsonify({
            'sucesso': True,
            'dados': {
                'consultas_hoje': consultas_hoje,
                'pacientes_ativos': pacientes_ativos,
                'exames_pendentes': exames_pendentes,
                'consultas_proximas': consultas_proximas
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@dashboard_bp.route('/alertas', methods=['GET'])
@jwt_required()
def obter_alertas():
    """Retorna alertas clínicos (diagnósticos graves)"""
    try:
        # Diagnósticos graves/críticos
        diagnosticos_graves = Diagnostico.query.filter(
            Diagnostico.gravidade.in_(['GRAVE', 'CRITICA'])
        ).all()
        
        alertas = []
        for diag in diagnosticos_graves:
            consulta = Consulta.query.get(diag.id_consulta)
            if not consulta:
                continue
                
            paciente = Paciente.query.get(consulta.id_paciente)
            if not paciente:
                continue
                
            alertas.append({
                'paciente': paciente.nome,
                'tipo': 'DIAGNÓSTICO GRAVE',
                'descricao': diag.descricao,
                'gravidade': diag.gravidade,
                'data': consulta.data_consulta.isoformat() if consulta.data_consulta else None
            })
        
        return jsonify({
            'sucesso': True,
            'total': len(alertas),
            'dados': alertas
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500

@dashboard_bp.route('/proximas-consultas', methods=['GET'])
@jwt_required()
def proximas_consultas():
    """Retorna próximas consultas agendadas"""
    try:
        hoje = datetime.now().date()
        proximas = Consulta.query.filter(
            Consulta.data_consulta >= datetime(hoje.year, hoje.month, hoje.day),
            Consulta.data_consulta <= datetime(hoje.year, hoje.month, hoje.day) + timedelta(days=30)
        ).order_by(Consulta.data_consulta).all()
        
        consultas_list = []
        for c in proximas:
            consultas_list.append({
                'id': c.id,
                'paciente': c.paciente.nome if c.paciente else 'N/A',
                'medico': c.medico.usuario.nome if c.medico and c.medico.usuario else 'N/A',
                'data': c.data_consulta.isoformat() if c.data_consulta else None,
                'motivo': c.motivo or 'Consulta',
                'status': c.status or 'Agendada'
            })
        
        return jsonify({
            'sucesso': True,
            'total': len(consultas_list),
            'dados': consultas_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'mensagem': f'Erro: {str(e)}'
        }), 500