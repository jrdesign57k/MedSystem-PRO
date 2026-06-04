"""
MedSystem Dashboard Routes - Métricas e visão geral
"""

from flask import Blueprint, request, jsonify
from flask_jwt_required import jwt_required
from app import db
from models import Consulta, Paciente, Medico, Exame, Prescricao, Diagnostico
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

# ════════════════════════════════════════════════════════════
# GET /api/dashboard
# Dashboard com métricas do dia
# ════════════════════════════════════════════════════════════
@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def obter_dashboard():
    try:
        today = datetime.utcnow().date()
        
        # Métricas do dia
        consultas_hoje = Consulta.query.filter(
            db.func.date(Consulta.data_consulta) == today
        ).count()
        
        consultas_semana = Consulta.query.filter(
            Consulta.data_consulta >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        pacientes_ativos = Paciente.query.filter_by(ativo=True).count()
        
        novos_pacientes = Paciente.query.filter(
            Paciente.data_cadastro >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        exames_pendentes = Exame.query.filter(
            Exame.status.in_(['SOLICITADO', 'AGUARDANDO', 'EM_ANÁLISE'])
        ).count()
        
        # Próximos retornos (timeline)
        proximos_retornos = Consulta.query.filter(
            Consulta.data_consulta >= datetime.utcnow(),
            Consulta.status.in_(['AGENDADA', 'CONFIRMADA'])
        ).order_by(Consulta.data_consulta).limit(5).all()
        
        retornos_list = []
        for c in proximos_retornos:
            retornos_list.append({
                'paciente': c.paciente.nome if c.paciente else 'Desconhecido',
                'motivo': c.motivo or 'Consulta',
                'medico': c.medico.usuario.nome if (c.medico and c.medico.usuario) else 'Desconhecido',
                'data': c.data_consulta.strftime('%d/%m/%Y'),
                'hora': c.hora_consulta or c.data_consulta.strftime('%H:%M')
            })
        
        # Exames pendentes
        exames_list = []
        exames = Exame.query.filter(
            Exame.status.in_(['SOLICITADO', 'AGUARDANDO', 'EM_ANÁLISE'])
        ).limit(5).all()
        
        for e in exames:
            exames_list.append({
                'paciente': e.paciente.nome if e.paciente else 'Desconhecido',
                'exame': e.nome_exame or 'Exame',
                'prioridade': e.prioridade,
                'status': e.status,
                'data_solicitacao': e.data_solicitacao.strftime('%d/%m/%Y') if e.data_solicitacao else None
            })
        
        # Alertas clínicos (diagnósticos graves)
        alertas = Diagnostico.query.filter(
            Diagnostico.gravidade.in_(['GRAVE', 'Grave'])
        ).limit(5).all()
        
        alertas_list = []
        for a in alertas:
            alertas_list.append({
                'paciente': a.paciente.nome if a.paciente else 'Desconhecido',
                'diagnóstico': a.descricao,
                'cid': a.cid,
                'gravidade': a.gravidade
            })
        
        return jsonify({
            'sucesso': True,
            'metricas': {
                'consultas_hoje': consultas_hoje,
                'consultas_semana': consultas_semana,
                'pacientes_ativos': pacientes_ativos,
                'novos_pacientes': novos_pacientes,
                'exames_pendentes': exames_pendentes
            },
            'proximos_retornos': retornos_list,
            'exames_pendentes': exames_list,
            'alertas': alertas_list,
            'data': today.strftime('%d/%m/%Y')
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ════════════════════════════════════════════════════════════
# GET /api/dashboard/agenda/semana
# Agenda semanal (consultas por dia e hora)
# ════════════════════════════════════════════════════════════
@dashboard_bp.route('/agenda/semana', methods=['GET'])
@jwt_required()
def agenda_semanal():
    try:
        today = datetime.utcnow()
        
        # Agrupar consultas por dia da semana
        dias = {}
        for i in range(7):
            dia = today + timedelta(days=i)
            dias[dia.strftime('%A')] = {
                'data': dia.strftime('%d/%m'),
                'numero': dia.day,
                'consultas': []
            }
        
        # Buscar consultas da semana
        consultas = Consulta.query.filter(
            Consulta.data_consulta >= today,
            Consulta.data_consulta <= today + timedelta(days=7)
        ).all()
        
        for c in consultas:
            dia_semana = c.data_consulta.strftime('%A')
            if dia_semana in dias:
                dias[dia_semana]['consultas'].append({
                    'hora': c.hora_consulta or c.data_consulta.strftime('%H:%M'),
                    'paciente': c.paciente.nome if c.paciente else 'Desconhecido',
                    'tipo': c.tipo_consulta or 'Consulta',
                    'medico': c.medico.usuario.nome if (c.medico and c.medico.usuario) else 'Desconhecido',
                    'status': c.status
                })
        
        # Estatísticas da semana
        total = len(consultas)
        confirmadas = Consulta.query.filter(
            Consulta.data_consulta >= today,
            Consulta.data_consulta <= today + timedelta(days=7),
            Consulta.status == 'CONFIRMADA'
        ).count()
        aguardando = total - confirmadas
        
        return jsonify({
            'sucesso': True,
            'dias': dias,
            'estatisticas': {
                'total': total,
                'confirmadas': confirmadas,
                'aguardando': aguardando,
                'canceladas': 0
            }
        })
    
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500
